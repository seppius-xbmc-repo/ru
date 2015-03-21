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
import re, os, urllib, cookielib, time
from time import gmtime, strftime
import urlparse, urllib2

import xbmc, xbmcgui, xbmcplugin, xbmcaddon

Addon = xbmcaddon.Addon(id='plugin.video.cinema.mosfilm.ru')
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

host_url = 'http://cinema.mosfilm.ru'
movie_url = None

def showMessage(heading, message, times = 3000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))

#---------- parameter/info structure -------------------------------------------
class Param:
    page    = '1'
    genre   = '?'
    genre_name = 'Все'
    country  = ''
    country_name = ''
    year    = '/films/'
    year_name = 'Все'
    search  = ''
    url     = ''
    prev_url= ''

class Info:
    img         = ''
    url         = '*'
    title       = ''
    year        = ''
    genre       = ''
    country     = ''
    director    = ''
    text        = ''
    actors      = ''

#---------- get parameters -----------------------------------------------------
def Get_Parameters(params):
    #-- page
    try:    p.page = urllib.unquote_plus(params['page'])
    except: p.page = '1'
    #-- genre
    try:    p.genre = urllib.unquote_plus(params['genre'])
    except: p.genre = '?'
    try:    p.genre_name = urllib.unquote_plus(params['genre_name'])
    except: p.genre_name = 'Все'
    #-- year
    try:    p.year = urllib.unquote_plus(params['year'])
    except: p.year = '/films/'
    try:    p.year_name = urllib.unquote_plus(params['year_name'])
    except: p.year_name = 'Все'
    #--search
    try:    p.search = urllib.unquote_plus(params['search'])
    except: p.search = ''
    #--url
    try:    p.url = urllib.unquote_plus(params['url'])
    except: p.url = ''
    try:    p.prev_url = urllib.unquote_plus(params['prev_url'])
    except: p.prev_url = ''
    #-----
    return p

#---------- get web page -------------------------------------------------------
def get_HTML(url, post = None, ref = None):

    print url

    request = urllib2.Request(url, post)
    host = urlparse.urlsplit(url).hostname

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

#---------- get MY-HIT.RU URL --------------------------------------------------
def Get_URL(par):

    if par.page == '1':
        url = host_url+par.year+par.genre
    else:
        url = par.url

    return url

#----------- get Header string ---------------------------------------------------
def Get_Header(par):

    info  = 'Page: ' + '[COLOR FF00FF00]'+ par.page +'[/COLOR]'

    if par.genre <> '':
        info += ' | Жанр: ' + '[COLOR FF00FFF0]'+ par.genre_name + '[/COLOR]'

    if par.year <> '':
        info += ' | Год: ' + '[COLOR FFFFF000]'+ par.year_name + '[/COLOR]'

    if par.search <> '':
        info += ' | Поиск: ' + '[COLOR FFFF9933]'+ par.search + '[/COLOR]'

    #-- info line
    name    = info
    i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
    u = sys.argv[0] + '?mode=EMPTY'
    u += '&name=%s'%urllib.quote_plus(name)
    #-- filter parameters
    u += '&page=%s'%urllib.quote_plus(par.page)
    u += '&genre=%s'%urllib.quote_plus(par.genre)
    u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
    u += '&country=%s'%urllib.quote_plus(par.country)
    u += '&country_name=%s'%urllib.quote_plus(par.country_name)
    u += '&year=%s'%urllib.quote_plus(par.year)
    u += '&year_name=%s'%urllib.quote_plus(par.year_name)
    xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- search
    '''
    if par.genre == '' and par.country == '' and par.page == '1' and par.search == '':
        name    = '[COLOR FFFF9933][Поиск][/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=SEARCH'
        u += '&name=%s'%urllib.quote_plus(name)
        #-- filter parameters
        u += '&page=%s'%urllib.quote_plus(par.page)
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&country=%s'%urllib.quote_plus(par.country)
        u += '&country_name=%s'%urllib.quote_plus(par.country_name)
        u += '&year=%s'%urllib.quote_plus(par.year)
        u += '&year_name=%s'%urllib.quote_plus(par.year_name)
        xbmcplugin.addDirectoryItem(h, u, i, True)
    '''
    #-- genres
    if par.search == '': #-- par.page == '1' and
        name    = '[COLOR FF00FFF0][Жанры][/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=GENRES'
        u += '&name=%s'%urllib.quote_plus(name)
        #-- filter parameters
        u += '&page=%s'%urllib.quote_plus(par.page)
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&country=%s'%urllib.quote_plus(par.country)
        u += '&country_name=%s'%urllib.quote_plus(par.country_name)
        u += '&year=%s'%urllib.quote_plus(par.year)
        u += '&year_name=%s'%urllib.quote_plus(par.year_name)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- year
    if par.search == '': #-- par.page == '1' and
        name    = '[COLOR FFFFF000][Год][/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=YEAR'
        u += '&name=%s'%urllib.quote_plus(name)
        #-- filter parameters
        u += '&page=%s'%urllib.quote_plus(par.page)
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&country=%s'%urllib.quote_plus(par.country)
        u += '&country_name=%s'%urllib.quote_plus(par.country_name)
        u += '&year=%s'%urllib.quote_plus(par.year)
        u += '&year_name=%s'%urllib.quote_plus(par.year_name)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- next page link
        if par.page != '1':
            url = par.prev_url

            name    = '[PAGE-1]'
            i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
            u = sys.argv[0] + '?mode=MOVIE'
            u += '&name=%s'%urllib.quote_plus(name)
            #-- filter parameters
            u += '&page=%s'%urllib.quote_plus(str(int(par.page)-1))
            u += '&genre=%s'%urllib.quote_plus(par.genre)
            u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
            u += '&year=%s'%urllib.quote_plus(par.year)
            u += '&year_name=%s'%urllib.quote_plus(par.year_name)
            u += '&url=%s'%urllib.quote_plus(url)
            xbmcplugin.addDirectoryItem(h, u, i, True)

def Empty():
    return False

#---------- movie list ---------------------------------------------------------
def Movie_List(params):
        #-- get filter parameters
        par = Get_Parameters(params)

        #== get movie list =====================================================
        url = Get_URL(par)
        html = get_HTML(url)

        # -- parsing web page --------------------------------------------------
        soup = BeautifulSoup(html)

        Get_Header(par)

        for rec in soup.findAll('div', {'class':"item"}):
            try:
                mi.title = rec.find('div', {'class':"title"}).text.encode('utf-8')
                mi.img   = 'http://cinema.mosfilm.ru/'+rec.find('div', {'class':"img actt"}).find('img')['src']
                mi.url   = 'http://cinema.mosfilm.ru/'+rec.find('div', {'class':"img actt"}).find('a')['href']
                mi.text  = rec.find('div', {'class':"descr"}).text.encode('utf-8')
                for r in rec.find('div', {'class':"creators"}).findAll('p'):
                    if (r.find('b').text) == u'Режиссер:':
                        mi.director = r.text.split(':',1)[1].encode('utf-8')
                    if (r.find('b').text) == u'Актеры:':
                        mi.actors   = r.text.split(':',1)[1].encode('utf-8')
                info = rec.find('div', {'class':"info"}).text.split(' | ')
                mi.year  = info[0].encode('utf-8')
                mi.genre = info[1].encode('utf-8')

                name = '[COLOR FFC3FDB8]'+mi.title+'[/COLOR]'

                i = xbmcgui.ListItem(name, iconImage=mi.img, thumbnailImage=mi.img)
                u = sys.argv[0] + '?mode=PLAY_LIST'
                u += '&name=%s'%urllib.quote_plus(mi.title)
                u += '&url=%s'%urllib.quote_plus(mi.url)
                u += '&img=%s'%urllib.quote_plus(mi.img)
                i.setInfo(type='video', infoLabels={'title':       mi.title,
                            						'year':        mi.year,
                            						'director':    mi.director,
                            						'plot':        mi.text,
                            						'artist':      mi.actors.split(','),
                            						'genre':       mi.genre})
                i.setProperty('fanart_image', mi.img)
                xbmcplugin.addDirectoryItem(h, u, i, True)
            except:
                pass

        #-- next page link
        try:
            r = soup.find('div', {'class':"show-more-center"}).find('a')

            if r['href'] != '#':
                url = host_url+r['href']
            else:
                url = 'http://cinema.mosfilm.ru/ajax/films/pager.php?'+'&'+r['rel']+'&serii='+r['serii']

            name    = '[PAGE+1]'
            i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
            u = sys.argv[0] + '?mode=MOVIE'
            u += '&name=%s'%urllib.quote_plus(name)
            #-- filter parameters
            u += '&page=%s'%urllib.quote_plus(str(int(par.page)+1))
            u += '&genre=%s'%urllib.quote_plus(par.genre)
            u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
            u += '&year=%s'%urllib.quote_plus(par.year)
            u += '&year_name=%s'%urllib.quote_plus(par.year_name)
            u += '&url=%s'%urllib.quote_plus(url)
            xbmcplugin.addDirectoryItem(h, u, i, True)
        except:
            pass

        xbmcplugin.endOfDirectory(h, updateListing=True)

#---------- search movie list --------------------------------------------------
def Search_List(params):
        list = []
        #-- get filter parameters
        par = Get_Parameters(params)

        # show search dialog
        skbd = xbmc.Keyboard()
        skbd.setHeading('Поиск фильмов.')
        skbd.doModal()
        if skbd.isConfirmed():
            SearchStr = skbd.getText().split(':')
            par.search = SearchStr[0]
        else:
            return False

        #== get movie list =====================================================
        url = 'http://my-hit.org/index.php?module=search&func=view&result_orderby=score&result_order_asc=0&result_perpage=1000&search_string=%s&x=0&y=0'%urllib.quote(par.search.decode('utf-8').encode('cp1251'))
        #print url
        html = get_HTML(url)

        # -- parsing web page --------------------------------------------------
        soup = BeautifulSoup(html, fromEncoding="windows-1251")

        pcount = 1
        mcount = 0

        # -- get list of found movies
        flag = 0
        for rec in soup.findAll("tr"):
            try:
                if rec.find('a').text.find(u'(фильм)')<>-1:
                    m_name = rec.find('a').text.replace(u'(фильм)', '').encode('utf-8')
                    flag = 1
                elif flag==1:
                    m_url  = rec.find('a')['href']
                    m_url = 'http://my-hit.org/film/'+m_url.split('&id=')[1]+'/online'

                    m_img  = 'http://my-hit.org'+rec.find('img')['src']
                    m_text = unescape(rec.text).encode('utf-8')
                    flag = 0
                    list.append({'name':m_name, 'url':m_url, 'img':m_img, 'text':m_text})
            except:
                pass
        mcount = len(list)

        if mcount == 0:
            return False

        #-- add header info
        Get_Header(par, mcount, pcount)

        for mov in list:
            #-- add movie to the list ------------------------------------------
            name = '[COLOR FFC3FDB8]'+mov['name']+'[/COLOR]'

            i = xbmcgui.ListItem(name, iconImage=mi.img, thumbnailImage=mi.img)
            u = sys.argv[0] + '?mode=PLAY'
            u += '&name=%s'%urllib.quote_plus(mov['name'])
            u += '&url=%s'%urllib.quote_plus(mov['url'])
            u += '&img=%s'%urllib.quote_plus(mov['img'])
            i.setInfo(type='video', infoLabels={ 'title':      mov['name'],
                        						'plot':        mov['text']})
            i.setProperty('fanart_image', mov['img'])
            xbmcplugin.addDirectoryItem(h, u, i, False)

        xbmcplugin.endOfDirectory(h)

#---------- get genge list -----------------------------------------------------
def Genre_List(params):
    #-- get filter parameters
    par = Get_Parameters(params)

    #-- get generes
    url = 'http://cinema.mosfilm.ru/films/'
    html = get_HTML(url)

    # -- parsing web page ------------------------------------------------------
    soup = BeautifulSoup(html)
    nav = soup.find('div', {'class':"filter"})

    for rec in nav.findAll('span'):
        if (rec.text) == u'Жанр':
            for g in rec.parent.findAll('li'):
                name     = g.find('a').text.encode('utf-8')
                genre_id = g.find('a')['href']
    			#---
                i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
    	        u = sys.argv[0] + '?mode=MOVIE'
    	        u += '&name=%s'%urllib.quote_plus(name)
    	        #-- filter parameters
    	        u += '&page=%s'%urllib.quote_plus('1')
    	        u += '&genre=%s'%urllib.quote_plus(genre_id)
    	        u += '&genre_name=%s'%urllib.quote_plus(name)
    	        u += '&year=%s'%urllib.quote_plus(par.year)
                u += '&year_name=%s'%urllib.quote_plus(par.year_name)
                u += '&url=%s'%urllib.quote_plus(par.url)
    	        xbmcplugin.addDirectoryItem(h, u, i, True)

    #xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
    #xbmcplugin.endOfDirectory(h)
    xbmcplugin.endOfDirectory(h, updateListing=True)

#---------- get year list -----------------------------------------------------
def Year_List(params):
    #-- get filter parameters
    par = Get_Parameters(params)

    #-- get generes
    url = 'http://cinema.mosfilm.ru/films/'
    html = get_HTML(url)

    # -- parsing web page ------------------------------------------------------
    soup = BeautifulSoup(html)
    nav = soup.find('div', {'class':"filter"})

    for rec in nav.findAll('span'):
        if (rec.text) == u'Год':
            for g in rec.parent.findAll('li'):
                name     = g.find('a').text.encode('utf-8')
                year_id  = g.find('a')['href']
    			#---
                i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
    	        u = sys.argv[0] + '?mode=MOVIE'
    	        u += '&name=%s'%urllib.quote_plus(name)
    	        #-- filter parameters
    	        u += '&page=%s'%urllib.quote_plus('1')
    	        u += '&genre=%s'%urllib.quote_plus(par.genre)
    	        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
    	        u += '&year=%s'%urllib.quote_plus(year_id)
                u += '&year_name=%s'%urllib.quote_plus(name)
                u += '&url=%s'%urllib.quote_plus(par.url)
    	        xbmcplugin.addDirectoryItem(h, u, i, True)

    #xbmcplugin.endOfDirectory(h)
    xbmcplugin.endOfDirectory(h, updateListing=True)

#-------------------------------------------------------------------------------

def Play_List(params):
    # -- parameters
    url   = urllib.unquote_plus(params['url'])
    img   = urllib.unquote_plus(params['img'])
    name  = urllib.unquote_plus(params['name'])

    is_Multi = False

    html = get_HTML(url)
    soup = BeautifulSoup(html)

    for rec in soup.findAll('div', {'class':"item series-prev"}):
        is_Multi = True
        mi.img      = 'http://cinema.mosfilm.ru'+rec.find('img')['src']
        mi.url      = rec.find('span', {'class':"episode"})['link']
        mi.title    = rec.find('span', {'class':"episode"}).text.encode('utf-8')

        name = '[COLOR FFC3FDB8]'+mi.title+'[/COLOR]'

        i = xbmcgui.ListItem(name, iconImage=mi.img, thumbnailImage=mi.img)
        u = sys.argv[0] + '?mode=PLAY'
        u += '&name=%s'%urllib.quote_plus(mi.title)
        u += '&url=%s'%urllib.quote_plus(mi.url)
        u += '&img=%s'%urllib.quote_plus(mi.img)
        i.setProperty('fanart_image', mi.img)
        xbmcplugin.addDirectoryItem(h, u, i, False)

    if is_Multi == False:
        url  = soup.find('embed')['src']
        name = '[COLOR FFC3FDB8]'+name+'[/COLOR]'

        i = xbmcgui.ListItem(name, iconImage=img, thumbnailImage=img)
        u = sys.argv[0] + '?mode=PLAY'
        u += '&name=%s'%urllib.quote_plus(name)
        u += '&url=%s'%urllib.quote_plus(url)
        u += '&img=%s'%urllib.quote_plus(img)
        i.setProperty('fanart_image', img)
        xbmcplugin.addDirectoryItem(h, u, i, False)

    xbmcplugin.endOfDirectory(h)

def PLAY(params):
    # -- parameters
    url   = urllib.unquote_plus(params['url'])
    img   = urllib.unquote_plus(params['img'])
    name  = urllib.unquote_plus(params['name'])

    #-- get video id
    print url
    #url      = soup.find('embed')['src']
    video_id = re.compile(u'\/v\/(.+?)\?', re.MULTILINE|re.DOTALL).findall(url)[0]

    print video_id

    xbmc.executebuiltin('PlayMedia(plugin://plugin.video.youtube/?action=play_video&videoid='+video_id+')')


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
cj = cookielib.FileCookieJar(fcookies)
hr  = urllib2.HTTPCookieProcessor(cj)
opener = urllib2.build_opener(hr)
urllib2.install_opener(opener)

p  = Param()
mi = Info()

mode = None

try:
	mode = urllib.unquote_plus(params['mode'])
except:
	Movie_List(params)

if mode == 'MOVIE':
	Movie_List(params)
if mode == 'SEARCH':
	Search_List(params)
elif mode == 'GENRES':
    Genre_List(params)
elif mode == 'YEAR':
    Year_List(params)
elif mode == 'COUNTRY':
	Country_List(params)
elif mode == 'EMPTY':
    Empty()
elif mode == 'PLAY_LIST':
	Play_List(params)
elif mode == 'PLAY':
	PLAY(params)


