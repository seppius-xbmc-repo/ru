#!/usr/bin/python
# -*- coding: utf-8 -*-


#/*
# *  Copyright (c) 2012 Teleplus, Teleplus Team, E-mail: boss@teleplus.ru
# *  Writer (c) 2012, Krilov V.A., E-mail: boss@teleplus.ru
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




import urllib2, re, xbmc, xbmcgui, xbmcplugin, xbmcaddon, os, urllib, urllib2, socket

socket.setdefaulttimeout(12)

PLUGIN_ID = 'plugin.audio.teleplus.ru'
__settings__ = xbmcaddon.Addon(id=PLUGIN_ID)
__language__ = __settings__.getLocalizedString
USERNAME = __settings__.getSetting('username')
USERPASS = __settings__.getSetting('password')
handle = int(sys.argv[1])
icon = os.path.join( os.getcwd(), "icon.png" )




def showMessage(heading, message, times = 5000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))




def strip_html(text):
	def fixup(m):
		text = m.group(0)
		if text[:1] == "<":
			if text[1:3] == 'br':
				return '\n'
			else:
				return ""
		if text[:2] == "&#":
			try:
				if text[:3] == "&#x":
					return chr(int(text[3:-1], 16))
				else:
					return chr(int(text[2:-1]))
			except ValueError:
				pass
		elif text[:1] == "&":
			import htmlentitydefs
			if text[1:-1] == "mdash":
				entity = " - "
			elif text[1:-1] == "ndash":
				entity = "-"
			elif text[1:-1] == "hellip":
				entity = "-"
			else:
				entity = htmlentitydefs.entitydefs.get(text[1:-1])
			if entity:
				if entity[:2] == "&#":
					try:
						return chr(int(entity[2:-1]))
					except ValueError:
						pass
				else:
					return entity
		return text
	ret =  re.sub("(?s)<[^>]*>|&#?\w+;", fixup, text)
	return re.sub("\n+", '\n' , ret)




def GET(url):
	try:
		req = urllib2.Request(url)
		f = urllib2.urlopen(req)
		content = f.read()
		f.close()
		return content
	except:
		showMessage('Не могу открыть URL', url)
		return None



def MAIN():

	arr = re.compile('key=(.+?)$').findall(sys.argv[2])
	if len(arr) > 0: key = arr[0]
	else: key = '0'

	content = GET('http://teleplus.ru/util/audio_content.php?key=%s&login=%s&password=%s'%(key,USERNAME,USERPASS))
	if content == None: return False

	if content.count('wrong auth') :
		dialog = xbmcgui.Dialog()
		dialog.ok( __language__(2002), __language__(2003))
		__settings__.openSettings()
		return False

	if content.count('subs expire') :
		dialog = xbmcgui.Dialog()
		dialog.ok( __language__(2004), __language__(2005))
		return False

	arr = re.compile('{(.+?);(.+?);(.+?)}').findall(content)
	if len(arr) > 0:

		for key, name, img in arr:

			name = strip_html(name).decode('windows-1251')

			img = 'http://teleplus.ru' + img

			item = xbmcgui.ListItem(name, iconImage=img, thumbnailImage=img)

			url = sys.argv[0] + '?key=' + key

			xbmcplugin.addDirectoryItem(handle, url, item, True)

		xbmcplugin.endOfDirectory(handle)
		return False

	xbmc.executebuiltin("xbmc.PlayMedia("+content+")")




MAIN()
