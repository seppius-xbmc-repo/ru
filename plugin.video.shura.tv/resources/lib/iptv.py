# -*- coding: utf-8 -*
# SHURA.TV python class
# (c) AKGDRG, 2010-2012
# akgdrg@gmail.com

import urllib2
import datetime
import re, os, sys
from time import time
from xml.dom.minidom import parseString
import datetime

now = datetime.datetime.now()

__author__ = 'AKGDRG <akgdrg@gmail.com>'
__version__ = '0.1'

try:
	import xbmc, xbmcaddon
except ImportError:
	class xbmc_boo:
		
		def __init__(self):
			self.nonXBMC = True
			self.LOGDEBUG = 1
		
		def output(self, data, level = 0):
			print "xbmc.output is depricated. use xbmc.log instead"
			self.log(data, level)
		
		def log(self, data, level = 0):
			print data
		
		def getInfoLabel(self, param):
			return '%s unknown' % param
		
		def translatePath(self, param):
			return './'
	
	class xbmcaddon_foo:
		def __init__(self, id):
			self.id = id
		
		def getAddonInfo(self, param):
			if param == 'version':
				return __version__
			elif param == 'id':
				return self.id + ' by %s' % __author__
			else:
				return '%s unknown' % param
	
	class xbmcaddon_boo:
		def Addon(self, id = ''):
			if not id:
				id = os.path.basename(__file__)
			return xbmcaddon_foo(id)
	
	xbmc = xbmc_boo()
	xbmcaddon = xbmcaddon_boo()

#
# platform package usage disabled as
# cousing problems with x64 platforms
#
#try:
#	import platform
#except ImportError:
class platform_boo:
	
	def system(self):
		return os.name
	
	def release(self):
		plat = sys.platform
		return plat
			
	def python_version(self):
		ver = sys.version_info
		return '%s.%s.%s' % (ver[0], ver[1], ver[2])

platform = platform_boo()

LASTLISTFILE = os.path.join(xbmc.translatePath('special://temp/'), 'last.ShuraTVPLaylist')
LASTEPGFILE = os.path.join(xbmc.translatePath('special://temp/'), 'last.ShuraTVPEPG')
try:
	import json
except ImportError:
	xbmc.log('[SHURA.TV] module json is not available. using demjson')
	import demjson
	JSONDECODE = demjson.decode
	JSONENCODE = demjson.encode
else:
	JSONDECODE = json.loads
	JSONENCODE = json.dumps


		
class shura:
	
	def __init__(self, OTT, StreamType, ServerName, addonid = ''):
		
		if not addonid:
			addonid = os.path.basename(__file__)

		self.media_key = None
		self.OTT = OTT
		self.uid = None
		self.to = None
		self.timeshift = 0
		self.addonid = addonid
		self.last_settings = None
		self.auto_timezone = False
		self.StreamType= StreamType
		if ServerName=='UK':
			self.ServerName=1
		else:
			self.ServerName=3
		
		self.last_list = None
		self.last_epg = {}
		if os.path.isfile(LASTEPGFILE):
			l = open(LASTEPGFILE, 'rb')
			try:
				self.last_epg = JSONDECODE(l.read())
			except Exception, e:
				xbmc.log('[SHURA.TV] Error loading last epg %s' % e)
				self.last_epg = {}
			l.close()
		xbmc.log('[SHURA.TV] last epg initialized size%s' % str(len(self.last_epg)))
		
		self.supported_settings = {'media_server_id': {'name': 'media_server_id', 'language_key': 34001, 'lookup_in': 'media_servers', 'lookup': 'id', 'display': 'title'}, 'time_shift': {'name': 'time_shift', 'language_key': 34002, 'defined': [('0', '0'), ('60', '1'), ('120', '2'), ('180', '3'), ('240', '4'), ('300', '5'), ('360', '6'), ('420', '7'), ('480', '8'), ('540', '9'), ('600', '10'), ('660', '11'), ('720', '12')]}, 'time_zone': {'name': 'time_zone', 'language_key': 34003, 'defined': [('-720', '-12 GMT (New Zealand Standard Time)'), ('-660', '-11 GMT (Midway Islands Time)'), ('-600', '-10 GMT (Hawaii Standard Time)'), ('-540', '-9 GMT (Alaska Standard Time)'), ('-480', '-8 GMT (Pacific Standard Time)'), ('-420', '-7 GMT (Mountain Standard Time)'), ('-360', '-6 GMT (Central Standard Time)'), ('-300', '-5 GMT (Eastern Standard Time)'), ('-240', '-4 GMT (Puerto Rico and US Virgin Islands Time)'), ('-180', '-3 GMT (Argentina Standard Time)'), ('-120', '-2 GMT'), ('-60', '-1 GMT (Central African Time)'), ('0', '0 GMT (Greenwich Mean Time)'), ('60', '+1 GMT (European Central Time)'), ('120', '+2 GMT (Eastern European Time)'), ('180', '+3 GMT (Eastern African Time)'), ('240', '+4 GMT (Near East Time)'), ('300', '+5 GMT (Pakistan Lahore Time)'), ('360', '+6 GMT (Bangladesh Standard Time)'), ('420', '+7 GMT (Vietnam Standard Time)'), ('480', '+8 GMT (China Taiwan Time)'), ('540', '+9 GMT (Japan Standard Time)'), ('600', '+10 GMT (Australia Eastern Time)'), ('660', '+11 GMT (Solomon Standard Time)')]}}
		
		self.COLORSCHEMA = {'#000000': 'ddffffff'}	# default black looks not great on black background
		self.time_zone = 0

	def _errors_check(self, json):
		if 'error' in json:
			err = json['error']
			if 'message' in err:
				message = err['message']
				if message == None:
					message = err['code']
				xbmc.log('[SHURA.TV] ERROR: %s' % message.encode('utf8'))
	
	def getLast(self):
		if self.last_list and 'ttl' in self.last_list:
			if self.last_list['ttl'] <> now.strftime('%Y-%m-%d') or 'ott' not in self.last_list or self.last_list['ott']<>self.OTT or 'server' not in self.last_list or self.last_list['server']<>self.ServerName or 'streamType' not in self.last_list or self.last_list['streamType']<>self.StreamType:
				xbmc.log('[SHURA.TV] Last list expired')
				self.last_list = None
		if not self.last_list:
			if os.path.isfile(LASTLISTFILE):
				f = open(LASTLISTFILE, 'rb')
				try:
					self.last_list = JSONDECODE(f.read())
				except Exception, e:
					xbmc.log('[SHURA.TV] Error loading last list %s' % e)
					self.getChannelsList()
				f.close()
			else:
				self.getChannelsList()
			if self.last_list and 'ttl' in self.last_list:
				if self.last_list['ttl'] <> now.strftime('%Y-%m-%d') or 'ott' not in self.last_list or self.last_list['ott']<>self.OTT or 'server' not in self.last_list or self.last_list['server']<>self.ServerName or 'streamType' not in self.last_list or self.last_list['streamType']<>self.StreamType:
					xbmc.log('[SHURA.TV] Last list expired')
					self.getChannelsList()
		return self.last_list['channels']
	def getChannelsList(self):
		
		url = 'http://pl.tvshka.net/?uid='+self.OTT +'&srv='+str(self.ServerName)+'&type=xml'
		xbmc.log('requested url='+url)
		
		req = urllib2.Request(url, data = None)
		req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
		req.add_header('Accept', '*/*')
		req.add_header('Accept-Language', 'ru-RU')
		req.add_header('Referer',	'http://www.shura.tv')
		resp = urllib2.urlopen(req)
		response = resp.read()
		resp.close();
		
		res = []
		
		dom = parseString(response)
		#retrieve the first xml tag (<tag>data</tag>) that the parser finds with name tagName:
		#feeds = dom.getElementsByTagName('feed')
		for feed in dom.firstChild.childNodes:
			id = name = url = archive = None
			if feed.nodeName == 'feed': 
				id = feed.getAttribute('id')
				name = feed.getElementsByTagName('name')[0].firstChild.wholeText
				if self.StreamType == '1':
					#xbmc.log('url type=HLS')
					url = feed.getElementsByTagName('url_hls')[0].firstChild.data
				else:
					#xbmc.log('url type=Standard')
					url = feed.getElementsByTagName('url')[0].firstChild.data
				archive = feed.getElementsByTagName('archive')[0].firstChild.data
				#xbmc.log('archive='+archive)
				#self.getCurrentEPG(url, id)
				res.append({ 
					'id':		id,
					'name':		name,
					'url':	url,
					'archive':	archive
					})

		#xbmc.log('[SHURA.TV] Channel list %s' % response, level=xbmc.LOGDEBUG)
		#try:
			#response = JSONDECODE(response)
		#except:
			#xbmc.log('[SHURA.TV] Error.. :(')
		self.last_list = {'channels': res, 'ttl': now.strftime('%Y-%m-%d'), 'ott':self.OTT, 'server':self.ServerName, 'streamType':self.StreamType}
		f = open(LASTLISTFILE, 'wb')
		try:
			jsave = JSONENCODE(self.last_list, encoding='utf8')
			f.write(jsave)
		except Exception, e:
			xbmc.log('[SHURA.TV] Error saving last list %s' % e)
		f.close()
		return res
		
	def getCurrentEPG( self, HOST, FEED):
		host=HOST
		feed=FEED
		url = '%s%s/epg/pf.json' % (host.split('~')[0], feed)

		ua = 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)'
		postparams = None
		try:
			req = urllib2.Request(url, postparams, {'User-agent': ua, 'Connection': 'Close', 'Accept': 'application/json, text/javascript, */*', 'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'text/html;charset=utf-8'})
			#xbmc.log('[SHURA.TV] get current epg url=' + str(url))
			resstream = urllib2.urlopen(req)
			resp = resstream.read()
			#xbmc.log('[SHURA.TV] epg resp=' + str(resp))
		except Exception, e:
			xbmc.log('[SHURA.TV] Error in get response' + str(e))
		#mindex = resp.index('},{')
		#epg1 = resp[1:mindex+1]
		try:
			if resp <> None and len(resp)>0:
				resp2 = JSONDECODE(resp)
			else:
				resp2=None
		except Exception, e:
			xbmc.log('[SHURA.TV] Error in decoding json currentEPG' + str(e) +'for'+str(resp) +'len='+ str(len(resp)))
			resp2=None
		else:
			resstream.close();

		self.last_epg[str(int(FEED))]= resp2
		g = open(LASTEPGFILE, 'wb')
		try:
			jsave2 = JSONENCODE(self.last_epg)
			g.write(jsave2)
		except Exception, e:
			xbmc.log('[SHURA.TV] Error saving last epg file %s' % e)
		g.close()	
		return resp2
	
	def getLastEPG(self, HOST, FEED):
		if len(self.last_epg)==0:
			xbmc.log('[SHURA.TV] last epg empty')
			if os.path.isfile(LASTEPGFILE):
				f2 = open(LASTEPGFILE, 'rb')
				try:
					self.last_epg = JSONDECODE(f2.read, encoding='utf8')
				except Exception, e:
					xbmc.log('[SHURA.TV] Error loading last epg %s' % e)
					self.getCurrentEPG(HOST, FEED)
				f2.close()
		if not str(int(FEED)) in self.last_epg:
			xbmc.log('[SHURA.TV] last epg not found for feed='+ str(int(FEED)))
			self.getCurrentEPG(HOST, FEED)
		return self.last_epg[str(int(FEED))]

	def getWeekEPG( self, HOST, FEED):
		host=HOST
		feed=FEED
		url = '%s%s/epg/week.json' % (host.split('~')[0], feed)

		ua = 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)'
		postparams = None
		req = urllib2.Request(url, postparams, {'User-agent': ua, 'Connection': 'Close', 'Accept': 'application/json, text/javascript, */*', 'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'text/html;charset=utf-8'})

		resstream = urllib2.urlopen(req)
		resp = resstream.read()
		xbmc.log('[SHURA.TV] get week epg url=' + str(req))
		#xbmc.log('[SHURA.TV] epg resp=' + str(resp))
		#mindex = resp.index('},{')
		#epg1 = resp[1:mindex+1]
		try:
			resp2 = JSONDECODE(resp)
		except Exception, e:
			xbmc.log('[SHURA.TV] Error in decoding json weekEPG' + str(e))
			resp2=None
		else:
			resstream.close();

		#self.last_epg[str(int(FEED))]= resp2
		#g = open(LASTEPGFILE, 'wb')
		#try:
			#jsave2 = JSONENCODE(self.last_epg)
			#g.write(jsave2)
		#except Exception, e:
			#xbmc.log('[SHURA.TV] Error saving last epg file %s' % e)
		#g.close()	
		return resp2
	
	def getArchive( self, HOST, FEED):
		host=HOST
		feed=FEED
		url = '%s%s/epg/archive.json' % (host.split('~')[0], feed)

		ua = 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)'
		postparams = None
		req = urllib2.Request(url, postparams, {'User-agent': ua, 'Connection': 'Close', 'Accept': 'application/json, text/javascript, */*', 'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'text/html;charset=utf-8'})

		resstream = urllib2.urlopen(req)
		resp = resstream.read()
		resp = resp.replace('\n','')
		resp = resp.replace('\\','')
		if len(resp)>0:
			resp = JSONDECODE(resp, encoding='utf8')
		resstream.close();
		return resp
		
if __name__ == '__main__':
	foo = shura('demo', 'demo')
	foo.test()   
