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
import re, os, urllib, urllib2, cookielib, time, sys, urlparse
from time import gmtime, strftime

try:
    import json
except ImportError:
    try:
        import simplejson as json
        #xbmc.log( '[%s]: Error import json. Uses module simplejson' % addon_id, 2 )
    except ImportError:
        try:
            import demjson3 as json
            #xbmc.log( '[%s]: Error import simplejson. Uses module demjson3' % addon_id, 3 )
        except ImportError:
            xbmc.log( '[%s]: Error import demjson3. Sorry.' % addon_id, 4 )

import xbmc, xbmcgui, xbmcplugin, xbmcaddon

Addon = xbmcaddon.Addon(id='plugin.video.nogomya.ch')
icon = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'),'icon.png'))
fcookies = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'), r'cookies.txt'))

# load XML library
try:
    sys.path.append(os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib'))
    from BeautifulSoup  import BeautifulSoup
    import xppod
except:
    try:
        sys.path.insert(0, os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib'))
        from BeautifulSoup  import BeautifulSoup
        import xppod
    except:
        sys.path.append(os.path.join(os.getcwd(), r'resources', r'lib'))
        from BeautifulSoup  import BeautifulSoup
        import xppod
        icon = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'icon.png'))

import HTMLParser
hpar = HTMLParser.HTMLParser()

h = int(sys.argv[1])

def showMessage(heading, message, times = 3000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))

#---------- get web page -------------------------------------------------------
def get_HTML(url, post = None, ref = None):
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

    html = f.read()

    return html


#----------  -----------------------------------------------------

#---------- archive ------------------------------------------------------------
def Archive_List(params):

    #-- get generes
    url = 'http://nogomya.ch/match/filter'

    values = {
                #'items[league][]' : '10'
             }

    post = urllib.urlencode(values)

    html = get_HTML(url, post)
    j = json.loads(html)

    soup = BeautifulSoup(j['match_filter'])

    for rec in soup.findAll('div', {'class':"block"}):
        url       = 'http://nogomya.ch' + rec.find('a', {'class':"block"})['href']
        img_home  = 'http://nogomya.ch' + rec.find('div', {'class':"home"}).find('img')['src']
        img_guest = 'http://nogomya.ch' + rec.find('div', {'class':"guest"}).find('img')['src']
        league  = rec.find('div', {'class':"league"}).text
        season  = rec.find('div', {'class':"season"}).text
        team    = rec.find('div', {'class':"team"}).text

        name    = (league+' '+season+' '+team).encode('utf-8')

        i = xbmcgui.ListItem(name, iconImage=img_home, thumbnailImage=img_guest)
        #i.setProperty('fanart_image', img_guest)
        u = sys.argv[0] + '?mode=EMPTY'
        u += '&name=%s'%urllib.quote_plus(name)
        #-- filter parameters
        #u += '&page=%s'%urllib.quote_plus(par.page)
        #u += '&liga=%s'%urllib.quote_plus(liga_id)
        #u += '&liga_name=%s'%urllib.quote_plus(name)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(h)


#---------- get liga list -----------------------------------------------------
def Liga_List(params):

    #-- get generes
    url = 'http://nogomya.ch/match'
    html = get_HTML(url)

    # -- parsing web page ------------------------------------------------------
    soup = BeautifulSoup(html)

    for rec in soup.find('ul', {'data-type':"league"}).findAll('li'):
        name    = rec.find('a').text.encode('utf-8')
        liga_id = rec.find('input')['value']

        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=EMPTY'
        u += '&name=%s'%urllib.quote_plus(name)
        #-- filter parameters
        #u += '&page=%s'%urllib.quote_plus(par.page)
        u += '&liga=%s'%urllib.quote_plus(liga_id)
        u += '&liga_name=%s'%urllib.quote_plus(name)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(h)

#----------- get Header string -------------------------------------------------
def Get_Header(par):

    info  = 'Фильмов: ' + '[COLOR FF00FF00]' + str(par.count) + '[/COLOR]'

    if par.max_page > 1:
        info += ' | Pages: ' + '[COLOR FF00FF00]'+ par.page + '/' + str(par.max_page) +'[/COLOR]'

    if par.genre <> '':
        info += ' | Жанр: ' + '[COLOR FF00FFF0]'+ par.genre_name + '[/COLOR]'

    if par.search <> '':
        info  += ' | Поиск: ' + '[COLOR FFFFFF00]'+ par.search +'[/COLOR]'

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

    #-- genres & search
    if par.genre == '' and par.search == '' and par.page == '1':
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

        name    = '[COLOR FFFFFF00]' + '[ПОИСК]' + '[/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=SEARCH'
        #-- filter parameters
        u += '&search=%s'%urllib.quote_plus('Y')
        xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- previous page
    if int(par.page) > 1 and par.search == '':
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
    if int(par.page) >= 10 and par.search == '':
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

#---------- get list of TV channels --------------------------------------------
def Get_TV_Channels():
    url = 'http://nogomya.ch/stream'
    html = get_HTML(url)
    soup = BeautifulSoup(html)

    if soup.find('form', {'class':"form-signin"}) != None:
        try:
            print '-------------'
            #-- login to tvisio.tv
            login       = 'Silen'
            password    = 'privet'

            print login
            print password

            values = {
                    'LoginForm[username]'   : login,
                    'LoginForm[password]'   : password,
                    'LoginForm[rememberMe]' : 0,
                    'yt0'                   : 'впустите'
                }

            post = urllib.urlencode(values)

            url = 'http://nogomya.ch/login'
            html = get_HTML(url, post, url)
        except:
            pass

        url = 'http://nogomya.ch/stream'
        html = get_HTML(url)
        soup = BeautifulSoup(html)

    if soup.find('form', {'class':"form-signin"}) != None:
        print 'ERROR: Login'
        return False


##    name    = '[COLOR FF00FFF0][Жанры][/COLOR]'
##    i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
##    u = sys.argv[0] + '?mode=LIGA'
##    u += '&name=%s'%urllib.quote_plus(name)
##    #-- filter parameters
##    #u += '&page=%s'%urllib.quote_plus(par.page)
##    #u += '&genre=%s'%urllib.quote_plus(par.genre)
##    #u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
##    #u += '&max_page=%s'%urllib.quote_plus(str(par.max_page))
##    #u += '&count=%s'%urllib.quote_plus(str(par.count))
##    xbmcplugin.addDirectoryItem(h, u, i, True)

    for rec in soup.findAll('div', {'class':re.compile("col-sm-6  highlight")}):
        ch_url  = 'http://nogomya.ch'+rec.find('a')['href']
        title   = rec.find('span').text
        descr   = rec.find('h4').text
        img     = rec.find('img')['src']

        name = ('[COLOR FFCCFF33][B]'+title+'[/B][/COLOR] [COLOR FFB8B8B8][I]'+descr+'[/I][/COLOR]').encode('utf-8')

        i = xbmcgui.ListItem(name, iconImage=img, thumbnailImage=img)
        u = sys.argv[0] + '?mode=PLAY'
        u += '&name=%s'%urllib.quote_plus(name)
        u += '&url=%s'%urllib.quote_plus(ch_url)
        u += '&img=%s'%urllib.quote_plus(img)
        xbmcplugin.addDirectoryItem(h, u, i, False)

    xbmcplugin.endOfDirectory(h)

#-------------------------------------------------------------------------------

def PLAY(params):
    # -- parameters
    url  = urllib.unquote_plus(params['url'])
    img  = urllib.unquote_plus(params['img'])
    name = urllib.unquote_plus(params['name'])

    # -- check if video available
    html = get_HTML(url)

    soup = BeautifulSoup(html)
    for rec in soup.findAll("script"):
        if 'id:"mediaplayer"' in rec.text:
            html = rec.text

    # -- parsing web page ----------------------------------------------------------
    try:
        str = re.compile('<embed (.+?)><\/embed>', re.MULTILINE|re.DOTALL).findall(html)[0]
        str = re.compile('flashvars="(.+?)"', re.MULTILINE|re.DOTALL).findall(str)[0]
        str = urllib.unquote(str).replace('src=','')
    except:
        try:
            str = re.compile('"file":"(.+?)"', re.MULTILINE|re.DOTALL).findall(html)[0]
        except:
            print '###'

    if str.find('http:') == -1:
            str = xppod.Decode(str)

    p_r = "rtmp://stream.nogomya.ch:1935/live"
    p_a = "live?"+str.split('&')[0].split('?')[1]
    p_f = "WIN 13,0,0,206"
    p_W = "http://nogomya.ch/player/StrobeMediaPlayback.swf"
    p_p = "http://nogomya.ch/stream/"+str.split('?')[0].split('/')[-1].split('.')[0]
    p_y = str.split('&')[0].split('/')[-1]

    video = str #'%s app=%s swfUrl=%s pageUrl=%s playpath=%s swfVfy=1 live=1'%(p_r, p_a, p_W, p_p, p_y, )

    i = xbmcgui.ListItem(name, path = urllib.unquote(video), thumbnailImage=img)
    xbmc.Player().play(video, i)
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
try:
    cj.load(ignore_discard=True)
except:
    pass
hr  = urllib2.HTTPCookieProcessor(cj)
opener = urllib2.build_opener(hr)
urllib2.install_opener(opener)

mode = None

try:
	mode = urllib.unquote_plus(params['mode'])
except:
	Get_TV_Channels()

if mode == 'PLAY':
	PLAY(params)
elif mode == 'LIGA':
    Archive_List(params) #Liga_List(params)
elif mode == 'EMPTY':
    Empty()

#-- store cookies
cj.save(ignore_discard=True)


