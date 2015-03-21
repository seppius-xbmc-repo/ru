#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2011 Muzunga.TV, http://muzunga.tv/
# Writer (c) 2011, Kostynoy S.A., E-mail: seppius2@gmail.com

import sys, xbmc, xbmcgui, xbmcplugin, xbmcaddon
import os, urllib, urllib2, datetime
import xml.dom.minidom

__addon__ = xbmcaddon.Addon(id = 'plugin.video.muzunga.tv')

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
sicon  = xbmc.translatePath(os.path.join(addon_path, 'search.png'))

h = int(sys.argv[1])

private_key      = __addon__.getSetting('private_key')
private_login    = __addon__.getSetting('username')
private_password = __addon__.getSetting('password')

try:
	view_limit = [10,20,30,40,50][int(__addon__.getSetting('limit'))]
except:
	view_limit = 30
	__addon__.setSetting('limit', 2)

def showMessage(heading, message, times = 3000, pics = icon):
	try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading.encode('utf-8'), message.encode('utf-8'), times, pics))
	except Exception, e:
		try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, pics))
		except Exception, e:
			print '[%s]: showMessage: exec failed [%s]' % (addon_id, e)

def GET(targeturl):
	#print '[%s]: GET [%s]' % (addon_id, targeturl)
	try:
		req = urllib2.Request(targeturl)
		req.add_header(     'User-Agent', '%s/%s %s/%s/%s' % (addon_type, addon_id, addon_author, addon_version, urllib.quote_plus(addon_name)))
		f = urllib2.urlopen(req)
		CE = f.headers.get('content-encoding')
		if CE:
			if 'gzip' in CE:
				import io, gzip
				bindata = io.BytesIO(f.read())
				gzipf = gzip.GzipFile(fileobj = bindata, mode='rb')
				a = gzipf.read()
			else: a = f.read()
		else: a = f.read()
		f.close()
		#print a
		return a
	except Exception, e:
		print '[%s]: GET EXCEPT [%s]' % (addon_id, e)
		showMessage('HTTP ERROR', href, 5000)

def parse_meta(document):
	mdata = {'title': document.getElementsByTagName('name')[0].firstChild.data}
	try:
		year = int(document.getElementsByTagName('year')[0].firstChild.data)
		mdata['year'] = year
	except: year = None
	try:
		try:
			duration = int(document.getElementsByTagName('episode_duration')[0].firstChild.data)
		except:
			duration = int(document.getElementsByTagName('duration')[0].firstChild.data)
		mdata['duration'] = '%d:%d:00' % (int(duration / 60), int(duration % 60))
	except: pass
	gg = ''
	for dg in document.getElementsByTagName('category'):
		gg += u', %s' % dg.getElementsByTagName('name')[0].firstChild.data #.encode('utf-8','replace')
	if len(gg) > 2: gg = gg[2:]
	try: video_type = int(document.getElementsByTagName('video_type')[0].firstChild.data)
	except: video_type = 0
	if video_type == 1:   gg2 = u'Фильм, '
	elif video_type == 2: gg2 = u'Cериал, '
	elif video_type == 3: gg2 = u'Развлечение, '
	elif video_type == 4: gg2 = u'Мультфильмы, '
	else: gg2 = ''
	mdata['genre'] = gg2 + gg
	try:
		production = document.getElementsByTagName('production')[0].firstChild.data #.encode('utf-8','replace')
		mdata['studio'] = production
	except: production = None
	try:
		mdata['director'] = document.getElementsByTagName('director')[0].firstChild.data
	except: pass
	try:
		mdata['writer'] = document.getElementsByTagName('screenwriter')[0].firstChild.data
	except: pass
	try:
		mdata['plot'] = document.getElementsByTagName('description')[0].firstChild.data
	except: pass
	try:
		mdata['cast'] = document.getElementsByTagName('actor')[0].firstChild.data.split(', ')
	except: pass
	try:
		mdata['rating'] = float(document.getElementsByTagName('rating_kinopoisk')[0].firstChild.data)
	except: pass
	try:
		added = int(document.getElementsByTagName('added')[0].firstChild.data)
		pdb = datetime.datetime.fromtimestamp(added)
		mdata['date'] = str(pdb.strftime('%d.%m.%Y'))
	except: pass
	try:
		if int(document.getElementsByTagName('view_completed')[0].firstChild.data) == 1:
			mdata['overlay'] = 7 # ICON_OVERLAY_WATCHED
	except: pass

	return mdata




#========================================================#
#					ROOT
#========================================================#
def showroot(params): # IMPLEMENTED
	uparam = {'device_type':'xbmc'}
	if len(private_key): uparam['private_key'] = private_key
	if len(private_login): uparam['login'] = private_login
	if len(private_password): uparam['password'] = private_password
	http = GET('http://muzunga.tv/stb/xml/key_status.php?%s' % urllib.urlencode(uparam))
	if not http: return False
	document = xml.dom.minidom.parseString(http)
	user_found = int(document.getElementsByTagName('user_found')[0].firstChild.data)
	if user_found == 0:
		showMessage('Ошибка авторизации на сайте Muzunga.TV', 'Проверьте правильность логина и пароля', 10000)
		__addon__.openSettings()
		return False
	try:
		new_key = document.getElementsByTagName('new_key')[0].firstChild.data
		if len(new_key):
			__addon__.setSetting('private_key', new_key)
			showMessage(u'Ключ: %s' % new_key, 'Пожалуйста привяжите его к вашему логину', 60000)
	except: pass
	#-----------------------------------------------------#
	http = GET('http://muzunga.tv/stb/xml/category.php')
	if not http: return False
	i = xbmcgui.ListItem('[ Поиск ]', iconImage = sicon, thumbnailImage = sicon)
	i.setProperty('fanart_image', sicon)
	xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'showsearch'})), i, True)
	i = xbmcgui.ListItem('[ Все категории ]', iconImage = icon, thumbnailImage = icon)
	i.setProperty('fanart_image', icon)
	xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'showlist', 'id':0})), i, True)
	i = xbmcgui.ListItem('[ Сериалы ]', iconImage = icon, thumbnailImage = icon)
	i.setProperty('fanart_image', icon)
	xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'showlist', 'id':0, 'video_type':2})), i, True)
	document = xml.dom.minidom.parseString(http)
	for item in document.getElementsByTagName('item'):
		i = xbmcgui.ListItem(item.getElementsByTagName('name')[0].firstChild.data, iconImage = icon, thumbnailImage = icon)
		i.setProperty('fanart_image', icon)
		xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'showlist', 'id':item.getElementsByTagName('id')[0].firstChild.data})), i, True)

	i = xbmcgui.ListItem('[ Недосмотренное ]', iconImage = icon, thumbnailImage = icon)
	xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'finished', 'page':0, 'mode':0})), i, True)

	xbmcplugin.endOfDirectory(h)



def finished(params):

	uparam = {'device_type':'xbmc', 'detail_info':1, 'view_limit':view_limit}
	if len(private_key): uparam['private_key'] = private_key

	try:    uparam['view_start'] = int(params['page']) * view_limit
	except: uparam['view_start'] = 0

	try:    uparam['mode'] = params['mode']
	except: uparam['mode'] = 0

	http = GET('http://muzunga.tv/stb/xml/finished.php?%s' % urllib.urlencode(uparam))
	if not http: return False

	if int(params['mode']) != 1:
		i = xbmcgui.ListItem('[ Просмотренные полностью ]', iconImage = icon, thumbnailImage = icon)
		i.setProperty('fanart_image', icon)
		xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'finished', 'mode':1, 'page':0})), i, True)

	document = xml.dom.minidom.parseString(http)

	items = document.getElementsByTagName('item')
	for item in items:
		item_id = item.getElementsByTagName('id')[0].firstChild.data
		poster = 'http://muzunga.tv/thumbs/%s/thumb/1.jpg?%s' % (item_id,item_id)
		mdata = parse_meta(item)
		i = xbmcgui.ListItem(mdata['title'], iconImage = poster, thumbnailImage = poster)
		i.setInfo(type = 'video', infoLabels = mdata)
		i.setProperty('fanart_image', poster)
		xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'play', 'id':item_id, 'season':0, 'episode':0})), i, True)


	if len(items) == view_limit:
		params['page'] = int(params['page']) + 1
		i = xbmcgui.ListItem('[ ЕЩЕ! ]', iconImage = icon, thumbnailImage = icon)
		i.setProperty('fanart_image', icon)
		xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode(params)), i, True)


	xbmcplugin.endOfDirectory(h)


#========================================================#
#					search
#========================================================#
def showsearch(params):
	try:    params['page'] = int(params['page'])
	except: params['page'] = 0
	uparam = {'private_key': private_key, 'view_limit': view_limit, 'detail_info': 0, 'view_start': view_limit * params['page']}
	try: uparam['search'] = params['search']
	except:
		KB = xbmc.Keyboard('', 'Поиск по Muzunga.TV')
		KB.doModal()
		if KB.isConfirmed(): uparam['search'] = KB.getText()
		else: return False
	http = GET('http://muzunga.tv/stb/xml/search.php?%s' % urllib.urlencode(uparam))
	if not http: return False
	items = xml.dom.minidom.parseString(http).getElementsByTagName('item')
	for item in items:
		item_id = item.getElementsByTagName('id')[0].firstChild.data
		poster = 'http://muzunga.tv/thumbs/%s/thumb/1.jpg?%s' % (item_id,item_id)
		mdata = parse_meta(item)
		i = xbmcgui.ListItem(mdata['title'], iconImage = poster, thumbnailImage = poster)
		i.setInfo(type = 'video', infoLabels = mdata)
		i.setProperty('fanart_image', poster)
		xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'play', 'id':item_id, 'season':0, 'episode':0})), i, True)
	if len(items) == view_limit:
		params['page'] += 1
		params['search'] = uparam['search']
		i = xbmcgui.ListItem('[ ЕЩЕ! ]', iconImage = icon, thumbnailImage = icon)
		i.setProperty('fanart_image', icon)
		xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode(params)), i, True)
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


#========================================================#
#					browse cats
#========================================================#
def showlist(params):
	try:    params['page'] = int(params['page'])
	except: params['page'] = 0
	try:    params['video_type'] = int(params['video_type'])
	except: params['video_type'] = 0
	uparam = {'private_key':private_key, 'view_limit':view_limit, 'detail_info':1, 'category_id': params['id'], 'video_type':params['video_type'], 'view_start': view_limit * params['page']}
	http = GET('http://muzunga.tv/stb/xml/list.php?%s' % urllib.urlencode(uparam))
	if not http: return False
	items = xml.dom.minidom.parseString(http).getElementsByTagName('item')
	for item in items:
		item_id = item.getElementsByTagName('id')[0].firstChild.data
		poster = 'http://muzunga.tv/thumbs/%s/thumb/1.jpg?%s' % (item_id,item_id)
		mdata = parse_meta(item)
		i = xbmcgui.ListItem(mdata['title'], iconImage = poster, thumbnailImage = poster)
		i.setInfo(type = 'video', infoLabels = mdata)
		i.setProperty('fanart_image', poster)
		xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'play', 'id':item_id, 'season':0, 'episode':0})), i, True)
	if len(items) == view_limit:
		params['page'] += 1
		i = xbmcgui.ListItem('[ ЕЩЕ! ]', iconImage = icon, thumbnailImage = icon)
		i.setProperty('fanart_image', icon)
		xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode(params)), i, True)
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


#========================================================#
#					showseasons
#========================================================#
def showseasons(params):
	uparam = {'id':params['id'], 'private_key':private_key}
	http = GET('http://muzunga.tv/stb/xml/movie.php?%s' % urllib.urlencode(uparam))
	if not http: return False
	seasons = xml.dom.minidom.parseString(http).getElementsByTagName('season')
	if len(seasons) == 1:
		params['season_id'] = seasons[0].getElementsByTagName('id')[0].firstChild.data
		showepisodes(params)
	else:
		for season in seasons:
			season_id = int(season.getElementsByTagName('id')[0].firstChild.data)
			mdata = {'season': season_id}
			mdata['title'] = u'Сезон %d (%s серий)' % (season_id, season.getElementsByTagName('episode_count')[0].firstChild.data)
			poster = 'http://muzunga.tv/thumbs/%s/thumb/1.jpg?%s' % (params['id'], params['id'])
			i = xbmcgui.ListItem(mdata['title'], iconImage = poster, thumbnailImage = poster)
			i.setInfo(type = 'video', infoLabels = mdata)
			i.setProperty('fanart_image', poster)
			xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'showepisodes', 'id':params['id'], 'season_id':season_id})), i, True)
		xbmcplugin.endOfDirectory(h)

#========================================================#
#					showepisodes
#========================================================#
def showepisodes(params):
	season_id = int(params['season_id'])
	uparam = {'id':params['id'], 'season':season_id, 'detail_info':1, 'private_key':private_key}
	http = GET('http://muzunga.tv/stb/xml/movie.php?%s' % urllib.urlencode(uparam))
	if not http: return False
	document = xml.dom.minidom.parseString(http)
	poster = 'http://muzunga.tv/thumbs/%s/thumb/1.jpg?%s' % (params['id'], params['id'])
	for season in document.getElementsByTagName('season'):
		if season_id == int(season.getElementsByTagName('id')[0].firstChild.data):
			for episode in season.getElementsByTagName('episode'):
				episode_id = int(episode.getElementsByTagName('id')[0].firstChild.data)
				mdata = parse_meta(episode)
				mdata['title'] = '%d. %s' % (episode_id, mdata['title'])
				mdata['season']  = season_id
				mdata['episode'] = episode_id
				i = xbmcgui.ListItem(mdata['title'], iconImage = poster, thumbnailImage = poster)
				i.setInfo(type = 'video', infoLabels = mdata)
				i.setProperty('fanart_image', poster)
				xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'play', 'id':params['id'], 'season':season_id, 'episode':episode_id})), i, True)
	xbmcplugin.endOfDirectory(h)


#******************************

def play(params):
	uparam = {'id':params['id'], 'private_key':private_key, 'detail_info':1}

	try:    uparam['season'] = int(params['season'])
	except: uparam['season'] = 0
	try:    uparam['episode'] = int(params['episode'])
	except: uparam['episode'] = 0

	try:    asselect = int(params['asselect'])
	except: asselect = 0

	movie_url = 'http://muzunga.tv/stb/xml/movie.php?%s' % urllib.urlencode(uparam)
	http = GET(movie_url)
	if not http: return False

	document = xml.dom.minidom.parseString(http)
	try:
		queue = int(document.getElementsByTagName('queue')[0].firstChild.data)
		if queue:
			showMessage('Пробуй немного позже', 'Место в очереди на подключение: %d' % queue, 2000)
			return False
	except:
		print '[%s]: playstart: queue failed' % (addon_id)
		pass


	use_episode = 0
	if document.getElementsByTagName('season'):
		use_episode = 1
		if uparam['episode'] == 0:
			showseasons(params)
			return False

	mdata = parse_meta(document)

	item_id = document.getElementsByTagName('id')[0].firstChild.data

	poster = 'http://muzunga.tv/thumbs/%s/thumb/1.jpg?%s' % (item_id, item_id)

	imgs = []
	try:
		for snap in document.getElementsByTagName('snap'):
			try:
				for big in snap.getElementsByTagName('big'):
					if big.firstChild.data: imgs.append('http://muzunga.tv/thumbs/%s' % big.firstChild.data)
			except: pass
	except: pass

	if use_episode:
		mdata['tvshowtitle'] = mdata['title']
		mdata['title'] = document.getElementsByTagName('episode_name')[0].firstChild.data
		try: mdata['season'] = int(document.getElementsByTagName('season_id')[0].firstChild.data)
		except: pass
		try: mdata['episode'] = int(document.getElementsByTagName('episode_id')[0].firstChild.data)
		except: pass
		try: mdata['plot'] = document.getElementsByTagName('episode_description')[0].firstChild.data
		except: pass
	else:
		try:
			if mdata['year']: mdata['title'] += u' (%s)' % mdata['year']
		except: pass

	try:    streamer = document.getElementsByTagName('streamer')[0].firstChild.data
	except: return False


	file_hd = document.getElementsByTagName('file_hd')
	file_sd = document.getElementsByTagName('file_sd')


	if file_hd:
		img = poster
		if len(imgs):
			img = imgs[0]
			del imgs[0]
		i = xbmcgui.ListItem('Смотреть в HD', iconImage = img, thumbnailImage = img)
		i.setInfo(type = 'video', infoLabels = mdata)
		i.setProperty('IsPlayable', 'true')
		uparam['func'] = 'playstart'
		uparam['hd'] = '1'
		i.setProperty('fanart_image', poster)
		xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode(uparam)), i)

	if file_sd:
		img = poster
		if len(imgs):
			img = imgs[0]
			del imgs[0]
		i = xbmcgui.ListItem('Смотреть в SD', iconImage = img, thumbnailImage = img)
		i.setInfo(type = 'video', infoLabels = mdata)
		i.setProperty('IsPlayable', 'true')
		uparam['func'] = 'playstart'
		uparam['hd'] = '0'
		i.setProperty('fanart_image', poster)
		xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode(uparam)), i)

	audios = document.getElementsByTagName('audio')

	if file_hd and len(file_hd) and audios and len(audios):
		for audio in audios:
			img = poster
			if len(imgs):
				img = imgs[0]
				del imgs[0]
			i = xbmcgui.ListItem(u'Смотреть в HD, звук: %s' % audio.getElementsByTagName('name')[0].firstChild.data, iconImage = img, thumbnailImage = img)
			i.setInfo(type = 'video', infoLabels = mdata)
			i.setProperty('IsPlayable', 'true')
			uparam['func'] = 'playstart'
			uparam['hd'] = '1'
			uparam['audio'] = audio.getElementsByTagName('id')[0].firstChild.data
			i.setProperty('fanart_image', poster)
			xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode(uparam)), i)

	if file_sd and len(file_sd) and audios and len(audios):
		for audio in audios:
			img = poster
			if len(imgs):
				img = imgs[0]
				del imgs[0]
			i = xbmcgui.ListItem(u'Смотреть в SD, звук:  %s' % audio.getElementsByTagName('name')[0].firstChild.data, iconImage = img, thumbnailImage = img)
			i.setInfo(type = 'video', infoLabels = mdata)
			i.setProperty('IsPlayable', 'true')
			uparam['func'] = 'playstart'
			uparam['hd'] = '0'
			uparam['audio'] = audio.getElementsByTagName('id')[0].firstChild.data
			i.setProperty('fanart_image', poster)
			xbmcplugin.addDirectoryItem(h, '%s?%s' % (sys.argv[0], urllib.urlencode(uparam)), i)

	subtitles = document.getElementsByTagName('subtitle')
	if subtitles and len(subtitles): showMessage('Субтитры', 'Этот фильм имеет субтитры', 3000)

	xbmcplugin.endOfDirectory(h)



def playstart(params):

	del params['func']

	try: del params['detail_info']
	except: pass

	if params['hd'] == '1': vkey = 'file_hd'
	else: vkey = 'file_sd'

	del params['hd']

	try:
		audio = '_%s' % params['audio']
		del params['audio']
	except: audio = ''

	http = GET('http://muzunga.tv/stb/xml/movie.php?%s' % urllib.urlencode(params))
	if not http: return False
	document = xml.dom.minidom.parseString(http)
	try:
		queue = int(document.getElementsByTagName('queue')[0].firstChild.data)
		if queue:
			showMessage('Пробуй немного позже', 'Место в очереди на подключение: %d' % queue, 2000)
			return False
	except:
		print '[%s]: playstart: queue failed' % (addon_id)
		pass

	try:    streamer = document.getElementsByTagName('streamer')[0].firstChild.data
	except: return False

	vfile = document.getElementsByTagName(vkey)[0].firstChild.data
	vpath = '%s app=%s playpath=%s%s' % (streamer, streamer.split('/')[-1], vfile, audio)


	i = xbmcgui.ListItem(path = vpath)
	xbmcplugin.setResolvedUrl(h, True, i)
	xbmc.sleep(2000)
	subtitles = document.getElementsByTagName('subtitle')
	if subtitles and len(subtitles):
		for subtitle in subtitles: xbmc.Player().setSubtitles('http://www.muzunga.tv%s' % subtitle.getElementsByTagName('filename')[0].firstChild.data)
		xbmc.Player().disableSubtitles()


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
		showroot(params)

	if func != None:
		try: pfunc = globals()[func]
		except:
			pfunc = None
			print '[%s]: Function "%s" not found' % (addon_id, func)
			showMessage('Internal addon error', 'Function "%s" not found' % func, 2000)
		if pfunc: pfunc(params)
