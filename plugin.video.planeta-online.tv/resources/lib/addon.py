#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#   Copyright (c) 2011 XBMC-Russia, HD-lab Team, E-mail: dev@hd-lab.ru
#   Writer (c) 2011, Kostynoy S.A., E-mail: seppius2@gmail.com
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

import sys, xbmc, xbmcgui, xbmcplugin, xbmcaddon
import os, urllib, urllib2, re

import html5lib
from html5lib import treebuilders

__addon__ = xbmcaddon.Addon( id = 'plugin.video.planeta-online.tv' )
__language__ = __addon__.getLocalizedString

addon_id      = __addon__.getAddonInfo( 'id' )
#addon_path    = __addon__.getAddonInfo( 'path' )
addon_name    = __addon__.getAddonInfo( 'name' )
addon_version = __addon__.getAddonInfo( 'version' )
#addon_author  = __addon__.getAddonInfo( 'author' )

#icon = xbmc.translatePath( os.path.join( addon_path, 'icon.png' ) )

xbmc.log('[%s] Starting version [%s] "%s"' % (addon_id, addon_version, addon_name), 1)

h = int(sys.argv[1])

def GET(url):
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Opera/9.80 (X11; Linux i686; U; ru) Presto/2.7.62 Version/11.00')
	req.add_header('Accept', 'text/html, application/xml, application/xhtml+xml, */*')
	req.add_header('Accept-Language', 'ru,en;q=0.9')
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	return link

def getitems(params):
	http = GET('http://www.planeta-online.tv/')
	if http != None:
		DT = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder('dom')).parse(http)
		for div0 in DT.getElementsByTagName('div'):
			if div0.getAttribute('id') == 'mainChannelList':
				for div1 in div0.getElementsByTagName('a'):
					if div1.getAttribute('class') == 'tip_trigger chA':
						title = None
						img = None
						for child in div1.childNodes:
							if child.nodeType == child.TEXT_NODE:
								title = child.data.encode('utf8')
							else:
								for imgs in child.getElementsByTagName('img'):
									img = 'http://www.planeta-online.tv%s' % imgs.getAttribute('src').encode('utf8')
						if title and img:
							uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'play', 'href':div1.getAttribute('href')}))
							i = xbmcgui.ListItem(title, iconImage = img, thumbnailImage = img)
							i.setProperty('IsPlayable', 'true')
							xbmcplugin.addDirectoryItem(h, uri, i)
		xbmcplugin.endOfDirectory(h)

def play(params):
	url = 'http://www.planeta-online.tv%s' % params['href']
	response = GET(url)
	SWFObject = 'http://www.planeta-online.tv%s' % re.compile('embedSWF\("(.*?)"').findall(response)[0]
	flashvars = re.compile('.*?:"(.*?)"').findall(re.compile('var flashvars = \{(.*?)\};', re.DOTALL).findall(response)[0].replace(',',',\n'))
	for fval in flashvars:
		if fval.startswith('rtmp://'):
			xbmcplugin.setResolvedUrl(h, True, xbmcgui.ListItem(path = '%s swfurl=%s pageUrl=%s swfVfy=True Live=True' % (fval, SWFObject, url)))
			return True

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
		func = None
		xbmc.log( '[%s]: Primary input' % addon_id, 1 )
		getitems(params)

	if func != None:
		try: pfunc = globals()[func]
		except:
			pfunc = None
			xbmc.log( '[%s]: Function "%s" not found' % (addon_id, func), 4 )
			showMessage('Internal addon error', 'Function "%s" not found' % func, 2000)
		if pfunc: pfunc(params)
