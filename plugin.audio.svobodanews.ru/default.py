#!/usr/bin/python
# -*- coding: utf-8 -*-
#/*
# *  Copyright (c) 2011-2012 XBMC-Russia, HD-lab Team, E-mail: dev@hd-lab.ru
# *  Writer (c) 2011, Kostynoy S.A., E-mail: seppius2@gmail.com
# *
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# */
import xml.dom.minidom, urllib, urllib2, re, sys, os
import xbmcplugin, xbmcgui, xbmcaddon

try: Emulating = xbmcgui.Emulating
except: Emulating = False

bgread = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'background.png'))
fanart = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'fanart.jpg'))
icon   = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'icon.png'))
pluginhandle = int(sys.argv[1])
xbmcplugin.setPluginFanart(pluginhandle, fanart)

COORD_1080I      = 0
COORD_720P       = 1
COORD_480P_4X3   = 2
COORD_480P_16X9  = 3
COORD_NTSC_4X3   = 4
COORD_NTSC_16X9  = 5
COORD_PAL_4X3    = 6
COORD_PAL_16X9   = 7
COORD_PAL60_4X3  = 8
COORD_PAL60_16X9 = 9

ACTION_MOVE_LEFT        = 1
ACTION_MOVE_RIGHT       = 2
ACTION_MOVE_UP          = 3
ACTION_MOVE_DOWN        = 4
ACTION_PAGE_UP          = 5
ACTION_PAGE_DOWN        = 6
ACTION_SELECT_ITEM      = 7
ACTION_HIGHLIGHT_ITEM   = 8
ACTION_PARENT_DIR       = 9
ACTION_PREVIOUS_MENU    = 10
ACTION_SHOW_INFO        = 11
ACTION_PAUSE            = 12
ACTION_STOP             = 13
ACTION_NEXT_ITEM        = 14
ACTION_PREV_ITEM        = 15

class Reader(xbmcgui.Window):
	def __init__(self, txt_data):
		if Emulating: xbmcgui.Window.__init__(self)
		self.setCoordinateResolution(COORD_720P)
		self.addControl(xbmcgui.ControlImage(0, 0, 1280, 720, bgread))
		self.NewsTextBox = xbmcgui.ControlTextBox(10,10,1260,700)
		self.addControl(self.NewsTextBox)
		self.NewsTextBox.setText(txt_data)
	def onAction(self, action):
		if action == ACTION_MOVE_UP:
			self.NewsTextBox.scroll(1)
		elif action == ACTION_MOVE_DOWN:
			self.NewsTextBox.scroll(-1)
		elif action == ACTION_PAGE_UP:
			self.NewsTextBox.scroll(1)
		elif action == ACTION_PAGE_DOWN:
			self.NewsTextBox.scroll(-1)
		else: self.close()

def clean(name):
	remove=[('  ',' '),('&ndash;',''),('<br>','\n'),('<br />','\n'),('&amp;','&'),('&quot;','"'),('&#39;','\''),('&nbsp;',' '),('&laquo;','"'),('&raquo;', '"'),('&#151;','-')]
	for trash, crap in remove:
		name=name.replace(trash, crap)
	return name

def getURL(url):
	#xbmc.output('def getURL(%s)'%url)
	try:
		req = urllib2.Request(url)
		response = urllib2.urlopen(req)
		link = response.read()
		response.close()
	except urllib2.URLError, e:
		xbmcgui.Dialog().ok('HTTP ERROR', str(e))
		return None
	else:
		return link


def RssParser(http):
	item_count = 0
	titles = []
	descriptions = []
	links = []
	guids = []
	pubDates  = []
	categorys = []
	comments  = []
	if http != None:
		region_1 = re.compile('<item>(.*?)</item>', re.DOTALL).findall(http)
		if len(region_1) > 0:
			for region in region_1:
				current_title       = ''
				current_description = 'No description'
				current_link        = ''
				current_guid        = ''
				current_pubDate     = 'No pub Date'
				current_category    = 'No category'
				current_comments    = 'No comments'
				current_title_raw       = re.compile('<title>(.*?)</title>').findall(region)
				current_description_raw = re.compile('<description>(.*?)</description>', re.DOTALL).findall(region)
				current_link_raw        = re.compile('<link>(.*?)</link>').findall(region)
				current_guid_raw        = re.compile('<guid>(.*?)</guid>').findall(region)
				current_pubDate_raw     = re.compile('<pubDate>(.*?)</pubDate>').findall(region)
				current_category_raw    = re.compile('<category>(.*?)</category>').findall(region)
				current_comments_raw    = re.compile('<comments>(.*?)</comments>', re.DOTALL).findall(region)
				if (len(current_title_raw) > 0) and (current_guid_raw > 0):
					item_count += 1
					current_title       = current_title_raw[0]
					if len(current_description_raw) > 0:
						current_description = current_description_raw[0]
					if len(current_link_raw) > 0:
						current_link = current_link_raw[0]
					current_guid        = current_guid_raw[0]
					if len(current_pubDate_raw) > 0:
						current_pubDate = current_pubDate_raw[0]
					if len(current_category_raw) > 0:
						current_category = current_category_raw[0]
					if len(current_comments_raw) > 0:
						current_comments = current_comments_raw[0]
					titles.append(current_title)
					descriptions.append(clean(current_description))
					links.append(current_link)
					guids.append(current_guid)
					pubDates.append(current_pubDate)
					categorys.append(current_category)
					comments.append(current_comments)
	return item_count, titles, descriptions, links, guids, pubDates, categorys, comments

def RSSRoot(url):
	http = getURL(url)
	if http == None:
		return
	r1 = re.compile('</h5>(.*?)</div><div class=\'rsspage_links\'><a class=\'addico linksmall\' href=\'(.*?)\'>').findall(http)
	x=1
	for rssTitle, rssUrl in r1:
		rssUrl = rssUrl.replace('count=50','count=150')
		rssTitle = clean(rssTitle)
		uri = sys.argv[0] + '?mode=RSSShow'
		uri += '&url='  + urllib.quote_plus(rssUrl)
		uri += '&name=' + urllib.quote_plus(rssTitle)
		item = xbmcgui.ListItem(('%s. %s' % (x, rssTitle)), iconImage = icon)
		xbmcplugin.addDirectoryItem(handle = pluginhandle, url = uri, listitem = item, isFolder = True)
		x += 1
	xbmcplugin.endOfDirectory(pluginhandle)

def RSSShow(url, name):
	http = getURL(url)
	if http == None:
		return
	(item_count, titles, descriptions, links, guids, pubDates, categorys, comments) = RssParser(http)
	if item_count > 0:
		for x in range(item_count):
			Title       = clean(titles[x])
			Description = descriptions[x]
			Link        = links[x]
			Guid        = guids[x]
			PubDate     = pubDates[x]
			Category    = categorys[x]
			Comment     = comments[x]
			#xbmc.output('      Title = %s' % Title)
			#xbmc.output('Description = %s' % Description)
			#xbmc.output('       Link = %s' % Link)
			#xbmc.output('       Guid = %s' % Guid)
			#xbmc.output('    PubDate = %s' % PubDate)
			#xbmc.output('   Category = %s' % Category)
			#xbmc.output('    Comment = %s' % Comment)
			uri = sys.argv[0] + '?mode=ShowPage'
			uri += '&url='  + urllib.quote_plus(Guid)
			uri += '&name=' + urllib.quote_plus(Title)
			uri += '&plot=' + urllib.quote_plus(Description)
			item = xbmcgui.ListItem('%s. %s' % ((x+1), Title), iconImage = icon)
			xbmcplugin.addDirectoryItem(handle = pluginhandle, url = uri, listitem = item, isFolder = True)
	xbmcplugin.endOfDirectory(pluginhandle)






def ShowPage(url, name, plot):
	#xbmc.output('ShowPage(%s, %s, %s)' % (url, name, plot))

	http = getURL(url)
	if http == None: return False

	r1 = re.compile('"zoomMe">(.*?)<div', re.DOTALL).findall(http)
	if len(r1) > 0:
		rdata = re.sub('(?is)<.*?>', '', clean(r1[0]), re.DOTALL)
		uri = sys.argv[0] + '?mode=Read'
		uri += '&plot='  + urllib.quote_plus(rdata)
		item = xbmcgui.ListItem('Читать новость', iconImage = icon)
		xbmcplugin.addDirectoryItem(handle = pluginhandle, url = uri, listitem = item)

	r2 = re.compile('<img[ ]*border="[0-9]*"[ ]*class="photo"[ ]*alt="(.*?)"[ ]*src="(.*?)"[ ]*/>').findall(http)
	if len(r2) > 0:
		for alt, photo in r2:
			#xbmc.output('ShowPage   alt = %s' % alt)
			#xbmc.output('ShowPage photo = %s' % photo)
			item = xbmcgui.ListItem( ('Фото %s' % os.path.basename(photo)), iconImage = 'DefaultPicture.png', thumbnailImage=photo)
			item.setInfo(type='Pictures', infoLabels={'title': photo, 'picturepath': photo})
			xbmcplugin.addDirectoryItem(handle = pluginhandle, url = photo, listitem = item)

	r3 = re.compile('<li[ ]*class="listenlink"><a[ ]*class="listenico"[ ]*target="_blank"[ ]*href="(.*?)"').findall(http)
	if len(r3) > 0:
		for aurl in r3:
			aurl = 'http://www.svobodanews.ru' + aurl
			#xbmc.output('ShowPage aurl = %s' % aurl)
			http2 = getURL(aurl)
			r_a = re.compile('GetFlashXml.aspx(.*?)[\',\"]').findall(http2)
			if len(r_a) > 0:
				naurl = 'http://www.svobodanews.ru/GetFlashXml.aspx' + r_a[0]
			(result, title, plot, protocol, media_type, mediaSource, PreviewImage, MediaUrl) = GetFlashXml(naurl, name, plot)
			if result == True:
				item = xbmcgui.ListItem('Слушать "%s"' % title, thumbnailImage = PreviewImage)
				item.setInfo(type=media_type, infoLabels={'title': title, 'genre': 'Новости', 'plot': plot})
				item.setProperty('IsPlayable', 'true')
				xbmcplugin.addDirectoryItem(handle = pluginhandle, url = mediaSource, listitem = item)


	r4 = re.compile('GetFlashXml.aspx(.*?)[\',\"]').findall(http)
	if len(r4) > 0:
		for vurl in r4:
			naurl = 'http://www.svobodanews.ru/GetFlashXml.aspx' + vurl
			(result, title, plot, protocol, media_type, mediaSource, PreviewImage, MediaUrl) = GetFlashXml(naurl, name, plot)
			if result == True:
				item = xbmcgui.ListItem('Смотреть "%s"' % title, thumbnailImage = PreviewImage)
				item.setInfo(type=media_type, infoLabels={'title': title, 'genre': 'Новости', 'plot': plot})
				item.setProperty('IsPlayable', 'true')
				xbmcplugin.addDirectoryItem(handle = pluginhandle, url = mediaSource, listitem = item)

	xbmcplugin.endOfDirectory(pluginhandle)


def GetFlashXml(url, title='Нет названия', plot='Нет описания'):
	#xbmc.output('GetFlashXml(%s, %s, %s)' % (url, title, plot))
	protocol = 'unknown'
	PreviewImage = icon
	MediaUrl = url
	http = getURL(url)
	if http == None:
		return False,None,None,None,None,None,None,None
	r1 = re.compile('<title>.*<\!\[CDATA\[(.*?)\]\]>.*</title>').findall(http)
	r2 = re.compile('<description>.*<\!\[CDATA\[(.*?)\]\]>.*</description>').findall(http)
	r3 = re.compile('<protocol value="(.*?)"/>').findall(http)
	if len(r1) > 0:    title = r1[0]
	if len(r2) > 0:     plot = r2[0]
	if len(r3) > 0: protocol = r3[0]
	if protocol == 'http':
		r4 = re.compile('<mediaSource.*value="(.*?)".*>.*</mediaSource>').findall(http)
		if len(r4) > 0:
			mediaSource = r4[0]
		else:
			#xbmc.output('GetFlashXml ERROR: Нет mediaSource для протокола HTTP')
			#xbmc.output('GetFlashXml HTTP = %s' % http)
			return False,None,None,None,None,None,None,None
	elif protocol == 'rtmp':
		r4 = re.compile('<mediaSource.*value="(.*?)".*server="(.*?)".*>.*</mediaSource>').findall(http)
		if len(r4) > 0:
			(rpath, rserv) = r4[0]
			mediaSource = rserv + rpath
		else:
			#xbmc.output('GetFlashXml ERROR: Нет mediaSource для протокола RTMP')
			#xbmc.output('GetFlashXml HTTP = %s' % http)
			return False,None,None,None,None,None,None,None
	else:
		#xbmc.output('GetFlashXml ERROR: Неизвестный протокол %s' % protocol)
		#xbmc.output('GetFlashXml HTTP = %s' % http)
		return False,None,None,None,None,None,None,None
	if http.find('media type="video"') <> -1:
		media_type='video'
		r5 = re.compile('<videoPreviewImage.*value="(.*?)".*>.*</videoPreviewImage>').findall(http)
		r6 = re.compile('<videoUrl.*value="(.*?)".*>.*</videoUrl>').findall(http)
		if len(r5) > 0:
			PreviewImage = r5[0]
		if len(r6) >0:
			MediaUrl = r6[0]
	elif http.find('media type="audio') <> -1:
		media_type='music'
	else:
		#xbmc.output('GetFlashXml ERROR: Неизвестный media type')
		#xbmc.output('GetFlashXml HTTP = %s' % http)
		return False,None,None,None,None,None,None,None
	#xbmc.output('GetFlashXml ____________title = %s' % title)
	#xbmc.output('GetFlashXml _____________plot = %s' % plot)
	#xbmc.output('GetFlashXml _________protocol = %s' % protocol)
	#xbmc.output('GetFlashXml _____________type = %s' % media_type)
	#xbmc.output('GetFlashXml ______mediaSource = %s' % mediaSource)
	#xbmc.output('GetFlashXml _____PreviewImage = %s' % PreviewImage)
	#xbmc.output('GetFlashXml _________MediaUrl = %s' % MediaUrl)
	return True, title, plot, protocol, media_type, mediaSource, PreviewImage, MediaUrl

def get_params():
	param=[]
	paramstring=sys.argv[2]
	if len(paramstring)>=2:
		params=sys.argv[2]
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
	return param

params=get_params()
url =None
name=None
mode=None


try:
	url=urllib.unquote_plus(params["url"])
except:
	pass

try:
	name=urllib.unquote_plus(params["name"])
except:
	name=''

try:
	mode=params["mode"]
except:
	pass

try:
	premiered=urllib.unquote_plus(params["premiered"])
except:
	premiered=''

try:
    plot=urllib.unquote_plus(params["plot"])
except:
    plot=''

if mode=='RSSShow':
	RSSShow(url, name)

if mode=='ShowPage':
	ShowPage(url, name, plot)

if mode=='Read':
	Read = Reader(txt_data = plot)
	Read.doModal()
	del Read

if mode == None:
	item = xbmcgui.ListItem('* SVOBODA-NEWS ONLINE *', iconImage = icon)
	item.setInfo(type='music', infoLabels={'title': '* SVOBODA-NEWS ONLINE *'})
	item.setProperty('IsPlayable', 'true')
	xbmcplugin.addDirectoryItem(handle = pluginhandle, url = 'http://svobodanews.fvds.ru:8000/Test_RFERL_stream.m3u', listitem = item)

	RSSRoot('http://www.svobodanews.ru/rsspage.aspx')

