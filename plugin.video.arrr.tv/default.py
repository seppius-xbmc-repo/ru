#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#   Writer (c) 19/10/2011, Khrysev D.A., E-mail: x86demon@gmail.com
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

import sys
import os

sys.path.append(os.path.join(os.getcwd().replace(';', ''), 'resources', 'lib'))

import httplib
import urllib
import urllib2
import Cookie
import simplejson as json

import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmc

import socket
socket.setdefaulttimeout(50)

icon = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''), 'icon.png'))
siteUrl = 'arrr.tv'
httpSiteUrl = 'http://%s' % siteUrl
apiUrl = '%s/api' % httpSiteUrl
__settings__ = xbmcaddon.Addon(id='plugin.video.arrr.tv')
sid_file = os.path.join(xbmc.translatePath('special://temp/'), 'plugin.video.arrr.tv.cookies.sid')

h = int(sys.argv[1])

def construct_request(params):
	return '%s?%s' % (sys.argv[0], urllib.urlencode(params))

def showMessage(heading, message, times = 3000):
	xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))

headers  = {
	'User-Agent' : 'Opera/9.80 (X11; Linux i686; U; ru) Presto/2.7.62 Version/11.00',
	'Accept'     :' text/html, application/xml, application/xhtml+xml, image/png, image/jpeg, image/gif, image/x-xbitmap, */*',
	'Accept-Language':'ru-RU,ru;q=0.9,en;q=0.8',
	'Accept-Charset' :'utf-8, utf-16, *;q=0.1',
	'Accept-Encoding':'identity, *;q=0'
}

def GET(target, referer, post_params = None, accept_redirect = True, get_redirect_url = False):
	try:
		connection = httplib.HTTPConnection(siteUrl)

		if post_params == None:
			method = 'GET'
			post = None
		else:
			method = 'POST'
			post = urllib.urlencode(post_params)
			headers['Content-Type'] = 'application/x-www-form-urlencoded'

		if os.path.isfile(sid_file):
			fh = open(sid_file, 'r')
			csid = fh.read()
			fh.close()
			headers['Cookie'] = 'session=%s' % csid

		headers['Referer'] = referer
		connection.request(method, target, post, headers = headers)
		response = connection.getresponse()

		if response.status == 403:
			raise Exception("Forbidden, check credentials")
		if response.status == 404:
			raise Exception("File not found")
		if accept_redirect and response.status in (301, 302):
			target = response.getheader('location', '')
			if target.find("://") < 0:
				target = httpSiteUrl + target
			if get_redirect_url:
				return target
			else:
				return GET(target, referer, post_params, False)

		try:
			sc = Cookie.SimpleCookie()
			sc.load(response.msg.getheader('Set-Cookie'))
			fh = open(sid_file, 'w')
			fh.write(sc['session'].value)
			fh.close()
		except: pass

		if get_redirect_url:
			return False
		else:
			http = response.read()
			return http

	except Exception, e:
		showMessage('Error', e, 5000)
		return None

def apiCall(href):
	http = GET(href, apiUrl)
	if http == None: return False

	response = {"status": "nok", "data": []}
	try:
		response = json.loads(http)
	except:
		showMessage('ОШИБКА', 'Неверный ответ сервера', 3000)
		return

	if response['status'] != 'ok' or len(response['data']) == 0:
		showMessage('ОШИБКА', 'Данных не найдено', 3000)
		return False
	else:
		return response

def getCategories(params):
	li = xbmcgui.ListItem('Tv Shows')
	uri = construct_request({
		'mode': 'getshows',
		'href': apiUrl + '/shows/'
	})
	xbmcplugin.addDirectoryItem(h, uri, li, True)

	li = xbmcgui.ListItem('Movies')
	uri = construct_request({
		'mode': 'getmovies',
		'href': apiUrl + '/movies/'
	})
	xbmcplugin.addDirectoryItem(h, uri, li, True)

	xbmcplugin.endOfDirectory(h)

def getLang():
	langs = {"0": "ru", "1": "en"}
	return langs[__settings__.getSetting('Preferred language')]

def getTitle(ruTitle, enTitle, id):
	if enTitle == None and ruTitle == None:
		originalName = id.replace('-', ' ')
		return originalName[0].upper() + originalName[1:]
	elif enTitle == None and ruTitle != None:
		return ruTitle
	elif enTitle != None and ruTitle == None:
		return enTitle
	else:
		showTitleType = __settings__.getSetting("Show title")
		title = enTitle
		if showTitleType == "0":
			title = ruTitle
		if showTitleType == "1":
			title = enTitle
		if showTitleType == "2":
			title = '%s/%s' % (ruTitle, enTitle)
		if showTitleType == "3":
			title = '%s/%s' % (enTitle, ruTitle)

		return title

def getAvailableLanguages(video):
	result = []
	for videoData in video:
		try:
			result.index(videoData[0])
		except:
			result.append(videoData[0])
	return result

def getmovies(params):
	lang = getLang()
	movies = apiCall(urllib.unquote_plus(params['href']))
	showLanguages = __settings__.getSetting("Show available languages") == "true"
	if movies != False:
		for movie in movies['data']:
			id = movie['id']
			cover = movie['cover'][lang]
			backdrop = movie['backdrop']
			try:
				plot = movie['description'][lang]
			except:
				plot = ""

			try:
				title = getTitle(movie['title']["ru"], movie['title']["en"], id)
			except:
				title = '[No-title]'
			video = movie['video']
			availableLanguages = getAvailableLanguages(video)

			try:
				if __settings__.getSetting('Show preferred language only') == "true":
					availableLanguages.index(lang)
				listName = title
				if showLanguages:
					listName += " (" + ", ".join(getAvailableLanguages(video)) + ")"
				li = xbmcgui.ListItem(listName, iconImage = cover, thumbnailImage = cover)
				if backdrop != None:
					li.setProperty('fanart_image', backdrop)
				li.setInfo(type='video', infoLabels={'title': title, 'plot': plot})
				li.setProperty('IsPlayable', 'true')
				uri = construct_request({
					'mode': 'play',
					'video': json.dumps(video),
					'href': "%s/movies/%s/video/" % (apiUrl, id)
				})
				xbmcplugin.addDirectoryItem(h, uri, li)
			except:
				pass

	xbmcplugin.endOfDirectory(h)

def getshows(params):
	shows = apiCall(urllib.unquote_plus(params['href']))
	if shows != False:
		for show in shows['data']:
			id = show['id']
			cover = show['cover']
			title = getTitle(show['title']["ru"], show['title']["en"], id)

			li = xbmcgui.ListItem(title, iconImage = cover, thumbnailImage = cover)
			li.setInfo(type='video', infoLabels={'title': title})
			uri = construct_request({
				'mode': 'getepisodes',
				'href': "%s/shows/%s/" % (apiUrl, id),
				'tvshow': show['title']["en"]
			})
			xbmcplugin.addDirectoryItem(h, uri, li, True)

	xbmcplugin.endOfDirectory(h)

def getepisodes(params):
	lang = getLang()
	tvshow = urllib.unquote_plus(params['tvshow'])
	episodes = apiCall(urllib.unquote_plus(params['href']))
	showLanguages = __settings__.getSetting("Show available languages") == "true"
	if episodes != False:
		for episode in episodes['data']:
			id = episode['id']
			cover = episode['cover'][lang]
			backdrop = episode['backdrop']
			title = getTitle(episode['title']["ru"], episode['title']["en"], id)
			seasonNum = int(episode['season'])
			episodeNum = int(episode['episode'])
			video = episode['video']
			availableLanguages = getAvailableLanguages(video)

			try:
				if __settings__.getSetting('Show preferred language only') == "true":
					availableLanguages.index(lang)
				listName = "[s%de%02d] %s" % (seasonNum, episodeNum, title)
				if showLanguages:
					listName += " (" + ", ".join(availableLanguages) + ")"
				li = xbmcgui.ListItem(listName, iconImage = cover, thumbnailImage = cover)
				li.setProperty('fanart_image', backdrop)
				li.setInfo(type='video', infoLabels={
					'title': title,
					'episode': episodeNum,
					'season': seasonNum,
					'tvshowtitle': tvshow
				})
				uri = construct_request({
					'mode': 'play',
					'video': json.dumps(video),
					'href': "%s/shows/%s/video/" % (apiUrl, id)
				})
				li.setProperty('IsPlayable', 'true')
				xbmcplugin.addDirectoryItem(h, uri, li)
			except:
				pass

	xbmcplugin.endOfDirectory(h)

def getFiles(files):
	keys = files.keys()
	keys.sort()
	if __settings__.getSetting("Prefer HD") == "true":
		keys.reverse()
	return [files[key] for key in keys]

def getFilesByLang(files):
	if __settings__.getSetting('Show preferred language only') == "true":
		try:
			return [files[getLang()]]
		except:
			showMessage('Error', 'No files in selected language were found')
			return []
	else:
		keys = files.keys()
		keys.sort()
		if __settings__.getSetting("Preferred language") != "1":
			keys.reverse()

		return [files[key] for key in keys]

def play(params):
	login = __settings__.getSetting("Login")
	password = __settings__.getSetting("Password")
	if len(login) == 0 or len(password) == 0:
		showMessage('Error', 'Проверьте логин и пароль', 3000)
		return False

	href = urllib.unquote_plus(params['href'])
	video = json.loads(urllib.unquote_plus(params['video']))
	files = {}
	for videoData in video:
		try:
			files[videoData[0]]
		except:
			files[videoData[0]] = {}
		files[videoData[0]][videoData[1]] = "%s/%s.%s" % (videoData[0], videoData[1], videoData[2])

	for filesData in getFilesByLang(files):
		for file in getFiles(filesData):
			target = href + file
			fileUrl = GET(
				target, apiUrl, {
					"username": login,
					"password": password
				}, True, True)
			if fileUrl and isRemoteFile(fileUrl):
				i = xbmcgui.ListItem(path = fileUrl)
				i.setProperty('mimetype', 'video/x-msvideo')
				xbmcplugin.setResolvedUrl(h, True, i)
				return True

	return False

def isRemoteFile(url):
	try:
		urllib2.urlopen(urllib2.Request(url))
		return True
	except:
		return False

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

try:
	mode = urllib.unquote_plus(params['mode'])
except:
	getCategories(params)

if (mode != None):
	try:
		func = globals()[mode]
	except:
		pass
	if func: func(params)
