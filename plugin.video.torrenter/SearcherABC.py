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

import abc
import urllib
import urllib2
import cookielib
import re
import tempfile
import hashlib
import xbmcgui
import xbmc
import Localization

class SearcherABC:
    __metaclass__ = abc.ABCMeta

    searchIcon = '/icons/video.png'
    sourceWeight = 1
    cookieJar = None

    @abc.abstractmethod
    def search(self, keyword):
        '''
        Retrieve keyword from the input and return a list of tuples:
        filesList.append((
            int(weight),
            int(seeds),
            str(title),
            str(link),
            str(image),
        ))
        '''
        return

    @abc.abstractproperty
    def isMagnetLinkSource(self):
        return 'Should never see this'

    def getTorrentFile(self, url):
        return url

    def makeRequest(self, url, data={}, headers=[]):
        self.cookieJar = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookieJar))
        opener.addheaders = headers
        if 0 < len(data):
            encodedData = urllib.urlencode(data)
        else:
            encodedData = None
        return opener.open(url, encodedData).read()

    def askCaptcha(self, url):
        urllib.URLopener().retrieve(url, tempfile.gettempdir() + '/captcha.png')
        window = xbmcgui.Window(xbmcgui.getCurrentWindowId())
        image = xbmcgui.ControlImage(460, 20, 360, 160, tempfile.gettempdir() + '/captcha.png')
        window.addControl(image)
        keyboardCaptcha = xbmc.Keyboard('', Localization.localize('Input symbols from CAPTCHA image:'))
        keyboardCaptcha.doModal()
        captchaText = keyboardCaptcha.getText()
        window.removeControl(image)
        if not captchaText:
            return False
        else:
            return captchaText

    htmlCodes = (
        ('&', '&amp;'),
        ('<', '&lt;'),
        ('>', '&gt;'),
        ('"', '&quot;'),
        ("'", '&#39;'),
    )
    stripPairs = (
        ('<p>', '\n'),
        ('<li>', '\n'),
        ('<br>', '\n'),
        ('<.+?>', ' '),
        ('</.+?>', ' '),
        ('&nbsp;', ' '),
    )

    def unescape(self, string):
        for (symbol, code) in self.htmlCodes:
            string = re.sub(code, symbol, string)
        return string

    def stripHtml(self, string):
        for (html, replacement) in self.stripPairs:
            string = re.sub(html, replacement, string)
        return string

    def md5(self, string):
        hasher = hashlib.md5()
        hasher.update(string)
        return hasher.hexdigest()
