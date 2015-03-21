#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
import urllib
import simplejson as json
import xbmcgui
import xbmcplugin
import xbmcaddon
import re

from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup

__addon__ = xbmcaddon.Addon( id = 'plugin.image.manga24.ru' )
__language__ = __addon__.getLocalizedString

addon_icon    = __addon__.getAddonInfo('icon')
addon_fanart  = __addon__.getAddonInfo('fanart')
addon_path    = __addon__.getAddonInfo('path')
addon_type    = __addon__.getAddonInfo('type')
addon_id      = __addon__.getAddonInfo('id')
addon_author  = __addon__.getAddonInfo('author')
addon_name    = __addon__.getAddonInfo('name')
addon_version = __addon__.getAddonInfo('version')

baseUrl = 'http://manga24.ru/'

hos = int(sys.argv[1])
headers  = {
	'User-Agent' : 'XBMC',
	'Accept'     :' text/html, application/xml, application/xhtml+xml, image/png, image/jpeg, image/gif, image/x-xbitmap, */*',
	'Accept-Language':'ru-RU,ru;q=0.9,en;q=0.8',
	'Accept-Charset' :'utf-8, utf-16, *;q=0.1',
	'Accept-Encoding':'identity, *;q=0'
}

#basePhotoUrl = " https://api.500px.com/v1/photos/{photoid}?image_size=4&consumer_key=LvUFQHMQgSlaWe3aRQot6Ct5ZC2pdTMyTLS0GMfF"
#thisPlugin = int(sys.argv [1])
#featureNames = ['popular', 'upcoming', 'editors', 'fresh_today', 'fresh_yesterday', 'fresh_week']
#index = int(xbmcplugin.getSetting(thisPlugin, 'feature'))
#featureName = featureNames[index]
#PHOTOS_PER_PAGE = 20

def GET(target, post=None):
	#print target
	try:
		req = urllib2.Request(url = target, data = post, headers = headers)
		resp = urllib2.urlopen(req)
		CE = resp.headers.get('content-encoding')
		http = resp.read()
		resp.close()
		return http
	except Exception, e:
		xbmc.log( '[%s]: GET EXCEPT [%s]' % (addon_id, e), 4 )
		showMessage('HTTP ERROR', e, 5000)
def construct_request(params):
	return '%s?%s' % (sys.argv[0], urllib.urlencode(params))
	
def showMessage(heading, message, times = 3000, pics = addon_icon):
	try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading.encode('utf-8'), message.encode('utf-8'), times, pics.encode('utf-8')))
	except Exception, e:
		xbmc.log( '[%s]: showMessage: Transcoding UTF-8 failed [%s]' % (addon_id, e), 2 )
		try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, pics))
		except Exception, e:
			xbmc.log( '[%s]: showMessage: exec failed [%s]' % (addon_id, e), 3 )

def get_manga(params):
	link='http://manga24.ru%s'%params['m_path']
	http = GET(link)
	if http == None: return False
	#print http
	beautifulSoup = BeautifulSoup(http)
	content = beautifulSoup.find('ul', attrs={'class': 'mlist'})
	try:
		cats=content.findAll('li')
		for scene in cats:
			title= str(scene).split('"')[1].split('/')[2]
			path= scene.find('a')['href']
			listitem=xbmcgui.ListItem(title,addon_icon,addon_icon)
			listitem.setProperty('IsPlayable', 'false')
			
			uri = construct_request({
				'func': 'read_manga',
				'm_path':path
				})
			xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
	except: 
		try:
			content = beautifulSoup.find('div', attrs={'class': 'item2'})
			path= content.find('a')['href']
			listitem=xbmcgui.ListItem("Читать",addon_icon,addon_icon)
			listitem.setProperty('IsPlayable', 'false')
			uri = construct_request({
				'func': 'read_manga',
				'm_path':path
				})
			xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
		except: pass
	xbmcplugin.addSortMethod(hos, xbmcplugin.SORT_METHOD_LABEL)
	xbmcplugin.addSortMethod(hos, xbmcplugin.SORT_METHOD_TITLE)
	#xbmcplugin.endOfDirectory(handle=hos, succeeded=True, updateListing=False, cacheToDisc=True)
	xbmcplugin.endOfDirectory(handle=hos, succeeded=True, updateListing=False, cacheToDisc=True)	
	
def read_manga(params):

	link='http://manga24.ru/%s'%params['m_path']
	print link
	http = GET(link)
	if http == None: return False
	beautifulSoup = BeautifulSoup(http)
	beautifulSoup.prettify()
	body=str(beautifulSoup).split('\n')
	d_f=None
	i_f=None
	imgs=[]
	pat=re.compile('[a-zA-Z0-9-_.!]+.[png|jpg|PNG|JPG]', re.S)
	for line in body:
		if line.split(':')[0].find('dir')>0 and not d_f: 
			url=line.split('"')[1].replace('\/','/')
			d_f=True
		if line.split(':')[0].find('images')>0 and not i_f: 
			img = re.findall(pat, line)
			i_f=True
	for ism in img:
		try:
			mm=xbmcgui.ListItem(ism,addon_icon,addon_icon)
			xbmcplugin.addDirectoryItem(hos,url+ism,mm,False)
			print ism
		except: pass

	xbmcplugin.endOfDirectory(handle=hos, succeeded=True, updateListing=False, cacheToDisc=True)
def mainScreen(params):
	link='http://manga24.ru/all/'
	http = GET(link)
	if http == None: return False
	beautifulSoup = BeautifulSoup(http)
	content = beautifulSoup.find('select', attrs={'id': 'manga_list'})
	cats=content.findAll('option')
	for manga in cats:
		try:
			manga.prettify()
			title=manga.string
			path=str(manga).split('"')[1]
			listitem=xbmcgui.ListItem(title,addon_icon,addon_icon)
			listitem.setProperty('IsPlayable', 'false')
			listitem.setLabel(title)
			uri = construct_request({
				'func': 'get_manga',
				'm_path':path
				})
			xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
		except: pass
	#xbmcplugin.addSortMethod(hos, xbmcplugin.SORT_METHOD_LABEL)
	#xbmcplugin.addSortMethod(hos, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.endOfDirectory(handle=hos, succeeded=True, updateListing=False, cacheToDisc=True)
	
def zmainScreen(params):
	listitem=xbmcgui.ListItem('Самое популярное',addon_icon,addon_icon)
	listitem.setProperty('IsPlayable', 'false')
	uri = construct_request({
		'func': 'get_pop'
		})
	xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
	listitem=xbmcgui.ListItem('Каталог',addon_icon,addon_icon)
	listitem.setProperty('IsPlayable', 'false')
	uri = construct_request({
		'func': 'get_all'
		})
	xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
	xbmcplugin.endOfDirectory(hos)
	
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

params = get_params(sys.argv[2])
try:
	func = params['func']
	del params['func']
except:
	func = None
	xbmc.log( '[%s]: Primary input' % addon_id, 1 )
	mainScreen(params)
if func != None:
	try: pfunc = globals()[func]
	except:
		pfunc = None
		xbmc.log( '[%s]: Function "%s" not found' % (addon_id, func), 4 )
		showMessage('Internal addon error', 'Function "%s" not found' % func, 2000)
	if pfunc: pfunc(params)

