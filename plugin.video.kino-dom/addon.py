# -*- coding: utf-8 -*-

import urllib, urllib2, re, sys, json
import xbmcplugin, xbmcgui

def getHTML(url, data = False):
    headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3', 'Content-Type':'application/x-www-form-urlencoded'}
    if data == False:
        conn = urllib2.urlopen(urllib2.Request(url, urllib.urlencode({}), headers))
    else:
        conn = urllib2.urlopen(urllib2.Request(url, urllib.urlencode(data), headers))
    
    html = conn.read()
    conn.close()
    
    return html

def showkeyboard(txtMessage="",txtHeader="",passwordField=False):
    if txtMessage=='None': txtMessage=''
    keyboard = xbmc.Keyboard(txtMessage, txtHeader, passwordField)#("text to show","header text", True="password field"/False="show text")
    keyboard.doModal()
    if keyboard.isConfirmed():
        return keyboard.getText()
    else:
        return False # return ''

def Search():
    text = showkeyboard('', 'Поиск по названию')
    url = 'http://kino-dom.org/engine/ajax/search.php'
    data =  {'query' : text}
    html = getHTML(url, data)
    genre_links = re.compile('href="(http\:\/\/kino-dom\.tv\/[^\/]+\/[^\.]+\.html)"><span\sclass="searchheading">[<b>]*([^<]+)<').findall(html.decode('windows-1251').encode('utf-8'))
    for link, title in genre_links:
        addDir(title, link, 25, None)



def isLinkUseful(needle):
    haystack = ['/?do=archive', 'http://www.linecinema.org/', 'http://www.animult.tv/', 
    '/faq.html', '/agreement.html', '/copyright.html', '/reklama.html', '/contacts.html', '/news-kino-serials/']
    return needle not in haystack

def Categories():
    url = 'http://kino-dom.org'
    html = getHTML(url)
    links_place = re.compile('<div class="list-wrapper">([\s\S]+?)</div>').findall(html.decode('windows-1251').encode('utf-8'))[0]
    genre_links = re.compile('<li><a href="' + url + '(.+?)">(.+?)</a></li>').findall(links_place)
    #genre_links = re.compile('<div class="list-wrapper"><li><a href="' + url + '(.+?)">(.+?)</a></li>').findall(html.decode('windows-1251').encode('utf-8'))
    addDir('Поиск...', '', 35, None)
    for link, title in genre_links:
        if isLinkUseful(link):
            addDir(title, url + link, 20, None)

def Movies(url):
    html = getHTML(url)
    
    genre_links = re.compile('<div class="post info">\s*<a href="(.+?)">').findall(html.decode('windows-1251').encode('utf-8'))
    genre_names = re.compile('<div class="post-title">(.+?)</div>').findall(html.decode('windows-1251').encode('utf-8'))
    genre_pict = re.compile('<div style="background-image:url\((.+?)\)" class="post-image">').findall(html.decode('windows-1251').encode('utf-8'))

    next_link = re.compile('<li class="nav next"><a href="(.+?)">').findall(html.decode('windows-1251').encode('utf-8'))

    addDir("<< На главную", url, None, None)

    for i in range(0,len(genre_links)):
        addDir(genre_names[i], genre_links[i], 25, genre_pict[i])

    if len(next_link) > 0:
        addDir("Следующая страница >>", next_link[0], 20, None)

def Studios(url, title):
    html = getHTML(url)
    studios_links = re.compile('<input type="hidden" name="pl" value="(.+?)" />').findall(html.decode('windows-1251').encode('utf-8'))
    studios_names = re.compile('<li><span><a href=".+?">(.+?)</a></span></li>').findall(html.decode('windows-1251').encode('utf-8'))
    if len(studios_links) > 1:
        for i in range(1,len(studios_links)):
            addDir(studios_names[i-1], studios_links[i], 30, None)
    else:
        Videos(studios_links[0], title)

def Videos(url, title):
    html = getHTML(url)
    data = json.loads(html)

    for series in data['playlist']:
        if 'playlist' in series and len(series['playlist']) > 0:
            for sr in series['playlist']:
                addLink(series['comment'] + ': '+ sr['comment'], sr['file'])
        else:
            addLink(series['comment'], series['file'])

    #addLink(title, link)


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


def addDir(title, url, mode, picture):

    if picture == None:
        item = xbmcgui.ListItem(title, iconImage='DefaultFolder.png', thumbnailImage='')
    else:
        item = xbmcgui.ListItem(title, iconImage='DefaultFolder.png', thumbnailImage=picture)

    sys_url = sys.argv[0] + '?title=' + urllib.quote_plus(title) + '&url=' + urllib.quote_plus(url) + '&mode=' + urllib.quote_plus(str(mode))
    
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

elif mode == 25:
    Studios(url, title)

elif mode == 30:
    Videos(url, title)

elif mode == 35:
    Search()

xbmcplugin.endOfDirectory(int(sys.argv[1]))