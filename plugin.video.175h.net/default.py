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

import sys
import os
import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmc
import xbmcvfs

__settings__ = xbmcaddon.Addon(id='plugin.video.175h.net')
__addondir__ = xbmc.translatePath(__settings__.getAddonInfo('profile'))
if not xbmcvfs.exists(__addondir__):
    xbmcvfs.mkdir(__addondir__)

# sys.path.append(os.path.join(__settings__.getAddonInfo('path'), 'resources', 'lib'))
icon = xbmc.translatePath(os.path.join(__settings__.getAddonInfo('path'), 'icon.png'))

import urllib
import urllib2
import re
import cookielib
import socket
import simplejson as json

import SimpleDownloader as downloader
from BeautifulSoup import BeautifulStoneSoup

socket.setdefaulttimeout(50)

__author__ = "Dmitry Khrysev"
__license__ = "GPL"
__maintainer__ = "Dmitry Khrysev"
__email__ = "x86demon@gmail.com"
__status__ = "Production"

__language__ = __settings__.getLocalizedString

siteUrl = '175h.net'
httpSiteUrl = 'http://' + siteUrl
cookiepath = os.path.join(__addondir__, 'plugin.video.175h.net.cookies.lwp')
if isinstance(cookiepath, unicode):
    cookiepath = cookiepath.encode('utf8')

h = int(sys.argv[1])

def construct_request(params):
    return '%s?%s' % (sys.argv[0], urllib.urlencode(params))


def htmlEntitiesDecode(string):
    return BeautifulStoneSoup(string, convertEntities=BeautifulStoneSoup.HTML_ENTITIES).contents[0]


def show_message(heading, message, times=3000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, icon))


headers = {
'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:25.0) Gecko/20100101 Firefox/25.0',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
'Accept-Charset': 'utf-8, utf-16, *;q=0.1',
'Accept-Encoding': 'identity, *;q=0'
}


def get_full_url(url):
    if not '://' in url:
        url = httpSiteUrl + url
    return url


def GET(url, referer, post_params=None):
    headers['Referer'] = referer
    url = get_full_url(url)

    if post_params is not None:
        post_params = urllib.urlencode(post_params)
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
    elif headers.has_key('Content-Type'):
        del headers['Content-Type']

    jar = cookielib.LWPCookieJar(cookiepath)
    if xbmcvfs.exists(cookiepath):
        jar.load()

    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))
    urllib2.install_opener(opener)
    req = urllib2.Request(url, post_params, headers)

    response = opener.open(req)
    the_page = response.read()
    response.close()

    jar.save()

    return the_page

def main(params):
    ids = GET(httpSiteUrl + '/id.js', httpSiteUrl)
    array_regexp = re.compile('\[([^\]]+)')
    data_regexp = re.compile('\{([^\}]+)')
    ids = array_regexp.findall(ids)[0].split(',')
    for material_id in ids:
        material_id = material_id.strip().strip("'")
        material_data = GET(httpSiteUrl + '/' + material_id + '/a.js', httpSiteUrl)
        material_data = '{' + data_regexp.findall(material_data)[0] + '}'
        material_data = fix_broken_json(material_data)
        data = json.loads(material_data)

        href = get_file_path(data)
        li = xbmcgui.ListItem(
            fix_string(data['title']),
            thumbnailImage=get_image(data),
            path=href
        )
        li.addStreamInfo('video', {'duration': data['time']*60})
        li.setInfo('video', {
            'genre': fix_string(data['genre']),
            'year': data['year'],
            'cast': fix_string(data['cast']).split(','),
            'director': fix_string(data['director']),
            'writer': fix_string(data['writer']),
            'title': fix_string(data['title']),
            'originaltitle': fix_string(data['title_original']),
            'plot': fix_string(data['storyline'])
        })
        li.setProperty('IsPlayable', 'true')
        li.addContextMenuItems([
            (
            "Download", "XBMC.RunPlugin(%s)" % construct_request({
                'mode': 'download',
                'file_url': str(href.encode('utf-8')),
                'file_name': '%s.%s.mp4' % (data['title_original'], data['quality'])
            })
            )
        ])
        uri = construct_request({
            'href': href,
            'mode': 'play',
        })
        xbmcplugin.addDirectoryItem(h, uri, li, False)

    xbmcplugin.endOfDirectory(h)


def get_file_path(data):
    return '%s/%s/%s.mp4' % (httpSiteUrl, data['id'], data['quality'])


def get_image(data):
    return '%s/%s/p.jpg' % (httpSiteUrl, data['id'])


def fix_string(string):
    if isinstance(string, unicode):
        return string.encode('utf8')
    return string


def fix_broken_json(data):
    data = data.replace('"', '')
    data = data.replace('\\', '')
    data = re.sub(r'(\w+):', r'"\1":', data)
    data = re.sub(r':\s*\'', ': "', data)
    data = re.sub(r'\s+', ' ', data)
    data = data.replace('\',', '",')

    return data


def play(params):
    fileUrl = urllib.unquote_plus(params['href'])

    i = xbmcgui.ListItem(path=get_full_url(fileUrl))
    xbmcplugin.setResolvedUrl(h, True, i)


def download(params):
    fileUrl = get_full_url(urllib.unquote_plus(params['file_url']))
    fileName = urllib.unquote_plus(params['file_name'])
    if not fileName:
        fileName = fileUrl.split('/')[-1]
    download_params = {
        'url': fileUrl,
        'download_path': __settings__.getSetting('Download Path')
    }
    client = downloader.SimpleDownloader()
    client.download(fileName, download_params)


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


params = get_params(sys.argv[2])

mode = None
func = None

try:
    mode = urllib.unquote_plus(params['mode'])
except:
    main(params)

if mode is not None:
    try:
        func = globals()[mode]
    except:
        pass
    if func:
        func(params)
