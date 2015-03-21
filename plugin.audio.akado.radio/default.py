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
import urllib,urllib2,re,sys,os
import xbmcplugin,xbmcgui

pluginhandle = int(sys.argv[1])
thumb = os.path.join(os.getcwd().replace(';', ''), "icon.png" )

def getURL(url):
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Opera/10.60 (X11; openSUSE 11.3/Linux i686; U; ru) Presto/2.6.30 Version/10.60')
	req.add_header('Accept', 'text/html, application/xml, application/xhtml+xml, */*')
	req.add_header('Accept-Language', 'ru,en;q=0.9')
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	return link

def root(url):
	http = getURL(url)
	r1 = re.compile('<div class="st">(.*?)</div></div></div>').findall(http)
	if len(r1)==0: return False
	for rb in r1:
		rb += '#@#'
		xbmc.output('rb=%s'%rb)

		img = thumb
		imbb = re.compile('<img src="(.*?)" class="logo"').findall(rb)
		if len(imbb) > 0:
			img = 'http://radio.akado.ru'+ imbb[0]
		vurl = ''
		title = re.compile('title="(.*?)"').findall(rb)[0]
		playblock = re.compile('<div class="play">(.*?)#@#').findall(rb)
		if len(playblock) > 0:
			purlblock = re.compile('<a href="(.*?)">').findall(playblock[0])
			if len(purlblock) > 0:
				vurl = purlblock[0]
		uri = vurl
		if uri != '':
			item=xbmcgui.ListItem(title, iconImage=img, thumbnailImage=img)
			item.setInfo(type='music', infoLabels={'title': title})
			item.setProperty('IsPlayable', 'true')
			item.setProperty('fanart_image',img)
			xbmcplugin.addDirectoryItem(pluginhandle,uri,item)
	xbmcplugin.endOfDirectory(pluginhandle)

root('http://radio.akado.ru/')

