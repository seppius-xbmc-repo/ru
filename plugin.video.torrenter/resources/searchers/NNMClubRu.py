#-*- coding: utf-8 -*-
'''
    Torrenter plugin for XBMC
    Copyright (C) 2012 Vadim Skorba
    vadim.skorba@gmail.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import SearcherABC
import Localization
import urllib
import json, re, os, time, tempfile
import sys

class NNMClubRu(SearcherABC.SearcherABC):
    
    '''
    Weight of source with this searcher provided.
    Will be multiplied on default weight.
    Default weight is seeds number
    '''
    sourceWeight = 1

    '''
    Relative (from root directory of plugin) path to image
    will shown as source image at result listing
    '''
    searchIcon = '/resources/searchers/icons/nnm-club.ru.png'

    '''
    Flag indicates is this source - magnet links source or not.
    Used for filtration of sources in case of old library (setting selected).
    Old libraries won't to convert magnet as torrent file to the storage
    '''
    @property
    def isMagnetLinkSource(self):
        return False

    '''
    Main method should be implemented for search process.
    Receives keyword and have to return dictionary of proper tuples:
    filesList.append((
        int(weight),# Calculated global weight of sources
        int(seeds),# Seeds count
        str(title),# Title will be shown
        str(link),# Link to the torrent/magnet
        str(image),# Path/URL to image shown at the list
    ))
    '''
    def search(self, keyword):
        filesList = []
        url = "http://playble.ru/data/4.php?q=%s&section=video" % (urllib.quote_plus(keyword))
        response = self.makeRequest(url)
        try: jdata=json.loads(response)
        except: return
        if None != response and 0 < len(jdata['results']):
            for data in jdata['results']:
                seeds=int(data['seeds'])
                title=data['title'].encode('utf-8', 'ignore')
                torrentTitle = "%s [%s: %s]" % (title, Localization.localize('Seeds'), seeds)
                image = sys.modules[ "__main__"].__root__ + self.searchIcon
                link='http://nnm-club.ru/forum/download.php?id='+re.search('(\d+)$', data['fast_download']).group(1)+'&'+re.search('(\d+)$', data['download']).group(1)
                filesList.append((
                    int(int(self.sourceWeight) * int(seeds)),
                    int(seeds),
                    self.unescape(self.stripHtml(torrentTitle)),
                    self.__class__.__name__ + '::' + link,
                    image,
                ))
        return filesList

    def getTorrentFile(self, url):
        cookie=None
        try:do_login=int(time.time())-int(sys.modules[ "__main__" ].__settings__.getSetting("nnm-auth-time"))
        except: do_login=10001
        if do_login>1000: cookie = self.login()
        if cookie: sys.modules[ "__main__" ].__settings__.setSetting("nnm-auth", cookie)

        referer = 'http://nnm-club.ru/forum/viewtopic.php?t=' + re.search('(\d+)$', url).group(1)
        #print url
        cookie = sys.modules[ "__main__" ].__settings__.getSetting("nnm-auth") + ';'
        localFileName = tempfile.gettempdir() + os.path.sep + self.md5(url)
        content = self.makeRequest(
            url,
            headers=[('Cookie', cookie), ('Referer', referer)]
        )
        localFile = open(localFileName, 'wb+')
        localFile.write(content)
        localFile.close()
        return 'file:///' + localFileName

    def login(self):
        sys.modules[ "__main__" ].__settings__.setSetting("nnm-auth-time", str(int(time.time())))
        pageContent = self.makeRequest('http://nnm-club.ru/forum/login.php')
        captchaMatch = re.compile('(http://static\.nnm\.org/captcha/\d+/\d+/[0-9a-f]+\.jpg\?\d+).+?name="cap_sid" value="(.+?)".+?name="(cap_code_[0-9a-f]+)"', re.DOTALL).search(pageContent)
        data = {
            'password': 'torrenter',
            'username': 'torrenter-plugin',
            'login': '%C2%F5%EE%E4',
            'redirect': 'index.php',
            'autologin': 'on'
        }
        if captchaMatch:
            captchaCode = self.askCaptcha(captchaMatch.group(1))
            if captchaCode:
                data['cap_sid'] = captchaMatch.group(2)
                data[captchaMatch.group(3)] = captchaCode
            else:
                return False
        self.makeRequest(
            'http://nnm-club.ru/forum/login.php',
            data
        )
        for cookie in self.cookieJar:
            if cookie.name == 'phpbb2mysql_4_sid':
                return 'phpbb2mysql_4_sid=' + cookie.value
        return False