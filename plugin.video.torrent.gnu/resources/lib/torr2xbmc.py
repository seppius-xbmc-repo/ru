#!/usr/bin/python
# -*- coding: utf-8 -*-

import httplib
import urllib
import urllib2
import re
import sys
import os
import socket

import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmc
import xbmcaddon
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup

from TSCore import TSengine as tsengine
import base64

hos = int(sys.argv[1])
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

__addon__ = xbmcaddon.Addon( id = 'plugin.video.torrent.gnu' )
__language__ = __addon__.getLocalizedString

addon_icon    = __addon__.getAddonInfo('icon')
addon_fanart  = __addon__.getAddonInfo('fanart')
addon_path    = __addon__.getAddonInfo('path')
addon_type    = __addon__.getAddonInfo('type')
addon_id      = __addon__.getAddonInfo('id')
addon_author  = __addon__.getAddonInfo('author')
addon_name    = __addon__.getAddonInfo('name')
addon_version = __addon__.getAddonInfo('version')

ktv_folder=unicode(__addon__.getSetting('download_path'),'utf-8')
prt_file=__addon__.getSetting('port_path')
aceport=62062
try:
	if prt_file: 
		gf = open(prt_file, 'r')
		aceport=int(gf.read())
		gf.close()
except: prt_file=None

if not prt_file:
	try:
		fpath= os.path.expanduser("~")
		pfile= os.path.join(fpath,'AppData\Roaming\TorrentStream\engine' ,'acestream.port')
		gf = open(pfile, 'r')
		aceport=int(gf.read())
		gf.close()
		__addon__.setSetting('port_path',pfile)
		print aceport
	except: aceport=62062
	
while not __addon__.getSetting('download_path'): __addon__.openSettings()
ktv_folder=unicode(__addon__.getSetting('download_path'),'utf-8')
# JSON понадобится, когда будет несколько файлов в торренте
try:
	import json
except ImportError:
	try:
		import simplejson as json
		xbmc.log( '[%s]: Error import json. Uses module simplejson' % addon_id, 2 )
	except ImportError:
		try:
			import demjson3 as json
			xbmc.log( '[%s]: Error import simplejson. Uses module demjson3' % addon_id, 3 )
		except ImportError:
			xbmc.log( '[%s]: Error import demjson3. Sorry.' % addon_id, 4 )

def construct_request(params):
	return '%s?%s' % (sys.argv[0], urllib.urlencode(params))
	
def GET(target, post=None):
	#print target
	try:
		req = urllib2.Request(url = target, data = post)
		req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
		resp = urllib2.urlopen(req)
		http = resp.read()
		resp.close()
		return http
	except Exception, e:
		xbmc.log( '[%s]: GET EXCEPT [%s]' % (addon_id, e), 4 )
		showMessage('HTTP ERROR', e, 5000)
		
def showMessage(heading, message, times = 3000, pics = addon_icon):
	try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading.encode('utf-8'), message.encode('utf-8'), times, pics.encode('utf-8')))
	except Exception, e:
		xbmc.log( '[%s]: showMessage: Transcoding UTF-8 failed [%s]' % (addon_id, e), 2 )
		try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, pics))
		except Exception, e:
			xbmc.log( '[%s]: showMessage: exec failed [%s]' % (addon_id, e), 3 )
def rutor(params):
	http = GET('http://www.rutor.org/browse/0/1/0/2')
	beautifulSoup = BeautifulSoup(http)
	channels=beautifulSoup.findAll('tr', attrs={'class': 'gai'})
	for it in channels:
		link=it.find('a')['href']
		title= it.find(href=re.compile("/torrent/.+")).string.encode('utf-8')
		li = xbmcgui.ListItem(title)
		uri = construct_request({
				'func': 'play_url',
				'file':link
			})
		xbmcplugin.addDirectoryItem(hos, uri, li, True)
	xbmcplugin.endOfDirectory(hos)
	
def stream (params):
	torr_link='f4a94963c11a47f213b145697f494b5fc5485b02'
	TSplayer=tsengine()
	out=TSplayer.load_torrent(torr_link,'INFOHASH',port=aceport)
	if out=='Ok':
		TSplayer.play_url_ind(0,'stream',None)
	TSplayer.end()
def ttv (params):
	http = GET('http://torrent-tv.ru/channels.php')
	beautifulSoup = BeautifulSoup(http)
	channels=beautifulSoup.findAll('div', attrs={'class': 'best-channels-content'})
	for ch in channels: 
		link =ch.find('a')['href']
		title= ch.find('strong').string.encode('utf-8')
		img='http://torrent-tv.ru/'+ch.find('img')['src']
		li = xbmcgui.ListItem(title,img,img)
		uri = construct_request({
				'func': 'play_ch',
				'img':img,
				'title':title,
				'file':link
			})
		xbmcplugin.addDirectoryItem(hos, uri, li)
	xbmcplugin.endOfDirectory(hos)
	
def play_ch(params):
	http = GET('http://torrent-tv.ru/'+params['file'])
	print 'http://torrent-tv.ru/'+params['file']
	beautifulSoup = BeautifulSoup(http)
	tget= beautifulSoup.find('div', attrs={'class':'tv-player-wrapper'})
	#print tget
	#this.loadTorrent("http://94.242.221.195:7773/file?name=%D0%A2%D0%9D%D0%A2"
	#print http
	#print 'http://torrent-tv.ru/'+params['file']
	m=re.search('http:(.+)"', str(tget))
	torr_link= m.group(0).split('"')[0]
	m=re.search('http://[0-9]+.[0-9]+.[0-9]+.[0-9]+:[0-9]+', torr_link)
	try:
		pre_link= m.group(0)
		http = GET(pre_link)
		beautifulSoup = BeautifulSoup(http)
		lnk=pre_link+beautifulSoup.find('a')['href']
		#print lnk
		torr_link=lnk
	except: pass
	TSplayer=tsengine()
	out=TSplayer.load_torrent(torr_link,'TORRENT',port=aceport)
	if out=='Ok':
		TSplayer.play_url_ind(0,params['title'],addon_icon,params['img'])
	TSplayer.end()
	showMessage('Торрент', 'Стоп', 2000)    
def mainScreen(params):
	li = xbmcgui.ListItem('test stream')
	uri = construct_request({
		'func': 'stream'
	})
	xbmcplugin.addDirectoryItem(hos, uri, li, True)
	li = xbmcgui.ListItem('torrent-tv')
	uri = construct_request({
		'func': 'ttv'
	})
	xbmcplugin.addDirectoryItem(hos, uri, li, True)
	li = xbmcgui.ListItem('rutor.top')
	uri = construct_request({
		'func': 'rutor'
	})
	xbmcplugin.addDirectoryItem(hos, uri, li, True)
	li = xbmcgui.ListItem('.torrent Player')
	uri = construct_request({
		'func': 'tpl'
	})
	xbmcplugin.addDirectoryItem(hos, uri, li, True)
	xbmcplugin.endOfDirectory(hos)
from urllib import unquote, quote, quote_plus
def tpl(params):
	dirList=os.listdir(ktv_folder)
	#print os.listdir(ktv_folder)
	for fname in dirList:
		if re.search(u'.+.torrent', fname):
			#print fname.encode('utf-8')
			img=None
			timg=ktv_folder + fname.replace(u'.torrent',u'')+u'.png'
			if os.path.isfile(timg): img=timg
			timg=ktv_folder + fname.replace(u'.torrent','')+u'.jpg'
			if os.path.isfile(timg): img=timg
			if img: li = xbmcgui.ListItem(fname.replace(u'.torrent',u''),img,img)
			else: li = xbmcgui.ListItem(fname.replace(u'.torrent',u''))
			uri = construct_request({
				'func': 'play_file',
				'file': (ktv_folder + fname).encode('utf-8')
			})
			xbmcplugin.addDirectoryItem(hos, uri, li, True)
	xbmcplugin.endOfDirectory(hos)

def play_file(params):
	#получаем содержимое файла в base64
	f = open(params['file'].decode('utf-8'), 'rb')
	buf=f.read()
	f.close
	torr_link=base64.b64encode(buf)
	xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
	TSplayer=tsengine()
	out=TSplayer.load_torrent(torr_link,'RAW',port=aceport)
	if out=='Ok':
		for k,v in TSplayer.files.iteritems():

			li = xbmcgui.ListItem(urllib.unquote(k))
			uri = construct_request({
				'torr_url': torr_link,
				'title': k,
				'ind':v,
				'img':None,
				'func': 'play_it'
			})
			xbmcplugin.addDirectoryItem(hos, uri, li, False)
	xbmcplugin.endOfDirectory(hos)
	TSplayer.end()
	
def play_it(params):
	torr_link=params['torr_url']	
	TSplayer=tsengine()
	out=TSplayer.load_torrent(torr_link,'RAW',port=aceport)
	if out=='Ok':
		TSplayer.play_url_ind(int(params['ind']),params['title'],addon_icon,params['img'])
	TSplayer.end()
	showMessage('Торрент', 'Стоп', 2000)    

def play_url(params):
	torr_link=params['file']
	
	TSplayer=tsengine()
	out=TSplayer.load_torrent(torr_link,'TORRENT',port=aceport)
	if out=='Ok':
		for k,v in TSplayer.files.iteritems():
			li = xbmcgui.ListItem(urllib.unquote(k))
			uri = construct_request({
				'torr_url': torr_link,
				'title': k,
				'ind':v,
				'img':None,
				'func': 'play_url2'
			})
			xbmcplugin.addDirectoryItem(hos, uri, li, False)
	xbmcplugin.endOfDirectory(hos)
	TSplayer.end()
	
def play_url2(params):
	torr_link=params['torr_url']	
	TSplayer=tsengine()
	out=TSplayer.load_torrent(torr_link,'TORRENT',port=aceport)
	if out=='Ok':
		TSplayer.play_url_ind(int(params['ind']),params['title'],addon_icon,params['img'])
	TSplayer.end()
	showMessage('Торрент', 'Стоп', 2000)    
		
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
	#xbmc.log( '[s]: play' , 2 )
	params = get_params(sys.argv[2])
	try:
		func = params['func']
		del params['func']
	except:
		func = None
		xbmc.log( '[%s]: Primary input' % addon_id, 1 )
		tpl(params)
	if func != None:
		try: pfunc = globals()[func]
		except:
			pfunc = None
			xbmc.log( '[%s]: Function "%s" not found' % (addon_id, func), 4 )
			showMessage('Internal addon error', 'Function "%s" not found' % func, 2000)
		if pfunc: pfunc(params)
