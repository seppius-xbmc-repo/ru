#!/usr/bin/python
# -*- coding: utf-8 -*-
#/*
# *   Copyright (с) 2011 XBMC-Russia, HD-lab Team, E-mail: dev@hd-lab.ru
# *   Writer (C) 06/03/2011, Kostynoy S.A., E-mail: seppius2@gmail.com
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
# *  http://www.gnu.org/licenses/gpl.html
# */

import xbmc, xbmcaddon
import Cookie, httplib, urllib
import kbxbmc
import xmlrpc2scgi
import socket
socket.setdefaulttimeout(15)


API_SERV = 'api.kinobaza.tv'

headers = { 'Content-Type' : 'application/x-www-form-urlencoded',
			'User-Agent'   : 'XBMC/10-series (Python addon; XBMC-Russia; HD-lab Team; 2011; http://www.xbmc.ru)' }


def showMessage(heading, message, times = 3000, pics = ''):
	xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, pics))

__settings__ = xbmcaddon.Addon(id = 'plugin.video.kinobaza.tv')
__language__ = __settings__.getLocalizedString

rtc_uri             = __settings__.getSetting('rtc_uri')
rtc_select          = __settings__.getSetting('rtc_select').lower()
list_limit          = __settings__.getSetting('list_limit')

print 'initial info - rtc_uri    = [%s]' % rtc_uri
print 'initial info - rtc_select = [%s]' % rtc_select


def get_rtc():
	rtc = xmlrpc2scgi.RTorrentXMLRPCClient(rtc_uri)
	if (len(rtc_uri) < 4) or (rtc == None):
		showMessage('Ошибка подключения', 'Проверьте rTorrent URI', 5000)
		return None
	try:
		rtc_version = rtc.system.client_version()
		print 'Версия rTorrent [%s]' % rtc_version
	except:
		showMessage('rTorrent не подключен!', rtc_uri, 5000)
		return None
	return rtc


def LIST_LIMIT():
	limits = [10,25,50,75,100]
	return limits[int(list_limit)]


def POSTER(poster):
	return 'http://media.kinobaza.tv/films/%d/poster/207.jpg' % poster


def replace_quality(quality):
	if quality != None:
		quality = quality.encode('utf-8')
		quality = quality.replace('low','Низкое')
		quality = quality.replace('medium','Среднее')
		quality = quality.replace('high','Высокое')
		quality = quality.replace('hd','HD 720 или выше')
		quality = quality.replace('unknown','Неизвестно')
		qualitys = 'Качество: %s, ' % quality
		return qualitys
	else:
		return ''



def KBREQUEST(target, post_params = None):

	print 'KBREQUEST -> URL         = [%s]' % target
	print 'KBREQUEST -> post_params = [%s]' % post_params

	if post_params == None:
		method = 'GET'
		post = None
	else:
		method = 'POST'
		post = urllib.urlencode(post_params)

	connection = httplib.HTTPConnection(API_SERV)

	PHPSESSID = __settings__.getSetting('PHPSESSID')
	if PHPSESSID != '': headers['Cookie'] = 'PHPSESSID='+PHPSESSID

	connection.request(method, target, post, headers = headers)
	response = connection.getresponse()

	try:
		sc = Cookie.SimpleCookie()
		sc.load(response.msg.getheader('Set-Cookie'))
		__settings__.setSetting('PHPSESSID', sc['PHPSESSID'].value)
	except: pass

	http = response.read()

	if response.status != 200:
		print 'response.status != 200, response.reason = %s' % response.reason
		kbxbmc.showMessage('oops', 'response.reason = %s' % response.reason, 5000)

#		code = djson['code']
#		message = djson['message']
#		showMessage('Ошибка %d'%code, message.encode('utf-8'), 5000)
#		print 'ERROR %s MESSAGE %s ' % (code, message.encode('utf-8'))
#		return True


		print http
		return None
	print 'KBREQUEST -> COMPLETED, LEN %d' % len(http)
	return http



def getmetadata(data, film_id):
	info = {}
	#info = {'count': int(data['id'])}

	try:    info['title'] = data['name'].encode('utf-8')
	except: info['title'] = 'Название не указано'

	#original_name = data['original_name']
	try:
		if (data['original_name'] != None):
			if len(data['original_name']) > 0:
				info['plotoutline'] = 'Оригинальное название: "%s"' % data['original_name'].encode('utf-8')
	except: pass
	try:    info['year'] = int(data['year'])
	except: pass
	try:
		film_duration = int(data['duration'])
		if (film_duration > 0):
			if film_duration > 59: tstr = '%s:%s:00' % (film_duration/60, film_duration%60)
			else: tstr = '%s:00' % film_duration
			info['duration'] = tstr
	except: pass

	try:    info['plot'] = data['description'].encode('utf-8')
	except: info['plot'] = ''

	try:
		if data['budget'] == None: plo_budget = ''
		else: plo_budget = 'Бюджет: %s $\n' % data['budget']
	except: plo_budget = ''

	try:
		if data['revenue_usa'] == None: plo_rev_usa = ''
		else: plo_rev_usa = 'Доход в США: %s $\n' % data['revenue_usa']
	except: plo_rev_usa = ''

	try:
		if data['revenue_world'] == None: plo_rev_world = ''
		else: plo_rev_world = 'Доход в мире: %s $\n' % data['revenue_world']
	except: plo_rev_world = ''

	try:
		if data['revenue_russia'] == None: plo_rev_russia = ''
		else: plo_rev_russia = 'Доход в России: %s $\n' % data['revenue_russia']
	except: plo_rev_russia = ''

	try:
		film_countries = data['countries']
	except: film_countries = None
	if film_countries != None:
		scountry = ''
		for country in film_countries:
			country_id   = country['id']
			country_name = country['name'].encode('utf-8')
			scountry += ', %s'%country_name
		if len(scountry) > 0:
			scountry = 'Страна:%s' % (scountry[1:])
			info['plot'] = scountry + '\n' + info['plot']

	a4 = ''
	a5 = ''
	a6 = ''

	try:
		film_participants = data['participants']
	except: film_participants = None

	if film_participants != None:


		if film_participants['actor'] != None:
			a1 = []
			for actor in film_participants['actor']: a1.append(actor['name'].encode('utf-8'))
			info['cast'] = a1

		if film_participants['director'] != None:
			if len(film_participants['director']) > 0:
				a2 = ''
				for director in film_participants['director']: a2 += ', %s' % director['name'].encode('utf-8')
				info['director'] = a2[2:]

		if film_participants['writer'] != None:
			if len(film_participants['writer']) > 0:
				a3 = ''
				for writer in film_participants['writer']: a3 += ', %s' % writer['name'].encode('utf-8')
				info['writer'] = a3[2:]

		if film_participants['producer'] != None:
			if len(film_participants['producer']) > 0:
				for producer in film_participants['producer']: a4 += ', %s'%producer['name'].encode('utf-8')
				a4 = 'Продюсер: %s\n' % a4[2:]

		if film_participants['operator'] != None:
			if len(film_participants['operator']) > 0:
				for operator in film_participants['operator']: a5 += ', %s'%operator['name'].encode('utf-8')
				a5 = 'Оператор: %s\n' % a5[2:]

		if film_participants['composer'] != None:
			if len(film_participants['composer']) > 0:
				for composer in film_participants['composer']: a6 += ', %s'%composer['name'].encode('utf-8')
				a6 = 'Композитор: %s\n' % a6[2:]

	info['credits'] = a6

	try:
		genres = data['genres']
	except: genres = None

	if genres != None:
		genre = ''
		for gArray in genres:
			genre_name = gArray['name'].encode('utf-8')
			genre += ', %s'%(genre_name)
		if len(genre) > 0:
			info['genre'] = genre[2:]
			info['tagline'] = info['genre'].replace(',','')


	try:
		fbtq = data['best_torrent_quality']
	except: fbtq = None

	fbtqs = replace_quality(fbtq)


	info['plot'] = fbtqs + info['plot'] + plo_budget + plo_rev_usa + plo_rev_world + plo_rev_russia + a4 + a5 + a6

	try:
		film_ratings = data['ratings'] # array
	except: film_ratings = None
	if film_ratings != None:

		arates = []
		avotes = []

		rstring = ''

		imdb_com     = film_ratings['imdb.com']
		if imdb_com != None:
			arates.append(imdb_com['rate'])
			avotes.append(imdb_com['votes'])
			rstring += 'Рейтинг imdb.com: %s, голосов: %s\n'%(imdb_com['rate'], imdb_com['votes'])

		kinopoisk_ru = film_ratings['kinopoisk.ru']
		if imdb_com != None:
			arates.append(kinopoisk_ru['rate'])
			avotes.append(kinopoisk_ru['votes'])
			rstring += 'Рейтинг kinopoisk.ru: %s, голосов: %s\n'%(kinopoisk_ru['rate'], kinopoisk_ru['votes'])

		tv_com       = film_ratings['tv.com']
		if imdb_com != None:
			arates.append(tv_com['rate'])
			avotes.append(tv_com['votes'])
			rstring += 'Рейтинг tv.com: %s, голосов: %s\n'%(tv_com['rate'], tv_com['votes'])

		rstring = rstring.replace('None','Нет')
		info['votes'] = str(max(avotes))
		try: info['rating'] = float(max(arates))
		except: pass
		if rstring != '': info['plot'] = info['plot'] + '\n' + rstring

	info['iconImage'] = 'http://media.kinobaza.tv/films/%s/poster/60.jpg'%film_id
	info['thumbnailImage'] = 'http://media.kinobaza.tv/films/%s/poster/207.jpg'%film_id

	return info


#def calc_file_size(size):
#	SUFFIXES = ['KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
#	multiple = 1024
#	for suffix in SUFFIXES:
#		size /= 1024
#		if size < 1024:
#			return '{0:.1f} {1}'.format(size, suffix)
