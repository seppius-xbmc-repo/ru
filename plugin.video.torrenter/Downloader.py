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

#http://www.rasterbar.com/products/libtorrent/manual.html
import warnings
warnings.filterwarnings('ignore', category=RuntimeWarning)
import libtorrent
import time
import thread
import os
import urllib2
import hashlib
import re
import xbmc
import xbmcgui
import xbmcvfs
import Localization

class Torrent:
    torrentFile = None
    magnetLink = None
    storageDirectory = ''
    torrentFilesDirectory = 'torrents'
    startPart = 0
    endPart = 0
    partOffset = 0
    torrentHandle = None
    session = None
    downloadThread = None
    threadComplete = False
    lt = None

    def __init__(self, storageDirectory = '', torrentFile = '', torrentFilesDirectory = 'torrents'):
        #http://www.rasterbar.com/products/libtorrent/manual.html
        try:
            import platform
            if 'Linux' == platform.system():
                if 'x86_64' == platform.machine():
                    from python_libtorrent.linux_x86_64 import libtorrent
                else:
                    from python_libtorrent.linux_x86 import libtorrent
            else:
                from python_libtorrent.windows import libtorrent
        except:
            try:
                import libtorrent
            except:
                raise ImportError("The script.module.libtorrent module is not installed, libtorrent not found or unsupported system used")
        self.lt = libtorrent
        del libtorrent
        self.torrentFilesDirectory = torrentFilesDirectory
        self.storageDirectory = storageDirectory
        if not xbmcvfs.exists(self.storageDirectory + os.sep + self.torrentFilesDirectory):
            self._makedirs(self.storageDirectory + os.sep + self.torrentFilesDirectory)
        if xbmcvfs.exists(torrentFile):
            self.torrentFile = torrentFile
            self.torrentFileInfo = self.lt.torrent_info(self.torrentFile)
        elif re.match("^magnet\:.+$", torrentFile):
            self.magnetLink = torrentFile
        
    def saveTorrent(self, torrentUrl):
        if re.match("^magnet\:.+$", torrentUrl):
            self.magnetLink = torrentUrl
            self.magnetToTorrent(torrentUrl)
            return self.magnetLink
        else:
            torrentFile = self.storageDirectory + os.sep + self.torrentFilesDirectory + os.sep + self.md5(torrentUrl) + '.torrent'
            try:
                request = urllib2.Request(torrentUrl)
                request.add_header('Referer', torrentUrl)
                localFile = open(torrentFile, "w+b")
                result = urllib2.urlopen(request)
                localFile.write(result.read())
                localFile.close()
            except:
                print 'Unable to save torrent file from "' + torrentUrl + '" to "' + torrentFile + '" in Torrent::saveTorrent'
                return
            if xbmcvfs.exists(torrentFile):
                try:
                    self.torrentFileInfo = self.lt.torrent_info(torrentFile)
                except:
                    xbmcvfs.delete(torrentFile)
                    return
                baseName = os.path.basename(self.getFilePath())
                newFile = self.storageDirectory + os.sep + self.torrentFilesDirectory + os.sep + baseName + '.' + self.md5(torrentUrl) + '.torrent'
                newFile = newFile.decode('utf-8').encode('ascii', 'ignore')
                try:xbmcvfs.delete(newFile)
                except:pass
                if not xbmcvfs.exists(newFile):
                    try:
                        xbmcvfs.rename(torrentFile, newFile)
                    except:
                        print 'Unable to rename torrent file from "' + torrentFile + '" to "' + newFile + '" in Torrent::renameTorrent'
                        return
                self.torrentFile = newFile
                self.torrentFileInfo = self.lt.torrent_info(self.torrentFile)
                return self.torrentFile

    def getMagnetInfo(self):
        magnetSettings = {
            'save_path': self.storageDirectory,
            'storage_mode': self.lt.storage_mode_t(2),
            'paused': True,
            'auto_managed': True,
            'duplicate_is_error': True
        }
        progressBar = xbmcgui.DialogProgress()
        progressBar.create(Localization.localize('Please Wait'), Localization.localize('Magnet-link is converting.'))
        self.torrentHandle = self.lt.add_magnet_uri(self.session, self.magnetLink, magnetSettings)
        iterator = 0
        while not self.torrentHandle.has_metadata():
            time.sleep(0.1)
            progressBar.update(iterator)
            iterator += 1
            if iterator == 100:
                iterator = 0
            if progressBar.iscanceled():
                progressBar.update(0)
                progressBar.close()
                return
        progressBar.update(0)
        progressBar.close()
        return self.torrentHandle.get_torrent_info()

    def magnetToTorrent(self, magnet):
        self.magnetLink = magnet
        self.initSession()
        torrentInfo = self.getMagnetInfo()
        try:
            torrentFile = self.lt.create_torrent(torrentInfo)
            baseName = os.path.basename(self.storageDirectory + os.sep + torrentInfo.files()[0].path).decode('utf-8').encode('ascii', 'ignore')
            self.torrentFile = self.storageDirectory + os.sep + self.torrentFilesDirectory + os.sep + baseName + '.torrent'
            torentFileHandler = open(self.torrentFile, "wb")
            torentFileHandler.write(self.lt.bencode(torrentFile.generate()))
            torentFileHandler.close()
            self.torrentFileInfo = self.lt.torrent_info(self.torrentFile)
        except:
            xbmc.executebuiltin("Notification(%s, %s, 7500)" % (Localization.localize('Error'), Localization.localize('Your library out of date and can\'t save magnet-links.')))
            self.torrentFileInfo = torrentInfo

    def getUploadRate(self):
        if None == self.torrentHandle:
            return 0
        else:
            return self.torrentHandle.status().upload_payload_rate

    def getDownloadRate(self):
        if None == self.torrentHandle:
            return 0
        else:
            return self.torrentHandle.status().download_payload_rate

    def getPeers(self):
        if None == self.torrentHandle:
            return 0
        else:
            return self.torrentHandle.status().num_peers

    def getSeeds(self):
        if None == self.torrentHandle:
            return 0
        else:
            return self.torrentHandle.status().num_seeds

    def getFileSize(self, contentId = 0):
        return self.getContentList()[contentId].size

    def getFilePath(self, contentId = 0):
        return self.storageDirectory + os.sep + self.getContentList()[contentId].path.decode('utf8')

    def getContentList(self):
        return self.torrentFileInfo.files()

    def setUploadLimit(self, bytesPerSecond):
        self.session.set_upload_rate_limit(int(bytesPerSecond))

    def setDownloadLimit(self, bytesPerSecond):
        self.session.set_download_rate_limit(int(bytesPerSecond))

    def md5(self, string):
        hasher = hashlib.md5()
        try:hasher.update(string)
        except:hasher.update(string.encode('utf-8','ignore'))
        return hasher.hexdigest()

    def downloadProcess(self, contentId):
        for part in range(self.startPart, self.endPart + 1):
            self.getPiece(part)
            time.sleep(0.1)
            self.checkThread()
        self.threadComplete = True

    def initSession(self):
        try:
            self.session.remove_torrent(self.torrentHandle)
        except:
            pass
        self.session = self.lt.session()
        self.session.start_dht()
        self.session.add_dht_router("router.bittorrent.com", 6881)
        self.session.add_dht_router("router.utorrent.com", 6881)
        self.session.add_dht_router("router.bitcomet.com", 6881)
        self.session.listen_on(6881, 6891)
        self.session.set_alert_mask(self.lt.alert.category_t.storage_notification)

    def startSession(self, contentId = 0, seeding = True):
        self.initSession()
        if None == self.magnetLink:
            self.torrentHandle = self.session.add_torrent({'ti': self.torrentFileInfo, 'save_path': self.storageDirectory})
        else:
            self.torrentFileInfo = self.getMagnetInfo()

        selectedFileInfo = self.getContentList()[contentId]
        self.partOffset = 50 * 1024 * 1024 / self.torrentFileInfo.piece_length()#50 MB
        #print 'partOffset ' + str(self.partOffset)
        self.startPart = selectedFileInfo.offset / self.torrentFileInfo.piece_length()
        self.endPart = (selectedFileInfo.offset + selectedFileInfo.size) / self.torrentFileInfo.piece_length()

        for i in range(self.torrentFileInfo.num_pieces()):
            self.torrentHandle.piece_priority(i, 0)
        for i in range(self.startPart, self.startPart + self.partOffset):
            if i <= self.endPart:
                self.torrentHandle.piece_priority(i, 7)
        self.torrentHandle.piece_priority(self.endPart, 7)
        self.torrentHandle.set_sequential_download(True)
        thread.start_new_thread(self.downloadProcess, (contentId,))
        if seeding:# and None == self.magnetLink:
            thread.start_new_thread(self.addToSeeding, ())

    def addToSeeding(self):
        for filename in os.listdir(self.storageDirectory + os.sep + self.torrentFilesDirectory):
            currentFile = self.storageDirectory + os.sep + self.torrentFilesDirectory + os.sep + filename
            if re.match('^.+\.torrent$', currentFile):
                info = self.lt.torrent_info(currentFile)
                fileSettings = {
                    'ti': info,
                    'save_path': self.storageDirectory,
                    'paused': False,
                    'auto_managed': False,
                    'seed_mode': True,
                }
                self.session.add_torrent(fileSettings)

    def fetchSeekBytes(self, bytes):
        seekPartsOffset = self.startPart + bytes / self.torrentFileInfo.piece_length()
        priorities = self.torrentHandle.piece_priorities()
        status = self.torrentHandle.status()
        if len(status.pieces) == 0:
            return
        if status.pieces[seekPartsOffset] == False:
            self.checkThread()
            self.torrentHandle.piece_priority(seekPartsOffset, 7)

    def fetchParts(self):
        priorities = self.torrentHandle.piece_priorities()
        status = self.torrentHandle.status()
        downloading = 0
        #print priorities
        if len(status.pieces) == 0:
            return
        for part in range(self.startPart, self.endPart + 1):
            if priorities[part] != 0 and status.pieces[part] == False:
                self.checkThread()
                downloading += 1
        for part in range(self.startPart, self.endPart + 1):
            if priorities[part] == 0 and downloading < self.partOffset:
                self.checkThread()
                self.torrentHandle.piece_priority(part, 1)
                downloading += 1
        for part in range(self.startPart, self.endPart + 1):
            if priorities[part] != 0 and status.pieces[part] == False:
                self.checkThread()
                break

    def checkThread(self):
        if self.threadComplete == True:
            self.session.remove_torrent(self.torrentHandle)
            thread.exit()

    def getPiece(self, index):
        cache = {}
        if index in cache:
            result = cache[index]
            cache[index] = 0
            return result
        while True:
            status = self.torrentHandle.status()
            if len(status.pieces) == 0:
                break
            if status.pieces[index] == True:
                break
            time.sleep(0.5)
            self.checkThread()
        self.torrentHandle.read_piece(index)
        while True:
            part = self.session.pop_alert()
            if isinstance(part, self.lt.read_piece_alert):
                if part.piece == index:
                    return part.buffer
                else:
                    cache[part.piece] = part.buffer
                break
            time.sleep(0.5)
            self.checkThread()

    def _makedirs(self, _path):
        success = False
        if (xbmcvfs.exists(_path)):
            return True
        # temp path
        tmppath = _path
        # loop thru and create each folder
        while (not xbmcvfs.exists(tmppath)):
            success = xbmcvfs.mkdir(tmppath)
            if not success:
                tmppath = os.path.dirname(tmppath)
        # call function until path exists
        self._makedirs(_path)
