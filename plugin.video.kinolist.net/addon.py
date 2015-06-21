# -*- coding: utf-8 -*-

import urllib, urllib2, re, sys, os
import xbmc, xbmcgui, xbmcplugin, xbmcaddon

#-- !!
from BeautifulSoup  import BeautifulSoup

Addon = xbmcaddon.Addon(id='plugin.video.kinolist.net')
icon = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'),'icon.png'))
fcookies = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'), r'resources', r'data', r'cookies.txt'))

# load XML library
try:
    sys.path.append(os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib'))
    from BeautifulSoup  import BeautifulSoup
except:
    try:
        sys.path.insert(0, os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib'))
        from BeautifulSoup  import BeautifulSoup
    except:
        sys.path.append(os.path.join(os.getcwd(), r'resources', r'lib'))
        from BeautifulSoup  import BeautifulSoup
        icon = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'icon.png'))

import HTMLParser
hpar = HTMLParser.HTMLParser()

h = int(sys.argv[1])

def showMessage(heading, message, times = 3000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))

host    = 'http://kinolist.net/'
#-- !!


def getHTML(url):
    headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3', 'Content-Type':'application/x-www-form-urlencoded'}
    conn = urllib2.urlopen(urllib2.Request(url, urllib.urlencode({}), headers))

    html = conn.read()
    conn.close()

    return html

def isLinkUseful(needle):
    haystack = ['/']
    for a in haystack:
        if needle == a:
            return False

    return True

def Categories():
    html = getHTML(host+'films-online-good-quality/')
	#genre_links = re.compile('<td><a href="http://kinolist.net/smotret-(.+?)" class="menuItem">(.+?)</a></td>').findall(html)
    soup = BeautifulSoup(html)
    '''
	for link, title in genre_links:
	    if isLinkUseful(link):
	        addDir(title, url + link, 20)
    '''
    for rec in soup.find('div', {'class' : "left-adv"}).findAll('tr'):
        link    = rec.find('a')['href']+'/'
        title   = rec.find('a').text.encode('utf-8')
        if link != '#':
	        addDir(title, link, 20)


def Movies(url):
    print url
    html = getHTML(url)
	#movie_links = re.compile('<h3><a href="(.+?)">(.+?)</a></h3>').findall(html)
    soup = BeautifulSoup(html)

    #-- получаем текущую страницу и кол-во страниц в категории
    max_page = 0
    for rec in soup.find('nav', {'class' : "paginator"}).findAll('li'):
        try:
            if rec['class'] == "current":
                page = int(rec.find('a').text)
        except:
            pass

        ps = rec.find('a')['href']
        pn = ps[ps.find('/', -1):]
        try:
            pn = int(pn)
        except:
            pn = 1

        if max_page < pn:
            max_page = pn

    #-- добавляем переход на предыдущую страницу
    if page > 1:
        link  = url[:url.find('/', -1)]+'/'+str(page-1)
        title = '[COLOR FF00FF00][PAGE -1][/COLOR]'
        addDir(title, link, 20)

    '''
	for link, title in movie_links:
	    addDir(title, link, 30)
    '''
    for rec in soup.findAll('div', {'class' : "item"}):
        title = rec.find('h3').find('a').text.encode('utf-8')
        link  = rec.find('h3').find('a')['href']
        addDir(title, link, 30)

    #-- добавляем переход на следующую страницу
    if page < max_page:
        link  = url[:url.find('/', -1)]+'/'+str(page+1)
        title = '[COLOR FF00FF00][PAGE +1][/COLOR]'
        addDir(title, link, 20)

def Videos(url, title):
	html = getHTML(url)
	link = re.compile('<param name="flashvars" value=".+?file=(.+?)"').findall(html)[0]

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