#!/usr/bin/python
# -*- coding: utf-8 -*-
# *
# *      Copyright (C) 2011 Silen
# *
# *
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# */
import re, os, urllib, cookielib, time
import urlparse
# from multiprocessing.process import Process
# -----------------------------------------------
import random, sys, json
# from urlparse import urlparse, urlunparse
# -----------------------------------------------

import urllib2

try:
    import urllib3
    from urllib3.exceptions import HTTPError

    hasUrllib3 = True
except ImportError:
    # import urllib2
    from urllib2 import HTTPError

    hasUrllib3 = False

import xbmc, xbmcgui, xbmcplugin, xbmcaddon

Addon = xbmcaddon.Addon(id='plugin.video.my-hit.ru')
icon = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'), 'icon.png'))
fcookies = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'), r'resources', r'data', r'cookies.txt'))

# load XML library
try:
    sys.path.append(os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib'))
    from BeautifulSoup import BeautifulSoup
except:
    try:
        sys.path.insert(0, os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib'))
        from BeautifulSoup import BeautifulSoup
    except:
        sys.path.append(os.path.join(os.getcwd(), r'resources', r'lib'))
        from BeautifulSoup import BeautifulSoup

        icon = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''), 'icon.png'))

import HTMLParser

hpar = HTMLParser.HTMLParser()

h = int(sys.argv[1])

host_url = 'https://my-hit.org'
movie_url = None


def showMessage(heading, message, times=3000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, icon))


# ---------- parameter/info structure -------------------------------------------
class Param:
    page = '1'
    genre = ''
    genre_name = ''
    country = ''
    country_name = ''
    year = ''
    year_name = ''
    search = ''


class Info:
    img = ''
    url = '*'
    title = ''
    year = ''
    genre = ''
    country = ''
    director = ''
    text = ''


# ---------- get parameters -----------------------------------------------------
def Get_Parameters(params):
    # -- page
    try:
        p.page = urllib.unquote_plus(params['page'])
    except:
        p.page = '1'
    # -- genre
    try:
        p.genre = urllib.unquote_plus(params['genre'])
    except:
        p.genre = ''
    try:
        p.genre_name = urllib.unquote_plus(params['genre_name'])
    except:
        p.genre_name = ''
    # -- country
    try:
        p.country = urllib.unquote_plus(params['country'])
    except:
        p.country = ''
    try:
        p.country_name = urllib.unquote_plus(params['country_name'])
    except:
        p.country_name = ''
    # -- year
    try:
        p.year = urllib.unquote_plus(params['year'])
    except:
        p.year = ''
    try:
        p.year_name = urllib.unquote_plus(params['year_name'])
    except:
        p.year_name = ''
    # --search
    try:
        p.search = urllib.unquote_plus(params['search'])
    except:
        p.search = ''
    # -----
    return p


# ---------- get web page -------------------------------------------------------
def get_HTML(url, post=None, ref=None):
    # xbmc.log(url)

    request = urllib2.Request(url, post)

    host = urlparse.urlsplit(url).hostname

    request.add_header('User-Agent',
                       'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host', host)
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Language', 'ru-RU')
    request.add_header('Referer', ref)

    try:
        f = urllib2.urlopen(request)
    except IOError, e:
        if hasattr(e, 'reason'):
            xbmc.log('We failed to reach a server.')
        elif hasattr(e, 'code'):
            xbmc.log('The server couldn\'t fulfill the request.')
    html = f.read()
    return html


# ---------- get MY-HIT.RU URL --------------------------------------------------
def Get_URL(par):
    # http://my-hit.ru/index.php?module=search&func=view&result_orderby=score&result_order_asc=0&search_string=%EA%E8%ED&x=0&y=0

    url = host_url + '/film/'

    par_div = ''
    filter = ''
    # -- year
    if par.year <> '':
        if filter != '':
            filter += '-'
        filter += par.year
        par_div = '/'
    # -- genre
    if par.genre <> '':
        if filter != '':
            filter += '-'
        filter += par.genre
        par_div = '/'
    # -- country
    if par.country <> '':
        if filter != '':
            filter += '-'
        filter += par.country
        par_div = '/'
    # -- page
    url += filter + par_div + '?p=' + par.page

    return url


# ----------- get Header string ---------------------------------------------------
def Get_Header(par, mcount, pcount):
    info = 'Фильмов: ' + '[COLOR FF00FF00]' + str(mcount) + '[/COLOR]'

    if pcount > 1:
        info += ' | Pages: ' + '[COLOR FF00FF00]' + par.page + '/' + str(pcount) + '[/COLOR]'

    if par.genre <> '':
        info += ' | Жанр: ' + '[COLOR FF00FFF0]' + par.genre_name + '[/COLOR]'

    if par.year <> '':
        info += ' | Год: ' + '[COLOR FFFFF000]' + par.year_name + '[/COLOR]'

    if par.country <> '':
        info += ' | Страна: ' + '[COLOR FFFF00FF]' + par.country_name + '[/COLOR]'

    if par.search <> '':
        info += ' | Поиск: ' + '[COLOR FFFF9933]' + par.search + '[/COLOR]'

    # -- info line
    name = info
    i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
    u = sys.argv[0] + '?mode=EMPTY'
    u += '&name=%s' % urllib.quote_plus(name)
    # -- filter parameters
    u += '&page=%s' % urllib.quote_plus(par.page)
    u += '&genre=%s' % urllib.quote_plus(par.genre)
    u += '&genre_name=%s' % urllib.quote_plus(par.genre_name)
    u += '&country=%s' % urllib.quote_plus(par.country)
    u += '&country_name=%s' % urllib.quote_plus(par.country_name)
    u += '&year=%s' % urllib.quote_plus(par.year)
    u += '&year_name=%s' % urllib.quote_plus(par.year_name)
    xbmcplugin.addDirectoryItem(h, u, i, True)

    # -- search
    '''
    if par.genre == '' and par.country == '' and par.page == '1' and par.search == '':
        name = '[COLOR FFFF9933][Поиск][/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=SEARCH'
        u += '&name=%s'%urllib.quote_plus(name)
        #-- filter parameters
        u += '&page=%s'%urllib.quote_plus(par.page)
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&country=%s'%urllib.quote_plus(par.country)
        u += '&country_name=%s'%urllib.quote_plus(par.country_name)
        u += '&year=%s'%urllib.quote_plus(par.year)
        u += '&year_name=%s'%urllib.quote_plus(par.year_name)
        xbmcplugin.addDirectoryItem(h, u, i, True)
    '''
    # -- genres
    if par.genre == '' and par.page == '1' and par.search == '':
        name = '[COLOR FF00FFF0][Жанры][/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=GENRES'
        u += '&name=%s' % urllib.quote_plus(name)
        # -- filter parameters
        u += '&page=%s' % urllib.quote_plus(par.page)
        u += '&genre=%s' % urllib.quote_plus(par.genre)
        u += '&genre_name=%s' % urllib.quote_plus(par.genre_name)
        u += '&country=%s' % urllib.quote_plus(par.country)
        u += '&country_name=%s' % urllib.quote_plus(par.country_name)
        u += '&year=%s' % urllib.quote_plus(par.year)
        u += '&year_name=%s' % urllib.quote_plus(par.year_name)
        xbmcplugin.addDirectoryItem(h, u, i, True)
    # -- alphabet
    if par.country == '' and par.page == '1' and par.search == '':
        name = '[COLOR FFFF00FF][Страна][/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=COUNTRY'
        u += '&name=%s' % urllib.quote_plus(name)
        # -- filter parameters
        u += '&page=%s' % urllib.quote_plus(par.page)
        u += '&genre=%s' % urllib.quote_plus(par.genre)
        u += '&genre_name=%s' % urllib.quote_plus(par.genre_name)
        u += '&country=%s' % urllib.quote_plus(par.country)
        u += '&country_name=%s' % urllib.quote_plus(par.country_name)
        u += '&year=%s' % urllib.quote_plus(par.year)
        u += '&year_name=%s' % urllib.quote_plus(par.year_name)
        xbmcplugin.addDirectoryItem(h, u, i, True)
    # -- year
    if par.year == '' and par.page == '1' and par.search == '':
        name = '[COLOR FFFFF000][Год][/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=YEAR'
        u += '&name=%s' % urllib.quote_plus(name)
        # -- filter parameters
        u += '&page=%s' % urllib.quote_plus(par.page)
        u += '&genre=%s' % urllib.quote_plus(par.genre)
        u += '&genre_name=%s' % urllib.quote_plus(par.genre_name)
        u += '&country=%s' % urllib.quote_plus(par.country)
        u += '&country_name=%s' % urllib.quote_plus(par.country_name)
        u += '&year=%s' % urllib.quote_plus(par.year)
        u += '&year_name=%s' % urllib.quote_plus(par.year_name)
        xbmcplugin.addDirectoryItem(h, u, i, True)


def Empty():
    return False


# ---------- movie list ---------------------------------------------------------
def Movie_List(params):
    # -- get filter parameters
    par = Get_Parameters(params)

    # == get movie list =====================================================
    url = Get_URL(par)
    # print url
    html = get_HTML(url)

    # -- parsing web page --------------------------------------------------
    soup = BeautifulSoup(html)

    pinfo = \
    soup.find('div', {'class': "col-xs-10 col-md-8 conten fullstory"}).find('div', {'class': "col-xs-3"}).text.split(
        ':')[1].replace('(', '').replace(')', '')
    mcount = int(pinfo.split(' ')[0])
    pfilm = int(pinfo.split(' ')[1].split('-')[1])
    pcount = mcount / pfilm + 1

    Get_Header(par, mcount, pcount)

    nav = soup.find("div", {"class": "film-list"})

    for mov in nav.findAll("div", {"class": "row"}):
        mi.title = mov.find('div', {'class': 'col-xs-3 text-center'}).find('a')['title'].encode('utf-8')
        mi.url = host_url + mov.find('div', {'class': 'col-xs-3 text-center'}).find('a')['href']
        mi.img = host_url + mov.find('div', {'class': 'col-xs-3 text-center'}).find('a').find('img')['src']

        for li in mov.find('ul', {'class': "list-unstyled text-right"}).findAll('li'):
            if li.find('b').text == u'Жанр:':
                mi.genre = li.find('a').text.encode('utf-8')
            if li.find('b').text == u'Год:':
                mi.year = li.find('a').text.encode('utf-8')
            if li.find('b').text == u'Страна':
                mi.country = li.find('a').text.encode('utf-8')
            if li.find('b').text == u'Режиссер:':
                mi.director = li.find('a').text.encode('utf-8')
            if li.find('b').text == u'Краткое описание:':
                mi.text = li.find('p').text.encode('utf-8')

        # -- add movie to the list ---------------------------------------
        if mi.url == '*':
            name = '[COLOR FFFF0000]' + mi.title + '[/COLOR]'
        else:
            name = '[COLOR FFC3FDB8]' + mi.title + '[/COLOR]'

        i = xbmcgui.ListItem(name, iconImage=mi.img, thumbnailImage=mi.img)
        u = sys.argv[0] + '?mode=PLAY_MODE'
        u += '&name=%s' % urllib.quote_plus(mi.title)
        u += '&url=%s' % urllib.quote_plus(mi.url)
        u += '&img=%s' % urllib.quote_plus(mi.img)
        i.setInfo(type='video', infoLabels={'title': mi.title,
                                            'year': mi.year,
                                            'director': mi.director,
                                            'plot': mi.text,
                                            'country': mi.country,
                                            'genre': mi.genre})
        i.setProperty('fanart_image', mi.img)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    # -- next page link
    if int(par.page) < pcount:
        name = '[NEXT PAGE]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=MOVIE'
        u += '&name=%s' % urllib.quote_plus(name)
        # -- filter parameters
        u += '&page=%s' % urllib.quote_plus(str(int(par.page) + 1))
        u += '&genre=%s' % urllib.quote_plus(par.genre)
        u += '&genre_name=%s' % urllib.quote_plus(par.genre_name)
        u += '&country=%s' % urllib.quote_plus(par.country)
        u += '&country_name=%s' % urllib.quote_plus(par.country_name)
        u += '&year=%s' % urllib.quote_plus(par.year)
        u += '&year_name=%s' % urllib.quote_plus(par.year_name)
        xbmcplugin.addDirectoryItem(h, u, i, True)
    xbmcplugin.endOfDirectory(h)


# ---------- search movie list --------------------------------------------------
def Search_List(params):
    list = []
    # -- get filter parameters
    par = Get_Parameters(params)

    # show search dialog
    skbd = xbmc.Keyboard()
    skbd.setHeading('Поиск фильмов.')
    skbd.doModal()
    if skbd.isConfirmed():
        SearchStr = skbd.getText().split(':')
        par.search = SearchStr[0]
    else:
        return False

    # == get movie list =====================================================
    url = host_url + '/index.php?module=search&func=view&result_orderby=score&result_order_asc=0&result_perpage=1000&search_string=%s&x=0&y=0' % urllib.quote(
        par.search.decode('utf-8').encode('cp1251'))
    # print url
    html = get_HTML(url)

    # -- parsing web page --------------------------------------------------
    soup = BeautifulSoup(html, fromEncoding="windows-1251")

    pcount = 1

    # -- get list of found movies
    flag = 0
    for rec in soup.findAll("tr"):
        try:
            if rec.find('a').text.find(u'(фильм)') <> -1:
                m_name = rec.find('a').text.replace(u'(фильм)', '').encode('utf-8')
                flag = 1
            elif flag == 1:
                m_url = rec.find('a')['href']
                m_url = host_url + '/film/' + m_url.split('&id=')[1] + '/online'

                m_img = host_url + rec.find('img')['src']
                m_text = unescape(rec.text).encode('utf-8')
                flag = 0
                list.append({'name': m_name, 'url': m_url, 'img': m_img, 'text': m_text})
        except:
            pass
    mcount = len(list)

    if mcount == 0:
        return False

    # -- add header info
    Get_Header(par, mcount, pcount)

    for mov in list:
        # -- add movie to the list ------------------------------------------
        name = '[COLOR FFC3FDB8]' + mov['name'] + '[/COLOR]'

        i = xbmcgui.ListItem(name, iconImage=mi.img, thumbnailImage=mi.img)
        u = sys.argv[0] + '?mode=PLAY'
        u += '&name=%s' % urllib.quote_plus(mov['name'])
        u += '&url=%s' % urllib.quote_plus(mov['url'])
        u += '&img=%s' % urllib.quote_plus(mov['img'])
        i.setInfo(type='video', infoLabels={'title': mov['name'],
                                            'plot': mov['text']})
        i.setProperty('fanart_image', mov['img'])
        xbmcplugin.addDirectoryItem(h, u, i, False)

    xbmcplugin.endOfDirectory(h)


# ---------- get genge list -----------------------------------------------------
def Genre_List(params):
    # -- get filter parameters
    par = Get_Parameters(params)

    # -- get generes
    url = host_url + '/film/'
    html = get_HTML(url)

    # -- parsing web page ------------------------------------------------------
    soup = BeautifulSoup(html)
    nav = soup.find('div', {'class': "sidebar-nav"}).find('ul', {'class': "nav nav-list"})
    is_genre = False

    for item in nav.findAll('li'):
        if item.get('class') == "nav-header":
            if is_genre == False and item.text == u'Жанр:':
                is_genre = True
            else:
                is_genre = False

        if is_genre:
            if item.find('a'):
                name = (item.find('a').text).encode('utf-8')
                genre_id = item.find('a').get('href').replace('/film/', '').replace('/', '')
                # ---
                i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
                u = sys.argv[0] + '?mode=MOVIE'
                u += '&name=%s' % urllib.quote_plus(name)
                # -- filter parameters
                u += '&page=%s' % urllib.quote_plus(par.page)
                u += '&genre=%s' % urllib.quote_plus(genre_id)
                u += '&genre_name=%s' % urllib.quote_plus(name)
                u += '&country=%s' % urllib.quote_plus(par.country)
                u += '&country_name=%s' % urllib.quote_plus(par.country_name)
                u += '&year=%s' % urllib.quote_plus(par.year)
                u += '&year_name=%s' % urllib.quote_plus(par.year_name)
                xbmcplugin.addDirectoryItem(h, u, i, True)

    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(h)


# ---------- get year list -----------------------------------------------------
def Year_List(params):
    # -- get filter parameters
    par = Get_Parameters(params)

    # -- get generes
    url = host_url + '/film/'
    html = get_HTML(url)

    # -- parsing web page ------------------------------------------------------
    soup = BeautifulSoup(html)
    nav = soup.find('div', {'class': "sidebar-nav"}).find('ul', {'class': "nav nav-list"})
    is_year = False
    is_Found = False

    for item in nav.findAll('li'):
        if item.get('class') == "nav-header":
            if is_year == False and item.text == u'Год:':
                is_year = True
            else:
                is_year = False

        if is_year:
            if item.find('a'):
                if item.find('a')['href'] == '#':
                    is_Found = True
                    continue

        if is_Found:
            if item.find('a'):
                name = (item.find('a').text).encode('utf-8')
                year_id = item.find('a').get('href').replace('/film/', '').replace('/', '')
                # ---
                i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
                u = sys.argv[0] + '?mode=MOVIE'
                u += '&name=%s' % urllib.quote_plus(name)
                # -- filter parameters
                u += '&page=%s' % urllib.quote_plus(par.page)
                u += '&genre=%s' % urllib.quote_plus(par.genre)
                u += '&genre_name=%s' % urllib.quote_plus(par.genre_name)
                u += '&country=%s' % urllib.quote_plus(par.country)
                u += '&country_name=%s' % urllib.quote_plus(par.country_name)
                u += '&year=%s' % urllib.quote_plus(year_id)
                u += '&year_name=%s' % urllib.quote_plus(name)
                xbmcplugin.addDirectoryItem(h, u, i, True)

    xbmcplugin.endOfDirectory(h)


# ---------- get year list -----------------------------------------------------
def Country_List(params):
    # -- get filter parameters
    par = Get_Parameters(params)

    # -- get generes
    url = host_url + '/film/'
    html = get_HTML(url)

    # -- parsing web page ------------------------------------------------------
    soup = BeautifulSoup(html)
    nav = soup.find('div', {'class': "sidebar-nav"}).find('ul', {'class': "nav nav-list"})
    is_year = False

    for item in nav.findAll('li'):
        if item.get('class') == "nav-header":
            if is_year == False and item.text == u'Страна:':
                is_year = True
            else:
                is_year = False

        if is_year:
            if item.find('a'):
                name = (item.find('a').text).encode('utf-8')
                country_id = item.find('a').get('href').replace('/film/', '').replace('/', '')
                # ---
                i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
                u = sys.argv[0] + '?mode=MOVIE'
                u += '&name=%s' % urllib.quote_plus(name)
                # -- filter parameters
                u += '&page=%s' % urllib.quote_plus(par.page)
                u += '&genre=%s' % urllib.quote_plus(par.genre)
                u += '&genre_name=%s' % urllib.quote_plus(par.genre_name)
                u += '&country=%s' % urllib.quote_plus(country_id)
                u += '&country_name=%s' % urllib.quote_plus(name)
                u += '&year=%s' % urllib.quote_plus(par.year)
                u += '&year_name=%s' % urllib.quote_plus(par.year_name)
                xbmcplugin.addDirectoryItem(h, u, i, True)

    xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(h)


# ---------- show availabl;e video sources --------------------------------------
def Play_Mode(params):
    url = urllib.unquote_plus(params['url']) + 'online/'
    img = urllib.unquote_plus(params['img'])
    name = urllib.unquote_plus(params['name'])

    # -- get play list
    html = get_HTML(url)
    pl = re.compile(u'var flashvars \= \{(.+?)\}', re.MULTILINE | re.DOTALL).findall(html)[0].replace("'", '')
    # xbmc.log(pl)
    for rec in pl.split(','):
        if rec.strip().split(':', 1)[0] == 'pl':
            url = host_url + rec.split(':', 1)[1].strip()
            url_type = 'PL'
        if rec.strip().split(':')[0] == 'file':
            url = rec.split(':', 1)[1].strip()
            url_type = 'FILE'

    list = []
    # xbmc.log(url_type)
    try:
        if url_type == 'PL':
            html = get_HTML(url)

            for rec in json.loads(html)['playlist']:
                # xbmc.log('.....')
                # xbmc.log(rec['file'])
                _url = rec['file']
                _img = rec['poster']
                list.append({'url': _url, 'img': _img, 'type': 'AHDS'})
            '''
            mov = re.compile(u'\[\{"file":"(.+?)"', re.MULTILINE|re.DOTALL).findall(html)[0]

            mov =  mov.replace('\\','').replace('[','#').replace(']','#')
            mov_u = mov.split('#')

            xbmc.log(mov)
            '''
            mov_q_def = {'9': '1080p', '8': ' 720p', '7': ' 480p', '6': ' 360p', '5': ' 320p', '4': ' 240p'}
        else:
            list.append({'url': url, 'img': img, 'type': 'AHDS'})

        # -- old movie format
        for mov in list:
            # xbmc.log('---')
            # xbmc.log(mov['url'])
            name_ = '[COLOR FFC3FDB8]' + name + '[/COLOR]'
            i = xbmcgui.ListItem(name_, iconImage=img, thumbnailImage=img)
            u = sys.argv[0] + '?mode=PLAY'
            u += '&name=%s' % urllib.quote_plus('[COLOR FFC3FDB8]' + name + '[/COLOR]')
            u += '&url=%s' % urllib.quote_plus(mov['url'])
            u += '&img=%s' % urllib.quote_plus(img)
            u += '&type=%s' % urllib.quote_plus(mov['type'])
            i.setProperty('fanart_image', img)
            xbmcplugin.addDirectoryItem(h, u, i, False)
    except:
        pass

    # xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(h)


# -------------------------------------------------------------------------------

def playF4mLink(url, name, proxy=None, use_proxy_for_chunks=False, auth_string=None, streamtype='HDS',
                setResolved=False):
    from F4mProxy import f4mProxyHelper
    player = f4mProxyHelper()
    maxbitrate = 0
    simpleDownloader = False
    if setResolved:
        urltoplay, item = player.playF4mLink(url, name, proxy, use_proxy_for_chunks, maxbitrate, simpleDownloader,
                                             auth_string, streamtype, setResolved)
        item.setProperty("IsPlayable", "true")
        xbmcplugin.setResolvedUrl(h, True, item)

    else:
        xbmcplugin.endOfDirectory(h, cacheToDisc=False)
        player.playF4mLink(url, name, proxy, use_proxy_for_chunks, maxbitrate, simpleDownloader, auth_string,
                           streamtype, setResolved)

    return


def PLAY(params):
    global movie_url, IP_ADDRESS, PORT_NUMBER, PROXY_THREADS
    # -- parameters
    movie_url = urllib.unquote_plus(params['url'])
    img = urllib.unquote_plus(params['img'])
    name = urllib.unquote_plus(params['name'])
    type_ = urllib.unquote_plus(params['type'])

    xbmc.log('-------------')
    xbmc.log(type_)

    if type_ == 'FLV':
        i = xbmcgui.ListItem(name, path=urllib.unquote(movie_url), thumbnailImage=img)
        xbmc.Player().play(movie_url, i)
    else:
        # -- play video using f4m proxy
        playF4mLink(movie_url, name)


# -------------------------------------------------------------------------------
def unescape(text):
    try:
        text = hpar.unescape(text)
    except:
        text = hpar.unescape(text.decode('utf8'))

    try:
        text = unicode(text, 'utf-8')
    except:
        text = text

    return text


def get_url(url):
    return "http:" + urllib.quote(url.replace('http:', ''))


# -------------------------------------------------------------------------------
def get_params(paramstring):
    param = []
    if len(paramstring) >= 2:
        params = paramstring
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


# -------------------------------------------------------------------------------
params = get_params(sys.argv[2])

# get cookies from last session
cj = cookielib.FileCookieJar(fcookies)
hr = urllib2.HTTPCookieProcessor(cj)
opener = urllib2.build_opener(hr)
urllib2.install_opener(opener)

p = Param()
mi = Info()

mode = None

try:
    mode = urllib.unquote_plus(params['mode'])
except:
    Movie_List(params)

if mode == 'MOVIE':
    Movie_List(params)
if mode == 'SEARCH':
    Search_List(params)
elif mode == 'GENRES':
    Genre_List(params)
elif mode == 'YEAR':
    Year_List(params)
elif mode == 'COUNTRY':
    Country_List(params)
elif mode == 'EMPTY':
    Empty()
elif mode == 'PLAY_MODE':
    Play_Mode(params)
elif mode == 'PLAY':
    PLAY(params)
