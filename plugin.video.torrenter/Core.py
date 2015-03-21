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

import Downloader
import Localization
import sys
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs
import urllib
import urllib2
import re
import tempfile
import time
import cookielib
import json
import xml.dom.minidom
import os.path

class Core:
    __plugin__ = sys.modules[ "__main__"].__plugin__
    __settings__ = sys.modules[ "__main__" ].__settings__
    ROOT = sys.modules[ "__main__"].__root__.decode('utf-8').encode(sys.getfilesystemencoding())
    userStorageDirectory = __settings__.getSetting("storage")
    USERAGENT = "Mozilla/5.0 (Windows NT 6.1; rv:5.0) Gecko/20100101 Firefox/5.0"
    URL = 'http://torrenter.host.org'
    torrentFilesDirectory = 'torrents'
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
    skinOptimizations = (
        {#Confluence
            'list': 50,
            'info': 50,
            'wide': 51,
            'icons': 500,
        },
        {#Transperency!
            'list': 50,
            'info': 51,
            'wide': 52,
            'icons': 53,
        }
    )
    print 'SYS ARGV: '+str(sys.argv)

    def __init__(self):
        if 0 == len(self.userStorageDirectory):
            self.userStorageDirectory = tempfile.gettempdir() + os.path.sep + 'Torrenter'
        else:
            self.userStorageDirectory = self.userStorageDirectory + 'Torrenter'

    def drawItem(self, title, action, link = '', image='', isFolder = True, contextMenu=None):
        title=title.replace('720p', '[B]720p[/B]')
        listitem = xbmcgui.ListItem(title, iconImage=image, thumbnailImage=image)
        url = '%s?action=%s&url=%s' % (sys.argv[0], action, urllib.quote_plus(link))
        if contextMenu:
            listitem.addContextMenuItems(contextMenu, replaceItems=True)
        if isFolder:
            listitem.setProperty("Folder", "true")
            listitem.setInfo(type = 'Video', infoLabels = {"Title":title, "plot":title})
        else:
            listitem.setInfo(type = 'Video', infoLabels = {"Title":title, "plot":title})
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem, isFolder=isFolder)

    def fetchData(self, url, referer = None):
        request = urllib2.Request(url)
        if referer != None:
            request.add_header('Referer', referer)
        request.add_header('User-Agent', self.USERAGENT)
        if self.__settings__.getSetting("auth"):
            authString = '; ' + self.__settings__.getSetting("auth")
        else:
            authString = ''
        request.add_header('Cookie', authString)
        try:
            connection = urllib2.urlopen(request)
            result = connection.read()
            connection.close()
            return (result)
        except (urllib2.HTTPError, urllib2.URLError) as e:
            print self.__plugin__ + " fetchData(" + url + ") exception: " + str(e)
            return

    def lockView(self, viewId):
        xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
        if 'true' == self.__settings__.getSetting("lock_view"):
            try:
                xbmc.executebuiltin("Container.SetViewMode(%s)" % str(self.skinOptimizations[int(self.__settings__.getSetting("skin_optimization"))][viewId]))
            except:
                return

    def getParameters(self, parameterString):
        commands = {}
        splitCommands = parameterString[parameterString.find('?')+1:].split('&')
        for command in splitCommands:
            if (len(command) > 0):
                splitCommand = command.split('=')
                if (len(splitCommand) > 1):
                    name = splitCommand[0]
                    value = splitCommand[1]
                    commands[name] = value
        return commands

    def unescape(self, string):
        for (symbol, code) in self.htmlCodes:
            string = re.sub(code, symbol, string)
        return string

    def stripHtml(self, string):
        for (html, replacement) in self.stripPairs:
            string = re.sub(html, replacement, string)
        return string

    def executeAction(self, params = {}):
        get = params.get
        if hasattr(self, get("action")):
            getattr(self, get("action"))(params)
        else:
            self.sectionMenu()

    def clearStorage(self, params = {}):
        try:
            xbmcaddon.Addon(id='plugin.video.myshows')
            fuckyou=True
        except: fuckyou=False
        if not fuckyou:
            if xbmcvfs.exists(self.userStorageDirectory):
                import shutil
                shutil.rmtree(self.userStorageDirectory, ignore_errors=True)
            xbmc.executebuiltin("Notification(%s, %s, 2500)" % (Localization.localize('Storage'), Localization.localize('Storage was cleared')))

    # dev state
    def serv(self, path):
        import socket
        import thread
        HOST = '127.0.0.1'
        PORT = 51515
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.settimeout(10)
        s.bind((HOST, PORT))
        s.listen(1)
        while 1:
            conn, addr = s.accept()
            data = conn.recv(1024)
            print 'streaming ' + path
            print data
            thread.start_new_thread(self.strm, (conn, path, ))
        return

    # dev state
    def strm(self, conn, path):
        fp = open(path, "rb")
        conn.send("HTTP/1.1 200 OK\r\nContent-Type: video/mp4\r\n")
        conn.send("\r\n")
        while True:
            chunk = fp.read(1024)
            if chunk:
                try:
                    conn.send(chunk)
                except socket.error, e:
                    conn.close()
                    break
            else:
                break
        conn.close()
        fp.close()

    def calculateIterator(self, current, full):
        if (100 * 1024 * 1024) > full:#<100Mb
            return current * (100 / 25 * 100) / full# 25% of file size = 100% of progress 
        elif (500 * 1024 * 1024) > full:#<500Mb
            return current * (100 / 7 * 100) / full# 7% of file size = 100% of progress 
        elif (2000 * 1024 * 1024) > full:#<2000Mb
            return current * (100 / 3 * 100) / full# 3% of file size = 100% of progress 
        elif (4000 * 1024 * 1024) > full:#<4000Mb
            return current * (100 / 1 * 100) / full# 1% of file size = 100% of progress 
        else:#>4000Mb
            return current * 100 / (50 * 1024 * 1024)# 50Mb file size = 100% of progress 

    def playTorrent(self, params = {}):
        torrentUrl = self.__settings__.getSetting("lastTorrent")
        if 0 != len(torrentUrl):
            get = params.get
            contentId = int(get("url"))
            torrent = Downloader.Torrent(self.userStorageDirectory, torrentUrl, self.torrentFilesDirectory)
            if 'false' == self.__settings__.getSetting("keep_seeding"):
                torrent.startSession(contentId, seeding=False)
            else:
                torrent.startSession(contentId)
            if 0 < int(self.__settings__.getSetting("upload_limit")):
                torrent.setUploadLimit(int(self.__settings__.getSetting("upload_limit")) * 1000000 / 8) #MBits/second
            if 0 < int(self.__settings__.getSetting("download_limit")):
                torrent.setDownloadLimit(int(self.__settings__.getSetting("download_limit")) * 1000000 / 8) #MBits/second
            iterator = 0
            progressBar = xbmcgui.DialogProgress()
            progressBar.create(Localization.localize('Please Wait'), Localization.localize('Seeds searching.'))
            fullSize = torrent.getFileSize(contentId)
            downloadedSize = 0
            while iterator < 100 and downloadedSize < (45 * 1024 * 1024):#45Mb
                time.sleep(1)
                downloadedSize = torrent.torrentHandle.file_progress()[contentId]
                iterator = self.calculateIterator(downloadedSize, fullSize)
                dialogText = Localization.localize('Preloaded: ') + str(downloadedSize / 1024 / 1024) + ' MB / ' + str(fullSize / 1024 / 1024) + ' MB'
                peersText = ' [%s: %s; %s: %s]' % (Localization.localize('Seeds'), str(torrent.getSeeds()), Localization.localize('Peers'), str(torrent.getPeers()))
                speedsText = '%s: %s Mbit/s; %s: %s Mbit/s' % (Localization.localize('Downloading'), str(torrent.getDownloadRate() * 8/ 1000000), Localization.localize('Uploading'), str(torrent.getUploadRate() * 8 / 1000000))
                progressBar.update(iterator, Localization.localize('Seeds searching.') + peersText, dialogText, speedsText)
                if progressBar.iscanceled():
                    progressBar.update(0)
                    progressBar.close()
                    torrent.threadComplete = True
                    return
            progressBar.update(0)
            progressBar.close()

            from Proxier import Proxier
            import thread
            proxier = Proxier()
            thread.start_new_thread(proxier.server, (torrent.getFilePath(contentId), ))
            #xbmc.Player().play('http://127.0.0.1:51515/play.avi')
            #return

            playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
            playlist.clear()
            listitem = xbmcgui.ListItem(torrent.getContentList()[contentId].path)
            playlist.add('http://127.0.0.1:51515/%s.avi' % torrent.md5(torrent.getFilePath(contentId)), listitem)
            xbmc.Player().play(playlist)
            #self.addHistory(torrent.getContentList()[contentId].path)
            bufferingBar = xbmcgui.DialogProgress()
            while 1 == xbmc.Player().isPlayingVideo():
                torrent.fetchParts()
                torrent.checkThread()
                time.sleep(1)
                if proxier.seekBytes > 0:
                    torrent.fetchSeekBytes(proxier.seekBytes)
                    proxier.seekBytes = 0
                if proxier.buffering > 0:
                    bufferingBar.create(Localization.localize('Please Wait'), Localization.localize('Buffering...'))
                    bufferingBar.update(proxier.buffering / 60 * 100)
                    if bufferingBar.iscanceled():
                        bufferingBar.update(0)
                        bufferingBar.close()
                        torrent.threadComplete = True
                        return
                else:
                    try:
                        bufferingBar.update(0)
                        bufferingBar.close()
                    except:
                        pass

            if 'false' == self.__settings__.getSetting("keep_files"):
                torrent.threadComplete = True
                self.clearStorage()
            else:
                dialog = xbmcgui.Dialog()
                if dialog.yesno(
                    Localization.localize('Torrent Downloading'),
                    Localization.localize('Do you want to STOP torrent downloading and seeding?'),
                    Localization.localize('Preloaded: ') + str(downloadedSize / 1024 / 1024) + ' MB / ' + str(fullSize / 1024 / 1024) + ' MB'
                ):
                    xbmc.executebuiltin("Notification(%s, %s)" % (Localization.localize('Information'), Localization.localize('Torrent downloading is stopped.')))
                    torrent.threadComplete = True
            #self.addRate(torrent.getContentList()[contentId].path)
        else:
            print self.__plugin__ + " Unexpected access to method playTorrent() without torrent content"

    def openTorrent(self, params = {}):
        get = params.get
        try: external=urllib.unquote_plus(get("external"))
        except: external=None
        try: silent=get("silent")
        except: silent=None
        url = urllib.unquote_plus(get("url"))
        self.__settings__.setSetting("lastTorrentUrl", url)
        classMatch = re.search('(\w+)::(.+)', url)
        if classMatch:
            searcher = classMatch.group(1)
            if self.ROOT + os.sep + 'resources' + os.sep + 'searchers' not in sys.path:
                sys.path.insert(0, self.ROOT + os.sep + 'resources' + os.sep + 'searchers')
            try:
                searcherObject = getattr(__import__(searcher), searcher)()
            except Exception, e:
                print 'Unable to use searcher: ' + searcher + ' at ' + self.__plugin__ + ' openTorrent(). Exception: ' + str(e)
                return
            url = searcherObject.getTorrentFile(classMatch.group(2))
        self.__settings__.setSetting("lastTorrentUrl", url)
        torrent = Downloader.Torrent(self.userStorageDirectory, torrentFilesDirectory = self.torrentFilesDirectory)
        if not torrent: torrent = Downloader.Torrent(self.userStorageDirectory, torrentFilesDirectory = self.torrentFilesDirectory)
        self.__settings__.setSetting("lastTorrent", torrent.saveTorrent(url))
        if silent!='true':
            contentId = 0
            if external:
                myshows_setting=xbmcaddon.Addon(id='plugin.video.myshows')
                myshows_lang=myshows_setting.getLocalizedString
                myshows_items=[]
                myshows_files=[]
                contentList = []
                for contentId, contentFile in enumerate(torrent.getContentList()):
                    fileTitle = "%s" % (contentFile.path)#In MB
                    contentList.append((self.unescape(fileTitle), str(contentId)))
                contentList = sorted(contentList, key=lambda x: x[0])
                for title, identifier in contentList:
                    #self.drawItem(title, 'playTorrent', identifier, isFolder=False)
                    myshows_items.append(title)
                    myshows_files.append('plugin://plugin.video.torrenter/?action=playTorrent&url='+identifier)
                if len(myshows_items)>1:myshows_items=self.cutFileNames(myshows_items)
                myshows_items.append(unicode(myshows_lang(30400)))
                myshows_files.append('plugin://plugin.video.myshows/?mode=203&stringdata='+get("sdata"))
                dialog = xbmcgui.Dialog()
                if len(myshows_items)==2: ret=0
                else:ret = dialog.select(unicode(myshows_lang(30401)), myshows_items)
                if ret>-1:
                    xbmc.executebuiltin('xbmc.RunPlugin("'+myshows_files[ret]+'")')
            else:
                listitem = xbmcgui.ListItem('<' + Localization.localize('Add To Bookmarks') + ' >')
                itemUrl = '%s?action=%s&url=%s&name=%s&seeds=%s&image=%s' % (sys.argv[0], 'addBookmark', urllib.quote_plus(url), urllib.quote_plus(torrent.getContentList()[0].path), 0, '')
                listitem.setInfo(type = 'Video', infoLabels = {"Title":'<' + Localization.localize('Add To Bookmarks') + ' >'})
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=itemUrl, listitem=listitem)
                contentList = []
                for contentId, contentFile in enumerate(torrent.getContentList()):
                    fileTitle = "%s [%s MB]" % (contentFile.path, contentFile.size / 1024 / 1024)#In MB
                    contentList.append((self.unescape(fileTitle), str(contentId)))
                contentList = sorted(contentList, key=lambda x: x[0])
                for title, identifier in contentList:
                    self.drawItem(title, 'playTorrent', identifier, isFolder=False)
                    #xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_TITLE)
                self.lockView('wide')
                xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)

    def cutFileNames(self, l):
        from difflib import Differ
        d = Differ()
        i=-1
        m=self.getDirList(None, l)
        if len (m)<2: return l
        text1 = str(m[0])
        text2 = str(m[1])

        seps=['.|:| ', '.|:|x', ' |:|x', ' |:|-', '_|:|',]
        for s in seps:
            sep_file=str(s).split('|:|')[0]
            result=list(d.compare(text1.split(sep_file), text2.split(sep_file)))
            if len(result)>5:
                break

        print list(d.compare(text1.split(sep_file), text2.split(sep_file)))

        start=''
        end=''

        for res in result:
            if str(res).startswith('-') or str(res).startswith('+') or str(res).startswith('.?'):
                break
            start=start+str(res).strip()+sep_file
        result.reverse()
        for res in result:
            if str(res).startswith('-') or str(res).startswith('+') or str(res).startswith('?'):
                break
            end=sep_file+str(res).strip()+end


        newl=l
        l=[]
        for fl in newl:
            if fl[0:len(start)]==start: fl=fl[len(start):]
            if fl[len(fl)-len(end):]==end: fl=fl[0:len(fl)-len(end)]
            #fl=fl[len(start):len(fl)-len(end)] только это вместо 2 сверху
            l.append(fl)
        return l

    def getDirList(self, path, newl=None):
        l=[]
        try:
            if not newl: newl=os.listdir(path)
        except:
            if not newl: newl=os.listdir(path.decode('utf-8').encode('cp1251'))
        for fl in newl:
            match=re.match('.avi|.mp4|.mkV|.flv|.mov|.vob|.wmv|.ogm|.asx|.mpg|mpeg|.avc|.vp3|.fli|.flc|.m4v', fl[int(len(fl))-4:len(fl)], re.I)
            if match:
                l.append(fl)
        return l

    def recentPlaybleRu(self, params = {}):
        address = 'http://playble.ru/search/video/~rss'
        document = xml.dom.minidom.parse(urllib.urlopen(address))
        for item in document.getElementsByTagName('item'):
            try:
                title = item.getElementsByTagName('title')[0].firstChild.data.encode('utf-8', 'replace')
                description = item.getElementsByTagName('description')[0].firstChild.data.encode('utf-8', 'replace')
                #seeds = re.search("<span class=\"s\">(\d+)</span>", description).group(1)
                image = re.search("<img src=\"(.+?)\" alt=\"\" />", description).group(1)
                self.drawItem(title, 'openSection', title, image)
            except:
                pass
        self.lockView('info')
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)

    def recentRuTorOrg(self, params = {}):
        categories = [1, 5, 12, 4, 6, 7, 10, 13, 15]
        for category in  categories:
            address = 'http://rutor.org/rss.php?category=' + str(category)
            document = xml.dom.minidom.parse(urllib.urlopen(address))
            for item in document.getElementsByTagName('item'):
                try:
                    title = item.getElementsByTagName('title')[0].firstChild.data.encode('utf-8', 'replace')
                    link = item.getElementsByTagName('link')[0].firstChild.data
                    image = self.ROOT + '/icons/video.png'
                    link = 'http://d.rutor.org/download.php?rss=' + re.search('^.+\/(\d+)$', link).group(1)
                    self.drawItem(title, 'openTorrent', link, image)
                except:
                    pass
        self.lockView('wide')
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)

    def recentOpenSharingOrg(self, params = {}):
        categories = [1, 4, 6, 7]
        for category in  categories:
            address = 'http://opensharing.org/rss.php?category=' + str(category)
            document = xml.dom.minidom.parse(urllib.urlopen(address))
            for item in document.getElementsByTagName('item'):
                try:
                    title = item.getElementsByTagName('title')[0].firstChild.data.encode('utf-8', 'replace')
                    link = item.getElementsByTagName('link')[0].firstChild.data
                    image = self.ROOT + '/icons/video.png'
                    link = 'http://opensharing.org/download/' + re.search('^.+\/(\d+)/$', link).group(1)
                    self.drawItem(title, 'openTorrent', link, image)
                except:
                    pass
        self.lockView('wide')
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)

    def recentRuTrackerOrg(self, params = {}):
        address = 'http://xpoft.ru/torrents.ru/rss.xml?352;93;101;905;100;2198;313;2199;312;33;124;149;7;187;2459;212;2221;2091;2092;2093;2090;921;4;2365;930;208;1900;539;822;22;941;789;772'
        try:
            document = xml.dom.minidom.parse(urllib.urlopen(address))
        except:
            return
        for item in document.getElementsByTagName('item'):
            try:
                title = item.getElementsByTagName('title')[0].firstChild.data.encode('utf-8', 'replace')
                title = re.search('^(.+?)[\[\(]', title).group(1)
                description = item.getElementsByTagName('description')[0].firstChild.data.encode('utf-8', 'replace')
                try:
                    image = re.search("<img src=\"(.+?)\">", self.unescape(description)).group(1)
                except:
                    image = self.ROOT + '/icons/video.png'
                self.drawItem(title, 'openSection', title, image)
            except:
                pass
        self.lockView('info')
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)

    def recentKinopoiskRuBluRay(self, params = {}):
        address = 'http://st.kinopoisk.ru/rss/bluray.rss'
        document = xml.dom.minidom.parse(urllib.urlopen(address))
        for item in document.getElementsByTagName('item'):
            try:
                title = item.getElementsByTagName('title')[0].firstChild.data.encode('utf-8', 'replace')
                try:
                    image = item.getElementsByTagName('enclosure')[0].attributes.get('url').nodeValue
                except:
                    image = self.ROOT + '/icons/video.png'
                self.drawItem(title, 'openSection', re.search('^Blu-Ray\:\s(.+)$', title).group(1), image)
            except:
                pass
        self.lockView('info')
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)

    def recentKinopoiskRuDvd(self, params = {}):
        address = 'http://st.kinopoisk.ru/rss/dvd.rss'
        document = xml.dom.minidom.parse(urllib.urlopen(address))
        for item in document.getElementsByTagName('item'):
            try:
                title = item.getElementsByTagName('title')[0].firstChild.data.encode('utf-8', 'replace')
                try:
                    image = item.getElementsByTagName('enclosure')[0].attributes.get('url').nodeValue
                except:
                    image = self.ROOT + '/icons/video.png'
                self.drawItem(title, 'openSection', re.search('^DVD\:\s(.+)$', title).group(1), image)
            except:
                pass
        self.lockView('info')
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)

    def recentKinopoiskRu(self, params = {}):
        address = 'http://st.kinopoisk.ru/rss/premiere.rss'
        document = xml.dom.minidom.parse(urllib.urlopen(address))
        for item in document.getElementsByTagName('item'):
            try:
                title = item.getElementsByTagName('title')[0].firstChild.data.encode('utf-8', 'replace')
                image =  item.getElementsByTagName('enclosure')[0].attributes.get('url').nodeValue
                self.drawItem(title, 'openSection', title, image)
            except:
                pass
        self.lockView('info')
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)

    def recentNNMClubRu(self, params = {}):
        address = 'http://nnm-club.ru/forum/rss2.php?r&s&f=220,224,229,918,216,318,254,256,768,769,713,576,603,610'
        document = xml.dom.minidom.parse(urllib.urlopen(address))
        for item in document.getElementsByTagName('item'):
            try:
                title = item.getElementsByTagName('title')[0].firstChild.data.encode('utf-8', 'replace')
                image = self.ROOT + '/icons/video.png'
                self.drawItem(title, 'openSection', re.search('^(.+) \[.+?\]$', title).group(1), image)
            except:
                pass
        self.lockView('wide')
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)

    def recentMaterilas(self, params = {}):
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)
        import Filters
        filters = Filters.Filters()
        filters.doModal()
        return
        self.drawItem('RuTor.Org', 'recentRuTorOrg')
        self.drawItem('OpenSharing.Org', 'recentOpenSharingOrg')
        self.drawItem('NNM-Club.Ru', 'recentNNMClubRu')
        #self.drawItem('RuTracker.Org', 'recentRuTrackerOrg')
        self.drawItem('Playble.Ru', 'recentPlaybleRu')
        self.drawItem('Kinopoisk.Ru', 'recentKinopoiskRu')
        self.drawItem('Kinopoisk.Ru - DVD', 'recentKinopoiskRuDvd')
        self.drawItem('Kinopoisk.Ru - Blu-Ray', 'recentKinopoiskRuBluRay')
        self.lockView('info')
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)

    def sectionMenu(self):
        self.drawItem(Localization.localize('< Search >'), 'search', image=self.ROOT + '/icons/search.png')
        '''self.drawItem(Localization.localize('< Popular >'), 'getPopular', image=self.ROOT + '/icons/video.png')
        self.drawItem(Localization.localize('< Ratings >'), 'getRatings', image=self.ROOT + '/icons/video.png')        
        self.drawItem(Localization.localize('< Recent Materials >'), 'recentMaterilas', image=self.ROOT + '/icons/video.png')
        if self.__settings__.getSetting("auth"):
            self.drawItem(Localization.localize('< Bookmarks >'), 'getBookmarks', image=self.ROOT + '/icons/bookmarks.png')
            self.drawItem(Localization.localize('< History >'), 'getHistory', image=self.ROOT + '/icons/history.png')
            self.drawItem(Localization.localize('< Logout >'), 'logoutUser', image=self.ROOT + '/icons/logout.png')
        else:
            self.drawItem(Localization.localize('< Login >'), 'loginUser', image=self.ROOT + '/icons/login.png')
            self.drawItem(Localization.localize('< Register >'), 'registerUser', image=self.ROOT + '/icons/register.png')'''
        if 'true' == self.__settings__.getSetting("keep_files"):
            self.drawItem(Localization.localize('< Clear Storage >'), 'clearStorage', isFolder = True)
        self.lockView('list')
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)

    def openSection(self, params = {}): #myshows
        get = params.get
        url = urllib.unquote_plus(get("url"))
        try: external=urllib.unquote_plus(get("external"))
        except: external=None
        filesList = []
        if None == get('isApi'):
            progressBar = xbmcgui.DialogProgress()
            progressBar.create(Localization.localize('Please Wait'), Localization.localize('Materials are loading now.'))
            iterator = 0
        searchersList = []
        dirList = os.listdir(self.ROOT + os.sep + 'resources' + os.sep + 'searchers')
        if not external or external=='torrenterall':
            for searcherFile in dirList:
                if re.match('^(\w+)\.py$', searcherFile):
                    searchersList.append(searcherFile)
        else: searchersList.append(external+'.py')
        for searcherFile in searchersList:
            searcher = re.search('^(\w+)\.py$', searcherFile).group(1)
            if searcher:
                if None == get('isApi'):
                    progressBar.update(int(iterator), searcher)
                    iterator += 100 / len(searchersList)
                filesList += self.searchWithSearcher(url, searcher)
            if None == get('isApi') and progressBar.iscanceled():
                progressBar.update(0)
                progressBar.close()
                return
        if None == get('isApi'):
            progressBar.update(0)
            progressBar.close()
        filesList = sorted(filesList, key=lambda x: x[0], reverse=True)
        self.showFilesList(filesList, params)

    def searchWithSearcher(self, keyword, searcher):
        filesList = []
        if self.ROOT + os.sep + 'resources' + os.sep + 'searchers' not in sys.path:
            sys.path.insert(0, self.ROOT + os.sep + 'resources' + os.sep + 'searchers')
        try:
            searcherObject = getattr(__import__(searcher), searcher)()
            if searcherObject.isMagnetLinkSource and 'false' == self.__settings__.getSetting("use_magnet_links"):
                return filesList
            filesList = searcherObject.search(keyword)
        except Exception, e:
            print 'Unable to use searcher: ' + searcher + ' at ' + self.__plugin__ + ' searchWithSearcher(). Exception: ' + str(e)
        return filesList

    def jstr(self, s):
        if not s: s='null'
        elif not unicode(s).isnumeric(): s='"%s"'%(s)
        return str(s)

    def showFilesList(self, filesList, params={}): #myshows
        get = params.get
        try: external=urllib.unquote_plus(get("external"))
        except: external=None
        if external:
            try:
                s=json.loads(json.loads(urllib.unquote_plus(get("sdata"))))
                if len(filesList)<1:
                    xbmc.executebuiltin('XBMC.ActivateWindow(%s)' % 'Videos,plugin://plugin.video.myshows/?mode=20&showId=%s' % (self.jstr(s['showId'])))
                    return
                myshows_setting=xbmcaddon.Addon(id='plugin.video.myshows')
                myshows_lang=myshows_setting.getLocalizedString
                for (order, seeds, title, link, image) in filesList:
                    #print '{"filename":"%s", "stype":%s, "showId":%s, "seasonId":%s, "id":%s, "episodeId":%s}' % (link, self.jstr(s['stype']), self.jstr(s['showId']), self.jstr(s['seasonId']), self.jstr(s['id']), self.jstr(s['episodeId']))
                    contextMenu = [
                        (myshows_lang(30409),
                         'XBMC.RunPlugin(%s)' % ('plugin://plugin.video.myshows/?mode=3010&sort=activate&stringdata='+urllib.quote_plus('{"filename":"%s", "stype":%s, "showId":%s, "seasonId":%s, "id":%s, "episodeId":%s}' % (link, self.jstr(s['stype']), self.jstr(s['showId']), self.jstr(s['seasonId']), self.jstr(s['id']), self.jstr(s['episodeId']))))),
                        (myshows_lang(30400) ,
                         'XBMC.ActivateWindow(%s)' % 'Videos,plugin://plugin.video.myshows/?mode=20&showId=%s' % (self.jstr(s['showId'])))
                    ]
                    self.drawItem(title, 'openTorrent', link, image, contextMenu=contextMenu)
            except:
                xbmc.executebuiltin('XBMC.ActivateWindow(%s)' % 'Videos,plugin://plugin.video.myshows/?mode=20&showId=%s' % (self.jstr(s['showId'])))
                return
        else:
            for (order, seeds, title, link, image) in filesList:
                contextMenu = [
                    (Localization.localize('Add To Bookmarks'),
                     'XBMC.RunPlugin(%s)' % ('%s?action=%s&url=%s&name=%s&seeds=%s&image=%s') % (sys.argv[0], 'addBookmark', urllib.quote_plus(link), urllib.quote_plus(title), seeds, urllib.quote_plus(image)))
                ]
                self.drawItem(title, 'openTorrent', link, image, contextMenu=contextMenu)
        self.lockView('wide')
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)

    def getPopular(self, params = {}):
        filesList = []
        response = json.loads(self.fetchData(self.URL + '/popular').encode('utf-8'))
        for record in response:
            filesList.append((0, 0, '%s [%s: %s]' % (str(record['name'].encode('utf-8', 'replace')), Localization.localize('Views'), str(record['count'])), record['link'], ''))
        self.showFilesList(filesList)

    def addHistory(self, name):
        if 0 < len(self.__settings__.getSetting("auth")):
            response = json.loads(self.fetchData(self.URL + '/history/add?link=%s&name=%s' % (urllib.quote_plus(self.__settings__.getSetting("lastTorrentUrl")), urllib.quote_plus(name))).encode('utf-8'))
        try:
            if not self.checkForAuth(response):
                return
        except: return

    def getHistory(self, params = {}):
        filesList = []
        response = json.loads(self.fetchData(self.URL + '/history').encode('utf-8'))
        if not self.checkForAuth(response):
            return
        for record in response:
            filesList.append((0, 0, str(record['name'].encode('utf-8', 'replace')), record['link'], ''))
        self.showFilesList(filesList)

    def getBookmarks(self, params = {}):
        response = json.loads(self.fetchData(self.URL + '/bookmarks').encode('utf-8'))
        if not self.checkForAuth(response):
            return
        for record in response:
            contextMenu = [(
                Localization.localize('Remove From Bookmarks'),
                'XBMC.RunPlugin(%s)' % ('%s?action=%s&id=%s') % (sys.argv[0], 'removeBookmark', record['id'])
            )]
            self.drawItem(str(record['name'].encode('utf-8', 'replace')), 'openTorrent', record['link'], record['image'], contextMenu=contextMenu)
        self.lockView('wide')
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)

    def removeBookmark(self, params = {}):
        get = params.get
        if 0 < len(self.__settings__.getSetting("auth")):
            response = json.loads(self.fetchData(self.URL + '/bookmarks/remove?id=%s' % (get("id"))).encode('utf-8'))
            if not self.checkForAuth(response):
                return
            if 'removed' == response:
                xbmc.executebuiltin("Notification(%s, %s, 2500)" % (Localization.localize('Bookmark'), Localization.localize('Item successfully removed from Bookmarks')))
                xbmc.executebuiltin("Container.Refresh()")
            else:
                xbmc.executebuiltin("Notification(%s, %s, 2500)" % (Localization.localize('Bookmark'), Localization.localize('Bookmark not removed')))

    def addBookmark(self, params = {}):
        get = params.get
        if 0 < len(self.__settings__.getSetting("auth")):
            response = json.loads(self.fetchData(self.URL + '/bookmarks/add?link=%s&name=%s&seeds=%s&image=%s' % (get("url"), get('name'), get('seeds'), get('image'))).encode('utf-8'))
            if not self.checkForAuth(response):
                return
            if 'added' == response:
                xbmc.executebuiltin("Notification(%s, %s, 2500)" % (Localization.localize('Bookmark'), Localization.localize('Item successfully added to Bookmarks')))
            else:
                xbmc.executebuiltin("Notification(%s, %s, 2500)" % (Localization.localize('Bookmark'), Localization.localize('Bookmark not added')))

    def getRatings(self, params = {}):
        filesList = []
        response = json.loads(self.fetchData(self.URL + '/rated').encode('utf-8'))
        for record in response:
            filesList.append((0, 0, '%s [%s: %s/ %s: %s]' % (str(record['name'].encode('utf-8', 'replace')), Localization.localize('Views'), str(record['cnt']), Localization.localize('Rating'), str(record['rating'])), record['link'], ''))
        self.showFilesList(filesList)

    def addRate(self, name):
        #xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=False)
        import Rates
        rating = Rates.Rates()
        rating.doModal()
        result = rating.rate
        del rating
        #xbmc.executebuiltin("Notification(%s, %s, 2500)" % ('Rating', str(rating.rate)))
        if 0 < len(self.__settings__.getSetting("auth")):
            response = json.loads(self.fetchData(self.URL + '/rating/add?link=%s&name=%s&rating=%s' % (urllib.quote_plus(self.__settings__.getSetting("lastTorrentUrl")), urllib.quote_plus(name), str(result))).encode('utf-8'))
            if not self.checkForAuth(response):
                return

    def search(self, params = {}):
        defaultKeyword = params.get('url')
        try:
            myshows_setting=xbmcaddon.Addon(id='plugin.video.myshows')
            showKey=myshows_setting.getSetting("torrenter_keyboard")
        except: showKey="true"
        if showKey=="true" or defaultKeyword=='' or not defaultKeyword:
            if not defaultKeyword:
                defaultKeyword = ''
            keyboard = xbmc.Keyboard(defaultKeyword, Localization.localize('Search Phrase') + ':')
            keyboard.doModal()
            query = keyboard.getText()
            if not query:
                return
            elif keyboard.isConfirmed():
                params["url"] = urllib.quote_plus(query)
                self.openSection(params)
        else:
            self.openSection(params)

    def loginUser(self, params = {}):
        if self.__settings__.getSetting("auth"):
            xbmc.executebuiltin("Notification(%s, %s, 2500)" % (Localization.localize('Auth'), Localization.localize('Already logged in')))
            return

        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=False)
        keyboardUser = xbmc.Keyboard("", Localization.localize("Input Email:"))
        keyboardUser.doModal()
        email = keyboardUser.getText()
        if not email:
            return

        keyboardPass = xbmc.Keyboard("", Localization.localize("Input Password:"))
        keyboardPass.setHiddenInput(True)
        keyboardPass.doModal()
        password = keyboardPass.getText()
        keyboardPass.setHiddenInput(False)
        if not password:
            return
        try:
            cookieJar = cookielib.CookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))
            value = json.loads(opener.open(self.URL + "/login?email=%s&password=%s" % (email, password)).read().encode('utf-8'))
            if 'logged' == value:
                xbmc.executebuiltin("Notification(%s, %s, 2500)" % (Localization.localize('Auth'), Localization.localize('Login successfull')))
                for cookie in cookieJar:
                    if cookie.name == 'PHPSESSID':
                        self.__settings__.setSetting("auth", 'PHPSESSID=' + cookie.value)
            else:
                xbmc.executebuiltin("Notification(%s, %s [%s], 2500)" % (Localization.localize('Auth'), Localization.localize('Login failed'), value))
                self.loginUser()
        except urllib2.HTTPError, e:
            print self.__plugin__ + " loginUser() exception: " + str(e)
        xbmc.executebuiltin("Container.Refresh()")

    def registerUser(self, params = {}):
        if self.__settings__.getSetting("auth"):
            xbmc.executebuiltin("Notification(%s, %s, 2500)" % (Localization.localize('Auth'), Localization.localize('Already logged in')))
            return

        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=False)
        keyboardUser = xbmc.Keyboard("", Localization.localize("Input Email (for password recovery):"))
        keyboardUser.doModal()
        email = keyboardUser.getText()
        if not email:
            return

        keyboardPass = xbmc.Keyboard("", Localization.localize("Input Password (6+ symbols):"))
        keyboardPass.setHiddenInput(True)
        keyboardPass.doModal()
        password = keyboardPass.getText()
        keyboardPass.setHiddenInput(False)
        if not password:
            return
        try:
            cookieJar = cookielib.CookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))
            value = json.loads(opener.open(self.URL + "/register?email=%s&password=%s" % (email, password)).read().encode('utf-8'))
            if 'logged' == value:
                xbmc.executebuiltin("Notification(%s, %s, 2500)" % (Localization.localize('Auth'), Localization.localize('Login successfull')))
                for cookie in cookieJar:
                    if cookie.name == 'PHPSESSID':
                        self.__settings__.setSetting("auth", 'PHPSESSID=' + cookie.value)
            else:
                xbmc.executebuiltin("Notification(%s, %s [%s], 2500)" % (Localization.localize('Auth'), Localization.localize('Login failed'), value))
                self.loginUser()
        except urllib2.HTTPError, e:
            print self.__plugin__ + " registerUser() exception: " + str(e)
        xbmc.executebuiltin("Container.Refresh()")

    def logoutUser(self, params = {}):
        if not self.__settings__.getSetting("auth"):
            xbmc.executebuiltin("Notification(%s, %s, 2500)" % (Localization.localize('Auth'), Localization.localize('User not logged in')))
            return
        self.__settings__.setSetting("auth", '')
        cookieJar = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))
        opener.open(self.URL + "/logout").read()
        xbmc.executebuiltin("Notification(%s, %s, 2500)" % (Localization.localize('Auth'), Localization.localize('User successfully logged out')))
        xbmc.executebuiltin("Container.Refresh()")

    def checkForAuth(self, response):
        if response == 'auth problems':
            xbmc.executebuiltin("Notification(%s, %s, 2500)" % (Localization.localize('Auth'), Localization.localize('Auth expired, please relogin')))
            time.sleep(2.5)
            self.logoutUser()
            return False
        return True