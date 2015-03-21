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
import urllib
import re
import sys
import tempfile
import os
import Localization
import time

class RuTrackerOrg(SearcherABC.SearcherABC):
    
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
    searchIcon = '/resources/searchers/icons/rutracker.org.png'

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
        cookie=None
        try:do_login=int(time.time())-int(sys.modules[ "__main__" ].__settings__.getSetting("rutracker-auth-time"))
        except: do_login=10001
        if do_login>1000: cookie = self.login()
        if cookie: sys.modules[ "__main__" ].__settings__.setSetting("rutracker-auth", cookie)
        filesList = []
        if not sys.modules[ "__main__" ].__settings__.getSetting("rutracker-auth"):
            cookie = self.login()
            if cookie:
                sys.modules[ "__main__" ].__settings__.setSetting("rutracker-auth", cookie)
            else:
                print 'Auth attempt was failed'
                return filesList
        response = self.makeRequest(
            'http://rutracker.org/forum/tracker.php?nm=' + urllib.quote_plus(keyword),
            headers=[('Cookie', sys.modules[ "__main__" ].__settings__.getSetting("rutracker-auth"))]
        )
        if re.search('ses_short', response):
            cookie = self.login()
            if cookie:
                sys.modules[ "__main__" ].__settings__.setSetting("rutracker-auth", cookie)
            else:
                print 'Auth attempt was failed'
                return filesList
            response = self.makeRequest(
                'http://rutracker.org/forum/tracker.php?nm=' + urllib.quote_plus(keyword), 
                headers=[('Cookie', sys.modules[ "__main__" ].__settings__.getSetting("rutracker-auth"))]
            )
        if None != response and 0 < len(response):
            response = response.decode('cp1251').encode('utf8')
            #print response
            forums = [7, 187, 2090, 2221, 2091, 2092, 2093, 934, 505, 212, 2459, 1235, 185, 22, 941, 1666, 124, 1543, 376, 709, 1577, 511, 656, 93, 905, 1576, 101, 100, 103, 572, 1670, 2198, 2199, 313, 2201, 312, 2339, 314, 352, 549, 1213, 2109, 514, 2097, 4, 930, 2365, 1900, 521, 2258, 208, 539, 209, 484, 822, 921, 922, 1247, 923, 924, 1991, 925, 1165, 1245, 928, 926, 1246, 1250, 927, 1248, 33, 281, 1386, 1387, 1388, 282, 599, 1105, 1389, 404, 1390, 1642, 1391, 893, 1478, 670, 2107, 294, 1453, 1475, 46, 2178, 671, 2177, 251, 97, 851, 821, 2076, 98, 56, 1469, 2123, 1280, 876, 752, 1114, 2380, 1467, 672, 249, 552, 500, 2112, 1327, 1468, 24, 1959, 115, 939, 1481, 113, 882, 1482, 393, 1569, 373, 1186, 137, 1321, 532, 979, 827, 1484, 1485, 114, 1332, 1495, 255, 256, 1986, 1551, 626, 262, 1326, 978, 1287, 1188, 1667, 1675, 257, 845, 875, 263, 2073, 550, 2124, 1470, 528, 486, 854, 2079, 260, 2111, 1608, 1952, 1613, 1614, 1623, 1615, 1630, 2514, 1616, 2014, 1617, 1987, 2171, 1620, 1621, 1998, 751, 1697, 2004, 2001, 2002, 283, 1997, 2003, 2009, 2010, 2006, 2007, 2005, 259, 2008, 126, 9, 104, 1535, 91, 1356, 856, 188, 1408, 310, 202, 935, 990, 80, 119, 1530, 175, 79, 172, 812, 207, 805, 123, 189, 271, 273, 743, 184, 842, 194, 1605, 85, 1144, 595, 1288, 1171, 1694, 1690, 820, 819, 625, 84, 242, 623, 1417, 1798, 106, 166, 236, 507, 504, 536, 173, 918, 920, 203, 1243, 1120, 140, 636, 606, 776, 235, 1499, 81, 266, 252, 1102, 1449, 196, 372, 110, 193, 1531, 237, 265, 181, 1214, 497, 121, 721, 1117, 1359, 387, 134, 195, 2366, 2390, 2391, 2392, 2407, 2393, 2370, 2394, 2408, 2395, 2396, 2397, 2398, 2399, 2400, 2401, 2402, 2403, 2404, 2405, 2406, 911, 1691, 704, 1493, 1500, 1574, 1940, 1539, 1939, 823, 1006, 972, 1299, 781, 717, 1300, 1803, 1298, 825, 1606, 1458, 1463, 1459, 1938, 1461, 718, 1498, 907, 877, 992, 607, 594, 775, 534, 1462, 904, 1460, 816, 815, 325, 1457, 1301, 1692, 1540, 694, 1949, 1678, 1541, 860, 1941, 1537, 2100, 2102, 2103, 1242, 2104, 610, 1542, 2335, 1544, 1545, 1546, 1549, 1597, 1552, 1550, 1568, 1553, 1554, 617, 1555, 2017, 1257, 1258, 2208, 677, 1255, 1479, 1261, 614, 1259, 2065, 1254, 1260, 2209, 2210, 1547, 1548, 2211, 615, 1581, 1590, 1587, 1594, 1591, 1588, 1596, 1585, 1586, 2078, 1929, 1593, 1592, 1595, 1556, 1560, 1561, 1653, 1570, 1654, 1655, 1656, 1930, 1931, 1932, 1562, 1563, 1626, 1564, 1565, 1559, 1566, 1573, 1567]
            for (forum, link, title, seeds) in re.compile('<a class="gen f" href="tracker\.php\?f=(\d+)">.+? class=".+?" href="\./viewtopic\.php\?t=(\d+)">(.+?)</a>.+?<td class=".+?"><b>(\d+)', re.DOTALL).findall(response):
                if int(forum) in forums:
                    torrentTitle = "%s [%s: %s]" % (title, Localization.localize('Seeds'), seeds)
                    image = sys.modules[ "__main__"].__root__ + self.searchIcon
                    link = 'http://dl.rutracker.org/forum/dl.php?t=' + link
                    #print forum, int(seeds), self.unescape(self.stripHtml(torrentTitle)), link, image
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
        try:do_login=int(time.time())-int(sys.modules[ "__main__" ].__settings__.getSetting("rutracker-auth-time"))
        except: do_login=10001
        if do_login>1000: cookie = self.login()
        if cookie: sys.modules[ "__main__" ].__settings__.setSetting("rutracker-auth", cookie)

        referer = 'http://rutracker.org/forum/viewtopic.php?t=' + re.search('(\d+)$', url).group(1)
        cookie = sys.modules[ "__main__" ].__settings__.getSetting("rutracker-auth") + '; bb_dl=' + re.search('(\d+)$', url).group(1)
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
        sys.modules[ "__main__" ].__settings__.setSetting("rutracker-auth-time", str(int(time.time())))
        pageContent = self.makeRequest('http://login.rutracker.org/forum/login.php')
        captchaMatch = re.compile('(http://static\.rutracker\.org/captcha/\d+/\d+/[0-9a-f]+\.jpg\?\d+).+?name="cap_sid" value="(.+?)".+?name="(cap_code_[0-9a-f]+)"', re.DOTALL|re.MULTILINE).search(pageContent)
        data = {
            'login_password': 'torrenter',
            'login_username': 'torrenter-plugin',
            'login': '%C2%F5%EE%E4',
            'redirect': 'index.php'
        }
        if captchaMatch:
            captchaCode = self.askCaptcha(captchaMatch.group(1))
            if captchaCode:
                data['cap_sid'] = captchaMatch.group(2)
                data[captchaMatch.group(3)] = captchaCode
            else:
                return False
        self.makeRequest(
             'http://login.rutracker.org/forum/login.php',
             data
        )
        for cookie in self.cookieJar:
            if cookie.name == 'bb_data':
                return 'bb_data=' + cookie.value
        return False
