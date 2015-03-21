#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2011 XBMC-Russia, HD-lab Team, E-mail: dev@hd-lab.ru
# Writer (c) 2011, Kostynoy S.A., E-mail: seppius2@gmail.com

import sys, xbmc, xbmcgui, xbmcplugin, xbmcaddon
import os, urllib, urllib2, cookielib, base64
import sha

__addon__ = xbmcaddon.Addon( id = 'plugin.video.xbmc.rus' )
__language__ = __addon__.getLocalizedString

addon_id      = __addon__.getAddonInfo( 'id' )
addon_path    = __addon__.getAddonInfo( 'path' )
addon_name    = __addon__.getAddonInfo( 'name' )
addon_version = __addon__.getAddonInfo( 'version' )
addon_author  = __addon__.getAddonInfo( 'author' )

licf = xbmc.translatePath( os.path.join( addon_path, 'LICENSE.UTF8.TXT' ) )
icon = xbmc.translatePath( os.path.join( addon_path, 'icon.png' ) )

xbmc.log('[%s] Starting version [%s] "%s"' % (addon_id, addon_version, addon_name), 1)

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

try:
	import io, gzip
	AcceptEncoding = 'gzip'
except ImportError:
	xbmc.log( '[%s]: Error import io, gzip. Setting plain accept encoding.' % addon_id, 2 )
	AcceptEncoding = 'plain'

try:
	import socket
	socket.setdefaulttimeout([5,10,15,20,30,45,60,100][int(__addon__.getSetting('timeout'))])
except Exception, e:
	xbmc.log( '[%s]: Error setting default timeout [%s]' % (addon_id, e), 3 )


def showMessage(heading, message, times = 3000, pics = icon):
	try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading.encode('utf-8'), message.encode('utf-8'), times, pics.encode('utf-8')))
	except Exception, e:
		xbmc.log( '[%s]: showMessage: Transcoding UTF-8 failed [%s]' % (addon_id, e), 2 )
		try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, pics))
		except Exception, e:
			xbmc.log( '[%s]: showMessage: exec failed [%s]' % (addon_id, e), 3 )


class TextReader(xbmcgui.Window):
	def __init__(self, txt_data):
		self.bgread = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''), 'resources', 'img', 'background.png'))
		self.setCoordinateResolution(1) # 0 for 1080
		self.addControl(xbmcgui.ControlImage(0, 0, 1280, 720, self.bgread))
		self.NewsTextBox = xbmcgui.ControlTextBox(10,10,1260,700)
		self.addControl(self.NewsTextBox)
		self.NewsTextBox.setText(txt_data)
		self.scroll_pos = 0
	def onAction(self, action):
		aID = action.getId()
		if aID in [1,3,5]:
			self.scroll_pos -= 5
			self.NewsTextBox.scroll(self.scroll_pos)
		elif aID in [2,4,6]:
			self.scroll_pos += 5
			self.NewsTextBox.scroll(self.scroll_pos)
		elif aID in [9,10]: self.close()


def directshowtext(params):
	TextReader(txt_data = params['text']).doModal()


def showtext(params):
	http = GET(params['href'])
	TextReader(txt_data = http).doModal()


def builtin(params):
	try: xbmc.executebuiltin(urllib.unquote_plus(params['href']))
	except Exception, e:
		xbmc.log( '[%s]: builtin: exec failed [%s]' % (addon_id, e), 3 )


def GET(href, post=None):
	token0   = __addon__.getSetting('token0')
	token1   = __addon__.getSetting('token1')
	username = __addon__.getSetting('username')
	password = __addon__.getSetting('password')
	vquality = int(__addon__.getSetting('quality'))
	listsize = [10,25,50,100,150,200,250,300][int(__addon__.getSetting('size'))]
	aUA = 'XBMC/%s (%s; %s; %s; http://xbmc.ru; http://hd-lab.ru)' % (addon_id, urllib.quote_plus(addon_name), addon_version, addon_author)
	headers = {'Accept-Encoding':AcceptEncoding, 'User-Agent':aUA}
	try:
		if href.startswith('http://') or href.startswith('https://'):
			target = href
			sendpw = False
		else:
			target = base64.b64decode(__language__(30000)) + href
			sendpw = True
		CJ = cookielib.CookieJar()
		urllib2.install_opener(urllib2.build_opener(urllib2.HTTPCookieProcessor(CJ)))
		if sendpw: cooks = {'token0':token0, 'token1':token1, 'user':username, 'hash':sha.new(':%s:%s:%s:%s:'%(token0, token1, password, target)).hexdigest()}
		else:      cooks = {'token0':token0}
		cooks['size']  = listsize
		cooks['grade'] = vquality
		headers['Cookie'] = urllib.urlencode(cooks).replace('&','; ')
		req = urllib2.Request(url = target, data = post, headers = headers)
		resp = urllib2.urlopen(req)
		CE = resp.headers.get('content-encoding')
		if CE == 'bz2':
			import bz2
			http = bz2.decompress(resp.read())
		elif (CE == 'gzip'):
			bindata = io.BytesIO(resp.read())
			gzipf = gzip.GzipFile(fileobj = bindata, mode='rb')
			http = gzipf.read()
		else:
			xbmc.log( '[%s]: Unknown Content-Encoding [%s]' % (addon_id, CE), 3 )
			http = resp.read()
		for Cook in CJ:
			#resp.headers.get('set-cookie')
			if   Cook.name == 'token0': __addon__.setSetting('token0', Cook.value)
			elif Cook.name == 'token1': __addon__.setSetting('token1', Cook.value)
		resp.close()
		return http
	except Exception, e:
		xbmc.log( '[%s]: GET EXCEPT [%s]' % (addon_id, e), 4 )
		showMessage('HTTP ERROR', e, 5000)


def advt_show(jsdata):
	try:    adv = jsdata['advt']
	except: return
	if adv['type'] == 'showmessage': showMessage(adv['heading'], adv['message'], adv['delay'], adv['picture'])
	elif adv['type'] == 'dialogOK':  xbmcgui.Dialog().ok(adv['heading'],adv['lines'])
	elif adv['type'] == 'textbox':  TextReader(txt_data = adv['text']).doModal()
	else: xbmc.log( '[%s]: Unsupported adv type' % addon_id, 2 )


def getitems(params):

	if __addon__.getSetting('LicenseApproved') != 'true':
		xbmc.log( '[%s]: License not approved!' % addon_id, 2 )
		xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], 'func=licenseshow'), xbmcgui.ListItem('Читать соглашение'), False)

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
			except: pass
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


def Play_Exec(jsdata):
	selects = []
	jsdata = json.loads(jsdata)
	for item in jsdata:
		try:    selects.append(item['title'])
		except: xbmc.log( '[%s]: Skipping element without name' % addon_id, 2 )
	if   len(selects) == 0:
		script = None
		sparam = None
		try:
			script = jsdata[0]['script']
			sparam = jsdata[0]['params']
		except: pass
		if script != None:
			code = compile(script, '<string>', 'exec')
			ns = {}
			exec code in ns
			pdat = ns['getfiles'](sparam)
			args1 = []
			args2 = []
			args3 = []
			for arg1,arg2,arg3 in pdat:
				args1.append(arg1)
				args2.append(arg2)
				args3.append(arg3)
			if len(args1) > 0:
				s = xbmcgui.Dialog().select(addon_name, args1)
				if s < 0:
					return False
				else:
					arg2 = args2[s]
					arg3 = args3[s]
					pappends = ''
					if arg2.startswith('http://') or arg2.startswith('https://'):
						for parg in arg3: pappends += '&%s=%s' % (parg, urllib.quote_plus(arg3[parg]))
						if pappends != '':
							pappends = '|' + pappends[1:]
					elif arg2.startswith('rtmp://') or arg2.startswith('rtmpt://') or arg2.startswith('rtmpe://') or arg2.startswith('rtmpte://'):
						for parg in arg3: pappends += ' %s=%s' % (parg, arg3[parg])
					i = xbmcgui.ListItem(path = arg2 + pappends)
					xbmcplugin.setResolvedUrl(h, True, i)
					return True
			else:
				return False
		else:
			return False
	elif len(selects) == 1: s = 0
	else:
		s = xbmcgui.Dialog().select(addon_name, selects)
		if s < 0: return False
	sjs = jsdata[s]
	advt_show(sjs) # advt
	playables = []
	def parse_plist_section(arrs):
		if len(arrs) == 0: return
		for carr in arrs:
			vid_url = carr['url']
			pappends = ''
			try:
				vproto = carr['proto']
				try:
					vparam = carr['params']
					if vproto == 'rtmp':
						for pkeys in vparam: pappends += ' %s=%s' % (pkeys, vparam[pkeys])
					elif vproto == 'http':
						for pkeys in vparam: pappends += '&%s=%s' % (pkeys, urllib.quote_plus(vparam[pkeys]))
						if pappends != '':   pappends = '|' + pappends[1:]
					else: xbmc.log( '[%s]: Unsupported protocol [%s]' % (addon_id, vproto), 2 )
				except: pass
			except: pass
			playables.append(vid_url + pappends)
	try:    parse_plist_section(sjs['video'])
	except: pass
	if len(playables) == 0: return False
	play_path = ''
	if len(playables) > 1:
		play_path = 'stack://'
		for pitem in playables: play_path += pitem.replace(',',',,') + ' , '
		play_path = play_path[:-3]
	elif len(playables) == 1:
		play_path = playables[0]
	i = xbmcgui.ListItem(path=play_path)
	try:    i.setProperty('mimetype', sjs['mimetype'])
	except: pass
	xbmcplugin.setResolvedUrl(h, True, i)


def directplay(params):
	Play_Exec(params['href'])


def play(params):
	http = GET(urllib.unquote_plus(params['href']))
	if http == None: return False
	Play_Exec(http)


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


def licenseshow(params):
	af = open(licf, 'r')
	TextReader(txt_data = af.read()).doModal()
	af.close()
	if xbmcgui.Dialog().yesno(addon_name, 'Вы прочитали, принимаете и обязуетесь', 'выполнять условия соглашения?', 'Без этого дополнение не будет работать.', 'Отказаться', 'Принять'):
		xbmc.log( '[%s]: Has accepted license' % addon_id, 2 )
		__addon__.setSetting('LicenseApproved', 'true')
		xbmc.executebuiltin('Container.Refresh')
	else:
		xbmc.log( '[%s]: User refused license' % addon_id, 2 )


def addon_main():
	params = get_params(sys.argv[2])
	try:
		func = params['func']
	except:
		func = None
		xbmc.log( '[%s]: Primary input' % addon_id, 1 )
		if not os.path.isfile(licf):
			xbmc.log( '[%s]: The license file [%s] is missing!' % (addon_id, licf), 3 )
			xbmcgui.Dialog().ok(addon_name, 'Лицензионный файл отсутствует', 'Переустановите дополнение')
		getitems(params)
	if func != None:
		try: pfunc = globals()[func]
		except:
			pfunc = None
			xbmc.log( '[%s]: Function "%s" not found' % (addon_id, func), 4 )
			showMessage('Internal addon error', 'Function "%s" not found' % func, 2000)
		if pfunc: pfunc(params)
