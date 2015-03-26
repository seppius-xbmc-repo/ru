#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2011, myvi.ru
# Writer (c) 2011, Kostynoy S.A., E-mail: seppius2@gmail.com

import sys, xbmc, xbmcgui, xbmcplugin, xbmcaddon
import os, urllib, urllib2, re


__addon__ = xbmcaddon.Addon(id = 'plugin.video.myvi.ru')

addon_icon    = __addon__.getAddonInfo('icon')
addon_fanart  = __addon__.getAddonInfo('fanart')
addon_path    = __addon__.getAddonInfo('path')
addon_type    = __addon__.getAddonInfo('type')
addon_id      = __addon__.getAddonInfo('id')
addon_author  = __addon__.getAddonInfo('author')
addon_name    = __addon__.getAddonInfo('name')
addon_version = __addon__.getAddonInfo('version')

icon   = xbmc.translatePath(addon_icon)
fanart = xbmc.translatePath(addon_fanart)


__language__ = __addon__.getLocalizedString

h = int(sys.argv[1])

try:
	import json
except ImportError:
	print '[%s]: Error import json. Uses module demjson2.' % addon_id
	import demjson2 as json

try:
	import socket
	socket.setdefaulttimeout([5,10,15,20,30,45,60,100][int(__addon__.getSetting('timeout'))])
except Exception, e:
	print '[%s]: Error setting default timeout [%s]' % (addon_id, e)


def showMessage(heading, message, times = 3000, pics = icon):
	try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading.encode('utf-8'), message.encode('utf-8'), times, pics))
	except Exception, e:
		print '[%s]: showMessage: Transcoding UTF-8 failed [%s]' % (addon_id, e)
		try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, pics))
		except Exception, e:
			print '[%s]: showMessage: exec failed [%s]' % (addon_id, e)


def GET(href, post=None):
	UniversalUserID   = __addon__.getSetting('UniversalUserID')
	listsize = [10,25,30,50,100][int(__addon__.getSetting('size'))]
	aUA = '%s/%s %s/%s/%s' % (addon_type, addon_id, addon_author, addon_version, urllib.quote_plus(addon_name))
	headers = {'User-Agent':aUA}
	try:
		if href.startswith('http://') or href.startswith('https://'): target = href
		else: target = 'http://anime.myvi.ru/xbmc/fresh'
		cooks = {'UniversalUserID':UniversalUserID}
		if '?' in target: target += '&size=%s' % listsize
		else: target += '?size=%s' % listsize
		headers['Cookie'] = urllib.urlencode(cooks).replace('&','; ')
		req = urllib2.Request(url = target, data = post, headers = headers)
		resp = urllib2.urlopen(req)
		SetCookie = resp.headers.get('set-cookie')
		UniversalUserID = re.compile('UniversalUserID=(.+?);').findall(SetCookie)
		if len(UniversalUserID):
			__addon__.setSetting('UniversalUserID', UniversalUserID[0])
		http = resp.read()
		resp.close()
		return http
	except Exception, e:
		print '[%s]: GET EXCEPT [%s]' % (addon_id, e)
		showMessage('HTTP ERROR', e, 5000)


def advt_show(jsdata):
	try:    adv = jsdata['advt']
	except: return
	if adv['type'] == 'showmessage': showMessage(adv['heading'], adv['message'], adv['delay'], adv['picture'])
	elif adv['type'] == 'dialogOK':  xbmcgui.Dialog().ok(adv['heading'],adv['lines'])
	elif adv['type'] == 'textbox':  TextReader(txt_data = adv['text']).doModal()
	else: print '[%s]: Unsupported adv type' % addon_id


def getitems(params):
	try: href = params['href']
	except: href = ''
	try:
		usreq = params['usreq'].lower()
		if usreq == 'keyboard':
			kbd = xbmc.Keyboard()
			kbd.setDefault(params['kbtext'])
			kbd.setHeading(params['kbhead'])
			kbd.setHiddenInput(eval(params['kbmask']))
			kbd.doModal()
			if kbd.isConfirmed():
				answer = kbd.getText()
			else:
				return False
		elif usreq == 'numeric':
			nutype = int(params['nutype'])
			nuhead = params['nuhead']
			nutext = params['nutext']
			answer = xbmcgui.Dialog().numeric(nutype, nuhead, nutext)
			if nutext == answer:
				return False
		elif usreq == 'select':
			sehead = params['sehead']
			selist = params['selist'].split('\n')
			answer = xbmcgui.Dialog().select(sehead, selist)
			if answer == -1:
				return False
		elif usreq == 'yesno':
			ynhead = params['ynhead']
			yntext = params['yntext'].split('\n')
			answer = xbmcgui.Dialog().yesno(addon_name, ynhead, '', '', yntext[0], yntext[1])
		else:
			return False
		href += '&answer=%s' % urllib.quote_plus(answer)
	except: pass
	http = GET(href)
	if http == None: return False
	jsdata = json.loads(http)
	dispitem = 0
	for item in jsdata:
		isitem = False
		try:
			title = item['title']
			uri   = item['uri']
			del item['uri']
			uri = '%s?%s'%(sys.argv[0], uri)
			isitem = True
		except: pass
		if isitem:
			try:
				item_type = item['type']
				del item['type']
			except: item_type = 'video'
			try:
				IsPlayable = item['playable']
				del item['playable']
			except: IsPlayable = False
			try:
				IsFolder = item['folder']
				del item['folder']
			except: IsFolder = False
			try:    ico_img = item['icons'][0]
			except: ico_img = ''
			try:    thu_img = item['icons'][1]
			except: thu_img = ''

			i = xbmcgui.ListItem(title, iconImage = ico_img, thumbnailImage = thu_img)
			try: i.setProperty('fanart_image', item['icons'][2])
			except: i.setProperty('fanart_image', fanart)

			try: del item['icons']
			except: pass
			try:
				conmenu = item['conmenu']
				del item['conmenu']
				cm = []
				for curcm in conmenu['items']:
					cm.append((curcm['name'].encode('utf8','ignore'), 'xbmc.runPlugin(%s?%s)' % (sys.argv[0], curcm['uri'])))
				i.addContextMenuItems(items=cm, replaceItems=conmenu['replace'])
			except: pass
			try:
				i.setProperty('mimetype', item['mimetype'])
				del item['mimetype']
			except: pass
			workitem = {}
			for citem in item:
				if item[citem] != None: workitem[citem] = item[citem]
			i.setInfo(type = item_type, infoLabels = workitem)
			if IsPlayable: i.setProperty('IsPlayable', 'true')
			xbmcplugin.addDirectoryItem(h, uri, i, IsFolder)
			dispitem += 1
		else:
			advt_show(item)
	if dispitem > 0:
		xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_UNSORTED)
		xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_DATE)
		xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_DURATION)
		xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_GENRE)
		xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_TITLE)
		xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_VIDEO_RATING)
		xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_VIDEO_RUNTIME)
		xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_VIDEO_TITLE)
		xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
		xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_LABEL)
		xbmcplugin.endOfDirectory(h)
	else: return False


def play(params):
	UniversalUserID   = __addon__.getSetting('UniversalUserID')
	CooData = urllib.urlencode({'UniversalUserID':UniversalUserID}).replace('&','; ')
	http = GET(urllib.unquote_plus(params['href']))
	if http == None: return False
	jsdata = json.loads(http)
	if len(jsdata) > 1:
		play_path = 'stack://'
		for pitem in jsdata:
			cpitem = '%s|Cookie=%s' % (pitem, CooData)
			play_path += cpitem.replace(',',',,') + ' , '
		play_path = play_path[:-3]
	elif len(jsdata) == 1:
		play_path = '%s|Cookie=%s' % (jsdata[0], CooData)
	i = xbmcgui.ListItem(path=play_path)
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
		getitems(params)

	if func != None:
		try: pfunc = globals()[func]
		except:
			pfunc = None
			print '[%s]: Function "%s" not found' % (addon_id, func)
			showMessage('Internal addon error', 'Function "%s" not found' % func, 2000)
		if pfunc: pfunc(params)
