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

import sqlite3

class EasyDB:
    def __init__(self, filename):
        exists = os.path.exists(filename)

        self.connection = sqlite3.connect(filename)
        if not exists:
            query = "CREATE TABLE ignore (channel)"
            self.query(query)

    def __del__(self):
        self.connection.commit()
        self.connection.close()

    def query(self, *args, **kwargs):
        cursor = self.connection.cursor()
        result = cursor.execute(*args, **kwargs)
        return result

    def add(self, channel):
        query = "INSERT INTO ignore(channel) VALUES ('%s')" % channel
        self.query(query)

    def delete(self, channel):
        query = "DELETE FROM ignore WHERE channel = '%s'" % channel
        self.query(query)

    def exists(self, channel):
        query = "SELECT COUNT(*) as Cnt FROM ignore WHERE channel = '%s'" % channel
        rez = self.query(query)
        for rec in rez.fetchall():
            if rec[0] > 0:
                return True
            else:
                return False

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

Addon = xbmcaddon.Addon(id='plugin.video.telik.in.ua')
icon = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'),'icon.png'))
fcookies = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'), r'cookies.txt'))
db_file = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'),'ignore.db'))

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

#-- ignore list ----------------------------------------------------------------
def Add_To_Ignore(str):
    f = open('ignore.cfg', 'r')

#---------- get web page -------------------------------------------------------
def get_HTML(url, post = None, ref = None):
    request = urllib2.Request(url, post)
    print url
    if post == None:
        print '--- GET'
    else:
        print '--- POST'
    host = urlparse.urlsplit(url).hostname
    if ref==None:
        ref='http://'+host

    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host',   host)
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Language', 'ru-RU')
    request.add_header('Referer',             ref)

    #try:
    f = urllib2.urlopen(request)
    #except IOError, e:
	#if hasattr(e, 'reason'):
	 #  xbmc.log('We failed to reach a server.')
	#elif hasattr(e, 'code'):
	 #  xbmc.log('The server couldn\'t fulfill the request.')
    if f == None:
	html = ''
    else:
        html = f.read()

    return html

#---------- get list of TV channels --------------------------------------------
def Get_TV_Channels():
    db = EasyDB(db_file)

    #-- add config command
    name = ('[COLOR FFFF9900][B]'+'Настройки каналов'+'[/B][/COLOR]')#.encode('utf-8')

    i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
    u = sys.argv[0] + '?mode=CONFIG'
    xbmcplugin.addDirectoryItem(h, u, i, True)


    #-- list of available channels
    url = 'http://telik.in.ua/'
    html = get_HTML(url)

    soup = BeautifulSoup(html)

    for rec in soup.findAll('div', {'class':"movie"}):
        ch_url  = rec.find('a')['href']
        title   = rec.find('span', {'class':"name"}).text

        #-- check if channel in ignore list
        if db.exists(title):
            continue

        img     = "http://telik.in.ua/"+rec.find('img')['src']

        name = ('[COLOR FFCCFF33][B]'+title+'[/B][/COLOR]').encode('utf-8')

        i = xbmcgui.ListItem(name, iconImage=img, thumbnailImage=img)
        u = sys.argv[0] + '?mode=PLAY'
        u += '&name=%s'%urllib.quote_plus(name)
        u += '&url=%s'%urllib.quote_plus(ch_url)
        u += '&img=%s'%urllib.quote_plus(img)
        xbmcplugin.addDirectoryItem(h, u, i, False)

    for rec in soup.findAll('div', {'class':"movie last"}):
        ch_url  = rec.find('a')['href']
        title   = rec.find('span', {'class':"name"}).text
        img     = "http://telik.in.ua/"+rec.find('img')['src']

        name = ('[COLOR FFCCFF33][B]'+title+'[/B][/COLOR]').encode('utf-8')

        i = xbmcgui.ListItem(name, iconImage=img, thumbnailImage=img)
        u = sys.argv[0] + '?mode=PLAY'
        u += '&name=%s'%urllib.quote_plus(name)
        u += '&url=%s'%urllib.quote_plus(ch_url)
        u += '&img=%s'%urllib.quote_plus(img)
        xbmcplugin.addDirectoryItem(h, u, i, False)

    xbmcplugin.endOfDirectory(h)

#---------- config TV channels --------------------------------------------
def Config_TV_Channels():
    db = EasyDB(db_file)

    #-- list of available channels
    url = 'http://telik.in.ua/'
    html = get_HTML(url)

    soup = BeautifulSoup(html)

    for rec in soup.findAll('div', {'class':"movie"}):
        title   = rec.find('span', {'class':"name"}).text

        #-- check if channel in ignore list
        if db.exists(title):
            color = 'FFFF3300'
        else:
            color = 'FF99CC00'

        name = ('[COLOR '+color+'][B]'+title+'[/B][/COLOR]').encode('utf-8')

        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=?IGNORE'
        u += '&name=%s'%urllib.quote_plus(title.encode('utf-8'))
        xbmcplugin.addDirectoryItem(h, u, i, False)

    for rec in soup.findAll('div', {'class':"movie last"}):
        title   = rec.find('span', {'class':"name"}).text

        #-- check if channel in ignore list
        if db.exists(title):
            color = 'FFFF3300'
        else:
            color = 'FF99CC00'

        name = ('[COLOR '+color+'][B]'+title+'[/B][/COLOR]').encode('utf-8')

        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=?IGNORE'
        u += '&name=%s'%urllib.quote_plus(title.encode('utf-8'))
        xbmcplugin.addDirectoryItem(h, u, i, False)

    xbmcplugin.endOfDirectory(h)

#-------------------------------------------------------------------------------

def Ignore_TV_Channel(params):
    name = urllib.unquote_plus(params['name'])

    db = EasyDB(db_file)

    if db.exists(name):
        db.delete(name)
    else:
        db.add(name)

    xbmc.executebuiltin("Container.Refresh")
    xbmc.executebuiltin("Container.Update(plugin://plugin.video.telik.in.ua)")
    return False

#-------------------------------------------------------------------------------

def PLAY(params):
    # -- parameters
    url  = urllib.unquote_plus(params['url'])
    img  = urllib.unquote_plus(params['img'])
    name = urllib.unquote_plus(params['name'])

    # -- check if video available
    html = get_HTML(url)
    soup = BeautifulSoup(html)

    url = soup.find('iframe')['src']
    html = get_HTML(url)
    soup = BeautifulSoup(html)

    video = soup.find('embed')['src']

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
#try:
#   cj.load(ignore_discard=True)
#except:
#    pass
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
elif mode == 'CONFIG':
    Config_TV_Channels()
elif mode == 'IGNORE':
    Ignore_TV_Channel(params)

#-- store cookies
#cj.save(ignore_discard=True)


