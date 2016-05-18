#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#   Writer (c) 23/06/2011, Khrysev D.A., E-mail: x86demon@gmail.com
#
#   This Program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2, or (at your option)
#   any later version.
#
#   This Program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; see the file COPYING.  If not, write to
#   the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#   http://www.gnu.org/licenses/gpl.html

__author__ = "Dmitry Khrysev"
__license__ = "GPL"
__maintainer__ = "Dmitry Khrysev"
__email__ = "x86demon@gmail.com"
__status__ = "Production"

import socket
socket.setdefaulttimeout(50)

import os
import re
import sys
import urllib
import hashlib

import simplejson as json

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs
from lib.fsua import FsUa
from lib.httpclient import HttpClient

import SimpleDownloader as downloader
from BeautifulSoup import BeautifulSoup
from lib import strutils, kodi

# from pydev import pydevd
# pydevd.settrace('localhost', port=63342, stdoutToServer=True, stderrToServer=True)

__settings__ = xbmcaddon.Addon(id='plugin.video.fs.ua')
__addondir__ = xbmc.translatePath(__settings__.getAddonInfo('profile'))
icon = xbmc.translatePath(os.path.join(__settings__.getAddonInfo('path'), 'icon.png'))
cache_path = xbmc.translatePath(os.path.join(__addondir__, 'cache'))

if not xbmcvfs.exists(__addondir__):
    xbmcvfs.mkdir(__addondir__)

if not xbmcvfs.exists(cache_path):
    xbmcvfs.mkdir(cache_path)

__language__ = __settings__.getLocalizedString

siteUrl = __settings__.getSetting('Site URL')
httpSiteUrl = 'http://' + siteUrl

client = HttpClient(http_site_url=httpSiteUrl, cookie_path=__addondir__)
fs_ua = FsUa(settings=__settings__, client=client)

h = int(sys.argv[1])


def show_message(heading, message, times=3000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, icon))


def logout(params):
    client.GET(httpSiteUrl + '/logout.aspx', httpSiteUrl)
    __settings__.setSetting("Login", "")
    __settings__.setSetting("Password", "")


def check_login():
    login = __settings__.getSetting("Login")
    password = __settings__.getSetting("Password")

    if len(login) > 0:
        http = client.GET(httpSiteUrl, httpSiteUrl)
        if http is None:
            return False

        beautifulSoup = BeautifulSoup(http)
        userPanel = beautifulSoup.find('a', 'm-header__user-link_favourites')

        if userPanel is None:
            client.remove_cookie()

            loginResponse = client.GET(httpSiteUrl + '/login.aspx', httpSiteUrl, {
                'login': login,
                'passwd': password,
                'remember': 'on'
            })

            loginSoup = BeautifulSoup(loginResponse)
            userPanel = loginSoup.find('a', 'm-header__user-link_favourites')
            if userPanel is None:
                show_message('Login', 'Check login and password', 3000)
            else:
                return True
        else:
            return True
    return False


def main(params):
    li = xbmcgui.ListItem('[Видео]')
    uri = strutils.construct_request({
        'href': httpSiteUrl + '/video/',
        'mode': 'get_categories',
        'category': 'video',
        'filter': '',
        'firstPage': 'yes'
    })
    xbmcplugin.addDirectoryItem(h, uri, li, True)

    li = xbmcgui.ListItem('[Аудио]')
    uri = strutils.construct_request({
        'href': httpSiteUrl + '/audio/',
        'mode': 'get_categories',
        'category': 'audio',
        'filter': '',
        'firstPage': 'yes'
    })
    xbmcplugin.addDirectoryItem(h, uri, li, True)

    if check_login():
        li = xbmcgui.ListItem('В процессе')
        uri = strutils.construct_request({
            'mode': 'get_fav_categories',
            'type': 'inprocess'
        })
        xbmcplugin.addDirectoryItem(h, uri, li, True)

        li = xbmcgui.ListItem('Избранное')
        uri = strutils.construct_request({
            'mode': 'get_fav_categories',
            'type': 'favorites'
        })
        xbmcplugin.addDirectoryItem(h, uri, li, True)

        li = xbmcgui.ListItem('Рекомендуемое')
        uri = strutils.construct_request({
            'mode': 'get_fav_categories',
            'type': 'recommended'
        })
        xbmcplugin.addDirectoryItem(h, uri, li, True)

        li = xbmcgui.ListItem('На будущее')
        uri = strutils.construct_request({
            'mode': 'get_fav_categories',
            'type': 'forlater'
        })
        xbmcplugin.addDirectoryItem(h, uri, li, True)

        li = xbmcgui.ListItem('Я рекомендую')
        uri = strutils.construct_request({
            'mode': 'get_fav_categories',
            'type': 'irecommended'
        })
        xbmcplugin.addDirectoryItem(h, uri, li, True)

        li = xbmcgui.ListItem('Завершенное')
        uri = strutils.construct_request({
            'mode': 'get_fav_categories',
            'type': 'finished'
        })
        xbmcplugin.addDirectoryItem(h, uri, li, True)

    xbmcplugin.endOfDirectory(h, True)


def get_categories(params):
    section = params['category']
    categoryUrl = urllib.unquote_plus(params['href'])

    http = client.GET(categoryUrl, httpSiteUrl)
    if http is None:
        return False

    beautifulSoup = BeautifulSoup(http)
    categorySubmenu = beautifulSoup.find('div', 'm-header__menu-section_type_' + section)
    if categorySubmenu is None:
        show_message('ОШИБКА', 'Неверная страница', 3000)
        return False

    subcategories = categorySubmenu.findAll('a', 'b-header__menu-subsections-item')
    if len(subcategories) == 0:
        show_message('ОШИБКА', 'Неверная страница', 3000)
        return False

    for subcategory in subcategories:
        label = subcategory.find('span')
        li = xbmcgui.ListItem('[' + label.string + ']')
        uri = strutils.construct_request({
            'href': client.get_full_url(subcategory['href']),
            'mode': 'readcategory',
            'cleanUrl': client.get_full_url(subcategory['href']),
            'section': section,
            'start': 0,
            'filter': ''
        })
        xbmcplugin.addDirectoryItem(h, uri, li, True)
    loadMainPageItems = __settings__.getSetting('Load main page items')
    if loadMainPageItems == 'true':
        readcategory({
            'href': params['href'],
            'cleanUrl': params['href'],
            'section': section,
            'start': 0,
            'filter': '',
        })
    else:
        xbmcplugin.endOfDirectory(h)


def get_fav_categories(params):
    http = client.GET(httpSiteUrl + '/myfavourites.aspx?page=' + params['type'], httpSiteUrl)
    if http is None:
        return False

    beautifulSoup = BeautifulSoup(http)
    favSectionsContainer = beautifulSoup.find('div', 'b-tabpanels')
    if favSectionsContainer is None:
        show_message('ОШИБКА', 'В избранном пусто', 3000)
        return False

    favSections = favSectionsContainer.findAll('div', 'b-category')
    if len(favSections) == 0:
        show_message('ОШИБКА', 'В избранном пусто', 3000)
        return False
    sectionRegexp = re.compile("\s*\{\s*section:\s*'([^']+)")
    subsectionRegexp = re.compile("subsection:\s*'([^']+)")
    for favSection in favSections:
        rel = favSection.find('a', 'b-add')['rel'].encode('utf-8')
        section = sectionRegexp.findall(rel)[0]
        subsection = subsectionRegexp.findall(rel)[0]
        title = str(favSection.find('a', 'item').find('b').string)
        li = xbmcgui.ListItem(title)

        uri = strutils.construct_request({
            'mode': 'read_favs',
            'section': section,
            'subsection': subsection,
            'type': params['type'],
            'page': 0
        })
        xbmcplugin.addDirectoryItem(h, uri, li, True)
    xbmcplugin.endOfDirectory(h, True)


def read_favs(params):
    href = httpSiteUrl + "/myfavourites.aspx?ajax&section=" + params['section'] \
           + "&subsection=" + params['subsection'] \
           + "&rows=1&curpage=" + params['page'] \
           + "&action=get_list&setrows=1&page=" + params['type']

    favorites = read_fav_data(urllib.unquote_plus(href))
    if len(favorites) == 0:
        show_message('ОШИБКА', 'В избранном пусто', 3000)
        return False

    for item in favorites:
        additional = ''
        if item['season'] > 0:
            additional = ' (s%se%s)' % (item['season'], item['episode'])
        li = xbmcgui.ListItem(
            strutils.html_entities_decode(item['title']) + additional,
            iconImage=fs_ua.thumbnail(item['cover']),
            thumbnailImage=fs_ua.poster(item['cover'])
        )
        li.setProperty('IsPlayable', 'false')

        id = item['href'].split('/')[-1]
        li.addContextMenuItems([
            (
                __language__(50003), "XBMC.RunPlugin(%s)" % strutils.construct_request({
                    'mode': 'addto',
                    'section': 'favorites',
                    'id': id,
                    'title': item['title']
                })
            ),
            (
                __language__(50004), "XBMC.RunPlugin(%s)" % strutils.construct_request({
                    'mode': 'addto',
                    'section': 'playlist',
                    'id': id,
                    'title': item['title']
                })
            )
        ])

        uri = strutils.construct_request({
            'href': item['href'],
            'referer': href,
            'mode': 'read_dir',
            'cover': item['cover'],
            'folder': 0,
            'isMusic': item['isMusic']
        })
        xbmcplugin.addDirectoryItem(h, uri, li, True)

    li = xbmcgui.ListItem('[NEXT PAGE >]')
    li.setProperty('IsPlayable', 'false')
    params['page'] = int(params['page']) + 1
    uri = strutils.construct_request(params)
    xbmcplugin.addDirectoryItem(h, uri, li, True)

    xbmcplugin.endOfDirectory(h)


def read_fav_data(favoritesUrl):
    favorites = []
    http = client.GET(favoritesUrl, httpSiteUrl)
    if http is None:
        return favorites

    data = json.loads(str(http))
    http = data['content'].encode('utf-8')

    beautifulSoup = BeautifulSoup(http)
    container = beautifulSoup.find('div', 'b-posters')
    if container is None:
        return favorites

    items = container.findAll('div', 'b-poster-thin__wrapper ')
    if len(items) == 0:
        return favorites

    cover_regexp = re.compile("url\s*\('([^']+)")
    episode_regexp = re.compile("s(\d+)e(\d+)")

    for wrapper in items:
        item = wrapper.find('a', 'b-poster-thin')

        season = 0
        episode = 0

        episode_data = episode_regexp.findall(str(wrapper))
        if episode_data is not None and len(episode_data) > 0:
            season = episode_data[0][0]
            episode = episode_data[0][1]

        cover = cover_regexp.findall(str(item['style']))[0]
        title = str(item.find('b', 'subject-link').find('span').string)
        href = client.get_full_url(item['href'])

        isMusic = "no"
        if re.search('audio', href):
            isMusic = "yes"

        #get_material_details(href)

        favorites.append({
            'href': href,
            'title': strutils.html_entities_decode(title),
            'cover': cover,
            'season': season,
            'episode': episode,
            'isMusic': isMusic
        })

    return favorites


def get_material_details(url):
    data = {}
    cache_file_name = '%s.json' % hashlib.md5(url).hexdigest()
    cache_file_path = os.path.join(cache_path, cache_file_name)

    if xbmcvfs.exists(cache_file_path):
        fp = open(cache_file_path, 'r')
        data = json.load(fp)
        fp.close()

        return data

    http = client.GET(url, httpSiteUrl)
    if http is None:
        return data

    cover_regexp = re.compile("url\s*\(([^\)]+)")

    beautifulSoup = BeautifulSoup(http)

    info = beautifulSoup.find('div', 'item-info')
    genre_element_container = info.findAll('span', {"itemprop" : "genre"})
    genres = []
    for genre_element in genre_element_container:
        genres.append(strutils.fix_string(genre_element.find('span').string.strip()))

    title = strutils.fix_string(beautifulSoup.find('div', 'b-tab-item__title-inner').find('span').string)
    original_title = strutils.html_entities_decode(beautifulSoup.find('div', 'b-tab-item__title-origin').string)
    description = beautifulSoup.find('p', 'item-decription').string.encode('utf-8')

    poster = fs_ua.poster(client.get_full_url(beautifulSoup.find('div', 'poster-main').find('img')['src']))
    print poster

    images_container = beautifulSoup.find('div', 'b-tab-item__screens')
    image_elements = images_container.findAll('a')
    images = []
    for image_element in image_elements:
        images.append(
            client.get_full_url(
                fs_ua.poster(
                    cover_regexp.findall(str(image_element['style']).strip())[0]
                )
            )
        )

    rating_positive = beautifulSoup.find('div', 'm-tab-item__vote-value_type_yes').string.strip()
    rating_negative = beautifulSoup.find('div', 'm-tab-item__vote-value_type_no').string.strip()

    data = {
        'title': title.strip(),
        'original_title': original_title.strip(),
        'poster': poster,
        'description': description,
        'images': images,
        'genres': genres,
        'rating_positive': rating_positive,
        'rating_negative': rating_negative
    }

    fp = open(cache_file_path, 'w')
    json.dump(data, fp)
    fp.close()

    return data


def readcategory(params):
    start = int(params['start'])
    category_href = urllib.unquote_plus(params['href'])

    categoryUrl = fs_ua.get_url_with_sort_by(
        category_href,
        params['section'],
        params['start'],
        'detailed'
    )

    http = client.GET(categoryUrl, httpSiteUrl)
    if http is None:
        return False

    try:
        params['filter']
    except:
        params['filter'] = ''

    beautifulSoup = BeautifulSoup(http)
    itemsClass = 'b-poster-detail'

    items = beautifulSoup.findAll('div', itemsClass)

    if len(items) == 0:
        show_message('ОШИБКА', 'Неверная страница', 3000)
        return False
    else:
        if start == 0 and 'hideFirstPageData' not in params:
            load_first_page_sections(category_href, params)

        for item in items:
            cover = None
            href = None

            img = item.find('img')
            link = item.find('a', itemsClass + '__link')
            title = item.find('span', 'b-poster-detail__title').contents[0]
            if img is not None:
                cover = img['src']
                href = client.get_full_url(link['href'])

            if title is not None:
                plot = []
                details = item.find('span', 'b-poster-detail__description').contents
                for detail in details:
                    try:
                        plot.append(detail.encode('utf8'))
                    except:
                        pass
                titleText = strutils.html_entities_decode(title.encode('utf8'))
                li = xbmcgui.ListItem(titleText, iconImage=fs_ua.thumbnail(cover),
                                      thumbnailImage=fs_ua.poster(cover))
                if plot != '':
                    li.setInfo(type=params['section'], infoLabels={'title': titleText, 'plot': plot})
                li.setProperty('IsPlayable', 'false')

                id = str(link['href'].split('/')[-1])
                li.addContextMenuItems([
                    (
                    __language__(50001), "XBMC.RunPlugin(%s)" % strutils.construct_request({
                            'mode': 'addto',
                            'section': 'favorites',
                            'id': id
                        })
                    ),
                    (
                    __language__(50002), "XBMC.RunPlugin(%s)" % strutils.construct_request({
                            'mode': 'addto',
                            'section': 'playlist',
                            'id': id
                        })
                    )
                ])

                isMusic = 'no'
                if params['section'] == 'audio':
                    isMusic = 'yes'

                uri = strutils.construct_request({
                    'href': href,
                    'referer': categoryUrl,
                    'mode': 'read_dir',
                    'cover': cover,
                    'folder': 0,
                    'isMusic': isMusic
                })

                xbmcplugin.addDirectoryItem(h, uri, li, True)

    li = xbmcgui.ListItem('[NEXT PAGE >]')
    li.setProperty('IsPlayable', 'false')
    uri = strutils.construct_request({
        'href': category_href,
        'mode': 'readcategory',
        'section': params['section'],
        'filter': params['filter'],
        'start': start + 1,
        'firstPage': 'no'
    })
    xbmcplugin.addDirectoryItem(h, uri, li, True)

    xbmcplugin.endOfDirectory(h)


def load_first_page_sections(href, params):
    #Add search list item
    li = xbmcgui.ListItem("[ПОИСК]")
    li.setProperty('IsPlayable', 'false')
    uri = strutils.construct_request({
        'mode': 'runsearch',
        'section': params['section'],
        'url': urllib.unquote_plus(params['cleanUrl'])
    })
    xbmcplugin.addDirectoryItem(h, uri, li, True)

    first_page_data = client.GET(href, httpSiteUrl)
    if first_page_data is None:
        return False

    beautifulSoup = BeautifulSoup(first_page_data)
    if beautifulSoup is None:
        return False

    groups = beautifulSoup.find('div', 'b-section-menu')
    if groups is not None:
        yearLink = groups.find('a', href=re.compile(r'year'))
        if yearLink is not None:
            li = xbmcgui.ListItem("[По годам]")
            li.setProperty('IsPlayable', 'false')
            uri = strutils.construct_request({
                'mode': 'getGenreList',
                'section': params['section'],
                'filter': params['filter'],
                'href': yearLink['href'],
                'cleanUrl': urllib.unquote_plus(params['cleanUrl']),
                'css': 'main'
            })
            xbmcplugin.addDirectoryItem(h, uri, li, True)
        genreLink = groups.find('a', href=re.compile(r'genre'))
        if genreLink is not None:
            li = xbmcgui.ListItem("[Жанры]")
            li.setProperty('IsPlayable', 'false')
            uri = strutils.construct_request({
                'mode': 'getGenreList',
                'section': params['section'],
                'filter': params['filter'],
                'href': genreLink['href'],
                'cleanUrl': urllib.unquote_plus(params['cleanUrl']),
                'css': 'b-list-subcategories'
            })
            xbmcplugin.addDirectoryItem(h, uri, li, True)


def getGenreList(params):
    http = client.GET(urllib.unquote_plus(params['href']), httpSiteUrl)
    if http is None:
        return False

    beautifulSoup = BeautifulSoup(http)
    items = beautifulSoup.find('div', params['css']).findAll('a')

    if len(items) == 0:
        show_message('ОШИБКА', 'Неверная страница', 3000)
        return False
    else:
        for item in items:
            li = xbmcgui.ListItem(item.string)
            li.setProperty('IsPlayable', 'false')
            uri = strutils.construct_request({
                'href': client.get_full_url(item['href'].encode('utf-8')),
                'mode': 'readcategory',
                'section': params['section'],
                'filter': '',
                'cleanUrl': urllib.unquote_plus(params['cleanUrl']),
                'start': 0,
                'hideFirstPageData': 1
            })
            xbmcplugin.addDirectoryItem(h, uri, li, True)
        xbmcplugin.endOfDirectory(h)


def read_dir(params):
    folderUrl = urllib.unquote_plus(params['href'])
    cover = urllib.unquote_plus(params['cover'])
    folder = params['folder']

    getUrl = folderUrl + '?ajax&folder=' + folder

    http = client.GET(getUrl, httpSiteUrl)
    if http is None:
        return False

    beautifulSoup = BeautifulSoup(http)
    if params['folder'] == '0':
        has_blocked = beautifulSoup.find('div', attrs={'id': 'file-block-text'})
        if has_blocked is not None:
            show_message('Blocked content', 'Некоторые файлы заблокированы')

    mainItems = beautifulSoup.find('ul', 'filelist')

    if mainItems is None:
        show_message('ОШИБКА', 'No filelist', 3000)
        return False

    if 'quality' in params and params['quality'] is not None and params['quality'] != 'None' and params['quality'] != '':
        items = mainItems.findAll('li', 'video-' + params['quality'])
    else:
        items = mainItems.findAll('li')

    materialQualityRegexp = re.compile('quality_list:\s*[\'|"]([a-zA-Z0-9,]+)[\'|"]')
    if len(items) == 0:
        show_message('ОШИБКА', 'Неверная страница', 3000)
        return False
    else:
        for item in items:
            isFolder = 'folder' in item['class']
            playLink = None
            if isFolder:
                linkItem = item.find('a', 'title')
                playLinkClass = ''
            else:
                playLinkClass = 'b-file-new__link-material'
                linkItem = item.find('a', 'b-file-new__link-material-download')
                playLink = item.find('a', playLinkClass)
                if playLink is None:
                    playLinkClass = 'b-file-new__material'
                    playLink = item.find('div', playLinkClass)

            if linkItem is not None:
                materialData = linkItem['rel']
                if materialData is not None:
                    qualities = materialQualityRegexp.findall(linkItem['rel'])
                    itemsCount = item.find('span', 'material-series-count')
                    if qualities is not None and len(qualities) > 0:
                        qualities = str(qualities[0]).split(',')
                        for quality in qualities:
                            add_directory_item(linkItem, isFolder, playLink, playLinkClass, cover, folderUrl, folder, params['isMusic'], quality, itemsCount)
                    else:
                        add_directory_item(linkItem, isFolder, playLink, playLinkClass, cover, folderUrl, folder, params['isMusic'], None, itemsCount)
                else:
                    add_directory_item(linkItem, isFolder, playLink, playLinkClass, cover, folderUrl, folder, params['isMusic'], None, None)

    xbmcplugin.endOfDirectory(h)


def add_directory_item(linkItem, isFolder, playLink, playLinkClass, cover, folderUrl, folder, isMusic, quality = None, itemsCount = None):
    folderRegexp = re.compile('(\d+)')
    lang = None
    langRegexp = re.compile('\s*m\-(\w+)\s*')
    lang_data = langRegexp.findall(linkItem['class'])
    if len(lang_data) > 0:
        lang = str(lang_data[0])
    title = ""
    if isFolder:
        title = strutils.fix_string(linkItem.text)

        if (itemsCount):
                title = "%s (%s)" % (title, strutils.fix_string(itemsCount.text))

        lang_quality_el = linkItem.find('font')
        if lang_quality_el:
            lang_quality = strutils.fix_string(lang_quality_el.text)
            title = title.replace(lang_quality, ' ' + lang_quality)

        if quality is not None:
            title = "%s [%s]" % (title, quality)
    else:
        try:
            title = str(playLink.find('span', playLinkClass + '-filename-text').string)
        except:
            pass
    if lang is not None:
        title = lang.upper() + ' - ' + title

    if playLink is not None and playLink.name == 'a':
        if 'href' in playLink:
            playLink = client.get_full_url(str(playLink['href']))
        elif 'rel' in playLink:
            playLink = client.get_full_url(str(playLink['rel']))
        else:
            playLink = ''
    else:
        playLink = ''

    href = linkItem['href']
    try:
        folder = folderRegexp.findall(linkItem['rel'])[0]
    except:
        pass

    if isFolder:
        li = xbmcgui.ListItem(
            strutils.html_entities_decode(title),
            iconImage=fs_ua.thumbnail(cover),
            thumbnailImage=fs_ua.poster(cover)
        )
        li.setProperty('IsPlayable', 'false')

        uri = strutils.construct_request({
            'cover': cover,
            'href': folderUrl,
            'referer': folderUrl,
            'mode': 'read_dir',
            'folder': folder,
            'isMusic': isMusic,
            'quality': quality
        })
        xbmcplugin.addDirectoryItem(h, uri, li, isFolder)
    else:
        item_type = 'video'
        if isMusic == 'yes':
            item_type = 'music'

        add_folder_file({
            'title': title,
            'cover': cover,
            'href': href,
            'referer': folderUrl,
            'type': item_type,
            'playLink': playLink
        })


def add_folder_file(item):
    title = item['title']
    cover = item['cover']
    href = item['href']
    referer = item['referer']
    item_type = item['type']

    li = xbmcgui.ListItem(
        strutils.html_entities_decode(title),
        iconImage=fs_ua.thumbnail(cover),
        thumbnailImage=fs_ua.poster(cover),
        path=href
    )
    li.setProperty('IsPlayable', 'true')

    li.setInfo(type=item_type, infoLabels={'title': title})
    playCount = kodi.get_play_count(strutils.html_entities_decode(title))
    if playCount:
        li.setInfo(type=item_type, infoLabels={'title': title, 'playcount': 1})
        li.addContextMenuItems([
            (
            __language__(40001), "XBMC.RunPlugin(%s)" % strutils.construct_request({
                'mode': 'download',
                'file_url': str(href.encode('utf-8')),
                'file_name': strutils.html_entities_decode(title)
            })
            )
        ])

    if item_type == 'music' or (__settings__.getSetting('Autoplay next') == 'true'):
        uri = strutils.construct_request({
            'file': str(href.encode('utf-8')),
            'referer': referer,
            'mode': 'play',
            'playLink': item['playLink']
        })
    else:
        uri = client.get_full_url(href)

    xbmcplugin.addDirectoryItem(h, uri, li, False)


def download(params):
    fileUrl = client.get_full_url(urllib.unquote_plus(params['file_url']))
    fileName = fileUrl.split('/')[-1]
    download_params = {
        'url': fileUrl,
        'download_path': __settings__.getSetting('Download Path')
    }
    client = downloader.SimpleDownloader()
    client.download(fileName, download_params)


def runsearch(params):
    skbd = xbmc.Keyboard()
    skbd.setHeading('Что ищем?')
    skbd.doModal()
    if skbd.isConfirmed():
        SearchStr = skbd.getText()
        searchUrl = '%ssearch.aspx?search=%s' % (urllib.unquote_plus(params['url']), urllib.quote_plus(SearchStr))
        params = {
            'href': searchUrl,
            'section': params['section']
        }
        return render_search_results(params)


def render_search_results(params):
    searchUrl = urllib.unquote_plus(params['href'])
    http = client.GET(searchUrl, httpSiteUrl)
    if http is None:
        return False

    beautifulSoup = BeautifulSoup(http)
    results = beautifulSoup.find('div', 'b-search-page__results')

    if results is None:
        show_message('ОШИБКА', 'Ничего не найдено', 3000)
        return False
    else:
        items = results.findAll('a','b-search-page__results-item')
        if len(items) == 0:
            show_message('ОШИБКА', 'Ничего не найдено', 3000)
            return False

        for item in items:
            title = str(item.find('span', 'b-search-page__results-item-title').text.encode('utf-8'))
            href = client.get_full_url(item['href'])
            cover = item.find('span', 'b-search-page__results-item-image').find('img')['src']
            section = item.find('span', 'b-search-page__results-item-subsection').text

            if title is not None:
                li = xbmcgui.ListItem('[%s] %s' % (strutils.html_entities_decode(section), strutils.html_entities_decode(title)), iconImage=fs_ua.thumbnail(cover),
                                      thumbnailImage=fs_ua.poster(cover))
                li.setProperty('IsPlayable', 'false')
                id = item['href'].split('/')[-1]
                li.addContextMenuItems([
                    (
                    __language__(50001), "XBMC.RunPlugin(%s)" % strutils.construct_request({
                            'mode': 'addto',
                            'section': 'favorites',
                            'id': id
                        })
                    ),
                    (
                    __language__(50002), "XBMC.RunPlugin(%s)" % strutils.construct_request({
                            'mode': 'addto',
                            'section': 'playlist',
                            'id': id
                        })
                    )
                ])

                isMusic = 'no'
                if params['section'] == 'audio':
                    isMusic = 'yes'

                uri = strutils.construct_request({
                    'href': href,
                    'referer': searchUrl,
                    'mode': 'read_dir',
                    'cover': cover,
                    'folder': 0,
                    'isMusic': isMusic
                })

                xbmcplugin.addDirectoryItem(h, uri, li, True)

    xbmcplugin.endOfDirectory(h)


def addto(params):
    idRegexp = re.compile("([^-]+)")
    itemId = idRegexp.findall(params['id'])[0]
    addToHref = httpSiteUrl + "/addto/" + params['section'] + '/' + itemId + "?json"
    client.GET(addToHref, httpSiteUrl)
    show_message('Result', "Toggled state in " + params['section'], 5000)


def play(params):
    plfile = urllib.unquote_plus(params['file'])

    plfile = urllib.urlopen(client.get_full_url(plfile))
    fileUrl = plfile.geturl()

    i = xbmcgui.ListItem(path=client.get_full_url(fileUrl))
    xbmcplugin.setResolvedUrl(h, True, i)


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
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]
    return param


execution_params = get_params(sys.argv[2])

mode = None
func = None

try:
    mode = urllib.unquote_plus(execution_params['mode'])
except:
    main(execution_params)

if mode is not None:
    try:
        func = globals()[mode]
    except:
        pass
    if func:
        func(execution_params)
