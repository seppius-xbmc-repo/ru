# coding: utf8
#!/usr/bin/python

from __future__ import unicode_literals

import urllib, urllib2, os, re, sys, json, cookielib

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

__settings__ = xbmcaddon.Addon(id='plugin.video.shikimori.org')
h = int(sys.argv[1])

plugin_path = __settings__.getAddonInfo('path').replace(';', '')
plugin_icon = xbmc.translatePath(os.path.join(plugin_path, 'icon.png'))
context_path = xbmc.translatePath(os.path.join(plugin_path, 'default.py'))

def Alert(title, message):
    xbmcgui.Dialog().ok(title, message)

def Notificator(title, message, timeout=1000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (title, message, timeout, plugin_icon))

def GetHTML(url):
    cookieJar = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))
    connection = opener.open(url)
    html = connection.read()
    connection.close()
    return html


def Main(main_url):
    if main_url == None :
        main_url = site_url
    
    html = GetHTML(main_url)
    soup = bs(html, "html.parser")
    content = soup.find_all('article', attrs={'class': 'c-anime'})
    
    if main_url == site_url :
        addDir('Поиск', site_url, mode="SEARCH")
        submenu = soup.find('div', attrs={'class': 'submenu'})
        submenu = submenu.find_all('a')
        
        for el in submenu:
            addDir(el['title'], url_protocol + el['href'], iconImg=plugin_icon)

    for num in content:
        block = num.find('', attrs={'class': 'cover'})
        title_block = num.find('span', attrs={'class': 'name-ru'})
        if title_block == None:
            title_block = num.find('div', attrs={'class': 'name'})
            if title_block == None:
                title = num.find(['a', 'span'], attrs={'class': 'title'}).getText().encode('utf-8')
            else:
                title = title_block.getText().encode('utf-8')
        else:
            title = title_block['data-text'].encode('utf-8')
            
        if block.has_attr('data-href'):
            url = block['data-href']
        else:
            url = block['href']
        url = url_protocol + url
        image = num.find('meta', attrs={'itemprop': 'image'})['content']
        addDir(title, url, iconImg=image, mode="FILMS")
    next = soup.find('a', {'class': 'next'})
    if next :
        addDir('---Следующая страница---', url_protocol + next['href'], iconImg=plugin_icon)

def addDir(title, url, iconImg="DefaultVideo.png", mode="", inbookmarks=False):
    sys_url = sys.argv[0] + '?url=' + urllib.quote_plus(url) + '&mode=' + urllib.quote_plus(str(mode))
    item = xbmcgui.ListItem(title, iconImage=iconImg, thumbnailImage=iconImg)
    item.setInfo(type='Video', infoLabels={'Title': title})
    xbmcplugin.addDirectoryItem(handle=h, url=sys_url, listitem=item, isFolder=True)

def addLink(title, url, iconImg="DefaultVideo.png"):
    sys_url = sys.argv[0] + '?mode=' + urllib.quote_plus('PLAY_URL') + '&url=' + urllib.quote_plus(url)
    item = xbmcgui.ListItem(title, iconImage=iconImg, thumbnailImage=iconImg)
    item.setProperty('IsPlayable', 'true')
    item.setInfo(type='Video', infoLabels={'Title': title})
    xbmcplugin.addDirectoryItem(h, sys_url, item)

def Search():
    kbd = xbmc.Keyboard()
    kbd.setDefault('')
    kbd.setHeading("Поиск")
    kbd.doModal()
    if kbd.isConfirmed():
        SearchStr = kbd.getText()
        url = url_protocol + '//play.shikimori.org/animes/search/' + SearchStr.decode('utf-8')
        html = GetHTML(url.encode('utf-8'))
        soup = bs(html, "html.parser")
        content = soup.find_all('article', attrs={'class': 'c-anime'})
        for num in content:
            title = num.find('span', attrs={'class': 'title'})
            if title: title = title.text
            title_en = num.find('span', attrs={'class': 'name-en'})
            if title_en: title = title_en.text
            title_ru = num.find('span', attrs={'class': 'name-ru'})
            if title_ru: title += " / " + title_ru['data-text']
            url = url_protocol + num.find('a')['href']
            image = num.find('meta', attrs={'itemprop': 'image'})['content']
            addDir(title, url, iconImg=image, mode="FILMS")
    else:
        return False

def GetFilmsList(url_main) :
    html = GetHTML(url_main)
    soup = bs(html, "html.parser")
    content = soup.find('div', attrs={'class': 'c-anime_video_episodes'})
    content = content.find_all('div', attrs={'class': 'b-video_variant'})
    for num in content:
        lnk = num.find('a')
        title = 'Эпизод ' + lnk.find('span', attrs={'class': 'episode-num'}).text
        # img = num.find('img')['src']
        url = url_protocol + lnk['href']
        addDir(title, url, iconImg="DefaultVideo.png", mode="VOICES")

def GetVKUrl(html):
    soup = bs(html, "html.parser")
    vk_url = 'http:' + soup.find('div', {'class':'b-video_player'}).find('iframe')['src']
    soup = bs(GetHTML(vk_url), "html.parser")
    video = ''
    if soup.find('div', {'id': 'video_ext_msg'}):
        Notificator('ERROR', 'Video is not available', 3600)
        return None 
    
    source = soup.find('video').find('source')['src']
    
    return source

def GetSibnetUrl(html):
    soup = bs(html, "html.parser")
    # print soup
    player = soup.find('div', {'class':'b-video_player'})
    param = player.find('param', {'name': 'movie'})
    if param :
        video_id = param['value']
    else :
        video_id = player.find('iframe')['src']
    #print video_id
    http = GetHTML('http://video.sibnet.ru/shell_config_xml.php?videoid=' + video_id.split('=', 1)[1])
    soup = bs(http, "html.parser")
    video = soup.find('file').text
    return video

def GetMyviUrl(html, url):
    headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.2; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
            'referer': url,
    }

    with requests.session() as s:
        # logging.basicConfig(level=logging.DEBUG) 
        # import time
        #_startTime = time.time()
        #r = s.get(url)
        s.headers.update(headers)
        soup = bs(html, "html.parser")
        #print "Elapsed time: {:.3f} sec".format(time.time() - _startTime)
        url = soup.find('div', {'class':'player-area'}).find('iframe')['src']
        url = 'http:' + url
        r = s.get(url, allow_redirects=True)
        UniversalUserID = r.cookies['UniversalUserID']
        js = bs(r.text, "html.parser").find('body').find('script', {'type': 'text/javascript'}).encode('utf-8')
        js = '{%s}' % (js.decode('utf-8').split('{', 1)[1].rsplit('}', 1)[0])
        js = re.sub(ur'([\s*{\s*,])([a-z]\w*):', ur'\1"\2":', js)
        js = js.replace("'", '"')
        json_data = json.loads(js)
        api = 'http://myvi.ru' + json_data['dataUrl']
        r = s.get(api)
        data = json.loads(r.text)
        url = data['sprutoData']['playlist'][0]['video'][0]['url']
        r = s.get(url, allow_redirects=False)
        return r.headers['Location'] + '|Cookie=' + urllib.quote_plus(urllib.urlencode({'UniversalUserID' : UniversalUserID }))
    return None

def GetRutubeUrl(html):
    soup = bs(html, "html.parser")
    try:
        url = soup.find('div', {'class':'b-video_player'}).find('iframe')['src']
        url = 'http://rutube.ru/api/play/options/' + url.split('http://rutube.ru/play/embed/', 1)[1] + '/?format=xml'
        http = GetHTML(url)
        soup = bs(http, "html.parser")
        url = soup.find('video_balancer').find('m3u8').text
    except:
        return None
    return url
    
def PlayUrl(url):
    html = GetHTML(url);
    soup = bs(html, "html.parser")
    player = soup.find('div', {'class':'c-videos'}).find('a', {'class': 'active'}).find('span', {'class': 'video-hosting'}).text
    if 'vk.com' in player:
        url = GetVKUrl(html)
    elif 'myvi.tv' in player or 'myvi.ru' in player:
        url = GetMyviUrl(html, url)
    elif 'rutube.ru' in player:
        url = GetRutubeUrl(html)
    elif 'sibnet.ru' in player:
        url = GetSibnetUrl(html)
    else :
        Notificator('ERROR', 'Not supported player', 3600)
        return None
    i = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(h, True, i)

def GetVoicesList(url):
    http = GetHTML(url)
    soup = bs(http, "html.parser")
    content = soup.find('div', attrs={'class': 'c-videos'})
    content = content.find_all('div', attrs={'class': 'b-video_variant'})
    for voice in content:
        lnk = voice.find('a')
        player = lnk.find('span', attrs={'class': 'video-hosting'}).text

        if player not in ['vk.com','myvi.tv','myvi.ru','rutube.ru','sibnet.ru']:
            continue

        title = '[' + lnk.find('span', attrs={'class': 'video-kind'}).text + ']' + '[' + player + ']'
        author = lnk.find('span', attrs={'class': 'video-author'})
        if author:
            title += author.text
        # img = num.find('img')['src']
        url = url_protocol + lnk['href']
        # print player.encode('utf-8')

        addLink(title, url, iconImg="DefaultVideo.png")

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
url_protocol = 'https:'
site_url = url_protocol+'//play.shikimori.org/'
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
elif mode == 'FILMS': GetFilmsList(url)
elif mode == 'PLAY_URL': PlayUrl(url)
elif mode == 'VOICES': GetVoicesList(url)
elif mode == 'FAVS': GetFilmsList(url)

xbmcplugin.endOfDirectory(h)
