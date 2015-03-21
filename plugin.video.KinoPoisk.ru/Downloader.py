#-*- coding: utf-8 -*-
'''
	Torrenter plugin for XBMC
	Copyright (C) 2011 Vadim Skorba
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
#import libtorrent

try:
	from python_libtorrent.linux_x86_64 import libtorrent
except ImportError, v:
	pass
try:
	from python_libtorrent.linux_x86 import libtorrent
except ImportError, v:
	pass
try:
	from python_libtorrent.windows import libtorrent
except ImportError, v:
	pass
try:
	import libtorrent
except ImportError, v:
	pass

import time
import thread
import os.path
import urllib2
import hashlib
import xbmc
import xbmcgui

class Torrent:
	torrentFile = None
	storageDirectory = ''
	startPart = 0
	endPart = 0
	partOffset = 0
	torrentHandle = None
	session = None
	downloadThread = None
	threadComplete = False
	canPlay = False
	def __init__(self, torrentUrl, storageDirectory = '', isMagnet=False):
		self.torrentFile = storageDirectory + os.sep + 'torrents' + os.sep + self.md5(torrentUrl) + '.torrent'
		print self.torrentFile
		if not os.path.exists(storageDirectory + os.sep + 'torrents'):
			os.makedirs(storageDirectory + os.sep + 'torrents')
		if isMagnet:
			self.magnetToTorrent(torrentUrl)
		elif not os.path.exists(self.torrentFile):
			try:
				request = urllib2.Request(torrentUrl)
				request.add_header('Referer', torrentUrl)
				localFile = open(self.torrentFile, "w+b")
				result = urllib2.urlopen(request)
				localFile.write(result.read())
				localFile.close()
			except:
				print 'Unable to save torrent file from "' + torrentUrl + '" to "' + self.torrentFile + '" in Torrent::__init__'
		self.storageDirectory = storageDirectory
		self.torrentFileInfo = libtorrent.torrent_info(self.torrentFile)
		self.partOffset = 45 * 1024 * 1024 / self.torrentFileInfo.piece_length()#45 MB

	def magnetToTorrent(self, magnet):
		session = libtorrent.session()
		session.start_dht()
		session.add_dht_router("router.bittorrent.com", 6881)
		session.add_dht_router("router.utorrent.com", 6881)
		session.add_dht_router("router.bitcomet.com", 6881)
		session.listen_on(6881, 6891)
		session.set_alert_mask(libtorrent.alert.category_t.storage_notification)
		handle = libtorrent.add_magnet_uri(session, magnet, {'save_path': self.storageDirectory, 'storage_mode': libtorrent.storage_mode_t(2)})
		iterator = 0
		progressBar = xbmcgui.DialogProgress()
		progressBar.create('Подождите', 'Идёт преобразование magnet-ссылки.')
		while not handle.has_metadata():
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
		torrent = libtorrent.create_torrent(handle.get_torrent_info())
		torentFile = open(self.torrentFile, "wb")
		torentFile.write(libtorrent.bencode(torrent.generate()))
		torentFile.close()
		session.remove_torrent(handle)

	def getFilePath(self, contentId = 0):
		return self.storageDirectory + os.sep + self.getContentList()[contentId].path

	def getContentList(self):
		return self.torrentFileInfo.files()

	def md5(self, string):
		hasher = hashlib.md5()
		hasher.update(string)
		return hasher.hexdigest()

	def downloadProcess(self, contentId):
		for part in range(self.startPart, self.endPart + 1):
			#print 'parts from ' + str(self.startPart) + ' to ' + str(self.endPart + 1) + ' now - ' + str(part)
			self.getPiece(part)
			time.sleep(0.1)
			self.checkThread()
			if part > 1:
				self.canPlay = True
		self.threadComplete = True

	def startSession(self, contentId = 0):
		selectedFileInfo = self.getContentList()[contentId]
		self.startPart = selectedFileInfo.offset / self.torrentFileInfo.piece_length()
		self.endPart = (selectedFileInfo.offset + selectedFileInfo.size) / self.torrentFileInfo.piece_length()
		
		self.session = libtorrent.session()
		self.session.start_dht()
		self.session.add_dht_router("router.bittorrent.com", 6881)
		self.session.add_dht_router("router.utorrent.com", 6881)
		self.session.add_dht_router("router.bitcomet.com", 6881)
		self.session.listen_on(6881, 6891)
		self.session.set_alert_mask(libtorrent.alert.category_t.storage_notification)
		self.torrentHandle = self.session.add_torrent({'ti': self.torrentFileInfo, 'save_path': self.storageDirectory, 'storage_mode': libtorrent.storage_mode_t(2)})
		for i in range(self.torrentFileInfo.num_pieces()):
			self.torrentHandle.piece_priority(i, 0)
		for i in range(self.startPart, self.startPart + self.partOffset):
			if i <= self.endPart:
				self.torrentHandle.piece_priority(i, 7)
		self.torrentHandle.set_sequential_download(True)
		thread.start_new_thread(self.downloadProcess, (contentId,))

	def fetchParts(self):
		priorities = self.torrentHandle.piece_priorities()
		status = self.torrentHandle.status()
		downloading = 0
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
			if isinstance(part, libtorrent.read_piece_alert):
				if part.piece == index:
					return part.buffer
				else:
					cache[part.piece] = part.buffer
				break
			time.sleep(0.5)
			self.checkThread()
