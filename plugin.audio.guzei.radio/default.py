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
import xbmc, xbmcgui, xbmcplugin, urllib2, urllib, re, string, sys, os, traceback, xbmcaddon
from urllib import urlretrieve, urlcleanup

HEADER      = 'Opera/10.60 (X11; openSUSE 11.3/Linux i686; U; ru) Presto/2.6.30 Version/10.60'
GUZEI_RADIO = 'GUZEI.RADIO'


handle = int(sys.argv[1])

__settings__ = xbmcaddon.Addon(id='plugin.audio.guzei.radio')
__language__ = __settings__.getLocalizedString

BASE_PLUGIN_THUMBNAIL_PATH = os.path.join( os.getcwd(), "resources" )
play_thumb   = os.path.join(BASE_PLUGIN_THUMBNAIL_PATH, "PlayOnGreen.png")

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
	remove=[('  ','^|$'),('\n',' '),('^|$',' ')]
	for trash, crap in remove:
		name=name.replace(trash, crap)
	return name

def clean2(name):
	remove=[('(',''),(')',''),(':',''),('  ',' ')]
	for trash, crap in remove:
		name=name.replace(trash, crap)
	return name

def get_programs():
	try:
		req = urllib2.Request('http://guzei.com/online_radio/list')
		req.add_header('User-Agent', HEADER)
		f = urllib2.urlopen(req)
		a = f.read()
		f.close()
	except:
		return
	stage1 = re.compile('<tr><td>'+__language__(30000).encode('utf-8')+'(.*?)</td></tr>').findall(a)[0]
	if len(stage1) == 0:
		return
	stage2 = re.compile('<td title="(.+?)"><a target="_top" href="(.+?)">(.+?)</a></td>').findall(stage1)
	if len(stage2) == 0:
		return
	for st_name, st_url, st_count in stage2:
		Caption = st_name
		new_name = re.compile('.*&quot;(.+?)&quot;.*').findall(st_name)
		if len(new_name) > 0:
			Caption = new_name[0]
		Title = Caption+' ('+str(st_count)+')'
		listitem=xbmcgui.ListItem(Title, iconImage=play_thumb, thumbnailImage=play_thumb)
		listitem.setInfo(type="Music", infoLabels = {
			"Title":	Title,
			"Studio":	GUZEI_RADIO,
			"Plot":		st_name,
			"Genre":	Caption } )
		url = sys.argv[0]+"?list="+urllib.quote_plus(st_url)+'&genre='+urllib.quote_plus(Caption)
		xbmcplugin.addDirectoryItem(handle, url, listitem, True)


def get_list(url, genre):
	try:
		req = urllib2.Request(url)
		req.add_header('User-Agent', HEADER)
		f = urllib2.urlopen(req)
		a = f.read()
		f.close()
	except:
		return
	stage1 = re.compile('<ol>(.+?)</ol>', re.DOTALL).findall(a)[0]
	if len(stage1) == 0:
		return
	stage2 = re.compile('<li>(.+?)</li>').findall(stage1)
	if len(stage2) == 0:
		return
	for stage2x in stage2:
		(r_rates, r_name, r_city, r_plot) = re.compile('(.+)<span class="r">(.+?)</span>(.+?)<a class="name".*</a>(.+)').findall(stage2x + ' ')[0]
		speeds = re.compile('<a class="name" href="(.+?)">(.+?)</a>').findall(stage2x)
		spd_cnt = len(speeds)
		if spd_cnt == 0:
			return
		r_rates = clean2(r_rates)
		r_name  = clean2(r_name)
		r_city  = clean2(r_city)
		r_plot  = clean2(r_plot)
		u1 = ''
		x  = 0
		for run_url, run_speed in speeds:
			run_id = re.compile('.*id=([0-9]*)').findall(run_url)[0]
			u1 = u1 + '&spd'+str(x)+'='+run_speed+'&id'+str(x)+'='+run_id
			x=x+1
		url = sys.argv[0]+"?speeds="+str(spd_cnt)+u1+'&rate='+urllib.quote_plus(r_rates)+ \
			'&name='+urllib.quote_plus(r_name)+'&city='+urllib.quote_plus(r_city)+ \
			'&plot='+urllib.quote_plus(r_plot)+'&genre='+urllib.quote_plus(genre)
		listitem=xbmcgui.ListItem(r_name, iconImage=play_thumb, thumbnailImage=play_thumb)
		listitem.setInfo(type="Music", infoLabels = {
			"Title":	r_name,
			"Studio":	r_city,
			"Plot":		r_plot,
			"Genre":	genre } )
		xbmcplugin.addDirectoryItem(handle, url, listitem, False)


def get_play(url, rate, name, city, plot, genre):
	try:
		req = urllib2.Request(url)
		req.add_header('User-Agent', HEADER)
		f = urllib2.urlopen(req)
		a = f.read()
		f.close()
	except:
		return

	#xbmc.output(a)


	play_url = None

	r0 = re.compile('<embed.*src="(.*?)".*</embed>', re.DOTALL).findall(a)
	cnt = len(r0)


	if cnt > 0:
		play_url = r0[cnt-1]
	else: return False
	if play_url == None: return False

	#play_url = re.compile("<script>player\(\'(.*?)\'\,'\.*'\)</script>", re.DOTALL).findall(a)[0]

	if len(play_url) == 0:
		return
	playList = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
	playList.clear()

	listitem=xbmcgui.ListItem(name,iconImage=play_thumb,thumbnailImage=play_thumb)
	listitem.setInfo(type="Music", infoLabels = {
		"Title": 	name,
		"Studio": 	city,
		"Plot": 	plot,
		"Artist":	GUZEI_RADIO,
		"Genre": 	genre } )
	xbmc.output(play_url)
	playList.add(play_url, listitem)
	player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
	player.play(playList)



params = get_params()
list_url    = None
list_speeds = 0


try:
	list_url = urllib.unquote_plus(params["list"])
except:
	pass
try:
	list_speeds = params["speeds"]
except:
	pass

if len(params) == 0:
	get_programs()
	xbmcplugin.setPluginCategory(handle, GUZEI_RADIO)
	xbmcplugin.endOfDirectory(handle)

elif list_url != None:
	list_genre = __language__(30001)
	try:
		list_genre = urllib.unquote_plus(params["genre"])
	except:
		pass
	get_list(list_url, list_genre)
	xbmcplugin.setPluginCategory(handle, GUZEI_RADIO+' / '+list_genre)
	xbmcplugin.endOfDirectory(handle)

elif list_speeds != None:
	rate = 0
	name = __language__(30002)
	city = __language__(30003)
	plot = __language__(30004)
	genre = __language__(30005)
	dialog = xbmcgui.Dialog()
	list = []
	try:
		rate = int(params["rate"])
	except:
		pass
	try:
		name = urllib.unquote_plus(params["name"])
	except:
		pass
	try:
		city = urllib.unquote_plus(params["city"])
	except:
		pass
	try:
		plot = urllib.unquote_plus(params["plot"])
	except:
		pass
	try:
		genre = urllib.unquote_plus(params["genre"])
	except:
		pass
	spcn = int(list_speeds)
	if spcn == 1:
		play_id = params["id0"]
	else:
		for x in range(spcn):
			list.append(params["spd"+str(x)])
		selected = dialog.select(name, list)
		play_id = params["id"+str(selected)]
	work_url = 'http://guzei.com/online_radio/listen.php?online_radio_id='+str(play_id)
	get_play(work_url, rate, name, city, plot, genre)

