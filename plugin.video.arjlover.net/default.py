#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#   Writer (c) 23/06/2011, Khrysev D.A., E-mail: x86demon@gmail.com
#
#   This Program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2, or (at your option)
#   any later version.
#
#   This Program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; see the file COPYING.  If not, write to
#   the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#   http://www.gnu.org/licenses/gpl.html

import httplib
import urllib
import urllib2
import re
import sys
import os
import Cookie

import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmc

from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
import socket
socket.setdefaulttimeout(50)

icon = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''), 'icon.png'))
siteUrl = 'arjlover.net'
httpSiteUrl = 'http://' + siteUrl
sid_file = os.path.join(xbmc.translatePath('special://temp/'), 'plugin.video.arjlover.net.cookies.sid')

h = int(sys.argv[1])

def construct_request(params):
	return '%s?%s' % (sys.argv[0], urllib.urlencode(params))

def htmlEntitiesDecode(string):
	return BeautifulStoneSoup(string, convertEntities=BeautifulStoneSoup.HTML_ENTITIES).contents[0]

def showMessage(heading, message, times = 3000):
	xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))

headers  = {
	'User-Agent' : 'Opera/9.80 (X11; Linux i686; U; ru) Presto/2.7.62 Version/11.00',
	'Accept'     :' text/html, application/xml, application/xhtml+xml, image/png, image/jpeg, image/gif, image/x-xbitmap, */*',
	'Accept-Language':'ru-RU,ru;q=0.9,en;q=0.8',
	'Accept-Charset' :'utf-8, utf-16, *;q=0.1',
	'Accept-Encoding':'identity, *;q=0'
}

def GET(target, referer, post_params = None, accept_redirect = True, get_redirect_url = False):
	try:
		connection = httplib.HTTPConnection(siteUrl)

		if post_params == None:
			method = 'GET'
			post = None
		else:
			method = 'POST'
			post = urllib.urlencode(post_params)
			headers['Content-Type'] = 'application/x-www-form-urlencoded'

		if os.path.isfile(sid_file):
			fh = open(sid_file, 'r')
			csid = fh.read()
			fh.close()
			headers['Cookie'] = 'session=%s' % csid

		headers['Referer'] = referer
		connection.request(method, target, post, headers = headers)
		response = connection.getresponse()

		if response.status == 403:
			raise Exception("Forbidden, check credentials")
		if response.status == 404:
			raise Exception("File not found")
		if accept_redirect and response.status in (301, 302):
			target = response.getheader('location', '')
			if target.find("://") < 0:
				target = httpSiteUrl + target
			if get_redirect_url:
				return target
			else:
				return GET(target, referer, post_params, False)

		try:
			sc = Cookie.SimpleCookie()
			sc.load(response.msg.getheader('Set-Cookie'))
			fh = open(sid_file, 'w')
			fh.write(sc['session'].value)
			fh.close()
		except: pass

		if get_redirect_url:
			return False
		else:
			http = response.read()
			return http

	except Exception, e:
		showMessage('Error', e, 5000)
		return None

def mainScreen(params):
	li = xbmcgui.ListItem('МУЛЬТФИЛЬМЫ')
	uri = construct_request({
		'href': 'http://multiki.arjlover.net/multiki/',
		'mode': 'getFiles'
	})
	xbmcplugin.addDirectoryItem(h, uri, li, True)

	li = xbmcgui.ListItem('ФИЛЬМЫ')
	uri = construct_request({
		'href': 'http://film.arjlover.net/film/',
		'mode': 'getFiles'
	})
	xbmcplugin.addDirectoryItem(h, uri, li, True)

	li = xbmcgui.ListItem('ДЕТСКИЕ ФИЛЬМЫ')
	uri = construct_request({
		'href': 'http://filmiki.arjlover.net/filmiki/',
		'mode': 'getFiles'
	})
	xbmcplugin.addDirectoryItem(h, uri, li, True)

	xbmcplugin.endOfDirectory(h)

def getFiles(params):
	categoryUrl = urllib.unquote_plus(params['href'])
	http = GET(categoryUrl, httpSiteUrl)
	if http == None: return False

	beautifulSoup = BeautifulSoup(http)
	links = beautifulSoup.findAll('td', 'l')

	if len(links) == 0:
		showMessage('ОШИБКА', 'Неверная страница', 3000)
		return False
	else:
		for link in links:
			try:
				titleText = link.find('a').string

				tds = link.findNextSiblings('td')
				href = tds[-1].find('a')['href']
				parts = href.split('/')

				li = xbmcgui.ListItem(titleText)
				li.setProperty('IsPlayable', 'true')
				li.setInfo(type='video', infoLabels={'title': titleText})
				uri = construct_request({
					'mode': 'play',
					'file': categoryUrl + parts[-1],
					'referer': categoryUrl
				})
				xbmcplugin.addDirectoryItem(h, uri, li)
			except:
				pass

	xbmcplugin.endOfDirectory(h)

def play(params):
	referer = urllib.unquote_plus(params['referer'])
	file = urllib.unquote_plus(params['file'])
	headers['Referer'] = referer

#	file = urllib.urlopen(file)
#	fileUrl = file.geturl()
#	i = xbmcgui.ListItem(path = fileUrl)

	i = xbmcgui.ListItem(path = file)
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

params = get_params(sys.argv[2])

mode   = None
func   = None

try:
	mode = urllib.unquote_plus(params['mode'])
except:
	mainScreen(params)

if (mode != None):
	try:
		func = globals()[mode]
	except:
		pass
	if func: func(params)
