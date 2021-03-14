#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Kodi plugin: play media from 1tv (Russia).

"""

import sys
import urllib
import urlparse
import exceptions

import xbmcgui
import xbmcplugin

from sport import SportDirectoryParser, SportItemsParser
from shows import ShowDirectoryParser, ShowItemsParser
from doc import DocDirectoryParser, DocItemsParser
from news import NewsItemsParser

__author__ = "Dmitry Sandalov"
__copyright__ = "Copyright 2017, Dmitry Sandalov"
__credits__ = []
__license__ = "GNU GPL v2.0"
__version__ = "1.1.0"
__maintainer__ = "Dmitry Sandalov"
__email__ = "dmitry@sandalov.org"
__status__ = "Development"

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

xbmcplugin.setContent(addon_handle, 'movies')


def add_directory_items(dir_items):
    for item in dir_items:
        url_item = build_url({'mode': 'folder', 'foldername': item['name']})
        li_item = xbmcgui.ListItem(item['title'], iconImage='DefaultFolder.png')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url_item,
                                    listitem=li_item, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)


def get_sport_directory():
    all_sport = 'https://www.1tv.ru/sport?all'
    html = urlopen_safe(all_sport)
    parser = SportDirectoryParser()
    parser.feed(html)
    return parser.get_sport_directory()


def get_shows_directory():
    all_shows = 'https://www.1tv.ru/shows?all'
    html = urlopen_safe(all_shows)
    parser = ShowDirectoryParser()
    parser.feed(html)
    return parser.get_shows_directory()


def add_sport_items(folder):
    sport_link = 'https://www.1tv.ru' + folder
    html = urlopen_safe(sport_link).decode("utf8")
    parser = SportItemsParser()
    parser.feed(html)
    sport_items = parser.get_sport_items()

    for sport_item in sport_items:
        url_item = get_url_for_item(sport_item)
        li_item = xbmcgui.ListItem(
            sport_item['title'], iconImage=sport_item['poster'])
        xbmcplugin.addDirectoryItem(
            handle=addon_handle, url=url_item, listitem=li_item)
    xbmcplugin.endOfDirectory(addon_handle)
    return []


def add_show_items(folder):
    show_link = 'https://www.1tv.ru' + folder
    html = urlopen_safe(show_link).decode("utf8")
    parser = ShowItemsParser()
    parser.feed(html)
    show_items = parser.get_show_items()

    for show_item in show_items:
        url_item = get_url_for_item(show_item)
        li_item = xbmcgui.ListItem(
            show_item['title'], iconImage=show_item['poster'])
        xbmcplugin.addDirectoryItem(
            handle=addon_handle, url=url_item, listitem=li_item)
    xbmcplugin.endOfDirectory(addon_handle)
    return []


def get_doc_directory():
    all_doc = 'https://www.1tv.ru/doc'
    html = urlopen_safe(all_doc)
    parser = DocDirectoryParser()
    parser.feed(html)
    return parser.get_doc_directory()


def add_doc_items(folder):
    doc_link = 'https://www.1tv.ru' + folder
    html = urlopen_safe(doc_link).decode("utf8")
    parser = DocItemsParser()
    parser.feed(html)
    doc_items = parser.get_doc_items()

    for doc_item in doc_items:
        url_item = get_url_for_item(doc_item)
        li_item = xbmcgui.ListItem(
            doc_item['title'], iconImage=doc_item['poster'])
        xbmcplugin.addDirectoryItem(
            handle=addon_handle, url=url_item, listitem=li_item)
    xbmcplugin.endOfDirectory(addon_handle)
    return []


def add_news_items():
    news_link = 'https://www.1tv.ru/news/issue'
    html = urlopen_safe(news_link).decode("utf8")
    parser = NewsItemsParser()
    parser.feed(html)
    news_items = parser.get_news_items()

    for news in news_items:
        url_item = get_url_for_item(news)
        li_item = xbmcgui.ListItem(
            news['title'], iconImage=news['poster'])
        xbmcplugin.addDirectoryItem(
            handle=addon_handle, url=url_item, listitem=li_item)
    xbmcplugin.endOfDirectory(addon_handle)
    return []


def get_url_for_item(item):
    res = check_resolution(item)
    url_item = ''
    try:
        url_parts = item['mbr'][res]['src'].rsplit('_', 1)
        url_parts1 = url_parts[1].split('.')
        bitrate = url_parts1[0]
        extension = url_parts1[1]
        url_item = "https:" + url_parts[0] + "_," + bitrate + ",." \
                   + extension + ".urlset/master.m3u8"
    except IndexError:
        print "Cannot find link for current resolution"
    if not url_item:
        url_item = 'https:' + item['mbr'][res]['src']
    return url_item


def build_url(query):
    """Plugin navigation."""
    return base_url + '?' + urllib.urlencode(query)


def urlopen_safe(link):
    """Handle network issues."""
    while True:
        try:
            return urllib.urlopen(link).read()
        except exceptions.IOError:
            retry = err_no_connection()
            if retry:
                continue
            else:
                sys.exit()


def err_no_connection():
    """Display a network error message."""
    dialog = xbmcgui.Dialog()
    return dialog.yesno(heading="No connection",
                        line1="Check your connection and try again",
                        nolabel="Exit", yeslabel="Retry")


def check_resolution(video):
    """
    Select the best resolution with respect to settings.
    (Some video files have only one resolution.)
    :param video: list of formats for selected video
    :return: resolution
    """
    max_res = len(video['mbr'])
    return resolution \
        if max_res >= resolution + 1 \
        else max_res - 1


# Gets resolution from plugin settings
resolutions_dict = {'hd': 0, 'sd': 1, 'ld': 2}
resolution_setting = xbmcplugin.getSetting(addon_handle, 'video_res')
resolution = resolutions_dict[resolution_setting.lower()]

mode = args.get('mode', None)

if mode is None:
    root_items = [
        # {'name': 'live', 'title': 'Прямой эфир (TODO)'},
        {'name': 'shows', 'title': 'Телепроекты'},
        {'name': 'news', 'title': 'Новости'},
        # {'name': 'movies', 'title': 'Фильмы и сериалы (TODO)'},
        {'name': 'doc', 'title': 'Доккино'},
        {'name': 'sport', 'title': 'Спорт'}
    ]
    add_directory_items(root_items)

elif mode[0] == 'folder':
    foldername = args['foldername'][0]

    if foldername == 'shows':
        shows = []
        show_links = get_shows_directory()
        for show in show_links:
            if 'stream' not in show['href']:
                shows.append({'title': show['name'], 'name': show['href']})
        add_directory_items(shows)
    elif '/shows/' in foldername:
        add_show_items(foldername)
    elif foldername == 'sport':
        sports = []
        sport_links = get_sport_directory()
        for sport in sport_links:
            if 'stream' not in sport['href']:
                sports.append({'title': sport['name'], 'name': sport['href']})
        add_directory_items(sports)
    elif '/sport/' in foldername:
        add_sport_items(foldername)
    elif foldername == 'doc':
        docs = []
        doc_links = get_doc_directory()
        for doc in doc_links:
            docs.append({'title': doc['name'], 'name': doc['href']})
        add_directory_items(docs)
    elif '/doc/' in foldername:
        add_doc_items(foldername)
    elif foldername == 'news':
        add_news_items()
    else:
        url = 'http://localhost/not_supported_yet.mkv'
        li = xbmcgui.ListItem(
            foldername + ' (not supported)', iconImage='DefaultVideo.png')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
        xbmcplugin.endOfDirectory(addon_handle)
