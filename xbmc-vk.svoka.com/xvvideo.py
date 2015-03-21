#!/usr/bin/python
# -*- coding: utf-8 -*-
# VK-XBMC add-on
# Copyright (C) 2011 Volodymyr Shcherban

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


import xbmcgui, xbmc, xbmcplugin, xbmcaddon, datetime, os, urllib, re, sys
import base64


from xml.dom import minidom

from vkparsers import GetVideoFilesAPI
from xbmcvkui import XBMCVkUI_VKSearch_Base,SEARCH, PrepareString

try:
    import json
except ImportError:
    import simplejson as json


__settings__ = xbmcaddon.Addon(id='xbmc-vk.svoka.com')
__language__ = __settings__.getLocalizedString


SEARCH_RESULT, TOP_DOWNLOADS, SERIES, MY_VIDEOS, SEASONS, SEASON_SERIES = "SEARCH_RESULT,TOP_DOWNLOADS,SERIES,MY_VIDEOS,SEASONS,SEASON_SERIES".split(',')
SEARCH_RESULT_DOWNLOAD = "SEARCH_RESULT_DOWNLOAD"
VIDEO_DOWNLOAD = "VIDEO_DOWNLOAD"
GROUP_VIDEO = "GROUP_VIDEO"
GROUPS = "GROUPS"

# ALBUM_VIDEO = "ALBUM_VIDEO"



class XVKVideo(XBMCVkUI_VKSearch_Base):

    def __init__(self, *params):
        self.offset = 0
        self.per_page = 50
        self.histId = None
        self.apiName = "video.search"
        self.locale = {"newSearch":__language__(30005), "history": __language__(30007), "input":__language__(30003)}
        XBMCVkUI_VKSearch_Base.__init__(self, *params)

    def DoSearchTweaks(self):
        if __settings__.getSetting('hdOnly') == 'true' or "hd" in self.params:
            self.searchTweaks["hd"] = "1"
        else:
            listItem = xbmcgui.ListItem(__language__(30019))
            xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=SEARCH, query=self.searchTweaks["q"], hd = "1") , listItem, True)
        if __settings__.getSetting('sortLen') == 'true':
            self.searchTweaks["sort"] = "1"

    def ProcessFoundEntry(self, a):
        duration = str(datetime.timedelta(seconds=int(a["duration"])))
        title = duration + " - " + PrepareString(a["title"])
        videos = base64.encodestring(json.dumps(a["files"]))
        thumb = a.get("thumb") or a.get("image")
        listItem = xbmcgui.ListItem(title, a["description"], thumb, thumb)
        listItem.setInfo(type = "Video", infoLabels = {
            "title"     : title
            ,"duration" : duration
            ,"tagline"  : a["description"]
            } )
        xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=SEARCH_RESULT, thumb=thumb, v=videos, title=a["title"].encode('utf-8')),
                                    listItem, True)

    def Do_SEARCH_RESULT(self):
        vf = GetVideoFilesAPI(self.params["v"])
        if vf:
            for a in vf:
                n = a[a.rfind("/")+1:]
                if a.startswith("http"):
                    n = __language__(30039) + " " + n
                else:
                    n = "YouTube: " + n
                listitem = xbmcgui.ListItem(n, "", self.params.get("thumb"), self.params.get("thumb"), path=a)
                listitem.setProperty('IsPlayable', 'true')
                listitem.setInfo(type = "video", infoLabels = {'title': self.params.get("title")})                
                xbmcplugin.addDirectoryItem(self.handle, a, listitem)
        if vf and __settings__.getSetting("ShowDownload"):        
            for a in vf:
                if a.startswith("http"):
                    listitem = xbmcgui.ListItem(__language__(30035) + " " + a[a.rfind("/")+1:], "", self.params.get("thumb"), self.params.get("thumb"))
                    xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=VIDEO_DOWNLOAD, thumb=self.params.get("thumb"), v=base64.encodestring(a).strip()), listitem, False)

    def Do_SEARCH_RESULT_DOWNLOAD(self):
        vf = GetVideoFilesAPI(self.params["v"])
        if vf:
            for a in vf:
                listitem = xbmcgui.ListItem(__language__(30035) + " " + a[a.rfind("/")+1:], "", self.params.get("thumb"), self.params.get("thumb"))
                xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=VIDEO_DOWNLOAD, thumb=self.params.get("thumb"), v=base64.encodestring(a).strip()), listitem, True)

    def Do_VIDEO_DOWNLOAD(self):
        downloadCmd = __settings__.getSetting("downloadCmd")
        if not downloadCmd:
            if xbmc.getCondVisibility("system.platform.windows"):
                downloadCmd = "start"
            else:
                downloadCmd = "open"
            __settings__.setSetting("downloadCmd", downloadCmd)

        url = base64.decodestring(self.params["v"])
        os.system(downloadCmd + " " + url)
        

    def Do_HOME(self):
        XBMCVkUI_VKSearch_Base.Do_HOME(self)
        listItem = xbmcgui.ListItem(__language__(30010))
        xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=TOP_DOWNLOADS), listItem, True)
        listItem = xbmcgui.ListItem(__language__(30011))
        xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=SERIES), listItem, True)
        listItem = xbmcgui.ListItem(__language__(30012))
        xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=MY_VIDEOS), listItem, True)
        listItem = xbmcgui.ListItem(__language__(30042))
        xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=GROUPS), listItem, True)

        self.friendsEntry("video")

        listItem = xbmcgui.ListItem(__language__(30020))
        xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode="LOGOUT"), listItem, True)


    def prevPage(self, **params):
        self.offset = int(self.params.get("offset") or 0)
        if self.offset:
            listItem = xbmcgui.ListItem(__language__(30046)%(self.offset/self.per_page))
            xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=self.params["mode"], offset=self.offset-self.per_page, **params), listItem, True)
            listItem = xbmcgui.ListItem(__language__(30021))
            xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode="HOME"), listItem, True)


    def nextPage(self, v, **params):
        if v:
            if int(v[0]) >= self.offset+self.per_page:
                listItem = xbmcgui.ListItem(__language__(30044)%(1+self.offset/self.per_page))
                xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=self.params["mode"], offset=self.offset+self.per_page, **params), listItem, True)


    def Do_GROUP_VIDEO(self):
        gid = self.params["gid"]
        self.prevPage(gid=gid)
        v = self.api.call('video.get', gid=gid, count=self.per_page, offset=self.offset)
        if v:
            for a in v[1:]:
                self.ProcessFoundEntry(a)
        self.nextPage(v,gid=gid)


    def processFriendEntry(self, uid):
        self.prevPage(uid=uid)
        v = self.api.call('video.get', uid=uid, count=self.per_page, offset=self.offset)
        if v:
            for a in v[1:]:
                self.ProcessFoundEntry(a)
        self.nextPage(v,uid=uid)

    def Do_GROUPS(self):
        resp = self.api.call('groups.get',extended=1)
        groups = resp[1:]
        for group in groups:
            listItem = xbmcgui.ListItem(group['name'], "", group['photo_big'])
            xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=GROUP_VIDEO, gid=group['gid'], thumb=group['photo_medium'])  , listItem, True)


    def Do_SERIES(self):
        series = json.load(urllib.urlopen("http://api.myshows.ru/shows/top/all/"))
        for s in series:
            thumb = s.get('image') or ""
            names = (PrepareString(s.get('title') or ""), PrepareString(s.get('ruTitle') or ""))
            if all(names):
                listItem = xbmcgui.ListItem(" / ".join(names), str(s.get('year') or ""), thumb, thumb)
            else:
                listItem = xbmcgui.ListItem(names[0] or names[1], str(s.get('year') or ""), thumb, thumb)
            xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=SEASON_SERIES, id=s['id']), listItem, True)


    def Do_SEASON_SERIES(self):
        show = json.load(urllib.urlopen("http://api.myshows.ru/shows/" + self.params["id"]))
        film = PrepareString(show.get('ruTitle') or "") or PrepareString(show.get('title') or "")
        episodes = show['episodes']
        thumb = show.get('image')
        srt = []
        for eid in episodes:
            e = episodes[eid]
            title = e["title"]
            desc = e["airDate"] or ""
            title = __language__(30014) % (e['seasonNumber'], e['episodeNumber']) + (title and (u": " + title))
            et = e.get('image') or thumb
            listItem = xbmcgui.ListItem(PrepareString(title), desc, et, et)
            q = "%s  %s  %s" % (film, e['seasonNumber'], e['episodeNumber'])
            q = q.encode('utf-8')
            srt.append((int(e['seasonNumber'])*1000 + int(e['episodeNumber']) , self.GetURL(mode=SEARCH, query=q), listItem))
        for el in sorted(srt):
            _, q, i = el
            xbmcplugin.addDirectoryItem(self.handle, q, i, True)

    def Do_MY_VIDEOS(self):
        self.prevPage()
        v = self.api.call("video.get", count=self.per_page, offset=self.offset)
        if v:
            for a in v[1:]:
                self.ProcessFoundEntry(a)
        self.nextPage(v)

    def Do_TOP_DOWNLOADS(self):
        html = urllib.urlopen("http://kinobaza.tv/ratings/top-downloadable").read()
        regex = re.compile(r'<img width="60" src="(.*?)" alt="(.*?)" class="poster-pic" />.*?<span class="english">(.*?)</span>',re.UNICODE|re.DOTALL)
        r = regex.findall(html)
        for thumb, ru, en in r:
            thumb = thumb.replace('60.jpg','207.jpg')
            title = ru.decode("utf-8") + " / " + en.decode('utf-8')
            listItem = xbmcgui.ListItem(PrepareString(title) , en, thumb, thumb)
            q= ru + " " + en.replace("(","").replace(")","")
            xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=SEARCH,query=q), listItem, True)

    def Do_MY_SHOWS_LIST(self):
        pass
