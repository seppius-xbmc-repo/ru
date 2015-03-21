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
# *  http://www.gnu.org/licenses/gpl.html
# */


import urllib,urllib2,os,re
import xbmcplugin,xbmcgui,xbmc

import socket
socket.setdefaulttimeout(15)

h = int(sys.argv[1])
icon = os.path.join(os.getcwd().replace(';', ''), "icon.png" )

def GET(url):
	try:
		req = urllib2.Request(url)
		req.add_header('User-Agent', 'XBMC/10-series (Python addon; XBMC-Russia; HD-lab Team; 2011; http://www.xbmc.ru)')
		req.add_header('Accept', 'text/html, application/xml, application/xhtml+xml, */*')
		req.add_header('Accept-Language', 'ru,en;q=0.9')
		response = urllib2.urlopen(req)
		link=response.read().decode('cp1251').encode('utf8')
		response.close()
		return link
	except:
		return None

def showroot(params):

	http = GET('http://sradio.ru/')
	if http == None: return False

	def make_url(hdata):
		hrefs = hdata.split('/')
		h1 = hrefs[len(hrefs)-2]
		h1 = h1.replace('bitrate', 'bit')
		h2 = hrefs[len(hrefs)-1]
		return 'http://sradio.ru/%s.php?c=%s'%(h1,h2)

	s1 = re.compile('<li><a href="http://sradio.ru/theme/(.*?)">(.*?)</a></li>').findall(http)
	if len(s1) > 0:
		for href, name in s1:
			href = 'http://sradio.ru/theme/' + href
			li = xbmcgui.ListItem('Формат: ' + name, iconImage = icon, thumbnailImage = icon)
			uri = sys.argv[0] + '?mode=openradio'
			uri += '&href='+urllib.quote_plus(make_url(href))
			uri += '&page=0'
			uri += '&name='+urllib.quote_plus(name)
			xbmcplugin.addDirectoryItem(h, uri, li, True)

	s1 = re.compile('<a href=http://sradio.ru/bitrate/(.*?)>(.*?)</a>').findall(http)
	if len(s1) > 0:
		for href, name in s1:
			href = 'http://sradio.ru/bitrate/' + href
			li = xbmcgui.ListItem('Битрейт: ' + name + 'kbps', iconImage = icon, thumbnailImage = icon)
			uri = sys.argv[0] + '?mode=openradio'
			uri += '&href='+urllib.quote_plus(make_url(href))
			uri += '&page=0'
			uri += '&name='+urllib.quote_plus(name)
			xbmcplugin.addDirectoryItem(h, uri, li, True)

	s1 = re.compile('<a href="http://sradio.ru/country/(.*?)">(.*?)</a>').findall(http)
	if len(s1) > 0:
		for href, name in s1:
			href = 'http://sradio.ru/country/' + href
			li = xbmcgui.ListItem('Страна: ' + name, iconImage = icon, thumbnailImage = icon)
			uri = sys.argv[0] + '?mode=openradio'
			uri += '&href='+urllib.quote_plus(make_url(href))
			uri += '&page=0'
			uri += '&name='+urllib.quote_plus(name)
			xbmcplugin.addDirectoryItem(h, uri, li, True)

	xbmcplugin.endOfDirectory(h)

def openradio(params):
	href = urllib.unquote_plus(params['href'])
	page = int(params['page'])
	http = GET(href + '&p=%d'%page)
	if http == None: return False

	s1 = re.compile('<a href=\'http://sradio.ru/live/(.*?)\'>(.*?)</a><td>(.*?)<td>(.*?)<td>').findall(http)
	if len(s1) > 0:
		for rid, name, bitrate, city in s1:
			nhref = 'http://sradio.ru/live/' + rid
			li = xbmcgui.ListItem('%s (%s, %s)'%(name, bitrate, city), iconImage = icon, thumbnailImage = icon)
			li.setInfo(type='music', infoLabels = {'title': '%s (%s, %s)'%(name, bitrate, city)})
			#li.setProperty('IsPlayable', 'true')
			uri = sys.argv[0] + '?mode=play'
			uri += '&href='+urllib.quote_plus(nhref)
			xbmcplugin.addDirectoryItem(h, uri, li, False)

	if len(s1) > 29:
		li = xbmcgui.ListItem('Далее, на страницу %d >'%(page+1), iconImage = icon, thumbnailImage = icon)
		uri = sys.argv[0] + '?mode=openradio'
		uri += '&href='+urllib.quote_plus(href)
		uri += '&page=%d'%(page+1)
		uri += '&name='+urllib.quote_plus(name)
		xbmcplugin.addDirectoryItem(h, uri, li, True)

	xbmcplugin.endOfDirectory(h)


def play(params):
	http = GET(urllib.unquote_plus(params['href']))
	if http == None: return False

	streams = []

	try:
		m3_id = re.compile('href="http://sradio.ru/stream/(.*?)\.m3u"').findall(http)[0]
		streams.append('http://sradio.ru/stream/%s.m3u' % m3_id)
	except: pass

	try:
		asx_id = re.compile('href="http://sradio.ru/asx/(.*?)\.asx"').findall(http)[0]
		streams.append('http://sradio.ru/asx/%s.asx' % asx_id)
	except: pass

	if len(streams) == 0:
		showMessage('НЕ МОГУ ВОСПРОИЗВЕСТИ', 'Не найдено потоков', 3000)
		return False

	if len(streams) > 1:
		s = xbmcgui.Dialog().select('Поток?', streams)
		if s < 0: return True
		purl = streams[s]
	else:
		purl = streams[0]

	#print 'purl=%s'%purl

	xbmc.Player().play(purl)

	#i = xbmcgui.ListItem(path = purl)
	#xbmcplugin.setResolvedUrl(h, True, i)


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

params = get_params(sys.argv[2])

mode   = None
func   = None

try:
	mode = urllib.unquote_plus(params['mode'])
except:
	showroot(params)

if (mode != None):
	try:
		func = globals()[mode]
	except:
		pass
	if func: func(params)

