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

import os, sys
import urllib, os
import xbmcplugin, xbmcgui, xbmcaddon, xbmc
import demjson
import kbutils

h = int(sys.argv[1])

icon     = xbmc.translatePath(os.path.join(os.path.join(os.getcwd().replace(';', '')), 'icon.png'))

img_base = os.path.join(os.getcwd().replace(';', ''), 'resources', 'icons')
ifilms   = xbmc.translatePath(os.path.join(img_base, 'films.png'))
ifriends = xbmc.translatePath(os.path.join(img_base, 'friends.png'))
icon0    = xbmc.translatePath(os.path.join(img_base, 'icon0.png'))
irecom   = xbmc.translatePath(os.path.join(img_base, 'recom.png'))
iseries  = xbmc.translatePath(os.path.join(img_base, 'series.png'))
rtorimg  = xbmc.translatePath(os.path.join(img_base, 'rtorrent.png'))

Thumbs_Down  = xbmc.translatePath(os.path.join(img_base, 'Thumbs_Down.png'))
Thumbs_Up    = xbmc.translatePath(os.path.join(img_base, 'Thumbs_Up.png'))
iOK          = xbmc.translatePath(os.path.join(img_base, 'OK.png'))
iDOWNLOADING = xbmc.translatePath(os.path.join(img_base, 'DOWNLOADING.png'))
iSTART       = xbmc.translatePath(os.path.join(img_base, 'START.png'))






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



# Главное меню. Установка переходов во все функции.
def showroot(params):

	limit = kbutils.LIST_LIMIT()

#	li = xbmcgui.ListItem('Список доступных жанров', iconImage=icon0, thumbnailImage=icon0)
#	xbmcplugin.addDirectoryItem(h, '%s?mode=showgenres'%sys.argv[0], li, isFolder = True)

#	li = xbmcgui.ListItem('Список доступных стран', iconImage=icon0, thumbnailImage=icon0)
#	xbmcplugin.addDirectoryItem(h, '%s?mode=showcountries'%sys.argv[0], li, isFolder = True)

#	li = xbmcgui.ListItem('Список известных языков', iconImage=icon0, thumbnailImage=icon0)
#	xbmcplugin.addDirectoryItem(h, '%s?mode=showlanguages'%sys.argv[0], li, isFolder = True)

#	li = xbmcgui.ListItem('Список поддерживаемых трекеров', iconImage=icon0, thumbnailImage=icon0)
#	xbmcplugin.addDirectoryItem(h, '%s?mode=showtrackers'%sys.argv[0], li, isFolder = True)

	li = xbmcgui.ListItem('Фильмы : Обзор', iconImage=ifilms, thumbnailImage=ifilms)
	xbmcplugin.addDirectoryItem(h, '%s?mode=filmsbrowse&fields_mask=63&limit=%d&offset=0&type=movie&href=%s'%(sys.argv[0], limit, urllib.quote_plus('/films/browse')), li, isFolder = True, totalItems = limit)

	li = xbmcgui.ListItem('Фильмы : Поиск', iconImage=ifilms, thumbnailImage=ifilms)
	xbmcplugin.addDirectoryItem(h, '%s?mode=filmssearch&fields_mask=63&limit=%d&offset=0&type=movie&href=%s'%(sys.argv[0], limit, urllib.quote_plus('/films/search')), li, isFolder = True, totalItems = limit)

	li = xbmcgui.ListItem('Сериалы : Обзор', iconImage=iseries, thumbnailImage=iseries)
	xbmcplugin.addDirectoryItem(h, '%s?mode=filmsbrowse&fields_mask=63&limit=%d&offset=0&type=series&href=%s'%(sys.argv[0], limit, urllib.quote_plus('/films/browse')), li, isFolder = True, totalItems = limit)

	li = xbmcgui.ListItem('Сериалы : Поиск', iconImage=iseries, thumbnailImage=iseries)
	xbmcplugin.addDirectoryItem(h, '%s?mode=filmssearch&fields_mask=63&limit=%d&offset=0&type=series&href=%s'%(sys.argv[0], limit, urllib.quote_plus('/films/search')), li, isFolder = True, totalItems = limit)

	li = xbmcgui.ListItem('Ваши загрузки', iconImage = rtorimg, thumbnailImage = rtorimg)
	xbmcplugin.addDirectoryItem(h, '%s?mode=rtcshowdl'%(sys.argv[0]), li, True)

	xbmcplugin.endOfDirectory(h)





'''
def openuserprofile(params):

	print '=== def openuserprofile(%s): ===' % params

	try:    action = info['action']
	except: action = None

	if action == None:
		# GET /my/series/seen 						Список сериалов, которые пользователь когда-либо смотрел
		li = xbmcgui.ListItem('Список просмотренных сериалов', iconImage=icon, thumbnailImage=icon)
		xbmcplugin.addDirectoryItem(h, '%s?mode=showgenres'%sys.argv[0], li, True)

		# GET /my/subscriptions 					Возвращает список подписок на фильмы/сериалы
		li = xbmcgui.ListItem('Ваши подписки (фильмы и сериалы)', iconImage=icon, thumbnailImage=icon)
		xbmcplugin.addDirectoryItem(h, '%s?mode=showgenres'%sys.argv[0], li, True)

		# GET /my/subscriptions/films 				Возвращает список подписок на фильмы
		li = xbmcgui.ListItem('Ваши подписки на фильмы', iconImage=icon, thumbnailImage=icon)
		xbmcplugin.addDirectoryItem(h, '%s?mode=showgenres'%sys.argv[0], li, True)

		# GET /my/subscriptions/films/unreaded 		Возвращает список подписок на фильмы, которые пользователь еще не отметил просмотренными
		li = xbmcgui.ListItem('Ваши подписки на фильмы (не просмотренные)', iconImage=icon, thumbnailImage=icon)
		xbmcplugin.addDirectoryItem(h, '%s?mode=showgenres'%sys.argv[0], li, True)

		# GET /my/subscriptions/series 				Возвращает список подписок на сериалы
		li = xbmcgui.ListItem('Ваши подписки на сериалы', iconImage=icon, thumbnailImage=icon)
		xbmcplugin.addDirectoryItem(h, '%s?mode=showgenres'%sys.argv[0], li, True)

		# GET /my/trackers 							Список отслеживаемых пользователем трекеров
		li = xbmcgui.ListItem('Список отслеживаемых вами трекеров', iconImage=icon, thumbnailImage=icon)
		xbmcplugin.addDirectoryItem(h, '%s?mode=showgenres'%sys.argv[0], li, True)

		xbmcplugin.endOfDirectory(h)
'''


def rtcshowdl(params):




	print '=== def rtcshowdl(%s): ===' % params

	rtc = kbutils.get_rtc()
	if rtc == None: return False

	try:    action = params['action']
	except: action = None

	if action == None:

		dlds = []
		dlds = rtc.d.multicall('main', "d.get_name=", "d.get_hash=", "d.get_completed_chunks=", "d.get_size_chunks=", "d.get_size_files=", \
			"d.get_directory=", "d.is_active=", "d.get_complete=", "d.get_priority=", "d.is_multi_file=", "d.get_size_bytes=", \
			"d.get_custom=", "d.get_custom1=", "d.get_custom2=", "d.get_custom3=", "d.get_custom4=", "d.get_custom5=", "d.get_custom=kbmeta" )

		dlds_len = len(dlds)

		for dld in dlds:
			dld_name = dld[0]
			dld_hash = dld[1]
			dld_completed_chunks = dld[2]
			dld_size_chunks = dld[3]
			dld_percent_complete = dld_completed_chunks*100/dld_size_chunks
			dld_size_files = dld[4]
			dld_directory = dld[5]
			dld_is_active = dld[6]
			dld_complete = dld[7]
			dld_priority = dld[8]
			dld_is_multi_file = dld[9]
			dld_size_bytes = int(dld[10])
			dld_custom = dld[11]
			dld_custom1 = dld[12] # kinobaza
			dld_custom2 = dld[13] # Comment (metadata)
			dld_custom3 = dld[14]
			dld_custom4 = dld[15]
			dld_custom5 = dld[16]
			dld_kbmeta = dld[17]

			if dld_custom1 == 'kinobaza':
				#print 'dld_custom  [%s]' % dld_custom
				#print 'dld_custom1 [%s]' % dld_custom1
				#print 'dld_custom2 [%s]' % dld_custom2
				#print 'dld_custom3 [%s]' % dld_custom3
				#print 'dld_custom4 [%s]' % dld_custom4
				#print 'dld_custom5 [%s]' % dld_custom5

				#dld_kbmeta = dld_kbmeta.replace('custom_value="','').replace('"','')

				#print 'kbmeta: %s' % dld_kbmeta

				info = get_params(dld_kbmeta)
				for curi in info: info[curi] = urllib.unquote_plus(info[curi])

				def key_to_int(arr, keyname):
					try: arr[keyname] = int(arr[keyname])
					except:
						try: del info[keyname]
						except: pass
				key_to_int(info, 'count')
				key_to_int(info, 'year')
				key_to_int(info, 'episode')
				key_to_int(info, 'season')
				key_to_int(info, 'top250')
				key_to_int(info, 'tracknumber')
				key_to_int(info, 'playcount')
				key_to_int(info, 'overlay')
				try:
					info['rating'] = float(info['rating'])
				except:
					try: del info['rating']
					except: pass

				info['size'] = dld_size_bytes
				info['title'] = '%s (%s%%)'%(info['title'],dld_percent_complete)

				if dld_is_active == 1: cm_action = 'СТОП', 'xbmc.runPlugin(%s?mode=rtcshowdl&action=dlstop&hash=%s)'  % (sys.argv[0], dld_hash)
				else:                  cm_action = 'СТАРТ','xbmc.runPlugin(%s?mode=rtcshowdl&action=dlstart&hash=%s)' % (sys.argv[0], dld_hash)

				fdc = 'xbmc.runPlugin(%s?mode=rtcshowdl&action=setprio&hash=%s&prio=%s)'
				cm = [cm_action, ('УДАЛИТЬ', 'xbmc.runPlugin(%s?mode=rtcshowdl&action=erase&hash=%s)'%(sys.argv[0],dld_hash)),\
					('Приоритет: высокий',     fdc % (sys.argv[0], dld_hash, 3)),\
					('Приоритет: нормальный',  fdc % (sys.argv[0], dld_hash, 2)),\
					('Приоритет: низкий',      fdc % (sys.argv[0], dld_hash, 1)),\
					('Приоритет: не загружать',fdc % (sys.argv[0], dld_hash, 0)) ]

				li = xbmcgui.ListItem(label = info['title'], label2 = dld_name, iconImage=info['iconImage'], thumbnailImage=info['thumbnailImage'])
				li.addContextMenuItems(items = cm, replaceItems = True)
				li.setInfo(type = 'video', infoLabels = info)

				if dld_size_files > 1:
					uri = '%s?mode=rtcshowdl&action=showfiles&hash=%s&numfiles=%s'%(sys.argv[0], dld_hash, dld_size_files)
					if not xbmcplugin.addDirectoryItem(h, uri, li, isFolder = True, totalItems = dlds_len): break
				else:
					#li.setProperty('IsPlayable', 'true')
					uri = '%s?mode=rtcshowdl&action=playfile&film_id=%s'%(sys.argv[0], info['film_id'])
					if not xbmcplugin.addDirectoryItem(h, uri, li,isFolder = True, totalItems=dlds_len): break

		xbmcplugin.addSortMethod(h, sortMethod = xbmcplugin.SORT_METHOD_TITLE )
		xbmcplugin.addSortMethod(h, sortMethod = xbmcplugin.SORT_METHOD_SIZE )
		xbmcplugin.endOfDirectory(h, cacheToDisc = False)

	elif action == 'setprio':
		rtc.d.set_priority('%s' % params['hash'], int(params['prio']))
		xbmc.executebuiltin('Container.Refresh')
	elif action == 'erase':
		#rtc.d.set_priority('%s' % params['hash'], int(params['prio']))

		rtc.d.erase(params['hash'])
		kbutils.showMessage('Удален торрент', 'Сами файлы остались на месте', 5000)
		xbmc.executebuiltin('Container.Refresh')

	elif action == 'showfiles':




		#print 'Воспроизводим %s' % dhash
		pfile = os.path.join(rtc.d.get_directory(params['hash']),rtc.d.get_name(params['hash']))
		#print 'Файл %s' % pfile
		#i = xbmcgui.ListItem(path = pfile)
		#xbmcplugin.setResolvedUrl(h, True, i)
		#return True



		files = []
		files = rtc.f.multicall(params['hash'],1,"f.get_path=","f.get_completed_chunks=","f.get_size_chunks=","f.get_priority=","f.get_size_bytes=")
		i=0
		for f in files:
			f_name = f[0]
			f_completed_chunks = int(f[1])
			f_size_chunks = int(f[2])
			f_size_bytes = int(f[4])
			f_percent_complete = f_completed_chunks*100/f_size_chunks
			f_priority = f[3]
			if f_percent_complete==100:
				f_complete = 1
			else:
				f_complete = 0
			#tbn=getIcon(0,1,f_complete,f_priority)
			if f_percent_complete<100:
				li_name = f_name+' ('+str(f_percent_complete)+'%)'
			else:
				li_name = f_name
			li = xbmcgui.ListItem( \
				label=li_name, \
				iconImage=icon, thumbnailImage=icon)
			#cm = [(g.__lang__(30120),"xbmc.runPlugin(%s?mode=action&method=f.set_priority&arg1=%s&arg2=%s&arg3=2)" % ( sys.argv[0], hash,i)), \
			#	(g.__lang__(30121),"xbmc.runPlugin(%s?mode=action&method=f.set_priority&arg1=%s&arg2=%s&arg3=1)" % ( sys.argv[0], hash,i)), \
			#	(g.__lang__(30124),"xbmc.runPlugin(%s?mode=action&method=f.set_priority&arg1=%s&arg2=%s&arg3=0)" % ( sys.argv[0], hash,i))]
			#li.addContextMenuItems(items=cm,replaceItems=True)
			li.setInfo('video',{'title':li_name,'size':f_size_bytes})

			#uri = '%s?mode=rtcshowdl&action=playfile&hash=%s&file_id=%s'%(sys.argv[0], params['hash'], i)

			uri = os.path.join(pfile, rtc.f.get_frozen_path(params['hash'], i))
			if not xbmcplugin.addDirectoryItem(h,uri,li,isFolder = True, totalItems=len(files)): break
			i=i+1
		xbmcplugin.addSortMethod(h, sortMethod=xbmcplugin.SORT_METHOD_TITLE )
		xbmcplugin.addSortMethod(h, sortMethod=xbmcplugin.SORT_METHOD_SIZE )
		xbmcplugin.endOfDirectory(h, cacheToDisc=False)



	elif action == 'playfile':
		print 'playfile....'
		openfilm({'film_id': params['film_id']})





def filmssearch(params):
	KB = xbmc.Keyboard()
	KB.setHeading('Что ищем?')
	KB.doModal()
	if (KB.isConfirmed()):
		params['query'] = urllib.quote_plus(KB.getText())
		params['mode'] = 'filmsbrowse'
		filmsbrowse(params)
	else: return False



def showgenres(params):
	http = kbutils.KBREQUEST('/genres/')
	djson = demjson.decode(http)
	for cur in djson:
		genre_id   = cur['id']
		genre_name = cur['name'].encode('utf-8')
		li = xbmcgui.ListItem('Жанр "%s"'%genre_name, iconImage=icon, thumbnailImage=icon)
		xbmcplugin.addDirectoryItem(h, '%s?mode=opengenre&genre_id=%s&genre_name=%s'%(sys.argv[0],genre_id,urllib.quote_plus(genre_name)), li, True)
	xbmcplugin.endOfDirectory(h)


def showcountries(params):
	http = kbutils.KBREQUEST('/countries/')
	djson = demjson.decode(http)
	for cur in djson:
		country_id   = cur['id']
		country_name = cur['name'].encode('utf-8')
		country_iso  = cur['iso']
		li = xbmcgui.ListItem('Страна "%s"'%country_name, iconImage=icon, thumbnailImage=icon)
		xbmcplugin.addDirectoryItem(h, '%s?mode=opencountry&country_id=%s&country_name=%s&country_iso=%s'%(sys.argv[0],country_id,urllib.quote_plus(country_name),country_iso), li, True)
	xbmcplugin.endOfDirectory(h)


def showlanguages(params):
	http = kbutils.KBREQUEST('/languages')
	djson = demjson.decode(http)
	for cur in djson:
		lang_id   = cur['id']
		lang_name = cur['name'].encode('utf-8')
		li = xbmcgui.ListItem('Язык "%s"'%lang_name, iconImage=icon, thumbnailImage=icon)
		xbmcplugin.addDirectoryItem(h, '%s?mode=openlanguage&lang_id=%s&lang_name=%s'%(sys.argv[0],lang_id,urllib.quote_plus(lang_name)), li, True)
	xbmcplugin.endOfDirectory(h)


def showtrackers(params):
	http = kbutils.KBREQUEST('/trackers')
	djson = demjson.decode(http)
	for cur in djson:
		tracker_id   = cur['id']
		tracker_name = cur['url'].encode('utf-8')
		print 'Tracker ID = %s, URL = %s'%(tracker_id,tracker_name)
		li = xbmcgui.ListItem('Трекер %s'%tracker_name, iconImage=icon, thumbnailImage=icon)
		xbmcplugin.addDirectoryItem(h, '%s?mode=openlantracker&tracker_id=%s&tracker_name=%s'%(sys.argv[0],tracker_id,urllib.quote_plus(tracker_name)), li, True)
	xbmcplugin.endOfDirectory(h)


# -------------------------------------------------------------------------------------- #


def filmsbrowse(params):
	print '=== def filmsbrowse(%s): ===' % params


	try:
		href = urllib.unquote_plus(params['href'])
		params['href'] = href
	except: href = ''
	try: params['query'] = urllib.unquote_plus(params['query'])
	except: pass

	GL = params.copy()
	del GL['mode']
	del GL['href']

	#url =
	http = kbutils.KBREQUEST('%s?%s'%(href,urllib.urlencode(GL)))

	djson = demjson.decode(http)
	#print djson



	# Если подключен rTorrent - генерируем список подкаталогов, для проверки загрузки
	rtc = kbutils.get_rtc()
	if rtc != None:
		base_dl_path = rtc.get_directory()
		dpa = []
		if (kbutils.rtc_select == 'true'):
			for ddir in os.listdir(base_dl_path):
				dpa.append(os.path.join(base_dl_path, ddir))
		else:
			dpa.append(os.path.join(base_dl_path))


	for cur in djson:

		info = kbutils.getmetadata(cur, cur['id'])

		if rtc != None:
			for chkdir in dpa:
				if os.path.exists(os.path.join(chkdir, str(cur['id']))):
					info['title'] = '[DL] %s'%info['title']
					break

		li = xbmcgui.ListItem(label = info['title'], iconImage = info['iconImage'], thumbnailImage = info['thumbnailImage'])
		li.setInfo(type = 'video', infoLabels = info)

		if cur['type'] == 'movie':
			#li.setProperty('IsPlayable', 'true')
			uri = '%s?mode=openfilm&film_id=%s'%(sys.argv[0], cur['id'])
			if not xbmcplugin.addDirectoryItem(h, uri, li, isFolder=True): break
		elif cur['type'] == 'series':
			uri = '%s?mode=openseasons&series_id=%s'%(sys.argv[0], cur['id'])
			if not xbmcplugin.addDirectoryItem(h, uri, li, isFolder=True): break
		else:
			kbutils.showMessage('Ой, "%s"' % film_type, 'Не могу добавить этот тип фильма')


	if len(djson) == int(params['limit']):
		li = xbmcgui.ListItem('Далее >', iconImage=icon, thumbnailImage=icon)
		params['offset'] = str(int(params['offset'])+int(params['limit']))
		uri  = '%s?%s'%(sys.argv[0],urllib.urlencode(params))
		xbmcplugin.addDirectoryItem(h, uri, li, isFolder = True, totalItems = kbutils.LIST_LIMIT())



	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_UNSORTED)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_ALBUM)
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

################################################################
# Эта функция должна открыть сериал по series_id
# и создать список сезонов
################################################################
def openseasons(params):
	print '=== def openseasons(%s): ===' % params
	try:
		series_id = params['series_id']
	except:
		print 'ERROR: Не указан ключевой параметр series_id'
		return False
	# Получение метаданных
	meta_http = kbutils.KBREQUEST('/films/%s?fields_mask=63' % series_id)
	if meta_http != None:
		meta_json = demjson.decode(meta_http)
		# Парсинг метаданных
		meta_info = kbutils.getmetadata(meta_json, series_id)
	else:
		meta_info = None
	http = kbutils.KBREQUEST('/films/%s/seasons' % series_id)
	if http == None:
		return False
	djson = demjson.decode(http)
	series_id = djson['series_id'] # int
	seasons   = djson['seasons']   # array
	if len(seasons) > 0:
		series_img = kbutils.POSTER(series_id)
		for season in seasons:
			info = {}
			if meta_info != None: info = meta_info.copy()
			season_num     = season['num']            # int 1
			episodes_count = season['episodes_count'] # int 29
			start_date     = season['start_date']     #.encode('utf-8')     # str 2003-02-01
			end_date       = season['end_date']       #.encode('utf-8')       # str 2004-03-16
			if start_date == None: start_date = ''
			else: start_date = start_date.encode('utf-8')
			if end_date == None: end_date = ''
			else: end_date = end_date.encode('utf-8')
			if (start_date == '') and (end_date == ''): date_block = ''
			else: date_block = ' [%s : %s]' % (start_date, end_date)
			info['title']     = '%s : Сезон %d%s' % (info['title'], season_num, date_block)
			info['premiered'] = start_date
			info['season']    = int(season_num)
			li = xbmcgui.ListItem(info['title'], iconImage = series_img, thumbnailImage = series_img)
			li.setInfo(type = 'video', infoLabels = info)
			uri = '%s?mode=openepisodes&series_id=%s&season_num=%s' % (sys.argv[0], series_id, season_num)
			xbmcplugin.addDirectoryItem(h, uri, li, isFolder = True, totalItems = episodes_count)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_DATE)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.endOfDirectory(h)



################################################################
# Получение эпизодов для указанного сезона и сериалы
# Должен быть указан season_num и series_id
################################################################
def openepisodes(params):
	print '=== def openepisodes(%s): ===' % params
	try:
		series_id  = params['series_id']
		season_num = params['season_num']
	except:
		print 'ERROR: Не указан ключевой параметр series_id или season_num'
		return False
	# Получение метаданных
	meta_http = kbutils.KBREQUEST('/films/%s?fields_mask=63' % series_id)
	if meta_http != None:
		meta_json = demjson.decode(meta_http)
		# Парсинг метаданных
		meta_info = kbutils.getmetadata(meta_json, series_id)
	else:
		meta_info = None
	http = kbutils.KBREQUEST('/films/%s/seasons/%s/episodes' % (series_id, season_num))
	if http == None:
		return False
	djson = demjson.decode(http)
	series_id      = djson['series_id']   # int 1
	season_num     = djson['season_num'] # int 1
	episodes       = djson['episodes']   # array
	if len(episodes) > 0:
		series_img = kbutils.POSTER(series_id)
		for episode in episodes:
			info = {}
			if meta_info != None: info = meta_info.copy()
			episode_num  = episode['num']          # int 1
			episode_name = episode['name'].encode('utf-8')         # str Role Play
			release_date = episode['release_date'] #3.encode('utf-8') # str 2003-02-01
			info['title'] = '%d. %s'%(episode_num, episode_name)
			if release_date != None:
				info['premiered'] = release_date
				info['premiered'] = release_date
			info['episode'] = int(episode_num)
			info['season']  = int(season_num)
			li = xbmcgui.ListItem(info['title'], iconImage = series_img, thumbnailImage = series_img)
			li.setInfo(type = 'video', infoLabels = info)
			uri = '%s?mode=openfilm&series_id=%d&season_num=%d&episode_num=%d'%(sys.argv[0],series_id,season_num,episode_num)
			xbmcplugin.addDirectoryItem(h, uri, li, isFolder = True)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_DATE)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.endOfDirectory(h)







################################################################
# Эта функция должна проверить наличие загрузок в rTorrent
# предложить список к воспроизведению, если есть загруженные
# файлы, либо предложить поставить на загрузку торрент
################################################################
def openfilm(params):
	print '=== def openfilm(%s): ===' % params

	film_type = 0 # 1: movie, 2: series

	try:
		film_id     = params['series_id']   #'series_id': '357767'
		season_num  = params['season_num']  #'season_num': '1'
		episode_num = params['episode_num'] #'episode_num': '1'
		torget  = '/films/%s/seasons/%s/episodes/%s/torrents' % (film_id, season_num, episode_num)
		dlpath  = os.path.join(film_id, season_num, episode_num)
		film_type = 2
	except: pass

	if film_type == 0:
		try:
			film_id = params['film_id']   #'series_id': '357767'
			torget = '/films/%s/torrents?all_trackers=false' % film_id
			dlpath = os.path.join(film_id)
			film_type = 1
		except: pass

	print 'openfilm -> torget      = [%s]' % torget

	if film_type == 0:
		print 'ERROR: Тип раздачи не был установлен (film_type == 0)'
		return False

	http = kbutils.KBREQUEST(torget)
	if http == None: return False

	djson = demjson.decode(http)

	film_id  = djson['film_id']
	filters  = djson['filters']
	torrents = djson['torrents']

	hash_arrs = []
	hash_data = {}

	rtc = kbutils.get_rtc()

	for torrent in torrents:
		approved = torrent['is_approved']
		tracker = torrent['tracker_url'].encode('utf-8').replace('http:','').replace('/','')
		size = int(torrent['size'])
		try:
			filetype = torrent['filetype'].encode('utf-8')
		except:
			filetype = '?'

		quality = kbutils.replace_quality(torrent['quality'])
		quality = quality.replace(',','')
		seeders = int(torrent['seeders'])
		leechers = int(torrent['leechers'])
		THASH = torrent['hash'].encode('utf-8')
		hash_arrs.append(THASH)
		try: percent = (int(rtc.f.get_completed_chunks(THASH, 0))*100)/int(rtc.f.get_size_chunks(THASH, 0))
		except: percent = 0
		subdata = {'approved':approved,'tracker':tracker,'size':size,'filetype':filetype,
		'quality':quality,'seeders':seeders,'leechers':leechers,'percent':percent,'hash':THASH}
		hash_data[THASH] = subdata


	uhash_arrs = set(hash_arrs)

	# TODO Add METADATA

	def set_approved(let,li):
		if let['approved']: li.setProperty('fanart_image', Thumbs_Up)
		else: li.setProperty('fanart_image', Thumbs_Down)

	# Поиск полностью загруженных раздач
	for uhash in uhash_arrs:
		ninfo = hash_data[uhash]
		if ninfo['percent'] == 100:
			it = '%s Тип:%s %s' % (ninfo['tracker'], ninfo['filetype'], ninfo['quality'])
			li = xbmcgui.ListItem(it, iconImage = iOK, thumbnailImage = iOK)
			li.setInfo('video', {'title':it, 'size':ninfo['size']})
			set_approved(ninfo,li)
			if rtc.d.get_size_files(uhash) > 1:
				xbmcplugin.addDirectoryItem(h, rtc.d.get_directory(uhash), li, isFolder = True)
			else:
				xbmcplugin.addDirectoryItem(h, os.path.join(rtc.d.get_directory(uhash),rtc.d.get_name(uhash)), li, isFolder = False)


	# Поиск загружаемых раздач
	for uhash in uhash_arrs:
		ninfo = hash_data[uhash]
		# TODO and paused...
		try:    is_active = int(rtc.d.is_active(ninfo['hash']))
		except: is_active = 0
		if (ninfo['percent'] < 100) and (is_active == 1):
			it = '%d%% S=%s, L=%s %s(%s), от %s' % (ninfo['percent'],ninfo['seeders'],ninfo['leechers'],ninfo['quality'],ninfo['filetype'],ninfo['tracker'])
			li = xbmcgui.ListItem(it, iconImage = iDOWNLOADING, thumbnailImage = iDOWNLOADING)
			li.setInfo('video', {'title':it, 'size':ninfo['size']})
			set_approved(ninfo,li)
			# TODO Сделать доп. пункты.
			ppath = os.path.join(rtc.d.get_directory(uhash),rtc.d.get_name(uhash))
			if rtc.d.get_size_files(uhash) > 1:
				xbmcplugin.addDirectoryItem(h, rtc.d.get_directory(uhash), li, isFolder = True)
			else:
				xbmcplugin.addDirectoryItem(h, os.path.join(rtc.d.get_directory(uhash),rtc.d.get_name(uhash)), li, isFolder = False)


	for uhash in uhash_arrs:
		ninfo = hash_data[uhash]
		if ninfo['percent'] == 0:
			it = 'S=%s, L=%s %s(%s), от %s' % (ninfo['seeders'],ninfo['leechers'],ninfo['quality'],ninfo['filetype'],ninfo['tracker'])
			li = xbmcgui.ListItem(it, iconImage = iSTART, thumbnailImage = iSTART)
			li.setInfo('video', {'title':it, 'size':ninfo['size']})
			set_approved(ninfo,li)
			uri = '%s?mode=loadtorrent&hash=%s&film_id=%s&dlpath=%s' % (sys.argv[0], uhash, film_id, urllib.quote_plus(dlpath))
			xbmcplugin.addDirectoryItem(h, uri, li)

	xbmcplugin.addSortMethod(h, sortMethod = xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.addSortMethod(h, sortMethod = xbmcplugin.SORT_METHOD_SIZE)
	xbmcplugin.endOfDirectory(h)


'''


		fdc = 'xbmc.runPlugin(%s?mode=rtcshowdl&action=setprio&hash=%s&prio=%s)'
		cm = [cm_action, ('УДАЛИТЬ', 'xbmc.runPlugin(%s?mode=rtcshowdl&action=erase&hash=%s)'%(sys.argv[0],dld_hash)),\
			('Приоритет: высокий',     fdc % (sys.argv[0], dld_hash, 3)),\
			('Приоритет: нормальный',  fdc % (sys.argv[0], dld_hash, 2)),\
			('Приоритет: низкий',      fdc % (sys.argv[0], dld_hash, 1)),\
			('Приоритет: не загружать',fdc % (sys.argv[0], dld_hash, 0)) ]

		li = xbmcgui.ListItem(label = info['title'], label2 = dld_name, iconImage=info['iconImage'], thumbnailImage=info['thumbnailImage'])
		li.addContextMenuItems(items = cm, replaceItems = True)
		li.setInfo(type = 'video', infoLabels = info)



	if dpercent > 0:

		if int(rtc.d.is_active(dhash)) == 1:
			ans0 = ['Остановить загрузку','Поставить на паузу','Удалить', 'Попытаться воспроизвести']
			s = xbmcgui.Dialog().select('Раздача загружается. Готово: %d%%'%dpercent, ans0)
			if s < 0:
				print 'Не выбрано, выход...'
				return True
			if s == 0:
				rtc.d.close(dhash)
				return True
			elif s == 1:
				rtc.d.pause(dhash)
				return True
			elif s == 2:
				rtc.d.erase(dhash)
				return True
			elif s == 3:
				play
				print 'Воспроизводим %s' % dhash
				pfile = os.path.join(rtc.d.get_directory(dhash),rtc.d.get_name(dhash))
				#print 'Файл %s' % pfile
				i = xbmcgui.ListItem(path = pfile)
				xbmcplugin.setResolvedUrl(h, True, i)
				return True
		else:
			ans0 = ['Продолжить','Удалить','Попытаться воспроизвести']
			s = xbmcgui.Dialog().select('Раздача на паузе. Готово: %d%%'%dpercent, ans0)
			if s < 0:
				print 'Не выбрано, выход...'
				return True
			if s == 0:
				rtc.d.start(dhash)
				return True
			elif s == 1:
				rtc.d.erase(dhash)
				return True
			elif s == 2:
				print 'Воспроизводим %s' % dhash
				pfile = os.path.join(rtc.d.get_directory(dhash),rtc.d.get_name(dhash))
				#print 'Файл %s' % pfile
				i = xbmcgui.ListItem(path = pfile)
				xbmcplugin.setResolvedUrl(h, True, i)
				return True
'''



def loadtorrent(params):

	print '=== def loadtorrent(%s): ===' % params
	try:
		dhash   = params['hash']
		film_id = params['film_id']
		dlpath  = urllib.unquote_plus(params['dlpath'])
	except:
		print 'ERROR: Не указан ключевой параметр hash, dlpath или film_id'
		return False

	rtc = kbutils.get_rtc()

	rtpath = rtc.get_directory()
	print 'rTorrent base dir (rtpath) = %s' % rtpath
	dpath = rtpath

	if kbutils.rtc_select == 'true':
		print 'Указан выбор каталога загрузки...'
		dpa = []
		for ddir in os.listdir(rtpath): dpa.append(ddir)

		s = xbmcgui.Dialog().select('Куда качать?', dpa)
		if s < 0:
			print 'Не выбрано, выход...'
			return True
		else:
			dpath = os.path.join(rtpath, dpa[s])

	dpath = os.path.join(dpath, dlpath)

	print 'Download path [%s]' % dpath

	if not os.path.exists(dpath):
		os.makedirs(dpath)
		print 'Path %s created...' % dpath
	else:
		print 'Path %s exists...' % dpath

	url_gt = '/torrents/%s/direct-link' % dhash
	print 'url_gt GET: %s' % url_gt
	http3 = kbutils.KBREQUEST(url_gt)
	if http3 == None:
		return False

	djson2 = demjson.decode(http3)


	#print djson2
	tf_url  = djson2['url']
	print 'Direct Link = %s' % tf_url

	meta_http = kbutils.KBREQUEST('/films/%s?fields_mask=63' % film_id)
	if meta_http != None:
		meta_json = demjson.decode(meta_http)
		meta_info = kbutils.getmetadata(meta_json, film_id)
	else:
		meta_info = None

	try:
		if len(meta_info['cast']) > 0:
			casts = ''
			for cucast in meta_info['cast']:
				casts += ',%s' % urllib.quote_plus(cucast)
			if casts != '':
				casts = casts[1:]
				meta_info['cast'] = casts
	except: pass

	custom2 = '&film_id=%s' % film_id
	if meta_info != None:
		for cinfo in meta_info:
			custom2 += '&%s=%s' % (cinfo, urllib.quote_plus(str(meta_info[cinfo])))
	custom2 = custom2[1:]

	# 'd.set_custom2="%s"'%custom2
	rtc.load_start(tf_url, 'd.set_directory="%s"'%dpath, 'd.set_custom1="kinobaza"', 'd.set_custom=kbmeta,%s'%custom2)
	#return True






##########################################
# Системная часть аддона
# Дальше нет ничего интересного
##########################################
def addon_main():

	params = get_params(sys.argv[2])

	mode   = None
	func   = None

	try:
		mode = urllib.unquote_plus(params['mode'])
	except:
		showroot(params)

	if (mode != None):
		try:
			func = globals()[mode]
		except:
			pass
		if func: func(params)
