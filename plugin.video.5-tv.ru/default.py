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

import xbmc, xbmcgui, xbmcplugin, xbmcaddon
from datetime import date

Addon = xbmcaddon.Addon(id='plugin.video.5-tv.ru')
icon = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'),'icon.png'))

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

#---------- get categories  ----------------------------------------------------
def Get_Categories():
    # get categories from 5-TV site
    url = 'http://www.5-tv.ru/video/'
    post = None
    request = urllib2.Request(url, post)

    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host',	'5-tv.ru')
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Language', 'ru-RU')
    request.add_header('Referer',	'http://google.com')

    try:
        f = urllib2.urlopen(request)
    except IOError, e:
        if hasattr(e, 'reason'):
            xbmc.log('We failed to reach a server. Reason: '+ e.reason)
        elif hasattr(e, 'code'):
            xbmc.log('The server couldn\'t fulfill the request. Error code: '+ e.code)

    html = f.read()

    # -- parsing web page ------------------------------------------------------

    soup = BeautifulSoup(html, fromEncoding="windows-1251")

    tv5_nav = soup.find("div", { "class" : "nav" }).findAll("li", { "class" : "" })
    for nav in tv5_nav:
        if nav.find("a")["href"] <> "http://www.5-tv.ru/persons/" and nav.find("a")["href"] <> "http://5-tv.ru/persons/":
            name = unescape(nav.find("a").text).encode('utf-8')
            tag  = nav.find("a")["href"]
            i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
            if nav.find("a")["href"] == "http://www.5-tv.ru/video/doc/" or nav.find("a")["href"] == "http://5-tv.ru/video/doc/":
                u = sys.argv[0] + '?mode=EPISODES'
            else:
                u = sys.argv[0] + '?mode=SUBCATEGORIES'
            u += '&name=%s'%urllib.quote_plus(name)
            u += '&url=%s'%urllib.quote_plus(tag)
            xbmcplugin.addDirectoryItem(h, u, i, True)

    xbmcplugin.endOfDirectory(h)
#-------------------------------------------------------------------------------

#---------- get subcategories  -------------------------------------------------
def Get_Subcategories(params):
    # -- parameters
    url  = urllib.unquote_plus(params['url'])
    # get subcategories from 5-TV site
    if url == '#':
        url2 = 'http://www.5-tv.ru/video/'
    else:
        url2 = get_url(url)

    post = None
    request = urllib2.Request(url2, post)

    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host',	'5-tv.ru')
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Language', 'ru-RU')
    request.add_header('Referer',	'http://google.com')

    try:
        f = urllib2.urlopen(request)
    except IOError, e:
        if hasattr(e, 'reason'):
            xbmc.log('We failed to reach a server. Reason: '+ e.reason)
        elif hasattr(e, 'code'):
            xbmc.log('The server couldn\'t fulfill the request. Error code: '+ e.code)

    html = f.read()

    # -- parsing web page ------------------------------------------------------

    soup = BeautifulSoup(html, fromEncoding="windows-1251")

    tv5_nav = soup.find("div", { "class" : "nav" }).findAll("li")
    for nav in tv5_nav:
        if nav.find("a")["href"] == url:
            for rec in nav.find("ul").findAll("li"):
                name = unescape(rec.find("a").text).encode('utf-8')
                tag  = unescape(rec.find("a")["href"])
                i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
                u = sys.argv[0] + '?mode=EPISODES'
                u += '&name=%s'%urllib.quote_plus(name)
                u += '&url=%s'%urllib.quote_plus(tag)
                xbmcplugin.addDirectoryItem(h, u, i, True)

    xbmcplugin.endOfDirectory(h)
#-------------------------------------------------------------------------------

#---------- get list of episodes -----------------------------------------------
def Get_Episodes(params):
    # -- parameters
    url  = get_url(urllib.unquote_plus(params['url']))

    # get episodess from 5-TV site
    post = None
    request = urllib2.Request(url, post)

    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host',	'5-tv.ru')
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Language', 'ru-RU')
    request.add_header('Referer',	'http://google.com')

    try:
        f = urllib2.urlopen(request)
    except IOError, e:
        if hasattr(e, 'reason'):
            xbmc.log('We failed to reach a server. Reason: '+ e.reason)
        elif hasattr(e, 'code'):
            xbmc.log('The server couldn\'t fulfill the request. Error code: '+ e.code)

    html = f.read()

    # -- parsing web page ------------------------------------------------------
    soup = BeautifulSoup(html, fromEncoding="windows-1251")

    # -- get list of episodes from page
    tv5_nav = soup.findAll("div", { "class" : "vitem" })
    for nav in tv5_nav:
        nav_det = nav.find("div", {"class" : "vitem_mb"})

        name  = (unescape(nav.find("a").text)+" ("+unescape(nav.find("span", {"class" : "vitem_mb_h"}).text).replace("|", "")+")").encode('utf-8')
        image = unescape(nav_det.find("img")["src"])
        text  = unescape(nav.find("p").text).encode('utf-8')

        i = xbmcgui.ListItem(name, iconImage=image, thumbnailImage=image)
        u = sys.argv[0] + '?mode=PLAY'
        u += '&name=%s'%urllib.quote_plus(name)
        u += '&url=%s'%urllib.quote_plus(unescape(nav.find("a")["href"]))
        u += '&img=%s'%urllib.quote_plus(image)

        i.setInfo(type='video', infoLabels={  'title':       name,
            						          'plot':        text})
        i.setProperty('fanart_image', image)

        #i.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(h, u, i, False)

    # -- check if exist next page
    try:
        tv5_page = soup.find("div", { "class" : "paginator" })
        prev_page = int(tv5_page.find("b").text)+1

        for page in tv5_page.findAll("a"):
                if int(unescape(page.text)) == prev_page:
                    name = ("<< PAGE "+str(prev_page)+" >>").encode('utf-8')
                    tag  = unescape(page["href"])
                    i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
                    u = sys.argv[0] + '?mode=EPISODES'
                    u += '&name=%s'%urllib.quote_plus(name)
                    u += '&url=%s'%urllib.quote_plus(tag)
                    xbmcplugin.addDirectoryItem(h, u, i, True)
    except:
        print 'no pages found'

    xbmcplugin.endOfDirectory(h)


#---------- get serial video links ---------------------------------------------
def Get_Video(url):
    cj = cookielib.CookieJar()
    h  = urllib2.HTTPCookieProcessor(cj)
    opener = urllib2.build_opener(h)
    urllib2.install_opener(opener)
    post = None

    post = None
    request = urllib2.Request(url, post)

    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host',	'5-tv.ru')
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Language', 'ru-RU')
    request.add_header('Referer',	'http://google.com')

    try:
        f = urllib2.urlopen(request)
    except IOError, e:
        if hasattr(e, 'reason'):
            xbmc.log('We failed to reach a server. Reason: '+ e.reason)
        elif hasattr(e, 'code'):
            xbmc.log('The server couldn\'t fulfill the request. Error code: '+ e.code)

    html = f.read()

    # -- parsing web page ------------------------------------------------------
    soup = BeautifulSoup(html, fromEncoding="windows-1251")
    tv5_nav = soup.findAll("a", { "class" : "videoplayer" })
    for nav in tv5_nav:
        video = nav["href"]

    return video
#-------------------------------------------------------------------------------

def PLAY(params):
    # -- parameters
    url         = urllib.unquote_plus(params['url'])
    img         = urllib.unquote_plus(params['img'])
    name        = urllib.unquote_plus(params['name'])

    video = Get_Video(url)

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

mode = None

try:
	mode = urllib.unquote_plus(params['mode'])
except:
	Get_Categories()

if mode == 'SUBCATEGORIES':
	Get_Subcategories(params)
elif mode == 'EPISODES':
    Get_Episodes(params)
elif mode == 'PLAY':
	PLAY(params)
