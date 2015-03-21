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
from operator import itemgetter

try:
    import json
except ImportError:
    try:
        import simplejson as json
        xbmc.log( '[%s]: Error import json. Uses module simplejson' % addon_id, 2 )
    except ImportError:
        try:
            import demjson3 as json
            xbmc.log( '[%s]: Error import simplejson. Uses module demjson3' % addon_id, 3 )
        except ImportError:
            xbmc.log( '[%s]: Error import demjson3. Sorry.' % addon_id, 4 )

import xbmc, xbmcgui, xbmcplugin, xbmcaddon

Addon = xbmcaddon.Addon(id='plugin.video.cn.ru.tv')
icon = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'),'icon.png'))
fcookies = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'), r'cookies.txt'))

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

#---------- get list of TV channels --------------------------------------------
def Get_TV_Channels():
    url = 'http://www.cn.ru/tv/'
    html = get_HTML(url).replace('<s>Rec</s>', '')

    # -- parsing web page ------------------------------------------------------
    soup = BeautifulSoup(html, fromEncoding="windows-1251")

    nav = soup.find('ol', {'id':'lst-rec'})
    for ch in nav.findAll('li'):
        name    = '[COLOR FF2F9FF0]'+unescape(ch.find('a').text).encode('utf-8')+'[/COLOR]'
        img     = ch.find('img')['src'].replace('_bg.','.')
        ch_url  = 'http://www.cn.ru'+ch.find('a')['href']
        i = xbmcgui.ListItem(name, iconImage=img, thumbnailImage=img)
        u = sys.argv[0] + '?mode=EPG_DATE'
        u += '&name=%s'%urllib.quote_plus(name)
        u += '&url=%s'%urllib.quote_plus(ch_url)
        u += '&img=%s'%urllib.quote_plus(img)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    xbmcplugin.endOfDirectory(h)
#-------------------------------------------------------------------------------

def Get_EPG_Date(params):
    list = []
    # -- parameters
    url  = urllib.unquote_plus(params['url'])
    img = urllib.unquote_plus(params['img'])

    html = get_HTML(url)

    # -- parsing web page ------------------------------------------------------
    soup = BeautifulSoup(html, fromEncoding="windows-1251")

    #-- fill up ETR data list
    nav = soup.find('div', {'id':'mtvprg-week'})

    ord_asc     = 1
    ord_desc    = 1000

    for rec in nav.findAll('a'):
        if rec['class'] == 'old' or rec['class'] == 'old cur' or rec['class'] == 'now cur':
            durl = 'http://www.cn.ru'+rec['href']
            date = durl.replace(url,'').replace('/','')
            dw = rec.find('small').text
            name = '[COLOR FF00FF00]'+date.encode('utf-8')+'[/COLOR] ('+dw.encode('utf-8')+')'

            list.append({'name':name, 'url':durl, 'img':img, 'desc':ord_desc, 'asc': ord_asc})

            ord_asc  += 1
            ord_desc -= 1

    if Addon.getSetting('back_date') == 'true':
        list = sorted(list, key=itemgetter('desc'))
    else:
        list = sorted(list, key=itemgetter('asc'))

    for rec in list:
            i = xbmcgui.ListItem(rec['name'], iconImage=rec['img'], thumbnailImage=rec['img'])
            u = sys.argv[0] + '?mode=EPG'
            u += '&name=%s'%urllib.quote_plus(rec['name'])
            u += '&url=%s'%urllib.quote_plus(rec['url'])
            u += '&img=%s'%urllib.quote_plus(rec['img'])
            xbmcplugin.addDirectoryItem(h, u, i, True)

    xbmcplugin.endOfDirectory(h)

#---------- get EPG for selected channel ---------------------------------------
def Get_EPG(params):
    list = []
    # -- parameters
    url = urllib.unquote_plus(params['url'])
    img = urllib.unquote_plus(params['img'])

    #---------------------------------------------------------------------------
    name    = '[COLOR FF00FF00]' + urllib.unquote_plus(params['name']) + '[/COLOR]'
    i = xbmcgui.ListItem(name, iconImage=img, thumbnailImage=img)
    u = sys.argv[0] + '?mode=EMPTY'
    u += '&name=%s'%urllib.quote_plus(name)
    u += '&url=%s'%urllib.quote_plus(url)
    u += '&img=%s'%urllib.quote_plus(img)
    u += '&ref=%s'%urllib.quote_plus(url)
    xbmcplugin.addDirectoryItem(h, u, i, False)
    #---------------------------------------------------------------------------

    html = get_HTML(url)

    # -- parsing web page ------------------------------------------------------
    soup = BeautifulSoup(html, fromEncoding="windows-1251")
    nav = soup.find('div', {'id':'mtvprg-program'})

    ord_asc     = 1
    ord_desc    = 1000

    for rec in nav.findAll('li'):
        prg = '*'
        for ins in rec.findAll('ins'):
            try:
                cls = ins['class']
                if cls == 'play':
                    prg = ins.find('a')['href']
            except:
                time = ins.text

        #-- check if playable
        if rec.find('div')['class'].find('is-able') == -1:
            prg = '*'
        #--
        name1    = rec.find('dfn').find('a').text
        try:
            detail  = rec.find('dfn').find('small').text
        except:
            detail = ''

        name = '[COLOR FF3BB9FF]'+unescape(time).encode('utf-8')+'[/COLOR]'+' '
        if prg == '*':
            name += '[COLOR FFFF0000]'+unescape(name1).encode('utf-8')+'[/COLOR]'
        else:
            name += '[COLOR FFC3FDB8]'+unescape(name1).encode('utf-8')+'[/COLOR]'

        if detail <> '':
            name += '[COLOR FFBEBEBE] ('+unescape(detail).encode('utf-8')+')[/COLOR]'

        list.append({'name':name, 'url':prg, 'img':img, 'desc':ord_desc, 'asc': ord_asc})

        ord_asc  += 1
        ord_desc -= 1

    if Addon.getSetting('back_time') == 'true':
        list = sorted(list, key=itemgetter('desc'))
    else:
        list = sorted(list, key=itemgetter('asc'))

    for rec in list:
            i = xbmcgui.ListItem(rec['name'], iconImage=rec['img'], thumbnailImage=rec['img'])
            u = sys.argv[0] + '?mode=PLAY'
            u += '&name=%s'%urllib.quote_plus(rec['name'])
            u += '&url=%s'%urllib.quote_plus(rec['url'])
            u += '&img=%s'%urllib.quote_plus(rec['img'])
            u += '&ref=%s'%urllib.quote_plus(url)
            xbmcplugin.addDirectoryItem(h, u, i, False)

    xbmcplugin.endOfDirectory(h)
#-------------------------------------------------------------------------------

def Empty():
    return False

#-------------------------------------------------------------------------------

def PLAY(params):
    # -- parameters
    url  = urllib.unquote_plus(params['url'])
    ref  = urllib.unquote_plus(params['ref'])
    img  = urllib.unquote_plus(params['img'])
    name = urllib.unquote_plus(params['name'])

    if url == '*':
        return False

    #-- get playlist
    html = get_HTML(url, None, ref)

    url = re.compile('file: (.+?),', re.MULTILINE|re.DOTALL).findall(html)[0].replace("'",'')
    url = url.split('?')[0]

    #--
    print url
##    html = get_HTML(url)
##
##    f = open("d:\\test.m3u8", "w")
##    f.write(html)
##    f.close()

    #url = 'd:\\30066714.m3u8'

    i = xbmcgui.ListItem(name, path = urllib.unquote(url), thumbnailImage=img)
    xbmc.Player().play(url, i)
    #xbmcplugin.setResolvedUrl(h, False, i)

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
    cj.load()
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

if mode == 'EPG_DATE':
	Get_EPG_Date(params)
elif mode == 'EPG':
	Get_EPG(params)
elif mode == 'PLAY':
	PLAY(params)
elif mode == 'EMPTY':
    Empty()

#-- store cookies
cj.save()


