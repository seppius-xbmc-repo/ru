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

import demjson3 as json
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
def Get_TV_Channels(params):
    # -- parameters
    archiv = []

    #-- get link to archive TV
    url = 'http://telepoisk.com/arhiv-tv/'
    html = get_HTML(url)
    # -- parsing web page
    soup = BeautifulSoup(html, fromEncoding="utf-8")
    for rec in soup.findAll('div', {'class':'products-img'}):
        try:
            img     = rec.find('img')['src']
            archiv.append(img)
        except:
            pass

    url = 'http://telepoisk.com/online-tv'
    html = get_HTML(url)
    archive_flag = 'N'
    # -- parsing web page
    soup = BeautifulSoup(html, fromEncoding="utf-8")
    for rec in soup.find('div', {'id':'aside'}).findAll('li'):
        try:
            name    = rec.find('h3').find('a').text.encode('utf-8')
            img     = 'http://telepoisk.com'+rec.find('img')['src']
            live    = 'http://telepoisk.com'+rec.find('a')['href']

            if rec.find('img')['src'] in archiv:
                i = xbmcgui.ListItem('[COLOR FF00FF00]'+name+'[/COLOR]', iconImage=img, thumbnailImage=img)
                u = sys.argv[0] + '?mode=LIVE_ARCHIVE'
                u += '&name=%s'%urllib.quote_plus(name)
                u += '&url=%s'%urllib.quote_plus(live)
                u += '&img=%s'%urllib.quote_plus(img)
                xbmcplugin.addDirectoryItem(h, u, i, True)
            else:
                i = xbmcgui.ListItem('[COLOR FF00FFFF]'+name+'[/COLOR]', iconImage=img, thumbnailImage=img)
                u = sys.argv[0] + '?mode=PLAY_LIVE'
                u += '&name=%s'%urllib.quote_plus(name)
                u += '&url=%s'%urllib.quote_plus(live)
                u += '&img=%s'%urllib.quote_plus(img)
                xbmcplugin.addDirectoryItem(h, u, i, False)
        except:
            pass

    xbmcplugin.endOfDirectory(h)
#-------------------------------------------------------------------------------

def Get_EPG_Date(params):
    img      = urllib.unquote_plus(params['img'])
    ch_name  = urllib.unquote_plus(params['name'])

    #-- watch archive
    #-- get MSK time
    MSK = time.mktime(MSK_time())
    #-- fill up ETR data list
    for day_off in range(0, 16):    #-- tvisio.tv keeps 2 weeks of TV data
        ETR_date = time.localtime(MSK-day_off*24*60*60)
        name = '[COLOR FF00FF00]'+unescape(strftime("%Y-%m-%d", ETR_date)).encode('utf-8')+'[/COLOR] ([COLOR FF3BB9FF]'+unescape(strftime("%A", ETR_date)).encode('utf-8')+'[/COLOR])'
        id   = str(ETR_date.tm_mday)+'-'+str(ETR_date.tm_mon)+'-'+str(ETR_date.tm_year) #strftime("%d-%m-%Y", ETR_date)
        i = xbmcgui.ListItem(name, iconImage=img, thumbnailImage=img)
        u = sys.argv[0] + '?mode=EPG'
        u += '&date=%s'%urllib.quote_plus(id)
        u += '&name=%s'%urllib.quote_plus(name)
        u += '&img=%s'%urllib.quote_plus(img)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    xbmcplugin.endOfDirectory(h)

#---------- get EPG for selected channel ---------------------------------------
def Get_EPG(params):
    # -- parameters
    epg_date     = urllib.unquote_plus(params['date'])
    img          = urllib.unquote_plus(params['img'])
    prg_name     = urllib.unquote_plus(params['name'])

    url = 'http://telepoisk.com/arhiv-tv/'+ epg_date
    html = get_HTML(url)

    # -- parsing web page ------------------------------------------------------
    soup = BeautifulSoup(html, fromEncoding="utf-8")
    for rec in soup.findAll('li', {'class':'box'}):
        try:
            if rec.find('img')['src'] in img:
                for epg in rec.findAll('p'):
                    try:
                        prg = 'http://telepoisk.com'+epg.find('a')['href']
                    except:
                        prg = '*'

                    epg_time = epg.text[0:5]
                    epg_name = epg.text[5:]
                    if epg_name[0] == ' ':
                        epg_name = epg_name[1:]

                    name = '[COLOR FF3BB9FF]'+unescape(epg_time).encode('utf-8')+'[/COLOR]'+' '
                    if prg == '*':
                        name += '[COLOR FFFF0000]'+unescape(epg_name).encode('utf-8')+'[/COLOR]'
                    else:
                        name += '[COLOR FFC3FDB8]'+unescape(epg_name).encode('utf-8')+'[/COLOR]'
                     #-- add line to EPG
                    i = xbmcgui.ListItem(name, iconImage=img, thumbnailImage=img)
                    u = sys.argv[0] + '?mode=PLAY'
                    u += '&name=%s'%urllib.quote_plus(name)
                    u += '&url=%s'%urllib.quote_plus(prg)
                    u += '&prg=%s'%urllib.quote_plus(prg_name+' '+name)
                    u += '&img=%s'%urllib.quote_plus(img)
                    xbmcplugin.addDirectoryItem(h, u, i, False)
        except:
            pass

    xbmcplugin.endOfDirectory(h)
#-------------------------------------------------------------------------------

def Get_Live_Archive(params):
    # -- parameters
    img      = urllib.unquote_plus(params['img'])
    name     = urllib.unquote_plus(params['name'])
    url      = urllib.unquote_plus(params['url'])

    #-- show live TV
    i = xbmcgui.ListItem('[COLOR FF3BB9FF]Онлайн ТВ[/COLOR]', iconImage=img, thumbnailImage=img)
    u = sys.argv[0] + '?mode=PLAY_LIVE'
    u += '&name=%s'%urllib.quote_plus(name)
    u += '&url=%s'%urllib.quote_plus(url)
    u += '&img=%s'%urllib.quote_plus(img)
    xbmcplugin.addDirectoryItem(h, u, i, False)
    #-- show EPG
    i = xbmcgui.ListItem('[COLOR FFC3FDB8]Архив телепередач[/COLOR]', iconImage=img, thumbnailImage=img)
    u = sys.argv[0] + '?mode=EPG_DATE'
    u += '&name=%s'%urllib.quote_plus(name)
    u += '&img=%s'%urllib.quote_plus(img)
    xbmcplugin.addDirectoryItem(h, u, i, True)

    xbmcplugin.endOfDirectory(h)

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

    rec = re.compile("jwplayer\('mediaspace'\).setup\({(.+?)}\);", re.MULTILINE|re.DOTALL).findall(html)[0]

    str =  '{'+rec.replace('\n','').replace(' ','').replace('\'','"')+'}'
    j1 = json.loads(str)

    v_server = j1['streamer']
    v_swf    = j1['flashplayer']
    v_stream = j1['file'][:-4]

    video = '%s app=file swfUrl=http://tvisio.tv%s pageUrl=%s playpath=%s swfVfy=1' % (v_server, v_swf, url, v_stream)

    i = xbmcgui.ListItem(name, path = urllib.unquote(video), thumbnailImage=img)
    i.setProperty('IsPlayable', 'true')

    xbmc.Player( xbmc.PLAYER_CORE_MPLAYER).play(video, i)

#-------------------------------------------------------------------------------

def PLAY_LIVE(params):
    #-- get filter parameters
    url  = urllib.unquote_plus(params['url'])
    img  = urllib.unquote_plus(params['img'])
    name = urllib.unquote_plus(params['name'])

    #-- assemble video link
    post = None
    html = get_HTML(url, post)
    soup = BeautifulSoup(html, fromEncoding="utf-8")

    url = soup.find('iframe')['src']

    html = get_HTML(url, post)
    soup = BeautifulSoup(html, fromEncoding="utf-8")

    f_str = soup.find('param',{'name':'flashVars'})['value']
    for rec in f_str.split('&'):
        if rec.split('=')[0] == 'videoid':
            varsideoid = rec.split('=')[1]
        if rec.split('=')[0] == 'sessid':
            sessid = rec.split('=')[1]

    url = 'http://clients.cdnet.tv/flashplayer/instruction.php?' + soup.find('object').find('param',{'name':'flashVars'})['value'].replace('videotype=','type=')+'&0.19851545616984367'
    html = get_HTML(url, post, 'http://clients.cdnet.tv/flashplayer/player.swf')

    soup = BeautifulSoup(html, fromEncoding="utf-8")
    if Addon.getSetting('HQ') == 'true':
        try:
            stream_sd = soup.find('root')['stream_hd']
            chanel_sd = soup.find('root')['chanel_hd']
        except:
            stream_sd = soup.find('root')['stream_sd']
            chanel_sd = soup.find('root')['chanel_sd']
    else:
        stream_sd = soup.find('root')['stream_sd']
        chanel_sd = soup.find('root')['chanel_sd']

    video = '%s/%s swfUrl=http://clients.cdnet.tv/flashplayer/player.swf pageUrl=http://clients.cdnet.tv/flashbroadcast.php?channel=%s token=%s live=true swfVfy=true' % (stream_sd, chanel_sd, varsideoid, 'Rd#n@k72JDh')

    #-- play TV
    i = xbmcgui.ListItem(name, path = urllib.unquote(video), thumbnailImage=img)
    i.setProperty('IsPlayable', 'true')
    xbmc.Player( xbmc.PLAYER_CORE_MPLAYER).play(video, i)
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
	Get_TV_Channels(params)

if mode == 'EPG_DATE':
	Get_EPG_Date(params)
elif mode == 'EPG':
	Get_EPG(params)
elif mode == 'LIVE_ARCHIVE':
	Get_Live_Archive(params)
elif mode == 'PLAY_LIVE':
	PLAY_LIVE(params)
elif mode == 'PLAY':
	PLAY(params)

#-- store cookies
cj.save()


