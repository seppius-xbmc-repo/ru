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
import re, os, urllib, urllib2, cookielib, time, random, sys
from time import gmtime, strftime
import urlparse
from datetime import date
import demjson3 as json
import subprocess, ConfigParser
import xbmc, xbmcgui, xbmcplugin, xbmcaddon

Addon = xbmcaddon.Addon(id='plugin.video.ultimatv.net')
xbmcplugin.setContent(int(sys.argv[1]), 'movies')
icon = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'),'icon.png'))
fcookies = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'), r'resources', r'data', r'cookies.txt'))

try:
    from hashlib import md5 as md5
except:
    import md5


# load XML library
lib_path = os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib')

sys.path.append(os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib'))
from BeautifulSoup  import BeautifulSoup
from ElementTree  import Element, SubElement, ElementTree

import HTMLParser
hpar = HTMLParser.HTMLParser()

h = int(sys.argv[1])

def showMessage(heading, message, times = 3000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))

#---------- HTPP interface -----------------------------------------------------
def get_HTML(url, post = None, ref = None, get_url = False):
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
           print 'We failed to reach a server.'
        elif hasattr(e, 'code'):
           print 'The server couldn\'t fulfill the request.'

    if get_url == True:
        html = f.geturl()
    else:
        html = f.read()

    return html

#---------- parameter/info structure -------------------------------------------
class Param:
    url             = ''
    name            = ''
    img             = ''
    group           = ''

def Empty():
    return False

#---------- get parameters -----------------------------------------------------
def Get_Parameters(params):
    #-- url
    try:    p.url = urllib.unquote_plus(params['url'])
    except: p.url = ''
    #-- img
    try:    p.img = urllib.unquote_plus(params['img'])
    except: p.img = ''
    #-- name
    try:    p.name = urllib.unquote_plus(params['name'])
    except: p.name = ''
    #-- group
    try:    p.group = urllib.unquote_plus(params['group'])
    except: p.group = ''
    #-----
    return p

def Empty():
    return False

#---------- group list ---------------------------------------------------------
def Group_List(params):
    #-- get filter parameters
    par = Get_Parameters(params)

    # add last viewed serial
    name = '[COLOR FF00FF00]'+ '[ИСТОРИЯ]' + '[/COLOR]'
    i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
    u = sys.argv[0] + '?mode=HISTORY'
    u += '&name=%s'%urllib.quote_plus(name)
    xbmcplugin.addDirectoryItem(h, u, i, True)

    post = None
    url = 'http://ultimatv.net/index.php'
    html = get_HTML(url, post)
    soup = BeautifulSoup(html, fromEncoding="utf-8")

    channels = soup.find('div', {'id':'div-main-c'})

    #-- get channels
    for rec in channels.findAll(re.compile('h2|div')):
        c_name = rec.name
        try:
            c_type = rec['class']
        except:
            c_type = ''

        if c_name == 'h2' or (c_name == 'div' and c_type == 'channel_logo'):
            if c_name == 'h2':
                name = rec.find('a').text.encode('utf-8')

                i = xbmcgui.ListItem('[COLOR FFFFF000]'+name+'[/COLOR]', iconImage=icon, thumbnailImage=icon)
                u = sys.argv[0] + '?mode=LIST'
                u += '&group=%s'%urllib.quote_plus(name)
                xbmcplugin.addDirectoryItem(h, u, i, True)

    xbmcplugin.endOfDirectory(h)

#---------- channel list ---------------------------------------------------------
def Channel_List(params):
    #-- get filter parameters
    par = Get_Parameters(params)

    post = None
    url = 'http://ultimatv.net/index.php'
    html = get_HTML(url, post)
    soup = BeautifulSoup(html, fromEncoding="utf-8")

    channels = soup.find('div', {'id':'div-main-c'})

    group_flag = False
    #-- get channels
    for rec in channels.findAll(re.compile('h2|div')):
        c_name = rec.name
        try:
            c_type = rec['class']
        except:
            c_type = ''

        if c_name == 'h2' or (c_name == 'div' and c_type == 'channel_logo'):
            if c_name == 'h2':
                if par.group == rec.find('a').text.encode('utf-8'):
                    group_flag = True
            else:
                if group_flag == True:
                    name = rec.find('img')['alt'].encode('utf-8')
                    url  = 'http://ultimatv.net/'+rec.find('a')['href']
                    img  = 'http://ultimatv.net/'+rec.find('img')['src']

                    i = xbmcgui.ListItem('[COLOR FF00FF00]   '+name+'[/COLOR]', path = urllib.unquote(url), thumbnailImage=img) # iconImage=mi.img
                    u = sys.argv[0] + '?mode=PLAY'
                    u += '&url=%s'%urllib.quote_plus(url)
                    u += '&name=%s'%urllib.quote_plus(name)
                    u += '&img=%s'%urllib.quote_plus(img)
                    i.setProperty('fanart_image', img)
                    #i.setProperty('IsPlayable', 'true')
                    xbmcplugin.addDirectoryItem(h, u, i, False)

    xbmcplugin.endOfDirectory(h)

#---------- history list ------------------------------------------------------
def History_List(params):
    # try to open history
    try:
        htree = ElementTree()
        htree.parse(os.path.join(Addon.getAddonInfo('path'), r'resources', r'data', r'history.xml'))
        xml_h = htree.getroot()
    except:
        xbmc.log("*** HISTORY NOT FOUND ")
        return False

    # build list of history
    for rec_h in xml_h:
        try:
            #get channel details
            name     = rec_h.find('Channel').text.encode('utf-8')
            img      = rec_h.find('Image').text
            url      = rec_h.find('URL').text

            i = xbmcgui.ListItem(rec_h.find('Date').text+' [COLOR FF00FF00]   '+name+'[/COLOR]', path = urllib.unquote(url), thumbnailImage=img) # iconImage=mi.img
            u = sys.argv[0] + '?mode=PLAY'
            u += '&url=%s'%urllib.quote_plus(url)
            u += '&name=%s'%urllib.quote_plus(name)
            u += '&img=%s'%urllib.quote_plus(img)
            i.setProperty('fanart_image', img)
            #i.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(h, u, i, False)
        except:
            pass

    xbmcplugin.endOfDirectory(h)

#-------------------------------------------------------------------------------

def PLAY(params):
    #-- get filter parameters
    par = Get_Parameters(params)
    #-- assemble video link
    post = None
    html = get_HTML(par.url, post)
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

    #-- save history
    Save_History(par.name, par.url, par.img)
    #-- play TV
    i = xbmcgui.ListItem(par.name, path = urllib.unquote(video), thumbnailImage=par.img)
    i.setProperty('IsPlayable', 'true')
    #xbmcplugin.setResolvedUrl(h, True, i)
    xbmc.Player( xbmc.PLAYER_CORE_MPLAYER).play(video, i)

#-------------------------------------------------------------------------------

def Save_History(name, url, img):
    tag = 'ch_'+f_md5(url).hexdigest()

    # get max history lenght
    try:
        max_history = (1, 5, 10, 20, 30, 50)[int(Addon.getSetting('history_len'))]
        if max_history > 99:
            max_history = 99
    except:
        max_history = 10

    sdate = today = date.today().isoformat()

    # load or create history file
    try:
        tree = ElementTree()
        tree.parse(os.path.join(Addon.getAddonInfo('path'), r'resources', r'data', r'history.xml'))
        xml1 = tree.getroot()
    except:
        # create XML structure
        xml1 = Element("ULTIMATV_HISTORY")

    # shrink history to limit
    if len(xml1) > max_history:
        idx = 1
        for rec in xml1:
            if idx >= max_history:
                xml1.remove(rec)
            idx = idx + 1

    xml_hist = None
    # update sequince number for history records
    for rec in xml1:
        if rec.tag == tag:
            rec.find("ID").text = str(0).zfill(2)
            xml_hist = rec
        else:
            rec.find("ID").text = str(int(rec.find("ID").text)+1).zfill(2)

    if xml_hist == None:
        xml_hist = SubElement(xml1, tag)
        SubElement(xml_hist, "ID").text     = str(0).zfill(2)
        SubElement(xml_hist, "Channel").text = unescape(name)
        SubElement(xml_hist, "URL").text    = url
        SubElement(xml_hist, "Image").text  = img
        SubElement(xml_hist, "Date").text   = sdate
    else:
        xml_hist.find("Date").text   = sdate

    # sort history by IDs
    xml1[:] = sorted(xml1, key=getkey)

    ElementTree(xml1).write(os.path.join(Addon.getAddonInfo('path'), r'resources', r'data', r'history.xml'), encoding='utf-8')

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

def getkey(elem):
    return elem.findtext("name")

def f_md5(str):
    try:
        rez = md5(str)
    except:
        rez = md5.md5(str)

    return rez

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

mode = None

#---------------------------------

try:
	mode = urllib.unquote_plus(params['mode'])
except:
	mode = '$'

if mode == '$':
    mode = 'GROUP'

if mode == 'LIST':
	Channel_List(params)
elif mode == 'GROUP':
    Group_List(params)
elif mode == 'HISTORY':
    History_List(params)
elif mode == 'EMPTY':
    Empty()
elif mode == 'PLAY':
	PLAY(params)



