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
import Localization

class KrasfsRu(SearcherABC.SearcherABC):
    
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
    searchIcon = '/resources/searchers/icons/krasfs.ru.png'

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
        response = self.makeRequest(
            'http://www.krasfs.ru/',
            {'query': keyword, 'checkbox_tor': 'on', 'submit': ''},
        )
        if None != response and 0 < len(response):
            seeds = 1
            for (link, title) in re.compile('<a target=_blank href=(/index\.php\?hash=[0-9a-f]+)>\s(.+?)</a> </td> <td align=center>', re.DOTALL).findall(response):
                torrentTitle = "%s [%s: %s]" % (title, Localization.localize('Seeds'), '?')
                image = sys.modules[ "__main__"].__root__ + self.searchIcon
                link = 'http://www.krasfs.ru' + link
                filesList.append((
                    int(int(self.sourceWeight) * int(seeds)),
                    int(seeds),
                    self.unescape(self.stripHtml(torrentTitle)),
                    self.__class__.__name__ + '::' + link,
                    image,
                ))
        return filesList
