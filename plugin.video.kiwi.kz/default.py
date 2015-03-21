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

import xbmc, xbmcgui, xbmcplugin, xbmcaddon, re
import os, urllib, urllib2
import socket
socket.setdefaulttimeout(15)


h = int(sys.argv[1])
icon = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'icon.png'))
fanartimage = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'fanart.jpg'))


def strip_html(text):
	def fixup(m):
		text = m.group(0)
		if text[:1] == "<":
			if text[1:3] == 'br':
				return '\n'
			else:
				return "" # ignore tags
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




def showMessage(heading, message, times = 3000, pics = icon):
	xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, pics))



def GET(target):
	#xbmc.output('target='+target)
	try:
		req = urllib2.Request(target)
		req.add_header(     'User-Agent','XBMC/10-series (Python addon; XBMC-Russia; HD-lab Team; 2011; http://www.xbmc.ru)')
		req.add_header(         'Accept','text/html, application/xml, application/xhtml+xml, image/png, image/jpeg, image/gif, image/x-xbitmap, */*')
		req.add_header('Accept-Language','ru-RU,ru;q=0.9,en;q=0.8')
		req.add_header( 'Accept-Charset','utf-8, utf-16, *;q=0.1')
		req.add_header('Accept-Encoding','identity, *;q=0')
		req.add_header(     'Connection','Keep-Alive')
		f = urllib2.urlopen(req)
		a = f.read()
		f.close()
		#xbmc.output(a)
		return a
	except Exception, e:
		showMessage(target, e, 5000)
		return None



def showroot(params):
	li = xbmcgui.ListItem('Видео', iconImage=icon, thumbnailImage=icon)
	li.setProperty('fanart_image', fanartimage)
	xbmcplugin.addDirectoryItem(h, '%s?mode=showlist&target=%s&page=1&subsys=watch'%(sys.argv[0], urllib.quote_plus('http://kiwi.kz/tracks/tracks/page/')), li, True)
	li = xbmcgui.ListItem('Каналы', iconImage=icon, thumbnailImage=icon)
	li.setProperty('fanart_image', fanartimage)
	xbmcplugin.addDirectoryItem(h, '%s?mode=showlist&target=%s&page=1&subsys=channels'%(sys.argv[0], urllib.quote_plus('http://kiwi.kz/channels/channels/page/')), li, True)
	li = xbmcgui.ListItem('Трансляции', iconImage=icon, thumbnailImage=icon)
	li.setProperty('fanart_image', fanartimage)
	xbmcplugin.addDirectoryItem(h, '%s?mode=showlist&target=%s&page=1&subsys=broadcast'%(sys.argv[0], urllib.quote_plus('http://kiwi.kz/broadcast/broadcasts?sort=viewers&category=Array&page=')), li, True)
	li = xbmcgui.ListItem('Радио', iconImage=icon, thumbnailImage=icon)
	li.setProperty('fanart_image', fanartimage)
	xbmcplugin.addDirectoryItem(h, '%s?mode=showlist&target=%s&page=1&subsys=radio'%(sys.argv[0], urllib.quote_plus('http://kiwi.kz/radio/radio/page/')), li, True)
	li = xbmcgui.ListItem('ТВ', iconImage=icon, thumbnailImage=icon)
	li.setProperty('fanart_image', fanartimage)
	xbmcplugin.addDirectoryItem(h, '%s?mode=showlist&target=%s&page=1&subsys=tv'%(sys.argv[0], urllib.quote_plus('http://kiwi.kz/tv/tv/page/')), li, True)
	xbmcplugin.endOfDirectory(h)




def showlist(params):
	try:    target = urllib.unquote_plus(params['target'])
	except: target = ''
	try:    page = int(params['page'])
	except: page = 1
	try:    subsys = params['subsys']
	except: subsys = 'none'

	http = GET('%s%d'%(target,page))
	if http == None:
		return False


	r1 = re.compile('<a href="http://kiwi.kz/%s/(.*?)".+?>(.*?)</a>'%subsys).findall(http)
	if len(r1) == 0:
		showMessage('Ой, ошибка', 'Не найдено ссылок %s'%subsys)
		return False
	for wid, wname in r1:
		wname = strip_html(wname)
		wid = wid.replace('/','').replace(' ','')
		r2 = re.compile('<img id="track_img_%s" class="screenshot" src="(.*?)">'%wid).findall(http)
		if len(r2) > 0:
			thumb = r2[0]
		else: thumb = icon
		ntarget = 'http://kiwi.kz/%s/%s/'%(subsys,wid)
		li = xbmcgui.ListItem(wname, iconImage = thumb, thumbnailImage = thumb)
		li.setProperty('fanart_image', fanartimage)
		li.setProperty('IsPlayable', 'true')
		if subsys == 'radio':
			#li.setProperty('mimetype',   'audio/mp3')
			tt = 'music'
		else:
			li.setProperty('mimetype',   'video/mp4')
			tt = 'video'
		li.setInfo(type=tt, infoLabels={'title':wname})
		uri = '%s?mode=watch&target=%s' % (sys.argv[0], urllib.quote_plus(ntarget))
		xbmcplugin.addDirectoryItem(h, uri, li)

	li = xbmcgui.ListItem('Далее >', iconImage = icon, thumbnailImage = icon)
	li.setProperty('fanart_image', fanartimage)
	xbmcplugin.addDirectoryItem(h, '%s?mode=showlist&target=%s&page=%d&subsys=%s'%(sys.argv[0], urllib.quote_plus(target), page+1, subsys), li, True)


	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_UNSORTED)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.endOfDirectory(h)


def watch(params):
	try:    target = urllib.unquote_plus(params['target'])
	except: target = ''

	http = GET(target)
	if http == None:
		return False

	if target.find('radio') != -1:
		r1 = re.compile('<div class="player-code-input">.+?name="watch_url" id="watch_url" value="(.*?)".+?></div></div>').findall(http)
	else:
		r1 = re.compile('file=(.*?)\&').findall(http)

	if len(r1) == 0:
		showMessage('Ой, ошибка', 'Не найдено ссылок на file')
		return False

	fname = urllib.unquote_plus(r1[len(r1)-1])

	li = xbmcgui.ListItem(path = fname)
	xbmcplugin.setResolvedUrl(h, True, li)



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
try:    mode = urllib.unquote_plus(params['mode'])
except: showroot(params)

if mode != None:
	try:    func = globals()[mode]
	except: pass
	if func: func(params)



#GET http://kiwi.kz/broadcast/broadcasts?page=1&sort=viewers&category=Array
#BAD
#GET http://kiwi.kz/channels/channels/page/1
#<a class="channel-badge-link" href="(.*?)">\s.+?<img src="(.*?)">\s.+?</a>
#FULL_URL (http://kiwi.kz/user/Proofik/) http://kiwi.kz/user/(.*?)/
#FULL_IMG
#GET http://kiwi.kz/user/vladikPL/video/?sort=latest&time=alltime&category=all&page=
