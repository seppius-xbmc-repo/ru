#!/usr/bin/python
# -*- coding: utf-8 -*-
import base64
import binascii
from future.utils import PY3
import json
import os
import re
import sys

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
from bs4 import BeautifulSoup

from lib import pyaes

if PY3:
    import urllib.parse as urllib_parse
    import urllib.request as urllib_request
    import http.cookiejar as cookielib
else:
    import urllib2 as urllib_request
    import urllib as urllib_parse
    import cookielib as cookielib

USER_AGENT = "Mozilla/5.0 (Windows NT 6.2; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0"

debug = False

# todo fix temp solution for kodistubs in PY3
if PY3:
    __settings__ = xbmcaddon.Addon()
else:
    __settings__ = xbmcaddon.Addon(id='plugin.video.baskino.com')

plugin_path = __settings__.getAddonInfo('path').replace(';', '')
plugin_icon = xbmc.translatePath(os.path.join(plugin_path, 'icon.png'))
context_path = xbmc.translatePath(os.path.join(plugin_path, 'default.py'))

site_url = 'http://baskino.me'

antizapret_settings = __settings__.getSetting("antizapret")
antizapret_enabled = antizapret_settings == "true"
if antizapret_enabled:
    try:
        import antizapret as az
        print ("AntiZapret imported")
    except:
        antizapret_enabled = False
        xbmc.executebuiltin("InstallAddon(script.module.antizapret)")


def alert(title, message):
    if debug:
        print("===== Alert =====")
        print(title)
        print(message)
    xbmcgui.Dialog().ok(title, message)


def notificator(title, message, timeout=500):
    if debug:
        print("===== Notificator =====")
        print(title)
        print(message)
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (title, message, timeout, plugin_icon))


def play_url(web_url):
    if debug:
        print_str = "Playing url: " + web_url
        print (print_str)
    item = xbmcgui.ListItem(path=web_url)
    xbmcplugin.setResolvedUrl(handle=h, succeeded=True, listitem=item)


def get_html(web_url):
    cookie_jar = cookielib.CookieJar()
    if mode == 'FAVS':
        cookie_jar = auth(cookie_jar)
    if antizapret_enabled:
        opener = urllib_request.build_opener(urllib_request.HTTPCookieProcessor(cookie_jar),
                                             az.AntizapretProxyHandler())
    else:
        opener = urllib_request.build_opener(urllib_request.HTTPCookieProcessor(cookie_jar))
    opener.addheaders = [("User-Agent", USER_AGENT)]
    connection = opener.open(web_url)
    html = connection.read()
    connection.close()
    return html.decode('utf-8')


def get_html_with_referer(page_url, referer):
    cookie_jar = cookielib.CookieJar()
    if mode == 'FAVS':
        cookie_jar = auth(cookie_jar)
    if antizapret_enabled:
        opener = urllib_request.build_opener(urllib_request.HTTPCookieProcessor(cookie_jar),
                                             az.AntizapretProxyHandler())
    else:
        opener = urllib_request.build_opener(urllib_request.HTTPCookieProcessor(cookie_jar))
    if referer is not None:
        opener.addheaders = [("Referer", referer)]
    connection = opener.open(page_url)
    html = connection.read()
    connection.close()
    return html.decode('utf-8')


def post_request(page_url, req_data=None, headers=None):
    if headers is None:
        headers = {}
    if antizapret_enabled:
        opener = urllib_request.build_opener(urllib_request.HTTPCookieProcessor(),
                                             az.AntizapretProxyHandler())
    else:
        opener = urllib_request.build_opener(urllib_request.HTTPCookieProcessor())
    opener.addheaders = [("User-Agent", USER_AGENT)]
    conn = urllib_request.Request(page_url, urllib_parse.urlencode(req_data).encode('utf-8'), headers)
    connection = opener.open(conn)
    html = connection.read()
    return html


def main():
    html = get_html(site_url)
    soup = BeautifulSoup(html, 'html5lib')
    content = soup.find('li', attrs={'class': 'first'})
    content = content.find_all('li')
    add_dir('Поиск', site_url + '/index.php', dir_mode="SEARCH")
    add_dir('Закладки', site_url + '/favorites/', dir_mode="FAVS")
    add_dir('Новинки', site_url + '/new/', dir_mode="FILMS")
    add_dir('Сериалы', site_url + '/serial/', dir_mode="FILMS")
    for num in content:
        if num.find('a')['href'] != ('/mobile/' and '/announcement/'):
            title = num.find('a').contents[0]
            dir_url = site_url + num.find('a')['href']
            add_dir(title, dir_url, dir_mode="FILMS")


def add_dir(title, dir_url, icon_img="DefaultVideo.png", dir_mode="", referer="", inbookmarks=False):
    sys_url = sys.argv[0] + '?url=' + urllib_parse.quote_plus(dir_url) + '&mode=' + urllib_parse.quote_plus(
        str(dir_mode)) + \
              '&referer=' + urllib_parse.quote_plus(str(referer))
    item = xbmcgui.ListItem(title, iconImage=icon_img, thumbnailImage=icon_img)
    item.setInfo(type='Video', infoLabels={'Title': title})
    dir_id = dir_url.split('-')[0].split('/')[-1]
    context_menu_items = []
    if inbookmarks:
        context_menu_items.append(('Удалить из закладок', 'XBMC.RunScript(%s,%i,%s)' %
                                   (context_path, 1, 'mode=remove_bookmark&url=' + dir_id)))
    else:
        context_menu_items.append(('Добавить в закладки', 'XBMC.RunScript(%s,%i,%s)' %
                                   (context_path, 1, 'mode=add_bookmark&url=' + dir_id)))
    item.addContextMenuItems(context_menu_items)
    xbmcplugin.addDirectoryItem(handle=h, url=sys_url, listitem=item, isFolder=True)
    if debug:
        print("===== Add Dir =====")
        if not isinstance(title, str):
            print(title.encode('utf-8'))
            print(sys_url.encode('utf-8'))
        else:
            print(title)
            print(sys_url.encode('utf-8'))


def add_link(title, info_labels, link_url, icon_img="DefaultVideo.png"):
    item = xbmcgui.ListItem(title, iconImage=icon_img, thumbnailImage=icon_img)
    item.setInfo(type='Video', infoLabels=info_labels)
    item.setProperty('IsPlayable', 'true')
    xbmcplugin.addDirectoryItem(handle=h, url=link_url, listitem=item)
    if debug:
        print("===== Add Link =====")
        if not isinstance(title, str):
            print(title.encode('utf-8'))
            print(link_url.encode('utf-8'))
        else:
            print(title)
            print(link_url.encode('utf-8'))


def search(search_str):
    if search_str is None:
        kbd = xbmc.Keyboard()
        kbd.setDefault('')
        kbd.setHeading("Поиск")
        kbd.doModal()
        if kbd.isConfirmed():
            generate_search_list(kbd.getText())
        else:
            return False
    else:
        generate_search_list(search_str)


def generate_search_list(search_str):
    search_url = site_url + '/index.php?do=search&subaction=search&actors_only=0&search_start=1&full_search=0' \
                            '&result_from=1&result_from=1&story=' + urllib_parse.quote(search_str)
    get_films_list(search_url)


def get_films_list(url_main):
    html = get_html(url_main)
    soup = BeautifulSoup(html, 'html5lib')
    content = soup.find_all('div', attrs={'class': 'postcover'})
    for num in content:
        title = num.find('img')['title']
        img = num.find('img')['src']
        dir_url = num.find('a')['href']
        if mode == 'FAVS':
            add_dir(title, dir_url, img, dir_mode="FILM_LINK", inbookmarks=True)
        else:
            add_dir(title, dir_url, img, dir_mode="FILM_LINK")
    # noinspection PyBroadException
    try:
        nav = soup.find('div', attrs={'class': 'navigation'})
        nav = nav.find_all('a')
        for num2 in nav:
            title = num2.contents[0].encode('utf-8')
            if title == 'Вперед':
                if url_main.find('do=search') > -1:
                    num_page = (url_main[83])
                    num_page_next = str(int(num_page) + 1)
                    dir_url = url_main.replace('search_start=' + num_page, 'search_start=' + num_page_next)
                else:
                    dir_url = num2['href']
                add_dir('---Следующая страница---', dir_url, dir_mode="FILMS")
    except:
        return False


class EncryptedData:
    def __init__(self):
        pass

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, separators=(',', ':'))


def generate_vs_request(player_url, player_page):
    mw_pid = re.compile(r"partner_id:\s*(\w*),").findall(player_page)[0]
    p_domain_id = re.compile(r"domain_id:\s*(\w*),").findall(player_page)[0]

    _mw_adb = False

    video_token = re.compile(r"video_token:\s*\S?\'([0-9a-f]*)\S?\'").findall(player_page)[0]

    cookies = get_cookies(player_page)

    js_path = re.compile(r'script src=\"(.*)\"').findall(player_page)[0]
    js_page = get_html("http://" + player_url.split('/')[2] + js_path)

    regex_window_value = r'eval\("window"\)\["' + cookies[0] + r'"\]="(\w+)"'
    window_value = re.compile(regex_window_value).findall(js_page)[0]  # d value

    e_value = re.compile(r'getVideoManifests:function\(\){var e="(\w+)"').findall(js_page)[0]  # key

    r_value = re.compile(r'r="(\w+)",o').findall(js_page)[0]  # iv

    t = EncryptedData()
    t.a = mw_pid
    t.b = p_domain_id
    t.c = _mw_adb
    t.d = window_value
    t.e = video_token
    # t.f = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
    t.f = USER_AGENT

    json_string = t.to_json()

    encrypt_mode = pyaes.AESModeOfOperationCBC(binascii.a2b_hex('7316d0c4' + e_value), binascii.a2b_hex(r_value))
    encrypter = pyaes.Encrypter(encrypt_mode)
    encrypted = bytes()
    encrypted += encrypter.feed(json_string)
    encrypted += encrypter.feed()

    return base64.standard_b64encode(encrypted)


def parse_player_page(player_url, player_page, episode_number=0, referer=''):
    if episode_number == 0:
        try:
            episodes = re.compile(r'episodes:\s(.*),').findall(player_page)[0]
            if episodes == 'null':
                pass
            else:
                episodes_data = json.loads(episodes)
                progress = xbmcgui.DialogProgress()
                progress.create("Загрузка серий")
                for episode in episodes_data:
                    percentage = (episode * 100) / (len(episodes_data))
                    progress.update(percentage, str(episode) + "/" + str(len(episodes_data)))
                    get_with_referer(player_url, referer, episode)
                progress.close()
                return
        except:
            pass

    request_data = generate_vs_request(player_url, player_page)

    compiled_url = "http://" + player_url.split('/')[2] + "/vs"

    req_data = {"q": request_data}
    json_data = post_request(compiled_url, req_data)
    data = json.loads(json_data)
    manifest_link_hls = data["m3u8"]
    manifest_link_mp4 = data["mp4"]
    links_mp4 = None
    links_hls = None
    if manifest_link_hls is not None:
        manifest_file_hls = get_html(manifest_link_hls)
        links_hls = re.compile("RESOLUTION=(\d*x\d*)\S*\s*(http\S*m3u8)").findall(manifest_file_hls)
    if manifest_link_mp4 is not None:
        manifest_file_mp4 = get_html(manifest_link_mp4)
        try:
            links_mp4 = json.loads(manifest_file_mp4)
        except:
            links_mp4 = re.compile("RESOLUTION=(\d*x\d*)\S*\s*(http\S*m3u8)").findall(manifest_file_mp4)

    if isinstance(links_mp4, list):
        links_mp4.extend(links_hls)
    else:
        if links_mp4 is None:
            links_mp4 = links_hls
        else:
            links_mp4.update(links_hls)
    return dict(links_mp4)


def get_cookies(player_page):
    cookie = re.compile(r"window\[\'(\w*)\'\]\s=\s\'(\w*)\';").findall(player_page)[0]
    cookie_header = cookie[0]
    cookie_header = re.sub('\'|\s|\+', '', cookie_header)
    cookie_data = cookie[1]
    cookie_data = re.sub('\'|\s|\+', '', cookie_data)
    cookies = [cookie_header, cookie_data]
    return cookies


def get_film_link(dir_url):
    film_url = dir_url
    html = get_html(dir_url)
    soup = BeautifulSoup(html, 'html5lib')
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

    content = soup.find('div', attrs={'id': re.compile('^news')})
    info = content.contents[0]
    if not isinstance(info, str):
        info = ''
    # noinspection PyUnboundLocalVariable
    info_label = {'title': title, 'year': year, 'genre': genre, 'plot': info, 'director': director, 'country': country}
    content = soup.find('div', attrs={'class': 'mobile_cover'})
    img = content.find('img', attrs={'itemprop': 'image'})['src']

    if dir_url.find('/serial/') > -1:
        # noinspection PyBroadException
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
                        dir_url = data[n][n1:n2]
                        dir_url = get_vk_url(dir_url)
                    else:
                        dir_url = get_flash_url(data[n])
                    if 'vkinos.com' in dir_url:
                        dir_url = get_vkinos_url(dir_url)
                        add_link(s.string + ' | ' + ep.string, info_label, dir_url, icon_img=img)
                    elif 'staticnlcdn.com' or 'previewer.cc' in dir_url:
                        add_dir(s.string + ' | ' + ep.string, dir_url, img, referer=film_url, dir_mode="REFERER")
                    else:
                        add_dir(s.string + ' | ' + ep.string, dir_url, img, dir_mode="FILM_LINK")
                k = k + 1
        except:
            pass
    else:
        content = soup.find_all('div', attrs={'class': 'player_code'})
        content.sort(key=content_comparator, reverse=True)
        for num in content:
            if num.find('iframe') is not None:
                dir_url = num.find('iframe')['src']
                if debug:
                    print(num['id'])
                    print(dir_url)
                if re.search('(vk.com|vkontakte.ru|vk.me)', dir_url):
                    dir_url = get_vk_url(dir_url)
                    add_link(title + ' [VK]', info_label, dir_url, icon_img=img)
                # elif 'gidtv.cc' in dir_url:
                #    dir_url = get_gidtv_url(dir_url)
                #    add_link(title + ' [GIDTV]', info_label, dir_url, iconImg=img)
                elif ('staticdn.nl' or 'moonwalk.cc') in dir_url:
                    '''dir_url = get_moonwalk_url(dir_url)'''
                    print(dir_url)
                    dir_url = get_real_url(dir_url)
                    print(dir_url)
                    dir_url = dir_url.replace('iframe', 'index.m3u8')
                    print(dir_url)
                    add_link(title + ' [HD]', info_label, dir_url, icon_img=img)
                elif 'vkinos.com' in dir_url:
                    if dir_url[-2:] == '5/':
                        dir_url = get_vkinos_url(dir_url)
                        add_link(title + ' [original]', info_label, dir_url, icon_img=img)
                    else:
                        dir_url = get_vkinos_url(dir_url)
                        add_link(title + ' [mp4]', info_label, dir_url, icon_img=img)
                elif 'staticnlcdn.com' in dir_url:
                    player_page = get_html_with_referer(dir_url, film_url)
                    mp4_urls = parse_player_page(dir_url, player_page)
                    mp4_keys = list(mp4_urls.keys())
                    mp4_keys.sort(key=mp4_comparator, reverse=True)
                    for key in mp4_keys:
                        add_link(title + " [" + key + "]", info_label, mp4_urls[key], icon_img=img)
                elif 'youtube' in dir_url:
                    video_id = parse_youtube_link(dir_url)
                    youtube_url = urllib_parse.quote_plus("plugin://plugin.video.youtube/play/?video_id=" + video_id)
                    sys_url = sys.argv[0] + '?url=' + youtube_url + '&mode=PLAY'
                    add_link(u"Анонс " + title, info_label, sys_url, icon_img=img)
            if num.find('div', attrs={'id': re.compile('^videoplayer')}) is not None:
                dir_url = num.find('script').string
                dir_url = get_flash_url(dir_url)
                if num['id'] == 'basplayer_original':
                    add_link(title + ' [ORIGINAL]', info_label, dir_url, icon_img=img)
                else:
                    add_link(title + ' [MP4]', info_label, dir_url, icon_img=img)

    xbmcplugin.setContent(h, 'movies')


def content_comparator(x):
    import bs4
    if isinstance(x, bs4.element.Tag):
        current_id = x['id']
        if 'hd' in current_id:
            return 1
    return 0


def mp4_comparator(x):
    if x.isdigit():
        return int(x) + 10000
    else:
        return int(x.split('x')[0])


def parse_youtube_link(dir_url):
    return re.findall(r'embed/(\w+)', dir_url)[0]


def get_with_referer(dir_url, film_url, episode_number=0):
    if episode_number == 0:
        player_page = get_html_with_referer(dir_url, film_url)
        parse_player_page(dir_url, player_page, referer=film_url)
    else:
        player_page = get_html_with_referer(dir_url + "&episode=" + str(episode_number), film_url)
        mp4_urls = parse_player_page(dir_url, player_page, episode_number=episode_number, referer=film_url)
        mp4_keys = list(mp4_urls.keys())
        mp4_keys.sort(key=mp4_comparator, reverse=True)
        for key in mp4_keys:
            if isinstance(key, str):
                add_link("Серия " + str(episode_number) + " [" + key + "]", None, mp4_urls[key])
            else:
                add_link("Серия " + str(episode_number) + " [" + key.encode('utf-8') + "]", None, mp4_urls[key])


def get_vk_url(vk_url):
    http = get_html(vk_url)
    soup = BeautifulSoup(http, 'html5lib')
    sdata1 = soup.find('div',
                       style="position:absolute; top:50%; text-align:center; right:0pt; left:0pt; font-family:Tahoma; "
                             "font-size:12px; color:#777;")
    if sdata1:
        print(sdata1.string.strip().encode('utf-8'))
        return False
    for rec in soup.find_all('param', {'name': 'flashvars'}):
        fv = {}
        for s in rec['value'].split('&'):
            sdd = s.split('=', 1)
            fv[sdd[0]] = sdd[1]
            if s.split('=', 1)[0] == 'uid':
                uid = s.split('=', 1)[1]
            if s.split('=', 1)[0] == 'vtag':
                vtag = s.split('=', 1)[1]
            if s.split('=', 1)[0] == 'host':
                host = s.split('=', 1)[1]
            if s.split('=', 1)[0] == 'hd':
                hd = s.split('=', 1)[1]
        vk_url = host + 'u' + uid + '/videos/' + vtag + '.240.mp4'
        if int(hd) == 3:
            vk_url = host + 'u' + uid + '/videos/' + vtag + '.720.mp4'
        if int(hd) == 2:
            vk_url = host + 'u' + uid + '/videos/' + vtag + '.480.mp4'
        if int(hd) == 1:
            vk_url = host + 'u' + uid + '/videos/' + vtag + '.360.mp4'
    if not touch(vk_url):
        # noinspection PyBroadException
        try:
            if int(hd) == 3:
                # noinspection PyUnboundLocalVariable
                vk_url = fv['cache720']
            if int(hd) == 2:
                # noinspection PyUnboundLocalVariable
                vk_url = fv['cache480']
            if int(hd) == 1:
                # noinspection PyUnboundLocalVariable
                vk_url = fv['cache360']
        except:
            print('Vk parser failed')
            return False
    return vk_url


def get_moonwalk_url(link_url):
    token = re.findall('http://moonwalk.cc/video/(.+?)/', link_url)[0]

    req = urllib_request.Request('http://moonwalk.cc/sessions/create_session',
                                 data='video_token=' + token + '&video_secret=HIV5')
    # noinspection PyBroadException
    try:
        response = urllib_request.urlopen(req)
        html = response.read()
        response.close()
    except Exception:
        print('GET: Error getting page ' + link_url)
        return None

    page = json.loads(html)
    manifest_url = page["manifest_m3u8"]
    return manifest_url


def get_gidtv_url(link_url):
    http = get_html(link_url)
    n1 = http.find('setFlash(') + 10
    n2 = http.find('.mp4', n1) + 4
    gid_url = http[n1:n2]
    return gid_url


def get_flash_url(link_url):
    flash_url = re.compile(r'src=\"(http[^\"]*)\"').findall(link_url)[0]
    return flash_url


def touch(link_url):
    req = urllib_request.Request(link_url)
    # noinspection PyBroadException
    try:
        res = urllib_request.urlopen(req)
        res.close()
        return True
    except:
        return False


def add_bookmark(bookmark_id):
    cookie_jar = auth(cookielib.CookieJar())
    fav_url = site_url + '/engine/ajax/favorites.php?fav_id=' + bookmark_id + '&action=plus&skin=Baskino'
    if antizapret_enabled:
        opener = urllib_request.build_opener(urllib_request.HTTPCookieProcessor(cookie_jar),
                                             az.AntizapretProxyHandler())
    else:
        opener = urllib_request.build_opener(urllib_request.HTTPCookieProcessor(cookie_jar))
    connection = opener.open(fav_url)
    connection.close()
    notificator('Добавление закладки', 'Закладка добавлена', 3000)


def remove_bookmark(bookmark_id):
    cookie_jar = auth(cookielib.CookieJar())
    fav_url = site_url + '/engine/ajax/favorites.php?fav_id=' + bookmark_id + '&action=minus&skin=Baskino'
    if antizapret_enabled:
        opener = urllib_request.build_opener(urllib_request.HTTPCookieProcessor(cookie_jar),
                                             az.AntizapretProxyHandler())
    else:
        opener = urllib_request.build_opener(urllib_request.HTTPCookieProcessor(cookie_jar))
    connection = opener.open(fav_url)
    connection.close()
    notificator('Удаление закладки', 'Закладка удалена', 3000)
    xbmc.executebuiltin('Container.Refresh()')


def auth(cookie_jar):
    username = __settings__.getSetting('username')
    password = __settings__.getSetting('password')

    if username == "" or password == "":
        __settings__.openSettings()
        username = __settings__.getSetting('username')
        password = __settings__.getSetting('password')

    if username == "" or password == "":
        alert('Вы не авторизованы', 'Укажите логин и пароль в настройках приложения')
        print('Пользователь не аторизован. Выход.')
        sys.exit()

    req_data = {'login_name': username, 'login_password': password, 'login': 'submit'}
    req_url = site_url + '/index.php'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": site_url.split('/')[2],
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.8,bg;q=0.6,it;q=0.4,ru;q=0.2,uk;q=0.2",
        "Accept-Encoding": "windows-1251,utf-8;q=0.7,*;q=0.7",
        "Referer": site_url + "/index.php"
    }
    if antizapret_enabled:
        opener = urllib_request.build_opener(urllib_request.HTTPCookieProcessor(cookie_jar),
                                             az.AntizapretProxyHandler())
    else:
        opener = urllib_request.build_opener(urllib_request.HTTPCookieProcessor(cookie_jar))
    conn = urllib_request.Request(req_url, urllib_parse.urlencode(req_data).encode('utf-8'), headers)
    connection = opener.open(conn)
    html = connection.read()
    html = html.decode('utf-8')
    connection.close()
    if 'Ошибка авторизации' in html:
        alert('Проверьте логин и пароль', 'Неверный логин либо пароль')
        __settings__.openSettings()
        sys.exit()
    return cookie_jar


def get_vkinos_url(vkinos_url):
    req = urllib_request.Request(vkinos_url)
    res = urllib_request.urlopen(req)
    html = res.read()
    try:
        lnk = re.compile('(http://.*.mp4)"').findall(html)[0]
    except:
        lnk = "https://github.com/seppius-xbmc-repo/ru/blob/master/plugin.video.baskino.com/samples/vkerror.mp4?" \
              "raw=true"
    return lnk


def get_real_url(req_url):
    req = urllib_request.Request(req_url)
    res = urllib_request.urlopen(req)
    final_url = res.geturl()
    return final_url


def get_params():
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        parameters = sys.argv[2]
        cleanedparams = parameters.replace('?', '')
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]

    return param


h = int(sys.argv[1])
params = get_params()

mode = None
url = None
referer = None
keyword = None

try:
    mode = urllib_parse.unquote_plus(params['mode'])
except:
    pass

try:
    url = urllib_parse.unquote_plus(params['url'])
except:
    pass

try:
    referer = urllib_parse.unquote_plus(params['referer'])
except:
    pass

try:
    keyword = urllib_parse.unquote_plus(params['keyword'])
except:
    pass

if mode is None or mode == 'MAIN':
    main()
elif mode == 'SEARCH':
    search(keyword)
elif mode == 'FILMS':
    get_films_list(url)
elif mode == 'FILM_LINK':
    get_film_link(url)
elif mode == 'REFERER':
    get_with_referer(url, referer)
elif mode == 'FAVS':
    get_films_list(url)
elif mode == 'PLAY':
    play_url(url)
elif mode == 'add_bookmark':
    add_bookmark(url)
elif mode == 'remove_bookmark':
    remove_bookmark(url)

xbmcplugin.endOfDirectory(h)
