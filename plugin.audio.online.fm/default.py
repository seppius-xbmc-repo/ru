#!/usr/bin/python
# -*- coding: utf-8 -*-
#/*
# *  Copyright (c) 2011-2012 XBMC-Russia, HD-lab Team, E-mail: dev@hd-lab.ru
# *  Writer (c) 2011, Kostynoy S.A., E-mail: seppius2@gmail.com
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

import urllib,urllib2,os
import xbmcplugin,xbmcgui
import demjson
import random

h = int(sys.argv[1])
img = os.path.join(os.getcwd().replace(';', ''), "icon.png" )

def getURL(url):
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (X11; U; Linux i686; ru; rv:1.9.2.12) Gecko/20101026 SUSE/3.6.12-0.7.1 Firefox/3.6.12')
	req.add_header('Accept', 'text/html, application/xml, application/xhtml+xml, */*')
	req.add_header('Accept-Language', 'ru,en;q=0.9')
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	return link


def GetRoot():
	djson = demjson.decode(getURL('http://online.fm/ext/config.json'))
	for ch in djson['channels']:
		n = djson['channels'][ch]['name']
		u = djson['channels'][ch]['uris']
		i = xbmcgui.ListItem(n, iconImage=img, thumbnailImage=img)
		i.setInfo(type='music', infoLabels = {'title': n})
		uri = sys.argv[0] + '?mode=PLAY'
		uri += '&first=%s'%urllib.quote_plus(u[0])
		uri += '&secon=%s'%urllib.quote_plus(u[1])
		uri += '&ch=%s'%urllib.quote_plus(ch)
		i.setProperty('IsPlayable', 'true')
		xbmcplugin.addDirectoryItem(h, uri, i)
	xbmcplugin.endOfDirectory(h)


def Play(first, secon, ch):
	swfUrl  = 'http://online.fm/player/fm/flash/JSPlayer.swf'
	pageUrl = 'http://online.fm/player/ru/%s'%ch
	snb     = '%s/ PlayPath=%s swfurl=%s tcUrl=%s pageUrl=%s swfVfy=True'
	if random.random() > 0.5: srv = first
	else: srv = secon
	p = snb%(srv, ch, swfUrl, srv, pageUrl)
	i = xbmcgui.ListItem(path = p)
	xbmcplugin.setResolvedUrl(h, True, i)


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

params=get_params(sys.argv[2])
mode = None
first = ''
secon = ''

try:
	mode = urllib.unquote_plus(params['mode'])
except:
	pass
try:
	first = urllib.unquote_plus(params['first'])
except:
	pass
try:
	secon = urllib.unquote_plus(params['secon'])
except:
	pass
try:
	ch = urllib.unquote_plus(params['ch'])
except:
	pass

if mode == None:
	GetRoot()
if mode == 'PLAY':
	Play(first, secon, ch)

