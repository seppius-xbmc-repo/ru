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
import xml.dom.minidom

iSearch = 'http://www.tvigle.ru/iphone/iSearch.php?q=%s'
iTree   = 'http://www.tvigle.ru/iphone/iTree.php'

socket.setdefaulttimeout(12)

h = int(sys.argv[1])

icon = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'icon.png'))

def showMessage(heading, message, times = 3000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))

def GET(url):
	try:
		req = urllib2.Request(url)
		f = urllib2.urlopen(req)
		a = f.read()
		f.close()
		return a
	except:
		showMessage('Не могу открыть URL', url)
		return None

def ADD_SEARCH():
	i = xbmcgui.ListItem('[ Поиск ]', iconImage=icon, thumbnailImage=icon)
	u  = sys.argv[0] + '?mode=SEARCH'
	xbmcplugin.addDirectoryItem(h, u, i, True)

def ROOT():
	http = GET(iTree)
	if http == None: return False
	Dom = xml.dom.minidom.parseString(http)
	Rubricas = Dom.getElementsByTagName('rubrica')
	if len(Rubricas) == 0:
		showMessage('ПОКАЗАТЬ НЕЧЕГО', 'Не найдены элементы "rubrica"')
		return False
	for Rubrica in Rubricas:
		R_ID   = Rubrica.getAttribute('id')
		R_NAME = Rubrica.getAttribute('name')
		R_IMG  = Rubrica.getAttribute('img')
		i = xbmcgui.ListItem(R_NAME, iconImage=R_IMG, thumbnailImage=R_IMG)
		u  = sys.argv[0] + '?mode=OPEN_RUBRICA'
		u += '&rubID=%s'%R_ID
		xbmcplugin.addDirectoryItem(h, u, i, True)
	ADD_SEARCH()
	xbmcplugin.endOfDirectory(h)


def OPEN_RUBRICA(rubID):
	http = GET(iTree)
	if http == None: return False
	Dom = xml.dom.minidom.parseString(http)
	Rubricas = Dom.getElementsByTagName('rubrica')
	if len(Rubricas) == 0:
		showMessage('ПОКАЗАТЬ НЕЧЕГО', 'Не найдены элементы "rubrica"')
		return False
	for Rubrica in Rubricas:
		R_ID = Rubrica.getAttribute('id')
		if str(rubID) == str(R_ID):
			genre = Rubrica.getAttribute('name').encode('utf-8')
			Channels = Rubrica.getElementsByTagName('channels')
			for Channel in Channels:
				ch_id   = Channel.getAttribute('id')
				ch_name = Channel.getAttribute('name')
				ch_img  = Channel.getAttribute('img')
				i = xbmcgui.ListItem(ch_name, iconImage=ch_img, thumbnailImage=ch_img)
				u  = sys.argv[0] + '?mode=OPEN_CHANNEL'
				u += '&chid=%s'%urllib.quote_plus(ch_id)
				u += '&url=%s'%urllib.quote_plus('http://www.tvigle.ru/iphone/iList.php?cnl=%s'%ch_id)
				u += '&genre=%s'%urllib.quote_plus(genre)
				u += '&page=1'
				xbmcplugin.addDirectoryItem(h, u, i, True)
	ADD_SEARCH()
	xbmcplugin.endOfDirectory(h)


def OPEN_CHANNEL(url, page, genre):
	wurl = '%s&page=%d'%(url, page)
	http = GET(wurl)
	if http == None: return False
	Dom = xml.dom.minidom.parseString(http)
	videos = Dom.getElementsByTagName('video')
	lvideos = len(videos)
	if lvideos == 0:
		showMessage('ПОКАЗАТЬ НЕЧЕГО', 'Не найдены элементы "video"')
		return False
	if lvideos > 99:
		page += 1
		i = xbmcgui.ListItem('Далее >>', iconImage=icon, thumbnailImage=icon)
		u  = sys.argv[0] + '?mode=OPEN_CHANNEL'
		u += '&url=%s'%urllib.quote_plus(url)
		u += '&genre=%s'%urllib.quote_plus(genre)
		u += '&page=%d'%page
		xbmcplugin.addDirectoryItem(h, u, i, True)

	for video in videos:
		#video_id         = video.getAttribute('id')
		#video_cnl_id     = video.getAttribute('cnl_id')
		video_name       = video.getAttribute('name').encode('utf-8')
		video_text       = video.getAttribute('text').encode('utf-8')
		#video_old        = video.getAttribute('old')
		#video_url3gp     = video.getAttribute('url3gp')
		video_urlmp4  = video.getAttribute('urlmp4')
		video_sizemp4 = video.getAttribute('sizemp4')
		if video_urlmp4 == '':
			video_urlmp4  = video.getAttribute('urlmp4low')
			video_sizemp4 = video.getAttribute('sizemp4low')
		#video_vw1        = video.getAttribute('vw1')
		#video_vw7        = video.getAttribute('vw7')
		#video_vote_all   = video.getAttribute('vote-all')
		#video_vote_plus  = video.getAttribute('vote-plus')
		#video_vote_minus = video.getAttribute('vote-minus')
		#video_geo_access = video.getAttribute('geo_access')
		#video_under      = video.getAttribute('under')
		try:
			hours, remainder = divmod(int(video.getAttribute('duration'))//1000, 3600)
			minutes, seconds = divmod(remainder, 60)
			duration = '%s:%s:%s' % (hours, minutes, seconds)
		except:
			duration = ''
		try:    size = int(video_sizemp4)
		except: size = 0
		try:    playcount = int(video.getAttribute('view'))
		except: playcount = 0

		i = xbmcgui.ListItem(video_name, iconImage = video.getAttribute('list'), thumbnailImage = video.getAttribute('img'))
		i.setInfo(type = 'video', infoLabels = {
			'title':       video_name,
			'studio':      video.getAttribute('cnl_name').encode('utf-8'),
			'size':        size,
			'genre':       genre,
			'duration':    duration,
			'tagline':     video.getAttribute('Tags').encode('utf-8'),
			'plot':        video_text.replace('<br />', '\n'),
			'playcount':   playcount,
			#'rating':      float(GetRegion(item_block, 'rating',     False, '0')),
			'date':        video.getAttribute('date'),
		})
		i.setProperty('fanart_image', video.getAttribute('old'))
		xbmcplugin.addDirectoryItem(h, video_urlmp4, i)

	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_UNSORTED)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_DATE)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_DURATION)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_GENRE)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_VIDEO_RATING)

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
	return param

params=get_params(sys.argv[2])

mode = None
ifac = None

try:
	mode = urllib.unquote_plus(params['mode'])
except:
	ROOT()

if mode == 'OPEN_RUBRICA':
	OPEN_RUBRICA(urllib.unquote_plus(params['rubID']))

if mode == 'OPEN_CHANNEL':
	OPEN_CHANNEL(urllib.unquote_plus(params['url']), int(urllib.unquote_plus(params['page'])), urllib.unquote_plus(params['genre']))

if mode == 'SEARCH':
	pass_keyboard = xbmc.Keyboard()
	pass_keyboard.setHeading('Что ищем?')
	pass_keyboard.doModal()
	if (pass_keyboard.isConfirmed()):
		SearchStr = pass_keyboard.getText()
		OPEN_CHANNEL(iSearch%SearchStr, 1, 'Поиск')

