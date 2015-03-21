#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2011 XBMC-Russia, HD-lab Team, E-mail: dev@hd-lab.ru
# Writer (c) 2011, Kostynoy S.A., E-mail: seppius2@gmail.com

import sys, xbmc, xbmcgui, xbmcplugin, xbmcaddon, re
import os, urllib, urllib2

__addon__ = xbmcaddon.Addon( id = 'plugin.video.sovok.tv' )
__language__ = __addon__.getLocalizedString

addon_id      = __addon__.getAddonInfo( 'id' )
addon_path    = __addon__.getAddonInfo( 'path' )
addon_name    = __addon__.getAddonInfo( 'name' )
addon_version = __addon__.getAddonInfo( 'version' )
addon_author  = __addon__.getAddonInfo( 'author' )

icon = xbmc.translatePath( os.path.join( addon_path, 'icon.png' ) )

xbmc.log('[%s] Starting version [%s]' % (addon_id, addon_version), 1)

UA = 'Opera/9.80 (X11; Linux i686; U; ru) Presto/2.7.62 Version/11.00'

h = int(sys.argv[1])

try:
	import json
except ImportError:
	try:
		import simplejson as json
		xbmc.log( '[%s]: Error import json. Uses module simplejson' % addon_id, 2 )
	except ImportError:
		try:
			import demjson3 as json
			xbmc.log( '[%s]: Error import simplejson. Uses module demjson3' % addon_id, 3 )
		except ImportError:
			xbmc.log( '[%s]: Error import demjson3. Sorry.' % addon_id, 4 )

def GET(targeturl, referer = None):
	req = urllib2.Request(targeturl)
	req.add_header(     'User-Agent',UA)
	if referer:
		req.add_header(     'Referer',referer)
	req.add_header( 'Accept-Language','ru-RU,ru;q=0.9,en;q=0.8')
	req.add_header( 'Accept-Encoding','plain')
	req.add_header(      'Connection','Keep-Alive')
	req.add_header(    'Content-Type','application/x-www-form-urlencoded')
	req.add_header('X-Requested-With','XMLHttpRequest')
	req.add_header(          'Accept','application/json, text/javascript, */*')
	f = urllib2.urlopen(req)
	a = f.read()
	f.close()
	return a

def getitems(params):
	http = GET('http://sovok.tv/api.php?get=list', 'http://sovok.tv/viewvideo.php')
	if http != None:
		js = json.loads(http)
		for group in js['group']:
			i = xbmcgui.ListItem(group['name'], iconImage = icon, thumbnailImage = icon)
			uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'getgroup', 'tvgid':group['gid']}))
			xbmcplugin.addDirectoryItem(h, uri, i, True)
		for _list in js['list']:
			_img = 'http://sovok.tv/images/tv/%s.gif' % _list['cid']
			i = xbmcgui.ListItem(_list['name'], iconImage = _img, thumbnailImage = _img)
			uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'play', 'tvcid':_list['cid']}))
			i.setProperty('IsPlayable', 'true')
			xbmcplugin.addDirectoryItem(h, uri, i, False)
		xbmcplugin.endOfDirectory(h)

def getgroup(params):
	try:    tvgid = int(params['tvgid'])
	except: tvgid = 1
	http = GET('http://sovok.tv/api.php?get=list', 'http://sovok.tv/viewvideo.php')
	if http != None:
		js = json.loads(http)
		ch = None
		for group in js['group']:
			if group['gid'] == tvgid: ch = group['ch']
		for _list in js['list']:
			if int(_list['cid']) in ch:
				_img = 'http://sovok.tv/images/tv/%s.gif' % _list['cid']
				i = xbmcgui.ListItem(_list['name'], iconImage = _img, thumbnailImage = _img)
				uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'play', 'tvcid':_list['cid']}))
				i.setProperty('IsPlayable', 'true')
				xbmcplugin.addDirectoryItem(h, uri, i, False)
		xbmcplugin.endOfDirectory(h)

def play(params):
	http = GET('http://sovok.tv/api.php?channel=%s' % params['tvcid'], 'http://sovok.tv/viewvideo.php')
	i = xbmcgui.ListItem( path = re.compile('\"url\"\:\"(.*?)\"').findall(http)[0] )
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
