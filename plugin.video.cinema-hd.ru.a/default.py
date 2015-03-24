#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib, urllib2
import sys, os, re, json, random, urlparse
import xbmc, xbmcgui, xbmcplugin, xbmcaddon

from bs4 import BeautifulSoup as bs
#from bs4.diagnose import diagnose


Addon = xbmcaddon.Addon(id = 'plugin.video.cinema-hd.ru.a')

addon_icon    = Addon.getAddonInfo('icon')
addon_fanart  = Addon.getAddonInfo('fanart')
addon_path    = Addon.getAddonInfo('path')
addon_id      = Addon.getAddonInfo('id')
addon_author  = Addon.getAddonInfo('author')
addon_name    = Addon.getAddonInfo('name')
addon_version = Addon.getAddonInfo('version')

#Get XBMC version
xbmcver = xbmc.getInfoLabel("System.BuildVersion").split()[0].split('-')[0]
xbmcver = float(xbmcver)

UA = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0'

use_translit = Addon.getSetting('use_translit') == 'true'
debug_mode = Addon.getSetting("debug_mode") == 'true'
use_ahds = Addon.getSetting("use_ahds") == 'true'

def ShowMessage(heading, message, times = 6000):
	xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % (heading, message, times))

if use_translit:
	try:  
		import Translit as translit
		translit = translit.Translit()  
	except:
		use_translit = False
		print 'Поиск в транслит выключен: не установлен script.module.translit' 
		#ShowMessage(addon_name, 'Поиск в translit не доступен: не установлен script.module.translit')

if use_ahds:
	if xbmc.getCondVisibility('System.HasAddon(script.video.F4mProxy)') == 0:
		use_ahds = False
		print 'Воспроизведение Adobe HDS видео формата выключено: не установлен script.video.F4mProxy' 
		#ShowMessage(addon_name, 'Воспроизведение Adobe HDS видео формата выключено: не установлен script.video.F4mProxy')

try:
	sys.path.append(os.path.join(os.path.dirname(__file__), "../plugin.video.unified.search"))
	from unified_search import UnifiedSearch
except: pass


def get_params(paramstring):
	params = []
	if len(paramstring) >= 2:
		params = {}
		if '?' in paramstring: qindex = paramstring.index('?')
		else: qindex = -1 
		cleanedparams = paramstring[qindex + 1:]
		pairsofparams = cleanedparams.split('&')
		for i in range(len(pairsofparams)):
			splitparams = {}
			splitparams = pairsofparams[i].split('=')
			if (len(splitparams)) == 2:
				params[splitparams[0]] = splitparams[1]
	if len(params) > 0:
		for p in params:
			params[p] = urllib.unquote_plus(params[p])
	return params

def GET(url, ref = None, opts = '', post = None):
	req = urllib2.Request(url, data = post)
	req.add_header('User-Agent', UA)
	print "GET: " + url
	if ref: req.add_header('Referer', ref)
	if 'xmlhttp' in opts:
		req.add_header('X-Requested-With', 'XMLHttpRequest')
	if 'timeout' in opts: timeout = 0.2
	else: timeout = 5
	try:
		response = urllib2.urlopen(req, timeout = timeout)
		html = response.read()
		if 'headers' in opts: headers = response.info()
		else: headers = None
		response.close()
		if headers: result = (html, headers)
		else: result = html
		return result
	except Exception, e:
		print 'GET: Error getting page ' + url + ' (' + str(e) + ')'
		ShowMessage('HTTP error', 'Error getting page: ' + url)
		return None

def construct_request(params):
	return '%s?%s' % (sys.argv[0], urllib.urlencode(params))

def clean_html(page, opts = None):
	page = page.replace('<br />','').replace(';="" ','').replace('</scr"+"ipt>','</script>')
	if opts:
		if 'ext' in opts:
			r1 = re.compile(r'<meta name="description".*?/>', flags = re.S)
			r2 = re.compile(r'<meta itemprop="description".*?>$', flags = re.M)
			page = r1.sub('', page, count = 1)
			page = r2.sub('', page, count = 1)
	return page

def IsIPv4(url):
	import socket
	try: 
		#print socket.getaddrinfo(sr[1], 80)
		socket.gethostbyname(url)
		return True
	except: return False

def touch(url):
	req = urllib2.Request(url)
	try:
		res = urllib2.urlopen(req)
		res.close()
		return True
	except:
		return False

def removed_message_special_conditions(tag):
	return tag.name == 'span' and tag.parent.name == 'b'

def video_conditions(tag):
	if tag.name == 'embed':
		try:
			if tag['allowscriptaccess'] == "always" and tag['wmode'] == "opaque":
				print "Layout B"
				return True
		except: return False
	elif tag.name == 'iframe':
		if re.search('(megogo.net|g-tv.ru)', tag['src']): return False
		return True
	else: return False

def ocb_seasons_conditions(tag):
	try:
		if tag.name == 'select':
			#print tag
			#print tag.previous_sibling.string.encode('utf-8')
			if u'Сезон' in tag.previous_sibling.string: return True
	except Exception, e:
		pass
	return False

def ocb_episodes_conditions(tag):
	try:
		if tag.name == 'select' and u'Серия' in tag.previous_sibling.string: return True
	except: pass
	return False

def Search(params):
	mode = params['mode'] if 'mode' in params else None
	kbd = xbmc.Keyboard()
	#kbd.setDefault('')
	if mode == 'clips': kbd.setHeading("Поиск по клипам")
	else: kbd.setHeading("Поиск")
	kbd.doModal()
	uri = {}
	if kbd.isConfirmed():
		query = kbd.getText()
		if use_translit:
			query = translit.rus(query)
			print 'detransified search query: ' + query
		query = urllib.quote_plus(query)
	else: return True
	if mode == 'clips': uri['url'] = '/load/'
	else: uri['url'] = '/board'
	uri['post'] = 'query=%s&a=2' % query
	uri['mode'] = 'search'
	ListCat(uri)


def Main(params):
	listitem = xbmcgui.ListItem('<ПОИСК>', thumbnailImage = addon_icon)
	uri = construct_request({
		'func': 'Search'
		})
	xbmcplugin.addDirectoryItem(hos, uri, listitem, True)

	listitem=xbmcgui.ListItem('Новое', iconImage = addon_icon)
	uri = construct_request({
		'func': 'ListCat',
		'url': '/board/0-1'
		})
	xbmcplugin.addDirectoryItem(hos, uri, listitem, True)

	http = GET('http://cinema-hd.ru/')
	if http == None: return False
	soup = bs(http, 'html.parser', from_encoding = "utf-8")
	http = clean_html(http)
	#content = soup.find('ul',attrs={'class':'subs'})
	#content = soup.find('li', attrs = {'class':'cat-menu sub'})
	content = soup.find('nav', class_ = "navigation clearfix")
	content = content.div.find_all('li')
	for num in content:
		title = num.find('a').string #.encode('utf-8')
		url = num.find('a')['href']
		#print url
		title = title.replace(u'Все ', '').replace(u'Вся ', '').replace(u' фильмы', '').strip().capitalize()
		
		listitem = xbmcgui.ListItem(title, iconImage = addon_icon, thumbnailImage = addon_icon)
		uri = construct_request({
			'func': 'ListCat',
			'url': url
			})
		if 'board' in url: xbmcplugin.addDirectoryItem(hos, uri, listitem, True)

	li = xbmcgui.ListItem("Клипы", iconImage = addon_icon, thumbnailImage = addon_icon)
	uri = construct_request({
		'func': 'ListCat',
		'url': "/load/"
		})
	xbmcplugin.addDirectoryItem(hos, uri, li, True)

	xbmcplugin.endOfDirectory(hos)


def ListCat(params):
	pq = int(Addon.getSetting('ipp')) + 1
	mode = params['mode'] if 'mode' in params else None
	if unified:
		params['url'] = '/board'
		params['post'] = 'query=%s&a=2' % params['keyword']
		unified_search_results = []
	blink = 'http://cinema-hd.ru' + params['url'] #base
	post = params['post'] if 'post' in params else None
	if mode == 'search':
		searchmode = True
		pq = 1
	else:
		searchmode = False
	innerpage = int(params['page']) if 'page' in params else 1

	if '/load/' in blink and innerpage == 1 and not searchmode:
		li = xbmcgui.ListItem('<Поиск клипов>', thumbnailImage = addon_icon)
		uri = construct_request({
			'func': 'Search',
			'mode': 'clips'
			})
		xbmcplugin.addDirectoryItem(hos, uri, li, True)
	
	for page in range((innerpage - 1) * pq + 1, innerpage * pq + 1):
		if page > 1:
			if re.search('board/0-1', blink): url = blink.replace('1', str(page)) #"Новое"
			elif re.search('/load/', blink): url = blink + '0-' + str(page) #Клипы
			else: url = blink + '-' + str(page) + '-2'
		else: url = blink
		http = GET(url, post = post)
		if not http: break
		http = clean_html(http)
		soup = bs(http, 'html.parser', from_encoding = 'utf-8')
		content = soup.find_all('div', attrs = {'id': re.compile('entryID[0-9]+')})
		for item in content:
			#sdata = item.find('a', href=re.compile('http://cinema-hd.ru/board/.+'))
			data = item.find('a')
			#print data
			link = data['href']
			#title = data.find('h2').string.encode('utf-8')
			title = data.string.encode('utf-8')
			#print title
			#img = item.find('img', width='250')['src']
			img = item.find('img')['src']
			#data1 = item.find_all('span', style = "font-family:'Georgia'")
			data1 = item.find('div', class_ = 'item-info inline')
			#print [i for i in data1]
			try:
				genredata = data1.p
				plotdata = data1.div
				genre = ' '.join(genredata.stripped_strings).encode('utf-8')
				plot = ' '.join(plotdata.stripped_strings).encode('utf-8')
			except:
				genre = plot = ''
			uri = construct_request({
				'func': 'ListSeries',
				'url': link,
				'title': title,
				'image': img
				})
			if unified:
				print addon_id, uri
				usurl = re.compile(addon_id + '(.+)$').findall(uri)[0]
				uspath = {
					'title': title,
					'url': urllib.quote_plus(usurl),
					'image': img,
					'plugin': addon_id
					 }
				unified_search_results.append(uspath)
			else:
				li = xbmcgui.ListItem(title, iconImage = img, thumbnailImage = img)
				li.setInfo(type = "video", infoLabels = {"title": title, "plot": plot, "genre": genre})
				#listitem.setProperty('IsPlayable', 'true')
				xbmcplugin.addDirectoryItem(hos, uri, li, True)
   
	if not searchmode:
		linp = xbmcgui.ListItem('< Следующая страница >', iconImage = addon_icon, thumbnailImage = addon_icon)
		uri = construct_request({
			'func': 'ListCat',
			'page': innerpage + 1,
			'url': params['url']
			})
		xbmcplugin.addDirectoryItem(hos, uri, linp, True)
	if unified:
		UnifiedSearch().collect(unified_search_results)
		return True
	xbmcplugin.setContent(hos, 'movies')
	xbmcplugin.endOfDirectory(hos)


def ListSeries(params):
	prtitle = ''; infoSet = {}; layout_marks = []; vhost_marks = []
	common_list = ['ФИЛЬМ', 'СМОТРЕТЬ', 'ТЕЛЕШОУ']
	common_titles_list = ['фильм', 'Фильм', 'документальный фильм', 'мультфильм', 'Телешоу', 'Концерт']

	http = GET(params['url'])
	http = clean_html(http, 'ext')

	#diagnose(http.decode('utf-8').encode('ascii','replace'))
	try: soup = bs(http, 'html5lib', from_encoding = "utf-8")
	except Exception, e:
		print "BS load error: " + str(e)
		ShowMessage(addon_name, "BS error")
		return True
	#print soup.prettify('utf-8')
	content = soup.find('div', class_ = 'full-item')
	#print content.prettify('utf-8')
	if not content:
		print "Content container is not found, used uncut html"
		content = soup
	try: 
		videos = content.find_all(video_conditions)
	except Exception, e:
		print "BS exception: " + str(e)
		ShowMessage(addon_name, "Exception in BS module")
		return True

	if len(videos) == 0:
		removedmes = content.find(removed_message_special_conditions, attrs = {"style": "color:red"})
		if removedmes:
			ShowMessage(addon_name, removedmes.string.encode('utf-8'), times = 45000)
			return True
		else:
			print "Failed to parse"
			ShowMessage(addon_name, "Неизвестный тип верстки")
			return True
	#print videos

	#plot = content.find('span', itemprop = "description")
	try: plot = content.find('div', class_ = "item-info inline")
	except Exception, e: print str(e)
	if plot:
		try:
			imdata = plot.find_parent('div', class_ = 'full-item-content')
			plot = ' '.join(plot.stripped_strings).encode('utf-8')
			infoSet['plot'] = plot
			#imdata = imdata.find('a', target = "_blank", class_ = "ulightbox")
			imdata = imdata.find('img', itemprop = "image")
			img = imdata['src']
			#print img
		except Exception, e:
			print str(e)
			img = params['image']
	else:
		img = params['image']

	#Metadata
	try:
		metadata = content.find('ul', class_ = 'film-tech-info')
		director = metadata.find('strong', itemprop = "director").next_sibling.strip().encode('utf-8')
		genre = content.find('span', itemprop = "genre").string.strip().encode('utf-8')
		actors = content.find('strong', itemprop = "actor").next_sibling.strip().encode('utf-8').split(', ')
		year = content.find('strong', itemprop = "dateCreated").next_sibling.encode('utf-8')
		infoSet.update({
			'genre': genre,
			'year': int(year),
			'director': director,
			'cast': actors
			})
	except Exception, e: print e

	#Fanart
	fanartcontlist = content.find_all('a', attrs = {"class": "ulightbox", "data-fancybox-group": "screenshots"})
	if fanartcontlist: fanartlist = [i['href'] for i in fanartcontlist]
	else: fanartlist = None
	#print fanartlist


	for iframe in videos:
		#Layout 1
		title = iframe.find_previous_sibling('span', style = re.compile("color\:.?(#ff9900|orange|yellow)"))
		if title:
			#print "Layout 1"
			layout_marks.append('1')
		#Layout 2
		if not title:
			title = iframe.find_parent('span', style = re.compile("color\:.?(#ff9900|orange|yellow)"))
			if title:
				#print "Layout 2"
				layout_marks.append('2')
		#Layout 3
		if not title:
			title = iframe.find_previous('font', color = "ff9900")
			if title: 
				titlecont = list(title.stripped_strings)
				if len(titlecont) == 0:
					title = title.find_previous('font', color = "ff9900")
					if title:
						#print "Layout 3b"
						layout_marks.append('3b')
				elif not title.font:
					#print "Layout 3"
					layout_marks.append('3')
			#Layout 3a
			if title and title.font:
				titlecontalt = list(title.stripped_strings)
				title.font.decompose()
				titlecont = list(title.stripped_strings)
				if len(titlecont) == 0:
					if len(titlecontalt) > 0:
						title = titlecontalt[0].encode('utf-8')
						#print "Layout 3a1"
						layout_marks.append('3a1')
					else: title = None
				else:
					#print "Layout 3a"
					layout_marks.append('3a')
		#Layout 4
		if not title:
			title = iframe.find_previous('span', style = re.compile("color\:.?(#ff9900|orange|yellow)"))
			#print title
			#print str(type(title.contents[0]))
			if title and str(type(title.contents[0])) == "<class 'bs4.element.Tag'>":
				#if title.contents[0].has_attr('style') and title.contents[0]['style']=='font-size:13pt':
				title = None
			else:
				if title:
					#print "Layout 4"
					layout_marks.append('4')

		#print type(title)
		if str(type(title)) == "<class 'bs4.element.Tag'>":
			titlecont = list(title.stripped_strings)
			title = titlecont[0].encode('utf-8')

		#Layout 5
		if not title or title in common_titles_list:
			title = content.find('meta', itemprop = "name")
			if title:
				title = title['content'].encode('utf-8')
				#print "Layout 5"
				layout_marks.append('5')

		#Layout N
		if not title:
			title = params['title']
			#print "Layout N"
			layout_marks.append('N')

		for common in common_list:
			if title and common in title:
				title = title.replace(common, '',  1).strip()

		#don't add trailer with the same name
		#if len(videos) == 2 and title == prtitle: break
		prtitle = title

		#print title, url
		#if title == 'трейлер' or title == 'Трейлер': continue

		url = iframe['src']
		if debug_mode:
			vhost_marks.append(re.findall(r'(?:www\.)?(?:[\w\-]+\.)*([\w\-]+)\.\w+/', url)[0])

		'''if 'moonwalk.cc/serial' in url:
			ListMWSeasons(url, params['url'])
			continue'''
		
		'''if 'online-cinema.biz' in url:
			ListOCBSeries(url)
			continue'''

		li = xbmcgui.ListItem(title, iconImage = addon_icon, thumbnailImage = img)
		li.setInfo(type = "video", infoLabels = infoSet)
		if fanartlist:
			fanart = random.choice(fanartlist)
			if xbmcver >= 13: li.setArt({'fanart': fanart})
			else: li.setProperty('fanart_image', fanart)
		IF = False; IP = True
		uri = {'url': url};
		if 'moonwalk.cc/serial' in url:
			uri['func'] = 'ListMWSeasons'
			uri['ref'] = params['url']
			IF = True; IP = False
		else:
			uri['func'] = 'Play'
		if 'moonwalk.cc/video' in url and use_ahds:
			IP = False
		uri = construct_request(uri)
		if IP: li.setProperty('IsPlayable', 'true')
		xbmcplugin.addDirectoryItem(hos, uri, li, IF)
	
	if debug_mode:
		ShowMessage(addon_name, "[COLOR bisque]" + "-".join(layout_marks) + "[/COLOR] " + ", ".join(vhost_marks), times = 8000)
	
	xbmcplugin.setContent(hos, 'movies')
	#skin = xbmc.getSkinDir()
	#if skin == 'skin.aeonmq5':
	#	print xbmc.getInfoLabel('Container.Viewmode')
	#	xbmc.executebuiltin('Container.SetViewMode(55)')
	xbmcplugin.endOfDirectory(hos)


def ListMWSeasons(params):
	url = params['url']
	ref = params['ref']
	http = GET(url)
	soup = bs(http)
	seasonsdata = soup.find('select', id = 'season')
	seasonsdata1 = seasonsdata.find_all('option')
	seasonslist = [int(i["value"]) for i in seasonsdata1]
	#seasonslist = [int(i["value"]) for i in seasonsdata.contents]
	seasonscount = max(seasonslist)
	for season in seasonslist:
		li = xbmcgui.ListItem("Сезон " + str(season))
		uri = construct_request({
			'func': 'ListMWEpisodes',
			'url': url[0:url.index('?')],
			'season': season,
			'ref': ref
			})
		xbmcplugin.addDirectoryItem(hos, uri, li, True)
	
	xbmcplugin.endOfDirectory(hos)

def ListMWEpisodes(params):
	url = params['url']
	season = params['season']
	ref = params['ref']
	http = GET(url + '?season=' + season + '&referer=' + ref)
	soup = bs(http)
	episodesdata = soup.find('select', id = 'episode')
	episodesdata1 = episodesdata.find_all('option')
	#print episodesdata1
	episodeslist = [int(i["value"]) for i in episodesdata1]
	for episode in episodeslist:
		li = xbmcgui.ListItem("Серия " + str(episode))
		uri = construct_request({
			'func': 'Play',
			'url': url + '?season=' + season + '&episode=' + str(episode)
			})
		if not use_ahds: li.setProperty('IsPlayable', 'true')
		xbmcplugin.addDirectoryItem(hos, uri, li)
	
	xbmcplugin.endOfDirectory(hos)

'''def ListOCBSeries(url):
	http = GET(url)
	soup = bs(http)
	seasonsdata = soup.find(ocb_seasons_conditions)
	seasonsdata1 = seasonsdata.find_all('option')
	seasonslist = [int(i.string) for i in seasonsdata1]
	print seasonslist
	seasonscount = max(seasonslist)
	for season in seasonslist:
		li = xbmcgui.ListItem("Сезон " + str(season))
		uri = construct_request({
			'func': 'ListOCBEpisodes',
			'url': url[0:url.index('?')],
			'season': season
			#'ref': ref
			})
		xbmcplugin.addDirectoryItem(hos, uri, li, True)
	
	xbmcplugin.endOfDirectory(hos)

def ListOCBEpisodes(url):
	http = GET(url)
	soup = bs(http)
	episodesdata = soup.find(ocb_episodes_conditions)
	episodesdata1 = seasonsdata.find_all('option')
	episodeslist = [int(i.string) for i in episodesdata1]
	print episodeslist
	#seasonscount = max(seasonslist)
	for episodr in episodeslist:
		li = xbmcgui.ListItem("Сезон " + str(season))
		uri = construct_request({
			'func': 'ListOCBEpisodes',
			'url': url[0:url.index('?')],
			'season': season
			#'ref': ref
			})
		xbmcplugin.addDirectoryItem(hos, uri, li, True)
	
	xbmcplugin.endOfDirectory(hos)'''

def PlayHDS(link, name = "f4mstream"):
	from F4mProxy import f4mProxyHelper
	player = f4mProxyHelper()
	player.playF4mLink(link, name)


def Play(params):
	url = params['url']
	if url.find('//') == 0: url = url[2:]
	if url.find('http') == -1: url = 'http://' + url
	
	if 'ivi.ru' in url:
		if xbmc.getCondVisibility('System.HasAddon(plugin.video.ivi.ru)') == 0:
			ShowMessage(addon_name, "Для просмотра данного видео необходим плагин ivi.ru")
			return True
		id = re.findall('videoId=(\d+)', url)
		if id:
			id = id[0]
			print "IVI.RU, id = " + str(id)
			link = "plugin://plugin.video.ivi.ru?func=playid&id=" + id
			#xbmc.executebuiltin('XBMC.RunScript(plugin.video.ivi.ru,, ?func=playid&id=%s)' % (id))
		else:
			print "IVI.RU video id is not found, " + url
			return True
	
	else:
		link = GetVideo(url)
		if link == False: return True
	
	if 'moonwalk.cc' in url and use_ahds:
		PlayHDS(link)
	else:
		item = xbmcgui.ListItem(path = link)
		item.setProperty('IsPlayable', 'true')
		xbmcplugin.setResolvedUrl(hos, True, item)


def GetVideo(url):
	if re.search('(vk\.com|vkontakte\.ru)', url):
		http = GET(url)
		soup = bs(http, from_encoding = "windows-1251")
		#sdata1 = soup.find('div', class_ = "scroll_fix_wrap", id = "page_wrap")
		rmdata = soup.find('div', style = "position:absolute; top:50%; text-align:center; right:0pt; left:0pt; font-family:Tahoma; font-size:12px; color:#FFFFFF;")
		if rmdata:
			rmdata = rmdata.find('div', style = False, class_ = False)
			#print rmdata
			if rmdata.br: rmdata.br.replace_with(" ")
			rmdata = "".join(list(rmdata.strings)).strip().encode('utf-8')
			print rmdata
			ShowMessage(addon_name, rmdata, times = 20000)
			return False
		rec = soup.find_all('param', {'name': 'flashvars'})[0]['value']
		fvs = urlparse.parse_qs(rec)
		#print json.dumps(fvs, indent = 1).encode('utf-8')
		uid = fvs['uid'][0]
		vtag = fvs['vtag'][0]
		host = fvs['host'][0]
		#vid = fvs['vid'][0]
		#oid = fvs['oid'][0]
		hd = fvs['hd'][0] if 'hd' in fvs else None
		q_list = {None: '240', '1': '360', '2': '480', '3': '720'}
		burl = host + 'u' + uid + '/videos/' + vtag + '.%s.mp4'
		q_url_map = {q: burl % q for q in q_list.values()}
		print q_url_map
		url = fvs['url' + q_list[hd]][0]
		#url = url.replace('vk.me', 'vk.com')
		sr = urlparse.urlsplit(url)
		if not IsIPv4(sr[1]): url = url.replace('v6', '', 1)
		#print url
		return url
	
	elif 'moonwalk.cc' in url:
		#if xbmcver < 14: ShowMessage(addon_name, "Неизвестный видеохостинг: " + url)
		page = GET(url)
		token = re.findall("video_token: '(.*?)'", page)[0]
		access_key = re.findall("access_key: '(.*?)'", page)[0]
		referer = re.findall(r'player_url = "(.+?\.swf)";', page)[0]
		#print referer
		post = urllib.urlencode({"video_token": token, "access_key": access_key})
		#print post
		page = GET('http://moonwalk.cc/sessions/create_session', post = post, opts = 'xmlhttp', ref = url)
		page = json.loads(page)
		if use_ahds:
			url = page["manifest_f4m"]
		else:
			url = page["manifest_m3u8"]
		
		headers = {'User-Agent': UA, 'Connection': 'Keep-Alive', 'Referer': referer}
		url += '|' + urllib.urlencode(headers)
		#print url
		return url
	
	elif 'rutube.ru' in url:
		data = GET(url)
		#print data
		import HTMLParser
		hp = HTMLParser.HTMLParser()
		data = hp.unescape(data)
		match = re.compile('"m3u8": "(.+?)"').findall(data)
		#print match
		if len(match) > 0:
			url = match[0]
			return url
	
	elif re.search('(api\.video\.mail\.ru|videoapi\.my\.mail\.ru)', url):
		data = GET(url)
		#match = re.compile('videoSrc = "(.+?)",').findall(data)
		match = re.compile('"metadataUrl":"(.+?)"').findall(data)
		if len(match) > 0:
			url = match[0]
		else:
			print "Mail.ru video parser is failed"
			ShowMessage(addon_name, "Mail.ru video parser is failed")
			return False
		data = GET(url, opts = 'headers')
		video_key_c = data[1].getheader('Set-Cookie')
		video_key_c = re.compile('(video_key=.+?;)').findall(video_key_c)
		if len(video_key_c) > 0:
			video_key_c = video_key_c[0]
		else:
			print "Mail.ru video parser is failed"
			ShowMessage(addon_name, "Mail.ru video parser is failed")
			return False
		jsdata = json.loads(data[0])
		vlist = jsdata['videos']
		vlist.sort(key = lambda i: i['key'])
		vdata = vlist[-1]
		url = vdata['url']
		headers = {'Cookie': video_key_c}
		url += '|' + urllib.urlencode(headers)
		return url
	
	elif 'youtube.com' in url:
		try:
			url = get_yt(url)
			print url
		except Exception as ex:
			print ex
		return url
	
	elif 'online-cinema.biz' in url:
		ShowMessage(addon_name, "Неизвестный видеохостинг: " + url)
		html = GET(url)
		url = re.findall('&file=(.+?)"', html)
		if len(url) > 0: url = url[0]
		else:
			print "Parsing is failed: online-cinema.biz"
			ShowMessage(addon_name, "Parsing is failed: online-cinema.biz")
			return False
		return url
	
	else:
		ShowMessage(addon_name, "Неизвестный видеохостинг: " + url)
		print "Неизвестный видеохостинг: " + url
		return False


def get_yt(url):
	if url.find('youtube.com') > -1:
		if url.find('/videoseries?') > -1:
			print "youtube playlist"
			playlist_id=re.findall('list=(.+?)&',url)[0]
			print playlist_id
			info_url = "http://gdata.youtube.com/feeds/api/playlists/%s" % (playlist_id)
			#info_url = "http://www.youtube.com/view_play_list?p=%s" % (playlist_id)
			print info_url
			try:
				infopage = GET(info_url)
				videoinfo = urlparse.parse_qs(infopage)
				#print type(videoinfo)
			except Exception as ex:
				print ex
			jso=videoinfo['app']
			links=[]
			for item in jso:
				#print item
				link=re.findall('media\:player url=\'(.+?)$',item)[0]
				#print link
				if link: links.append(get_yt(link))
			if links: video_url='stack://'+' , '.join(links)
			return video_url
		video_priority_map = {'38' : 1,'37' : 2,'22' : 3,'18' : 4,'35' : 5,'34' : 6,}
		video_url = url
		print url
		try:
			if url.find('youtube') > -1:
				found = False
				finder = url.find('=')
				video_id = url[finder + 1:]
				print video_id
				if url.find('/embed/')>-1:
					#print "embed"
					video_id=re.findall('embed/(.+)\??',url)[0]
					#if video_id=="videoseries": video_id=re.findall('list=(.+?)&',url)[0]
					print video_id
				for el in ['&el=embedded',
				'&el=detailpage',
				'&el=vevo',
				'']:
					info_url = 'http://www.youtube.com/get_video_info?&video_id=%s%s&ps=default&eurl=&gl=US&hl=en' % (video_id, el)
					print info_url
					try:
						infopage = GET(info_url)
						videoinfo = urlparse.parse_qs(infopage)
						print videoinfo
						if ('url_encoded_fmt_stream_map' or 'fmt_url_map') in videoinfo:
							found = True
							if 'use_cipher_signature' in videoinfo and videoinfo['use_cipher_signature'][0]=='True':
								print 'use_cipher_signature: '+ videoinfo['use_cipher_signature'][0]
								ShowMessage('use_cipher_signature:',videoinfo['use_cipher_signature'][0]) #FOR DEBUG
							break
					except Exception as ex:
						print ex

				if found:
					video_fmt_map = {}
					fmt_infomap = {}
					if videoinfo.has_key('url_encoded_fmt_stream_map'):
						tmp_fmtUrlDATA = videoinfo['url_encoded_fmt_stream_map'][0].split(',')
					else:
						tmp_fmtUrlDATA = videoinfo['fmt_url_map'][0].split(',')
					for fmtstring in tmp_fmtUrlDATA:
						fmturl = fmtid = fmtsig = ''
						#print fmtstring.split('&')
						if videoinfo.has_key('url_encoded_fmt_stream_map'):
							try:
								for arg in fmtstring.split('&'):
									print arg #FOR DEBUG
									if arg.find('=') >= 0:
										key, value = arg.split('=')
										if key == 'itag':
											if len(value) > 3:
												value = value[:2]
											fmtid = value
										elif key == 'url':
											fmturl = value
										elif key == 'sig':
											fmtsig = value

								if fmtid != '' and fmturl != '' and video_priority_map.has_key(fmtid):
									video_fmt_map[video_priority_map[fmtid]] = {'fmtid': fmtid,
									'fmturl': urllib.unquote_plus(fmturl)}
									#if fmtsig != '': video_fmt_map[video_priority_map[fmtid]]={'fmtid': fmtid,
									#'fmturl': urllib.unquote_plus(fmturl),'fmtsig': fmtsig}
									if fmtsig != '': video_fmt_map[video_priority_map[fmtid]]['fmtsig']=fmtsig
									fmt_infomap[int(fmtid)] = '%s' % (urllib.unquote_plus(fmturl))
									if fmtsig != '':fmt_infomap[int(fmtid)]+='&signature='+fmtsig
								fmturl = fmtid = fmtsig = ''
							except Exception as ex:
								#print type(ex).__name__
								print ex

						else:
							fmtid, fmturl = fmtstring.split('|')
						if video_priority_map.has_key(fmtid) and fmtid != '':
							video_fmt_map[video_priority_map[fmtid]] = {'fmtid': fmtid,
							'fmturl': urllib.unquote_plus(fmturl)}
							fmt_infomap[int(fmtid)] = urllib.unquote_plus(fmturl)

					if video_fmt_map and len(video_fmt_map):
						best_video = video_fmt_map[sorted(video_fmt_map.iterkeys())[0]]
						print best_video['fmturl']
						video_url = '%s' % (best_video['fmturl'].split(';')[0])
						if 'fmtsig' in best_video: video_url+='&signature='+best_video['fmtsig']
				else:
					print 'Youtube parser failed'
					ShowMessage("Youtube parser failed!",url)
		except Exception as ex:
			print ex

		if video_url != url:
			url = video_url
			#print url

	return url


hos = int(sys.argv[1])
#print sys.argv
params = get_params(sys.argv[2])
#print params

# -- Unified search API handling --
unified = bool(params['unified']) if 'unified' in params else False
if unified:
	params['func'] = 'ListCat'

mode = params["mode"] if 'mode' in params else None
if mode == 'show':
	print urllib.unquote_plus(params["url"])
	params = get_params(urllib.unquote_plus(params["url"]))
	print params
# ---------------------------------

try:
	func = params['func']
	del params['func']
except:
	func = None
	xbmc.log( '[%s]: Primary input' % addon_id, 1 )
	Main(params)
if func != None:
	try: pfunc = globals()[func]
	except:
		pfunc = None
		xbmc.log( '[%s]: Function "%s" not found' % (addon_id, func), 4 )
		ShowMessage('Internal addon error', 'Function "%s" not found' % func, 2000)
	if pfunc: pfunc(params)

