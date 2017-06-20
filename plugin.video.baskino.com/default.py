#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib, urllib2, os, re, sys, json, cookielib

import html5lib

import xbmc, xbmcaddon, xbmcgui, xbmcplugin

from bs4 import BeautifulSoup as bs

__settings__ = xbmcaddon.Addon(id='plugin.video.baskino.com')
plugin_path = __settings__.getAddonInfo('path').replace(';', '')
plugin_icon = xbmc.translatePath(os.path.join(plugin_path, 'icon.png'))
context_path = xbmc.translatePath(os.path.join(plugin_path, 'default.py'))

def Alert(title, message):
    xbmcgui.Dialog().ok(title, message)

def Notificator(title, message, timeout = 500):
	xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(title, message, timeout, plugin_icon))

def GetHTML(url):
    cookieJar = cookielib.CookieJar()
    if mode == 'FAVS': cookieJar = Auth(cookieJar)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))
    opener.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 6.2; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0")]
    connection = opener.open(url)
    html = connection.read()
    connection.close()
    return html


def get_html_with_referer(page_url, referer):
    cookie_jar = cookielib.CookieJar()
    if mode == 'FAVS':
        cookie_jar = Auth(cookie_jar)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_jar))
    opener.addheaders = [("Referer", referer)]
    connection = opener.open(page_url)
    html = connection.read()
    connection.close()
    return html


def post_request(page_url, req_data=None, headers={}):
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    conn = urllib2.Request(page_url, urllib.urlencode(req_data), headers)
    connection = opener.open(conn)
    html = connection.read()
    return html


def Main():
    site_url = 'http://baskino.co'
    html = GetHTML(site_url)
    soup = bs(html, 'html5lib', from_encoding="utf-8")
    content = soup.find('li', attrs={'class': 'first'})
    content = content.find_all('li')
    addDir('Поиск', site_url + '/index.php', mode="SEARCH")
    addDir('Закладки', site_url + '/favorites/', mode="FAVS")
    addDir('Новинки', site_url + '/new/', mode="FILMS")
    addDir('Сериалы', site_url + '/serial/', mode="FILMS")
    for num in content:
        if (num.find('a')['href'] != ('/mobile/' and '/announcement/')):
            title = num.find('a').contents[0]
            url = site_url + num.find('a')['href']
            addDir(title, url, mode="FILMS")

def addDir(title, url, iconImg="DefaultVideo.png", mode="", inbookmarks=False):
    sys_url = sys.argv[0] + '?url=' + urllib.quote_plus(url) + '&mode=' + urllib.quote_plus(str(mode))
    item = xbmcgui.ListItem(title, iconImage=iconImg, thumbnailImage=iconImg)
    item.setInfo(type='Video', infoLabels={'Title': title})
    id = url.split('-')[0].split('/')[-1]
    contextMenuItems = []
    if inbookmarks:
        contextMenuItems.append(('Удалить из закладок', 'XBMC.RunScript(%s,%i,%s)' %
                            (context_path, 1, 'mode=remove_bookmark&url='+id)))
    else:
        contextMenuItems.append(('Добавить в закладки', 'XBMC.RunScript(%s,%i,%s)' %
                            (context_path, 1, 'mode=add_bookmark&url='+id)))
    item.addContextMenuItems(contextMenuItems, replaceItems=True)
    xbmcplugin.addDirectoryItem(handle=h, url=sys_url, listitem=item, isFolder=True)

def addLink(title, infoLabels, url, iconImg="DefaultVideo.png"):
    item = xbmcgui.ListItem(title, iconImage=iconImg, thumbnailImage=iconImg)
    item.setInfo(type='Video', infoLabels=infoLabels)
    xbmcplugin.addDirectoryItem(handle=h, url=url, listitem=item)

def Search():
    kbd = xbmc.Keyboard()
    kbd.setDefault('')
    kbd.setHeading("Поиск")
    kbd.doModal()
    if kbd.isConfirmed():
        SearchStr = kbd.getText()
        url = site_url + '/index.php?do=search&subaction=search&actors_only=0&search_start=1&full_search=0&result_from=1&result_from=1&story=' + SearchStr
        GetFilmsList(url)
    else:
        return False

def GetFilmsList(url_main):
    html = GetHTML(url_main)
    soup = bs(html, 'html5lib', from_encoding="utf-8")
    content = soup.find_all('div', attrs={'class': 'postcover'})
    for num in content:
        title = num.find('img')['title']
        img = num.find('img')['src']
        url = num.find('a')['href']
        if mode == 'FAVS':
        	addDir(title, url, img, mode="FILM_LINK", inbookmarks=True)
        else:
        	addDir(title, url, img, mode="FILM_LINK")
    try:
        nav = soup.find('div', attrs={'class': 'navigation'})
        nav = nav.find_all('a')
        for num2 in nav:
            title = num2.contents[0].encode('utf-8')
            if (title == 'Вперед'):
                if url_main.find('do=search') > -1:
                    num_page = (url_main[83])
                    num_page_next = str(int(num_page) + 1)
                    url = url_main.replace('search_start='+num_page, 'search_start='+num_page_next)
                else:
                    url = num2['href']
                addDir('---Следующая страница---', url, mode="FILMS")
    except: return False


def parse_player_page(url, player_page):
    manifest_path = re.compile(r'(/manifest.*all)').findall(player_page)[0]
    compiled_url = "http://" + url.split('/')[2] + manifest_path
    video_token = re.compile(r"video_token:\s*\S?\'([0-9a-f]*)\S?\'").findall(player_page)[0]
    mw_key = re.compile(r"mw_key\s?=\s?\'(\w+)\';").findall(player_page)[0]
    content_type = re.compile(r"content_type:\W*\'(movie)\W?\'").findall(player_page)[0]
    mw_pid = re.compile(r"mw_pid:\W?(\d*)").findall(player_page)[0]
    p_domain_id = re.compile(r"p_domain_id:\W?(\d*)").findall(player_page)[0]
    csrf_token = re.compile(r"csrf-token\W\s?content\s?=\s?\"(\S*)\"").findall(player_page)[0]
    access_level = re.compile(r"X-Access-Level\S?\':\s?\S?\'([a-f0-9]*)\S?\'").findall(player_page)[0]
    ad_attr = '0'
    cookies = get_cookies(player_page)
    req_data = {"mw_key": mw_key, "content_type": content_type, "mw_pid": mw_pid, "p_domain_id": p_domain_id,
                "ad_attr": ad_attr, cookies[0]: cookies[1]}
    headers = {
        "X-Access-Level": access_level,
        "X-CSRF-Token": csrf_token,
        "X-Requested-With": "XMLHttpRequest"
    }
    json_data = post_request(compiled_url, req_data, headers)
    data = json.loads(json_data)
    html5data = urllib.urlencode({"manifest_m3u8": data["mans"]["manifest_m3u8"],
                                  "manifest_mp4": data["mans"]["manifest_mp4"], "token": video_token,
                                  "pid": mw_pid, "debug": 0})
    html5_player_url = "http://" + url.split('/')[2] + "/video/html5" + "?" + html5data
    html5_page = GetHTML(html5_player_url)

    # # this should work for mp4 streams
    # mp4_manifest_link = re.compile("getJSON\S?\S?\'(http\S*json\S*[0-9a-f])\S?\'").findall(html5_page)[0]
    # mp4file = GetHTML(mp4_manifest_link)
    # links = json.loads(mp4file)

    # this is for m3u8 streams
    manifest_link = re.compile("hls\s?:\s?\S?\'(http\S*[0-9a-f])\S?\'").findall(html5_page)[0]
    manifest_file = get_html_with_referer(manifest_link, html5_player_url)
    links = re.compile("RESOLUTION=(\d*x\d*)\S*\s*(http\S*m3u8)").findall(manifest_file)
    return dict(links)


def get_cookies(player_page):
    cookie = re.compile("\s\swindow\[.*\]\[(.*)\]\W?=\W?([a-z0-9\\\' +]*);").findall(player_page)[0]
    cookie_header = cookie[0]
    cookie_header = re.sub('\'|\s|\+', '', cookie_header)
    cookie_data = cookie[1]
    cookie_data = re.sub('\'|\s|\+', '', cookie_data)
    cookies = [cookie_header, cookie_data]
    return cookies


def GetFilmLink(url):
    film_url = url
    html = GetHTML(url)
    #print html
    soup = bs(html, 'html5lib', from_encoding="utf_8")
    content = soup.find('div', attrs={'class': 'info'})
    content = content.find_all('tr')
    for num in content:
        num = num.find_all('td')
        if num[0].string == u'Название:':
            title = num[1].string
        if num[0].string == u'Год:':
            year = num[1].string
        if num[0].string == u'Страна:':
            country = num[1].string
        if num[0].string == u'Режиссер:':
            director = num[1].string
        if num[0].string == u'Жанр:':
            genre = num[1].string
        if num[0].string == u'Время:':
            duration = num[1].string

    content = soup.find('div', attrs={'id': re.compile('^news')})
    info = content.contents[0]
    if not isinstance(info, unicode):
    	info = ''
    infoLabel = {'title': title, 'year': year, 'genre': genre, 'plot': info, 'director': director, 'country': country}
    content = soup.find('div', attrs={'class': 'mobile_cover'})
    img = content.find('img', attrs={'itemprop': 'image'})['src']

    if url.find('/serial/') > -1:
        try:
            script = soup.find('div', attrs={'class': 'basplayer'})
            script = script.find('div', attrs={'class': 'inner'})
            script = script.find('script', attrs={'type': 'text/javascript', 'src': '', 'language': ''}).string
            data = script.split("var tvs_codes = ", 1)[-1].rsplit(';', 1)[0]
            data = json.loads(data)

            seasons = soup.find('div', attrs={'class': 'tvs_slides_wrap tvs_slides_seasons'})
            seasons = seasons.find_all('span')

            episode = soup.find_all('div', attrs={'id': re.compile('^episodes-')})

            k = 0
            for s in seasons:
                epis = episode[k].find_all('span')
                for ep in epis:
                    n1 = ep['onclick'].find('(') + 1
                    n2 = ep['onclick'].find(',', n1)
                    n = ep['onclick'][n1:n2]
                    if data[n].find('vk.com') > -1:
                        n1 = data[n].find('src="') + 5
                        n2 = data[n].find('"', n1)
                        url = data[n][n1:n2]
                        url = GetVKUrl(url)
                    else:
                        url = GetFLASHUrl(data[n])
                    addLink(s.string + ' | ' + ep.string, infoLabel, url, iconImg=img)
                k = k + 1
        except: pass
    else:
        content = soup.find_all('div', attrs={'class': 'player_code'})
        for num in content:
            if num.find('iframe') != None:
                url = num.find('iframe')['src']
                print url
                if re.search('(vk.com|vkontakte.ru|vk.me)', url):
                    url = GetVKUrl(url)
                    addLink(title + ' [VK]', infoLabel, url, iconImg=img)
                #elif 'gidtv.cc' in url:
                #    url = GetGIDTVUrl(url)
                #    addLink(title + ' [GIDTV]', infoLabel, url, iconImg=img)
                elif ('staticdn.nl' or 'moonwalk.cc') in url:
                    '''url = GetMoonwalkUrl(url)'''
                    print url
                    url = getRealURL(url)
                    print url
                    url = url.replace('iframe','index.m3u8')
                    print url
                    addLink(title + ' [HD]', infoLabel, url, iconImg=img)
                elif ('vkinos.com') in url:
                    url = getVkinosUrl(url)
                    addLink(title + ' [mp4]', infoLabel, url, iconImg=img)
                elif ('staticnlcdn.com') in url:
                    global film_url
                    player_page = get_html_with_referer(url, film_url)
                    mp4_urls = parse_player_page(url, player_page)
                    for key in mp4_urls.keys():
                        addLink(title + " [" + key + "]", infoLabel, mp4_urls[key], iconImg=img)
            if num.find('div', attrs={'id': re.compile('^videoplayer')}) <> None:
                url = num.find('script').string
                url = GetFLASHUrl(url)
                if num['id'] == 'basplayer_original':
                    addLink(title + ' [ORIGINAL]', infoLabel, url, iconImg=img)
                else:
                    addLink(title + ' [MP4]', infoLabel, url, iconImg=img)

    xbmcplugin.setContent(h, 'movies')

def GetVKUrl(url):
    http = GetHTML(url)
    soup = bs(http, 'html5lib', from_encoding="utf-8")
    sdata1= soup.find('div', style="position:absolute; top:50%; text-align:center; right:0pt; left:0pt; font-family:Tahoma; font-size:12px; color:#777;")
    if sdata1:
        print sdata1.string.strip().encode('utf-8')
        xbmc.showMessage("Cinema-hd.ru.a",sdata1.string.strip().encode('utf-8'))
        return False
    for rec in soup.find_all('param', {'name':'flashvars'}):
        fv={}
        for s in rec['value'].split('&'):
            sdd=s.split('=',1)
            fv[sdd[0]]=sdd[1]
            if s.split('=',1)[0] == 'uid':
                uid = s.split('=',1)[1]
            if s.split('=',1)[0] == 'vtag':
                vtag = s.split('=',1)[1]
            if s.split('=',1)[0] == 'host':
                host = s.split('=',1)[1]
            if s.split('=',1)[0] == 'vid':
                vid = s.split('=',1)[1]
            if s.split('=',1)[0] == 'oid':
                oid = s.split('=',1)[1]
            if s.split('=',1)[0] == 'hd':
                hd = s.split('=',1)[1]
        url = host+'u'+uid+'/videos/'+vtag+'.240.mp4'
        if int(hd)==3:
            url = host+'u'+uid+'/videos/'+vtag+'.720.mp4'
        if int(hd)==2:
            url = host+'u'+uid+'/videos/'+vtag+'.480.mp4'
        if int(hd)==1:
            url = host+'u'+uid+'/videos/'+vtag+'.360.mp4'
    if not touch(url):
        try:
            if int(hd)==3:
                url = fv['cache720']
            if int(hd)==2:
                url = fv['cache480']
            if int(hd)==1:
                url = fv['cache360']
        except:
            print 'Vk parser failed'
            xbmc.showMessage("Baskino.com", 'Vk parser failed!')
            return False
    return url

def GetMoonwalkUrl(url):
    token=re.findall('http://moonwalk.cc/video/(.+?)/',url)[0]

    req = urllib2.Request('http://moonwalk.cc/sessions/create_session',data='video_token='+token+'&video_secret=HIV5')
    try:
        response = urllib2.urlopen(req)
        html=response.read()
        response.close()
    except Exception, e:
        print 'GET: Error getting page '+url
        return None

    page=json.loads(html)
    url = page["manifest_m3u8"]
    return url

def GetGIDTVUrl(url):
    http = GetHTML(url)
    n1 = http.find('setFlash(') + 10
    n2 = http.find('.mp4', n1) + 4
    url = http[n1:n2]
    return url

def GetFLASHUrl(url):
    n1 = url.find('file:') + 6
    n2 = url.find('.mp4', n1) + 4
    url = url[n1:n2]
    return url

def touch(url):
    req = urllib2.Request(url)
    try:
        res=urllib2.urlopen(req)
        res.close()
        return True
    except:
        return False
        
def add_bookmark(id):
    cookieJar = Auth(cookielib.CookieJar())
    url = site_url + '/engine/ajax/favorites.php?fav_id='+id+'&action=plus&skin=Baskino'
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))
    connection = opener.open(url)
    connection.close()
    Notificator('Добавление закладки', 'Закладка добавлена', 3000)

def remove_bookmark(id):
    cookieJar = Auth(cookielib.CookieJar())
    url = site_url + '/engine/ajax/favorites.php?fav_id='+id+'&action=minus&skin=Baskino'
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))
    connection = opener.open(url)
    connection.close()
    Notificator('Удаление закладки', 'Закладка удалена', 3000)
    xbmc.executebuiltin('Container.Refresh()')
        
def Auth(cookieJar):
    username = __settings__.getSetting('username')
    password = __settings__.getSetting('password')

    if ( username == "" or password == "" ):
        __settings__.openSettings()
        username = __settings__.getSetting('username')
        password = __settings__.getSetting('password')

    if ( username == "" or password == "" ):
        Alert('Вы не авторизованы', 'Укажите логин и пароль в настройках приложения')
        print 'Пользователь не аторизован. Выход.'
        sys.exit()

    reqData = {'login_name' : username, 'login_password' : password, 'login' : 'submit'}
    url = site_url + '/index.php'
    headers = {
            "User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3",
            "Content-Type" : "application/x-www-form-urlencoded",
            "Host": "baskino.com",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.8,bg;q=0.6,it;q=0.4,ru;q=0.2,uk;q=0.2",
            "Accept-Encoding" : "windows-1251,utf-8;q=0.7,*;q=0.7",
            "Referer": site_url + "/index.php"
    }
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))
    conn = urllib2.Request(url, urllib.urlencode(reqData), headers)
    connection = opener.open(conn)
    html = connection.read()
    connection.close()
    if 'Ошибка авторизации' in html:
    	Alert('Проверьте логин и пароль', 'Неверный логин либо пароль')
    	__settings__.openSettings()
    	sys.exit()
    return cookieJar

def getVkinosUrl(url):
    req = urllib2.Request(url)
    res = urllib2.urlopen(req)
    html = res.read()
    lnk = re.compile('(http:\/\/.*.mp4)').findall(html)[0]
    return lnk

def getRealURL(url):    
    req = urllib2.Request(url)
    res = urllib2.urlopen(req)
    finalurl = res.geturl()
    return finalurl

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

h = int(sys.argv[1])
params = get_params()

mode = None
url = None

try: mode = urllib.unquote_plus(params['mode'])
except: pass

try: url = urllib.unquote_plus(params['url'])
except: pass

if mode == None: Main()
elif mode == 'SEARCH': Search()
elif mode == 'FILMS': GetFilmsList(url)
elif mode == 'FILM_LINK': GetFilmLink(url)
elif mode == 'FAVS': GetFilmsList(url)
elif mode == 'add_bookmark': add_bookmark(url)
elif mode == 'remove_bookmark': remove_bookmark(url)

xbmcplugin.endOfDirectory(h)
