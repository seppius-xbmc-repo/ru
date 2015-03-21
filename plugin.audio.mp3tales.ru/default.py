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
icon   = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'icon.png'))
vinil = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'vinil.png'))


def showMessage(heading, message, times = 3000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))

def clean(name):
	remove=[('\t',''),('  ',' '),('&ndash;',''),('<br>','\n'),('<br />','\n'),('&amp;','&'),('&quot;','"'),('&#39;','\''),('&nbsp;',' '),('&laquo;','"'),('&raquo;', '"'),('&#151;','-')]
	for trash, crap in remove:
		name=name.replace(trash, crap)
	return name

def GET(target):
	conn = httplib.HTTPConnection(host='mp3tales.ru', port=80)
	html_headers = {
		'User-Agent': 'XBMC/10-series (Python addon; XBMC-Russia; HD-lab Team; 2011; http://www.xbmc.org)', \
		'Host':		'mp3tales.ru', \
		'Accept':	'text/html, application/xml, application/xhtml+xml, */*' } # 'Cookie':	'rules=yes'
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
	http = GET('/tales/?p=%d%s'%(page,ss))
	row = re.compile("<li class='item'><a href='(.*?)'>(.*?)</a>", re.DOTALL).findall(http)
	found_items = len(row)
	if found_items > 0:
		for new_target, new_name in row:
			new_name = new_name.replace('<b>','').replace('</b>','')
			uri = '%s?mode=playpage'%sys.argv[0]
			uri += '&href=%s' % urllib.quote_plus(new_target)
			uri += '&name=%s' % urllib.quote_plus(new_name)
			uri += '&search=%s' % search
			li = xbmcgui.ListItem(new_name, iconImage = vinil, thumbnailImage = vinil)
			xbmcplugin.addDirectoryItem(h, uri, li, False)
		if (found_items >24):
			uri = '%s?mode=getmenu&page=%d' % (sys.argv[0], page + 1)
			li = xbmcgui.ListItem('Далее >', iconImage = icon, thumbnailImage = icon)
			xbmcplugin.addDirectoryItem(h, uri, li, True)
	else:
		showMessage('Ой', 'Показать нечего', 5000)
		return False
	xbmcplugin.endOfDirectory(h)


def playpage(params):
	try:    href = urllib.unquote_plus(params['href'])
	except: href = '/'
	http = GET(href)
	try:    name = urllib.unquote_plus(params['name'])
	except: name = 'No name'
	furl = 'http://mp3tales.ru' + re.compile('file: "(.*?)",').findall(http)[0]
	try:
		fimg = 'http://mp3tales.ru' + re.compile('<img src="(.*?)" ').findall(http)[0]
	except:
		fimg = vinil
	li = xbmcgui.ListItem(name, iconImage=fimg, thumbnailImage=fimg)
	li.setInfo(type = 'music', infoLabels={'title':name, 'genre':'Мультфильм', 'album':'http://mp3tales.ru/'})
	xbmc.Player().play(furl, li)

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
