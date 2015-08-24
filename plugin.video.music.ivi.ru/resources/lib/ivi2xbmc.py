#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#     Writer (c) 2012, Nevenkin A.V., E-mail: nuismons@gmail.com
#   This Program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2, or (at your option)
#   any later version.
#
#   This Program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; see the file COPYING.  If not, write to
#   the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#   http://www.gnu.org/licenses/gpl.html

import urllib
import urllib2
import sys
import os
import xbmcplugin
import xbmcgui
import xbmc
import xbmcaddon
import time
import random
import threading

from urllib import unquote, quote, quote_plus
try:
	from hashlib import md5
except:
	from md5 import md5

adv_file = xbmc.translatePath('special://temp/'+ 'settings.m.ivi.adv')

Addon = xbmcaddon.Addon(id='plugin.video.music.ivi.ru')
language = Addon.getLocalizedString
addon_icon    = Addon.getAddonInfo('icon')
addon_fanart  = Addon.getAddonInfo('fanart')
addon_path    = Addon.getAddonInfo('path')
addon_type    = Addon.getAddonInfo('type')
addon_id      = Addon.getAddonInfo('id')
addon_author  = Addon.getAddonInfo('author')
addon_name    = Addon.getAddonInfo('name')
addon_version = Addon.getAddonInfo('version')

hos = int(sys.argv[1])
fhos = sys.argv[0]
HOST='http://music.ivi.ru/deviceapi/'
LIMIT=30
siteid=190
try:
	import platform
	xbmcver=xbmc.getInfoLabel( "System.BuildVersion" ).replace(' ','_').replace(':','_')
	UA = 'XBMC/%s (%s; U; %s %s %s %s) %s/%s XBMC/%s'% (xbmcver,platform.system(),platform.system(),platform.release(), platform.version(), platform.machine(),addon_id,addon_version,xbmcver)
except:
	UA = 'XBMC/Unknown %s/%s/%s' % (urllib.quote_plus(addon_author), addon_version, urllib.quote_plus(addon_name))

def get_len():
	try:
		if Addon.getSetting("cnt_v") == '0': return 10
		if Addon.getSetting("cnt_v") == '1': return 25
		if Addon.getSetting("cnt_v") == '2': return 50
		if Addon.getSetting("cnt_v") == '3': return 75
		if Addon.getSetting("cnt_v") == '4': return 100
		return 50
	except: return 50
LIMIT=get_len()


VERSION = '4.3as'
DOMAIN = '131896016'
GATrack='UA-30985824-1'

if not Addon.getSetting('GAcookie'):
	from random import randint
	GAcookie ="__utma%3D"+DOMAIN+"."+str(random.randint(0, 0x7fffffff))+"."+str(random.randint(0, 0x7fffffff))+"."+str(int(time.time()))+"."+str(int(time.time()))+".1%3B"
	Addon.setSetting('GAcookie', GAcookie)
if not Addon.getSetting('uniq_id'):
	from random import randint
	uniq_id=random.random()*time.time()
	Addon.setSetting('uniq_id', str(uniq_id))

GAcookie =Addon.getSetting('GAcookie')
uniq_id=Addon.getSetting('uniq_id')
session=Addon.getSetting("session")



def send_request_to_google_analytics(utm_url, ua):

	try:

		req = urllib2.Request(utm_url, None, {'User-Agent':UA} )
		response = urllib2.urlopen(req).read()
		print 'send ga'
	except:
		ShowMessage('music.ivi.ru', "GA fail: %s" % utm_url, 2000)
	#response = ''
	return response

def track_page_view(path,nevent='', tevent='',UATRACK='UA-30985824-7'):
	track_page_view2(path,nevent,tevent,UATRACK)
	track_page_view2(path,nevent,tevent,UATRACK="UA-11561457-41")
	
def track_page_view2(path,nevent='', tevent='',UATRACK='UA-30985824-7'):
	domain = DOMAIN
	document_path = unquote(path)
	utm_gif_location = "http://www.google-analytics.com/__utm.gif"
	extra = {}
	extra['screen'] = xbmc.getInfoLabel('System.ScreenMode')

	md5String = md5(str(uniq_id)).hexdigest()
	gvid="0x" + md5String[:16]
	utm_url = utm_gif_location + "?" + \
		"utmwv=" + VERSION + \
		"&utmn=" + get_random_number() + \
		"&utmsr=" + quote(extra.get("screen", "")) + \
		"&utmt=" + nevent + \
		"&utme=" + tevent +\
		"&utmhn=localhost" + \
		"&utmr=" + quote('-') + \
		"&utmp=" + quote(document_path) + \
		"&utmac=" + UATRACK + \
		"&utmvid=" + gvid + \
		"&utmcc="+ GAcookie
	return send_request_to_google_analytics(utm_url, UA)


import  json

def get_random_number():
	return str(random.randint(0, 0x7fffffff))

def construct_request(params):
	return '%s?%s' % (fhos, urllib.urlencode(params))

def ShowMessage(heading, message, times = 3000, pics = addon_icon):
	try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading.encode('utf-8'), message.encode('utf-8'), times, pics.encode('utf-8')))
	except Exception, e:
		print( '[%s]: ShowMessage: Transcoding UTF-8 failed [%s]' % (addon_id, e), 2 )
		try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, pics))
		except Exception, e:
			print( '[%s]: ShowMessage: exec failed [%s]' % (addon_id, e), 3 )

def GET(target, post=None):
	#print target
	try:
		req = urllib2.Request(url = target, data = post, headers = {'User-Agent':UA})
		resp = urllib2.urlopen(req)
		CE = resp.headers.get('content-encoding')
		http = resp.read()
		resp.close()
		return http
	except Exception, e:
		print( '[%s]: GET EXCEPT [%s]' % (addon_id, e), 4 )
		ShowMessage('HTTP ERROR', e, 5000)

def genre2name(gid):
	gdf = open(genres_dat_file, 'r')
	genres_data = json.loads(gdf.read())
	gdf.close()
	try:
		for n in genres_data:
			if int(n.split(';')[0]) == (gid):
				reti=n.split(';')[1]
		return reti
	except: return None

def adv_send(path,post):
	try:
		#print path
		req = urllib2.Request(path,post)
		req.add_header('Accept', 'text/plain')
		req.add_header('Content-Type','application/x-www-form-urlencoded')
		f = urllib2.urlopen(req)
		js = f.read()
	except: pass
	
class dig_player(xbmc.Player):

	def __init__( self, *args, **kwargs ):
		self.init()

	def init(self):
		self.mustEND=0
		self.active = None
		self.api_url = 'http://api.digitalaccess.ru/api/json/'
		self.log_url = 'http://api.digitalaccess.ru'
		self.sID='s190'
		self.vID=7029
		self.content=None
		self.ads_file=None
		self.state='pre_roll'
		self.watchid=None
		self.ads=[]
		self.midroll = []
		self.PosterImage = None
		self.main_item = None
		self.title=None
		self.lastad=0
		self.paused=None
		self.adv_file=None
		self.resume_timer=None
		self.content_start=None
		self.pre_end=None
		self.adstart_timer=None
		self.advid=None
		self.min=0
		self.ended=None
		self.send_ads=[]
		self.start_timer=None
		self.show=True
		self.playing=False
		self.strt_file=None

	def report_ads(self, curr_ads):
		
		json1 = self.POSTAPI({'method':'da.adv.watched', 'params':[self.vID, curr_ads['id'], {'contentid':self.vID,'site':self.sID, 'watchid':str(self.watchid),'advid':curr_ads['id'],'uid':uniq_id, "advwatchid":str(self.advwatchid)} ]})
		links= curr_ads['px_audit']
		
		if links:
			if len(links)<8:
				for n in links:
					GET(n)
			else: GET(links)


	def POSTAPI(self, post):
		#print post
		try:
			req = urllib2.Request(self.api_url)
			req.add_header('User-Agent', UA)
			f = urllib2.urlopen(req, json.dumps(post))
			js = json.loads(f.read())
			f.close()
			return js
		except: return None
		try:
			e_m = js['error']
			ShowMessage('ERROR %s SERVER %s' % (e_m['code'], js['server_name']), e_m['message'], times = 15000, pics = addon_icon)
			return None
		except:
			return js

	def getData    (self, vID):
		#self.sID='s190'
		self.vID=vID
		self.watchid='%s_%s_%s'%(self.vID,uniq_id,str(int(time.time()*1000)))
		json0 = self.POSTAPI({'method':'da.content.get', 'params':[self.vID, {'contentid':self.vID,'watchid':self.watchid,'site':self.sID, 'uid':uniq_id} ]})
		#print json0
		try:
			vc = json0['result']
			self.content = self.find_best(vc)
		except: vc=None

		if self.content and vc:

			http = GET(HOST+'video/?subsite=190&id=%s' % self.vID)
			#print http
			if http:
				data = json.loads(http)['result']
				self.PosterImage = getthumb(data)
				self.main_item = xbmcgui.ListItem(data['title'], iconImage = self.PosterImage, thumbnailImage = self.PosterImage)
				self.title=data['title']
				i = xbmcgui.ListItem(self.title, iconImage = self.PosterImage, thumbnailImage = self.PosterImage)
				iad = xbmcgui.ListItem(language(30011), iconImage = self.PosterImage, thumbnailImage = self.PosterImage)
			try:    self.content_percent_to_mark = int(vc['percent_to_mark'])
			except: self.content_percent_to_mark = 0
			try:    self.GA_id = int(vc['google_analytics_id'])
			except: self.GA_id = None
			try:    self.tns_id = int(vc['tns_id'])
			except: self.tns_id = None
			self.title=vc['title']
			try:    self.credits_begin_time = int(vc['credits_begin_time'])
			except: self.credits_begin_time = -1
			if self.credits_begin_time==0: self.credits_begin_time=-1
			try:    self.midroll = vc['midroll']
			except: self.midroll = []
			flname=self.content
			fio=i
			ind=0
			pre=self.getAds('preroll')
			#print pre
			if pre:
				self.adv_file=pre['url']
				self.advid=pre['id']
				self.state='preroll'
				self.send_ads=pre
				flname=self.adv_file
				fio=iad
			else: self.state='play'
			
			track_page_view(str(vID),'event','5(Video*Start)')
			#track_page_view('','event','5(Video*Videostart)',UATRACK=GATrack)
			self.active=True
			json1 = self.POSTAPI({'params':[self.vID, {'contentid':self.vID,'site':self.sID, 'watchid':self.watchid ,'uid':uniq_id} ],'method':'da.content.watched' })
			self.playing=False
			self.strt_file=flname

	def play_loop(self):

		self.last_ads_time=0
		added=None
		self.active=True
		self.min=0
		last=0
		self.Time = 0
		self.TotalTime = 9999
		self.percent = 0
		timeout=90
		while self.active==True:
			if self.playing:

				try:
					self.Time = int(self.getTime())
					self.TotalTime = self.getTotalTime()
					self.percent = (100 * self.Time) / self.TotalTime
				except:
					self.TotalTime = 999999
					self.Time = 0
					self.percent = 0
				if not self.paused and last!=self.Time:
					last=self.Time
					if self.state=='play' and self.content_start:
						seconds=int(time.time()-self.content_start)
						if seconds<=60:
							if self.state=='play' and self.content_start:
								self.sendstat('http://api.digitalaccess.ru/logger/content/time/',{'contentid':self.vID,'watchid':self.watchid,'fromstart':int(self.Time),'seconds':seconds})
						if seconds>=60: self.min=self.min+1
						if self.min>=60:
							if self.state=='play' and self.content_start:
								self.sendstat('http://api.digitalaccess.ru/logger/content/time/',{'contentid':self.vID,'watchid':self.watchid,'fromstart':int(self.Time),'seconds':seconds})
								self.min=0
					if self.state!='play' and self.adstart_timer:
						self.sendstat('http://api.digitalaccess.ru/logger/adv/time/',{'watchid':quote(self.watchid),'advwatchid':quote(self.advwatchid),'seconds':int(time.time()-self.adstart_timer)})
					if self.state!='play' and not self.ended:

						if self.Time>=int(self.TotalTime-1.3) and self.Time>5 and not added:
							if self.state=='preroll':
								self.pre_end=time.time()
							i = xbmcgui.ListItem(self.title, iconImage = self.PosterImage, thumbnailImage = self.PosterImage)
							i.setProperty('StartOffset', str(self.resume_timer))
							added=True
							f = open(adv_file, 'w')
							last_ad=str(int(time.time()))
							f.write(last_ad)
							f.close()
							self.lastad=last_ad
							self.state='play'
							self.playing=False
							self.play(self.content,i)

			  




			if not self.isPlaying():
				timeout=timeout-1
				if timeout==0: self.active=False
			else: timeout=90
			if self.mustEND==1:
				self.active=False
				break
			if self.TotalTime-self.Time>5 or self.state=='preroll':
				self.sleep(300)
			else: self.sleep(100)

	def onPlayBackEnded( self ):

		self.show=False
		self.active=False
		self.mustEND=1
		#track_page_view('','event','5(Video*VideoEnded)',UATRACK=GATrack)
	def onPlayBackStopped(self):

		self.active=False
		self.show=False
		self.mustEND=1
		#track_page_view('','event','5(Video*VideoStopped)',UATRACK=GATrack)
	def onPlayBackPaused( self ):
		self.paused=1
		
	def onPlayBackResumed( self ):
		self.paused=False

	def onPlayBackStarted( self ):
		self.playing=True
		if self.state=='play':
			if not self.content_start:

				self.content_start=time.time()
				self.sendstat('http://api.digitalaccess.ru/logger/mediainfo/speed/',{'watchid':self.watchid,'speed':self.content_start-self.pre_end})
		else:

			try:

				self.adstart_timer=time.time()
				self.advwatchid='%s_%s'%(self.advid,str(int(self.adstart_timer*1000)))
				json1 = self.POSTAPI({'method':'da.adv.got', 'params':[self.vID, self.advid, {'contentid':self.vID,'site':self.sID, 'watchid':str(self.watchid),'advid':self.advid,'uid':uniq_id, "advwatchid":str(self.advwatchid)} ]})
				self.report_ads(self.send_ads)
			except: pass
	def getAds(self, phase):
		json1 = self.POSTAPI({'method':'da.adv.get', 'params':[self.vID, {'contentid':self.vID,'site':self.sID, 'watchid':self.watchid, 'last_adv':(int(int(time.time())-int(self.lastad))), 'uid':uniq_id},phase]} )

		if json1:
			try:
				ad=json1['result'][0]
				ad_file = self.find_best(ad)
				if ad_file:
					adrow = {'url': ad_file, 'id': ad['id'], 'title': ad['title'].encode('utf-8'), 'px_audit': ad['px_audit'],
					'duration': ad['duration'], 'percent_to_mark': int(ad['percent_to_mark'])-1, 'save_show': ad['save_show']}

			except:
				adrow = None
				pass
		return adrow

	def sendstat(self,path,post):
		post=urllib.urlencode(post).replace('.','%2E').replace('_','%5F')
		t = threading.Thread(target=adv_send, args=(path,post))
		t.daemon = True
		t.start()
		
	def find_best(self, data):
		play_file = None
		if not play_file:
			for vcfl in data['files']:
				if vcfl['content_format'] == 'MP4-hi': play_file = vcfl['url']
		if not play_file:
			for vcfl in data['files']:
				if vcfl['content_format'] == 'FLV-hi': play_file = vcfl['url']
		if not play_file:
			for vcfl in data['files']:
				if vcfl['content_format'] == 'MP4-lo': play_file = vcfl['url']
		if not play_file:
			for vcfl in data['files']:
				if vcfl['content_format'] == 'FLV-lo': play_file = vcfl['url']
		return play_file

	def sleep(self, s):
		xbmc.sleep(s)
	def __del__(self):
		self.active=False

def show_info():
	xbmc.executebuiltin('ActivateWindow(movieinformation)')


def playid(params, play=False):


	try:
		f = open(adv_file, 'r')
		last_ad=f.readline()

	except:
		f = open(adv_file, 'w')
		last_ad=str(int(time.time()))
		f.write(last_ad)
		f.close()
	aplay=dig_player()
	aplay.init()
	aplay.lastad=last_ad
	aplay.pre_end=time.time()
	aplay.getData(params['id'])
	if aplay.strt_file!=None:
		item = xbmcgui.ListItem(path=aplay.strt_file)
		xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
		aplay.play_loop()
		aplay.stop
		aplay.active=False
	else:
		ShowMessage('music.ivi.ru', language(30010), 2000)
		#track_page_view(str(params['id']),'event','5(Video*VideoForbidden)',UATRACK=GATrack)
		aplay.stop

def read_genre(params):
	try:
		offset=int(params['offset'])
	except: offset=0
	http = GET(params['url']+'&limit=%s&offset=%s&sort=%s'%(LIMIT,offset,get_sort()))
	jsdata = json.loads(http)
	cnt=0
	for video in jsdata['result']:
		li = xbmcgui.ListItem(video['artist']+' - '+video['title'], iconImage = getthumb(video), thumbnailImage = getthumb(video))
		li.setProperty('fanart_image', addon_fanart)

		try: li.setInfo(type='video', infoLabels = vdata['info'])
		except: pass
		if session: li.addContextMenuItems([(language(30060), 'XBMC.RunPlugin(%s?func=add_to_playlist&id=%s)' % (sys.argv[0],  video['id']),)])
		u=sys.argv[0]+"?func=playid&id="+str(video['id'])
		li.setProperty('IsPlayable', 'true')
		info={}
		info['plot']=' '
		li.setInfo(type='video',infoLabels = info)
		li.setProperty('fanart_image', addon_fanart)
		xbmcplugin.addDirectoryItem(hos, url=u, listitem= li)
		cnt=cnt+1
	track_page_view('genre/%s'%params['genre'])
	if cnt==LIMIT:
		li = xbmcgui.ListItem(language(30020), iconImage = addon_icon, thumbnailImage = addon_icon)
		uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'read_genre','url':params['url'], 'genre': params['genre'],'offset':offset+LIMIT}))
		xbmcplugin.addDirectoryItem(hos, uri, li, True)
	xbmcplugin.endOfDirectory(hos)
	
def cust(params):
	try:
		offset=int(params['offset'])
	except: offset=0
	http = GET(params['url']+'/?subsite=s190&offset=%s&limit=%s'%(offset,LIMIT))
	jsdata = json.loads(http)
	cnt=0
	try:
		for categoryes in jsdata['result']:
			if params['url']==HOST+'artists': li = xbmcgui.ListItem(categoryes['title'], iconImage = getthumb(categoryes), thumbnailImage = getthumb(categoryes))
			else: li = xbmcgui.ListItem(categoryes['title'], iconImage = addon_icon, thumbnailImage = addon_icon)
			li.setProperty('fanart_image', addon_fanart)
			if params['url']==HOST+'genres':
				uri = construct_request({
					'func': 'read_genre',
					'genre': categoryes['id'],
					'url':HOST+'videos/?genre_id=%s'%categoryes['id']
				})
				
			if params['url']==HOST+'artists':
				uri = construct_request({
					'func': 'search',
					'genre': categoryes['id'],
					'url':HOST+'search/?subsite=190&type=videos&q="%s"'%(categoryes['title']).encode('utf-8').replace(' ','%20')
				})
				
			xbmcplugin.addDirectoryItem(hos, uri, li, True)
			cnt=cnt+1
	except: pass
	if params['url']==HOST+'genres': track_page_view('genres')
	else: track_page_view('artists')
	if cnt==LIMIT:
		addMainLink(language(30020),{'func':'cust', 'url': params['url'],'offset':offset+LIMIT},True)
	xbmcplugin.endOfDirectory(hos)
def search(params):
	try:
		track_page_view('artists/%s'%params['genre'])
	except: pass
	try:
		offset=int(params['offset'])
	except: offset=0
	link=params['url']+'&subsite=190&offset=%s&limit=%s'%(offset,LIMIT)
	http = GET(link)
	jsdata = json.loads(http)
	#print jsdata
	try:
		cnt=0
		for video in jsdata['result']['videos']:
			li = xbmcgui.ListItem(video['artist']+' - '+video['title'], iconImage = getthumb(video), thumbnailImage = getthumb(video))
			li.setProperty('fanart_image', addon_fanart)

			try: li.setInfo(type='video', infoLabels = vdata['info'])
			except: pass
			u=sys.argv[0]+"?func=playid&id="+str(video['id'])
			if session: li.addContextMenuItems([(language(30060), 'XBMC.RunPlugin(%s?func=add_to_playlist&id=%s)' % (sys.argv[0],  video['id']),)])
			li.setProperty('IsPlayable', 'true')
			info={}
			info['plot']=' '
			li.setInfo(type='video',infoLabels = info)
			li.setProperty('fanart_image', addon_fanart)
			xbmcplugin.addDirectoryItem(hos, url=u, listitem= li)
			cnt=cnt+1
		#print cnt
		if cnt==LIMIT:
			addMainLink(language(30020),{'func':'search','url':params['url'], 'offset':offset+LIMIT},True)
		xbmcplugin.endOfDirectory(hos)
	except: 
		ShowMessage('music.ivi.ru', language(30022), 2000)
		
def addMainLink(title,param, folder=True, img=addon_icon):
	li = xbmcgui.ListItem(title, iconImage = img, thumbnailImage = img)
	uri = construct_request(param)
	li.setProperty('fanart_image', addon_fanart)
	xbmcplugin.addDirectoryItem(hos, uri, li, folder)
		
def main_screen(params):

	mail=Addon.getSetting("username")
	passw=Addon.getSetting("password")

	addMainLink(language(30040),{'func': 'promo','url': HOST+'promo'})
	addMainLink(language(30041),{'func': 'cust', 'url': HOST+'genres'})
	addMainLink(language(30042),{'func': 'cust','url': HOST+'artists'})
	addMainLink(language(30043),{'func': 'edi_playlists','mode': '0'})
	addMainLink(language(30044),{'func': 'edi_playlists','mode': '1'})

	http=GET(HOST+'login/?provider=ivi&email=%s&password=%s'%(mail,passw))
	
	try:
		data=json.loads(http)
		session= data['result']['session']
		Addon.setSetting("session",session)
		Addon.setSetting("user",data['result']['nick_name'])
	except:
		Addon.setSetting("session","")
		Addon.setSetting("user","")
		
	session=Addon.getSetting("session")
		
	if session:	addMainLink(language(30045),{'func': 'ivi_playlists'})
	addMainLink(language(30046),{'func': 'run_search'})
	if session: addMainLink(language(30000),{'func': 'run_settings'},False)
	else: addMainLink(language(30047),{'func': 'run_settings'},False)
	
	xbmcplugin.endOfDirectory(hos)
	
def edi_playlists(params):
	http=GET(HOST+'editorschannels/')
	data=json.loads(http)
	
	if params['mode']=='0': 
		track_page_view('artists favorites')
		for pl in data['result']['like']:
			img=getthumb(pl)
			addMainLink(pl['title'],{'func': 'run_pl','url': HOST+'playlist/','pl':pl['id']},True,img)
			
	if params['mode']=='1':
		track_page_view('editors channel')
		for pl in data['result']['recommend']:
			img=getthumb(pl)
			addMainLink(pl['title'],{'func': 'run_pl','url': HOST+'playlist/','pl':pl['id']},True,img)
	
	xbmcplugin.endOfDirectory(hos)
	
def ivi_playlists(params):
	track_page_view('userplaylists')
	http=GET(HOST+'userplaylists/?session=%s'%(session))
	data=json.loads(http)
	try:
		
		for pl in data['result']:
			img=getthumb(pl)
			li = xbmcgui.ListItem(pl['title'], iconImage = img, thumbnailImage = img)
			if session: li.addContextMenuItems([(language(30062), 'XBMC.RunPlugin(%s?func=del_playlist&id=%s)' % (sys.argv[0],  pl['id'] ),)])
			li.setProperty('fanart_image', addon_fanart)
			uri = construct_request({
				'func': 'run_pl',
				'url': HOST+'userplaylist/',
				'pl':pl['id']
			})
			xbmcplugin.addDirectoryItem(hos, uri, li, True)
		
	except: pass
	xbmcplugin.endOfDirectory(hos)
	
def run_pl(params):

	http=GET(params['url']+'?id=%s&session=%s'%(params['pl'],session))
	#print http
	data=json.loads(http)
	ind=0
	for pl in data['result']:
		try:
			img=getthumb(pl)
			li = xbmcgui.ListItem(pl['artist']+' - '+pl['title'], iconImage = img, thumbnailImage = img)
			li.setProperty('IsPlayable', 'true')
			if session and params['url']==HOST+'userplaylist/': li.addContextMenuItems([(language(30060), 'XBMC.RunPlugin(%s?func=add_to_playlist&id=%s)' % (sys.argv[0],  pl['id']),),(language(30061), 'XBMC.RunPlugin(%s?func=del_from_playlist&id=%s&pl=%s&url=%s&ind=%s)' % (sys.argv[0],  pl['id'],params['pl'],quote(params['url']),str(ind) ),)])
			if session and params['url']!=HOST+'userplaylist/': li.addContextMenuItems([(language(30060), 'XBMC.RunPlugin(%s?func=add_to_playlist&id=%s)' % (sys.argv[0],  pl['id']),)])
			info={}
			info['plot']=' '
			li.setInfo(type='video',infoLabels = info)
			li.setProperty('fanart_image', addon_fanart)
			u=sys.argv[0]+"?func=playid&id="+str(pl['id'])
			xbmcplugin.addDirectoryItem(hos, url=u, listitem=li)
			ind=ind+1
		except: pass
	#print data
	xbmcplugin.endOfDirectory(hos)
def run_settings(params):

	Addon.openSettings()
	xbmc.executebuiltin('Container.Update(%s?func=main_screen)' % sys.argv[0])
	
def add_to_playlist(params):
	playlists=[]
	items=[]
	http=GET(HOST+'userplaylists/?session=%s'%(session))
	data=json.loads(http)
	try:
		for pl in data['result']:
			playlists.append(pl['title'])
			items.append(pl['id'])
	except: pass
	playlists.append(language(30064))
	dialog = xbmcgui.Dialog()
	ind=dialog.select(language(30063), playlists)
	if ind<len(items):
		http=GET(HOST+'addvideotoplaylist/?session=%s&id=%s&video_id=%s'%(session,items[ind].encode('utf-8'),params['id']))
		data=json.loads(http)
	else:
		kbd = xbmc.Keyboard()
		kbd.setDefault('')
		kbd.setHeading(language(30064))
		kbd.doModal()
		out=''
		if kbd.isConfirmed():
			out = kbd.getText()
		http=GET(HOST+'addplaylist/?session=%s&title=%s&video_id=%s'%(session,out,params['id']))
		playlists.append(out)
	ShowMessage('music.ivi.ru', language(30065), 2000)
	
def del_playlist(params):
	http=GET(HOST+'deleteplaylist/?id=%s&session=%s'%(params['id'],session))
	xbmc.executebuiltin('Container.Refresh(%s?func=ivi_playlists)'%sys.argv[0])
	ShowMessage('music.ivi.ru', language(30067), 2000)
	
def del_from_playlist(params):
	videos=[]
	http=GET(HOST+'userplaylist/?id=%s&session=%s'%(params['pl'],session))
	data=json.loads(http)
	ind=0
	for pl in data['result']:
		try: 
			if int(params['ind'])!=int(ind):
				videos.append(str(pl['id']))
		except: pass
		ind=ind+1

	asd='&videos[]='.join(videos)
	if ind>1: http=GET(HOST+'updateplaylist/?session=%s&id=%s&videos[]=%s'%(session,params['pl'],asd))
	else: http=GET(HOST+'updateplaylist/?session=%s&id=%s&videos='%(session,params['pl']))
	xbmc.executebuiltin('Container.Refresh(%s?func=run_pl&url=%s&pl=%s)' % (sys.argv[0],params['url'],params['pl']))
	ShowMessage('music.ivi.ru', language(30066), 2000)

def promo(params):                     # показ промо контента
	track_page_view('promo')
	http = GET(HOST+'promo/?offset=0&limit=%s'%LIMIT)
	if http == None: return False
	jsdata = json.loads(http)
	if jsdata:
		for video in jsdata['result']:
			li = xbmcgui.ListItem(video['artist']+' - '+video['title'], iconImage = getthumb(video), thumbnailImage = getthumb(video))
			if session: li.addContextMenuItems([(language(30060), 'XBMC.RunPlugin(%s?func=add_to_playlist&id=%s)' % (sys.argv[0],  video['id']),)])
			u=sys.argv[0]+"?func=playid&id="+str(video['id'])
			li.setProperty('IsPlayable', 'true')
			li.setProperty('fanart_image', addon_fanart)
			xbmcplugin.addDirectoryItem(hos, url=u, listitem= li)
		xbmcplugin.endOfDirectory(hos)
		
def getthumb(thumbs):
	#print thumbs
	export=''
	try: 
		if thumbs['thumbnail']['small']: export= thumbs['thumbnail']['small']
	except: pass
	try: 
		if thumbs['thumbnail']['medium']: export= thumbs['thumbnail']['medium']
	except: pass
	try: 
		if thumbs['thumbnail']['big'] : export= thumbs['thumbnail']['big']
	except: pass
	
	return export
def run_search(params):                # Поиск
	#track_page_view('search')
	#track_page_view('search',UATRACK=GATrack)
	kbd = xbmc.Keyboard()
	kbd.setDefault('')
	kbd.setHeading(language(30021))
	kbd.doModal()
	out=''
	if kbd.isConfirmed():
		out = kbd.getText()

	params['func'] = 'search'
	params['url'] = HOST+'search/?subsite=190&type=videos&q=%s'%out.replace(' ','%20')
	track_page_view('search=%s'%out)
	search(params)

def get_sort():

	if Addon.getSetting("sort_v") == '0': return 'top'
	if Addon.getSetting("sort_v") == '1': return 'playlists'
	if Addon.getSetting("sort_v") == '2': return 'date'
	return 'top'

def get_params(paramstring):
	param=[]
	if len(paramstring)>=2:
		params=paramstring
		cleanedparams=params.replace('?','')
		if (params[len(params)-1]=='/'):
			params=params[0:len(params)-2]
		pairsofparams=cleanedparams.split('&')
		param={}
		for i in range(len(pairsofparams)):
			splitparams={}
			splitparams=pairsofparams[i].split('=')
			if (len(splitparams))==2:
				param[splitparams[0]]=splitparams[1]
	if len(param) > 0:
		for cur in param:
			param[cur] = urllib.unquote_plus(param[cur])
	return param


def addon_main():

	params = get_params(sys.argv[2])
	try:
		func = params['func']
		del params['func']
	except:
		func = None
		print( '[%s]: Primary input' % addon_id, 1 )
		main_screen(params)
	if func != None:
		try: pfunc = globals()[func]
		except:
			pfunc = None
			print( '[%s]: Function "%s" not found' % (addon_id, func), 4 )
			ShowMessage('Internal addon error', 'Function "%s" not found' % func, 2000)
		if pfunc: pfunc(params)
