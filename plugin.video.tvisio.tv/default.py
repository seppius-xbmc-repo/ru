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

Addon = xbmcaddon.Addon(id='plugin.video.tvisio.tv')
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

#---------- get Moscow Time ----------------------------------------------------
def MSK_time():
    try:
        #-- get MSK time page from Time&Date server
        url = 'http://www.timeanddate.com/worldclock/city.html?n=166'
        html = get_HTML(url)

        MSK_TOff =  re.compile('<td>Current time zone offset:<\/td><td><strong>UTC\/GMT \+(.+?) hours<\/strong>', re.MULTILINE|re.DOTALL).findall(html)
        TOff = int(MSK_TOff[0])
    except:
        TOff = 3

    #--- return MSK time
    return gmtime(time.time()+TOff*60*60)


#---------- get list of TV channels --------------------------------------------
def Get_TV_Channels():
    url = 'http://tvisio.tv'
    html = get_HTML(url)

    try:
        #-- get authenticity token
        token = re.compile('<input name="authenticity_token" type="hidden" value="(.+?)" \/>', re.MULTILINE|re.DOTALL).findall(html)[0]
        #-- login to tvisio.tv
        login       = Addon.getSetting('Login')
        password    = Addon.getSetting('Password')

        values = {
              'user[email]' : login,
              'user[password]' : password,
              'user[remember_me]' : 1,
              'authenticity_token' : token,
              'commit' : 'Войти',
              'utf8' : '✓'
            }

        post = urllib.urlencode(values)

        url = 'http://tvisio.tv/users/login'
        html = get_HTML(url, post)
    except:
        pass

    # -- parsing web page ------------------------------------------------------
    html = re.compile('<body>(.+?)<\/body>', re.MULTILINE|re.DOTALL).findall(html)[0]
    soup = BeautifulSoup(html)

    nav = soup.find('div', { 'id':"channels_list"})
    for ch in nav.findAll("a"):
        name    = unescape(ch.find('img')['alt']).encode('utf-8')
        img     = 'http://tvisio.tv'+ch.find('img')['src']
        ch_url  = 'http://tvisio.tv'+ch['href']
        i = xbmcgui.ListItem(name, iconImage=img, thumbnailImage=img)
        u = sys.argv[0] + '?mode=EPG_DATE'
        u += '&name=%s'%urllib.quote_plus(name)
        u += '&url=%s'%urllib.quote_plus(ch_url)
        u += '&img=%s'%urllib.quote_plus(img)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    xbmcplugin.endOfDirectory(h)
#-------------------------------------------------------------------------------

def Get_EPG_Date(params):
    # -- parameters
    url  = urllib.unquote_plus(params['url'])
    img = urllib.unquote_plus(params['img'])

    #-- get online TV link
    print url
    html = get_HTML(url)
    html = re.compile('<body>(.+?)<\/body>', re.MULTILINE|re.DOTALL).findall(html)[0]
    soup = BeautifulSoup(html)

    print html

    for online in soup.find('div',{'class':'head'}).findAll("a"):
        prg = 'http://tvisio.tv'+online['href']

    name = '[COLOR FF3BB9FF]Смотреть онлайн[/COLOR]'

    prg_name = '<< Смотреть онлайн >>'

    i = xbmcgui.ListItem(name, iconImage=img, thumbnailImage=img)
    u = sys.argv[0] + '?mode=PLAY'
    u += '&name=%s'%urllib.quote_plus(name)
    u += '&url=%s'%urllib.quote_plus(prg)
    u += '&prg=%s'%urllib.quote_plus(prg_name)
    u += '&img=%s'%urllib.quote_plus(img)
    xbmcplugin.addDirectoryItem(h, u, i, False)


    #-- get MSK time
    MSK = time.mktime(MSK_time())
    #-- fill up ETR data list
    for day_off in range(0, 16):    #-- tvisio.tv keeps 2 weeks of TV data
        ETR_date = time.localtime(MSK-day_off*24*60*60)
        name = unescape(strftime("%a, %d %b %Y", ETR_date)).encode('utf-8')
        id   = url + '?date=' + strftime("%Y-%m-%d", ETR_date)
        i = xbmcgui.ListItem(name, iconImage=img, thumbnailImage=img)
        u = sys.argv[0] + '?mode=EPG'
        u += '&name=%s'%urllib.quote_plus(name)
        u += '&url=%s'%urllib.quote_plus(id)
        u += '&img=%s'%urllib.quote_plus(img)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    xbmcplugin.endOfDirectory(h)

#---------- get EPG for selected channel ---------------------------------------
def Get_EPG(params):
    # -- parameters
    url = urllib.unquote_plus(params['url'])
    img = urllib.unquote_plus(params['img'])

    html = get_HTML(url)

    # -- parsing web page ------------------------------------------------------
    html = re.compile('<body>(.+?)<\/body>', re.MULTILINE|re.DOTALL).findall(html)[0]
    soup = BeautifulSoup(html)

    nav = soup.findAll("div", { "class" : "broadcast" })
    for ch in nav:
        try:
            prg = 'http://tvisio.tv'+ch.find('a')['href']
        except:
            prg = '*'

        name = '[COLOR FF3BB9FF]'+unescape(ch.find("span", { "class" : "time" }).text).encode('utf-8')+'[/COLOR]'+' '
        if prg == '*':
            name += '[COLOR FFFF0000]'+unescape(ch.find("span", { "class" : "title" }).text).encode('utf-8')+'[/COLOR]'
        else:
            name += '[COLOR FFC3FDB8]'+unescape(ch.find("span", { "class" : "title" }).text).encode('utf-8')+'[/COLOR]'

        prg_name = unescape(ch.find("span", { "class" : "title" }).text).encode('utf-8')

        i = xbmcgui.ListItem(name, iconImage=img, thumbnailImage=img)
        u = sys.argv[0] + '?mode=PLAY'
        u += '&name=%s'%urllib.quote_plus(name)
        u += '&url=%s'%urllib.quote_plus(prg)
        u += '&prg=%s'%urllib.quote_plus(prg_name)
        u += '&img=%s'%urllib.quote_plus(img)
        xbmcplugin.addDirectoryItem(h, u, i, False)

    xbmcplugin.endOfDirectory(h)
#-------------------------------------------------------------------------------


#-------------------------------------------------------------------------------

def PLAY(params):
    # -- parameters
    url  = urllib.unquote_plus(params['url'])
    img  = urllib.unquote_plus(params['img'])
    name = urllib.unquote_plus(params['prg'])

    if url == '*':
        return False

    # -- check if video available
    html = get_HTML(url)

    # -- parsing web page ----------------------------------------------------------
    var = re.compile('flashvars.(.+?) = "(.+?)";', re.MULTILINE|re.DOTALL).findall(html)
    for rec in var:
        if rec[0].find('stream') > -1:
            v_stream = rec[1]
        elif rec[0].find('start') > -1:
            v_start = rec[1]
        elif rec[0].find('server') > -1:
            v_server = rec[1]
        elif rec[0].find('session') > -1:
            v_session = rec[1]

    swf = re.compile('swfobject.embedSWF\("(.+?)"', re.MULTILINE|re.DOTALL).findall(html)
    v_swf = swf[0]

    # -- assemble RTMP link ----------------------------------------------------
    if name <> '<< Смотреть онлайн >>':
        video = 'rtmp://%s/rtmp app=rtmp swfUrl=http://tvisio.tv%s pageUrl=%s playpath=%s?start=%s conn=S:%s' % (v_server, v_swf, url, v_stream, v_start, v_session)
    else:
        video = 'rtmp://%s/rtmp app=rtmp swfUrl=http://tvisio.tv%s pageUrl=%s playpath=%s conn=S:%s' % (v_server, v_swf, url, v_stream, v_session)

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

#-- store cookies
cj.save()


