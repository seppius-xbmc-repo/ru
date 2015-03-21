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

import xbmc, xbmcgui, xbmcplugin, xbmcaddon

Addon = xbmcaddon.Addon(id='plugin.video.9tv.co.il')
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
def get_HTML(url, post = None, ref = None, l = None):
    request = urllib2.Request(url, post)

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

    #-----
    return p

#-------------------------------------------------------------------------------
def Get_URL(par):
    if par.genre == 'video':
        url = 'http://9tv.co.il/video/news/'
    elif par.genre == 'shabat':
        url = 'http://9tv.co.il/video/shabat/'
    elif par.genre == 'w_order':
        url = 'http://9tv.co.il/video/world-order/'
    elif par.genre == 'contact':
        url = 'http://9tv.co.il/video/contact/'
    else:
        url = 'http://9tv.co.il'
        html = get_HTML(url)
        soup = BeautifulSoup(html, fromEncoding="windows-1251")

        for rec in soup.findAll("div", {"class":"block_title triang stl_2"}):
            if rec.text == u'Новости':
                url = rec.find('a')['href']

    return url

#----------- get Header string -------------------------------------------------
def Get_Header(par):

    info  = 'Жанр: ' + '[COLOR FF00FFF0]'+ par.genre_name + '[/COLOR]'

    if par.max_page > 1:
        info += ' | Pages: ' + '[COLOR FF00FF00]'+ par.page + '/' + str(par.max_page) +'[/COLOR]'

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
    u += '&url=%s'%urllib.quote_plus(par.url)
    xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- previous page
    if int(par.page) > 1:
        name    = '[COLOR FF00FF00][PAGE -1][/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=MOVIE'
        u += '&name=%s'%urllib.quote_plus(name)
        #-- filter parameters
        u += '&page=%s'%urllib.quote_plus(str(int(par.page)-1))
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&max_page=%s'%urllib.quote_plus(str(par.max_page))
        u += '&url=%s'%urllib.quote_plus(par.url)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- previous page
    if int(par.page) >= 10:
        name    = '[COLOR FF00FF00][PAGE -10][/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=MOVIE'
        u += '&name=%s'%urllib.quote_plus(name)
        #-- filter parameters
        u += '&page=%s'%urllib.quote_plus(str(int(par.page)-10))
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&max_page=%s'%urllib.quote_plus(str(par.max_page))
        u += '&url=%s'%urllib.quote_plus(par.url)
        xbmcplugin.addDirectoryItem(h, u, i, True)

def Empty():
    return False

#---------- movie list ---------------------------------------------------------
def Movie_List(params):
        #-- get filter parameters
        par = Get_Parameters(params)

        #-- get genre url
        if par.url == '':
            #-- get url
            par.url = Get_URL(par)

        #== get movie list =====================================================
        html = get_HTML(par.url+'?p='+par.page)
        soup = BeautifulSoup(html, fromEncoding="windows-1251")

        #-- get max pages
        if par.max_page == 0:
            for rec in soup.find("div", {"class":"info page"}).findAll('a'):
                if rec.text == '>>':
                    par.max_page = int(rec['href'].split('=')[1])

        # -- add header info
        Get_Header(par)

        # -- get movie info
        for rec in soup.findAll("div", {"class":"blockV"}):
            mi.url      = rec.find('a')['href']
            mi.title    = rec.find('a').text.encode('utf-8')
            mi.img      = rec.find('img')['src']

            mi.text     = ''
            for t in rec.findAll('a'):
                mi.text = mi.text +' '+ t.text
            mi.text     = mi.text +' '+ rec.find('span', {'class':'date'}).text.encode('utf-8')

            i = xbmcgui.ListItem(mi.title, iconImage=mi.img, thumbnailImage=mi.img)
            u = sys.argv[0] + '?mode=PLAY'
            u += '&name=%s'%urllib.quote_plus(mi.title)
            u += '&url=%s'%urllib.quote_plus(mi.url)
            u += '&img=%s'%urllib.quote_plus(mi.img)
            i.setInfo(type='video', infoLabels={ 'title':      mi.title,
                        						'plot':        mi.text,
                        						'genre':       par.genre_name})
            #i.setProperty('fanart_image', mi.img)
            xbmcplugin.addDirectoryItem(h, u, i, False)
        #-- next page link
        if int(par.page) < par.max_page :
            name    = '[COLOR FF00FF00][PAGE +1][/COLOR]'
            i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
            u = sys.argv[0] + '?mode=MOVIE'
            u += '&name=%s'%urllib.quote_plus(name)
            #-- filter parameters
            u += '&page=%s'%urllib.quote_plus(str(int(par.page)+1))
            u += '&genre=%s'%urllib.quote_plus(par.genre)
            u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
            u += '&max_page=%s'%urllib.quote_plus(str(par.max_page))
            u += '&url=%s'%urllib.quote_plus(par.url)
            xbmcplugin.addDirectoryItem(h, u, i, True)

        if int(par.page)+10 <= par.max_page :
            name    = '[COLOR FF00FF00][PAGE +10][/COLOR]'
            i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
            u = sys.argv[0] + '?mode=MOVIE'
            u += '&name=%s'%urllib.quote_plus(name)
            #-- filter parameters
            u += '&page=%s'%urllib.quote_plus(str(int(par.page)+10))
            u += '&genre=%s'%urllib.quote_plus(par.genre)
            u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
            u += '&max_page=%s'%urllib.quote_plus(str(par.max_page))
            u += '&url=%s'%urllib.quote_plus(par.url)
            xbmcplugin.addDirectoryItem(h, u, i, True)
        #xbmc.log("** "+str(pcount)+"  :  "+str(mcount))

        xbmcplugin.endOfDirectory(h)


#---------- get genge list -----------------------------------------------------
def Genre_List(params):
    #-- get filter parameters
    par = Get_Parameters(params)

    #--- NEWS -----------------------
    name     = 'Новости'
    genre_id = 'news'

    i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
    u = sys.argv[0] + '?mode=MOVIE'
    u += '&name=%s'%urllib.quote_plus(name)
    #-- filter parameters
    u += '&page=%s'%urllib.quote_plus('1')
    u += '&genre=%s'%urllib.quote_plus(genre_id)
    u += '&genre_name=%s'%urllib.quote_plus(name)
    u += '&url=%s'%urllib.quote_plus('')
    xbmcplugin.addDirectoryItem(h, u, i, True)

    #--- ACTUAL VIDEO ---------------
    name     = 'Актуальное видео'
    genre_id = 'video'

    i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
    u = sys.argv[0] + '?mode=MOVIE'
    u += '&name=%s'%urllib.quote_plus(name)
    #-- filter parameters
    u += '&page=%s'%urllib.quote_plus('1')
    u += '&genre=%s'%urllib.quote_plus(genre_id)
    u += '&genre_name=%s'%urllib.quote_plus(name)
    u += '&url=%s'%urllib.quote_plus('')
    xbmcplugin.addDirectoryItem(h, u, i, True)

    #--- World ORDER ---------------
    name     = '"Мировой порядок"'
    genre_id = 'w_order'

    i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
    u = sys.argv[0] + '?mode=MOVIE'
    u += '&name=%s'%urllib.quote_plus(name)
    #-- filter parameters
    u += '&page=%s'%urllib.quote_plus('1')
    u += '&genre=%s'%urllib.quote_plus(genre_id)
    u += '&genre_name=%s'%urllib.quote_plus(name)
    u += '&url=%s'%urllib.quote_plus('')
    xbmcplugin.addDirectoryItem(h, u, i, True)

    #--- PROGRAM CONTACT ---------------
    name     = 'Программа "Контакт"'
    genre_id = 'contact'

    i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
    u = sys.argv[0] + '?mode=MOVIE'
    u += '&name=%s'%urllib.quote_plus(name)
    #-- filter parameters
    u += '&page=%s'%urllib.quote_plus('1')
    u += '&genre=%s'%urllib.quote_plus(genre_id)
    u += '&genre_name=%s'%urllib.quote_plus(name)
    u += '&url=%s'%urllib.quote_plus('')
    xbmcplugin.addDirectoryItem(h, u, i, True)

    #--- SHABAT to SHABAT -------------
    name     = '"От шабата до шабата"'
    genre_id = 'shabat'

    i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
    u = sys.argv[0] + '?mode=MOVIE'
    u += '&name=%s'%urllib.quote_plus(name)
    #-- filter parameters
    u += '&page=%s'%urllib.quote_plus('1')
    u += '&genre=%s'%urllib.quote_plus(genre_id)
    u += '&genre_name=%s'%urllib.quote_plus(name)
    u += '&url=%s'%urllib.quote_plus('')
    xbmcplugin.addDirectoryItem(h, u, i, True)

    xbmcplugin.endOfDirectory(h)


#-------------------------------------------------------------------------------

def PLAY(params):
    try:
        # -- parameters
        url   = urllib.unquote_plus(params['url'])
        img   = urllib.unquote_plus(params['img'])
        name  = urllib.unquote_plus(params['name'])

        html = get_HTML(url)
        soup = BeautifulSoup(html, fromEncoding="windows-1251")

        video = soup.find("meta", {"property":"og:video"})['content'].split('&')[0].split('=')[1]

        # -- play video
        i = xbmcgui.ListItem(name, video, thumbnailImage=img)
        xbmc.Player().play(video, i)
    except:
        pass
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

try:
	mode = urllib.unquote_plus(params['mode'])
except:
	Genre_List(params)

if mode == 'MOVIE':
	Movie_List(params)
elif mode == 'EMPTY':
    Empty()
elif mode == 'PLAY':
	PLAY(params)


