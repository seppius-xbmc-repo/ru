#!/usr/bin/python
# -*- coding: utf-8 -*-
#/*
# *      Copyright (C) 2014 by Andrejs Semovs <andrejs.semovs|at|gmail.com>
# *      Copyright (C) 2015 by tolin
# *
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
import urllib2, re, xbmc, xbmcgui, xbmcplugin, os, urllib, urllib2, socket, math, operator, base64

try:
    import json
except ImportError:
    import simplejson as json

socket.setdefaulttimeout(12)

h = int(sys.argv[1])
#icon = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'icon.png'))
#path     = xbmc.translatePath(xbmcaddon.Addon(id='plugin.video.filmix.net').getAddonInfo('path') )
icon = xbmc.translatePath('icon.png')
siteUrl = 'serialu.net'
httpSiteUrl = 'http://' + siteUrl

def showMessage(heading, message, times = 5000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))

def GET(url):
	try:
		print 'def GET(%s):'%url
		req = urllib2.Request(url)
		f = urllib2.urlopen(req)
		a = f.read()
		f.close()
		return a
	except:
		showMessage('Не могу открыть URL def GET', url)
		return None
	    
def GETSER(url):
	http = GET(urllib.unquote_plus(params['url']))

	rows2 = re.compile("pl=(.*?)&#038;vast").findall(http)
	url = DEC(rows2[0])
	
	img = re.compile('src="(.*?)" class="m_pic"').findall(http)
	img = img[0]
	url += '&img=%s'%urllib.quote_plus(img)
	
	
	return url



def ROOT():


	name='Поиск'
        li = xbmcgui.ListItem(name)
        url = sys.argv[0] + '?mode=search'
        xbmcplugin.addDirectoryItem(h, url, li, True)
	
	
	http = GET(httpSiteUrl)
	if http == None: return False
	r1 = re.compile('<ul class="h-menu2">(.*?)</ul>',re.S).findall(http)
	r2 = re.compile('<li><a href="(.*?)">(.*?)</a></li>',re.S).findall(r1[0])
	if len(r2) == 0:
		showMessage('ПОКАЗАТЬ НЕЧЕГО', 'Нет элементов')
		return False
	for href, name in r2:
#		i = xbmcgui.ListItem(unicode(name, "cp1251"), iconImage=icon, thumbnailImage=icon)
		i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
		u  = sys.argv[0] + '?mode=top1'
		u += '&url=%s'%urllib.quote_plus(href)
#		u += '&name=%s'%urllib.quote_plus(name)
		xbmcplugin.addDirectoryItem(h, u, i, True)
        		
	xbmcplugin.endOfDirectory(h)
	

def top1(params):
	href = urllib.unquote_plus(params['url'])

        name='По добавлению'
        l = xbmcgui.ListItem(name)
        u = sys.argv[0] + '?mode=top_view'
	u += '&url=%s'%urllib.quote_plus(href)
        xbmcplugin.addDirectoryItem(h, u, l, True)
        
        name='Все от А до Я'
        l = xbmcgui.ListItem(name)
        u = sys.argv[0] + '?mode=top_view1'
	u += '&url=%s'%urllib.quote_plus(href)
        xbmcplugin.addDirectoryItem(h, u, l, True)
	
	xbmcplugin.endOfDirectory(h)



def top_view1(params):

	http = GET(urllib.unquote_plus(params['url']))
	if http == None: return False
#	showMessage('root3 url', params['url'])
	rs0 = re.compile('<div id="leftcolumn">(.*?)<div class="ls2"><div class="ls-h1">', re.DOTALL).findall(http)
#	r1 = re.compile('<li><a href="(.*?)">(.*?)</a></li>').findall(http)
#    rs0 = re.compile('<ul class="catalog">(.*?)<div class="sidebar" id="sideLeft">', re.DOTALL).findall(http)
#	rs = re.compile('<div class="full-link"><a href="(.+?)" class="showfull">(.+?)</a></div>\s*<div class="letter">(.+?)</div>').findall(rs0[0])
#	rs1 = re.compile('<li><a href="(.*?)">.*?</a></li>').findall(rs0[0])
	rs1 = re.compile('href="(.*?)">(.*?)</a><br/>').findall(rs0[0])
#	rs2 = re.compile('<div class="letter">(.*?)</div>').findall(rs0[0])
	io = 0
	if len(rs1) == 0:
		showMessage('ПОКАЗАТЬ НЕЧЕГО', 'Нет элементов id,name,link,numberOfMovies')
		return False
	for href, name in rs1:
#		name = rs2[io]
#		io = io + 1
		i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
#		i = xbmcgui.ListItem(unicode(name, "cp1251") + ' ' + unicode(name1, "cp1251"), iconImage=icon, thumbnailImage=icon)
#		i = xbmcgui.ListItem(name + ' ' + name1, iconImage=icon, thumbnailImage=icon)
		u  = sys.argv[0] + '?mode=OPEN_SER'
		u += '&url=%s'%urllib.quote_plus('http://serialu.net' + href)
#		u += '&url=%s'%urllib.quote_plus(href)
		u += '&name=%s'%urllib.quote_plus(name)
		xbmcplugin.addDirectoryItem(h, u, i, True)
		#showMessage('root3', u)
	xbmcplugin.endOfDirectory(h)


def top_view(params):
    
	http = GET(urllib.unquote_plus(params['url']))
#	showMessage('ПОКАЗАТЬ НЕЧЕГО', params['url'])
	if http == None: return False
#	rows = re.compile('<a href="(.+?)"><img src="(.+?)" alt="(.+?)" /></a>').findall(http)
	r1 = re.compile('<div id="maincontainer">(.*?)<div id="leftcolumn">',re.S).findall(http)
	r2 = re.compile('<h2><a href="(.*?)" rel="bookmark" title=".*?">(.*?)</a></h2>',re.S).findall(r1[0])
	r3 = re.compile('align="left" src="(.*?)"').findall(r1[0])
	r3 = re.compile('<p><img alt=".*?" align="left" src="(.*?)" class="m_pic" /></p>',re.I).findall(r1[0])
#	r4 = re.compile('<br />(.*?)</div>',re.S).findall(r1[0])
	
	if len(r2) == 0:
		showMessage('ПОКАЗАТЬ НЕЧЕГО', 'Нет элементов href, img, alt')
		return False
	ii = 0
#	name='[B][COLOR blue]Жанры[/COLOR][/B]'
#        li = xbmcgui.ListItem(name)
#        url = sys.argv[0] + '?mode=genre'
#        xbmcplugin.addDirectoryItem(h, url, li, True)
	for href, alt in r2:
#			img = 'http://filmix.net' + r3[ii]
#			if len(r3[ii]) == 0:
#			    img = icon
#			else:
#			    img = r3[ii]
			    
			img = icon
#			text = r4[ii]
			ii = ii + 1
#			i = xbmcgui.ListItem(unicode(alt, "cp1251"), iconImage=img, thumbnailImage=img)
#			i.setInfo(type='video', infoLabels={'title': unicode(alt, "cp1251"), 'plot': unicode(text, "cp1251")})
			i = xbmcgui.ListItem(alt, iconImage=img, thumbnailImage=img)
#			i.setInfo(type='video', infoLabels={'title': alt, 'plot': text})
			u  = sys.argv[0] + '?mode=OPEN_SER'
			u += '&url=%s'%urllib.quote_plus(href)
			#i.setProperty('IsPlayable', 'true')
			xbmcplugin.addDirectoryItem(h, u, i, True)
	try:
		rp = re.compile('<div class="wp-pagenavi">(.*?)<div class="clear"></div>', re.DOTALL).findall(r1[0])
		rp2 = re.compile('<a href="(.*?)" title=".*?">(.*?)</a>').findall(rp[0])
		for href, nr in rp2:
			u = sys.argv[0] + '?mode=top_view'
			u += '&url=%s'%urllib.quote_plus(href)
			nr = '[B][COLOR yellow]%s[/COLOR][/B]' % nr
			i = xbmcgui.ListItem('[ Страница %s ]'%nr)
			xbmcplugin.addDirectoryItem(h, u, i, True)
	except:
		pass
	xbmcplugin.endOfDirectory(h)


    
def search():
	
	skbd = xbmc.Keyboard()
	skbd.setHeading('Название фильма или часть названия')
	skbd.doModal()

	SearchString = skbd.getText(0)
	url = httpSiteUrl+'/?s='+ SearchString
	
	http = GET(url)
	if http == None: return False
#	rows = re.compile('<a href="(.+?)"><img src="(.+?)" alt="(.+?)" /></a>').findall(http)
	r1 = re.compile('<div id="maincontainer">(.*?)<div id="leftcolumn">',re.S).findall(http)
	r2 = re.compile('<h2><a href="(.*?)" rel="bookmark" title=".*?">(.*?)</a></h2>',re.S).findall(r1[0])
	r3 = re.compile('align="left" src="(.*?)"').findall(r1[0])
	r3 = re.compile('<p><img alt=".*?" align="left" src="(.*?)" class="m_pic" /></p>',re.I).findall(r1[0])
#	r4 = re.compile('<br />(.*?)</div>',re.S).findall(r1[0])
	
	if len(r2) == 0:
		showMessage('ПОКАЗАТЬ НЕЧЕГО', 'Нет элементов href, img, alt')
		return False
	ii = 0
#	name='[B][COLOR blue]Жанры[/COLOR][/B]'
#        li = xbmcgui.ListItem(name)
#        url = sys.argv[0] + '?mode=genre'
#        xbmcplugin.addDirectoryItem(h, url, li, True)
	for href, alt in r2:
#			img = 'http://filmix.net' + r3[ii]
#			if len(r3[ii]) == 0:
#			    img = icon
#			else:
#			    img = r3[ii]
			    
			img = icon
#			text = r4[ii]
			ii = ii + 1
#			i = xbmcgui.ListItem(unicode(alt, "cp1251"), iconImage=img, thumbnailImage=img)
#			i.setInfo(type='video', infoLabels={'title': unicode(alt, "cp1251"), 'plot': unicode(text, "cp1251")})
			i = xbmcgui.ListItem(alt, iconImage=img, thumbnailImage=img)
#			i.setInfo(type='video', infoLabels={'title': alt, 'plot': text})
			u  = sys.argv[0] + '?mode=OPEN_SER'
			u += '&url=%s'%urllib.quote_plus(href)
			#i.setProperty('IsPlayable', 'true')
			xbmcplugin.addDirectoryItem(h, u, i, True)
	try:
		rp = re.compile('<div class="wp-pagenavi">(.*?)<div class="clear"></div>', re.DOTALL).findall(r1[0])
		rp2 = re.compile('<a href="(.*?)" title=".*?">(.*?)</a>').findall(rp[0])
		for href, nr in rp2:
			u = sys.argv[0] + '?mode=top_view'
			u += '&url=%s'%urllib.quote_plus(href)
			nr = '[B][COLOR yellow]%s[/COLOR][/B]' % nr
			i = xbmcgui.ListItem('[ Страница %s ]'%nr)
			xbmcplugin.addDirectoryItem(h, u, i, True)
	except:
		pass
	xbmcplugin.endOfDirectory(h)
	


def DEC(param):
    
    hash1 = ("0","5","u","w","6","n","H","o","B","p","N","M","D","R","z","G","V","e","i","3","m","W","U","7","g","=");
    hash2 = ("c","T","I","4","Q","Z","v","Y","y","X","k","b","8","a","J","d","1","x","L","t","l","2","f","s","9","h");

    for i in range(0, len(hash1)):
        rr1 = hash1[i]
        rr2 = hash2[i]

        param = param.replace(rr1, '--')
        param = param.replace(rr2, rr1)
        param = param.replace('--', rr2)
	
    
    param = base64.b64decode(param)
    
    return param


# Parse given movie url into a list of urls with quality info
def PARSE_MOVIE_URL(url):
	result = []
	rqlt = r"\[([0-9,]*)\]"
	quality = re.compile(rqlt).findall(url)

	if quality is None or len(quality) == 0:
		result.append({'url': url, 'definition': '', 'quality': ''})

	else:
		# trim leading , if any and split into list
	    quality = quality[0].strip(',').split(',')

	    # cycle through available qualities
	    for bps in quality:
	    	# prepare url with given bps
	        parsed_url = re.sub(rqlt, bps, url)

	        # generate SD or HD string for menu title
	        suffix = 'SD' if int(bps) < 720 else 'HD'

	        # populate result with parsed url, definition and quality
	        result.append({'url': parsed_url, 'definition': suffix, 'quality': bps})

	return result


# Open movie list, that is passed in 'urls' parameter (mostly used to show different qualities of a movie)
def OPEN_MOVIE_URLS(params):
	urls = json.loads(urllib.unquote_plus(params['urls']))
#	showMessage('urls', urls)
	# notify if no urls are found
	if len(urls) == 0:
		showMessage('ПОКАЗАТЬ НЕЧЕГО', 'Нет элементов urls')
		return False

	# otherwise output all quality urls
	for url in urls:

		# show definition and bps
		if 'quality' in url and len(url['quality']):
			title = url['definition'] + ' ' + url['quality']
		# otherwise just use plain video file name
		else:
			title = os.path.basename(url['url'])

		i = xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=icon)
		i.setProperty('IsPlayable', 'true')
		xbmcplugin.addDirectoryItem(h, url['url'], i)

	xbmcplugin.endOfDirectory(h)


# Open serial movie list
def OPEN_SER(params):
    http = GET(urllib.unquote_plus(params['url']))
    
    r1 = re.compile('<div class="content">(.*?)/></p>',re.S).findall(http)
    
    rows2 = re.compile("pl=(.*?)&#038;vast").findall(http)
    url = DEC(rows2[0])
    
    img = re.compile('align="left" src="(.*?)"').findall(http)

    img = img[0]

    if url is None:
    	showMessage('ПОКАЗАТЬ НЕЧЕГО', 'Ссылка на видео файл не обнаружена', 5000)
    	return False

    # get and decode filmix playlist
    js = DEC(GET(urllib.unquote_plus(url)))

    # exit if no data received
    if js == None: return False

    # parse playlist JSON
    playlist = json.loads(js)

    # exit, if playlist empty
    if len(playlist) == 0:
    	showMessage('ПОКАЗАТЬ НЕЧЕГО', 'Нет элементов')
        return False

    # if season level is not found, create it
    if 'file' in playlist['playlist'][0]:
    	playlist = { 'playlist': [ playlist ] }

    # loop through playlist data
    for season in playlist['playlist']:
        for episode in season['playlist']:
#			urls = PARSE_MOVIE_URL(episode['file'])
			urls = episode['file']
			# if multiple video qualities are found, add folder link
			if len(urls) > 1:
#				u  = sys.argv[0] + '?mode=OPEN_MOVIE_URLS'
#				u += '&urls=%s' % urllib.quote_plus(json.dumps(urls))
				url = DEC(urls)
				i = xbmcgui.ListItem(episode['comment'], iconImage=img, thumbnailImage=img)
				i.setProperty('IsPlayable', 'true')
				xbmcplugin.addDirectoryItem(h, url, i)
#				xbmcplugin.addDirectoryItem(h, url, i, True)
	try:
#		rp = re.compile('<div class="wp-pagenavi">(.*?)<div class="clear"></div>', re.DOTALL).findall(r1[0])
		rp2 = re.compile('<a href="(.*?)">(.*?)</a>').findall(r1[0])
		for href, nr in rp2:
			u = sys.argv[0] + '?mode=OPEN_SER'
			u += '&url=%s'%urllib.quote_plus(href)
			nr = '[B][COLOR yellow]%s[/COLOR][/B]' % nr
			i = xbmcgui.ListItem(nr)
			xbmcplugin.addDirectoryItem(h, u, i, True)
	except:
		pass

			# otherwise add direct link to video
#			else:
#				for url in urls:
#					title = episode['comment']
#
#					# add quality info to title if available
#					if url['quality'] is not None and len(url['quality']):
#						title += ' - ' + url['definition'] + ' ' + url['quality']
#		
#					i = xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=icon)
#					i.setProperty('IsPlayable', 'true')
#					xbmcplugin.addDirectoryItem(h, url['url'], i)

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

try:
	mode = urllib.unquote_plus(params['mode'])
except:
	ROOT()

if mode == 'OPEN_MOVIES': OPEN_MOVIES(params)

if mode == 'OPEN_SER': OPEN_SER(params)

if mode == 'ROOT4': ROOT4()
	
if mode == 'OPEN_MOVIES2': OPEN_MOVIES2(params)
	
if mode == 'OPEN_MOVIES3': OPEN_MOVIES3(params)
	
if mode == 'OPEN_MOVIES4': OPEN_MOVIES4(params)

if mode == 'OPEN_MOVIE_URLS': OPEN_MOVIE_URLS(params)

if mode == 'ROOT3': ROOT3()

if mode == 'video_sub': video_sub()
if mode == 'serial_sub': serial_sub()
if mode == 'search': search()
if mode == 'genre': genre()
if mode == 'top1': top1(params)
if mode == 'top_view1': top_view1(params)
if mode == 'top_view': top_view(params)
if mode == 'PLAY': PLAY(params)
	
if mode == 'PLAY1': PLAY1(params)



