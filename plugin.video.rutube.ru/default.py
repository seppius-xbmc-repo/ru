#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#   Copyright (c) 2011 XBMC-Russia, HD-lab Team, E-mail: dev@hd-lab.ru
#   Writer (c) 2011, Kostynoy S.A., E-mail: seppius2@gmail.com
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

import urllib2, re, xbmc, xbmcgui, xbmcplugin, os, urllib, urllib2, socket


socket.setdefaulttimeout(12)

h = int(sys.argv[1])
icon = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'icon.png'))

def showMessage(heading, message, times = 3000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))

def strip_html(text):
	def fixup(m):
		text = m.group(0)
		if text[:1] == "<":
			if text[1:3] == 'br':
				return '\n'
			else:
				return ""
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

def GET(url):
	try:
		print 'def GET(%s):'%url
		req = urllib2.Request(url)
		f = urllib2.urlopen(req)
		a = f.read()
		f.close()
		return a.decode('koi8-r').encode('utf-8')
	except:
		showMessage('Не могу открыть URL', url)
		return None

#def ADD_SEARCH():
#	i = xbmcgui.ListItem('[ Поиск ]', iconImage=icon, thumbnailImage=icon)
#	u  = sys.argv[0] + '?mode=SEARCH'
#	xbmcplugin.addDirectoryItem(h, u, i, True)





def ROOT():
	http = GET('http://rutube.ru/cgi-bin/jsapi.cgi?rt_mode=categories')
	if http == None: return False
	r1 = re.compile('id:\s*(.[0-9]*)\s*,\s*name:\s*(.+)\s*,\s*link:\s*(.+)\s*,\s*numberOfMovies:\s*(.[0-9]*)').findall(http)
	if len(r1) == 0:
		showMessage('ПОКАЗАТЬ НЕЧЕГО', 'Нет элементов id,name,link,numberOfMovies')
		return False
	for cID, cName, cUrl, count in r1:
		url  = 'http://rutube.ru/cgi-bin/jsapi.cgi?rt_mode=movies&rt_category=%s&rt_count=50'%cID
		txt = '%s [%s роликов]'%(cName, count)
		i = xbmcgui.ListItem(txt, iconImage=icon, thumbnailImage=icon)
		u  = sys.argv[0] + '?mode=OPEN_MOVIES'
		u += '&url=%s'%urllib.quote_plus(url)
		u += '&page=0'
		xbmcplugin.addDirectoryItem(h, u, i, True)

	#ADD_SEARCH()
	xbmcplugin.endOfDirectory(h)


def OPEN_MOVIES(target, CurPage):
	http = GET('%s&rt_page=%s'%(target,CurPage))
	if http == None: return False
	rows = re.compile('{(.+?)}', re.DOTALL).findall(http)
	if len(rows) == 0:
		showMessage('ПОКАЗАТЬ НЕЧЕГО', 'Нет элементов {(.+?)}')
		return False
	for row in rows:
		r_title         = re.compile('title\s*:\s*(.+)\s*,').findall(row)
		r_playerLink    = re.compile("playerLink\s*:\s*'http://.+?/(.+?)'\s*,").findall(row)
		if ((len(r_title) > 0) and (len(r_playerLink) > 0)):
			title            = strip_html(r_title[0][1:-1])
			info = {'title':title, 'studio':'RuTube'}
			try:
				r_size             = re.compile('size\s*:\s*(.+)\s*,').findall(row)
				if len(r_size) > 0:
					size = r_size[0][1:-1].upper()
					if size.find('MB') != -1:
						mm = 1048576
					elif size.find('KB') != -1:
						mm = 1024
					size = size.replace(',','.').replace('KB','').replace('MB','')
					info['size'] = int(float(size)*mm)
			except: pass
			try:
				r_duration         = re.compile('duration\s*:\s*(.+)\s*,').findall(row)
				if len(r_duration) > 0:     info['duration'] = r_duration[0][1:-1]
			except: pass
			try:
				r_recordDate       = re.compile('recordDate\s*:\s*(.+)\s*,').findall(row)
				if len(r_recordDate) > 0:
					recordDate = r_recordDate[0][1:-1].lower()
					recordDate = recordDate.replace('&nbsp;','.')
					recordDate = recordDate.replace('янв','01').replace('фев','02').replace('мар','03').replace('апр','04')
					recordDate = recordDate.replace('май','05').replace('июн','06').replace('июл','07').replace('авг','08')
					recordDate = recordDate.replace('сен','09').replace('окт','10').replace('ноя','11').replace('дек','12')
					info['date'] = recordDate
			except: pass
			try:
				r_hits = re.compile('hits\s*:\s*(.+)\s*,').findall(row)
				if len(r_hits) > 0:
					info['playcount'] = int(r_hits[0])
			except: pass
			try:
				r_author = re.compile('author\s*:\s*(.+)\s*,').findall(row)
				if len(r_author) > 0:
					info['director'] = r_author[0][1:-1]
			except: pass
			try:
				r_description = re.compile('description\s*:\s*(.+)\s*,').findall(row)
				if len(r_description) > 0:
					info['plot'] = strip_html(r_description[0][1:-1])
			except: pass
			try:
				r_rating = re.compile('rating\s*:\s*(.+)\s*,').findall(row)
				if len(r_rating) > 0:
					info['rating'] = float(r_rating[0])
			except: pass
			try:
				r_votes = re.compile('votes\s*:\s*(.+)\s*,').findall(row)
				if len(r_votes) > 0:
					info['votes'] = r_votes[0][1:-1]
			except: pass
			#try:
				#r_numberOfComments = re.compile('numberOfComments\s*:\s*(.+)\s*,').findall(row)
				#if len(r_numberOfComments) > 0:
				#	info['size'] = r_size[0][1:-1]
			#except: pass
			try:
				r_categoryName     = re.compile('categoryName\s*:\s*(.+)\s*,').findall(row)
				if len(r_categoryName) > 0: info['genre'] = r_categoryName[0][1:-1]
			except: pass
			try:
				r_thumbnailLink    = re.compile('thumbnailLink\s*:\s*(.+)\s*,').findall(row)
				if len(r_thumbnailLink) > 0:
					img = r_thumbnailLink[0][1:-1]
			except: img = icon

			i = xbmcgui.ListItem(title, iconImage=img, thumbnailImage=img)
			i.setInfo(type = 'video', infoLabels = info)
			u  = sys.argv[0] + '?mode=PLAY'
			u += '&url=%s'%urllib.quote_plus('http://bl.rutube.ru/%s.xml'%r_playerLink[0])
			i.setProperty('IsPlayable', 'true')
			xbmcplugin.addDirectoryItem(h, u, i)

	cPage = int(CurPage) + 1
	r1 = re.compile('numberOfPages: (.+?),', re.DOTALL).findall(http)
	if len(r1) > 0:
		pages = int(r1[0])-1
		if (cPage <= pages):
			i = xbmcgui.ListItem('Далее [ на страницу %d ] >>'%cPage, iconImage=icon, thumbnailImage=icon)
			u  = sys.argv[0] + '?mode=OPEN_MOVIES'
			u += '&url=%s'%urllib.quote_plus(target)
			u += '&page=%d'%cPage
			xbmcplugin.addDirectoryItem(h, u, i, True)

	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_UNSORTED)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_SIZE)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_DATE)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_DURATION)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_GENRE)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_VIDEO_RATING)

	xbmcplugin.endOfDirectory(h)




def PLAY(wurl):
	swf_player = 'http://rutube.ru/player.swf'
	http = GET(wurl)
	if http == None: return False
	rows1 = re.compile('\!\[CDATA\[(.+?)\]\]').findall(http)
	if len(rows1) == 0:
		showMessage('ПОКАЗАТЬ НЕЧЕГО', 'Нет элементов CDATA')
		return False
	rows1 = re.compile('\!\[CDATA\[(.+?)\]\]').findall(http)
	if len(rows1) != 0:
		rtmp = rows1[0]
		artmp = rtmp.replace('://','/').split('/')
		tcUrl = '%s://%s/%s/'%(artmp[0],artmp[1],artmp[2])
		pageUrl = wurl #'http://rutube.ru/tracks?v=%s'
		playPath = artmp[3]
		try: playPath += '/%s'%artmp[4]
		except: pass
		try: playPath += '/%s'%artmp[5]
		except: pass
		try: playPath += '/%s'%artmp[6]
		except: pass
		try: playPath += '/%s'%artmp[7]
		except: pass
		try: playPath += '/%s'%artmp[8]
		except: pass
		try: playPath += '/%s'%artmp[9]
		except: pass
	i = xbmcgui.ListItem( path = '%s swfUrl=%s swfVfy=True tcUrl=%s pageUrl=%s playPath=%s' % (tcUrl, swf_player, tcUrl, pageUrl, playPath) )
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
	return param

params=get_params(sys.argv[2])


mode = None

try:
	mode = urllib.unquote_plus(params['mode'])
except:
	ROOT()

if mode == 'OPEN_MOVIES':
	OPEN_MOVIES(urllib.unquote_plus(params['url']),urllib.unquote_plus(params['page']))

if mode == 'PLAY':
	PLAY(urllib.unquote_plus(params['url']))

