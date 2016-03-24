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
from xml.sax.saxutils import unescape

__author__ = 'Volodymyr Shcherban'

import xbmcplugin, urllib, sys, os

PLUGIN_NAME = 'VK-xbmc'

HOME = 'HOME'
FRIENDS = "FRIENDS"
FRIEND_ENTRY = "FRIEND_ENTRY"


def PrepareString(str):
    return unescape(str, {"&apos;": "'", "&#039;" : "'", "&#39;" : "'", "&quot;": '"'})


class XBMCVkUI_Base:
    def __init__(self, parameters, handle, api):
        self.api = api
        self.handle = handle
        self.params = parameters
        self.Populate(getattr(self, "Do_" + self.params["mode"], self.Do_HOME))

    def Populate(self, content):
        self.PrefixActions()
        content()
        xbmcplugin.setPluginCategory(self.handle, PLUGIN_NAME)
        xbmcplugin.endOfDirectory(self.handle)

    def PrefixActions(self):
        pass

    def Do_HOME(self):
        pass

    def GetURL(self, __dict_params=dict(), **parameters):
        #UNOCODE things here???
        __dict_params.update(parameters)
        return sys.argv[0] + "?" + urllib.urlencode(__dict_params)

    def friendsEntry(self, type):
        listItem = xbmcgui.ListItem(xbmcaddon.Addon(id='xbmc-vk.svoka.com').getLocalizedString(30043))
        xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=FRIENDS, type=type), listItem, True)

    def Do_FRIENDS(self):
        type = self.params["type"]

        #we have 'music', 'video', 'image'
        call_params={"fields": 'uid,first_name,last_name,photo_big,nickname', "order": 'hints', "v": "5.7"}
        if type == 'music':
            call_params["fields"] += ",can_see_audio"
        resp = self.api.call('friends.get', **call_params)

        friends = resp['items']
        for friend in friends:
            if 'deactivated' in friend:
                continue
            if type == 'music' and not friend.get('can_see_audio'):
                continue
            name = "%s %s" % (friend.get('last_name'), friend.get('first_name'))
            if friend.get('nickname'):
                name += " " + friend.get('nickname')
            listItem = xbmcgui.ListItem(name, "", friend['photo_big'])
            xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=FRIEND_ENTRY, uid=friend['id'], thumb=friend['photo_big']), listItem, True)

    def Do_FRIEND_ENTRY(self):
        uid = self.params["uid"]
        self.processFriendEntry(uid) 

    def processFriendEntry(self, uid):
        pass

    def Do_LOGOUT(self):
        __settings__.setSetting('auth_token', "")
        __settings__.setSetting('username', "")



import xbmc,xbmcaddon, xbmcgui

saved_search_file = os.path.join(xbmc.translatePath('special://temp/').decode('utf-8'), u'vk-search%s.sess')
__settings__ = xbmcaddon.Addon(id='xbmc-vk.svoka.com')
SEARCH, SEARCH_HISTORY = "SEARCH,SEARCH_HISTORY".split(",")



class XBMCVkUI_Search_Base(XBMCVkUI_Base):
    def PrefixActions(self):
        listItem = xbmcgui.ListItem(self.locale["newSearch"]) #new search - always first element
        xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=SEARCH) , listItem, True)

    def Do_HOME(self):
        if self.GetSearchHistory(self.histId):
            listItem = xbmcgui.ListItem(self.locale["history"]) #search history
            xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=SEARCH_HISTORY) , listItem, True)


    def Do_SEARCH(self):
        query = self.params.get("query")
        if not query:
            kb = xbmc.Keyboard()
            kb.setHiddenInput(False)
            kb.setHeading(self.locale["input"])
            history = self.GetSearchHistory(self.histId)
            if history:
                kb.setDefault(history[0])
            kb.doModal()
            if kb.isConfirmed():
                query = kb.getText()
            self.params["query"] = query
        self.Search(query)


    def Do_SEARCH_HISTORY(self):
        history = self.GetSearchHistory(self.histId)
        if history:
            for q in history:
                listItem = xbmcgui.ListItem(PrepareString(q))
                xbmcplugin.addDirectoryItem(self.handle, self.GetURL(mode=SEARCH,query=q), listItem, True)


    def GetSearchHistory(self, searchId = None):
        history = []
        if os.path.isfile(saved_search_file % unicode(searchId)):
            fl = open(saved_search_file % unicode(searchId),"r")
            history = fl.readlines()
            history = map(lambda s: s.strip(), history)
            history = filter(None, history)
            fl.close()
        return history

    def AddSearchHistory(self, query, searchId = None):
        query = query.strip()
        if not query:
            return
        max = int(__settings__.getSetting('history'))
        max = [5, 10, 15, 20, 25, 30, 40, 50, 75, 100][max]
        lines = []
        if os.path.isfile(saved_search_file % unicode(searchId)):
            fl = open(saved_search_file % unicode(searchId),"r")
            lines = fl.readlines()
            fl.close()
        lines = map(lambda s: s.strip(), lines)
        lines = filter(None, lines)
        while query in lines:   #could replace with `if`, nothing should change...
            lines.remove(query)
        lines.insert(0, query)
        fl = open(saved_search_file % unicode(searchId), "w")
        fl.write("\n".join(lines[:max]))
        fl.close()



class XBMCVkUI_VKSearch_Base(XBMCVkUI_Search_Base):
    def __init__(self, *params):
        self.searchTweaks = {"count" : "25"}
        XBMCVkUI_Search_Base.__init__(self, *params)


    def Search(self,query):
        result = None
        if query:
            self.AddSearchHistory(query, self.histId)
            self.searchTweaks["q"]=query
            self.DoSearchTweaks()
            result = self.api.call(self.apiName, **self.searchTweaks)
            result = self.transformResult(result)
        if result:
            for a in result:
                self.ProcessFoundEntry(a)

    def transformResult(self, res):
        return res
    
    def DoSearchTweaks(self):
        pass
