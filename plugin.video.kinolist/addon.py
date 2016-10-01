#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib, urllib2, re, sys, os, json
import xbmcplugin, xbmcgui, xbmcaddon, xbmc

h = int(sys.argv[1])

addon = xbmcaddon.Addon(id='plugin.video.kinolist')
icon = os.path.join( addon.getAddonInfo('path'), "icon.png" )
xbmcplugin.setContent(h, 'movies')

def showMessage(heading, message, times = 5000):
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

host    = 'http://kinolist.org/'
        
def genre():
        u = sys.argv[0] + '?mode=search'
        i = xbmcgui.ListItem('[ ПОИСК ]', iconImage=icon, thumbnailImage=icon)
        xbmcplugin.addDirectoryItem(h, u, i, True)
	http = GET(host+'films-online-good-quality/')
	if http == None: return False
	r1 = re.compile('<div class="left-adv">(.*?)</div>',re.S).findall(http)
	r2 = re.compile('<a href="(.*?)" class="menuItem">(.*?)</a>',re.S).findall(r1[0])
	for href, name in r2:
		i = xbmcgui.ListItem(unicode(name, "utf-8"), iconImage=icon, thumbnailImage=icon)
		u  = sys.argv[0] + '?mode=OPEN_MOVIES'
		u += '&url=%s'%urllib.quote_plus(href)
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
		url = ('http://kinolist.org/?q='+query+'&submit_search=')
		OPEN_MOVIES({'url':urllib.quote_plus(url)})
	else:
		return False
	
def OPEN_MOVIES(params):
	http = GET(urllib.unquote_plus(params['url']))
	if http == None: return False
	r1 = re.compile('<div class="content">(.*?)<div class="page-footer"',re.S).findall(http)
	r2 = re.compile('<h3><a href="([^"]+)">(.*?)</a></h3>',re.S).findall(r1[0])
	r3 = re.compile('<img src="(.*?)"  alt="',re.S).findall(r1[0])
	r4 = re.compile('</dl>\s*<p>(.*?)</p>',re.S).findall(http)
	if len(r2) == 0:
		dialog = xbmcgui.Dialog()
		dialog.ok('ВНИМАНИЕ!', 'Нет такой страницы.', 'В этом разделе меньше страниц.')
		return False
	ii = 0
	for href, alt in r2:
			img = r3[ii]
			text = r4[ii]
			ii = ii + 1
			i = xbmcgui.ListItem(unicode(alt, "utf-8"), iconImage=img, thumbnailImage=img)
			i.setInfo(type='video', infoLabels={'title': unicode(alt, "utf-8"), 'plot': unicode(text, "utf-8")})
			u  = sys.argv[0] + '?mode=Play_kino'
			u += '&url=%s'%urllib.quote_plus(href)
			u += '&img=%s'%urllib.quote_plus(img)
			u += '&alt=%s'%urllib.quote_plus(alt)
			u += '&text=%s'%urllib.quote_plus(text)
			xbmcplugin.addDirectoryItem(h, u, i, True)
	try:
		rp = re.compile('<nav class="paginator">(.*?)</nav>', re.DOTALL).findall(http)[0]
		rp2 = re.compile('<li class="current"><a href="#">[0-9]+</a></li>\s*<li><a href="(.*?)">(.*?)</a></li>').findall(rp)
		for href, nr in rp2:
			u = sys.argv[0] + '?mode=OPEN_MOVIES'
			u += '&url=%s'%urllib.quote_plus(href)
			i = xbmcgui.ListItem('[COLOR yellow]Далее >[/COLOR] %s '%nr, iconImage='special://home/addons/next.png', thumbnailImage='special://home/addons/next.png')
			xbmcplugin.addDirectoryItem(h, u, i, True)
	except:
		pass
	try:
		rp = re.compile('(http://kinolist\.org.*?[^0-9]+)').findall(href)
		for hr in rp:
			ggg = hr#[0]
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
		url = (http+query)
		OPEN_MOVIES({'url':urllib.quote_plus(url)})
	else:
		return False
    
def Play_kino(params):#фильм готово
	img = urllib.unquote_plus(params['img'])
	alt = urllib.unquote_plus(params['alt'])
	text = urllib.unquote_plus(params['text'])
	http = GET(urllib.unquote_plus(params['url']))
	if http == None: return False
	r2 = re.compile('<param name="flashvars" value=".+?file=(.+?[^&]+)&').findall(http)
	for name in r2:
		i = xbmcgui.ListItem(unicode(alt, "windows-1251"), iconImage=img, thumbnailImage=img)
		i.setInfo(type='video', infoLabels={'title': unicode(alt, "utf-8"), 'plot': unicode(text, "utf-8")})
		i.setProperty("IsPlayable","true")
		pl = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
		pl.clear()
		pl.add(name, i)
		xbmc.Player().play(pl)

def MOVIES_search(params):
	http = GET(urllib.unquote_plus(params['url']))
	if http == None: return False
	r2 = re.compile('<div class="postershort"><a href="(.*?)" ><\!--dle_image_begin:(.*?)\|--><img src=".*?" alt=".*?" title="(.*?)"  /><\!--dle_image_end--></a></div>',re.S).findall(http)
	#r4 = re.compile('<span style="font-size:12pt;"><!--/sizestart-->(.*?)<!--sizeend--></span><!--/sizeend--></div>',re.S).findall(http)
	#ii = 0
	for href, img, alt in r2:
			text = alt
			#text = re.sub('<.*?>','', text)
			#ii = ii + 1
			i = xbmcgui.ListItem(unicode(alt, "windows-1251"), iconImage=img, thumbnailImage=img)
			#i.setInfo(type='video', infoLabels={'title': unicode(alt, "windows-1251"), 'plot': unicode(text, "windows-1251")})
			u  = sys.argv[0] + '?mode=SRAVN'
			u += '&url=%s'%urllib.quote_plus(href)
			u += '&img=%s'%urllib.quote_plus(img)
			u += '&alt=%s'%urllib.quote_plus(alt)
			u += '&text=%s'%urllib.quote_plus(text)
			xbmcplugin.addDirectoryItem(h, u, i, True)
	try:
		rp = re.compile('<div class="pagination">(.*?)</div>', re.DOTALL).findall(http)[0]
		rp2 = re.compile('<a href="(.*?)" class="page_btn next_page">(.*?)</a>').findall(rp)
		for href, nr in rp2:
			u = sys.argv[0] + '?mode=MOVIES_search'
			u += '&url=%s'%urllib.quote_plus(href)
			i = xbmcgui.ListItem('[COLOR yellow]Далее >[/COLOR] %s '%nr, iconImage='special://home/addons/next.png', thumbnailImage='special://home/addons/next.png')
			xbmcplugin.addDirectoryItem(h, u, i, True)
	except:
		pass
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
	genre()

if mode == 'OPEN_MOVIES': OPEN_MOVIES(params)
if mode == 'genre': genre()
if mode == 'search': search(params)
if mode == 'MOVIES_search': MOVIES_search(params)
if mode == 'Play_kino': Play_kino(params)
if mode == 'stran': stran(params)