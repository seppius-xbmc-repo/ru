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

import urllib



__author__ = 'vova'

import xbmcgui, xbmc, xbmcplugin, xbmcaddon, datetime, os

from xbmcvkui import XBMCVkUI_VKSearch_Base,SEARCH, PrepareString
import datetime

__settings__ = xbmcaddon.Addon(id='xbmc-vk.svoka.com')
__language__ = __settings__.getLocalizedString
saved_search_file = os.path.join(xbmc.translatePath('special://temp/').decode('utf-8'), u'vk-search.sess')

#modes
ALBUM,MY_MUSIC,HYPED_ARTISTS,RECOMENDED_MUSIC,POPULAR_MUSIC = "ALBUM,MY_MUSIC,HYPED_ARTISTS,RECOMENDED_MUSIC,POPULAR_MUSIC".split(',')

from xml.dom import minidom

class XVKAudio(XBMCVkUI_VKSearch_Base):
    def __init__(self, *params):
        self.histId = "Audio"
        self.apiName = "audio.search"
        self.locale = {"newSearch":__language__(30008), "history": __language__(30007), "input":__language__(30003)}
        XBMCVkUI_VKSearch_Base.__init__(self, *params)

    def Do_HOME(self):
        XBMCVkUI_VKSearch_Base.Do_HOME(self)
        listItem = xbmcgui.ListItem(__language__(30009))
        xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=MY_MUSIC) , listItem, True)
        listItem = xbmcgui.ListItem(__language__(30016))
        xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=HYPED_ARTISTS) , listItem, True)
        listItem = xbmcgui.ListItem(__language__(30023))
        xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=RECOMENDED_MUSIC) , listItem, True)
        listItem = xbmcgui.ListItem(__language__(30024))
        xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=POPULAR_MUSIC) , listItem, True)
        self.friendsEntry("music")
        listItem = xbmcgui.ListItem(__language__(30020))
        xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode="LOGOUT"), listItem, True)

    def processFriendEntry(self, uid):
        for a in self.api.call("audio.get", uid=uid):
            self.AddAudioEntry(a)


    def Do_HYPED_ARTISTS(self):
        srl = minidom.parse(urllib.urlopen("http://ws.audioscrobbler.com/2.0/?method=chart.gethypedartists&api_key=42db3eb160b603b55f8886e8c4e9a8f4"))
        artists = srl.getElementsByTagName("artist")
        for a in artists:
            thumb =""
            thumbNode =  a.getElementsByTagName("image")[2].childNodes
            if thumbNode:
                thumb = thumbNode[0].nodeValue
            name  =  a.getElementsByTagName("name") [0].childNodes[0].nodeValue
            name = name.encode('utf-8')
            listItem = xbmcgui.ListItem(name, "", thumb, thumb)
            xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=SEARCH, query=name, thumb=thumb) , listItem, True)


    def transformResult(self,res):
        if res and res[0]:
            return res[1:]
        else:
            return []

    def ProcessFoundEntry(self, a):
        self.AddAudioEntry(a)

            
    def Do_MY_MUSIC(self):
        for a in self.api.call("audio.get"):
            self.AddAudioEntry(a)

    def Do_RECOMENDED_MUSIC(self):
        for a in self.api.call("audio.getRecommendations", count=500):
            self.AddAudioEntry(a)

    def Do_POPULAR_MUSIC(self):
        for a in self.api.call("audio.getPopular", count=500):
            self.AddAudioEntry(a)

    def AddAudioEntry(self, a):
        title = a.get("artist")
        if title:
            title += u" : "
        title += a.get("title")
        d = unicode(datetime.timedelta(seconds=int(a["duration"])))
        listTitle = d + u" - " + title
        listitem = xbmcgui.ListItem(PrepareString(listTitle))
        print "\n\n\n\n\n\n\n\n"+str(a)+"\n\n\n\n\n"
        listitem.setInfo(type='Music', infoLabels={'url': a["url"],
                                                   'title': a.get("title") or "",
                                                   'artist': a.get("artist") or "",
                                                   'album': a.get("artist") or "",
                                                   'duration': a.get('duration') or 0})
        listitem.setProperty('mimetype', 'audio/mpeg')

        xbmcplugin.addDirectoryItem(self.handle, a["url"], listitem, False)
