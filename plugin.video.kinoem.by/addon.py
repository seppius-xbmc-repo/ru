#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib, urllib2, re, sys, os, json
import xbmcplugin, xbmcgui, xbmcaddon, xbmc

h = int(sys.argv[1])

xbmcplugin.setContent(h, 'movies')
icon = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''), 'icon.png'))

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
		
def genre():
        u = sys.argv[0] + '?mode=search'
        i = xbmcgui.ListItem('[ ПОИСК ]', iconImage=icon, thumbnailImage=icon)
        xbmcplugin.addDirectoryItem(h, u, i, True)

	wurl = 'http://kinoem.by/'
	http = GET(wurl)
	if http == None: return False
	r2 = re.compile('<li><a href="((?<=href=")\w.+?/)">([^>]+)</a></li>',re.S).findall(http)
	for href, name in r2:
		i = xbmcgui.ListItem(unicode(name, "utf-8"), iconImage=icon, thumbnailImage=icon)
		u  = sys.argv[0] + '?mode=OPEN_MOVIES'
		u += '&url=%s'%urllib.quote_plus('http://kinoem.by/'+href)
		u += '&name=%s'%urllib.quote_plus(name)
		xbmcplugin.addDirectoryItem(h, u, i, True)
	
	xbmcplugin.endOfDirectory(h)
       
def search(params):
	keyboard = xbmc.Keyboard()
	keyboard.setHeading('Что ищем?')
	keyboard.doModal()
	if keyboard.isConfirmed():
		query = keyboard.getText()
                query = re.sub(r' ','+', query)
                query = re.sub(r'0','а', query)
                query = re.sub(r'1','б', query)
                query = re.sub(r'2','в', query)
                query = re.sub(r'3','г', query)
                query = re.sub(r'4','д', query)
                query = re.sub(r'5','е', query)
                query = re.sub(r'6','ж', query)
                query = re.sub(r'7','з', query)
                query = re.sub(r'8','и', query)
                query = re.sub(r'9','й', query)
                query = re.sub(r'a','к', query)
                query = re.sub(r'b','л', query)
                query = re.sub(r'c','м', query)
                query = re.sub(r'd','н', query)
                query = re.sub(r'e','о', query)
                query = re.sub(r'f','п', query)
                query = re.sub(r'g','р', query)
                query = re.sub(r'h','с', query)
                query = re.sub(r'i','т', query)
                query = re.sub(r'j','у', query)
                query = re.sub(r'k','ф', query)
                query = re.sub(r'l','х', query)
                query = re.sub(r'm','ц', query)
                query = re.sub(r'n','ч', query)
                query = re.sub(r'o','ш', query)
                query = re.sub(r'p','щ', query)
                query = re.sub(r'q','ы', query)
                query = re.sub(r'r','э', query)
                query = re.sub(r's','ю', query)
                query = re.sub(r't','я', query)
                query = re.sub(r'u','ё', query)
                query = re.sub(r'v','ь', query)
                query = re.sub(r'w','ъ', query)
		url = ('http://kinoem.by/?do=search&subaction=search&story='+query)
		Blok_search({'url':urllib.quote_plus(url)})
	else:
		return False

def Blok_search(params):
	http = GET(urllib.unquote_plus(params['url']))
	r2 = re.compile('<a href="([^"]+)"><img src="([^"]+)" alt="([^"]+)" /></a>',re.S).findall(http)
	if len(r2) == 0:
		showMessage('ФИЛЬМЫ НЕ НАЙДЕНЫ', '')
		return False
	for href, img, alt in r2:
		img = 'http://kinoem.by/'+img
		i = xbmcgui.ListItem(unicode(alt, "utf-8"), iconImage=img, thumbnailImage=img)
		u  = sys.argv[0] + '?mode=SR_Cat'
		u += '&url=%s'%urllib.quote_plus(href)
		u += '&alt=%s'%urllib.quote_plus(alt)
		u += '&img=%s'%urllib.quote_plus(img)
		xbmcplugin.addDirectoryItem(h, u, i, True)
	xbmcplugin.endOfDirectory(h)
		
def OPEN_MOVIES(params):
	http = GET(urllib.unquote_plus(params['url']))
	r2 = re.compile('<div class="gpr">(.*?)</div>.*?<a href="([^"]+)" ><img src="(.*?)" width=".*?" height=".*?" alt=".*?" title="(.*?)" /></a>',re.S).findall(http)
	for god, href, img, alt in r2:
			img = 'http://kinoem.by/'+img
			i = xbmcgui.ListItem(unicode(alt+'  '+'('+god+')', "utf-8"), iconImage=img, thumbnailImage=img)
			u  = sys.argv[0] + '?mode=SR_Cat'
			u += '&url=%s'%urllib.quote_plus(href)
			u += '&img=%s'%urllib.quote_plus(img)
			u += '&alt=%s'%urllib.quote_plus(alt)
			xbmcplugin.addDirectoryItem(h, u, i, True)
	try:
		
		rp2 = re.compile('<a href="(.*?)">(вперед)</a>').findall(http)
		for href, nr in rp2:
			u = sys.argv[0] + '?mode=OPEN_MOVIES'
			u += '&url=%s'%urllib.quote_plus(href)
			i = xbmcgui.ListItem('[COLOR yellow]Далее > [/COLOR]')
			xbmcplugin.addDirectoryItem(h, u, i, True)
	except:
		pass
	xbmcplugin.endOfDirectory(h)

def SR_Cat(params):
	http = GET(urllib.unquote_plus(params['url']))
	if http is None:		return False
	if "-sezon.html" in http:
		SEZON(params)
	else:
		SERII(params)

def SEZON(params):
	http = GET(urllib.unquote_plus(params['url'])).replace(' class="selected"','')
	r1 = re.compile('<div class="h_mnu_01">(.*?)</div>',re.S).findall(http)
	r2 = re.compile('<li><a href="([^"]+)">(.*?)</a></li>',re.S).findall(r1[0])
	if len(r2) == 0:
		SERII(params)
		return False
	for href, name in r2:
		img = urllib.unquote_plus(params['img'])
		alt = urllib.unquote_plus(params['alt'])
		i = xbmcgui.ListItem(unicode(alt+'  '+name, "utf-8"), iconImage=img, thumbnailImage=img)
		u  = sys.argv[0] + '?mode=SERII'
		u += '&img=%s'%urllib.quote_plus(img)
		u += '&url=%s'%urllib.quote_plus('http://kinoem.by/'+href)
		u += '&alt=%s'%urllib.quote_plus(alt)
		u += '&name=%s'%urllib.quote_plus(name)
		xbmcplugin.addDirectoryItem(h, u, i, True)
        xbmcplugin.endOfDirectory(h)
		
def SERII(params):
	http = GET(urllib.unquote_plus(params['url']))
	r2 = re.compile('<iframe src="(.*?)"\s+width="',re.S).findall(http)
	http = GET(r2[0])
	r1 = re.compile('<script type="text/javascript" src="(htt.*?//[^\/]+).*?"></script>',re.S).findall(http)
	serv = r1[0]
	r2 = re.compile("'file':'(.*?)','comment':'(.*?)'",re.S).findall(http)
	if len(r2) == 0:
		PLAY(params)
		return False
	for href, name in r2:
		href = serv + href
		img = urllib.unquote_plus(params['img'])
		alt = urllib.unquote_plus(params['alt'])
		i = xbmcgui.ListItem(unicode(alt+'  '+name, "utf-8"), iconImage=img, thumbnailImage=img)
		u  = sys.argv[0] + '?mode=PLAY_Serii'
		u += '&img=%s'%urllib.quote_plus(img)
		u += '&url=%s'%urllib.quote_plus(href)
		u += '&alt=%s'%urllib.quote_plus(alt)
		u += '&name=%s'%urllib.quote_plus(name)
		xbmcplugin.addDirectoryItem(h, u, i, True)
        xbmcplugin.endOfDirectory(h)
		
def PLAY_Serii(params):
		http = urllib.unquote_plus(params['url'])
		name = urllib.unquote_plus(params['name'])
		alt = urllib.unquote_plus(params['alt'])
		img = urllib.unquote_plus(params['img'])
		i = xbmcgui.ListItem(unicode(alt+'  '+name, "utf-8"), iconImage=img, thumbnailImage=img)
		i.setProperty("IsPlayable","true")
		pl = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
		pl.clear()
		pl.add(http, i)
		xbmc.Player().play(pl)
		
def PLAY(params):
	http = GET(urllib.unquote_plus(params['url']))
	if http == None: return False
	r2 = re.compile('<iframe src="([^"]+)"\s+width="',re.S).findall(http)
	if len(r2) == 1:
            http = GET(r2[0])
            r2 = re.compile('"file":"(.*?)"',re.S).findall(http)
	for names in r2:
		img = urllib.unquote_plus(params['img'])
		alt = urllib.unquote_plus(params['alt'])
		i = xbmcgui.ListItem(unicode(alt, "utf-8"), iconImage=img, thumbnailImage=img)
		i.setProperty("IsPlayable","true")
		pl = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
		pl.clear()
		pl.add(names, i)
		xbmc.Player().play(pl)

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
	genre()

if mode == 'OPEN_MOVIES': OPEN_MOVIES(params)
if mode == 'genre': genre()
if mode == 'PLAY': PLAY(params)
if mode == 'search': search(params)
if mode == 'SR_Cat': SR_Cat(params)
if mode == 'SERII': SERII(params)
if mode == 'PLAY_Serii': PLAY_Serii(params)
if mode == 'SEZON': SEZON(params)
if mode == 'Blok_search': Blok_search(params)