#!/usr/bin/python
# -*- coding: utf-8 -*-
#/*
# *   Copyright (с) 2011 XBMC-Russia, HD-lab Team, E-mail: dev@hd-lab.ru
# *   Writer (C) 03/03/2011, Kostynoy S.A., E-mail: seppius2@gmail.com
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
# *  http://www.gnu.org/licenses/gpl.html
# */

import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import urllib2, urllib, os, xml.dom.minidom

import socket
socket.setdefaulttimeout(15)

h = int(sys.argv[1])
icon   = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'icon.png'))
fanart = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'fanart.jpg'))
xbmcplugin.setPluginFanart(h, fanart)

api_URL = 'http://russia.ru/xbmc/menu/list.xml'
api_FND = 'http://russia.ru/xbmc/search/videolist.xml'

__settings__ = xbmcaddon.Addon(id='plugin.video.russia.ru')
__language__ = __settings__.getLocalizedString
vqual = int(__settings__.getSetting('quality'))+1
lsize = (int(__settings__.getSetting('size'))+1)*10
argss = 'pagesize=%d&quality=%d'%(lsize,vqual)

def showMessage(heading, message, times = 3000):
	#heading = heading.encode('utf-8')
	#message = message.encode('utf-8')
	xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, icon))

def clean(name):
	remove = [('mdash;',''),('&ndash;',''),('hellip;','\n'),('&amp;',''),('&quot;','"'),
		  ('&#39;','\''),('&nbsp;',' '),('&laquo;','"'),('&raquo;','"'),('&#151;','-'),
		  ('<![CDATA[',''),(']]>','')]
	for trash, crap in remove:
		name = name.replace(trash, crap)
	return name

def CleanURL(name):
	remove = [('amp;', ''),('\n', ''),(' ',''),('\t','')]
	for trash, crap in remove:
		name = name.replace(trash, crap)
	return name


def GET(target):
	#print target
	try:
		req = urllib2.Request(target)
		req.add_header('User-Agent','XBMC/10-series (Python addon; XBMC-Russia; HD-lab Team; 2011; http://www.xbmc.org)')
		req.add_header(           'Host','russia.ru')
		req.add_header(         'Accept','text/html, application/xml, application/xhtml+xml, image/png, image/jpeg, image/gif, image/x-xbitmap, */*')
		req.add_header('Accept-Language','ru-RU,ru')
		#req.add_header( 'Accept-Charset','utf-8')
		req.add_header('Accept-Encoding','identity')
		req.add_header(     'Connection','Keep-Alive')
		f = urllib2.urlopen(req)
		a = f.read()
		f.close()
		#print a
		return a
	except Exception, e:
		showMessage(target, e, 5000)
		return None

def getsearch(params):
	KB = xbmc.Keyboard()
	KB.setHeading(__language__(30021))
	KB.doModal()
	if (KB.isConfirmed()):
		getitems({ 'url': urllib.quote_plus(api_FND + '?' + argss + '&q=' + urllib.quote_plus(KB.getText()))})


def getitems(params):
	try:    initurl = urllib.unquote_plus(params['url'])
	except: initurl = api_URL + '?' + argss
	http = GET(initurl)
	if http == None: return False
	document = xml.dom.minidom.parseString(http)
	for item in document.getElementsByTagName('item'):
		info = {}
		try:	label = item.getElementsByTagName('label')[0].firstChild.data
		except: label = ''
		try:	isFolder = item.getElementsByTagName('isFolder')[0].firstChild.data
		except: isFolder = '0'
		try:	Image = CleanURL(item.getElementsByTagName('thumbnailImage')[0].firstChild.data)
		except: Image = icon
		try: 	url = CleanURL(item.getElementsByTagName('url')[0].firstChild.data.encode('utf-8','replace'))
		except: url = api_URL
		try:    ifanart = item.getElementsByTagName('fanart')[0].firstChild.data
		except: ifanart = fanart
		try:	itype = item.getElementsByTagName('type')[0].firstChild.data
		except: itype = 'video'
		try:    info['date'] = item.getElementsByTagName('date')[0].firstChild.data
		except: info['date'] = ''
		try:	info['genre'] = item.getElementsByTagName('genre')[0].firstChild.data
		except: info['genre'] = ''
		try:	info['year'] = int(item.getElementsByTagName('year')[0].firstChild.data)
		except: info['year'] = 0
		try:	info['rating'] = float(item.getElementsByTagName('rating')[0].firstChild.data)
		except: info['rating'] = 0
		try:	info['playcount'] = int(item.getElementsByTagName('playcount')[0].firstChild.data)
		except: info['playcount'] = 0
		try:	info['director'] = item.getElementsByTagName('director')[0].firstChild.data
		except: info['director'] = ''
		try:	info['plot'] = item.getElementsByTagName('plot')[0].firstChild.data
		except: info['plot'] = ''
		try:	info['plotoutline'] = item.getElementsByTagName('plotoutline')[0].firstChild.data
		except: info['plotoutline'] = ''
		try:	info['title'] = item.getElementsByTagName('title')[0].firstChild.data
		except: info['title'] = label
		try:	info['duration'] = item.getElementsByTagName('duration')[0].firstChild.data
		except: info['duration'] = ''
		try:	info['studio'] = item.getElementsByTagName('studio')[0].firstChild.data
		except: info['studio'] = 'RUSSIA.RU'
		try:	info['tagline'] = item.getElementsByTagName('tagline')[0].firstChild.data
		except: info['tagline'] = ''
		try:	info['writer'] = item.getElementsByTagName('writer')[0].firstChild.data
		except: info['writer'] = ''
		IsFolder = (isFolder == '1')

		if IsFolder:
			uri = '%s?mode=getitems&url=%s' % (sys.argv[0], urllib.quote_plus(url))
		else: uri = url
		li = xbmcgui.ListItem(label, iconImage = Image, thumbnailImage = Image)
		li.setInfo(type = itype, infoLabels = info)

		if ifanart != None: li.setProperty('fanart_image', ifanart)
		xbmcplugin.addDirectoryItem(h, uri, li, IsFolder)

	uris = sys.argv[0] + '?mode=getsearch'
	items = xbmcgui.ListItem(__language__(30020), iconImage = icon, thumbnailImage = icon)
	items.setProperty('fanart_image', fanart)
	xbmcplugin.addDirectoryItem(h,uris,items,True)

	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_UNSORTED)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_DATE)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_DURATION)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_GENRE)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_VIDEO_RATING)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_VIDEO_RUNTIME)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_VIDEO_TITLE)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
	xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_LABEL)
	xbmcplugin.endOfDirectory(h)



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
	return param

params = get_params(sys.argv[2])
mode   = None
func   = None
try:    mode = urllib.unquote_plus(params['mode'])
except: getitems(params)
if mode != None:
	try:    func = globals()[mode]
	except: pass
	if func: func(params)
