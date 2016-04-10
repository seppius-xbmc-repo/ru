# coding: utf8
#!/usr/bin/python

from __future__ import unicode_literals

import urllib, urllib2, os, re, sys, json, urlparse

import requests
import logging

import xbmc, xbmcaddon, xbmcgui, xbmcplugin

from bs4 import BeautifulSoup as bs


REMOTE_DBG = False 

# append pydev remote debugger
if REMOTE_DBG:
    # Make pydev debugger works for auto reload.
    # Note pydevd module need to be copied in XBMC\system\python\Lib\pysrc
    try:
        import pysrc.pydevd as pydevd  # with the addon script.module.pydevd, only use `import pydevd`
    # stdoutToServer and stderrToServer redirect stdout and stderr to eclipse console
        pydevd.settrace('localhost', stdoutToServer=True, stderrToServer=True)
    except ImportError:
        sys.stderr.write("Error: " + 
            "You must add org.python.pydev.debug.pysrc to your PYTHONPATH.")
        sys.exit(1)

__settings__ = xbmcaddon.Addon(id='plugin.video.zoomby.ru')
h = int(sys.argv[1])

xbmcplugin.setContent(h, 'movies')

plugin_path = __settings__.getAddonInfo('path').replace(';', '')
plugin_icon = xbmc.translatePath(os.path.join(plugin_path, 'icon.png'))
context_path = xbmc.translatePath(os.path.join(plugin_path, 'default.py'))

headers = {
           "User-Agent": "Mozilla/5.0 (Windows NT 6.2; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
}

categories = ['cartoons', 'shows', 'sport']

pl=xbmc.PlayList(1)
pl.clear()

def Alert(title, message):
    xbmcgui.Dialog().ok(title, message)

def Notificator(title, message, timeout=1000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (title, message, timeout, plugin_icon))

def Get(url):
    r = requests.get(url, headers=headers)
    html = r.text
    return html


def Main(main_url):
    addDir('Поиск', site_url, mode="SEARCH")
    if main_url == None :
        main_url = site_url
        html = Get(main_url)
        soup = bs(html, "html.parser")
        content = soup.find('ul', {'class': 'main_menu'}).find_all('a', attrs={'class': 'main_menu_item_lnk'})
        for num in content:
            if 'news' not in num['href'] and 'deti' not in num['href'] and 'music' not in num['href'] :
                if 'sport' in num['href'] :
                    addDir(num.text, addUrlParams(site_url + num['href']), mode="CONTENT")
                else :
                    addDir(num.text, site_url + num['href'])
    else :
        print main_url
        cat = main_url.partition(site_url + '/')[-1] #.rpartition('?')[0]
        soup = bs(Get(main_url), "html.parser")
        content = None
        if 'films' in main_url:
            content = soup.find('ul', attrs={'class': 'main_menu'}).find_all('li', attrs={'class': 'mseries_cont'})[1].find('div', {'class': 'submenu01_cont'}).find_all('a')
        elif 'series' in main_url:
            content = soup.find('ul', attrs={'class': 'main_menu'}).find_all('li', attrs={'class': 'mseries_cont'})[0].find('div', {'class': 'submenu01_cont'}).find_all('a')
        elif (cat in main_url) and (cat in categories):
            content = soup.find('ul', attrs={'class': 'main_menu'}).find('li', attrs={'class': 'm' + cat + '_cont'}).find('div', {'class': 'submenu01_cont'}).find_all('a')

        if content:   
            for num in content:
                label = num.text
                if label == '':
                    label = 'ТНТ'
                addDir(label, addUrlParams(site_url + num['href']), mode="CONTENT")
        
def addDir(title, url, iconImg="DefaultVideo.png", mode="", inbookmarks=False):
    sys_url = sys.argv[0] + '?url=' + urllib.quote_plus(url) + '&mode=' + urllib.quote_plus(str(mode))
    item = xbmcgui.ListItem(title, iconImage=iconImg, thumbnailImage=iconImg)
    item.setInfo(type='Video', infoLabels={'title': title})
    xbmcplugin.addDirectoryItem(handle=h, url=sys_url, listitem=item, isFolder=True)

def addLink(title, url, iconImg="DefaultVideo.png"):
    sys_url = sys.argv[0] + '?url=' + urllib.quote_plus(url) + '&mode=' + urllib.quote_plus('PLAY_URL')
    item = xbmcgui.ListItem(title, iconImage=iconImg, thumbnailImage=iconImg)
    item.setProperty('IsPlayable', 'true')
    item.setInfo(type='Video', infoLabels={'title': title})
    xbmc.PlayList(1).add(sys_url, item)
    xbmcplugin.addDirectoryItem(h, sys_url, item)
    
def addUrlParams(url, p=1):
    params = {'offset':0, 'p':p}
    url_parts = list(urlparse.urlparse(url))    
    url_parts[4] = urllib.urlencode(params)
    print url_parts[4]
    return urlparse.urlunparse(url_parts)

def Content(url):
    html = Get(url)
    content = json.loads(html)
    print url
#     if 'series' in url:
    for num in content['catalog']:
        addDir(num['title'] + ' [' + num['year'] + ']', site_url + num['url'], mode="SERIALS", iconImg=num['preview'])
#     else:
#         for num in content['catalog']:
#             addLink(num['title'] + ' [' + num['year'] + ']', site_url + num['url'], iconImg=num['preview'])
         
    if 'next' in content:
        addDir('---Следующая страница---', addUrlParams(url, content['next']), mode="CONTENT", iconImg=plugin_icon)

def Serials(url):
    html = Get(url)
    content = bs(html, "html.parser")
    series = content.find('div', {'id': 'series_cont01'})
    if series :
        series = series.find('div', {'class': 'panel01_cont_catalog'}).find_all('a')
        for num in series:
            url = num['href']
            if url[0] != '/':
                url = '/watch/' + url
            addLink(num.strong.text, site_url + url, iconImg=num.img['src'])
    else :
        url = GetUrl(content)
        title = content.find('div', {'class': 'content_unit_heading'})
        img = content.find('img', {'class': 'content_preview01'})
        if img :
            item = xbmcgui.ListItem(title.text.strip(), iconImage=img['src'], thumbnailImage=img['src'])
        else :
            item = xbmcgui.ListItem(title.text.strip(), iconImage="DefaultVideo.png", thumbnailImage="DefaultVideo.png")
        item.setProperty('IsPlayable', 'true')
        item.setInfo(type='Video', infoLabels={'title': title.text.strip()})
        #xbmc.PlayList(1).add(sys_url, item)
        xbmcplugin.addDirectoryItem(h, url, item)
        #addLink(title.text.strip(), url, iconImg=img['src'])


def Search():
    kbd = xbmc.Keyboard()
    kbd.setDefault('')
    kbd.setHeading("Поиск")
    kbd.doModal()
    if kbd.isConfirmed():
        SearchStr = kbd.getText()
        url = site_url + '/api/suggest.json?q=' + SearchStr.decode('utf-8')
        html = Get(url.encode('utf-8'))
        content = json.loads(html)
        print content
        if (content['success']) :
            for num in content['titles']:
                addDir(num['name'] + ' [' + num['info'] + ']', site_url + num['url'], mode="SERIALS", iconImg=num['preview'])
    else:
        return False

def PlayUrl(url):
    html = Get(url);
    soup = bs(html, "html.parser")
    url = GetUrl(soup)
    i = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(h, True, i)

def GetUrl(soup):
    js = soup.find('div', {'class':'content_unit_heading'}).findNext('script').encode('utf-8')

    js = '{%s}' % (js.decode('utf-8').split('{', 1)[1].rsplit(',')[0])
    #print js.encode('utf-8')
    js = re.sub(ur'([\s*{\s*,])([a-z]\w*):', ur'\1"\2":', js)
    js = js.replace("'", '"')
    #print js.encode('utf-8')
    json_data = json.loads(js)
    #print json_data
    
    soup = bs(Get(json_data['video']), "html.parser").find('video')
    if 'rutube' in soup['streamer'] :
        url = GetRutubeUrl(soup['streamer'])
    else :
        url = soup['streamer'] + soup['file']
    return url

def GetRutubeUrl(id):
    try:
        id = id.partition('rutube://')[-1]
        url = 'http://rutube.ru/api/play/options/' + id + '/?format=xml'
        http = Get(url)
        soup = bs(http, "html.parser")
        url = soup.find('video_balancer').find('m3u8').text
    except:
        return None
    return url

    
def get_params():
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if (params[len(params) - 1] == '/'):
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]

    return param

site_url = 'http://zoomby.ru'
params = get_params()
print params
mode = None
url = None

try: mode = urllib.unquote_plus(params['mode'])
except: pass

try: url = urllib.unquote_plus(params['url'])
except: pass

if mode == None: Main(url)
elif mode == 'SEARCH': Search()
elif mode == 'CONTENT': Content(url)
elif mode == 'PLAY_URL': PlayUrl(url)
elif mode == 'SERIALS': Serials(url)
elif mode == 'FAVS': GetFilmsList(url)

xbmcplugin.endOfDirectory(h)
