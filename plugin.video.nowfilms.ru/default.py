#!/usr/bin/python
# -*- coding: utf-8 -*-
#/*
# *      Copyright (C) 2011 Silen
# *
# *
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# */
import re, os, urllib, urllib2, cookielib, time
from time import gmtime, strftime
import urlparse

#-- by bigbax :) ------------------
reload(sys)
sys.setdefaultencoding("UTF8")
#----------------------------------

import demjson3 as json

import xbmc, xbmcgui, xbmcplugin, xbmcaddon

Addon = xbmcaddon.Addon(id='plugin.video.nowfilms.ru')
icon = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'),'icon.png'))
fcookies = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'), r'resources', r'data', r'cookies.txt'))

# load XML library
try:
    sys.path.append(os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib'))
    from BeautifulSoup  import BeautifulSoup
except:
    try:
        sys.path.insert(0, os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib'))
        from BeautifulSoup  import BeautifulSoup
    except:
        sys.path.append(os.path.join(os.getcwd(), r'resources', r'lib'))
        from BeautifulSoup  import BeautifulSoup
        icon = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'icon.png'))

import HTMLParser
hpar = HTMLParser.HTMLParser()

h = int(sys.argv[1])

def showMessage(heading, message, times = 3000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))

def Debug(msg):
    try:
        print "[NowFilms.Ru] " + msg
    except UnicodeEncodeError:
        print "[NowFilms.Ru UTF-8] " + msg.encode( "utf-8", "ignore" )

#---------- parameter/info structure -------------------------------------------
class Param:
    page        = '1'
    genre       = ''
    genre_name  = ''
    genre_flag  = 0
    max_page    = 0
    count       = 0
    url         = ''
    pl          = ''
    search      = ''
    name        = ''
    lname       = ''

class Info:
    img         = ''
    url         = '*'
    title       = ''
    year        = ''
    genre       = ''
    country     = ''
    director    = ''
    text        = ''
    artist      = ''
    orig        = ''
    duration    = ''
    rating      = ''

#---------- get web page -------------------------------------------------------
def get_HTML(url, post = None, ref = None):
    request = urllib2.Request(url, post)

    try:
        host = urlparse.urlsplit(url).hostname
        if host==None:
            host = url.replace('http://', '').split('/')[0]
            if host==None:
                host = 'kinokong.net'
    except:
        host = 'kinokong.net'

    if ref==None:
        ref='http://'+host

    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host',   host)
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Language', 'ru-RU')
    request.add_header('Referer',             ref)

    try:
        f = urllib2.urlopen(request)
    except IOError, e:
        if hasattr(e, 'reason'):
           xbmc.log('We failed to reach a server.')
        elif hasattr(e, 'code'):
           xbmc.log('The server couldn\'t fulfill the request.')

    html = f.read()

    return html

#---------- get parameters -----------------------------------------------------
def Get_Parameters(params):
    #-- page
    try:    p.page = urllib.unquote_plus(params['page'])
    except: p.page = '1'
    #-- genre
    try:    p.genre = urllib.unquote_plus(params['genre'])
    except: p.genre = ''
    try:    p.genre_flag = int(urllib.unquote_plus(params['genre_flag']))
    except: p.genre_flag = 0
    # movie count
    try:    p.max_page = int(urllib.unquote_plus(params['max_page']))
    except: p.max_page = 0
    # movie count
    try:    p.count = int(urllib.unquote_plus(params['count']))
    except: p.count = 0
    #-- url
    try:    p.url = urllib.unquote_plus(params['url'])
    except: p.url = ''
    #-- pl
    try:    p.pl = urllib.unquote_plus(params['pl'])
    except: p.pl = ''
    #-- search
    try:    p.search = urllib.unquote_plus(params['search'])
    except: p.search = ''
    #-- name
    try:    p.name = urllib.unquote_plus(params['name'])
    except: p.name = ''
    #-- lname
    try:    p.lname = urllib.unquote_plus(params['lname'])
    except: p.lname = ''

    #-----
    return p

# ----- search on site --------------------------------------------------------
def get_Search_HTML(search_str, page):
    url = 'http://kinokong.net/index.php?do=search'
    str = search_str.decode('utf-8').encode('windows-1251')

    values = {
                 'do'            : 'search'
                ,'subaction'     : 'search'
                ,'story'         : str
                ,'search_start'  : page
                ,'full_search'   : 0
                ,'result_from'   : (page-1)*30+1
            }

    post = urllib.urlencode(values)
    html = get_HTML(url, post)

    return html

#---------- get HD720.RU URL --------------------------------------------------
def Get_URL(par):
    url = par.url+'page/'+par.page+'/'

    return url
#----------- get page count & number of movies ---------------------------------
def Get_Page_and_Movies_Count(par):
    url = par.url
    html = get_HTML(url)
    # -- parsing web page ------------------------------------------------------
    soup = BeautifulSoup(html, fromEncoding="windows-1251")
    try:
        max_page = 0
        for rec in soup.find("div", {"class":"navigation"}).findAll('a'):
            try:
                if max_page < int(rec.text):
                    max_page = int(rec.text)
            except:
                pass

        #if len(soup.find("div", {"class":"header_submenu"}).findAll('a')) > 0:
        #    par.genre_flag = 1
        #-- #2 -------------------------------------------------------------------------
        url += 'page/%i/'%max_page
        html = get_HTML(url)

        # -- parsing web page ------------------------------------------------------
        soup = BeautifulSoup(html, fromEncoding="windows-1251")
        count = 25*(max_page-1)+len(soup.findAll("div", {"class":"new_movie15"}))+len(soup.findAll("div", {"class":"short_music"}))

    except:
        max_page = 1
        count = len(soup.findAll("div", {"class":"new_movie15"}))++len(soup.findAll("div", {"class":"short_music"}))

    return max_page, count


#----------- get Header string -------------------------------------------------
def Get_Header(par):

    info  = 'Всего: ' + '[COLOR FF00FF00]' + str(par.count) + '[/COLOR]'

    if par.lname <> '':
        info = par.lname+' | '+info

    if par.max_page > 1:
        info += ' | Pages: ' + '[COLOR FF00FF00]'+ par.page + '/' + str(par.max_page) +'[/COLOR]'

    if par.genre <> '':
        info += ' | Жанр: ' + '[COLOR FFFFFF00]'+ par.genre + '[/COLOR]'

    #-- info line
    name    = info
    i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
    u = sys.argv[0] + '?mode=EMPTY'
    u += '&name=%s'%urllib.quote_plus(name)
    #-- filter parameters
    u += '&page=%s'%urllib.quote_plus(par.page)
    u += '&genre=%s'%urllib.quote_plus(par.genre)
    u += '&max_page=%s'%urllib.quote_plus(str(par.max_page))
    u += '&count=%s'%urllib.quote_plus(str(par.count))
    xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- genres
    if par.genre == '' and par.genre_flag == 1 and par.page == '1':
        name    = '[COLOR FFFFFF00][Жанры][/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=GENRES'
        u += '&name=%s'%urllib.quote_plus(name)
        #-- filter parameters
        u += '&url=%s'%urllib.quote_plus(par.url)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- previous page
    if int(par.page) > 1 :
        name    = '[COLOR FF00FF00][PAGE -1][/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=MOVIE'
        u += '&name=%s'%urllib.quote_plus(name)
        u += '&lname=%s'%urllib.quote_plus(par.lname)
        #-- filter parameters
        u += '&page=%s'%urllib.quote_plus(str(int(par.page)-1))
        u += '&url=%s'%urllib.quote_plus(str(par.url))
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- previous page
    if int(par.page) >= 10 :
        name    = '[COLOR FF00FF00][PAGE -10][/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=MOVIE'
        u += '&name=%s'%urllib.quote_plus(name)
        u += '&lname=%s'%urllib.quote_plus(par.lname)
        #-- filter parameters
        u += '&page=%s'%urllib.quote_plus(str(int(par.page)-10))
        u += '&url=%s'%urllib.quote_plus(str(par.url))
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        xbmcplugin.addDirectoryItem(h, u, i, True)

def Empty():
    return False

#---------- movie list ---------------------------------------------------------
def Movie_List(params):
        #-- get filter parameters
        par = Get_Parameters(params)

        # show search dialog
        if par.search == 'Y':
            skbd = xbmc.Keyboard()
            skbd.setHeading('Поиск сериалов.')
            skbd.doModal()
            if skbd.isConfirmed():
                SearchStr = skbd.getText().split(':')
                par.search = SearchStr[0]
            else:
                return False

            #-- get and parce result
            Search_List(par)

        else:
            # -- get total number of movies and pages if not provided
            if par.count == 0:
                (par.max_page, par.count) = Get_Page_and_Movies_Count(par)

            # -- add header info
            Get_Header(par)

            #== get movie list =====================================================
            url = Get_URL(par)
            html = get_HTML(url)

            # -- parsing web page --------------------------------------------------
            soup = BeautifulSoup(html, fromEncoding="windows-1251")

            if soup.find("div", {"class":"new_movie15"}):
            # -- get movie info
                for rec in soup.findAll('div', {'class':'new_movie15'}):
                    mi.url      = rec.find('span', {'class':"new_movie8"}).find('a')['href']
                    if mi.url[0] == '/':
                        mi.url = 'http://kinokong.net'+ mi.url
                    mi.title    = rec.find('span', {'class':"new_movinfo1"}).text.encode('utf-8')
                    mi.genre    = rec.find('span', {'class':"new_movinfo2"}).text.encode('utf-8')
                    mi.img      = rec.find('span', {'class':re.compile("new_movie4")}).find('img')['src']
                    if mi.img[0] == '/':
                        mi.img = 'http://kinokong.net'+ mi.img

                    #-- paint title ---
                    try:
                        m = min(mi.title.index('/'), mi.title.index('('))
                    except:
                        try:
                            m = mi.title.index('/')
                        except:
                            try:
                                m = mi.title.index('(')
                            except:
                                m = len(mi.title)

                    title = '[COLOR FF00FFFF]'+mi.title[0:m]+'[/COLOR]'+mi.title[m:]

                    try:
                        mi.text = rec.find('span', {'class':"new_movinfo3"}).text
                    except:
                        mi.text =''

                    try:
                        mi.text = mi.text+' '+rec.find('span', {'class':"serials_season"}).text
                    except:
                        pass
                    mi.text = mi.text.encode('utf-8')

                    i = xbmcgui.ListItem(title, iconImage=mi.img, thumbnailImage=mi.img)
                    u = sys.argv[0] + '?mode=SOURCE'
                    u += '&shortname=%s'%urllib.quote_plus(mi.title[0:m])
                    u += '&name=%s'%urllib.quote_plus(mi.title)
                    u += '&url=%s'%urllib.quote_plus(mi.url)
                    u += '&img=%s'%urllib.quote_plus(mi.img)
                    i.setInfo(type='video', infoLabels={ 'title':       mi.title,
                                						 'genre':       mi.genre,
                                                         'plot':        mi.text})
                    #i.setProperty('fanart_image', mi.img)
                    xbmcplugin.addDirectoryItem(h, u, i, True)
            else:
                # -- get music info
                for rec in soup.findAll('div', {'class':'short_music'}):
                    for u in rec.findAll('a'):
                        if u['href'][-4:] == 'html':
                            mi.url = u['href']

                    if mi.url[0] == '/':
                        mi.url = 'http://kinokong.net'+ mi.url

                    mi.title    = rec.find('span', {'class':"short_music2"}).text.encode('utf-8')
                    mi.img      = rec.find('span', {'class':"short_music1"}).find('img')['src']
                    if mi.img[0] == '/':
                        mi.img = 'http://kinokong.net'+ mi.img

                    #-- paint title ---
                    try:
                        m = min(mi.title.index('/'), mi.title.index('('))
                    except:
                        try:
                            m = mi.title.index('/')
                        except:
                            try:
                                m = mi.title.index('(')
                            except:
                                m = len(mi.title)

                    title = '[COLOR FF00FFFF]'+mi.title[0:m]+'[/COLOR]'+mi.title[m:]

                    i = xbmcgui.ListItem(title, iconImage=mi.img, thumbnailImage=mi.img)
                    u = sys.argv[0] + '?mode=SOURCE'
                    u += '&shortname=%s'%urllib.quote_plus(mi.title[0:m])
                    u += '&name=%s'%urllib.quote_plus(mi.title)
                    u += '&url=%s'%urllib.quote_plus(mi.url)
                    u += '&img=%s'%urllib.quote_plus(mi.img)
                    i.setInfo(type='video', infoLabels={ 'title':       mi.title})
                    #i.setProperty('fanart_image', mi.img)
                    xbmcplugin.addDirectoryItem(h, u, i, True)

                #except:
                    #pass
            #-- next page link
            if int(par.page) < par.max_page :
                name    = '[COLOR FF00FF00][PAGE +1][/COLOR]'
                i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
                u = sys.argv[0] + '?mode=MOVIE'
                u += '&name=%s'%urllib.quote_plus(name)
                u += '&lname=%s'%urllib.quote_plus(par.lname)
                #-- filter parameters
                u += '&page=%s'%urllib.quote_plus(str(int(par.page)+1))
                u += '&url=%s'%urllib.quote_plus(par.url)
                u += '&genre=%s'%urllib.quote_plus(par.genre)
                xbmcplugin.addDirectoryItem(h, u, i, True)


            if int(par.page)+10 <= par.max_page :
                name    = '[COLOR FF00FF00][PAGE +10][/COLOR]'
                i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
                u = sys.argv[0] + '?mode=MOVIE'
                u += '&name=%s'%urllib.quote_plus(name)
                u += '&lname=%s'%urllib.quote_plus(par.lname)
                #-- filter parameters
                u += '&page=%s'%urllib.quote_plus(str(int(par.page)+10))
                u += '&url=%s'%urllib.quote_plus(str(par.url))
                u += '&genre=%s'%urllib.quote_plus(par.genre)
                xbmcplugin.addDirectoryItem(h, u, i, True)
            #xbmc.log("** "+str(pcount)+"  :  "+str(mcount))

        xbmcplugin.endOfDirectory(h)

#---------- search list --------------------------------------------------------
def Search_List(par):
    #-- get and parce result
    html = get_Search_HTML(par.search, 1) #-- get first page
    soup = BeautifulSoup(html, fromEncoding="windows-1251")

    #-- get mumber of find movies
    try:
        count = int(re.compile(u'найдено (.+?) ответ', re.MULTILINE|re.DOTALL).findall(soup.find('div', {'class':"info1"}).text)[0])
    except:
        count = 0

    if count > 30:  #-- limit to 30 returned records
        count = 30

    #-- show header
    info   = 'Поиск: '+ '[COLOR FF00FF00]'+ par.search +'[/COLOR]'
    info  += '  |  Найдено: ' + '[COLOR FFFFFF00]' + str(count) + '[/COLOR]'
    #-- info line
    name    = info
    i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
    u = sys.argv[0] + '?mode=EMPTY'
    u += '&name=%s'%urllib.quote_plus(name)
    #-- filter parameters
    u += '&page=%s'%urllib.quote_plus(par.page)
    u += '&genre=%s'%urllib.quote_plus(par.genre)
    u += '&max_page=%s'%urllib.quote_plus(str(par.max_page))
    u += '&count=%s'%urllib.quote_plus(str(par.count))
    xbmcplugin.addDirectoryItem(h, u, i, True)

    if soup.find("div", {"class":"new_movie15"}):
    # -- get movie info
        for rec in soup.findAll('div', {'class':'new_movie15'}):
            mi.url      = rec.find('span', {'class':"new_movie8"}).find('a')['href']
            if 'http://' not in mi.url:
                mi.url = 'http://kinokong.net'+ mi.url
            mi.title    = rec.find('span', {'class':"new_movinfo1"}).text.encode('utf-8')
            mi.genre    = rec.find('span', {'class':"new_movinfo2"}).text.encode('utf-8')
            mi.img      = rec.find('span', {'class':re.compile("new_movie4")}).find('img')['src']
            if mi.img[0] == '/':
                mi.img = 'http://kinokong.net'+ mi.img
            #-- paint title ---
            try:
                m = min(mi.title.index('/'), mi.title.index('('))
            except:
                try:
                    m = mi.title.index('/')
                except:
                    try:
                        m = mi.title.index('(')
                    except:
                        m = len(mi.title)

            title = '[COLOR FF00FFFF]'+mi.title[0:m]+'[/COLOR]'+mi.title[m:]

            try:
                mi.text = rec.find('span', {'class':"new_movinfo3"}).text
            except:
                mi.text =''

            try:
                mi.text = mi.text+' '+rec.find('span', {'class':"serials_season"}).text
            except:
                pass
            mi.text = mi.text.encode('utf-8')

            i = xbmcgui.ListItem(title, iconImage=mi.img, thumbnailImage=mi.img)
            u = sys.argv[0] + '?mode=SOURCE'
            u += '&shortname=%s'%urllib.quote_plus(mi.title[0:m])
            u += '&name=%s'%urllib.quote_plus(mi.title)
            u += '&url=%s'%urllib.quote_plus(mi.url)
            u += '&img=%s'%urllib.quote_plus(mi.img)
            i.setInfo(type='video', infoLabels={ 'title':       mi.title,
                        						 'genre':       mi.genre,
                                                 'plot':        mi.text})
            #i.setProperty('fanart_image', mi.img)
            xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- get number of find records and show header
    for rec in soup.findAll('div', {'class':"short_news"}):
        mi.url      = rec.find('a')['href']
        if 'http://' not in mi.url:
            mi.url = 'http://kinokong.net'+ mi.url
        mi.title    = rec.find('span', {'class':"short_news4"}).find('img')['alt'].encode('utf-8')
        mi.img      = rec.find('span', {'class':"short_news4"}).find('img')['src']
        if mi.img[0] == '/':
            mi.img = 'http://kinokong.net'+ mi.img
        mi.text     = rec.find('span', {'class':"short_news2"}).find('span').text.encode('utf-8')

        title = '[COLOR FF00FFFF]'+mi.title+'[/COLOR]'
        i = xbmcgui.ListItem(title, iconImage=mi.img, thumbnailImage=mi.img)
        u = sys.argv[0] + '?mode=SOURCE'
        u += '&shortname=%s'%urllib.quote_plus(mi.title)
        u += '&name=%s'%urllib.quote_plus(mi.title)
        u += '&url=%s'%urllib.quote_plus(mi.url)
        u += '&img=%s'%urllib.quote_plus(mi.img)
        i.setInfo(type='video', infoLabels={ 'title':       mi.title,
                                             'plot':        mi.text})
        xbmcplugin.addDirectoryItem(h, u, i, True)

#---------- source list --------------------------------------------------------
def Source_List(params):
    url  = urllib.unquote_plus(params['url'])
    img  = urllib.unquote_plus(params['img'])
    name = urllib.unquote_plus(params['name'])

    #== get movie list =====================================================
    list = Get_PlayList(url, name)

    if len(list) == 1:
        url = '*'

    for rec in list:
        lname = rec['name'].replace('<b>',' ').replace('</b>',' ')
        i = xbmcgui.ListItem(lname, iconImage=img, thumbnailImage=img)
        u = sys.argv[0] + '?mode=PLAY'
        u += '&name=%s'%urllib.quote_plus(name)
        u += '&url=%s'%urllib.quote_plus(rec['url'])
        u += '&img=%s'%urllib.quote_plus(img)
        u += '&pl=%s'%urllib.quote_plus(url)
        if url <> '*':
            try:
                u += '&sel=%s'%urllib.quote_plus(lname.encode('utf-8'))
            except:
                u += '&sel=%s'%urllib.quote_plus(lname)
        if 'shortname' in params:
            u += '&shortname=%s'%params['shortname']
        #i.setProperty('fanart_image', img)
        xbmcplugin.addDirectoryItem(h, u, i, False)

    xbmcplugin.endOfDirectory(h)

def Get_PlayList(url, name):
    html = get_HTML(url)
    list = []
    # -- parsing web page --------------------------------------------------
    soup = BeautifulSoup(html, fromEncoding="windows-1251")
    # -- get movie info
    allResults = soup.findAll('param', attrs={'name': 'flashvars'})
	#xbmc.log('[NOWFILMS.RU] found links =%s' %allResults)
    for res in allResults:
        video = ''
        #xbmc.log('[NOWFILMS.RU] processing result=%s' %res)
        for rec in res['value'].split('&'):
            #xbmc.log('[NOWFILMS.RU] processing rec=%s' %rec)
            if rec.split('=',2)[0] == 'pl':
                video = rec.split('=',1)[1]
            if rec.split('=',2)[0] == 'file':
                video = rec.split('=',1)[1]
            #if rec.split('=',1)[0] == 'st':
                #video = rec.split('=',1)[1]
        if video <> '':
            if video[-3:] == 'txt':
                html = get_HTML(video)
                html = html.replace('\n', '')
                if html[0] <> '[' and html[-1] == ']':
                    html = html[:-1]
                pl = json.loads(html.decode('utf-8'))

                for rec in pl['playlist']:
                    try:
                        for rec1 in rec['playlist']:
                            lname = (rec['comment']+' - '+rec1['comment']).replace('<b>','').replace('</b>','')
                            list.append({'name': lname, 'url': rec1['file']})
                    except:
                        lname = rec['comment'].replace('<b>','').replace('</b>','')
                        list.append({'name': lname, 'url': rec['file']})
            else:
				list.append({'name': name.replace('<b>','').replace('</b>',''), 'url': video})

    #if len(list) == 0:

    for res in re.compile('varflashvars={(.+?)}', re.MULTILINE|re.DOTALL).findall(soup.find('div', {'id':"dengger"}).text.replace(' ','')):
        video = ''
        #res = res.replace('"', '')

        for rec in res.split('",'):
            rec = rec.replace('"', '')
            #-- movie
            if rec.split(':', 1)[0] == 'file':
                video = rec.split(':', 1)[1]
            #-- serial
            if rec.split(':', 1)[0] == 'pl':
                video = rec.split(':', 1)[1]

        if video <> '':
            if video[-3:] == 'txt':
                html = get_HTML(video)
                html = html[html.index('{'):]

                html = html.replace('\n', '')
                if html[0] <> '[' and html[-1] == ']':
                	html = html[:-1]

                pl = json.loads(html.decode('utf-8'))

                for rec in pl['playlist']:
                	try:
                		for rec1 in rec['playlist']:
                			list.append({'name': rec['comment'].replace('<b>','').replace('</b>','')+' - '+rec1['comment'].replace('<b>','').replace('</b>',''), 'url': rec1['file']})
                	except:
                		list.append({'name': rec['comment'].replace('<b>','').replace('</b>',''), 'url': rec['file']})
            else:
                for v in video.split(','):
                    list.append({'name': name.replace('<b>','').replace('</b>','') +' ('+ v.split('.')[-2]+')', 'url': v})

    return list

#---------- get genge list -----------------------------------------------------
def Genre_List(params):
    #-- get filter parameters
    par = Get_Parameters(params)

    #-- get generes
    url = par.url
    html = get_HTML(url)

    # -- parsing web page ------------------------------------------------------
    soup = BeautifulSoup(html, fromEncoding="windows-1251")

    for rec in soup.find("div", {"class":"header_submenu"}).findAll('a'):
        if rec.text == u'Фильмы онлайн':
            break
        url      = 'http://kinokong.net/'+rec['href']

        name     = rec.text.encode('utf-8')

        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=MOVIE'
        u += '&name=%s'%urllib.quote_plus(name)
        #-- filter parameters
        u += '&page=%s'%urllib.quote_plus('1')
        u += '&genre=%s'%urllib.quote_plus(name)
        u += '&url=%s'%urllib.quote_plus(url)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(h)

#---------- get type list -----------------------------------------------------
def Type_List(params):
    #-- get filter parameters
    par = Get_Parameters(params)

    #-- get generes
    url = 'http://kinokong.net'
    html = get_HTML(url)

    # -- search ----------------------------------------------------------------
    name    = '[COLOR FF00FFF0]' + '[ПОИСК]' + '[/COLOR]'
    i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
    u = sys.argv[0] + '?mode=MOVIE'
    #-- filter parameters
    u += '&search=%s'%urllib.quote_plus('Y')
    xbmcplugin.addDirectoryItem(h, u, i, True)

    # -- parsing web page ------------------------------------------------------
    soup = BeautifulSoup(html, fromEncoding="windows-1251")

    for rec in soup.find('div', { 'class':"flymenu1"}).find('ul', {'class':"reset flymenu2"}).findAll('li'):
        if rec.find('a').text <> u'Топ' and rec.find('a')['href'] <> u'/viewed.html':
            if rec.find('span'):
                txt = rec.find('a').text+' :  '
                for t in rec.find('span').findAll('a'):
                    name = (txt+t.text.split('(')[0]).encode('utf-8')
                    lname = '[COLOR FF66FF66]'+txt.encode('utf-8')+'[/COLOR][COLOR FFFFCC33]'+t.text.split('(')[0].encode('utf-8')+'[/COLOR]'
                    url = 'http://kinokong.net/'+ t['href']

                    i = xbmcgui.ListItem(lname, iconImage=icon, thumbnailImage=icon)
                    u = sys.argv[0] + '?mode=MOVIE'
                    u += '&name=%s'%urllib.quote_plus(name)
                    u += '&lname=%s'%urllib.quote_plus(lname)
                    #-- filter parameters
                    u += '&page=%s'%urllib.quote_plus('1')
                    u += '&url=%s'%urllib.quote_plus(url)
                    xbmcplugin.addDirectoryItem(h, u, i, True)
            else:
                name = rec.find('a').text.encode('utf-8')
                lname = '[COLOR FF66FF66]'+name+'[/COLOR]'
                url  = rec.find('a')['href']
                if url[0] == '/':
                    url = 'http://kinokong.net'+ url

                i = xbmcgui.ListItem(lname, iconImage=icon, thumbnailImage=icon)
                u = sys.argv[0] + '?mode=MOVIE'
                u += '&name=%s'%urllib.quote_plus(name)
                u += '&lname=%s'%urllib.quote_plus(lname)
                #-- filter parameters
                u += '&page=%s'%urllib.quote_plus('1')
                u += '&url=%s'%urllib.quote_plus(url)
                xbmcplugin.addDirectoryItem(h, u, i, True)

    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(h)

#-------------------------------------------------------------------------------

def int_xx(intxx):
    if intxx and intxx!='None':
        return '%02d' % (int(intxx))
    else:
        return '00'

def mynewtitle(title, sel, name):

    #Debug('[mynewtitle]:'+str((title, sel, name)))

    for repl in ['Сериал ', 'Смотреть ', 'Фильм ']:
        if title.startswith(repl): title=title.replace(repl,'', 1)

    if sel:
        season,episode=None,None
        match=re.compile('(\d+) (Cезон|cезон|Сезон|сезон|Season|season)').findall(sel)
        if match:
            season=int_xx(match[0][0])
        else:
            match=re.compile('(\d+) (Cезон|cезон|Сезон|сезон|Season|season)').findall(name)
            if match:
                season=int_xx(match[0][0])
        if season:
            match=re.compile('(\d+) (Cерия|cерия|Серия|серия|Episod|episod)').findall(sel)
            if match:
                episode=int_xx(match[0][0])
        if season and episode:
            title=title+'S%sE%s.flv'%(season,episode)

    return title

#-------------------------------------------------------------------------------

def PLAY(params):
    # -- parameters
    url     = urllib.unquote_plus(params['url'])
    img     = urllib.unquote_plus(params['img'])
    name    = urllib.unquote_plus(params['name'])
    plurl   = urllib.unquote_plus(params['pl'])

    if plurl == '*':
        # -- play video
        if 'shortname' in params:
            name=mynewtitle(name, None, None)
        i = xbmcgui.ListItem(name, path = urllib.unquote(url), thumbnailImage=img)
        xbmc.Player().play(url, i)
    else:
        sel     = urllib.unquote_plus(params['sel'])
        pl=xbmc.PlayList(1)
        pl.clear()
        flag = 0

        list = Get_PlayList(plurl, name)

        for rec in list:
            if rec['name'].encode('utf-8') == sel:
                flag = 1

            if flag == 1:
                newtitle=rec['name']
                if 'shortname' in params:
                    newtitle=mynewtitle(urllib.unquote_plus(params['shortname']), sel, name)

                i = xbmcgui.ListItem(newtitle, path = urllib.unquote(rec['url']), thumbnailImage=img)
##                i = xbmcgui.ListItem(rec['name'], path = urllib.unquote(rec['url']), thumbnailImage=img)
                i.setProperty('IsPlayable', 'true')
                pl.add(rec['url'], i)

        xbmc.Player().play(pl)

#-------------------------------------------------------------------------------

def unescape(text):
    try:
        text = hpar.unescape(text)
    except:
        text = hpar.unescape(text.decode('utf8'))

    try:
        text = unicode(text, 'utf-8')
    except:
        text = text

    return text

def get_url(url):
    return "http:"+urllib.quote(url.replace('http:', ''))

#-------------------------------------------------------------------------------
def get_params(paramstring):
	param=[]
	if len(paramstring)>=2:
		params=paramstring
		cleanedparams=params.replace('?','')
		if (params[len(params)-1]=='/'):
			params=params[0:len(params)-2]
		pairsofparams=cleanedparams.split('&')
		param={}
		for i in range(len(pairsofparams)):
			splitparams={}
			splitparams=pairsofparams[i].split('=')
			if (len(splitparams))==2:
				param[splitparams[0]]=splitparams[1]
	return param

def Initialize():

    url = 'http://kinokong.net/index.php'
    html = get_HTML(url)

    login       = Addon.getSetting('Login')
    password    = Addon.getSetting('Password')

	#if login == None:
	#	return

    values = {
          'login'	      :  'submit',
          'login_name'	  :  login,
          'login_password':  password
        }

    post = urllib.urlencode(values)
    html = get_HTML(url, post)

    Set_Order(1)

def Set_Order(ignor):
    #--------- set sort order ---------------------------
    val = Addon.getSetting('sortval')

    if val == Addon.getSetting('last_sortval') and ignor == 0:
        return

    Addon.setSetting(id='last_sortval', value=val)
    if (val == str(0)):      #-- алфавит
        _dir = 'asc'
        _sort= 'title'
    elif (val == str(1)):    #-- дата
        _dir = 'desc'
        _sort= 'date'
    else:               #-- КиноПоиск
        _dir = 'desc'
        _sort= 'kp_rating'

    url = 'http://kinokong.net/serial/boeviki/'
    values = {  'dlenewssortby'       : _sort,
                'dledirection'        : _dir,
                'set_new_sort'        :'dle_sort_cat',
                'set_direction_sort'  :'dle_direction_cat'
             }

    post = urllib.urlencode(values)
    html = get_HTML(url, post)


#-------------------------------------------------------------------------------
params=get_params(sys.argv[2])

# get cookies from last session
cj = cookielib.MozillaCookieJar(fcookies)
try:
	cj.load(fcookies, True, True)
except:
	pass

hr  = urllib2.HTTPCookieProcessor(cj)
opener = urllib2.build_opener(hr)
urllib2.install_opener(opener)

p  = Param()
mi = Info()

mode = None

try:
    mode = urllib.unquote_plus(params['mode'])
    Set_Order(0)
except:
	Initialize()
	Type_List(params)

if mode == 'MOVIE':
	Movie_List(params)
if mode == 'SOURCE':
	Source_List(params)
elif mode == 'GENRES':
	Genre_List(params)
elif mode == 'EMPTY':
	Empty()
elif mode == 'PLAY':
	PLAY(params)

cj.save(fcookies, True, True)
