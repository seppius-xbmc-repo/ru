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
    soup = bs(html)
    content = soup.find_all('article', attrs={'class': 'c-anime'})
    
    if main_url == site_url :
        addDir('Поиск', site_url, mode="SEARCH")
        submenu = soup.find('div', attrs={'class': 'submenu'})
        submenu = submenu.find_all('a')
        
        for el in submenu:
            addDir(el['title'], el['href'], iconImg=plugin_icon)

    for num in content:
        title = num.find('a').string.encode('utf-8')
        if main_url == site_url or '/page/' in main_url :
            url = num.find('a')['href']
        else :
            url = site_url + num.find('a')['href']
        image = num.find('meta', attrs={'itemprop': 'image'})['content']
        addDir(title, url, iconImg=image, mode="FILMS")
    next = soup.find('a', {'class': 'next'})
    if next :
        addDir('---Следующая страница---', next['href'], iconImg=plugin_icon)

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
        url = 'http://play.shikimori.org/animes/search/' + SearchStr.decode('utf-8')
        html = GetHTML(url.encode('utf-8'))
        soup = bs(html)
        content = soup.find_all('article', attrs={'class': 'c-anime'})
        for num in content:
            title = num.find('a').contents[0]
            url = site_url + num.find('a')['href']
            image = num.find('meta', attrs={'itemprop': 'image'})['content']
            addDir(title, url, iconImg=image, mode="FILMS")
    else:
        return False

def GetFilmsList(url_main) :
    html = GetHTML(url_main)
    soup = bs(html)
    content = soup.find('div', attrs={'class': 'c-episodes'})
    content = content.find_all('div', attrs={'class': 'episode'})
    for num in content:
        lnk = num.find('a')
        title = 'Эпизод ' + lnk.find('span', attrs={'class': 'episode-num'}).text
        # img = num.find('img')['src']
        url = lnk['href']
        addDir(title, url, iconImg="DefaultVideo.png", mode="VOICES")

def GetVKUrl(url):
    http = GetHTML(url)
    soup = bs(http)
    soup = bs(GetHTML(soup.find('div', {'class':'b-video_player'}).find('iframe')['src']))
    sdata1 = soup.find('div', style="position:absolute; top:50%; text-align:center; right:0pt; left:0pt; font-family:Tahoma; font-size:12px; color:#777;")
    video = ''
    if sdata1:
        return False
    for rec in soup.find_all('param', {'name':'flashvars'}):
        for s in rec['value'].split('&'):
            if s.split('=', 1)[0] == 'url240':
                url240 = s.split('=', 1)[1]
            if s.split('=', 1)[0] == 'url360':
                url360 = s.split('=', 1)[1]
            if s.split('=', 1)[0] == 'url480':
                url480 = s.split('=', 1)[1]
            if s.split('=', 1)[0] == 'url720':
                url720 = s.split('=', 1)[1]
            if s.split('=', 1)[0] == 'hd':
                hd = s.split('=', 1)[1]
        video = url240
        qual = __settings__.getSetting('qual')
        if int(hd) >= 3 and int(qual) == 3:
            video = url720
        elif int(hd) >= 2 and (int(qual) == 2 or int(qual) == 3):
            video = url480
        elif int(hd) >= 1 and (int(qual) == 1 or int(qual) == 2):
            video = url360
    return video

def GetSibnetUrl(url):
    http = GetHTML(url)
    soup = bs(http)
    # print soup
    player = soup.find('div', {'class':'b-video_player'})
    param = player.find('param', {'name': 'movie'})
    if param :
        video_id = param['value']
    else :
        video_id = player.find('iframe')['src']
    print video_id
    http = GetHTML('http://video.sibnet.ru/shell_config_xml.php?videoid=' + video_id.split('=', 1)[1])
    soup = bs(http)
    video = soup.find('file').text
    return video

def GetMyviUrl(url):
    headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.2; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
            'referer': url,
    }

    with requests.session() as s:
        # logging.basicConfig(level=logging.DEBUG) 
       # import time
        #_startTime = time.time()
        r = s.get(url)
        s.headers.update(headers)
        soup = bs(r.text)
        #print "Elapsed time: {:.3f} sec".format(time.time() - _startTime)
        url = soup.find('div', {'class':'player-area'}).find('iframe')['src']
        r = s.get(url, allow_redirects=True)
        UniversalUserID = r.cookies['UniversalUserID']
        js = bs(r.text).find('body').find('script', {'type': 'text/javascript'}).encode('utf-8')
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

def GetRutubeUrl(url):
    http = GetHTML(url)
    soup = bs(http)
    try:
        url = soup.find('div', {'class':'b-video_player'}).find('iframe')['src']
        url = 'http://rutube.ru/api/play/options/' + url.split('http://rutube.ru/play/embed/', 1)[1] + '/?format=xml'
        http = GetHTML(url)
        soup = bs(http)
        url = soup.find('video_balancer').find('m3u8').text
    except:
        return None
    return url
    
def PlayUrl(url):
    html = GetHTML(url);
    soup = bs(html)
    player = soup.find('div', {'class':'c-videos'}).find('a', {'class': 'active'}).find('span', {'class': 'video-hosting'}).text
    if 'vk.com' in player:
        url = GetVKUrl(url)
    elif 'myvi.tv' in player:
        url = GetMyviUrl(url)
    elif 'rutube.ru' in player:
        url = GetRutubeUrl(url)
    elif 'sibnet.ru' in player:
        url = GetSibnetUrl(url)
    else :
        Notificator('ERROR', 'Not supported player', 3600)
        return None  
    i = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(h, True, i)

def GetVoicesList(url):
    http = GetHTML(url)
    soup = bs(http)
    content = soup.find('div', attrs={'class': 'c-videos'})
    content = content.find_all('div', attrs={'class': 'episode'})
    for voice in content:
        lnk = voice.find('a')
        player = lnk.find('span', attrs={'class': 'video-hosting'}).text
        title = '[' + lnk.find('span', attrs={'class': 'video-kind'}).text + ']' + '[' + player + ']'
        author = lnk.find('span', attrs={'class': 'video-author'})
        if author:
            title += author.text
        # img = num.find('img')['src']
        url = lnk['href']
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
site_url = 'http://play.shikimori.org/'
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
