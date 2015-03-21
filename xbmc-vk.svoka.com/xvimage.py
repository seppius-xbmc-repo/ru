#!/usr/bin/python
# -*- coding: utf-8 -*-
# VK-XBMC add-on
# Copyright (C) 2011 Volodymyr Shcherban
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
__author__ = 'Volodymyr Shcherban'


import xbmcgui, xbmc, xbmcplugin, xbmcaddon, datetime, os

from xbmcvkui import XBMCVkUI_Base,HOME, PrepareString
from datetime import datetime

__settings__ = xbmcaddon.Addon(id='xbmc-vk.svoka.com')
__language__ = __settings__.getLocalizedString
saved_search_file = os.path.join(xbmc.translatePath('special://temp/').decode('utf-8'), u'vk-search.sess')

#modes
ALBUM = "ALBUM"




class XVKImage(XBMCVkUI_Base):

    def Do_HOME(self):
        for title, title2, thumb, id, owner in self.GetAlbums():
            listItem = xbmcgui.ListItem(title, title2, thumb, thumb, ) #search history
            xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=ALBUM, album=id, user=owner) , listItem, True)
        self.friendsEntry("image")
        listItem = xbmcgui.ListItem(__language__(30020))
        xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode="LOGOUT"), listItem, True)


            
    def Do_ALBUM(self):
        album = self.api.call("photos.get", uid = self.params["user"], aid = self.params["album"])
        photos = []
        for cameo in album:
            title = None
            if cameo["text"]:
                title = cameo["text"] + u" (" + unicode(str(datetime.fromtimestamp(int(cameo["created"])))) + u")"
            else:
                title =  unicode(str(datetime.fromtimestamp(int(cameo["created"]))))
            title = PrepareString(title)
            e = ( title,
                  cameo.get("src_xxbig") or cameo.get("src_xbig") or cameo.get("src_big") or cameo["src"],
                  cameo["src"] )
            photos.append(e)
        for title, url, thumb in photos:
            listItem = xbmcgui.ListItem(title, "", thumb, thumb, ) #search history
            xbmcplugin.addDirectoryItem(self.handle, url , listItem, False)

    def processFriendEntry(self, uid):
        for title, title2, thumb, id, owner in self.GetAlbums(uid):
            listItem = xbmcgui.ListItem(title, title2, thumb, thumb, ) #search history
            xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=ALBUM, album=id, user=owner) , listItem, True)

    def GetAlbums(self, uid=None):
        albums=None
        if uid:
            albums=self.api.call("photos.getAlbums", need_covers=1, uid=uid)
        else:
            albums=self.api.call("photos.getAlbums", need_covers=1)
        items = []
        for a in albums:
            print a.get('thumb_src')
            e = ( a["title"] + unicode(" (%s photo)" % a["size"]),
                  a["description"],
                  a.get('thumb_src'),
                  str(a["aid"]),
                  a["owner_id"]  )
            items.append(e)
        return items
