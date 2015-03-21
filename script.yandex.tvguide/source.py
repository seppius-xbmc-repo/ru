#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
#import simplejson
import datetime
import time
import urllib2
#from elementtree import ElementTree
from strings import *
#import ysapi

import pickle
import xml.dom.minidom

class Channel(object):
	def __init__(self, id, title, logo = None):
		self.id = id
		self.title = title
		self.logo = logo

	def __str__(self):
		return 'Channel(id=%s, title=%s, logo=%s)' % (self.id, self.title, self.logo)

class Program(object):
	def __init__(self, channel, title, startDate, endDate, description, imageLarge = None, imageSmall=None):
		self.channel = channel
		self.title = title
		self.startDate = startDate
		self.endDate = endDate
		self.description = description
		self.imageLarge = imageLarge
		self.imageSmall = imageSmall

	def __str__(self):
		return 'Program(channel=%s, title=%s, startDate=%s, endDate=%s, description=%s, imageLarge=%s, imageSmall=%s)' % \
			(self.channel, self.title, self.startDate, self.endDate, self.description, self.imageLarge, self.imageSmall)




class Source(object):
	KEY = "undefiend"

	def __init__(self, settings, hasChannelIcons):
		self.channelIcons = hasChannelIcons
		self.cachePath = settings['cache.path']

	def hasChannelIcons(self):
		return self.channelIcons

	def getChannelList(self):
		cacheFile = os.path.join(self.cachePath, self.KEY + '.channellist')

		try:
			cachedOn = datetime.datetime.fromtimestamp(os.path.getmtime(cacheFile))
			cacheHit = cachedOn.day == datetime.datetime.now().day
		except OSError:
			cacheHit = False

		#if not cacheHit:
		channelList = self._getChannelList()
		#	pickle.dump(channelList, open(cacheFile, 'w'))
		#else:
		#	channelList = pickle.load(open(cacheFile))

		return channelList

	def _getChannelList(self):
		return None

	def getProgramList(self, channel):
		id = str(channel.id).replace('/', '')
		cacheFile = os.path.join(self.cachePath, self.KEY + '-' + id + '.programlist')

		try:
			cachedOn = datetime.datetime.fromtimestamp(os.path.getmtime(cacheFile))
			cacheHit = cachedOn.day == datetime.datetime.now().day
		except OSError:
			cacheHit = False

		#if not cacheHit:
		programList = self._getProgramList(channel)
		#	pickle.dump(programList, open(cacheFile, 'w'))
		#else:
		#	programList = pickle.load(open(cacheFile))

		return programList

	def _getProgramList(self, channel):
		return None

	def _downloadUrl(self, url):
		u = urllib2.urlopen(url)
		content = u.read()
		u.close()

		return content




class XMLYandex(Source):


	def _parseDate(self, dateString):
		t = time.strptime(dateString, '%Y-%m-%d %H:%M:%S')
		return datetime.datetime(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)
	# http://yandex.st/tv/i/stv/279791.jpg

	def __init__(self, settings):
		Source.__init__(self, settings, True)
		self.time = time.time()
		self.time -= self.time % 3600
		target = 'http://tv.yandex.ru/export/programs.xml'
		print 'TARGET = [%s]' % target
		http = self._downloadUrl(target)
		print 'HTTP LEN = [%s]' % len(http)
		yaxml = xml.dom.minidom.parseString(http)

		self.yadoc = None
		self.page_size = None
		self.page_count = None
		self.page_hostname = None
		self.epg = {}

		for yatree in yaxml.getElementsByTagName('programs'):
			print 'INTERATOR'
			if yatree.getAttribute('page_size') and yatree.getAttribute('count') and yatree.getAttribute('hostname'):
				self.page_size     = int(yatree.getAttribute('page_size'))
				self.page_count    = int(yatree.getAttribute('count'))
				self.page_hostname = yatree.getAttribute('hostname').encode('utf-8')
				for channel in yatree.getElementsByTagName('channel'):
					if channel.getAttribute('id'):
						channel_id = int(channel.getAttribute('id'))
						levents = []
						for event in channel.getElementsByTagName('event'):
							# TODO: insert Yandex class
							initial = {'is_finished': None, 'weekday': None}
							initial['id']           = int(event.getElementsByTagName('id')[0].firstChild.data)


							#initial['img'] = 'http://yandex.st/tv/i/logo/%s.gif' % initial['id']



							initial['pid']          = int(event.getElementsByTagName('pid')[0].firstChild.data)
							initial['name']         =     event.getElementsByTagName('name')[0].firstChild.data.encode('utf-8')
							initial['channel']      = int(event.getElementsByTagName('channel')[0].firstChild.data)
							initial['flag']         = int(event.getElementsByTagName('flag')[0].firstChild.data)
							initial['gate']         = int(event.getElementsByTagName('gate')[0].firstChild.data)
							initial['start']  = self._parseDate(event.getElementsByTagName('start')[0].firstChild.data.encode('utf-8'))
							initial['finish'] = self._parseDate(event.getElementsByTagName('finish')[0].firstChild.data.encode('utf-8'))
							initial['hour']         = int(event.getElementsByTagName('hour')[0].firstChild.data)
							initial['minute']       = int(event.getElementsByTagName('minute')[0].firstChild.data)
							initial['fhour']        = int(event.getElementsByTagName('fhour')[0].firstChild.data)
							initial['fminute']      = int(event.getElementsByTagName('fminute')[0].firstChild.data)
							initial['day']          = int(event.getElementsByTagName('day')[0].firstChild.data)
							initial['channel_name'] =     event.getElementsByTagName('channel_name')[0].firstChild.data.encode('utf-8')
							initial['type_id']      = int(event.getElementsByTagName('type_id')[0].firstChild.data)
							initial['start_stamp']  = int(event.getElementsByTagName('start_stamp')[0].firstChild.data)
							initial['finish_stamp'] = int(event.getElementsByTagName('finish_stamp')[0].firstChild.data)
							initial['flag_shablon'] = int(event.getElementsByTagName('flag_shablon')[0].firstChild.data)
							initial['flag_type']    = int(event.getElementsByTagName('flag_type')[0].firstChild.data)
							initial['flag_subtype'] = int(event.getElementsByTagName('flag_subtype')[0].firstChild.data)
							try: initial['is_finished'] = int(event.getElementsByTagName('is_finished')[0].firstChild.data)
							except: pass
							try: initial['weekday'] = int(event.getElementsByTagName('weekday')[0].firstChild.data)
							except: pass
							try: initial['img']     = event.getElementsByTagName('img')[0].firstChild.data.encode('utf-8')
							except: pass
							levents.append(initial)
						self.epg[channel_id] = levents

	def _getChannelList(self):
		channelList = []
		for epg_ch in self.epg:
			epg_current = self.epg[epg_ch]
			channel_name = epg_current[0]['channel_name']
			channel_img  = 'http://yandex.st/tv/i/logo/%s.gif' % epg_ch
			channelList.append(Channel(epg_ch, channel_name, channel_img))
		return channelList

	def _getProgramList(self, cur_ch):
		programs = []
		epg_current = self.epg[cur_ch.id]
		description = cur_ch.title
		for event in epg_current:
			e_name    = event['name']
			e_start   = event['start']
			e_finish  = event['finish']
			e_i_large = 'http://company.yandex.ru/i/yandex-gigant.png'
			try:
				print event['img']
				e_i_small = 'http://yandex.st/tv/i/stv/%s' % event['img'].split('/')[-1]
				print e_i_small
			except: e_i_small = None
			programs.append(Program(cur_ch, e_name, e_start, e_finish, description, e_i_large, e_i_small))
		return programs


