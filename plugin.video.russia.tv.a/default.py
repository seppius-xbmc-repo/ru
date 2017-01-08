#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib, urllib2
import re, os, urlparse, sys, json
import xbmcplugin, xbmcgui, xbmc, xbmcaddon
from bs4 import BeautifulSoup as bs

Addon = xbmcaddon.Addon(id = 'plugin.video.russia.tv.a')
addon_id = Addon.getAddonInfo('id')
addon_icon = Addon.getAddonInfo('icon')
addon_path = Addon.getAddonInfo('path')
addon_name = Addon.getAddonInfo('name')

UA = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'

sites = [('Россия 1', 'http://russia.tv/video/', 'http://russia.tv/i/logo/standart-russia1.png'), ('Россия 2', 'http://russia2.tv/video/', 'http://russia2.tv/i/logo/standart-russia2.png'), ('Культура', 'http://tvkultura.ru/video/', 'http://tvkultura.ru/i/logo/standart-russiak.png')]


def GetParams(sparams):
	#print sparams
	sparams = sparams.replace('?', '', 1)
	params = urlparse.parse_qs(sparams)
	params = {key: params[key][0] for key in params}
	#print params
	return params

def ShowMessage(heading, message, times = 5000, image = addon_icon):
	xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, %s)' % (heading, message, times, image))

def construct_request(params):
	return '%s?%s' % (sys.argv[0], urllib.urlencode(params))

def GET(url, ref = None, opts = '', post = None, headers = None):
	req = urllib2.Request(url, data = post)
	req.add_header('User-Agent', UA)
	req.add_header('Accept-Language', 'ru-RU,ru;q=0.9,en;q=0.8')
	if headers: [req.add_header(k, v) for k, v in headers.items()]
	print "GET: " + url
	if ref: req.add_header('Referer', ref)
	if 'xmlhttp' in opts:
		req.add_header('X-Requested-With', 'XMLHttpRequest')
	if 'timeout' in opts: timeout = 0.2
	else: timeout = 7
	try:
		response = urllib2.urlopen(req, timeout = timeout)
		html = response.read()
		if 'headers' in opts: resp_headers = response.info()
		else: resp_headers = None
		response.close()
		if resp_headers: result = (html, resp_headers)
		else: result = html
		return result
	except Exception, e:
		print 'GET: Error getting page ' + url + ' (' + str(e) + ')'
		ShowMessage('HTTP error', 'Error getting page: ' + url)
		return None


def Main(params):
	for i, c in enumerate(sites):
		li = xbmcgui.ListItem(c[0], iconImage = c[2], thumbnailImage = c[2])
		uri = construct_request({'func': 'ListCats', 'site': i})
		xbmcplugin.addDirectoryItem(hos, uri, li, True)
	#li1 = xbmcgui.ListItem('ПОИСК')
	#uri = construct_request({'func': 'Search'})
	#xbmcplugin.addDirectoryItem(hos, uri, li1, True)
	xbmcplugin.endOfDirectory(hos)

	
def ListCats(params):
	site = int(params['site'])
	url = sites[site][1]
	html = GET(url)
	s = bs(html, 'html.parser')
	cats = s.find('ul', class_ = 'b-tabs items')
	cats = cats.find_all('a')
	#print cats
	uri = construct_request({
		'func': 'ListSeries',
		'site': site,
		'brand': 'new'
		})
	li = xbmcgui.ListItem("НОВОЕ")
	xbmcplugin.addDirectoryItem(hos, uri, li, True)
	
	for cat in cats:
		menu_id = re.findall('/(\d+)/$', cat['href'])
		if menu_id: menu_id = menu_id[0]
		else: menu_id = 'all'
		catname = cat.string
		#print menu_id, cat, catname
		li = xbmcgui.ListItem(catname)
		uri = construct_request({
			'func': 'ListCat',
			'site': site,
			'cat': menu_id
			})
		xbmcplugin.addDirectoryItem(hos, uri, li, True)
	
	xbmcplugin.endOfDirectory(hos)


def ListCat(params):
	site = int(params['site'])
	cat = params['cat']
	# "Новое"
	uri = construct_request({
		'func': 'ListSeries',
		'site': site,
		'brand': 'nc' + cat
		})
	lin = xbmcgui.ListItem("НОВОЕ")
	xbmcplugin.addDirectoryItem(hos, uri, lin, True)
	
	url = sites[site][1] + 'index/'
	if not cat == 'all': url += 'menu_id/' + cat + '/'
	url += 'sort_by/2'
	html = GET(url)
	s = bs(html, 'html.parser')
	brands = s.find_all('li', class_ = re.compile('item'))
	#print brands
	for brand in brands:
		title = brand.a.string.strip().encode('utf-8')
		genre = brand.p.string
		link = brand.a['href']
		brand_id = re.findall('/brand_id/(\d*)', link)[0]
		uri = construct_request({
			'func': 'ListSeries',
			'site': site,
			'brand': brand_id,
			'title': title
			})
		# todo: add genre
		li = xbmcgui.ListItem(title)
		xbmcplugin.addDirectoryItem(hos, uri, li, True)
	
	xbmcplugin.endOfDirectory(hos)


def ListSeries(params):
	site = int(params['site'])
	brand = params['brand']
	page = int(params['page']) if 'page' in params else 1
	contitle = params['title'] if 'title' in params else ''

	if 'n' in brand:
		url = sites[site][1] + 'json/'
		if 'nc' in brand: 
			cat = brand[2:]
			url += '/menu_id/' + cat
		url += '?page=' + str(page)
		jsonf = True
	else:
		url = sites[site][1] + 'jsonseries/brand_id/' + brand + '/sort_by/date/page/?page=' + str(page)
		jsonf = False
	
	data = GET(url, opts = 'xmlhttp')
	data = json.loads(data)
	#print json.dumps(html, indent = 1)
	if jsonf: items = data['row_list']
	else: 
		html = data['html'].encode('utf-8')
		#print html
		soup = bs(html, 'html.parser')
		#print str(bs)
		items = soup.find_all('div', class_ = 'pic')
		#print items
	
	for item in items:
		#print item
		if jsonf: 
			tvshowtitle = item['brand_title']
			name = tvshowtitle + '. ' + item['video_title']
		else: 
			name = item.find_all('a')[1].string.strip().encode('utf-8')
			if not name: name = params['title']
			tvshowtitle = contitle
		#print name
		if jsonf: img = item['picture_url']
		else: img = item.find('img')['data-original']
		img = img.replace('/md/', '/b/')
		#print img
		if jsonf: href = item['url']
		else: href = item.find('a')['href']
		
		eid = re.findall('episode_id/(\d+)', href)[0]
		try: vid = re.findall('video_id/(\d+)', href)[0]
		except:
			vid = None
			print 'doesn\'t have video ID'
		#print eid + " " + str(vid)
		if jsonf: plot = item['anons']
		else: plot = ''
		
		#duration
		if jsonf: duration = item['duration_hf']
		else: 
			duration = item.find('div', class_ = "duration")
			#print duration
			if duration:
				duration = duration.string.strip()
				#duration = str(duration)
				#print duration, type(duration)
			else: duration = ''
		if duration:
			hms = re.findall('(\d\d)\:(\d\d)\:(\d\d)', duration)
			#print hms
			if hms:
				#ds = int(hms[0][0]) * 60 * 60 + int(hms[0][1]) * 60 + int(hms[0][2])
				#print ds
				#listItem.addStreamInfo('video', {'duration': ds})
				dm = str(int(hms[0][0]) * 60 + int(hms[0][1]))
				if dm == 0: dm = ''
		else: dm = ''
		uri = {
			'func': 'Play',
			'eid': eid,
			'site': site,
			'brand': brand
			}
		if vid: uri.update({'vid': vid})
		uri = construct_request(uri)
		li = xbmcgui.ListItem(name, thumbnailImage = img, iconImage = img)
		li.setInfo(type = "video", infoLabels = {"duration": dm, 'tvshowtitle': tvshowtitle, 'plot': plot})
		li.setProperty('IsPlayable', 'true')
		li.setProperty("Fanart_Image", img)
		#retdesc = 'XBMC.Container.Update("%s?mode=serial&site=%s&brand=%s&page=%s&ret=1&item=%s", replace = False)' %  (sys.argv[0], str(site), str(brand), str(page), str(vid))
		#li.addContextMenuItems([('Описание', '')])
		xbmcplugin.addDirectoryItem(hos, uri, li)
	
	if jsonf: ilp = data['last_page'] != 0
	else: ilp = data['is_last_page'] != 0
	if not ilp:
		linp = xbmcgui.ListItem("ПОКАЗАТЬ ЕЩЕ")
		uri = {
			'func': 'ListSeries',
			'site': site,
			'brand': brand,
			'page': page + 1
			}
		if contitle: uri.update({'title': contitle})
		uri = construct_request(uri)
		xbmcplugin.addDirectoryItem(hos, uri, linp, True)
	xbmcplugin.endOfDirectory(hos)


def Play(params):
	eid = params['eid']
	vid = params['vid'] if 'vid' in params else None
	site = int(params['site'])
	brand = params['brand']
	if not vid or vid != eid:
		url = sites[site][1] + 'show/brand_id/' + brand + '/episode_id/' + eid
		if vid: url += '/video_id/' + vid
		html = GET(url)
		nvid = re.findall('iframe/video/id/(\d+)', html)[0]
	else: 
		nvid = vid
		print 'plain v_id'
	#print "%s %s %s" % (eid, vid, nvid)
	url = 'http://player.vgtrk.com/iframe/datavideo/id/' + nvid
	data = GET(url)
	#print data
	data = json.loads(data)
	#print json.dumps(data, indent = 1)
	try:
		vatrbs = data["data"]['playlist']['medialist'][0]
		link = vatrbs['sources']['m3u8']['auto']
		#print 'SOURCES: ' + str(vatrbs['sources'])
	except Exception, e:
		print str(e)
		print json.dumps(data, indent = 1)
		if data['errors']: 
			ShowMessage(addon_name, data['errors'].encode('utf-8'))
			print data['errors'].encode('utf-8')
		if vatrbs['errors']: ShowMessage(addon_name, vatrbs['errors'].encode('utf-8'))
		return
	img = vatrbs['picture'] if 'picture' in vatrbs else ''
	#print img
	title = vatrbs['title'] if 'title' in vatrbs else ''
	plot = vatrbs['anons'] if 'anona' in vatrbs else ''
	
	li = xbmcgui.ListItem(title, path = link, thumbnailImage = img)
	li.setInfo(type = "video", infoLabels = {"plot": plot})
	li.setProperty('IsPlayable', 'true')
	#print link
	xbmcplugin.setResolvedUrl(hos, True, li)


#print sys.argv
pname = sys.argv[0]
hos = int(sys.argv[1])
params = GetParams(sys.argv[2])

if 'func' in params: 
	func = params['func']
	del params['func']
else: func = 'Main'
pfunc = globals()[func]
pfunc(params)
