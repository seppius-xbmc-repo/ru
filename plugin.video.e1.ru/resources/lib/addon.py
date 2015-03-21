#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#   Copyright (c) 2011 XBMC-Russia, HD-lab Team, E-mail: dev@hd-lab.ru
#   Writer (c) 25/05/2011, Kostynoy S.A., E-mail: seppius2@gmail.com
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


import sys, xbmc, xbmcgui, xbmcplugin, xbmcaddon, re
import os, urllib, urllib2, httplib, xml.dom.minidom, cookielib

import html5lib
from html5lib import treebuilders

icon   = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''), 'icon.png'))
h = int(sys.argv[1])


addon_id       = 'unknown addon id'
addon_name     = 'unknown addon'
addon_version  = '0.0.0'
addon_provider = 'unknown'

addon_xml = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'addon.xml'))
if os.path.isfile(addon_xml):
	af = open(addon_xml, 'r')
	adom = xml.dom.minidom.parseString(af.read())
	af.close()
	areg = adom.getElementsByTagName('addon')
	addon_id       = areg[0].getAttribute('id')
	addon_name     = areg[0].getAttribute('name')
	addon_version  = areg[0].getAttribute('version')
	addon_provider = areg[0].getAttribute('provider-name')

def showMessage(heading, message, times = 3000):
	xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))

__settings__ = xbmcaddon.Addon(id=addon_id)
__language__ = __settings__.getLocalizedString


def GET(tu):
	#print 'GET [%s]' % tu
	try:
		req = urllib2.Request(tu)
		req.add_header(     'User-Agent','Opera/9.80 (X11; Linux i686; U; ru) Presto/2.8.131 Version/11.10')
		req.add_header(         'Accept','text/html, application/xml, application/xhtml+xml, image/png, image/jpeg, image/gif, image/x-xbitmap, */*')
		req.add_header('Accept-Language','ru-RU,ru;q=0.9,en;q=0.8')
		req.add_header( 'Accept-Charset','utf-8, utf-16, *;q=0.1')
		req.add_header('Accept-Encoding','identity, *;q=0')
		req.add_header(     'Connection','Keep-Alive')
		f = urllib2.urlopen(req)
		a = f.read()
		f.close()
		#print a
		return a
	except Exception, e:
		showMessage(tu, e, 5000)
		return None


def showroot():
	http = GET('http://www.e1.ru/news/spool/section_id-107.html')
	if http != None:
		DT = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder('dom')).parse(http.decode('windows-1251', 'ignore'))
		for div in DT.getElementsByTagName('tr'):
			div0 = div.getElementsByTagName('td')
			if len(div0) > 0:
				div0 = div0[0]
				img = None
				title = None
				date_time = None
				href  = None
				for div1 in div0.getElementsByTagName('img'):
					if div1.getAttribute('class') == 'news_photo':
						img = 'http://www.e1.ru' + div1.getAttribute('src')
				for div1 in div0.getElementsByTagName('span'):
					if div1.getAttribute('class') == 'small_gray':
						date_time = div1.firstChild.data.encode('utf8', 'ignore')
				for div1 in div0.getElementsByTagName('a'):
					if div1.getAttribute('class') == 'news':
						if div1.getAttribute('title') and div1.getAttribute('href'):
							href  = div1.getAttribute('href').encode('utf8', 'ignore')
							title = div1.getAttribute('title').encode('utf8', 'ignore')
				if img and title and date_time and href:
					li = xbmcgui.ListItem('[%s] %s' % (date_time, title), iconImage = img, thumbnailImage = img)
					li.setProperty('IsPlayable', 'true')
					xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'watch', 'href':href})), li)
		xbmcplugin.endOfDirectory(h)


def watch(params):
	http = GET('http://www.e1.ru' + params['href'])
	if http != None:
		r1 = re.compile('\?hash\=(.*?)\"').findall(http)
		if len(r1) > 0:
			i = xbmcgui.ListItem(path = 'http://www.e1.ru/video-cache/%s.flv' % r1[0])
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
	if len(param) > 0:
		for cur in param:
			param[cur] = urllib.unquote_plus(param[cur])
	return param


def addon_main():
	params = get_params(sys.argv[2])
	try:
		func = params['func']
	except:
		showroot()
		func = None

	if func != None:
		try: pfunc = globals()[func]
		except:
			pfunc = None
			print '[%s]: Function "%s" not found' % (addon_id, func)
			showMessage('Internal addon error', 'Function "%s" not found' % func, 2000)
		if pfunc: pfunc(params)

