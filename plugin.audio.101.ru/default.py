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
import socket
import xbmc, xbmcgui, xbmcaddon, xbmcplugin, urllib2, urllib, re, string, sys, os, traceback
from urllib import urlretrieve, urlcleanup

from locale import getdefaultlocale

__settings__ = xbmcaddon.Addon(id='plugin.audio.101.ru')
__language__ = __settings__.getLocalizedString


HEADER     = 'Opera/10.60 (X11; openSUSE 11.3/Linux i686; U; ru) Presto/2.6.30 Version/10.60'
handle     = int(sys.argv[1])
BASE_PLUGIN_THUMBNAIL_PATH = os.path.join( os.getcwd().replace(';', ''), "resources" )
play_thumb = os.path.join( BASE_PLUGIN_THUMBNAIL_PATH, "MusicPlay.png" )
path_thumb = os.path.join( BASE_PLUGIN_THUMBNAIL_PATH, "MusicFolder.png" )
thumb      = os.path.join( os.getcwd().replace(';', ''), "icon.png" )

url_101    = 'http://www.101.ru'
PLUGIN_NAME = '101.RU'
url_chan_all = url_101 + '/?an=port_allchannels'
url_cat_all  = url_101 + '/?an=port_groupchannels'
socket.setdefaulttimeout(10)


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


def getURL(url, ref = url_101 + '/'):
	xbmc.output('>>> getURL(%s)'%url)
	try:
		req = urllib2.Request(url)
		req.add_header('User-Agent', HEADER)
		req.add_header('Accept', 'text/html, application/xml, application/xhtml+xml, */*')
		req.add_header('Accept-Language', 'ru,en;q=0.9')
		req.add_header('Referer', ref)
		response = urllib2.urlopen(req)
		http = response.read().decode('cp1251').encode('utf8')
		response.close()
	except urllib2.URLError, e:
		xbmcgui.Dialog().ok('HTTP ERROR', str(e))
		return None
	else:
		#print http
		return http



''' *********************************************************************** '''


def get_rootmenu(url):

	http = getURL(url)
	if http == None: return False

	s1 = re.compile('<div id="radio_menu">\s.*<ul>(.+?)</ul>\s.*</div>', re.DOTALL).findall(http)
	if len(s1) == 0: return False

	cat_name = 'Все каналы 101.RU'
	item = xbmcgui.ListItem(cat_name, iconImage = path_thumb, thumbnailImage = path_thumb)
	item.setInfo(type='music', infoLabels = {'title': cat_name, 'album': url_101, 'genre': cat_name, 'artist': '101.RU'})
	uri = sys.argv[0] + '?mode=getall'
	uri += '&url='  + urllib.quote_plus(url_chan_all)
	uri += '&name=' + urllib.quote_plus(cat_name)
	xbmcplugin.addDirectoryItem(handle, uri, item, True)

	s2 = re.compile('<li id="(.+?)"><a href="(.+?)" id="(.+?)">(.+?)</a> <span id="(.+?)">(.+?)</span></li>').findall(s1[0])
	if len(s2) > 0:
		x = 1
		for data1, cat_url, data2, cat_name, data3, cat_count in s2:
			cat_url   = url_101 + cat_url.replace(' ', '').replace('&amp;', '&')
			item = xbmcgui.ListItem('%s. %s (%s)'%(x,cat_name,cat_count.replace(' ', '')), iconImage = path_thumb, thumbnailImage = path_thumb)
			item.setInfo(type='music', infoLabels = {'title': cat_name, 'album': cat_url, 'genre': cat_name, 'artist': '101.RU'})
			uri = sys.argv[0] + '?mode=getgroup'
			uri += '&url='  + urllib.quote_plus(cat_url)
			uri += '&name=' + urllib.quote_plus(cat_name)
			xbmcplugin.addDirectoryItem(handle, uri, item, True)
			x += 1
	xbmcplugin.endOfDirectory(handle)


def getgroup(url, name, modeALL):

	def addItemS(target, cat_name, ch_name, ch_plot, intera):
		ch_plot = clean(ch_plot)
		ch_name = ch_name.replace(' ', '')
		if modeALL: caption = '%s : %s'%(cat_name,ch_name)
		else: caption = '%s. %s'%(intera,ch_name)
		item = xbmcgui.ListItem(caption, iconImage = play_thumb, thumbnailImage = play_thumb)
		item.setInfo(type='music', infoLabels = {'title': ch_name, 'album': clean(ch_plot), 'genre': cat_name, 'artist': '101.RU'})
		uri = sys.argv[0] + '?mode=getplay'
		uri += '&name=' + urllib.quote_plus(ch_name)
		uri += '&url=' + urllib.quote_plus(url_101 + target.replace(' ', '').replace('&amp;', '&'))
		#item.setProperty('IsPlayable', 'true')
		xbmcplugin.addDirectoryItem(handle, uri, item, False)

	http = getURL(url)
	if http == None:
		return False
	s1 = re.compile('<div class="radio_list">(.+?)<div id="aux">', re.MULTILINE| re.DOTALL).findall(http)
	if len(s1) == 0:
		showMessage('ERROR', 'class="radio_list" - can not parsed')
		return False
	s2 = re.compile('<h2>(.+?)</div></li>\s\n</ul>', re.MULTILINE| re.DOTALL).findall(s1[0])
	if len(s2) == 0:
		showMessage('ERROR', 's2 block <h2> .. </ul> not found')
		return False
	for raw2 in s2:
		cat_raw = re.compile('<img src=".*" width=".*" height=".*" alt=".*">(.+?)</h2>').findall(raw2)
		if len(cat_raw) == 0:
			showMessage('ERROR', 'len(cat_raw) == 0')
			break
		cat_name = cat_raw[0]
		if modeALL:
			s3 = re.compile('<li><div class="schan">\s*<div class="play">(.+?)</div>\s*<div class="info">(.+?)</div></div>\s*</div>', re.DOTALL).findall(raw2)
		else:
			s3 = re.compile('<li><div class="schan">\s*<div class="play">(.+?)</div>\s*<div class="info">(.+?)</div></div>\s*<p>(.+?)</p>\s*</div>', re.DOTALL).findall(raw2)
		if len(s3) == 0:
			showMessage('ERROR', 's3 == 0')
			break
		x = 1
		for raw3 in s3:
			#cat_url_raw = re.compile('OpenWin\(\'(.+?)\'.*title=".*"').findall(raw3[0])
			#if len(cat_url_raw) == 0:
			#	showMessage('ERROR', 'len(cat_url_raw) == 0')
			#	xbmc.output(raw3[0])
			#	break
			#	<a href="/?an=port_channel_mp3&amp;channel=104" target="channel">

			cat_url_raw = re.compile('<a href="(.*?)" target="channel">').findall(raw3[0])

			if len(cat_url_raw) == 0:
				showMessage('ERROR', 'NEW len(cat_url_raw) == 0')
				xbmc.output(raw3[0])
				break

			#xbmc.output('cat_url_raw=%s'%cat_url_raw)

			plTarget = cat_url_raw[0].replace('&amp;', '&').replace('mp3', 'wma')

			xbmc.output('plTarget=%s'%plTarget)


			if modeALL:
				chandescr = re.compile(';">(.+?)</a></p>\s*<div class="chandescr" id=".*">(.+?)<p>.*</p><div id=".*">', re.DOTALL).findall(raw3[1])
				if len(chandescr) == 0: break
				(ch_name, ch_plot) = chandescr[0]
				addItemS(plTarget, cat_name, ch_name, ch_plot, x)
			else:
				onmouseover = re.compile('<h3><a href="(.+?)".*onmouseover.*;">(.+?)</a></h3>', re.DOTALL).findall(raw3[1])
				if len(onmouseover) == 0: break
				(ch_url, ch_name) = onmouseover[0]
				addItemS(plTarget, cat_name, ch_name, raw3[2], x)
			x += 1
	xbmcplugin.endOfDirectory(handle)


def get_play(url, name):
	xbmc.output('>>> get_play(%s, %s)' % (url, name))
	#use_wma = True
	#use_mp3 = True

	playList = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
	playList.clear()

#	if use_wma:
	#wma_url = url.replace('port_playmp3','port_playwma')
	wma0 = getURL(url)
	if wma0 != None:
		wma1 = re.compile('<param name="URL" value="(.*?)">').findall(wma0)
		if len(wma1) > 0:

			#xbmc.Player().play(wma1[0].replace('&amp;','&'))


			wma2 = getURL(wma1[0].replace('&amp;','&'))
			if wma2 != None:
				wma3 = re.compile('<ref href = "(.*?)"/>').findall(wma2)
				if len(wma3) > 0:
					x = 1
					stacked_url = ''
					for wma_purl in reversed(wma3):
						item = xbmcgui.ListItem('%s [WMA Server %s])'%(name,x),iconImage=play_thumb,thumbnailImage=play_thumb)
						item.setInfo(type='music',infoLabels={'title':name,'artist': '101.RU'})
						playList.add(wma_purl, item)
					xbmc.Player().play(playList)


#	if use_mp3:
#		mp3_url = url.replace('port_playwma','port_playmp3')
#		mp0 = getURL(mp3_url)
#		if mp0 != None:
#			mp1 = re.compile('"pl":"(.*?)"').findall(mp0)
#			if len(mp1) > 0:
#				cur_mpu = mp1[0].replace('|','&')
#				mp2 = getURL(cur_mpu, 'http://101.ru/101player/uppod7.swf')
#				mp3 = re.compile('"file":"(.*?)"').findall(mp2)
#				if len(mp3) > 0:
#					x = 1
#					for streamer in mp3:
#						item = xbmcgui.ListItem('Serv %s. %s (MP3)'%(x,name),iconImage=play_thumb,thumbnailImage=play_thumb)
#						item.setInfo(type='music',infoLabels={'title':name,'artist': '101.RU'})
#						xbmcplugin.addDirectoryItem(handle, streamer, item)
#	xbmcplugin.endOfDirectory(handle)


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

xbmc.output('START PLUGIN URL= %s'%url)

if   mode == None:
	listonly = __settings__.getSetting('listonly')
	if listonly == 'true': getgroup(url_chan_all, name, True)
	else: get_rootmenu(url_cat_all)

elif mode == 'getall':
	getgroup(url, name, True)

elif mode == 'getgroup':
	getgroup(url, name, False)

elif mode == 'getplay':
	get_play(url, name)

