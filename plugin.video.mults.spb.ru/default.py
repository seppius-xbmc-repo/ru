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

import xbmc, xbmcgui, xbmcplugin, xbmcaddon, os, urllib, httplib, socket, sys, re
import socket
socket.setdefaulttimeout(12)

h = int(sys.argv[1])
__addon__ = xbmcaddon.Addon(id='plugin.video.mults.spb.ru')
icon   = xbmc.translatePath(__addon__.getAddonInfo('path') + 'icon.png')
inext  = xbmc.translatePath(__addon__.getAddonInfo('path') + 'next.png')
ivideo = xbmc.translatePath(__addon__.getAddonInfo('path') + 'video.png')


def showMessage(heading, message, times = 3000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))

def clean(name):
	remove=[('\t',''),('  ',' '),('&ndash;',''),('<br>','\n'),('<br />','\n'),('&amp;','&'),('&quot;','"'),('&#39;','\''),('&nbsp;',' '),('&laquo;','"'),('&raquo;', '"'),('&#151;','-')]
	for trash, crap in remove:
		name=name.replace(trash, crap)
	return name

def GET(target):
	conn = httplib.HTTPConnection(host='mults.info', port=80)
	html_headers = {
		'User-Agent': 'XBMC/10-series (Python addon; XBMC-Russia; HD-lab Team; 2011; http://www.xbmc.org)', \
		'Host':		'mults.info', \
		'Accept':	'text/html, application/xml, application/xhtml+xml, */*', \
		'Cookie':	'rules=yes' }
	conn.request(method='GET', url=target, headers=html_headers)
	response = conn.getresponse()
	html = response.read().decode('cp1251', "ignore").encode('utf8', "ignore")
	conn.close()
	return html

def getsearch(params):
	KB = xbmc.Keyboard()
	KB.setHeading('Что ищем?')
	KB.doModal()
	if (KB.isConfirmed()):
		getmenu({'search':urllib.quote_plus(KB.getText().decode('utf8', "replace").encode('cp1251', "replace"))})
	else:
		return False

def getmenu(params):
	try:
		search = params['search']
		ss = '&s=%s&t=AND' % search
	except:
		search = ''
		ss = ''
	if search == '':
		uri = '%s?mode=getsearch'%sys.argv[0]
		li = xbmcgui.ListItem('Поиск?', iconImage = icon, thumbnailImage = icon)
		xbmcplugin.addDirectoryItem(h, uri, li, True)
	try:    page = int(urllib.unquote_plus(params['page']))
	except: page = 1
	http = GET('/mults/?wp=1&wf=1&p=%d%s'%(page,ss))
	row = re.compile('<TD.+?<A href=\'(.*?)\'.+?<IMG.+?src=\'(.*?)\'.+?<BR>(.*?)</A></TD>', re.DOTALL).findall(http)
	found_items = len(row)
	if found_items > 0:
		for new_target, new_image, new_name in row:
			new_image = 'http://mults.info' + new_image
			uri = '%s?mode=playpage'%sys.argv[0]
			uri += '&href=%s' % urllib.quote_plus('/mults/?id=%d' % int(re.compile('/mults/\?id=(.[0-9]+)').findall(new_target)[0]))
			uri += '&name=%s' % urllib.quote_plus(new_name)
			uri += '&search=%s' % search
			li = xbmcgui.ListItem(new_name, iconImage = new_image, thumbnailImage = new_image)
			xbmcplugin.addDirectoryItem(h, uri, li, False)
		if (found_items > 99):
			uri = '%s?mode=getmenu&page=%d' % (sys.argv[0], page + 1)
			li = xbmcgui.ListItem('Далее >', iconImage = inext, thumbnailImage = inext)
			xbmcplugin.addDirectoryItem(h, uri, li, True)
	else:
		showMessage('Ой', 'Показать нечего', 5000)
		return False
	xbmcplugin.endOfDirectory(h)

def playpage(params):
	try:    href = urllib.unquote_plus(params['href'])
	except: href = '/'
	try:    name = urllib.unquote_plus(params['name'])
	except: name = 'No name'
	try:
		descr = urllib.unquote_plus(params['descr'])
		descr = descr.replace('(','').replace(')','')
	except: descr = ''
	mults_http = GET(href)
	try:
		(Pid, flvu, imgu) = re.compile("show_flv\((.+?), '(.+?)', '(.+?)'\)").findall(mults_http)[0]
		imgu = 'http://mults.info/screen/' + imgu
	except:
		imgu = icon
	try:
		file_url = re.compile("<a href='(.+?)' title='Скачать мультфильм через HTTP'>").findall(mults_http)[0]
		file_url = 'http://mults.info' + file_url
		li = xbmcgui.ListItem(name, iconImage=imgu, thumbnailImage=imgu)
		li.setInfo(type = 'video', infoLabels={'studio':descr, 'genre':'Мультфильм', 'studio':'http://mults.info/'})
		xbmc.Player().play(file_url, li)
	except:
		return False

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
except: getmenu(params)
if mode != None:
	try:    func = globals()[mode]
	except: pass
	if func: func(params)
