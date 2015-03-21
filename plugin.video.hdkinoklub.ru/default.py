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
import urlparse, json
import subprocess

from subprocess import Popen, PIPE, STDOUT

import xbmc, xbmcgui, xbmcplugin, xbmcaddon

Addon = xbmcaddon.Addon(id='plugin.video.hdkinoklub.ru')
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

#---------- parameter/info structure -------------------------------------------
class Param:
    page        = '1'
    genre       = ''
    genre_name  = ''
    max_page    = 0
    count       = 0
    url         = ''
    search      = ''

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

#---------- get web page -------------------------------------------------------
def get_HTML(url, post = None, ref = None, l = None):
    request = urllib2.Request(url, post)

    xbmc.log(url)

    host = urlparse.urlsplit(url).hostname
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

    if l == None:
        html = f.read()
    else:
        html = f.read(l)

    return html


def makeCookie(name, value):
    return cookielib.Cookie(
        version=0,
        name=name,
        value=value,
        port=None,
        port_specified=False,
        domain="hdkinoklub.ru",
        domain_specified=True,
        domain_initial_dot=False,
        path="/",
        path_specified=True,
        secure=False,
        expires=None,
        discard=False,
        comment=None,
        comment_url=None,
        rest=None
    )

def is_Activated():
    for c in cj:
        if c.name == 'BPC' and c.domain == 'hdkinoklub.ru':
            return

    #-- activate
    url = 'http://hdkinoklub.ru'
    html = get_HTML(url)

    c_name  = ''
    c_value = ''
    c = ''

    soup = BeautifulSoup(html, fromEncoding="windows-1251")

    for rec in soup.find('script').text.split(';'):
        if rec.split('="')[0] == 'document.cookie':
            c = rec.split('="')[1].replace('"', '').split('=')
            c_name  = c[0]
            c_value = c[1]

            cookie = makeCookie(c_name, c_value)
            cj.set_cookie(cookie)

#---------- get parameters -----------------------------------------------------
def Get_Parameters(params):
    #-- page
    try:    p.page = urllib.unquote_plus(params['page'])
    except: p.page = '1'
    #-- genre
    try:    p.genre = urllib.unquote_plus(params['genre'])
    except: p.genre = ''

    try:    p.genre_name = urllib.unquote_plus(params['genre_name'])
    except: p.genre_name = ''
    # movie count
    try:    p.max_page = int(urllib.unquote_plus(params['max_page']))
    except: p.max_page = 0
    # movie count
    try:    p.count = int(urllib.unquote_plus(params['count']))
    except: p.count = 0
    #-- url
    try:    p.url = urllib.unquote_plus(params['url'])
    except: p.url = ''
    #-- search
    try:    p.search = urllib.unquote_plus(params['search'])
    except: p.search = ''

    #-----
    return p

#---------- get HD720.RU URL --------------------------------------------------
def Get_URL(par):
    url = 'http://hdkinoklub.ru'
    #-- genre
    if par.genre <> '':
        url += par.genre
    #-- page
    url += '/page/'+par.page+'/'

    return url


# ----- search on site --------------------------------------------------------
def get_Search_HTML(search_str):
    url = 'http://hdkinoklub.ru/index.php?do=search'
    str = search_str.decode('utf-8').encode('windows-1251')
    values = {
            'do'	        : 'search',
            'story'         : str,
            'subaction'	    : 'search',
            'full_search'	: 1,
            'result_from'	: 1,
            'result_num'	: 100,
            'search_start'	: 1,
            'beforeafter'	: 'after',
            'catlist[]'	    : 0,
            'replyless'	    : 0,
            'replylimit'	: 0,
            'resorder'	    : 'asc',
            'searchdate'	: 0,
            'searchuser'    : '',
            'showposts'	    : 0,
            'sortby'	    : 'title',
            'titleonly'	    : 3
        }

    post = urllib.urlencode(values)
    html = get_HTML(url, post)
    return html


#----------- get page count & number of movies ---------------------------------
def Get_Page_and_Movies_Count(par):
    url = 'http://hdkinoklub.ru'
    #-- genre
    if par.genre <> '':
        url += par.genre
    html = get_HTML(url)
    # -- parsing web page ------------------------------------------------------
    soup = BeautifulSoup(html) #, fromEncoding="windows-1251")
    max_page = 0

    for rec in soup.find('div',{'class':'navigation'}).findAll('a'):
        try:
            if max_page < int(rec.text):
                max_page = int(rec.text)
        except:
            pass
    #-- #2 -------------------------------------------------------------------------
    url += '/page/%i/'%max_page
    html = get_HTML(url)

    # -- parsing web page ------------------------------------------------------
    soup = BeautifulSoup(html, fromEncoding="windows-1251")
    count = 10*(max_page-1)+len(soup.find('div',{'id':'dle-content'}).findAll('div',{'class':'short'}))

    return max_page, count


#----------- get Header string -------------------------------------------------
def Get_Header(par):

    info  = 'Фильмов: ' + '[COLOR FF00FF00]' + str(par.count) + '[/COLOR]'

    if par.max_page > 1:
        info += ' | Pages: ' + '[COLOR FF00FF00]'+ par.page + '/' + str(par.max_page) +'[/COLOR]'

    if par.genre <> '':
        info += ' | Жанр: ' + '[COLOR FF00FFF0]'+ par.genre_name + '[/COLOR]'

    if par.search <> '':
        info += ' | Поиск: ' + '[COLOR FFFFFF00]'+ par.search + '[/COLOR]'

    #-- info line
    name    = info
    i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
    u = sys.argv[0] + '?mode=EMPTY'
    u += '&name=%s'%urllib.quote_plus(name)
    #-- filter parameters
    u += '&page=%s'%urllib.quote_plus(par.page)
    u += '&genre=%s'%urllib.quote_plus(par.genre)
    u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
    u += '&max_page=%s'%urllib.quote_plus(str(par.max_page))
    u += '&count=%s'%urllib.quote_plus(str(par.count))
    xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- search
    if par.genre == '' and par.page == '1' and par.search == '':
        name    = '[COLOR FFFFFF00]' + '[ПОИСК]' + '[/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=MOVIE'
        #-- filter parameters
        u += '&search=%s'%urllib.quote_plus('Y')
        u += '&name=%s'%urllib.quote_plus(name)
        #-- filter parameters
        u += '&page=%s'%urllib.quote_plus(str(int(par.page)-1))
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&max_page=%s'%urllib.quote_plus(str(par.max_page))
        u += '&count=%s'%urllib.quote_plus(str(par.count))
        xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- genres
    if par.genre == '' and par.page == '1':
        name    = '[COLOR FF00FFF0][Жанры][/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=GENRES'
        u += '&name=%s'%urllib.quote_plus(name)
        #-- filter parameters
        u += '&page=%s'%urllib.quote_plus(par.page)
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&max_page=%s'%urllib.quote_plus(str(par.max_page))
        u += '&count=%s'%urllib.quote_plus(str(par.count))
        xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- previous page
    if int(par.page) > 1 :
        name    = '[COLOR FF00FF00][PAGE -1][/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=MOVIE'
        u += '&name=%s'%urllib.quote_plus(name)
        #-- filter parameters
        u += '&page=%s'%urllib.quote_plus(str(int(par.page)-1))
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&max_page=%s'%urllib.quote_plus(str(par.max_page))
        u += '&count=%s'%urllib.quote_plus(str(par.count))
        xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- previous page
    if int(par.page) >= 10 :
        name    = '[COLOR FF00FF00][PAGE -10][/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=MOVIE'
        u += '&name=%s'%urllib.quote_plus(name)
        #-- filter parameters
        u += '&page=%s'%urllib.quote_plus(str(int(par.page)-10))
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&max_page=%s'%urllib.quote_plus(str(par.max_page))
        u += '&count=%s'%urllib.quote_plus(str(par.count))
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
            html = get_Search_HTML(par.search).replace('<br/>','|')
            soup = BeautifulSoup(html, fromEncoding="windows-1251")

            par.max_page = 1
            try:
                txt = soup.find('div', {'class':'info'}).text
                par.count = int(re.compile(u'Вашему запросу найдено (.+?) ответов', re.MULTILINE|re.DOTALL).findall(txt)[0])
            except:
                return False

            is_search = True
        else:
            # -- get total number of movies and pages if not provided
            if par.count == 0:
                (par.max_page, par.count) = Get_Page_and_Movies_Count(par)

            #== get movie list =====================================================
            url = Get_URL(par)
            html = get_HTML(url).replace('<br/>','|')

            # -- parsing web page --------------------------------------------------
            soup = BeautifulSoup(html, fromEncoding="windows-1251")
            is_search = False

        # -- add header info
        Get_Header(par)

        # -- get movie info
        for rec in soup.find('div',{'id':'dle-content'}).findAll('div',{'class':'short'}):
            try:
                #--
                r = rec.find('div',{'class':'short2'}).find('h2')
                try:
                    mi.url      = r.find('a')['href']
                except:
                    continue
                mi.title    = r.find('a').text.encode('utf-8')
                #--
                mi.img      = rec.find('div',{'class':'short1'}).find('img')['src']
                if mi.img[0] == '/':
                    mi.img =  'http://hdkinoklub.ru'+mi.img

                mi.text  = rec.find('div',{'class':'short3'}).find('span').text.encode('utf-8')
                #--
                mi.year  = int(rec.find('div',{'class':'short4'}).find('span',{'class':'short155'}).text)
                mi.genre = rec.find('div',{'class':'short2'}).find('span').text

                #--
                i = xbmcgui.ListItem(mi.title, iconImage=mi.img, thumbnailImage=mi.img)
                u = sys.argv[0] + '?mode=SOURCE'
                u += '&name=%s'%urllib.quote_plus(mi.title)
                u += '&url=%s'%urllib.quote_plus(mi.url)
                u += '&img=%s'%urllib.quote_plus(mi.img)
                i.setInfo(type='video', infoLabels={ 'title':      mi.title,
                            						 'year':        mi.year,
                            						 'genre':       mi.genre,
                                					 'plot':        mi.text
                                                   })
                #i.setProperty('fanart_image', mi.img)
                xbmcplugin.addDirectoryItem(h, u, i, True)
            except:
                pass

        #-- next page link
        if int(par.page) < par.max_page and is_search == False:
            name    = '[COLOR FF00FF00][PAGE +1][/COLOR]'
            i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
            u = sys.argv[0] + '?mode=MOVIE'
            u += '&name=%s'%urllib.quote_plus(name)
            #-- filter parameters
            u += '&page=%s'%urllib.quote_plus(str(int(par.page)+1))
            u += '&genre=%s'%urllib.quote_plus(par.genre)
            u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
            u += '&max_page=%s'%urllib.quote_plus(str(par.max_page))
            u += '&count=%s'%urllib.quote_plus(str(par.count))
            xbmcplugin.addDirectoryItem(h, u, i, True)

        if int(par.page)+10 <= par.max_page and is_search == False:
            name    = '[COLOR FF00FF00][PAGE +10][/COLOR]'
            i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
            u = sys.argv[0] + '?mode=MOVIE'
            u += '&name=%s'%urllib.quote_plus(name)
            #-- filter parameters
            u += '&page=%s'%urllib.quote_plus(str(int(par.page)+10))
            u += '&genre=%s'%urllib.quote_plus(par.genre)
            u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
            u += '&max_page=%s'%urllib.quote_plus(str(par.max_page))
            u += '&count=%s'%urllib.quote_plus(str(par.count))
            xbmcplugin.addDirectoryItem(h, u, i, True)
        #xbmc.log("** "+str(pcount)+"  :  "+str(mcount))

        xbmcplugin.endOfDirectory(h)

#---------- source list ---------------------------------------------------------
def Source_List(params):
    url  = urllib.unquote_plus(params['url'])
    img  = urllib.unquote_plus(params['img'])
    name = urllib.unquote_plus(params['name'])

    #== get movie list =====================================================
    html = get_HTML(url)
    # -- parsing web page --------------------------------------------------
    soup = BeautifulSoup(html, fromEncoding="windows-1251")
    # -- get movie info

    name_list = []
    for rec in soup.find('div', {'class' : "section"}).find('ul', {'class':'tabs'}).findAll('li'):
        name_list.append(rec.text.encode('utf-8'))

    #-- get video --------------------------------------------------------------
    idx = 0
    for rec in soup.findAll('iframe'):
        if "http://kodik.biz" in rec['src'] and Addon.getSetting('Kodik.Biz') == 'true':
            s_url   = rec['src']
            for r in Kodik_Biz(s_url):   ## q, s_url =
                s_title = '[COLOR FF00FF00]'+name_list[idx]
                if len(r['name']) > 0:
                    s_title = s_title + ' '+ r['name']
                s_title = s_title +' ([/COLOR][COLOR FF00FFFF]Kodik.biz ('+str(r['quality'])+')[/COLOR][COLOR FF00FF00])[/COLOR]'
                #--
                i = xbmcgui.ListItem(s_title+' '+name, iconImage=img, thumbnailImage=img)
                u = sys.argv[0] + '?mode=PLAY'
                u += '&name=%s'%urllib.quote_plus(s_title+' '+name)
                u += '&url=%s'%urllib.quote_plus(r['url'])
                u += '&img=%s'%urllib.quote_plus(img)
                u += '&vtype=%s'%urllib.quote_plus('VM')
                #i.setProperty('fanart_image', img)
                xbmcplugin.addDirectoryItem(h, u, i, False)

        elif 'video_ext.php' in rec['src']:
            s_url   = rec['src']

            #-- check url
            if 'vk.com/video_ext.php?' not in s_url:
                html = get_HTML(s_url)
                soup = BeautifulSoup(html, fromEncoding="windows-1251")
                for rec in soup.findAll('iframe', {'src' : re.compile('video_ext.php\?')}): #\?
                    s_url   = rec['src']

            s_title = '[COLOR FF00FF00]'+name_list[idx]+' ([/COLOR][COLOR FF00FFFF]ВКонтакте[/COLOR][COLOR FF00FF00])[/COLOR]'
            #--
            i = xbmcgui.ListItem(s_title+' '+name, iconImage=img, thumbnailImage=img)
            u = sys.argv[0] + '?mode=PLAY'
            u += '&name=%s'%urllib.quote_plus(s_title+' '+name)
            u += '&url=%s'%urllib.quote_plus(s_url)
            u += '&img=%s'%urllib.quote_plus(img)
            u += '&vtype=%s'%urllib.quote_plus('VK')
            #i.setProperty('fanart_image', img)
            xbmcplugin.addDirectoryItem(h, u, i, False)

        idx = idx+1
##    #-- RuVideo ----------------------------------------------------------------
##    for rec in soup.findAll('param', {'name':'flashvars'}):
##        for s in rec['value'].split('&'):
##            if s.split('=',1)[0] == 'file':
##                s_url = s.split('=',1)[1]
##        s_title = '[COLOR FF00FF00]SOURCE #'+str(source_number)+' ([/COLOR][COLOR FFFF00FF]RuVideo[/COLOR][COLOR FF00FF00])[/COLOR]'
##        source_number = source_number + 1
##        #--
##        i = xbmcgui.ListItem(s_title+' '+name, iconImage=img, thumbnailImage=img)
##        u = sys.argv[0] + '?mode=PLAY'
##        u += '&name=%s'%urllib.quote_plus(s_title+' '+name)
##        u += '&url=%s'%urllib.quote_plus(s_url)
##        u += '&img=%s'%urllib.quote_plus(img)
##        u += '&vtype=%s'%urllib.quote_plus('RV')
##        #i.setProperty('fanart_image', img)
##        xbmcplugin.addDirectoryItem(h, u, i, False)

    xbmcplugin.endOfDirectory(h)

#---------- get genge list -----------------------------------------------------
def Genre_List(params):
    #-- get filter parameters
    par = Get_Parameters(params)

    #-- get generes
    url = 'http://hdkinoklub.ru/'
    html = get_HTML(url)

    # -- parsing web page ------------------------------------------------------
    soup = BeautifulSoup(html, fromEncoding="windows-1251")

    for rec in soup.find('div', {'class':'top_menu'}).find('ul', {'class':'reset'}).findAll('li'):
        if rec.find('a').text == u'Жанры':
            for r in rec.find('ul', {'class':'reset'}).findAll('li'):
                name     = unescape(r.find('a').text).encode('utf-8')
                genre_id = r.find('a')['href']

                i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
                u = sys.argv[0] + '?mode=MOVIE'
                u += '&name=%s'%urllib.quote_plus(name)
                #-- filter parameters
                u += '&page=%s'%urllib.quote_plus(par.page)
                u += '&genre=%s'%urllib.quote_plus(genre_id)
                u += '&genre_name=%s'%urllib.quote_plus(name)
                xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- add serials
    name     = 'Сериалы'
    genre_id = '/serialy'

    i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
    u = sys.argv[0] + '?mode=MOVIE'
    u += '&name=%s'%urllib.quote_plus(name)
    #-- filter parameters
    u += '&page=%s'%urllib.quote_plus(par.page)
    u += '&genre=%s'%urllib.quote_plus(genre_id)
    u += '&genre_name=%s'%urllib.quote_plus(name)
    xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- add new movies
    name     = 'Новинки кино'
    genre_id = '/novinki'

    i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
    u = sys.argv[0] + '?mode=MOVIE'
    u += '&name=%s'%urllib.quote_plus(name)
    #-- filter parameters
    u += '&page=%s'%urllib.quote_plus(par.page)
    u += '&genre=%s'%urllib.quote_plus(genre_id)
    u += '&genre_name=%s'%urllib.quote_plus(name)
    xbmcplugin.addDirectoryItem(h, u, i, True)

    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(h)


#-------------------------------------------------------------------------------

def PLAY(params):
    try:
        # -- parameters
        url   = urllib.unquote_plus(params['url'])
        img   = urllib.unquote_plus(params['img'])
        name  = urllib.unquote_plus(params['name'])
        vtype = urllib.unquote_plus(params['vtype'])

        if url == '*':
            return False

        video = url
        # -- get VKontakte video url
        if vtype == 'VK':
            url = url.replace('vkontakte.ru', 'vk.com')
            html = get_HTML(url)

            soup = BeautifulSoup(html, fromEncoding="windows-1251")

            for rec in soup.findAll('script', {'type':'text/javascript'}):
                if 'video_host' in rec.text:
                    for r in re.compile('var (.+?) = \'(.+?)\';').findall(html):
                        if r[0] == 'video_host':
                            video_host = r[1]#.replace('userapi', 'vk')
                        if r[0] == 'video_uid':
                            video_uid = r[1]
                        if r[0] == 'video_vtag':
                            video_vtag = r[1]
            video = '%su%s/videos/%s.720.mp4'%(video_host, video_uid, video_vtag)
            html = get_HTML(video, None, None, 1000)


            for rec in soup.findAll('param', {'name':'flashvars'}):
                for s in rec['value'].split('&'):
                    if s.split('=',1)[0] == 'uid':
                        uid = s.split('=',1)[1]
                    if s.split('=',1)[0] == 'vtag':
                        vtag = s.split('=',1)[1]
                    if s.split('=',1)[0] == 'host':
                        host = s.split('=',1)[1]
                    if s.split('=',1)[0] == 'vid':
                        vid = s.split('=',1)[1]
                    if s.split('=',1)[0] == 'oid':
                        oid = s.split('=',1)[1]

            url = 'http://vk.com/videostats.php?act=view&oid='+oid+'&vid='+vid+'&quality=720'
            ref = 'http://vk.com'+soup.find('param',{'name':'movie'})['value']
            html = get_HTML(url, None, ref)

        # -- play video
        i = xbmcgui.ListItem(name, video, thumbnailImage=img)
        xbmc.Player().play(video, i)
    except:
        pass

#-- conver video urk from kodik.biz --------------------------------------------
def Kodik_Biz(vurl):
    list = []
    #--
    html = get_HTML(vurl)
    soup = BeautifulSoup(html, fromEncoding="windows-1251")

    if soup.find('div', {'class':'serial-series-box'}):
        for rec in soup.find('div', {'class':'serial-series-box'}).findAll('option'):
            for r in Kodik_Biz(rec['value']):
                list.append({'name':rec.text.encode('utf-8'), 'quality':r['quality'], 'url':r['url']})
    else:
        try:
            for rec in soup.findAll('script', {'type':'text/javascript'}):
                if 'eval(' in rec.text:
                    code = rec.text
                    break

            url = Run_Java(code)
            html = get_HTML(url)

            str = html.replace('responseWork(','')[:-2]
            j = json.loads(str)
            quality = 0

            for key, value in  j['response'].items():
                if key.find('url') != -1 and len(key) < 8:
                    if int(key.replace('url', '')) > quality:
                        quality = int(key.replace('url', ''))
                        url     = value

            if quality == 0:
                quality = 720
                url = j['response']['host']+'u'+j['response']['uid']+'/videos/'+j['response']['vtag']+'.720.mp4'

            list.append({'name':'', 'quality':quality, 'url':url})
        except:
            pass

    return list

def Run_Java(code):
    js_code = code + ';"http://api.vk.com/method/video.getEmbed?oid=" + s1 + "&video_id=" + s2 +"&embed_hash=" + s3 +"&callback=responseWork";'

    node_js = Addon.getSetting('Node.JS_Path')

    startupinfo = None
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= 1

    p = subprocess.Popen([node_js, '-p'], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE,shell= False, startupinfo=startupinfo)
    rez = p.communicate(input = js_code)[0]

    return rez


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
#-------------------------------------------------------------------------------
params=get_params(sys.argv[2])

# get cookies from last session
cj = cookielib.MozillaCookieJar(fcookies)
hr  = urllib2.HTTPCookieProcessor(cj)
opener = urllib2.build_opener(hr)
urllib2.install_opener(opener)

p  = Param()
mi = Info()

mode = None

is_Activated()

try:
	mode = urllib.unquote_plus(params['mode'])
except:
	Movie_List(params)

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


