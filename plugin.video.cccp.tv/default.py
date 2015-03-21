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
import urllib2, re, xbmc, xbmcgui, xbmcplugin, os, urllib, urllib2, socket

socket.setdefaulttimeout(12)

h = int(sys.argv[1])
icon = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'icon.png'))

def showMessage(heading, message, times = 3000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))

def strip_html(text):
	def fixup(m):
		text = m.group(0)
		if text[:1] == "<":
			if text[1:3] == 'br':
				return '\n'
			else:
				return ""
		if text[:2] == "&#":
			try:
				if text[:3] == "&#x":
					return chr(int(text[3:-1], 16))
				else:
					return chr(int(text[2:-1]))
			except ValueError:
				pass
		elif text[:1] == "&":
			import htmlentitydefs
			if text[1:-1] == "mdash":
				entity = " - "
			elif text[1:-1] == "ndash":
				entity = "-"
			elif text[1:-1] == "hellip":
				entity = "-"
			else:
				entity = htmlentitydefs.entitydefs.get(text[1:-1])
			if entity:
				if entity[:2] == "&#":
					try:
						return chr(int(entity[2:-1]))
					except ValueError:
						pass
				else:
					return entity
		return text
	ret =  re.sub("(?s)<[^>]*>|&#?\w+;", fixup, text)
	return re.sub("\n+", '\n' , ret)

def GET(url):
	try:
		print 'def GET(%s):'%url
		req = urllib2.Request(url)
		f = urllib2.urlopen(req)
		a = f.read()
		f.close()
		return a
	except:
		showMessage('Не могу открыть URL', url)
		return None


def ROOT():
	wurl = 'http://cccp.tv/'
	http = GET(wurl)
	if http == None: return False
	r1 = re.compile('<li class="li_year"><a href="(.*?)" class="rollerDate">(.*?)</a></li>').findall(http)
	if len(r1) == 0:
		showMessage('ПОКАЗАТЬ НЕЧЕГО', 'Нет элементов id,name,link,numberOfMovies')
		return False
	for href, name in r1:
		name = strip_html(name)
		i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
		u  = sys.argv[0] + '?mode=OPEN_MOVIES'
		u += '&url=%s'%urllib.quote_plus('http://cccp.tv' + href)
		u += '&name=%s'%urllib.quote_plus(name)
		xbmcplugin.addDirectoryItem(h, u, i, True)
	xbmcplugin.endOfDirectory(h)


def OPEN_MOVIES(params):
	http = GET(urllib.unquote_plus(params['url']))
	if http == None: return False
	rows = re.compile('<a href="(.+?)"><img src="(.+?)" alt="(.+?)" /></a>').findall(http)
	if len(rows) == 0:
		showMessage('ПОКАЗАТЬ НЕЧЕГО', 'Нет элементов href, img, alt')
		return False
	for href, img, alt in rows:
			img = 'http://cccp.tv' + img
			alt = strip_html(alt)
			i = xbmcgui.ListItem(alt, iconImage=img, thumbnailImage=img)
			u  = sys.argv[0] + '?mode=PLAY'
			u += '&url=%s'%urllib.quote_plus('http://cccp.tv' + href)
			i.setProperty('IsPlayable', 'true')
			xbmcplugin.addDirectoryItem(h, u, i)

	xbmcplugin.endOfDirectory(h)


def PLAY(params):
	http = GET(urllib.unquote_plus(params['url']))
	if http == None: return False
	rows1 = re.compile("url: '(.+?).flv',").findall(http)
	if len(rows1) == 0:
		showMessage('ОЙ', 'Нет FLV-видеофайла')
		return False
	i = xbmcgui.ListItem(path = rows1[0]+'.flv')
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

try:
	mode = urllib.unquote_plus(params['mode'])
except:
	ROOT()

if mode == 'OPEN_MOVIES':
	OPEN_MOVIES(params)

if mode == 'PLAY':
	PLAY(params)

