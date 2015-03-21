# -*- coding: utf-8 -*
# Rodnoe.TV python class
# (c) Eugene Bond, 2010-2012
# eugene.bond@gmail.com

import urllib2
from md5 import md5
import datetime
import re, os, sys
from time import time

__author__ = 'Eugene Bond <eugene.bond@gmail.com>'
__version__ = '1.10'

IPTV_DOMAIN = 'file-teleport.com'
IPTV_API = 'http://%s/iptv/api/v1/json/%%s' % IPTV_DOMAIN


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

COOKIEJAR = None
COOKIEFILE = os.path.join(xbmc.translatePath('special://temp/'), 'cookie.%s.txt' % IPTV_DOMAIN)
LASTLISTFILE = os.path.join(xbmc.translatePath('special://temp/'), 'last.%s.json' % IPTV_DOMAIN)

try:											# Let's see if cookielib is available
	import cookielib            
except ImportError:
	xbmc.log('[Rodnoe.TV] cookielib is not available..')
	pass
else:
	COOKIEJAR = cookielib.LWPCookieJar()		# This is a subclass of FileCookieJar that has useful load and save methods

try:
	import json
except ImportError:
	xbmc.log('[Rodnoe.TV] module json is not available. using demjson')
	import demjson
	JSONDECODE = demjson.decode
	JSONENCODE = demjson.encode
else:
	JSONDECODE = json.loads
	JSONENCODE = json.dumps

class rodnoe:
	
	def __init__(self, login, password, addonid = '', SID = None, SID_NAME = None):
		
		if not addonid:
			addonid = os.path.basename(__file__)
		
		self.SID = SID
		self.SID_NAME = SID_NAME
		self.AUTH_OK = False
		
		if COOKIEJAR != None:
			if os.path.isfile(COOKIEFILE):
				COOKIEJAR.load(COOKIEFILE)
        	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(COOKIEJAR))
        	urllib2.install_opener(opener)
		
		self.media_key = None
		self.login = login
		self.password = password
		self.uid = None
		self.to = None
		self.timeshift = 0
		self.addonid = addonid
		self.last_settings = None
		self.auto_timezone = False
		
		self.last_list = None
		
		self.supported_settings = {'media_server_id': {'name': 'media_server_id', 'language_key': 34001, 'lookup_in': 'media_servers', 'lookup': 'id', 'display': 'title'}, 'time_shift': {'name': 'time_shift', 'language_key': 34002, 'defined': [('0', '0'), ('60', '1'), ('120', '2'), ('180', '3'), ('240', '4'), ('300', '5'), ('360', '6'), ('420', '7'), ('480', '8'), ('540', '9'), ('600', '10'), ('660', '11'), ('720', '12')]}, 'time_zone': {'name': 'time_zone', 'language_key': 34003, 'defined': [('-720', '-12 GMT (New Zealand Standard Time)'), ('-660', '-11 GMT (Midway Islands Time)'), ('-600', '-10 GMT (Hawaii Standard Time)'), ('-540', '-9 GMT (Alaska Standard Time)'), ('-480', '-8 GMT (Pacific Standard Time)'), ('-420', '-7 GMT (Mountain Standard Time)'), ('-360', '-6 GMT (Central Standard Time)'), ('-300', '-5 GMT (Eastern Standard Time)'), ('-240', '-4 GMT (Puerto Rico and US Virgin Islands Time)'), ('-180', '-3 GMT (Argentina Standard Time)'), ('-120', '-2 GMT'), ('-60', '-1 GMT (Central African Time)'), ('0', '0 GMT (Greenwich Mean Time)'), ('60', '+1 GMT (European Central Time)'), ('120', '+2 GMT (Eastern European Time)'), ('180', '+3 GMT (Eastern African Time)'), ('240', '+4 GMT (Near East Time)'), ('300', '+5 GMT (Pakistan Lahore Time)'), ('360', '+6 GMT (Bangladesh Standard Time)'), ('420', '+7 GMT (Vietnam Standard Time)'), ('480', '+8 GMT (China Taiwan Time)'), ('540', '+9 GMT (Japan Standard Time)'), ('600', '+10 GMT (Australia Eastern Time)'), ('660', '+11 GMT (Solomon Standard Time)')]}}
		
		self.COLORSCHEMA = {'#000000': 'ddffffff'}	# default black looks not great on black background
		self.time_zone = 0
		
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
		
		xbmc.log('[Rodnoe.TV] Requesting %s' % url);
		
		osname = '%s %s' % (platform.system(), platform.release())
		pyver = platform.python_version()
		
		__settings__ = xbmcaddon.Addon(self.addonid)
		
		isXBMC = 'XBMC'
		if getattr(xbmc, "nonXBMC", None) is not None:
			isXBMC = 'nonXBMC'
		
		ua = '%s v%s (%s %s [%s]; %s; python %s) as %s' % (__settings__.getAddonInfo('id'), __settings__.getAddonInfo('version'), isXBMC, xbmc.getInfoLabel('System.BuildVersion'), xbmc.getInfoLabel('System.ScreenMode'), osname, pyver, self.login)
		
		xbmc.log('[Rodnoe.TV] UA: %s' % ua)
		
		req = urllib2.Request(url, postparams, {'User-agent': ua, 'Connection': 'Close', 'Accept': 'application/json, text/javascript, */*', 'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/x-www-form-urlencoded'})
		
		if COOKIEJAR == None and (self.SID != None):
			req.add_header("Cookie", self.SID_NAME + "=" + self.SID + ";")
		
		rez = urllib2.urlopen(req).read()
		
		xbmc.log('[Rodnoe.TV] Got %s' % rez, level=xbmc.LOGDEBUG)
		
		
		try:
			res = JSONDECODE(rez)
		except:
			xbmc.log('[Rodnoe.TV] Error.. :(')
			
		#xbmc.log('[Rodnoe.TV] Got JSON: %s' % res)
		
		self._errors_check(res)
		
		if COOKIEJAR != None:
			xbmc.log('[Rodnoe.TV] Saving cookies: %s' % COOKIEFILE)
			COOKIEJAR.save(COOKIEFILE)
		
		return res
	
	def initTimeFix(self):
		import time
		(val, opt) = self.getSettingCurrent('time_zone')
		self.time_zone = int(val)
		if self.auto_timezone:
			xbmc.log('[Rodnoe.TV] detecting local timezone')
			if time.timezone:
				self.time_zone = time.timezone / -60
			else:
				self.time_zone = 0
		xbmc.log('[Rodnoe.TV] timezone set to %s' % self.time_zone)
		(val, opt) = self.getSettingCurrent('time_shift')
		self.timeshift = int(val)
		xbmc.log('[Rodnoe.TV] time shift set to %s' % self.timeshift)
	
	def _auth(self, user, password):
		
		md5pass = md5(md5(self.login).hexdigest() + md5(self.password).hexdigest()).hexdigest()
		
		response = self._request('login', 'login=%s&pass=%s' % (self.login, md5pass), 1)
		self.AUTH_OK = False
		
		if 'sid' in response:
			self.SID = response['sid']
			self.SID_NAME = 'sid'#response['sid_name']
			
			#if COOKIEJAR != None:
			#	auth_cookie = cookielib.Cookie(version=0, name=self.SID_NAME, value=self.SID)
			#	COOKIEJAR.set_cookie(auth_cookie)
			
			self.AUTH_OK = True
				
	def _errors_check(self, json):
		if 'error' in json:
			err = json['error']
			if 'message' in err:
				message = err['message']
				if message == None:
					message = err['code']
				xbmc.log('[Rodnoe.TV] ERROR: %s' % message.encode('utf8'))
				self.AUTH_OK = False
	
	def getLast(self):
		if self.last_list and 'ttl' in self.last_list:
			if int(self.last_list['ttl']) < time():
				xbmc.log('[Rodnoe.TV] Last list expired')
				self.last_list = None
		if not self.last_list:
			f = open(LASTLISTFILE, 'rb')
			try:
				self.last_list = JSONDECODE(f.read())
			except Exception, e:
				xbmc.log('[Rodnoe.TV] Error loading last list %s' % e)
				res = self.getChannelsList()
			else:
				xbmc.log('[Rodnoe.TV] last list loaded')
			f.close()
			
		return self.last_list['channels']
	
	def testAuth(self):
		self.AUTH_OK = True
		account = self._request('get_account_info', '')
			
		if not self.AUTH_OK:
			self._auth(self.login, self.password)
		
		return self.AUTH_OK
	
	def fixTime(self, gmt, adjust = 0):
		return gmt + adjust#+ self.time_zone * 60 
	
	def getChannelsList(self):
		self.initTimeFix()
		
		response = self._request('get_list_tv', 'with_epg=1&time_shift=%s' % (self.timeshift))
		if 'servertime' in response:
			servertime = self.fixTime(int(response['servertime'])) 
		else:
			servertime = time();
		
		res = []
		for group in response['groups']:
			color = self._resolveColor(group['color'])
			for channel in group['channels']:
				icon = re.sub('%ICON%', channel['icon'], response['icons']['w40h30'])
				epg_start = 0;
				epg_end = 0;
				epg_title = ""
				epg_info = ""
				
				if "epg" in channel and "current" in channel["epg"]:
					if 'time_shift' in channel["epg"]:
						ts_fix = int(channel["epg"]["time_shift"])
					else:
						ts_fix = 0
					prog = channel["epg"]["current"]
					if 'begin' in prog and prog['begin']:
						epg_start = self.fixTime(int(prog['begin']), ts_fix)	
					if 'end' in prog and prog['end']:
						epg_end = self.fixTime(int(prog['end']), ts_fix)
					if 'info' in prog:
						epg_info = prog['info']
					if 'title' in prog:
						epg_title = prog['title']
				
					
				duration = epg_end - epg_start
				percent = 0
				if duration > 0:
					percent = (servertime - epg_start) * 100 / duration
				
				aspect_ratio = None
				if 'aspect_ratio' in channel:
					aspect_ratio = channel['aspect_ratio']				
				
				res.append({ 
					'title':	channel['name'],
					'id':		channel['id'],
					'icon':		icon,
					'info':		epg_info,
					'subtitle':	epg_title,
					'is_video':	('is_video' in channel) and (int(channel['is_video'])),
					'have_archive': ('has_archive' in channel) and (int(channel['has_archive'])),
					'have_epg':	True,
					'percent':	percent,
					'duration':	(duration / 60),
					'is_protected': ('protected' in channel) and (int(channel['protected'])),
					#'source':	channel,
					'genre':	group['name'] or "",
					'epg_start': epg_start,
					'epg_end':	epg_end,
					'aspect_ratio': aspect_ratio,
					'servertime': servertime,
					'color':	color,
				})
		
		self.last_list = self.last_list = {'channels': res, 'ttl': time() + 600}
		f = open(LASTLISTFILE, 'wb')
		try:
			jsave = JSONENCODE(self.last_list, encoding='utf8')
			f.write(jsave)
		except Exception, e:
			xbmc.log('[Rodnoe.TV] Error saving last list %s' % e)
		else:
			xbmc.log('[Rodnoe.TV] last list stored')
		f.close()
		
		return res
	
	def _resolveColor(self, color = False):
		if color and color in self.COLORSCHEMA:
			return self.COLORSCHEMA[color]
		
		if color:
			p = re.compile('^#')
			if re.match(p, str(color)):
				return re.sub(p, 'ee', str(color))
		
		return 'eeffffff'	# almost white
	
	def getEPG(self, chid, dt = None):
		self.initTimeFix()
		
		if dt == None:
			dt = time.replace(0, 0, 0)
		
		
		response = self._request('get_epg', 'cid=%s&from_uts=%s&hours=24&time_shift=%s' % (chid, dt, self.timeshift))
		res = []
		for channel in response['channels']:
			if 'time_shift' in channel:
				ts_fix = int(channel["time_shift"])*60
			else:
				ts_fix = self.timeshift *3600
			for epg in channel['epg']:
				res.append({ 
					'title':		epg['title'],
					'time':			self.fixTime(int(epg['begin']), ts_fix),
					'uts':			int(epg['begin']),
					'info':			epg['info'],
					'is_video':		0
				})
		return res   
	
	def getCurrentInfo(self, chid):
		self.initTimeFix()
		response = self._request('get_epg', 'cid=%s&time_shift=%s' % (chid, self.timeshift))
		res = []
		
		for prg in response['channels']:
			if 'time_shift' in prg:
				ts_fix = int(prg["time_shift"])
			else:
				ts_fix = self.timeshift * 3600
			for what in ('current', 'next'):
				res.append({ 
					'title':		prg[what]['title'],
					'time':			self.fixTime(int(prg[what]['begin']), ts_fix),
					'info':			prg[what]['info'],
					'is_video':		0
				})
			
		return res
	
	def getStreamUrl(self, id, gmt = None, code = None): 
		self.initTimeFix()
		
		params = 'cid=%s' % id
		if gmt != None:
			t = int(time())
			uts = gmt# - (t - self.fixTime(t))
			params += '&uts=%s' % uts
		
		params += '&time_shift=%s' % self.timeshift
		
		if code != None:
			params += '&protect_code=%s' % code
		
		response = self._request('get_url_tv', params)
		if 'url' in response:
			return response['url']
	
	def getSettingCurrent(self, setting_name):
		setting = self.supported_settings[setting_name]
		if self.last_settings == None:
			self.last_settings = self._request('get_settings', '')
		
		if setting_name in self.last_settings:
			server_setting = self.last_settings[setting_name]
			
			oplist = []
			lookup_in = 'list'
			if 'lookup_in' in setting:
				lookup_in = setting['lookup_in']
			
			if 'defined' in setting:
				oplist = setting['defined']	
			elif lookup_in in self.last_settings:
				for set in self.last_settings[lookup_in]:
					if 'lookup' in setting:
						oplist.append((str(set[setting['lookup']]), set[setting['display']].encode('utf8')))
					else:
						oplist.append((str(set), str(set)))
		else:
			server_setting = 'Error'
			oplist = []
			
		return (server_setting, oplist)
	
	def setSettingCurrent(self, setting_name, setting_value):
		res = self._request('set', 'var=%s&val=%s' % (setting_name, setting_value))
	
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
		xbmc.log('[Rodnoe.TV] settings: %s' % res)
		return res

	
	
	def test(self):
		
		print(self.testAuth())
		
		channels = self.getChannelsList()    
		print(channels)
		for channel in channels:
			print "%s - %s  %s - %s" % (datetime.datetime.fromtimestamp(channel['epg_start']).strftime('%H:%M'), datetime.datetime.fromtimestamp(channel['epg_end']).strftime('%H:%M'), "","")#channel['title'], channel['subtitle'])
		ch_url = self.getStreamUrl(102) 

		
			
if __name__ == '__main__':
	foo = rodnoe('demo', 'demo')
	foo.test()   
