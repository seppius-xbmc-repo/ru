# -*- coding: utf-8 -*-

import urllib, urllib2, re, sys
import xbmcplugin, xbmcgui

def getHTML(url):
    headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3', 'Content-Type':'application/x-www-form-urlencoded'}
    conn = urllib2.urlopen(urllib2.Request(url, urllib.urlencode({}), headers))
    
    html = conn.read()
    conn.close()
    
    return html

def isLinkUseful(needle):
    haystack = ['/index.php', '/newsz/Televydenye/100432-2008-3-11-432.html', '/newsz/500183-tex-podderzhka.html']
    for a in haystack:
        if needle == a:
            return False

    return True

def Categories():
	url = 'http://www.linecinema.org'
	html = getHTML(url)
	genre_links = re.compile('<a href="(.+?)" title="" class="mainmenu">(.+?)</a><br />').findall(html.decode('windows-1251').encode('utf-8'))

	for link, title in genre_links:
	    if isLinkUseful(link):
	        addDir(title, url + link, 20)

def Movies(url):
	html = getHTML(url)
	movie_links = re.compile('<h1> <a href="(.+?)">(.+?)</a>   </h1>').findall(html.decode('windows-1251').encode('utf-8'))

	for link, title in movie_links:
	    addDir(title[:-12], link, 30)

def Videos(url, title):
	html = getHTML(url)
	link = re.compile('file:   "(.+?)"').findall(html.decode('windows-1251').encode('utf-8'))[0]

	addLink(title, link)

	    


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


def addLink(title, url):
    item = xbmcgui.ListItem(title, iconImage='DefaultVideo.png', thumbnailImage='')
    item.setInfo( type='Video', infoLabels={'Title': title} )

    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=item)


def addDir(title, url, mode):
    sys_url = sys.argv[0] + '?title=' + urllib.quote_plus(title) + '&url=' + urllib.quote_plus(url) + '&mode=' + urllib.quote_plus(str(mode))

    item = xbmcgui.ListItem(title, iconImage='DefaultFolder.png', thumbnailImage='')
    item.setInfo( type='Video', infoLabels={'Title': title} )

    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=sys_url, listitem=item, isFolder=True)


params = get_params()
url    = None
title  = None
mode   = None

try:    title = urllib.unquote_plus(params['title'])
except: pass

try:    url = urllib.unquote_plus(params['url'])
except: pass

try:    mode = int(params['mode'])
except: pass

if mode == None:
    Categories()

elif mode == 20:
    Movies(url)

elif mode == 30:
    Videos(url, title)

xbmcplugin.endOfDirectory(int(sys.argv[1]))