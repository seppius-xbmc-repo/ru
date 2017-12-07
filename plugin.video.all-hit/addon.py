#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib, urllib2, re, sys, os, json
import xbmcplugin, xbmcgui, xbmcaddon, xbmc

h = int(sys.argv[1])

addon = xbmcaddon.Addon(id='plugin.video.all-hit')
icon = os.path.join( addon.getAddonInfo('path'), "icon.png" )
xbmcplugin.setContent(h, 'movies')

def construct_request(params):
        return '%s?%s' % (sys.argv[0], urllib.urlencode(params))

def showMessage(heading, message, times = 50000):
        xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))

def GET(url):
	try:
		print 'def GET(%s):'%url
		req = urllib2.Request(url)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
		response = urllib2.urlopen(req)
		http=response.read()
		response.close()
		return http
	except:
		showMessage('Не могу открыть URL def GET', url)
		return None

def format_s(s):
	s=s.decode('windows-1251').encode('utf-8')
	return s
		
def OPEN_KINO():
        name='[ ПОИСК ]'
        u = sys.argv[0] + '?mode=search'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        xbmcplugin.addDirectoryItem(h, u, i, True)

	#wurl = 'http://all-hit.tv'
	#http = GET(wurl)
	#try:
	#	r1 = re.compile('<div class="loolla">(.*?)<noindex>',re.S).findall(http)
	#	r2 = re.compile('<li><a href="(.*?)">(.*?)</a></li>',re.S).findall(r1[0])
	#	for href, name in r2:
	#		i = xbmcgui.ListItem(unicode(name, "windows-1251"), iconImage=icon, thumbnailImage=icon)
	#		u  = sys.argv[0] + '?mode=OPEN_MOVIES'
	#		u += '&url=%s'%urllib.quote_plus('http://all-hit.tv' + href)
	#		u += '&name=%s'%urllib.quote_plus(name)
	#		xbmcplugin.addDirectoryItem(h, u, i, True)
	#except:
	#	pass
	wurl = 'http://all-hit.tv'
	http = GET(wurl)
	if http == None: return False
	r1 = re.compile('<div class="poloha">(.*?)<noindex>',re.S).findall(http)
	r2 = re.compile('<li><a href="(.*?)">(.*?)</a></li>',re.S).findall(r1[0])
	for href, name in r2:
		i = xbmcgui.ListItem(unicode(name, "windows-1251"), iconImage=icon, thumbnailImage=icon)
		u  = sys.argv[0] + '?mode=OPEN_MOVIES'
		u += '&url=%s'%urllib.quote_plus('http://all-hit.tv' + href)
		u += '&name=%s'%urllib.quote_plus(name)
		xbmcplugin.addDirectoryItem(h, u, i, True)
	
	xbmcplugin.endOfDirectory(h)

def search():
        keyboard = xbmc.Keyboard("", 'Search', False) 
        keyboard.doModal()
        if keyboard.isConfirmed():
                query = keyboard.getText()
                query = re.sub(r' ','+', query)
                query = re.sub(r'а','%E0', query)
                query = re.sub(r'б','%E1', query)
                query = re.sub(r'в','%E2', query)
                query = re.sub(r'г','%E3', query)
                query = re.sub(r'д','%E4', query)
                query = re.sub(r'е','%E5', query)
                query = re.sub(r'ж','%E6', query)
                query = re.sub(r'з','%E7', query)
                query = re.sub(r'и','%E8', query)
                query = re.sub(r'й','%E9', query)
                query = re.sub(r'к','%EA', query)
                query = re.sub(r'л','%EB', query)
                query = re.sub(r'м','%EC', query)
                query = re.sub(r'н','%ED', query)
                query = re.sub(r'о','%EE', query)
                query = re.sub(r'п','%EF', query)
                query = re.sub(r'р','%F0', query)
                query = re.sub(r'с','%F1', query)
                query = re.sub(r'т','%F2', query)
                query = re.sub(r'у','%F3', query)
                query = re.sub(r'ф','%F4', query)
                query = re.sub(r'х','%F5', query)
                query = re.sub(r'ц','%F6', query)
                query = re.sub(r'ч','%F7', query)
                query = re.sub(r'ш','%F8', query)
                query = re.sub(r'щ','%F9', query)
                query = re.sub(r'ы','%FB', query)
                query = re.sub(r'э','%FD', query)
                query = re.sub(r'ю','%FE', query)
                query = re.sub(r'я','%FF', query)
                query = re.sub(r'ё','%B8', query)
                query = re.sub(r'ь','%FC', query)
                query = re.sub(r'ъ','%FA', query)
                url = ('http://all-hit.tv/?do=search&subaction=search&story='+query)
                Blok_search(url)
	
def Blok_search(url):
	http = GET(url).replace('\n','')
	r2 = re.compile('<div class="title">.*?<a href="(.*?)">(.*?)</a>.*?--><img src="([^"]+)" alt="',re.S).findall(http)
	r4 = re.compile('<!--dle_image_end-->(.*?)</div>',re.S).findall(http.replace('\t',''))
	if len(r2) == 0:
		showMessage('НЕЧЕГО НЕ НАЙДЕНО', 'Нет элементов')
		return False
	ii = 0
	for href, alt, img in r2:
		img = 'http://all-hit.tv' + img
		text = r4[ii]
		text = re.sub('<.*?>',' ', text)
		ii = ii + 1
		i = xbmcgui.ListItem(unicode(alt, "windows-1251"), iconImage=img, thumbnailImage=img)
		i.setInfo(type='video', infoLabels={'title': unicode(alt, "windows-1251"), 'plot': unicode(text, "windows-1251")})
		u  = sys.argv[0] + '?mode=SRAVN'
		u += '&url=%s'%urllib.quote_plus(href)
		u += '&alt=%s'%urllib.quote_plus(alt)
		u += '&text=%s'%urllib.quote_plus(text)
		u += '&img=%s'%urllib.quote_plus(img)
		xbmcplugin.addDirectoryItem(h, u, i, True)
	xbmcplugin.endOfDirectory(h)

def OPEN_MOVIES(params):
	try:
		http = GET(urllib.unquote_plus(params['url']))
		page_s = urllib.unquote_plus(params['url'])
		r1 = re.compile('<div id=\'dle-content\'>(.*?)<ul class="lcolomn reset navi">',re.S).findall(http)
		r2 = re.compile('<a href="([^"]+)">([^<]+)</a>\s*</div>',re.S).findall(r1[0])
		r3 = re.compile('--><img src="([^"]+)" alt="',re.I).findall(r1[0])
		r4 = re.compile(r'<br /><b>.*?</b>(.*?)<div class="',re.S).findall(http)
	except:
		dialog = xbmcgui.Dialog()
		dialog.ok('ВНИМАНИЕ!', 'Нет такой страницы.', 'В этом разделе меньше страниц.')# диалог ОК
	ii = 0
	for href, alt in r2:
			img = 'http://all-hit.tv' + r3[ii]
			text = r4[ii]
			text = re.sub('<.*?>',' ', text)
			ii = ii + 1
			i = xbmcgui.ListItem(unicode(alt, "windows-1251"), iconImage=img, thumbnailImage=img)
			i.setInfo(type='video', infoLabels={'title': unicode(alt, "windows-1251"), 'plot': unicode(text, "windows-1251")})
			u  = sys.argv[0] + '?mode=SRAVN'
			u += '&url=%s'%urllib.quote_plus(href)
			u += '&img=%s'%urllib.quote_plus(img)
			u += '&alt=%s'%urllib.quote_plus(alt)
			u += '&text=%s'%urllib.quote_plus(text)
			i.setProperty('IsPlayable', 'true')
			xbmcplugin.addDirectoryItem(h, u, i, True)
	try:
		
		rp2 = re.compile('<span>[0-9]+</span>\s+<a href="(.*?)">(.*?)</a>').findall(http)
		#rp2 = re.compile('<div align="center" class="basenavi">\s+.+?<span>.+?</span> <a href="(.*?)">(.*?)</a>').findall(http)
		for href, nr in rp2:
			u = sys.argv[0] + '?mode=OPEN_MOVIES'
			u += '&url=%s'%urllib.quote_plus(href)
			i = xbmcgui.ListItem('[COLOR yellow]Далее > [/COLOR] %s '%nr)
			xbmcplugin.addDirectoryItem(h, u, i, True)# конец блока страниц
	except:
		pass
	try:
		rp = re.findall('(http://allhit\.tv.*?page/)([0-9]+)', page_s)
		for hr in rp:
			ggg = str(hr[0])
			u = sys.argv[0] + '?mode=stran'
			u += '&url=%s'%urllib.quote_plus(ggg)
			i = xbmcgui.ListItem('[COLOR ff62ff59]Переход на стр. >[/COLOR]', 
                        iconImage='special://home/addons/next.png', 
                        thumbnailImage='special://home/addons/next.png')
			xbmcplugin.addDirectoryItem(h, u, i, True)
	except:
		pass
	xbmcplugin.endOfDirectory(h)

def stran(params):
	http = urllib.unquote_plus(params['url'])
	keyboard = xbmc.Keyboard()
	keyboard.setHeading('Перейти на страницу ...')
	keyboard.doModal()
	if keyboard.isConfirmed():
		query = keyboard.getText()
		url = (http+query+'/')
		OPEN_MOVIES({'url':urllib.quote_plus(url)})
	else:
		return False

def SRAVN(params):
	http = GET(urllib.unquote_plus(params['url']))
	if http is None:
		return False
	rows1 = re.findall(r'(file=)', http, re.S)
	if 'file=' in rows1:
		PLAY(params)
	else:
		rows1 = re.findall(r'(pl=)', http, re.S)
	if 'pl=' in rows1:
		SERII(params)
	else:
		VK_com(params)
		
def SERII(params):
	http = GET(urllib.unquote_plus(params['url']))
	r2 = re.compile('pl=([^&]+)',re.S).findall(http)
	http = GET('http://all-hit.tv' + r2[0])
	r2 = re.compile('"comment":"(.*?)","file":"(.*?)"',re.S).findall(http)
	for name, href in r2:
		img = urllib.unquote_plus(params['img'])
		alt = urllib.unquote_plus(params['alt'])
		text = urllib.unquote_plus(params['text'])
		i = xbmcgui.ListItem(format_s(alt)+'   '+name, iconImage=img, thumbnailImage=img)
		i.setInfo(type='video', infoLabels={'title': unicode(alt, "windows-1251"), 'plot': unicode(text, "windows-1251")})
		u  = sys.argv[0] + '?mode=PLAY_Serii'
		u += '&img=%s'%urllib.quote_plus(img)
		u += '&url=%s'%urllib.quote_plus(href)
		u += '&alt=%s'%urllib.quote_plus(alt)
		u += '&name=%s'%urllib.quote_plus(name)
		u += '&text=%s'%urllib.quote_plus(text)
		xbmcplugin.addDirectoryItem(h, u, i, True)
        xbmcplugin.endOfDirectory(h)
		
def VK_com(params):
	http = GET(urllib.unquote_plus(params['url']))
	if http == None: return False
	r2 = re.compile('<iframe src="(.*?)" width="',re.S).findall(http)
	if len(r2) == 0:
		r2 = re.compile('<option value="(.*?)">.*?</option>',re.S).findall(http)
	if len(r2) == 0:
		r2 = re.compile('<iframe src="(.*?)"\s+width=".*?"',re.S).findall(http)
	if len(r2) == 0:
		r2 = re.compile('<iframe .*?=\"(.*?)"\s+frameborder=\".*?"',re.S).findall(http)
	if len(r2) >= 1:
		http = GET(r2[0])
	r2 = re.compile(r'480=([^?]+)',re.S).findall(http)
	if len(r2) == 0:
		r2 = re.compile(r'480=([^?]+)',re.S).findall(http)
	if len(r2) == 0:
		r2 = re.compile(r'360=([^?]+)',re.S).findall(http)
	if len(r2) == 0:
		r2 = re.compile(r'240=([^?]+)',re.S).findall(http)
        for names in r2:
		img = urllib.unquote_plus(params['img'])
		alt = urllib.unquote_plus(params['alt'])
		text = urllib.unquote_plus(params['text'])
		i = xbmcgui.ListItem(unicode(alt, "windows-1251"), iconImage=img, thumbnailImage=img)
		i.setInfo(type='video', infoLabels={'title': unicode(alt, "windows-1251"), 'plot': unicode(text, "windows-1251")})
		i.setProperty("IsPlayable","true")
		pl = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
		pl.clear()
		pl.add(names, i)
		xbmc.Player().play(pl)
	
def PLAY(params):
	http = GET(urllib.unquote_plus(params['url']))
	if http == None: return False
	r2 = re.compile('file=([^&]+)',re.S).findall(http)
	for names in r2:
		img = urllib.unquote_plus(params['img'])
		alt = urllib.unquote_plus(params['alt'])
		text = urllib.unquote_plus(params['text'])
		i = xbmcgui.ListItem(unicode(alt, "windows-1251"), iconImage=img, thumbnailImage=img)
		i.setInfo(type='video', infoLabels={'title': unicode(alt, "windows-1251"), 'plot': unicode(text, "windows-1251")})
		i.setProperty("IsPlayable","true")
		pl = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
		pl.clear()
		pl.add(names, i)
		xbmc.Player().play(pl)
       
def PLAY_Serii(params):
    http = urllib.unquote_plus(params['url'])
    img = urllib.unquote_plus(params['img'])
    alt = urllib.unquote_plus(params['alt'])
    name = urllib.unquote_plus(params['name'])
    text = urllib.unquote_plus(params['text'])
    i = xbmcgui.ListItem(format_s(alt)+'   '+name, iconImage=img, thumbnailImage=img)
    i.setInfo(type='video', infoLabels={'title': format_s(alt)+'   '+name, 'plot': unicode(text, "windows-1251")})
    i.setProperty("IsPlayable","true")
    pl = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    pl.clear()
    pl.add(http, i)
    xbmc.Player(xbmc.PLAYER_CORE_MPLAYER).play(pl)
        
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
	OPEN_KINO()

if mode == 'OPEN_MOVIES': OPEN_MOVIES(params)
if mode == 'OPEN_KINO': OPEN_KINO()
if mode == 'SRAVN': SRAVN(params)
if mode == 'PLAY': PLAY(params)
if mode == 'VK_com': VK_com(params)
if mode == 'SERII': SERII(params)
if mode == 'PLAY_Serii': PLAY_Serii(params)
if mode == 'search': search()
if mode == 'Blok_search': Blok_search(url)
if mode == 'stran': stran(params)