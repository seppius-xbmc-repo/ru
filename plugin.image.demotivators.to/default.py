#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
import urllib
import simplejson as json
import xbmcgui
import xbmcplugin
import xbmcaddon

from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup

__addon__ = xbmcaddon.Addon( id = 'plugin.image.demotivators.to' )
__language__ = __addon__.getLocalizedString

addon_icon    = __addon__.getAddonInfo('icon')
addon_fanart  = __addon__.getAddonInfo('fanart')
addon_path    = __addon__.getAddonInfo('path')
addon_type    = __addon__.getAddonInfo('type')
addon_id      = __addon__.getAddonInfo('id')
addon_author  = __addon__.getAddonInfo('author')
addon_name    = __addon__.getAddonInfo('name')
addon_version = __addon__.getAddonInfo('version')

baseUrl = 'http://demotivators.to/'
Urls= ['http://demotivators.to/','http://demotivators.to/top/','http://demotivators.to/dzan/']
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
	
def findPic(url):
	url=baseUrl+url
	http = GET(url)
	beautifulSoup = BeautifulSoup(http)
	content = beautifulSoup.find('div', attrs={'class': 'posterimage'})
	content = content.find('img')
	return baseUrl+content['src']
	print url

def get_main_me(params):
	link=params['url']
	http = GET(link)
	if http == None: return False
	beautifulSoup = BeautifulSoup(http)
	content = beautifulSoup.findAll('td', attrs={'align': 'center', 'width':'200'})
	for n in content:
		linka=n.find('a',attrs={'target':'_blank'})['href']
		img=n.find('img')['src']
		img=img.replace('thumbs','images')
		img='http://demotivation.me'+img
		print img
		title=str(n.find('b')).replace('<b>','').replace('</b>','')
		zlink='http://demotivation.me'+linka
		listItem = xbmcgui.ListItem(title, '', '', '', '')
		xbmcplugin.addDirectoryItem(hos, img, listItem, False)
	
	xbmcplugin.endOfDirectory(handle=hos, succeeded=True, updateListing=False, cacheToDisc=True)
	
def get_news_me(params):
	print params
	page=params['p']
	link='%s?r=%s'%(params['url'],str(page))
	print link
	http = GET(link)
	if http == None: return False
	beautifulSoup = BeautifulSoup(http)
	content = beautifulSoup.findAll('td', attrs={'align': 'center', 'width':'200'})
	for n in content:
		linka=n.find('a',attrs={'target':'_blank'})['href']
		img=n.find('img')['src']
		img=img.replace('thumbs','images')
		img='http://demotivation.me'+img
		#print img
		title=str(n.find('b')).replace('<b>','').replace('</b>','')
		zlink='http://demotivation.me'+linka
		listItem = xbmcgui.ListItem(title, '', '', '', '')
		xbmcplugin.addDirectoryItem(hos, img, listItem, False)
		
	listitem=xbmcgui.ListItem('Еще',addon_icon,addon_icon)
	listitem.setProperty('IsPlayable', 'false')
	uri = construct_request({
		'url': params['url'],
		'p':int(params['p'])+60,
		'func': 'get_news_me'
		})
	xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
	
	xbmcplugin.endOfDirectory(handle=hos, succeeded=True, updateListing=False, cacheToDisc=True)

def get_main(params):

	max_pages=4
	currpage=0
	
	
	while currpage<max_pages:
		try:
			page=params['page']
			next='?page=%s'%str(int(page)+currpage)
			link=params['url']+next
		except:
			page=None
			next=None
			link=params['url']
		http = GET(link)
		if http == None: return False
		beautifulSoup = BeautifulSoup(http)
		content = beautifulSoup.find('div', attrs={'class': 'posterimage'})
		content = beautifulSoup.find('table')
		cats=content.findAll('a')
		for im in cats:
			if str(im).find('#comments')<0: 
				listItem = xbmcgui.ListItem(im.find('img')['alt'], '', '', '', '')
				xbmcplugin.addDirectoryItem(hos, findPic(im['href']), listItem, False)

		currpage=currpage+1
	listitem=xbmcgui.ListItem('Еще',addon_icon,addon_icon)
	listitem.setProperty('IsPlayable', 'false')
	if next:
		uri = construct_request({
			'url': params['url'],
			'page':int(params['page'])+currpage,
			'func': 'get_main'
			})
	else:
		uri = construct_request({
			'url': params['url'],
			'func': 'get_main'
			})
	xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
	xbmcplugin.endOfDirectory(handle=hos, succeeded=True, updateListing=False, cacheToDisc=True)
	#dat_file = os.path.join(addon_path, 'categories.txt')
	
	#xbmcplugin.addDirectoryItem(hos, uri, li, True)

	#xbmcplugin.endOfDirectory(hos)
def demotivation(params):
	listitem=xbmcgui.ListItem('Главная',addon_icon,addon_icon)
	listitem.setProperty('IsPlayable', 'false')
	uri = construct_request({
		'url': 'http://demotivation.me/',
		'page':1,
		'func': 'get_main_me'
		})
	xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
	
	listitem=xbmcgui.ListItem('Свежие',addon_icon,addon_icon)
	listitem.setProperty('IsPlayable', 'false')
	uri = construct_request({
		'url': 'http://demotivation.me/recent.php',
		'p':0,
		'func': 'get_news_me'
		})
	xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
	listitem=xbmcgui.ListItem('Наиболее Комментируемые',addon_icon,addon_icon)
	listitem.setProperty('IsPlayable', 'false')
	uri = construct_request({
		'url': 'http://demotivation.me/discussed.php',
		'p':0,
		'func': 'get_main_me'
		})
	xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
	listitem=xbmcgui.ListItem('Рандом',addon_icon,addon_icon)
	listitem.setProperty('IsPlayable', 'false')
	uri = construct_request({
		'url': 'http://demotivation.me/random.php',
		'p':0,
		'func': 'get_news_me'
		})
	xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
	listitem=xbmcgui.ListItem('Выбор Редакции',addon_icon,addon_icon)
	listitem.setProperty('IsPlayable', 'false')
	uri = construct_request({
		'url': 'http://demotivation.me/editors_choise.php',
		'p':0,
		'func': 'get_news_me'
		})
	xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
	xbmcplugin.endOfDirectory(hos)
def dem_to(params):
	listitem=xbmcgui.ListItem('Главная',addon_icon,addon_icon)
	listitem.setProperty('IsPlayable', 'false')
	uri = construct_request({
		'url': 'http://demotivators.to/',
		'page':1,
		'func': 'get_main'
		})
	xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
	listitem=xbmcgui.ListItem('Топ',addon_icon,addon_icon)
	listitem.setProperty('IsPlayable', 'false')
	uri = construct_request({
		'url': 'http://demotivators.to/top/',
		'page':1,
		'func': 'get_main'
		})
	xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
	listitem=xbmcgui.ListItem('Самые комментируемые',addon_icon,addon_icon)
	listitem.setProperty('IsPlayable', 'false')
	uri = construct_request({
		'url': 'http://demotivators.to/mostcommented/',
		'page':1,
		'func': 'get_main'
		})
	xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
	listitem=xbmcgui.ListItem('Дзен',addon_icon,addon_icon)
	listitem.setProperty('IsPlayable', 'false')
	uri = construct_request({
		'url': 'http://demotivators.to/dzan/',
		'func': 'get_main'
		})
	xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
	
	

	
	xbmcplugin.endOfDirectory(hos)
def mainScreen(params):

	listitem=xbmcgui.ListItem('demotivation.me',addon_icon,addon_icon)
	listitem.setProperty('IsPlayable', 'false')
	uri = construct_request({
		'func': 'demotivation'
		})
	xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
	
	#listitem=xbmcgui.ListItem('demotivators.ru',None,addon_icon)
	#listitem.setProperty('IsPlayable', 'false')
	#uri = construct_request({
	#	'func': 'dem_to'
	#	})
	#xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
#
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

