#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#   Copyright (c) 2011 XBMC-Russia, HD-lab Team, E-mail: dev@hd-lab.ru
#   Writer (c) 12/03/2011, Kostynoy S.A., E-mail: seppius2@gmail.com
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
import os, urllib, urllib2, xml.dom.minidom


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


def GET(targeturl):
	req = urllib2.Request(targeturl)
	req.add_header(     'User-Agent','Mozilla/5.0 (X11; Linux i686) AppleWebKit/534.32 SUSE/13.0.751.0 (KHTML, like Gecko) Chrome/13.0.751.0 Safari/534.32')
	req.add_header(         'Accept','text/css,*/*;q=0.1')
	req.add_header('Accept-Language','ru-RU,ru;q=0.9,en;q=0.8')
	req.add_header( 'Accept-Charset','utf-8, utf-16, *;q=0.1')
	req.add_header('Accept-Encoding','plain')
	req.add_header(     'Connection','Keep-Alive')
	req.add_header(        'Referer','http://tvrain.ru/')
	f = urllib2.urlopen(req)
	a = f.read()
	f.close()
	return a

def getitems(params):
	try:
		#http = GET('http://tvrain.ru/player/iframe.php')
		http = GET('http://tvrain.slon.ru/player/iframe.php')
		#print http
		r1 = re.compile('bitrates: \[(.*?)\]' ,re.DOTALL).findall(http)
		if len(r1) > 0:
			#print '1'
			r2 = re.compile('url:.+?\"(.*?)\"').findall(r1[0])
			if len(r2) > 0:
				#print '2'
				for cur_file in r2:
					#cur_file2 = urllib.unquote_plus(cur_file)
					cur_file2 = cur_file
					if  '340k' in cur_file2:  title = 'ДОЖДЬ (340 kbps)'
					elif '640k' in cur_file2: title = 'ДОЖДЬ (640 kbps)'
					elif '1m' in cur_file2:   title = 'ДОЖДЬ (1 Mbps)'
					else: title = 'ДОЖДЬ'
					swfUrl  = 'http://tvrain.ru/bitrix/templates/include/js/flowplayer/flowplayer.cluster-3.2.3.swf'
					tcUrl   = 'rtmp://tvrain-video.ngenix.net/secure'
					pageUrl = 'http://tvrain.ru/bitrix/templates/include/js/flowplayer/flowplayer-3.2.7.swf'
					general = 'rtmp://tvrain-video.ngenix.net:80/secure'
					uri = '%s swfUrl=%s tcUrl=%s pageUrl=%s playpath=%s swfVfy=true' % (general, swfUrl, tcUrl, pageUrl, cur_file2)
					li = xbmcgui.ListItem(title, iconImage = icon, thumbnailImage = icon)
					li.setProperty('IsPlayable', 'true')
					xbmcplugin.addDirectoryItem(h, uri, li)
	except:
		pass

	li = xbmcgui.ListItem('ДОЖДЬ (iPad)', iconImage = icon, thumbnailImage = icon)
	li.setProperty('IsPlayable', 'true')
	xbmcplugin.addDirectoryItem(h, 'http://tvrain-video.ngenix.net/mobile/TVRain1_ipad.stream/playlist.m3u8', li)

	li = xbmcgui.ListItem('ДОЖДЬ (iPhone)', iconImage = icon, thumbnailImage = icon)
	li.setProperty('IsPlayable', 'true')
	xbmcplugin.addDirectoryItem(h, 'http://tvrain-video.ngenix.net/mobile/TVRain1_iphone.stream/playlist.m3u8', li)

	xbmcplugin.endOfDirectory(h)




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
		getitems(params)
		func = None

	if func != None:
		try: pfunc = globals()[func]
		except:
			pfunc = None
			print '[%s]: Function "%s" not found' % (addon_id, func)
			showMessage('Internal addon error', 'Function "%s" not found' % func, 2000)
		if pfunc: pfunc(params)
