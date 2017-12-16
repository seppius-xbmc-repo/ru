#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import urllib


import os

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs

from lib import parser
from lib import utils
from lib.httpclient import HTTPClient

# this might needed for testing in kodi
# import web_pdb
# web_pdb.set_trace()

from lib.models import Movie

debug = True

__settings__ = xbmcaddon.Addon(id='plugin.video.1kinobig.ru')
__addon_dir__ = xbmc.translatePath(__settings__.getAddonInfo('profile'))
icon = xbmc.translatePath(os.path.join(__settings__.getAddonInfo('path'), 'icon.png'))

if not xbmcvfs.exists(__addon_dir__):
    xbmcvfs.mkdir(__addon_dir__)

__language__ = __settings__.getLocalizedString

siteUrl = __settings__.getSetting('Site URL')

# this needed for testing on PC
if debug:
    if __addon_dir__ == '':
        __addon_dir__ = '/home/uabart/.kodi/userdata/addon_data/plugin.video.1kinobig.ru/'
    if siteUrl == '':
        siteUrl = '1kinobig.ru'

httpSiteUrl = 'http://' + siteUrl

client = HTTPClient(site_url=httpSiteUrl, cookie_path=__addon_dir__)


def add_directory(title, dir_url, icon_img="DefaultVideo.png", dir_mode=""):
    sys_url = sys.argv[0] + '?url=' + urllib.quote_plus(dir_url) + '&mode=' + urllib.quote_plus(str(dir_mode))
    title = title.replace('<b>', '[B]')
    title = title.replace('</b>', '[/B]')
    item = xbmcgui.ListItem(title, iconImage=icon_img, thumbnailImage=icon_img)
    item.setInfo(type='Video', infoLabels={'Title': title})
    xbmcplugin.addDirectoryItem(handle=h, url=sys_url, listitem=item, isFolder=True)
    if debug:
        print "===== Add Dir ====="
        if not isinstance(title, str):
            print title.encode('utf-8'), sys_url.encode('utf-8')
        else:
            print title, sys_url.encode('utf-8')


def add_link(title, info_labels, link_url, icon_img="DefaultVideo.png"):
    item = xbmcgui.ListItem(title, iconImage=icon_img, thumbnailImage=icon_img)
    item.setInfo(type='Video', infoLabels=info_labels)
    xbmcplugin.addDirectoryItem(handle=h, url=link_url, listitem=item)
    if debug:
        print "===== Add Link ====="
        if not isinstance(title, str):
            print title.encode('utf-8'), link_url.encode('utf-8')
        else:
            print title, link_url.encode('utf-8')


def show_main_page():
    main_page_html = client.get_html('', httpSiteUrl)
    categories = parser.parse_main_page(main_page_html)
    categories = utils.resort_categories(categories)
    for cat in categories:
        title = cat[1]
        dir_url = cat[0]
        title = utils.fix_1251(title)
        add_directory(title, dir_url, dir_mode='CATEGORY')


def show_category_page(page_url):
    page_html = client.get_html(page_url, httpSiteUrl)
    movies = parser.parse_page_with_movies(page_html)
    for movie in movies:
        if isinstance(movie, Movie):
            title = movie.get_title()
            image_url = movie.img_url
            dir_url = movie.url
            title = utils.fix_1251(title)
            add_directory(title, dir_url, client.get_full_url(image_url), dir_mode='MOVIE')


def show_movie_page(page_url):
    page_html = client.get_html(page_url, httpSiteUrl)
    movie_dict = parser.parse_iframe_from_page(page_html, page_url, client)
    for movie_key in movie_dict.keys():
        add_link(movie_key, None, movie_dict.get(movie_key))


def get_params():
    param = []
    params_string = sys.argv[2]
    if len(params_string) >= 2:
        parameters = params_string
        cleaned_params = parameters.replace('?', '')
        pairs_of_params = cleaned_params.split('&')
        param = {}
        for i in range(len(pairs_of_params)):
            splitparams = pairs_of_params[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]
    return param


h = int(sys.argv[1])
params = get_params()

mode = None

try:
    mode = urllib.unquote_plus(params['mode'])
except:
    pass

try:
    url = urllib.unquote_plus(params['url'])
except:
    pass

if mode is None or mode == 'MAIN':
    show_main_page()
if mode == 'CATEGORY':
    show_category_page(url)
if mode == 'MOVIE':
    show_movie_page(url)


xbmcplugin.endOfDirectory(h)
