# -*- coding: utf-8 -*
# (c) Eugene Bond
# eugene.bond@gmail.com
#
# kartina tv XML/json api

import urllib2

from time import time
import datetime

import re, os, sys

__author__ = 'Eugene Bond <eugene.bond@gmail.com>'
__version__ = '2.10'

IPTV_DOMAIN = 'iptv.kartina.tv'
IPTV_API = 'http://%s/api/json/%%s' % IPTV_DOMAIN

try:
	import xbmc, xbmcaddon
except ImportError:
	class xbmc_boo:
		
		def __init__(self):
			self.nonXBMC = True
			self.LOGDEBUG = 1
			self.LOGWARNING = 2
		
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
				return self.id + '/%s (by %s) ' % (__version__, __author__)
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
		
	def processor(self):
		return ""
	
	def machine(self):
		return ""
		
	def python_version(self):
		ver = sys.version_info
		return '%s.%s.%s' % (ver[0], ver[1], ver[2])

platform = platform_boo()

COOKIEJAR = None
COOKIEFILE = os.path.join(xbmc.translatePath('special://temp/'), 'cookie.%s.txt' % IPTV_DOMAIN)
LASTLISTFILE = os.path.join(xbmc.translatePath('special://temp/'), 'last.%s.json' % IPTV_DOMAIN)

try:											# Let's see if cookielib is available
	import cookielib
except ImportError:
	xbmc.log('[KartinaTV] cookielib is not available..')
	pass
else:
	COOKIEJAR = cookielib.LWPCookieJar()		# This is a subclass of FileCookieJar that has useful load and save methods

try:
	import json
except ImportError:
	xbmc.log('[KartinaTV] module json is not available. using demjson')
	import demjson
	JSONDECODE = demjson.decode
	JSONENCODE = demjson.encode
else:
	JSONDECODE = json.loads
	JSONENCODE = json.dumps


class kartina:
	
	def __init__(self, login, password, addonid = '', SID = None, SID_NAME = None):
		self.SID = SID
		self.SID_NAME = SID_NAME
		self.channels = []
		self.channels_ttl = 0
		self.login = login
		self.password = password
		self.addonid = addonid
		self.timeshift = 0
		self.AUTH_OK = False
		
		self.last_list = None
		
		if COOKIEJAR != None:
			if os.path.isfile(COOKIEFILE):
				COOKIEJAR.load(COOKIEFILE)
        	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(COOKIEJAR))
        	urllib2.install_opener(opener)
		
		self.supported_settings = {'stream_server': {'name': 'stream_server', 'language_key': 34001, 'lookup': 'ip', 'display': 'descr'}, 'timeshift': {'name': 'timeshift', 'language_key': 34002}, 'bitrate': {'name': 'bitrate', 'language_key': 34004}, 'timezone': {'name': 'timezone', 'language_key': 34003, 'defined': [('-12', '-12 GMT (New Zealand Standard Time)'), ('-11', '-11 GMT (Midway Islands Time)'), ('-10', '-10 GMT (Hawaii Standard Time)'), ('-9', '-9 GMT (Alaska Standard Time)'), ('-8', '-8 GMT (Pacific Standard Time)'), ('-7', '-7 GMT (Mountain Standard Time)'), ('-6', '-6 GMT (Central Standard Time)'), ('-5', '-5 GMT (Eastern Standard Time)'), ('-4', '-4 GMT (Puerto Rico and US Virgin Islands Time)'), ('-3', '-3 GMT (Argentina Standard Time)'), ('-2', '-2 GMT'), ('-1', '-1 GMT (Central African Time)'), ('0', '0 GMT (Greenwich Mean Time)'), ('1', '+1 GMT (European Central Time)'), ('2', '+2 GMT (Eastern European Time)'), ('3', '+3 GMT (Eastern African Time)'), ('4', '+4 GMT (Near East Time)'), ('5', '+5 GMT (Pakistan Lahore Time)'), ('6', '+6 GMT (Bangladesh Standard Time)'), ('7', '+7 GMT (Vietnam Standard Time)'), ('8', '+8 GMT (China Taiwan Time)'), ('9', '+9 GMT (Japan Standard Time)'), ('10', '+10 GMT (Australia Eastern Time)'), ('11', '+11 GMT (Solomon Standard Time)')]}}
		
		self.COLORSCHEMA = {'Silver': 'ddefefef'}
	
	def genUa(self):
		osname = '%s %s; %s' % (platform.system(), platform.release(), platform.python_version())
		pyver = platform.python_version()
		
		__settings__ = xbmcaddon.Addon(self.addonid)
		
		isXBMC = 'XBMC'
		if getattr(xbmc, "nonXBMC", None) is not None:
			isXBMC = 'nonXBMC'
		
		#ua = '%s v%s (%s %s [%s]; %s; python %s) as %s' % (__settings__.getAddonInfo('id'), __settings__.getAddonInfo('version'), isXBMC, xbmc.getInfoLabel('System.BuildVersion'), xbmc.getInfoLabel('System.ScreenMode'), osname, pyver, self.login)
		
		ua = '%s/%s (%s; %s) %s/%s iptv/%s user/%s' % (isXBMC, xbmc.getInfoLabel('System.BuildVersion').split(" ")[0], xbmc.getInfoLabel('System.BuildVersion'), osname, __settings__.getAddonInfo('id'), __settings__.getAddonInfo('version'), __version__, self.login)
		
		xbmc.log('[Kartina.TV] UA: %s' % ua)
		return ua
	
	def _request(self, cmd, params, inauth = None):
		
		if self.AUTH_OK == False:
			if inauth == None:
				self._auth(self.login, self.password)
		
		url = IPTV_API % cmd
		if inauth:
			postparams = params
		else:
			url = url + '?' + params
			postparams = None
		
		#log.info('Requesting %s' % url)
		xbmc.log('[Kartina.TV] REQUESTING: %s' % url)
		
		ua = self.genUa()
		
		req = urllib2.Request(url, postparams, {'User-agent': ua, 'Connection': 'Close', 'Accept': 'application/json, text/javascript, */*', 'X-Requested-With': 'XMLHttpRequest'})
		
		if inauth == None and getattr(xbmc, "nonXBMC", None) is not None:
			from ga import track_page_view
			from ga import get_visitor_id
			path = cmd+"?"+params
			extra = {}
			extra['screen'] = xbmc.getInfoLabel('System.ScreenMode')
			track_page_view(get_visitor_id(self.login, None), path, ua, extra)
		
		if COOKIEJAR == None and (self.SID != None):
			req.add_header("Cookie", self.SID_NAME + "=" + self.SID + ";")
		
		rez = urllib2.urlopen(req).read()
		
		xbmc.log('[Kartina.TV] Got %s' % rez, level=xbmc.LOGDEBUG)
		
		try:
			res = JSONDECODE(rez)
		except:
			xbmc.log('[Kartina.TV] Error.. :(')
		
		#xbmc.log('[Kartina.TV] Got JSON: %s' % res)
			
		self._errors_check(res)
		
		if COOKIEJAR != None:
			xbmc.log('[Kartina.TV] Saving cookies: %s' % COOKIEFILE)
			COOKIEJAR.save(COOKIEFILE)
		
		return res
	
	def _auth(self, user, password):
		response = self._request('login', 'login=%s&pass=%s' % (user, password), 1)
		self.AUTH_OK = False
		
		if 'sid' in response:
			self.SID = response['sid']
			self.SID_NAME = response['sid_name']
			self.AUTH_OK = True
			if COOKIEJAR != None:
				try:
					cookie = cookielib.Cookie(0, self.SID_NAME, self.SID, '80', False, IPTV_DOMAIN, True, False, '/', True, False, time() + 600, False, None, None, {})
					COOKIEJAR.set_cookie(cookie)
				except:
					xbmc.log('[Kartina.TV] pipec kakaja strannaja shnyaga slu4ilas, pacany!', xbmc.LOGWARNING)
			value, options = self.getSettingCurrent('timeshift')
			self.timeshift = int(value) * 3600
		
	def getLast(self):
		if self.last_list and 'ttl' in self.last_list:
			if int(self.last_list['ttl']) < time():
				xbmc.log('[Kartina.TV] Last list expired')
				self.last_list = None
		if not self.last_list:
			f = open(LASTLISTFILE, 'rb')
			try:
				self.last_list = JSONDECODE(f.read())
			except Exception, e:
				xbmc.log('[Kartina.TV] Error loading last list %s' % e)
				res = self.getChannelsList()
			else:
				xbmc.log('[Kartina.TV] last list loaded')
			f.close()
			
		return self.last_list['channels']
	
	def _errors_check(self, json):
		if 'error' in json:
			err = json['error']
			if 'message' in err:
				xbmc.log('[Kartina.TV] ERROR: %s' % err['message'])
			if COOKIEJAR != None:
				try:
					cookie = cookielib.Cookie(0, self.SID_NAME, None, '80', False, IPTV_DOMAIN, True, False, '/', True, False, time() - 600, False, None, None, {})
					COOKIEJAR.set_cookie(cookie)
				except:
					xbmc.log('[Kartina.TV] blead, tut realno palevo nezdorovoe!', xbmc.LOGWARNING)
			self.AUTH_OK = False
	
	
	def getChannelsList(self):
		if self.channels_ttl < time():
			jsonChannels = self._request('channel_list', '')

			if 'servertime' in jsonChannels:
				servertime = int(jsonChannels['servertime']); 
			else:
				servertime = time();

			self.channels = []
			
			for channelGroup in jsonChannels['groups']:
				color = self._resolveColor(channelGroup['color'])
				for channel in channelGroup['channels']:
					programm = ""
					if 'epg_progname' in channel:
						programm = channel['epg_progname']
					programm += "\n"
					prog, desc = programm.split("\n", 1)
					
					epg_start = 0;
					epg_end = 0;
					if 'epg_start' in channel:
						epg_start = int(channel['epg_start'])

					if 'epg_end' in channel:
						epg_end = int(channel['epg_end'])

					
					duration = epg_end - epg_start
					percent = 0
					if duration > 0 :
						percent = (servertime - epg_start) * 100 / duration
					
					if 'icon' in channel:
						icon = channel['icon']
						if icon[:4] != 'http':
							icon = 'http://%s%s' % (IPTV_DOMAIN, icon)
					else:
						icon = ''
					
					channel2add = { 
							'title':	channel['name'],
							'id':		channel['id'],
							'icon':		icon,
							'info':		desc,
							'subtitle':	prog,
							'is_video':	('is_video' in channel) and (channel['is_video']),
							'have_archive': ('have_archive' in channel) and channel['have_archive'],
							'have_epg':	('epg_start' in channel) and (channel['epg_start']),
							'percent':	percent,
							'duration':	(duration / 60),
							'is_protected': ('protected' in channel) and (channel['protected']),
							'source':	channel,
							'genre':	channelGroup['name'],
							'epg_start': epg_start,
							'epg_end':	epg_end,
							'servertime': servertime,
							'color':	color,
						}
					self.channels.append(channel2add)
				
			self.channels_ttl = time() + 600
			
			self.last_list = {'channels': self.channels, 'ttl': time() + 600}
			f = open(LASTLISTFILE, 'wb')
			try:
				jsave = JSONENCODE(self.last_list, encoding='utf8')
				f.write(jsave)
			except Exception, e:
				xbmc.log('[Kartina.TV] Error saving last list %s' % e)
			else:
				xbmc.log('[Kartina.TV] last list stored')
			f.close()
			
		return self.channels
	
	def _resolveColor(self, color = False):
		if color and color in self.COLORSCHEMA:
			return self.COLORSCHEMA[color]
		
		if color:
			p = re.compile('^#')
			if re.match(p, str(color)):
				return re.sub(p, 'ee', str(color))
		
		return 'eeffffff'	# almost white
	
	def getStreamUrl(self, id, gmt = None, code = None): 
		params = 'cid=%s' % id
		if gmt != None:
			params += '&gmt=%s' % gmt
		
		if code != None:
			params += '&protect_code=%s' % code
		
		response = self._request('get_url', params)
		url = response['url']
		
		url = re.sub('http/ts(.*?)\s(.*)', 'http\\1', url)
		
		return url

	def getEPG(self, id, day = None):
		if not day:
			day = datetime.date.today().strftime('%d%m%y')
			
		params = 'cid=%s&day=%s' % (id, day)
		result = self._request('epg', params)
		res = []
		for epg in result['epg']:
			programm = ""
			if 'progname' in epg:
				programm = epg['progname']
			programm += "\n"
			prog, desc = programm.split("\n", 1)
			
			res.append({ 
				'title':		prog,
				'time':			int(epg['ut_start']),	#  + self.timeshift
				'info':			desc,
				'is_video':		0,
				'source':		epg
			})

		return res
	
	def getCurrentInfo(self, chid):
		response = self._request('epg_next', 'cid=%s' % chid)
		res = []
		
		if 'epg' in response and response['epg'] != False:
			epg = response['epg'][0:2]
			for prg in epg:
				programm = ""
				if 'progname' in prg:
					programm = prg['progname']
				programm += "\n"
				prog, desc = programm.split("\n", 1)
				res.append({ 
					'title':		prog,
					'time':			prg['ts'],
					'info':			desc,
					'is_video':		0
				})
			
		return res
	
	def getVideoList(self, mode, page, pagesize=15, search={}):
		if pagesize == 'all':
			pagesize = 999
			page = 1
			params = 'type=%s&nums=%s&page=%s' % (mode, 1, 1)
			result = self._request('vod_list', params)
			if 'total' in result:
				pagesize = result['total'] 
			xbmc.log('[Kartina.TV] pagesize set to %s to reflect "all" param' % pagesize)
		
		params = 'type=%s&nums=%s&page=%s' % (mode, pagesize, page)
		result = self._request('vod_list', params)
		res = []
		for vod in result['rows']:
			if 'poster' in vod:
				icon = vod['poster']
				if icon[:4] != 'http':
					icon = 'http://%s%s' % (IPTV_DOMAIN, icon)
			else:
				icon = ''
			xbmc.log('[Kartina.TV] VOD item: %s' % vod, level=xbmc.LOGDEBUG)
			res.append({
				'title':		vod['name'],
				'info':			vod['description'],
				'is_video':		1,
				'id':			vod['id'],
				'genre':		vod['genre_str'],
				'icon':			icon,
				'source':		vod
			})
			
		return res
	
	def getVideoInfo(self, id):
		params = 'id=%s' % id
		result = self._request('vod_info', params)
		
		return result['film']
	
	
	def getVideoUrl(self, id):
		params = 'fileid=%s' % id
		response = self._request('vod_geturl', params)
		url = response['url']
		
		url, junk = url.split(" ",1)
		
		return url
	
	def getSettingCurrent(self, setting_name):
		setting = self.supported_settings[setting_name]
		res = self._request('settings', 'var=%s' % setting['name'])
		server_setting = res['settings']
		
		oplist = []
		if 'defined' in setting:
			oplist = setting['defined']	
		elif 'list' in server_setting:
			for set in server_setting['list']:
				if 'lookup' in setting:
					oplist.append((str(set[setting['lookup']]), str(set[setting['display']])))
				else:
					oplist.append((str(set), str(set)))
			
		return (server_setting['value'], oplist)
	
	def setSettingCurrent(self, setting_name, setting_value):
		res = self._request('settings_set', 'var=%s&val=%s' % (setting_name, setting_value))
	
	def getSettingsList(self):
		
		res = []
		for set in self.supported_settings:
			setting = self.supported_settings[set]
			value, options = self.getSettingCurrent(set)
			res.append({
				'name':			setting['name'],
				'language_key':	setting['language_key'],
				'value':		value,
				'options':		options
			})
		xbmc.log('[Kartina.TV] settings: %s' % res)
		return res
	
	
	def test(self):
		#print(self.getChannelsList())
		print(self.getCurrentInfo(7))
	
	
	def testAuth(self):
		self.AUTH_OK = True
		account = self._request('account', '')
			
		if not self.AUTH_OK:
			self._auth(self.login, self.password)
		
		if self.AUTH_OK:
			value, options = self.getSettingCurrent('timeshift')
			self.timeshift = int(value) * 3600
		
		return self.AUTH_OK
		
if __name__ == '__main__':
	foo = kartina('148', '841')
	foo.test()