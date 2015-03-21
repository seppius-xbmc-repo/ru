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
from urlparse import urlparse

import xbmc, xbmcgui, xbmcplugin, xbmcaddon

Addon = xbmcaddon.Addon(id='plugin.video.galileo-tv.ru')
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
    page    = '1'
    letter  = ''
    letter_name = ''
    url = ''

class Info:
    img         = ''
    url         = '*'
    title       = ''
    text        = ''

#---------- get parameters -----------------------------------------------------
def Get_Parameters(params):
    #-- url
    try:    p.url = urllib.unquote_plus(params['url'])
    except: p.url = 'http://www.galileo-tv.ru/glossary'
    #-- page
    try:    p.page = urllib.unquote_plus(params['page'])
    except: p.page = '1'
    #-- letter
    try:    p.letter = urllib.unquote_plus(params['letter'])
    except: p.letter = ''
    try:    p.letter_name = urllib.unquote_plus(params['letter_name'])
    except: p.letter_name = ''
    #-----
    return p

#----------- get Header string ---------------------------------------------------
def Get_Header(par, pcount):

    info = ''

    if pcount > 1:
        info += 'Pages: ' + '[COLOR FF00FF00]'+ par.page + '/' + str(pcount) +'[/COLOR]'

    if par.letter <> '':
        if pcount > 1:
            info += ' | '
        info += 'Название: ' + '[COLOR FFFF00FF]'+ par.letter_name + '[/COLOR]'

    if info <> '':
        #-- info line
        name    = info
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=EMPTY'
        u += '&name=%s'%urllib.quote_plus(name)
        #-- filter parameters
        u += '&page=%s'%urllib.quote_plus(par.page)
        u += '&letter=%s'%urllib.quote_plus(par.letter)
        u += '&letter_name=%s'%urllib.quote_plus(par.letter_name)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- alphabet
    if par.letter == '' and par.page == '1':
        name    = '[COLOR FFFFF000]'+ '[Алфавит]' + '[/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=ALPHABET'
        u += '&name=%s'%urllib.quote_plus(name)
        #-- filter parameters
        u += '&page=%s'%urllib.quote_plus(par.page)
        u += '&letter=%s'%urllib.quote_plus(par.letter)
        u += '&letter_name=%s'%urllib.quote_plus(par.letter_name)
        xbmcplugin.addDirectoryItem(h, u, i, True)

def Empty():
    return False

#---------- movie list ---------------------------------------------------------
def Movie_List(params):
        #-- get filter parameters
        par = Get_Parameters(params)

        #== get movie list =====================================================
        url = par.url

        post = None
        request = urllib2.Request(url, post)

        request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
        request.add_header('Host',	'galileo-tv.ru')
        request.add_header('Accept', '*/*')
        request.add_header('Accept-Language', 'ru-RU')
        request.add_header('Referer',	'http://galileo-tv.ru')

        html = ''

        try:
            f = urllib2.urlopen(request)
            html = f.read()
        except IOError, e:
            if hasattr(e, 'reason'):
                xbmc.log('We failed to reach a server. Reason: '+ str(e.reason))
            elif hasattr(e, 'code'):
                xbmc.log('The server couldn\'t fulfill the request. Error code: '+ str(e.code))


        # -- parsing web page --------------------------------------------------
        soup = BeautifulSoup(html, fromEncoding="windows-1251")

        pcount = 1
        # -- get number of pages
        try:
            pcount = int(soup.find('li', {'class':"pager-last last"}).find('a')['href'].split('%2C')[2])
        except:
            try:
                pcount = int(soup.find('li', {'class':"pager-current last"}).text)-1
            except:
                pcount = 1

        #-- add header info
        Get_Header(par, pcount)

        #-- first page link
        if int(par.page) > 1:
            name    = '[FIRST PAGE]'
            i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
            u = sys.argv[0] + '?mode=MOVIE'
            u += '&name=%s'%urllib.quote_plus(name)
            #-- filter parameters
            u += '&page=%s'%urllib.quote_plus(str(1))
            u += '&letter=%s'%urllib.quote_plus(par.letter)
            u += '&letter_name=%s'%urllib.quote_plus(par.letter_name)
            u += '&url=%s'%urllib.quote_plus('http://galileo-tv.ru/glossary?page=0%2C0%2C'+str(1))
            xbmcplugin.addDirectoryItem(h, u, i, True)

        #-- next page+10 link
        if int(par.page)-10 > 1 :
            name    = '[PREVIOUS PAGE -10]'
            i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
            u = sys.argv[0] + '?mode=MOVIE'
            u += '&name=%s'%urllib.quote_plus(name)
            #-- filter parameters
            u += '&page=%s'%urllib.quote_plus(str(int(par.page)-10))
            u += '&letter=%s'%urllib.quote_plus(par.letter)
            u += '&letter_name=%s'%urllib.quote_plus(par.letter_name)
            u += '&url=%s'%urllib.quote_plus('http://galileo-tv.ru/glossary?page=0%2C0%2C'+str(int(par.page)-10))
            xbmcplugin.addDirectoryItem(h, u, i, True)

        #-- previus page link
        if int(par.page) > 1 :
            name    = '[PREVIOUS PAGE]'
            i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
            u = sys.argv[0] + '?mode=MOVIE'
            u += '&name=%s'%urllib.quote_plus(name)
            #-- filter parameters
            u += '&page=%s'%urllib.quote_plus(str(int(par.page)-1))
            u += '&letter=%s'%urllib.quote_plus(par.letter)
            u += '&letter_name=%s'%urllib.quote_plus(par.letter_name)
            u += '&url=%s'%urllib.quote_plus('http://galileo-tv.ru/glossary?page=0%2C0%2C'+str(int(par.page)-1))
            xbmcplugin.addDirectoryItem(h, u, i, True)

        #-- get movie info
        #try:
        for rec in soup.findAll("div", {"class":"video-teaser"}):
            mi.url   = 'http://galileo-tv.ru'+rec.find('a')['href']
            mi.title = rec.find('a')['title'].encode('utf-8')
            mi.img   = rec.find('img')['src']
            mi.text  = rec.find('ins').text.encode('utf-8')

            name = '[COLOR FFC3FDB8]'+mi.text+'[/COLOR]'+' '+mi.title

            i = xbmcgui.ListItem(name, iconImage=mi.img, thumbnailImage=mi.img)
            u = sys.argv[0] + '?mode=PLAY'
            u += '&name=%s'%urllib.quote_plus(mi.title)
            u += '&url=%s'%urllib.quote_plus(mi.url)
            u += '&img=%s'%urllib.quote_plus(mi.img)
            xbmcplugin.addDirectoryItem(h, u, i, False)
            i.setInfo(type='video', infoLabels={ 'title':      mi.title,
                        						'plot':        mi.text})
            i.setProperty('fanart_image', mi.img)
        #except:
        #    pass

        #-- next page link
        if int(par.page) < pcount :
            name    = '[NEXT PAGE]'
            i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
            u = sys.argv[0] + '?mode=MOVIE'
            u += '&name=%s'%urllib.quote_plus(name)
            #-- filter parameters
            u += '&page=%s'%urllib.quote_plus(str(int(par.page)+1))
            u += '&letter=%s'%urllib.quote_plus(par.letter)
            u += '&letter_name=%s'%urllib.quote_plus(par.letter_name)
            u += '&url=%s'%urllib.quote_plus('http://galileo-tv.ru/glossary?page=0%2C0%2C'+str(int(par.page)+1))
            xbmcplugin.addDirectoryItem(h, u, i, True)

        #-- next page+10 link
        if int(par.page)+10 < pcount :
            name    = '[NEXT PAGE +10]'
            i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
            u = sys.argv[0] + '?mode=MOVIE'
            u += '&name=%s'%urllib.quote_plus(name)
            #-- filter parameters
            u += '&page=%s'%urllib.quote_plus(str(int(par.page)+10))
            u += '&letter=%s'%urllib.quote_plus(par.letter)
            u += '&letter_name=%s'%urllib.quote_plus(par.letter_name)
            u += '&url=%s'%urllib.quote_plus('http://galileo-tv.ru/glossary?page=0%2C0%2C'+str(int(par.page)+10))
            xbmcplugin.addDirectoryItem(h, u, i, True)

        #-- last page link
        if int(par.page) < pcount :
            name    = '[LAST PAGE]'
            i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
            u = sys.argv[0] + '?mode=MOVIE'
            u += '&name=%s'%urllib.quote_plus(name)
            #-- filter parameters
            u += '&page=%s'%urllib.quote_plus(str(pcount))
            u += '&letter=%s'%urllib.quote_plus(par.letter)
            u += '&letter_name=%s'%urllib.quote_plus(par.letter_name)
            u += '&url=%s'%urllib.quote_plus('http://galileo-tv.ru/glossary?page=0%2C0%2C'+str(pcount))
            xbmcplugin.addDirectoryItem(h, u, i, True)

        #xbmc.log("** "+str(pcount)+"  :  "+str(mcount))

        xbmcplugin.endOfDirectory(h)

#---------- get year list -----------------------------------------------------
def Alphabet_List(params):
    #-- get filter parameters
    par = Get_Parameters(params)

    #-- get generes
    url = 'http://www.galileo-tv.ru/glossary'

    post = None
    request = urllib2.Request(url, post)

    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host',	'galileo-tv.ru')
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Language', 'ru-RU')
    request.add_header('Referer',	'http://galileo-tv.ru')

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

    for rec in soup.findAll("span", {"class":"views-summary views-summary-unformatted"}):
        letter   = rec.find('a').text.encode('utf-8')
        name     = unescape(letter).encode('utf-8')
        url      = 'http://www.galileo-tv.ru'+rec.find('a')['href']

        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=MOVIE'
        u += '&name=%s'%urllib.quote_plus(name)
        #-- filter parameters
        u += '&page=%s'%urllib.quote_plus(par.page)
        u += '&letter=%s'%urllib.quote_plus(letter)
        u += '&letter_name=%s'%urllib.quote_plus(name)
        u += '&url=%s'%urllib.quote_plus(url)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(h)

#-------------------------------------------------------------------------------

def PLAY(params):
    # -- parameters
    url  = urllib.unquote_plus(params['url'])
    img  = urllib.unquote_plus(params['img'])
    name = urllib.unquote_plus(params['name'])

    if url == '*':
        return False

    # -- check if video available
    post = None
    request = urllib2.Request(url, post)

    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host',	'galileo-tv.ru')
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Language', 'ru-RU')
    request.add_header('Referer',	'galileo-tv.ru')

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

    rez = str(soup.find('div', {'class':"field-items"}))
    r = re.compile('"file":"(.+?)"', re.MULTILINE|re.DOTALL).findall(rez.replace('\/','/'))
    video = r[0]

    i = xbmcgui.ListItem(name, path = urllib.unquote(video), thumbnailImage=img)
    i.setProperty('IsPlayable', 'true')
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
elif mode == 'GENRES':
    Genre_List(params)
elif mode == 'YEAR':
    Year_List(params)
elif mode == 'ALPHABET':
	Alphabet_List(params)
elif mode == 'EMPTY':
    Empty()
elif mode == 'PLAY':
	PLAY(params)


