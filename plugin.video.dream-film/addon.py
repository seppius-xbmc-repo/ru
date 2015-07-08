#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib, urllib2, re, sys, os, json
import xbmcplugin, xbmcgui, xbmcaddon, xbmc

h = int(sys.argv[1])
xbmcplugin.setContent(h, 'movies')
icon = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'icon.png'))

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
	    
def DEC(s):
	s=s.decode('windows-1251').encode('utf-8')
	return s

def genre():
	wurl = 'http://dream-film.net/'
	http = GET(wurl)
	if http == None: return False
	r1 = re.compile('<div id="content" class="cont_pad">(.*?)</ul>',re.S).findall(http)
	r2 = re.compile('<li><a href="(.+?)">(.+?)</a></li>',re.S).findall(r1[0])
	for href, name in r2:
		i = xbmcgui.ListItem(unicode(name, "windows-1251"), iconImage=icon, thumbnailImage=icon)
		u  = sys.argv[0] + '?mode=OPEN_MOVIES'
		u += '&url=%s'%urllib.quote_plus('http://dream-film.net/' + href)
		u += '&name=%s'%urllib.quote_plus(name)
		xbmcplugin.addDirectoryItem(h, u, i, True)
	
	xbmcplugin.endOfDirectory(h)

def OPEN_MOVIES(params):
	http = GET(urllib.unquote_plus(params['url']))
	if http == None: return False
	r1 = re.compile('<div id=\'dle-content\'>(.*?)<div class="small_box2 premiers">',re.S).findall(http)
	r2 = re.compile('<a href="([^"]+)"><img title=".*?" alt="(.*?)"',re.S).findall(r1[0])
	r3 = re.compile('src="http://dream-film.net/(.+?)"',re.I).findall(r1[0])
	ii = 0
	for href, alt in r2:
			img = 'http://dream-film.net/' + r3[ii]
			ii = ii + 1
			i = xbmcgui.ListItem(unicode(alt, "windows-1251"), iconImage=img, thumbnailImage=img)
			u  = sys.argv[0] + '?mode=FILMS'
			u += '&url=%s'%urllib.quote_plus(href)
			u += '&img=%s'%urllib.quote_plus(img)
			u += '&alt=%s'%urllib.quote_plus(alt)
			xbmcplugin.addDirectoryItem(h, u, i, True)
	try:
		rp = re.compile('div class="navigation">(.*?)</div>', re.DOTALL).findall(http)[0]
		rp2 = re.compile('<span class="nav_ext">...</span> <a href=".*?">24</a> <a href="(.*?)">(.*?)</a>').findall(rp)
		for href, nr in rp2:
			u = sys.argv[0] + '?mode=OPEN_MOVIES'
			u += '&url=%s'%urllib.quote_plus(href)
			i = xbmcgui.ListItem('[COLOR yellow]Далее > [/COLOR] %s '%nr, 
                        iconImage='special://home/addons/next.png', 
                        thumbnailImage='special://home/addons/next.png')
			xbmcplugin.addDirectoryItem(h, u, i, True)
	except:
		pass
	xbmcplugin.endOfDirectory(h)
 
def FILMS(params):
	http = GET(urllib.unquote_plus(params['url']))
	if http == None: return False
	r2 = re.compile('<video style=".*?" src="([^"]+)" type=',re.S).findall(http)
	r4 = re.compile('<div id="news-id-.*?" style="display.*?">(.*?)</div>',re.S).findall(http)
	if len(r2) == 0:
		FILMS_Serii(params)
	for hre in r2:
		text = r4[0]
		text = re.sub('<.*>',' ', text)
		img = urllib.unquote_plus(params['img'])
		alt = urllib.unquote_plus(params['alt'])
		i = xbmcgui.ListItem(unicode(alt, "windows-1251"), iconImage=img, thumbnailImage=img)
		i.setInfo(type='video', infoLabels={'title': unicode(alt, "windows-1251"), 'plot': unicode(text, "windows-1251")})
		i.setProperty("IsPlayable","true")
		pl = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
		pl.clear()
		pl.add(hre, i)
		xbmc.Player().play(pl)

# серии
def FILMS_Serii(params):
	http = GET(urllib.unquote_plus(params['url']))
        if http == None: return False
	r2 = re.compile("fl:'(.*?)'",re.S).findall(http)
	r4 = re.compile('<div id="news-id-.*?" style="display.*?">(.*?)</div>',re.S).findall(http)
	if len(r2) >= 1:
		http = GET(r2[0])
		r2 = re.compile('"comment":"([^"]+)","file":"([^"]+)"',re.S).findall(http)
        for name, href in r2:
		img = urllib.unquote_plus(params['img'])
		alt = urllib.unquote_plus(params['alt'])
		text = r4[0]
		text = re.sub('<.*>',' ', text)
		i = xbmcgui.ListItem(unicode(DEC(alt)+'   '+name, "utf-8"), iconImage=img, thumbnailImage=img)
		i.setInfo(type='video', infoLabels={'title': unicode(alt, "windows-1251"), 'plot': unicode(text, "windows-1251")})
		u  = sys.argv[0] + '?mode=PLAY'
		u += '&img=%s'%urllib.quote_plus(img)
		u += '&url=%s'%urllib.quote_plus(href)
		u += '&alt=%s'%urllib.quote_plus(alt)
		u += '&name=%s'%urllib.quote_plus(name)
		u += '&text=%s'%urllib.quote_plus(text)
		xbmcplugin.addDirectoryItem(h, u, i, True)
        xbmcplugin.endOfDirectory(h)
		
def PLAY(params):
		http = urllib.unquote_plus(params['url'])
		name = urllib.unquote_plus(params['name'])
		alt = urllib.unquote_plus(params['alt'])
		img = urllib.unquote_plus(params['img'])
		text = urllib.unquote_plus(params['text'])
		i = xbmcgui.ListItem(unicode(DEC(alt)+'   '+name, "utf-8"), iconImage=img, thumbnailImage=img)
		i.setInfo(type='video', infoLabels={'title': unicode(alt, "windows-1251"), 'plot': unicode(text, "windows-1251")})
		i.setProperty("IsPlayable","true")
		pl = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
		pl.clear()
		pl.add(http, i)
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
if mode == 'SERII': SERII()
if mode == 'genre': genre()
if mode == 'PLAY': PLAY(params)
if mode == 'FILMS': FILMS(params)
if mode == 'FILMS_Serii': FILMS_Serii(params)

