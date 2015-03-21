#!/usr/bin/python
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
import urllib2, re, xbmcaddon, string, xbmc, xbmcgui, xbmcplugin, os, urllib, cookielib
import xml.dom.minidom

__settings__ = xbmcaddon.Addon(id='plugin.video.rusd.tv')
__language__ = __settings__.getLocalizedString
USERNAME = __settings__.getSetting('username')
USERPASS = __settings__.getSetting('password')
handle = int(sys.argv[1])

PLUGIN_NAME   = 'RuSD.TV'
SITE_URL      = 'http://rusd.tv/'
thumb = os.path.join(os.getcwd().replace(';', ''), "icon.png" )

def showMessage(heading, message, times = 3000):
	heading = heading.encode('utf-8')
	message = message.encode('utf-8')
	xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, thumb))

def run_once():
	global USERNAME, USERPASS
	while (Get(SITE_URL + 'ShowSeries/') == None):
		user_keyboard = xbmc.Keyboard()
		user_keyboard.setHeading(__language__(30001))
		user_keyboard.doModal()
		if (user_keyboard.isConfirmed()):
			USERNAME = user_keyboard.getText()
			pass_keyboard = xbmc.Keyboard()
			pass_keyboard.setHeading(__language__(30002))
			pass_keyboard.setHiddenInput(True)
			pass_keyboard.doModal()
			if (pass_keyboard.isConfirmed()):
				USERPASS = pass_keyboard.getText()
				__settings__.setSetting('username', USERNAME)
				__settings__.setSetting('password', USERPASS)
			else:
				return False
		else:
			return False
	return True

def Get(url, ref=None):
	use_auth = False
	inter = 2
	while inter:
		cj = cookielib.CookieJar()
		h  = urllib2.HTTPCookieProcessor(cj)
		opener = urllib2.build_opener(h)
		urllib2.install_opener(opener)
		post = None
		if use_auth:
			post = urllib.urlencode({'login': USERNAME, 'password': USERPASS})
			url = SITE_URL
		request = urllib2.Request(url, post)
		if ref != None:
			request.add_header('Referer', ref)
		phpsessid = __settings__.getSetting('cookie')
		if len(phpsessid) > 0:
			request.add_header('Cookie', 'PHPSESSID=' + phpsessid)
		o = urllib2.urlopen(request)
		for index, cookie in enumerate(cj):
			cookraw = re.compile('<Cookie PHPSESSID=(.*?) for.*/>').findall(str(cookie))
			if len(cookraw) > 0:
				__settings__.setSetting('cookie', cookraw[0])
		http = o.read()
		o.close()
		if (http.find('<form id="loginform"') == -1): # 01.01.11 thanks SlavikZ xbmc.ru
			return http
		else:
			use_auth = True
		inter = inter - 1
	return None

def get_params():
	param=[]
	paramstring=sys.argv[2]
	if len(paramstring)>=2:
		params=sys.argv[2]
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

# http://xbmc.ru/showpost.php?p=6063&postcount=89
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
		return text # leave as is
	ret =  re.sub("(?s)<[^>]*>|&#?\w+;", fixup, text)
	return re.sub("\n+", '\n' , ret)

def GetRegion(data, region, modeall=False, defval=None):
	try:
		ret_val = re.compile('<%s>(.*?)</%s>'%(region,region),re.DOTALL|re.IGNORECASE).findall(data)
		if modeall: return ret_val
		else: return ret_val[0]
	except: return defval

def parse_playable_item(data):
	id_episodes = GetRegion(data, 'id_episodes')
	series      = GetRegion(data, 'series')
	snum        = GetRegion(data, 'snum')
	enum        = GetRegion(data, 'enum')
	vnum        = GetRegion(data, 'vnum')
	title       = GetRegion(data, 'title')
	tmark       = GetRegion(data, 'tmark')
	enable      = GetRegion(data, 'enable')
	sub         = GetRegion(data, 'sub')
	smark       = GetRegion(data, 'smark')
	mark        = GetRegion(data, 'mark')
	server      = GetRegion(data, 'server')
	vurl        = GetRegion(data, 'vurl')
	return id_episodes,series,snum,enum,vnum,strip_html(title),tmark,enable,sub,smark,mark,server,vurl

def parse_series_item(data):
	id_series = GetRegion(data, 'id_series')
	title     = GetRegion(data, 'title')
	etitle    = GetRegion(data, 'etitle')
	info      = GetRegion(data, 'info')
	fpimg     = GetRegion(data, 'fpimg')
	pimg      = GetRegion(data, 'pimg')
	mark      = GetRegion(data, 'mark')
	enable    = GetRegion(data, 'enable')
	pos       = GetRegion(data, 'pos')
	isclosed  = GetRegion(data, 'isclosed')
	fpimg = SITE_URL + fpimg
	pimg  = SITE_URL + pimg
	return id_series,strip_html(title),strip_html(etitle),strip_html(strip_html(info)),fpimg,pimg,mark,enable,pos,isclosed

def parse_content_urls(mark, snum, enum):
	snum0 = snum
	enum0 = enum
	if len(snum) == 1: snum0 = '0%s'%snum
	if len(enum) == 1: enum0 = '0%s'%enum
	sc     = '%ssc/%s/%s-%s.jpg' % (SITE_URL, mark, snum0, enum0)
	sub   = '%ssub/%s/%s-%s.srt' % (SITE_URL, mark, snum0, enum0)
	return sc,sub

def ShowSeries(url, showPay = False):
	http = Get(url)
	if http == None:
		showMessage(__language__(30014),__language__(30003))
		return False
	if showPay:
		user_region = re.compile('<user id=\'(.*?)\'>(.*?)</user>',re.DOTALL|re.IGNORECASE).findall(http)
		if len(user_region) > 0:
			(user_id, user_block) = user_region[0]
			login = GetRegion(user_block, 'login')
			mail  = GetRegion(user_block, 'mail')
			pdays_region = re.compile('<pdays state=\'(.*?)\'>(.*?)</pdays>',re.DOTALL|re.IGNORECASE).findall(user_block)
			pdays_state = '?'
			pdays_days  = '?'
			if len(pdays_region) > 0:
				(pdays_state, pdays_days) = pdays_region[0]
			user_item = '[ %s (%s: %s) %s ]'%(login, __language__(30004).encode('utf-8'), pdays_days, __language__(30005).encode('utf-8'))
			uri = sys.argv[0] + '?mode=openSettings'
			item=xbmcgui.ListItem(user_item, iconImage=thumb, thumbnailImage=thumb)
			xbmcplugin.addDirectoryItem(handle,uri,item)
		else:
			showMessage(__language__(30008),__language__(30019))
			xbmc.output('[%s] ShowSeries() ERROR: Unable to find "user" region' % (PLUGIN_NAME))
			xbmc.output('HTTP=%s'%http)
	fav_list = []
	favorites_block = GetRegion(http, 'favorites')
	if favorites_block != None:
		fav_list = GetRegion(http, 'series', True)
	serieslist_block = GetRegion(http, 'serieslist')
	if serieslist_block == None:
		showMessage(__language__(30008),__language__(30019))
		xbmc.output('[%s] ShowSeries() ERROR: Unable to find "serieslist" region' % (PLUGIN_NAME))
		xbmc.output('HTTP=%s'%http)
		return False
	item_blocks = GetRegion(serieslist_block, 'item', True)
	if item_blocks == None:
		showMessage(__language__(30008),__language__(30019))
		xbmc.output('[%s] ShowSeries() ERROR: Unable to find "item" region' % (PLUGIN_NAME))
		xbmc.output('HTTP=%s'%http)
		return False
	for item_block in item_blocks:
		(id_series,title,etitle,info,fpimg,pimg,mark,enable,pos,isclosed)=parse_series_item(item_block)
		tvshowtitle = '%s (%s)'%(etitle, title)
		if __language__(30000) == 'Russian':
			tvshowtitle = '%s (%s)'%(title, etitle)
		if isclosed == '1':
			if __settings__.getSetting('shclosed') == 'true':
				tvshowtitle += ' %s' % __language__(30121).encode('utf-8')
			info += '\n%s %s' % (__language__(30121).encode('utf-8'), __language__(30122).encode('utf-8'))
		if id_series in fav_list:
			fav_ti  = __language__(30006).encode('utf-8') + ' ' + PLUGIN_NAME
			fav_url = '%sRemoveFromFavorites/%s/'%(SITE_URL, id_series)
			fav_star = '*'
		else:
			fav_ti  = __language__(30007).encode('utf-8') + ' ' + PLUGIN_NAME
			fav_url = '%sAddToFavorites/%s/'%(SITE_URL, id_series)
			fav_star = ''
		uri2 = sys.argv[0] + '?mode=ExecURL'
		uri2 += '&url='    + urllib.quote_plus(fav_url)
		uri = sys.argv[0] + '?mode=ShowEpisodes'
		uri += '&url='    + urllib.quote_plus('%sShowEpisodes/%s/XML/'%(SITE_URL, id_series))
		item=xbmcgui.ListItem('%s %s'%(tvshowtitle, fav_star), iconImage=fpimg, thumbnailImage=fpimg)
		item.setInfo(type='video', infoLabels={'title': tvshowtitle, 'plot': info, 'tvshowtitle': tvshowtitle})
		item.setProperty('fanart_image',pimg)
		if showPay:
			item.addContextMenuItems([(fav_ti, 'XBMC.RunPlugin(%s)'%uri2,)])
		xbmcplugin.addDirectoryItem(handle,uri,item, True)
	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_GENRE)
	xbmcplugin.endOfDirectory(handle)


def ShowEpisodes(url):
	http = Get(url)
	if http == None:
		showMessage(__language__(30014),__language__(30003))
		return False
	series_raw = re.compile('<series id=\'(.*?)\'>(.*?)</series>',re.DOTALL|re.IGNORECASE).findall(http)
	if len(series_raw) == 0:
		showMessage(__language__(30008),__language__(30019))
		xbmc.output('[%s] ShowEpisodes() ERROR: Unable to find "series" region' % (PLUGIN_NAME))
		xbmc.output('HTTP=%s'%http)
		return False
	(id_series0, series_region) = series_raw[0]
	common_data = re.sub('(?is)<season.*>.*?</season>','',series_region,re.DOTALL|re.IGNORECASE)
	(id_series,title,etitle,info,fpimg,pimg,base_mark,enable,pos,isclosed)=parse_series_item(common_data)
	tvshowtitle = '%s (%s)'%(etitle, title)
	if __language__(30000) == 'Russian':
		tvshowtitle = '%s (%s)'%(title, etitle)
	season_raw = re.compile('<season(.*?)</season>',re.DOTALL|re.IGNORECASE).findall(http)
	if len(season_raw) == 0:
		showMessage(__language__(30008),__language__(30019))
		xbmc.output('[%s] ShowEpisodes() ERROR: Unable to find "season" region' % (PLUGIN_NAME))
		xbmc.output('HTTP=%s'%http)
		return False
	for cur_season in season_raw:
		items = GetRegion(cur_season, 'item', True)
		if items == None:
			showMessage(__language__(30008),__language__(30019))
			xbmc.output('[%s] ShowEpisodes() ERROR: Unable to find "item" region' % (PLUGIN_NAME))
		else:
			for itemblock in items:
				(id_episodes,series,snum,enum,vnum,title,tmark,enable,sub,smark,mark,server,vurl)=parse_playable_item(itemblock)
				ide_prefix = ''
				ide_mode = int(__settings__.getSetting('ide_mode'))
				if ide_mode == 1:
					ide_prefix = '%s.%s. '%(snum, enum)
				elif ide_mode == 2:
					ide_prefix = __language__(30115).encode('utf-8')%(snum, enum)
				elif ide_mode == 3:
					ide_prefix = 's%se%s '%(snum, enum)
				title = ide_prefix + title
				(sc,sub)=parse_content_urls(base_mark, snum, enum)
				uri = sys.argv[0] + '?mode=ShowEpisode'
				uri += '&url='   + urllib.quote_plus('%sGetEpisodeLink/%s/XML/'%(SITE_URL, id_episodes))
				uri += '&tvshowtitle=' + urllib.quote_plus(tvshowtitle)
				uri += '&info='  + urllib.quote_plus(info)
				item=xbmcgui.ListItem(title, iconImage=sc, thumbnailImage=sc)
				item.setInfo(type='video', infoLabels={ 'title':       title,
									'plot':        info,
									'season':      int(snum),
									'episode':     int(enum),
									'aired':       tmark,
									'tvshowtitle': tvshowtitle})
				#item.setProperty('IsPlayable', 'true')
				item.setProperty('fanart_image', pimg)
				xbmcplugin.addDirectoryItem(handle,uri,item)
	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_EPISODE)
	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_GENRE)
	xbmcplugin.endOfDirectory(handle)

def ShowEpisode(url, tvshowtitle, info):
	http = Get(url)
	if http == None:
		showMessage(__language__(30014),__language__(30003))
		return False
	if (http.find('type=\'nomoney\'') != -1):
		showMessage(__language__(30008),__language__(30009), 5000)
		return False
	if (http.find('type=\'notfound\'') != -1):
		showMessage(__language__(30008),__language__(30017))
		return False
	items = GetRegion(http, 'item', True)
	if (items == None) or (len(items) == 0):
		showMessage(__language__(30008),__language__(30019))
		xbmc.output('[%s] ShowEpisode() ERROR: Unable to find "item" region' % (PLUGIN_NAME))
		xbmc.output('HTTP=%s'%http)
		return False
	(id_episodes,series,snum,enum,vnum,title,tmark,enable,sub,smark,mark,server,vurl) = parse_playable_item(items[0])
	use_sub = False
	sub_mode = int(__settings__.getSetting('sub_mode'))
	if sub_mode == 1:
		if   sub == 'ru': use_sub = True
		else: showMessage(__language__(30020),__language__(30021))
	elif sub_mode == 2:
		if   sub == 'en': use_sub = True
		else: showMessage(__language__(30020),__language__(30022))
	elif sub_mode == 3:
		if   len(sub) == 2: use_sub = True
		else: showMessage(__language__(30020),__language__(30023))
	(sc,sub) = parse_content_urls(mark, snum, enum)
	item = xbmcgui.ListItem(title, iconImage=sc, thumbnailImage=sc)
	item.setInfo(type='video', infoLabels={'title': title, 'plot': info, 'season': int(snum), 'episode': int(enum), 'aired': tmark, 'tvshowtitle': tvshowtitle})
	xbmc.Player().play('http://%s/v/%s'%(server,vurl), item)
	xbmc.sleep(2000)
	if   use_sub: xbmc.Player().setSubtitles(sub)

def GetNews():
	http = Get(SITE_URL + 'ShowRSS/')
	if http == None:
		showMessage(__language__(30014),__language__(30003))
		return False
	item_blocks = GetRegion(http, 'item', True)
	if item_blocks == None:
		showMessage(__language__(30008),__language__(30019))
		xbmc.output('[%s] GetNews() ERROR: Unable to find "item" region' % (PLUGIN_NAME))
		xbmc.output('HTTP=%s'%http)
		return False
	x = 1
	for itemblock in item_blocks:
		link    = GetRegion(itemblock, 'link')
		if link == None:
			showMessage(__language__(30008),__language__(30019))
			xbmc.output('[%s] GetNews() ERROR: Unable to find "link" region' % (PLUGIN_NAME))
			xbmc.output('HTTP=%s'%http)
			return False
		title   = GetRegion(itemblock, 'title')
		if title == None:
			showMessage(__language__(30008),__language__(30019))
			xbmc.output('[%s] GetNews() ERROR: Unable to find "title" region' % (PLUGIN_NAME))
			xbmc.output('HTTP=%s'%http)
			return False
		pubdate = GetRegion(itemblock, 'pubDate')
		if pubdate == None:
			showMessage(__language__(30008),__language__(30019))
			xbmc.output('[%s] GetNews() ERROR: Unable to find "pubDate" region' % (PLUGIN_NAME))
			xbmc.output('HTTP=%s'%http)
			return False
		Title = strip_html('%s. %s' % (str(x), title))
		Plot = strip_html(pubdate)
		Target = link + 'XML/'
		Target = Target.replace('ShowEpisode','GetEpisodeLink')
		uri = sys.argv[0] + '?mode=ShowEpisode'
		uri += '&url='   + urllib.quote_plus(Target)
		uri += '&theme=' + urllib.quote_plus(__language__(30010).encode('utf-8'))
		uri += '&info='  + urllib.quote_plus(Plot)
		item=xbmcgui.ListItem(Title, iconImage=thumb, thumbnailImage=thumb)
		item.setInfo(type='video', infoLabels={'title': Title, 'plot': Plot, 'aired': Plot})
		#item.setProperty('IsPlayable', 'true')
		xbmcplugin.addDirectoryItem(handle,uri,item)
		x += 1
	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.endOfDirectory(handle)


def ShowNEW():
	use_russian = (__language__(30000) == 'Russian')
	http = Get(SITE_URL + 'ShowSeries/new/XML/')
	if http == None:
		showMessage(__language__(30014),__language__(30003))
		return False
	series_raw = re.compile('<series id=\'(.*?)\'>(.*?)</item></series>',re.DOTALL|re.IGNORECASE).findall(http)
	if len(series_raw) == 0:
		showMessage(__language__(30008),__language__(30018))
		return False
	for id_series0, series_region in series_raw:
		series_region += '</item>'
		seriesinfo = GetRegion(series_region, 'seriesinfo')
		if seriesinfo == None:
			showMessage(__language__(30008),__language__(30019))
			xbmc.output('[%s] ShowNEW() ERROR: Unable to find "seriesinfo" region' % (PLUGIN_NAME))
		else:
			(id_series,title,etitle,info,fpimg,pimg,mark,enable,pos,isclosed) = parse_series_item(seriesinfo)
			t1 = etitle
			t2 = title
			if use_russian:
				t1 = title
				t2 = etitle
			common_data = re.sub('(?is)<seriesinfo>.*?</seriesinfo>','',series_region,re.DOTALL|re.IGNORECASE)
			items = GetRegion(common_data, 'item', True)
			if items == None:
				showMessage(__language__(30008),__language__(30019))
				xbmc.output('[%s] ShowNEW() ERROR: Unable to find "item" region' % (PLUGIN_NAME))
			else:
				for itemblock in items:
					(id_episodes,series,snum,enum,vnum,title,tmark,enable,sub,smark,mark,server,vurl) = parse_playable_item(itemblock)
					if use_russian: t0 = title
					else: t0 = etitle
					item_title = '%s : s%se%s : %s'%(t1, snum, enum, t0)
					(sc,sub) = parse_content_urls(mark, snum, enum)
					uri = sys.argv[0] + '?mode=ShowEpisode'
					uri += '&url='   + urllib.quote_plus('%sGetEpisodeLink/%s/XML/'%(SITE_URL, id_episodes))
					uri += '&info='  + urllib.quote_plus(info)
					item=xbmcgui.ListItem(item_title, iconImage=sc, thumbnailImage=sc)
					item.setInfo( type='video', infoLabels={'title':       item_title,
										'plot':        info,
										'season':      int(snum),
										'episode':     int(enum),
										'aired':       tmark,
										'tvshowtitle': '%s (%s)'%(t1, t2)})
					#item.setProperty('IsPlayable', 'true')
					item.setProperty('fanart_image', pimg)
					xbmcplugin.addDirectoryItem(handle,uri,item)
	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_EPISODE)
	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_GENRE)
	xbmcplugin.endOfDirectory(handle)


if run_once():
	params = get_params()
	mode  = None
	url   = SITE_URL + 'ShowSeries/all/XML/'
	info  = ''
	tvshowtitle = ''

	try: mode  = urllib.unquote_plus(params['mode'])
	except: pass
	try: url   = urllib.unquote_plus(params['url'])
	except: pass
	try: tvshowtitle  = urllib.unquote_plus(params['tvshowtitle'])
	except: pass
	try: info  = urllib.unquote_plus(params['info'])
	except: pass

	if (mode == 'ShowSeries') or (mode == None):
		if mode == None:
			uri = sys.argv[0] + '?mode=GetNews'
			item = xbmcgui.ListItem(__language__(30011), iconImage=thumb, thumbnailImage=thumb)
			xbmcplugin.addDirectoryItem(handle,uri,item, True)

			uri  = sys.argv[0] + '?mode=ShowNEW'
			item = xbmcgui.ListItem(__language__(30012), iconImage=thumb, thumbnailImage=thumb)
			xbmcplugin.addDirectoryItem(handle,uri,item, True)

			uri  = sys.argv[0] + '?url=' + urllib.unquote_plus(SITE_URL + 'ShowSeries/my/XML/')
			uri += '&mode=ShowSeries'
			item = xbmcgui.ListItem(__language__(30013), iconImage=thumb, thumbnailImage=thumb)
			xbmcplugin.addDirectoryItem(handle,uri,item, True)
			ShowSeries(url, True)
		else:
			ShowSeries(url)

	elif mode == 'ShowEpisodes':
		ShowEpisodes(url)

	elif mode == 'ShowEpisode':
		ShowEpisode(url, tvshowtitle, info)

	elif mode == 'GetNews':
		GetNews()

	elif mode == 'ShowNEW':
		ShowNEW()

	elif mode == 'openSettings':
		__settings__.openSettings()
		__settings__.setSetting('cookie', '')
		xbmc.sleep(50)
		xbmc.executebuiltin('Container.Refresh')

	elif mode == 'ExecURL':
		Get(url)
		xbmc.sleep(50)
		xbmc.executebuiltin('Container.Refresh')
