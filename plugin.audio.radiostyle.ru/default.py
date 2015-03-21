#!/usr/bin/python
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
__scriptname__ = "RADIOSTYLE.RU"

import xbmc, xbmcgui, xbmcplugin, urllib2, urllib, re, string, sys, os, traceback
from urllib import urlretrieve, urlcleanup
HEADER     = 'Opera/9.80 (Linux; openSUSE 11.2 (i586); U; ru) Presto/2.2.15 Version/10.00'

handle     = int(sys.argv[1])
BASE_PLUGIN_THUMBNAIL_PATH = os.path.join( os.getcwd(), "resources" )
play_thumb = os.path.join( BASE_PLUGIN_THUMBNAIL_PATH, "MusicPlay.png" )
path_thumb = os.path.join( BASE_PLUGIN_THUMBNAIL_PATH, "MusicFolder.png" )
url_RADIOSTYLE    = 'http://www.radiostyle.ru'
thumb      = os.path.join( os.getcwd().replace(';', ''), "icon.png" )

def showMessage(heading, message, times = 3000):
#	heading = heading.encode('utf-8')
#	message = message.encode('utf-8')
	xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, thumb))


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

def clean(name):
	remove=[('  ',''),('\n',' ')]
	for trash, crap in remove:
		name=name.replace(trash, crap)
	return name

def get_rootmenu():
	try:
		req = urllib2.Request(url_RADIOSTYLE + '/catalog.php?view=genre')
		req.add_header('User-Agent', HEADER)
		f = urllib2.urlopen(req)
		a = f.read()
		f.close()
		s_uni = a.decode('cp1251')
		a = s_uni.encode('utf8')
	except:
		return
	stage1 = re.compile("<div class='ctn'>(.*?)<br><br>\s", re.DOTALL).findall(a)
	if len(stage1) > 0:
		stage2all = re.compile("<a href='(.*?)'>(.*?)</a>(.*?)<br>").findall(stage1[0])
		if len(stage2all) > 0:
			x=1
			for cat_url, cat_name, cat_count in stage2all:
				listitem=xbmcgui.ListItem(str(x) + '. ' + cat_name + cat_count, \
					iconImage = path_thumb, thumbnailImage = path_thumb)
				listitem.setInfo(type = "Music", infoLabels = {
					"Title": 	cat_name,
					"Album":	url_RADIOSTYLE,
					"Genre": 	cat_name } )
				url = sys.argv[0] + "?mode=getgroup&url=" + urllib.quote_plus(url_RADIOSTYLE+cat_url) + \
					"&name=" + urllib.quote_plus(cat_name)
				xbmcplugin.addDirectoryItem(handle, url, listitem, True)
				x = x + 1

def get_programs(url, name):
	try:
		req = urllib2.Request(url)
		req.add_header('User-Agent', HEADER)
		f = urllib2.urlopen(req)
		a = f.read()
		f.close()
		s_uni = a.decode('cp1251')
		a = s_uni.encode('utf8')
	except:
		return
	stage1 = re.compile("<td>(.*?)</td>\s*<td><a href=\"(.*?)\">(.*?)</a>\s\s.*<a href='(.*?)'><img src='(.*?)'></a>\s*<a href='(.*?)'><img src='(.*?)'></a></td><td>(.*?)</td><td>(.*?)</td>").findall(a)
	if len(stage1) > 0:
		for IDX, BlogURL, NAME, M3URL, M3ICO, ASXURL, ASXICO, PlaceBlock, RATE in stage1:
			BlogURL = url_RADIOSTYLE + '/' + BlogURL
			M3URL   = url_RADIOSTYLE + '/' + M3URL
			ASXURL  = url_RADIOSTYLE + '/' + ASXURL
			M3ICO   = url_RADIOSTYLE + M3ICO
			ASXICO  = url_RADIOSTYLE + ASXICO
			PlaceBlock = PlaceBlock + '</a>'
			#xbmc.output('_______IDX = [%s]'%IDX)
			#xbmc.output('___BlogURL = [%s]'%BlogURL)
			#xbmc.output('______NAME = [%s]'%NAME)
			#xbmc.output('_____M3URL = [%s]'%M3URL)
			#xbmc.output('_____M3ICO = [%s]'%M3ICO)
			#xbmc.output('____ASXURL = [%s]'%ASXURL)
			#xbmc.output('____ASXICO = [%s]'%ASXICO)
			#xbmc.output('PlaceBlock = [%s]'%PlaceBlock)
			#xbmc.output('______RATE = [%s]'%RATE)

			plBlock = re.compile("<a href='(.*?)'>(.*?)</a>").findall(PlaceBlock)
			Place = 'Unknown'
			try:	Place = plBlock[0][1]
			except: pass
			try:	Place = plBlock[0][1] + '/' + plBlock[1][1]
			except: pass

			Title = '%s. %s (%s)' % (IDX, NAME, Place)

			listitem = xbmcgui.ListItem(Title, iconImage = play_thumb, thumbnailImage = play_thumb)
			listitem.setInfo(type = "Music", infoLabels = {
				"Title": 	Title,
				"Album":	url_RADIOSTYLE,
				"Genre": 	name } )
			xbmcplugin.addDirectoryItem(handle, M3URL, listitem, False)
	else:
		showMessage('ERROR', 'stage1 not found')

	stage_pg = re.compile('</table>(.*?)&nbsp<br><br>').findall(a)
	if len(stage_pg) > 0:
		pg_row = re.compile("<a href='(.*?)'>(.*?)</a>").findall(stage_pg[0])
		if len(pg_row) > 0:
			for pg_url, pg_name in pg_row:
				pg_url = url_RADIOSTYLE + pg_url
				listitem=xbmcgui.ListItem('Page ' + pg_name)
				url = sys.argv[0] + "?mode=getgroup&url=" + urllib.quote_plus(pg_url) + \
					"&name=" + urllib.quote_plus(name)
				xbmcplugin.addDirectoryItem(handle, url, listitem, True)

params = get_params()
url  =	None
mode =	None
name =	''

try:
	url = urllib.unquote_plus(params["url"])
except:
	pass
try:
	mode = urllib.unquote_plus(params["mode"])
except:
	pass
try:
	name = urllib.unquote_plus(params["name"])
except:
	pass

if   mode == None:
	get_rootmenu()

elif mode == 'getgroup':
	get_programs(url, name)

xbmcplugin.setPluginCategory(handle, __scriptname__)
xbmcplugin.endOfDirectory(handle)


