#!/usr/bin/python
# -*- coding: utf-8 -*-

import httplib
import urllib
import urllib2
import re
import sys
import os
import socket
import threading
import time
import random
import json

import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmc
import xbmcaddon

_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
addon_icon=None

def _construct_request(params):
	return '%s?%s' % (sys.argv[0], urllib.urlencode(params))

def _showMessage(heading, message, times = 3000, pics = addon_icon):
	try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading.encode('utf-8'), message.encode('utf-8'), times, pics.encode('utf-8')))
	except Exception, e:
		xbmc.log( '[%s]: showMessage: Transcoding UTF-8 failed', 2 )
		try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, pics))
		except Exception, e:
			xbmc.log( '[%s]: showMessage: exec failed ' , 3 )

def _com_received(text):
        try:
                return text.split(' ')[0]
        except: return text
		
class TSengine(object):
	
	def _TSpush(self,command):
		#print '>>'+command
		_sock.send(command+'\r\n')
	
	def __init__(self, icon ):
		self.addon_icon=icon
		self.ready = False
		self.filelist = None
		self.file_count = None
		self.url=None
		self.player=None
		self.playing=False
		self.error_num=None

	def connect(self, host='127.0.0.1', port=62062):
		
		try:
			_sock.connect((host, port))
		except:
			_showMessage('TSengine', 'TS not started!', 2000,self.addon_icon)
			return False
			exit
			
		self.r = _TSpull(1)
		self.r.start()
	
		comm="HELLOBG"
		self._TSpush(comm)
		while not self.r.last_com:
			_showMessage('TSengine', 'Waiting responce TS', 2000,self.addon_icon)  
			time.sleep(1)
		
		comm='READY'
		self._TSpush(comm)
		self.ready=True
		return True
	
	def load(self,url):
		self.url=url
		comm='LOADASYNC '+ str(random.randint(0, 0x7fffffff)) +' TORRENT ' + url+ ' 0 0 0'
		self._TSpush(comm)
		while not self.r.files:
			time.sleep(1)
		self.filelist=self.r.files
		self.file_count = self.r.count
		#print self.filelist

	def geturl_ind(self, index=0):
		
		comm='START TORRENT ' + self.url + ' '+ str(index) +' 0 0 0'
		self._TSpush(comm)
		i=0
		lstprc=0
		while not self.r.got_url:
			if self.r.last_com=='STATUS':
				try: 
					prc=int(self.r.last_received.split(';')[1])
					if prc==lstprc: i+=1
					else: i=0
					lstprc=prc
					_showMessage('TSengine', '"%s" percents' % self.r.last_received.split(';')[1], 3500,self.addon_icon)
				except: pass
			#print r.last_received
				time.sleep(3)
				if i>10: 
					comm="SHUTDOWN"
					self._TSpush(comm)
					self.r.active = False
					_sock.close()
					return ""
		#print self.r.got_url
		return self.r.got_url
	
		
	def end(self):
		#print self.r.received
		
		comm="SHUTDOWN"
		self._TSpush(comm)
		self.r.active = False
		#self.r.end()
		_sock.close()
		#print 'Done'
		
class _TSpull(threading.Thread):
	def __init__(self,interval):
		threading.Thread.__init__(self)
		self.daemon = True
		self.interval = interval	#Я не пользуюсь, возможно пригодится, если будет тормозить
		self.active = True			#Если пошлем False - поток остановится и перестанет принимать данные
		self.lastresolt=None		
		self.received = []			#Тут хранится все, что пришло от сервера ТС (пригодится, я думаю)
		self.last_received=None		#Последний ответ от ТССервера
		self.last_com=None			#Последняя команда от ТССервера
		self.got_url=None			#Будет ссылка на файл после буфферизации
		self.files=None				#Список файлов в json
		self.buffer=10000000			#размер буффера для приема нужен большой, если файлов много
		self.count=None
	def run(self):
		while self.active:
			try:
				self.last_received=_sock.recv(self.buffer)
				#print self.last_received
				self.received.append(self.last_received)
				self.last_com = _com_received(self.last_received)
				if self.last_com=='PLAY': self.got_url=self.last_received.split(' ')[1] # если пришло PLAY URL, то забираем себе ссылку
				if self.last_com=='LOADRESP': 
					fil = self.last_received
					ll= fil[fil.find('{'):len(fil)]
					self.files=ll
					try:
						json_files=json.loads(ll)
						if json_files['status']==2:
							self.count=len(json_files['files'])
						if json_files['status']==1:
							self.count=1
						if json_files['status']==0:
							self.count=None
					except:
						self.count=None
						
			except:
				pass
				#_showMessage('Торренты', 'Ошибка приема данных', 2000)
				
	def end(self):
		self.daemon = False


		