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

import urllib, urllib2, re, sys, os, httplib, Cookie
import xbmcplugin, xbmcgui, xbmcaddon, xbmc
import socket
socket.setdefaulttimeout(50)

icon = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''), 'icon.png'))
siteUrl = 'www.filmy.net.ua'
httpSiteUrl = 'http://' + siteUrl
__settings__ = xbmcaddon.Addon(id='plugin.video.filmy.net.ua')

h = int(sys.argv[1])

def showMessage(heading, message, times = 3000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))

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

headers  = {
		'User-Agent' : 'Opera/9.80 (X11; Linux i686; U; ru) Presto/2.7.62 Version/11.00',
		'Accept'     :' text/html, application/xml, application/xhtml+xml, image/png, image/jpeg, image/gif, image/x-xbitmap, */*',
		'Accept-Language':'ru-RU,ru;q=0.9,en;q=0.8',
		'Accept-Charset' :'utf-8, utf-16, *;q=0.1',
		'Accept-Encoding':'identity, *;q=0'
	}

sid_file = os.path.join(xbmc.translatePath('special://temp/'), 'plugin_video_filmy_net_ua.sid')


def GET(target, referer, post_params = None):
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
			headers['Cookie'] = 'sid=%s' % csid

		headers['Referer'] = referer
		connection.request(method, target, post, headers = headers)
		response = connection.getresponse()

		try:
				sc = Cookie.SimpleCookie()
				sc.load(response.msg.getheader('Set-Cookie'))
				fh = open(sid_file, 'w')
				fh.write(sc['sid'].value)
				fh.close()
		except: pass

		http = response.read()
		http = http.decode('koi8-r').encode('utf-8')

		return http
	except Exception, e:
		showMessage(target, e, 5000)
		return None


def getitems(params):
	http = GET(httpSiteUrl + '/film/', httpSiteUrl)
	if http == None: return False

	href = httpSiteUrl + '/rating/'
	li = xbmcgui.ListItem("[ Топ скачиваний ]", iconImage = icon, thumbnailImage = icon)
	uri = sys.argv[0] + '?mode=getfilms'
	uri += '&href='+urllib.quote_plus(href)
	uri += '&referer='+urllib.quote_plus(httpSiteUrl)
	xbmcplugin.addDirectoryItem(h, uri, li, True)

	href = httpSiteUrl + '/last/'
	li = xbmcgui.ListItem("[ Последние поступления ]", iconImage = icon, thumbnailImage = icon)
	uri = sys.argv[0] + '?mode=getfilms'
	uri += '&href='+urllib.quote_plus(href)
	uri += '&referer='+urllib.quote_plus(httpSiteUrl)
	xbmcplugin.addDirectoryItem(h, uri, li, True)

	name = "Все"
	href = httpSiteUrl + '/film/all/add/'
	li = xbmcgui.ListItem(name, iconImage = icon, thumbnailImage = icon)
	uri = sys.argv[0] + '?mode=getfilms'
	uri += '&href='+urllib.quote_plus(href)
	uri += '&name='+urllib.quote_plus(name)
	uri += '&referer='+urllib.quote_plus(httpSiteUrl + '/film')
	xbmcplugin.addDirectoryItem(h, uri, li, True)

	s1 = re.compile('href=\"/film/(.*?)/add/1/(.*?)/\"').findall(http)
	if len(s1) > 0:
		for href, name in s1:
			name = strip_html(name)
			href = httpSiteUrl + '/film/%s/add/' % href
			li = xbmcgui.ListItem(name, iconImage = icon, thumbnailImage = icon)
			uri = sys.argv[0] + '?mode=getfilms'
			uri += '&href='+urllib.quote_plus(href)
			uri += '&name='+urllib.quote_plus(name)
			uri += '&referer='+urllib.quote_plus(httpSiteUrl + '/film')
			xbmcplugin.addDirectoryItem(h, uri, li, True)

		li = xbmcgui.ListItem('[ ПОИСК ]', iconImage = icon, thumbnailImage = icon)
		uri = sys.argv[0] + '?mode=runsearch'
		xbmcplugin.addDirectoryItem(h, uri, li, True)

		xbmcplugin.endOfDirectory(h)
	else:
		showMessage('ОШИБКА ДИЗАЙНА', '/film/(.*?)/add/1/(.*?)/"', 3000)
		return False




def runsearch(params):
	skbd = xbmc.Keyboard()
	skbd.setHeading('Что ищем?')
	skbd.doModal()
	if (skbd.isConfirmed()):
		SearchStr = skbd.getText()
		http = GET(httpSiteUrl + '/?com=search','http://www.filmy.net.ua', {'text':SearchStr.decode('utf-8').encode('koi8-r')})
		if http == None: return False
		http = http.replace('\t','') #.replace('\n','')
		s1 = re.compile('<a href="(.*?)" title="Фильм.+?" class="kommen".+?>\s(.*?)</a>').findall(http)
		if len(s1) > 0:
			for href, name in s1:
				name = strip_html(name)
				href = httpSiteUrl + href
				li = xbmcgui.ListItem(name, iconImage = icon, thumbnailImage = icon)
				uri = sys.argv[0] + '?mode=play'
				uri += '&href='+urllib.quote_plus(href)
				uri += '&referer='+urllib.quote_plus(httpSiteUrl + '/?com=search')
				li.setProperty('IsPlayable', 'true')
				li.setInfo(type='video', infoLabels={'title':name,'genre':'Результат поиска',})
				xbmcplugin.addDirectoryItem(h, uri, li, False)
			xbmcplugin.endOfDirectory(h)


def getfilms(params):
	showAltTitle = __settings__.getSetting("Show alt title") == "true"
	showQuality = __settings__.getSetting("Show quality") == "true"

	try:
		name = urllib.unquote_plus(params['name'])
	except:
		name = ''

	try:
		page = int(params['page'])
	except:
		page = 1

	target = urllib.unquote_plus(params['href']) + '%d/'%page

	try:
		http = GET(target, urllib.unquote_plus(params['referer']))
		if http == None: return False
	except: return False

	s1 = re.compile('(<div id="mainfilm\d*"\s*[^>]*>.*?</div>)', re.DOTALL).findall(http)
	if len(s1) == 0:
		showMessage('ОШИБКА ДИЗАЙНА', 'Нет <div id="mainfilm">.*?</div>', 3000)
		return False

	headers['Referer'] = target
	happend = '|%s' % urllib.urlencode(headers)

	titleRegexp = re.compile('<h2><a href="(.*?)" title=".*?" class="tfilm">(.*?)</a>')
	iconRegexp = re.compile('<img src="(.*?)" alt=".*?".+?></a>')
	altNameQualityRegexp = re.compile('<font size="1">(.*?) \((.*?)\)')
	genreYearRegexp = re.compile('<font size="1">(.*?)\. (.*?) год\.')
	ratingRegex = re.compile('<img src=".*?" title="(.*?)/10">')
	plotRegexp = re.compile('<div id="mainfilm2">(.*?)</div>')
	downloadCountRegexp = re.compile('Скачали: (\d+)')
	for curli in s1:

		try:
			(nhref, ntitle) = titleRegexp.findall(curli)[0]
			nhref  = httpSiteUrl + nhref
			ntitle = strip_html(ntitle).decode("utf-8")
		except:
			nhref  = None
			ntitle = None

		try:
			img1 = iconRegexp.findall(curli)[0]
			thumb = httpSiteUrl + img1.replace('_60x90','_650x') + happend
		except:
			thumb = icon

		try:
			(altTitle, quality) = altNameQualityRegexp.findall(curli)[0]
			if(showAltTitle and altTitle):
				ntitle += "/" + strip_html(altTitle)
			if(showQuality and quality):
				ntitle += " [" + quality + "]"
		except:
			altTitle = None
			quality = None

		try:
			(genre, year) = genreYearRegexp.findall(curli)[0]
			if(year):
				year = int(year)				
		except:
			genre = None
			year = None

		try:
			rating = ratingRegex.findall(curli)[0]
			if(rating):
				rating = float(rating)
		except:
			rating = None
		
		try:
			downloaded = downloadCountRegexp.findall(curli)[0]
		except:
			downloaded = None

		try:
			plot = strip_html(plotRegexp.findall(curli)[0])
		except:
			plot  = strip_html(curli)

		if (nhref != None) and (ntitle != None):
			uri = sys.argv[0] + '?mode=play'
			uri += '&href='+urllib.quote_plus(nhref)
			uri += '&referer='+target
			item = xbmcgui.ListItem(ntitle, iconImage=thumb, thumbnailImage=thumb)
			item.setInfo(type='video', infoLabels={'title':ntitle,'genre':genre,'plot':plot,'year':year,'rating':rating,'votes':downloaded})			
			item.setProperty('IsPlayable', 'true')
			xbmcplugin.addDirectoryItem(h,uri,item)

	if name:
		page += 1
		li = xbmcgui.ListItem('Далее, на страницу %d >' % page, iconImage = icon, thumbnailImage = icon)
		uri = sys.argv[0] + '?mode=getfilms'
		uri += '&href='+params['href']
		uri += '&name='+params['name']
		uri += '&referer='+target
		uri += '&page=%d'%page
		xbmcplugin.addDirectoryItem(h, uri, li, True)


	xbmcplugin.endOfDirectory(h)


def play(params):
	target  = urllib.unquote_plus(params['href'])
	referer = urllib.unquote_plus(params['referer'])
	http = GET(target, referer)
	u = re.compile('<a  href="(.*?)".*?class="download" id="migalka" >.*?</a>', re.DOTALL).findall(http)[0]
	headers['Referer'] = referer
	i = xbmcgui.ListItem(path = '%s|%s' % (u, urllib.urlencode(headers)))
	i.setProperty('mimetype', 'video/x-msvideo')
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

params = get_params(sys.argv[2])

mode   = None
func   = None

try:
	mode = urllib.unquote_plus(params['mode'])
except:
	getitems(params)

if (mode != None):
	try:
		func = globals()[mode]
	except:
		pass
	if func: func(params)
