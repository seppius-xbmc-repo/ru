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
import xbmc, xbmcgui, xbmcplugin, urllib2, urllib, re, string, sys, os, traceback, time, random
from urllib import urlretrieve, urlcleanup

HEADER     = 'Opera/10.60 (X11; openSUSE 11.3/Linux i686; U; ru) Presto/2.6.30 Version/10.60'
url_tvjam  = 'http://tvjam.ru'

handle = int(sys.argv[1])

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
	remove=[('<span>',''),('</span>',''),('&amp;','&'),('<strong>',''),('</strong>',''),('&quot;',''),('<b>',''),('</b>','')]
	for trash, crap in remove:
		name=name.replace(trash, crap)
	return name

def clean_tab(name):
	remove = [('\t',''),('\n','')]
	for trash, crap in remove:
		name= name.replace(trash, crap)
	return name


def get_programs():
	try:
		req = urllib2.Request('http://www.tvjam.ru/channels')
		req.add_header('Referer', 'http://www.tvjam.ru')
		req.add_header('User-Agent', HEADER)
		f = urllib2.urlopen(req)
		a = f.read()
		f.close()
	except:
		return
	raw_prog = re.compile('<div class="channels-container">(.*?)<div class="sidebar">', re.DOTALL).findall(a)
	start_prog = clean_tab(raw_prog[0])
	last_prog = re.compile('<div class="channels-block"><div class="channels-pic"><a href="(.*?)"><span    class="bw"><img src="(.*?)" width="(.*?)" height="(.*?)" class="corner iradius30" alt="(.*?)" title="(.*?)" /></span><span class="color"><img src="(.*?)" width="(.*?)" height="(.*?)" class="corner iradius30" alt="(.*?)" title="(.*?)" /></span></a></div><div class="(.*?)">(.*?)<h3><a href="(.*?)">(.*?)</a></h3><p>(.*?)</p><div class="channels-info">(.*?)</div></div></div>', re.DOTALL).findall(start_prog)
	if len(last_prog) > 0:
		x = 1
		for row_1, row_2, row_3, row_4, row_5, row_6, row_7, row_8, row_9, \
		    row_10, row_11, row_12, row_13, row_14, row_15, row_16, row_17 in last_prog:
			caption = clean(row_6)
			row_7 = row_7.replace('//', '/')
			img_url = url_tvjam + row_7
			pathurl = url_tvjam + row_1
			plot    = row_16
			plotraw = re.compile("(.*)<a.*a>").findall(row_16)
			if len(plotraw) != 0:
				plot = plotraw[0]
			#xbmc.output('row_1 =  %s' % row_1)
			#xbmc.output('row_2 =  %s' % row_2)
			#xbmc.output('row_6 =  %s' % row_6)
			#xbmc.output('row_7 =  %s' % row_7)
			#xbmc.output('row_11 = %s' % row_11)
			#xbmc.output('row_13 = %s' % row_13)
			#xbmc.output('row_14 = %s' % row_14)
			#xbmc.output('row_15 = %s' % row_15)
			#xbmc.output('row_16 = %s' % row_16)
			#xbmc.output('row_17 = %s' % row_17)
			listitem = xbmcgui.ListItem(str(x) + '. ' + caption, iconImage = img_url, thumbnailImage = img_url)
			listitem.setInfo(type = "Video", infoLabels = {
				"Title": 	caption,
				"Studio": 	url_tvjam,
				"Plot": 	plot,
				"Genre": 	row_17 } )
			url = sys.argv[0] + "?mode=channel&url=" + urllib.quote_plus(url_tvjam + row_1)
			xbmcplugin.addDirectoryItem(handle, url, listitem, True)
			x = x+1

def get_channels(url):
	try:
		req = urllib2.Request(url)
		req.add_header('Referer', 'http://www.tvjam.ru')
		req.add_header('User-Agent', HEADER)
		f = urllib2.urlopen(req)
		a = f.read()
		f.close()
	except:
		return

	raw_chan = re.compile('<div class="plot-block-in">(.*?)</div></div>', re.DOTALL).findall(a)
	if len(raw_chan) > 0:
		y = 1
		for row_1 in raw_chan:
			#xbmc.output('row_1 %s' % row_1)
			data1 = re.compile('<a href="(.*?)">').findall(row_1)
			data2 = re.compile('<img src="(.*?)".*/>').findall(row_1)
			data3 = re.compile('<h3><a href=".*">(.*?)</a></h3>').findall(row_1)
			data4 = re.compile('<span>(.*?)</span>').findall(row_1)
			full_url = url_tvjam + data1[0]
			imag_url = data2[0]
			name     = clean(data3[0])
			plot = name
			if len(data4) != 0:
				plot     = clean(data4[0])
			listitem = xbmcgui.ListItem(str(y) + '. ' + name, iconImage = imag_url, thumbnailImage = imag_url)
			listitem.setInfo(type = "Video", infoLabels = {
				"title": 	name,
				"studio": 	url_tvjam,
				"aired":	plot,
				"premiered":	plot,
				"director":	url_tvjam,
				"plot":		plot})
			wurl = sys.argv[0] + "?mode=page&url=" + urllib.quote_plus(full_url)
			xbmcplugin.addDirectoryItem(handle, wurl, listitem, False)
			y = y + 1

	pager = re.compile('<a href="\?page=(.*?)" class="">(.*?)</a>').findall(a)
	cntpg = len(pager)
	if cntpg != 0:
		for x in range(cntpg):
			if pager[x][0] == pager[x][1]:
				Cap = 'To page ' + pager[x][0]
				listitem = xbmcgui.ListItem(Cap)
				listitem.setInfo(type = "Video", infoLabels = {
					"Title": 	Cap,
					"Studio": 	url_tvjam } )
				url = sys.argv[0] + "?mode=channel&url=" + urllib.quote_plus(url + '?page=' + pager[x][0])
				xbmcplugin.addDirectoryItem(handle, url, listitem, True)

def get_page(url):
	xbmc.output('*** get_page(%s)' % url)
	try:
		req = urllib2.Request(url)
		req.add_header('Referer', 'http://www.tvjam.ru')
		req.add_header('User-Agent', HEADER)
		f = urllib2.urlopen(req)
		a = f.read()
		f.close()
	except:
		return


	raw_data = re.compile('<embed id="player".*video_id=(.[0-9]*).*</embed>').findall(a)
	if len(raw_data) == 0:
		return
	xml_url = '%s/video/%s.xml' % (url_tvjam, raw_data[0])
	try:
		req = urllib2.Request(xml_url)
		req.add_header('Referer', url)
		req.add_header('User-Agent', HEADER)
		f = urllib2.urlopen(req)
		a = f.read()
		f.close()
	except:
		return

	rbw_data = re.compile('<movie id="(.*?)" name="(.*?)" posted="(.*?)">.*<title>(.*?)</title>.*<duration>(.*?)</duration>.*<views>(.*?)</views>.*<preview>(.*?)</preview>.*<video>(.*?)</video>.*<link>(.*?)</link>.*<embed>', re.DOTALL).findall(a)
	if len(rbw_data) > 0:
		(flm_id, auth_nick, posted, name, dursec, views, img_url, videodata, full_url) = rbw_data[0]
		#xbmc.output('get_page flm_id    = %s' % flm_id)
		#xbmc.output('get_page auth_nick = %s' % auth_nick)
		#xbmc.output('get_page posted    = %s' % posted)
		#xbmc.output('get_page name      = %s' % name)
		#xbmc.output('get_page dursec    = %s' % dursec)
		#xbmc.output('get_page views     = %s' % views)
		#xbmc.output('get_page img_url   = %s' % img_url)
		#xbmc.output('get_page videodata = %s' % videodata)
		#xbmc.output('get_page full_url  = %s' % full_url)
		hdata = re.compile('<link title="(.*?)" bps="(.*?)".*>(.*?)</link>').findall(videodata)
		dialog = xbmcgui.Dialog()
		list = []
		spcn = len(hdata)
		if spcn == 1:
			selected = 0
		else:
			for x in range(spcn):
				list.append(hdata[x][0] + ' (' + str(hdata[x][1])  + ' bps)')
			selected = dialog.select('Quality?', list)
		if selected < 0:
			return
		video_type    = hdata[selected][0]
		video_bytrate = hdata[selected][1]
		video_mp4url  = hdata[selected][2]
		listitem = xbmcgui.ListItem(name, iconImage = img_url, thumbnailImage = img_url)
		listitem.setInfo(type = "Video", infoLabels = {
			"title": 	name,
			"studio": 	url_tvjam,
			"credits":	auth_nick,
			"aired":	posted,
			"premiered":	posted,
			"writer":	auth_nick,
			"director":	auth_nick,
			"plot":		'Views: ' + str(views)})
		playList = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
		playList.clear()
		playList.add(video_mp4url, listitem)
		player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
		player.play(playList)

params = get_params()
mode  = None

try:
	mode  = urllib.unquote_plus(params["mode"])
except:
	pass
try:
	url  = urllib.unquote_plus(params["url"])
except:
	pass

if mode == None:
	get_programs()
	xbmcplugin.setPluginCategory(handle, 'TVJAM.RU')
	xbmcplugin.endOfDirectory(handle)

elif mode == 'channel':
	get_channels(url)
	xbmcplugin.setPluginCategory(handle, 'TVJAM.RU')
	xbmcplugin.endOfDirectory(handle)

elif mode == 'page':
	get_page(url)

