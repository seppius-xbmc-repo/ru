# -*- coding: utf-8 -*-

import urllib, urllib2, re, sys
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
    url = 'http://linecinema.org/'
    data =  {'do': 'search', 'subaction': 'search', 'story' : text.decode('utf-8').encode('windows-1251')}
    html = getHTML(url, data)
    movie_links = re.compile('<h1>\s*<a href="(.+?)">(.+?)<\/a>\s*<\/h1>').findall(html.decode('windows-1251').encode('utf-8'))
    pictures_link = re.compile('<img\ssrc="http\:\/\/www.linecinema.org([^"]+)"\swidth="180">').findall(html.decode('windows-1251').encode('utf-8'))
    for i in range(0, len(movie_links)):
        if len(pictures_link) > i:
            addDir(movie_links[i][1], movie_links[i][0], 30, pictures_link[i])
        else:
            addDir(movie_links[i][1], movie_links[i][0], 30, None)

def isLinkUseful(needle):
    haystack = ['/index.php', '/newsz/Televydenye/100432-2008-3-11-432.html', '/newsz/500183-tex-podderzhka.html']
    return needle not in haystack

def Categories():
    url = 'http://www.linecinema.org'
    html = getHTML(url)
    genre_links = re.compile('<a href="(.+?)" title="" class="mainmenu">(.+?)</a><br />').findall(html.decode('windows-1251').encode('utf-8'))
    addDir('Поиск...', '', 35, None)
    for link, title in genre_links:
        if isLinkUseful(link):
            addDir(title, url + link, 20, None)

def Movies(url, page=1):
    html = getHTML(url + 'page/' + str(page) + '/')
    movie_links = re.compile('<h1>[\s\t\n]*<a href="(.+?)">(.+?)</a>[\s\t\n]*</h1>').findall(html.decode('windows-1251').encode('utf-8'))
    pictures_link = re.compile('<img src="(.+?)" width="180"></a>').findall(html.decode('windows-1251').encode('utf-8'))
    #next_link = re.compile('<a href="(.+?)">.+?</a></div></div>').findall(html.decode('windows-1251').encode('utf-8'))

    addDir("<< На главную", url, None, None)

    for i in range(0, len(movie_links)):
        addDir(movie_links[i][1], movie_links[i][0], 30, pictures_link[i])

    if len(movie_links) >= 15:
        addDir("Следующая страница >>", url , 20, None, str(int(page) + 1))

def Videos(url, title, picture):
    html = getHTML(url)
    link = re.compile('file:[\s\t]*"(.+?)"').findall(html.decode('windows-1251').encode('utf-8'))[0]

    addLink(title, link, picture)


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


def addLink(title, url, picture):
    if  picture == None:
        item = xbmcgui.ListItem(title, iconImage='DefaultVideo.png', thumbnailImage='')
    else:
        item = xbmcgui.ListItem(title, iconImage='DefaultVideo.png', thumbnailImage='http://www.linecinema.org/' + picture)
    item.setInfo( type='Video', infoLabels={'Title': title} )

    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=item)


def addDir(title, url, mode, picture, page=None):
    sys_url = sys.argv[0] + '?title=' + urllib.quote_plus(title) + '&url=' + urllib.quote_plus(url) + '&mode=' + urllib.quote_plus(str(mode))
    if  picture == None:
        item = xbmcgui.ListItem(title, iconImage='DefaultFolder.png', thumbnailImage='')
    else:
        item = xbmcgui.ListItem(title, iconImage='DefaultFolder.png' , thumbnailImage='http://www.linecinema.org' + picture)    
        sys_url += '&picture=' + urllib.quote_plus(str(picture))
    if page != None:
        sys_url += '&page=' + urllib.quote_plus(str(page))
    item.setInfo(type='Video', infoLabels={'Title': title})

    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=sys_url, listitem=item, isFolder=True)


params = get_params()
url = None
title = None
mode = None
picture = None
page = 1

try:
    title = urllib.unquote_plus(params['title'])
except:
    pass
try:
    url = urllib.unquote_plus(params['url'])
except:
    pass
try:
    mode = int(params['mode'])
except:
    pass
try:
    picture = params['picture']
except:
    pass
try:
    page = int(params['page'])
except:
    pass

if mode == None:
    Categories()
elif mode == 20:
    Movies(url, page)
elif mode == 30:
    Videos(url, title, picture)
elif mode == 35:
    Search()

xbmcplugin.endOfDirectory(int(sys.argv[1]))