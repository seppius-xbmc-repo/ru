#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#   Author(c) 26/12/2012, Dmitry Khrysev, E-mail: x86demon@gmail.com
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

import simplejson as json
import urllib2, urllib, cookielib
import hashlib, os

class TracksFlow:
    API_PREFIX = 'tracksflow.com'
    API_URLS = {
        'top_playlists': '/api/common/topplaylists',
        'my_playlists': '/api/common/playlists',
        'playlist': '/api/common/playlist',
        'search_track': '/api/search/source',
        'search': '/api/search',
        'auth': '/api/common/auth'
    }
    DEVICE_TYPE = 'website'

    def __init__(self, cookiepath, username, password):
        self.cookiepath = cookiepath
        self.username = username
        self.password = password

    def getTopPlaylists(self, pagenum = 0, pagesize = 25, days = 1):
        data = self.GET('top_playlists', {
            'pagesize': pagesize,
            'pagenum': pagenum,
            'days': days
        })
        return json.loads(data)

    def getPlaylists(self):
        data = self.GET('my_playlists')
        return json.loads(data)

    def getPlaylist(self, playlistId):
        data = self.GET(self.API_URLS['playlist'] + '/' + playlistId)
        return json.loads(data)

    def getTrack(self, artist, track):
        data = self.GET('search_track', {
            'artist': artist,
            'title': track
        })
        return json.loads(data)

    def auth(self, username, password):
        passHash = hashlib.md5()
        passHash.update(password)
        data = self.POST('auth', {
            'devicetype': self.DEVICE_TYPE,
            'email': username,
            'login': username,
            'password': passHash.hexdigest()
        })
        return json.loads(data)

    def search(self, term, type, page = 0, pageSize = 25):
        data = self.GET('search', {
            'id': term,
            'query': term,
            'section': type,
            'page': str(page),
            'pageSize': str(pageSize)
        })
        return json.loads(data)

    def GET(self, url, params = None):
        return self._request(url, 'GET', params)

    def POST(self, url, params):
        return self._request(url, 'POST', params)

    def PUT(self, url, params):
        return self._request(url, 'PUT', params)

    def DELETE(self, url):
        return self._request(url, 'DELETE')

    def _request(self, url, method, params = None):
        headers = {
            'Accept': '*/*',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Host': 'tracksflow.com',
            'X-Requested-With': 'XMLHttpRequest',
            'x-insight': 'activate',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:17.0) Gecko/20121213 Firefox/17.0 FirePHP/0.7.1',
            'Pragma': 'no-cache'
        }

        jar = cookielib.LWPCookieJar(self.cookiepath)
        if os.path.isfile(self.cookiepath):
            jar.load()

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))
        urllib2.install_opener(opener)

        try:
            url = self.API_URLS[url]
        except:
            pass

        encodedParams = None
        if params != None:
            encodedParams = urllib.urlencode(params)
        if method == 'GET':
            url = '%s?%s'%(url, encodedParams)
            encodedParams = None
        req = urllib2.Request('http://' + self.API_PREFIX + url, encodedParams, headers)
        req.get_method = lambda: method

        try:
            response = opener.open(req)
            the_page = response.read()
            response.close()

            jar.save()

            return the_page
        except urllib2.HTTPError as e:
            if e.code == 403 and url != 'auth':
                self.auth(self.username, self.password)
                return self._request(url, method, params)
