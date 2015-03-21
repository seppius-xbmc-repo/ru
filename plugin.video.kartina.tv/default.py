#!/usr/bin/python
#/*
# *      Copyright (C) 2010-2012 Eugene Bond
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

import xbmcaddon, string, xbmc, xbmcgui, xbmcplugin, os
sys.path.append(os.path.join(os.getcwd(), 'resources', 'lib'))
import iptv

import datetime, time
import urllib, threading, re

PLUGIN_ID = 'plugin.video.kartina.tv'
__settings__ = xbmcaddon.Addon(id=PLUGIN_ID)
__language__ = __settings__.getLocalizedString
USERNAME = __settings__.getSetting('username')
USERPASS = __settings__.getSetting('password')
handle = int(sys.argv[1])

PLUGIN_NAME = 'Kartina.TV'
PLUGIN_CORE = None
TRANSSID = ''
thumb = os.path.join( os.getcwd(), "icon.png" )

def get_params():
	param=[]
	paramstring=sys.argv[2]
	xbmc.log('[%s] parsing params from %s' % (PLUGIN_NAME, paramstring))
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


INFOTIMER_SHOW = None
INFOTIMER_HIDE = None


VIDEOTEKA = 'VideoLib'
if __settings__.getSetting('old_videolib') == 'true':
	VIDEOTEKA = 'Video'

def Archive(plugin, id, params):
	
	uri = sys.argv[0]
	
	in_arch = False
	
	dt = None
	if 'dt' in params:
		dt = datetime.datetime.fromordinal(int(params['dt']))
		in_arch = True
	
	if not dt:
		dt = datetime.datetime.today()
	
	epg = plugin.getEPG(id, dt.strftime('%d%m%y'))
	
	xbmc.log('[%s] Archive/EPG: fetching EPG from %s as %s' % (PLUGIN_NAME, id, epg))
	
	day_ago = datetime.datetime.fromordinal(int(dt.toordinal())-1)
	goback_title = '[B][ %s ][/B]' % (day_ago.strftime('%a, %d %B'))
	goback = xbmcgui.ListItem(goback_title)
	goback.setLabel(goback_title)
	goback.setProperty('IsPlayable', 'false')
	goback.setInfo( type='video', infoLabels={'title': goback_title, 'plot': __language__(30007)})
	uri = sys.argv[0] + '?mode=Archive&channel=%s&dt=%s&can_play=%s' % (id, day_ago.toordinal(), params['can_play'])
	xbmc.log(uri) 
	xbmcplugin.addDirectoryItem(handle,uri,goback,True)
	currentProg = False
	
	counter = 0
	for prog in epg:
		counter = counter + 1
		progStart = int(prog['time'])
		timeLabel = datetime.datetime.fromtimestamp(progStart + plugin.timeshift).strftime('%H:%M')
		can_play = params['can_play']
		
		if can_play:
			if progStart > time.time():
				can_play = False
		
		title = '%s %s %s' % (timeLabel, prog['title'], prog['info'])
		
		if progStart < time.time():
			if currentProg == False:
				if len(epg) > counter:
					p = epg[counter]
					if int(p['time']) > time.time():
						title = '[B][COLOR green]%s[/COLOR][/B]' % title
						currentProg = counter
			pass
		else:
			title = '[I]%s[/I]' % title
		
		item=xbmcgui.ListItem(title)
		item.setLabel(title)
		item.setLabel2(prog['info'])
		item.setInfo( type='video', infoLabels={'title': prog['title'], 'plot': prog['info']})
		uri = ''
		
		if can_play:
			item.setProperty('IsPlayable', 'true')
			item.setIconImage(os.path.join(os.getcwd(), 'resources', 'icons', 'play.png'))
			uri = sys.argv[0] + '?mode=WatchTV&channel=%s&title=%s&ts=%s' % (id, prog['title'], prog['time']) 
		else:
			item.setIconImage(os.path.join(os.getcwd(), 'resources', 'icons', 'play-stop.png'))
			item.setProperty('IsPlayable', 'false')
		
		xbmcplugin.addDirectoryItem(handle,uri,item,False)
	
	
	day_forward = datetime.datetime.fromordinal(int(dt.toordinal())+1)
	goahead_title = '[B][ %s ][/B]' % (day_forward.strftime('%a, %d %B'))
	goahead = xbmcgui.ListItem(goahead_title)
	goahead.setLabel(goahead_title)
	goahead.setProperty('IsPlayable', 'false')
	goahead.setInfo( type='video', infoLabels={'title': goahead_title, 'plot': __language__(30008)})
	uri = sys.argv[0] + '?mode=Archive&channel=%s&dt=%s&can_play=%s' % (id, day_forward.toordinal(), params['can_play'])
	xbmc.log(uri) 
	xbmcplugin.addDirectoryItem(handle,uri,goahead,True)
	
	xbmcplugin.endOfDirectory(handle, True, in_arch)
	#xbmc.executebuiltin( "Container.SetViewMode(51)")
	if currentProg:
		try:
			win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
			win.getControl(win.getFocusId()).selectItem(currentProg+1)
		except:
			xbmc.log('[%s] cannot to select %s item', PLUGIN_NAME, currentProg)
	

def resetAlarms(plugin, mode):
	refreshAlarmId = '%s_refresh_list' % PLUGIN_ID
	xbmc.executebuiltin("XBMC.CancelAlarm(%s,True)" % refreshAlarmId)
	resetInfoTimers()
	

def ShowChannelsList(plugin, mode = 'TV'):
	refreshAlarmId = '%s_refresh_list' % PLUGIN_ID
	
	channels = plugin.getChannelsList()
	counter = 0
	favs = __settings__.getSetting('favourites').split(',')
	
	if len(favs) < 2:
		mode = 'TV'
	
	xbmc.PlayList(xbmc.PLAYLIST_VIDEO).clear()
	
	total_items = len(channels)
	for channel in channels:
		if __settings__.getSetting('show_protected') == 'false':
			if channel['is_protected']:
				continue
		 
		if mode == 'FAV':
			if str(channel['id']) not in favs:
				continue
		
		if channel['is_video']:
			uri = sys.argv[0] + '?mode=WatchTV&as=%s&channel=%s&title=%s' % (mode, channel['id'], channel['title'])
			if channel['is_protected']:
				uri = '%s&code=xxx' % (uri)
				overlay = 3
			else:
				if channel['have_archive']:
					overlay = 1
				else:
					overlay = 0
					
			if str(channel['id']) in favs:
				overlay = 7
			
			item=xbmcgui.ListItem(channel['subtitle'], channel['title'], iconImage=channel['icon'], thumbnailImage=channel['icon'])
			color = channel['color']
			
			if __settings__.getSetting('show_played') != 'false' and channel['duration']:
				played = ' [%s%%]' % channel['percent']
			else:
				played = ''
			
			timerange = ''
			timeFieldSetting = int(__settings__.getSetting('show_time_field'))
			
			if timeFieldSetting == 1:
				if channel['epg_start']:
					channel['duration'] = int(datetime.datetime.fromtimestamp(channel['epg_start']).strftime('%H')) * 60 + int(datetime.datetime.fromtimestamp(channel['epg_start']).strftime('%M'))
				else:
					channel['duration'] = 0
			elif timeFieldSetting == 2:
				if channel['epg_end']:
					channel['duration'] = int(datetime.datetime.fromtimestamp(channel['epg_end']).strftime('%H')) * 60 + int(datetime.datetime.fromtimestamp(channel['epg_end']).strftime('%M'))
				else:
					channel['duration'] = 0
			elif timeFieldSetting == 3:
				pass
			elif timeFieldSetting == 4:
				if channel['epg_end']:
					channel['duration'] = (channel['epg_end'] - channel['servertime']) / 60
				else:
					channel['duration'] = 0
			elif timeFieldSetting == 5:
				if channel['epg_start']:
					timerange = '%s - %s ' % (datetime.datetime.fromtimestamp(channel['epg_start']).strftime('%H:%M'), datetime.datetime.fromtimestamp(channel['epg_end']).strftime('%H:%M'))
					channel['duration'] = 0
			else:
				channel['duration'] = 0
			
			rating = 0
			if str(channel['id']) in favs:
				rating = 10
			
			if __settings__.getSetting('colorize_groups') == 'false':
				channel_title = channel['title']
			else:
				channel_title = '[COLOR %s]%s[/COLOR]' % (color, channel['title'])
			
			label = '%s[B] %s.%s[/B] %s %s' % (timerange, channel_title, played, channel['subtitle'], channel['info'])
			item.setLabel(label)			
 			item.setIconImage(channel['icon'])
			item.setInfo( type='video', infoLabels={'title': channel['subtitle'], 'plotoutline': channel['info'], 'plot': channel['info'], 'genre': channel['genre'], 'duration': str(channel['duration']),  'overlay': overlay, 'ChannelNumber': str(counter), 'ChannelName': channel['title'], 'StartTime': datetime.datetime.fromtimestamp(channel['epg_start']).strftime('%H:%M'), 'EndTime': datetime.datetime.fromtimestamp(channel['epg_end']).strftime('%H:%M'), 'rating': rating})
			
			item.setProperty('IsPlayable', 'true')
			
			if 'aspect_ratio' in channel and channel['aspect_ratio']:
				item.setProperty('AspectRatio', channel['aspect_ratio'])
			
			popup = []
			
			if channel['have_epg'] != False:
				archive_text = __language__(30006)
				if channel['have_archive']:
					archive_text = __language__(30011)
				
				uri2 = sys.argv[0] + '?mode=Archive&channel=%s&can_play=%s' % (channel['id'], channel['have_archive'])
				popup.append((archive_text, 'XBMC.Container.Update(%s)'%uri2,))
			
			popup.append((__language__(30021), 'Container.Refresh',))
			
			uri2 = sys.argv[0] + '?mode=Favourite&channel=%s' % (channel['id'])
			if str(channel['id']) in favs:
				fav_label = __language__(30038)
			else:
				fav_label = __language__(30037)
			popup.append((fav_label, 'RunPlugin(%s)'%uri2,))
			
			if __settings__.getSetting('start_with_tv') == 'true':
				uriP = 'XBMC.Container.Update(%s)' % (sys.argv[0] + '?mode=%s')
				if mode == 'TV':
					popup.append((__language__(30041), uriP % 'FAV',))
				
				if mode == 'FAV':
					popup.append((__language__(30042), uriP % 'TV',))
				
				popup.append((__language__(30016), uriP % VIDEOTEKA,))
				popup.append((__language__(30004), uriP % 'Settings',))
			
			item.addContextMenuItems(popup, True)
			
			xbmcplugin.addDirectoryItem(handle,uri,item, False, total_items)
			counter = counter + 1
	
	refresh_rate = int(__settings__.getSetting('autorefresh_rate'))
	xbmcplugin.setContent(handle, 'Movies')
	xbmcplugin.endOfDirectory(handle, cacheToDisc=(__settings__.getSetting('always_refresh') == 'false'))
	
	if refresh_rate > 0:
		xbmc.executebuiltin("XBMC.AlarmClock(%s,XBMC.Container.Refresh,%s,True)" % (refreshAlarmId, refresh_rate))
	#xbmc.executebuiltin( "Container.SetViewMode(51)")


def Video(plugin, params):
	if 'mode' in params:
		mode = params['mode']
	else:
		mode = 'last'
	
	if 'page' in params:
		page = int(params['page'])
		if page < 1:
			page = 1
	else:
		page = 1
	
	
	
	if page > 1:
		goback_title = '[ %s ]' % __language__(30019)
		goback = xbmcgui.ListItem(goback_title)
		goback.setLabel(goback_title)
		goback.setProperty('IsPlayable', 'false')
		goback.setInfo( type='video', infoLabels={'title': goback_title})
		uri = sys.argv[0] + '?mode=Video&mode=%s&page=%d' % (mode, page-1)
		xbmc.log(uri) 
		xbmcplugin.addDirectoryItem(handle,uri,goback,True)
	
	
	vlist = plugin.getVideoList(mode, page, 50)
	
	for film in vlist:
		title = film['title']
		item=xbmcgui.ListItem(title, title, iconImage=film['icon'], thumbnailImage=film['icon'])
		item.setLabel(title)
		item.setIconImage(film['icon'])
		item.setLabel2(film['info'])
		item.setInfo( type='video', infoLabels={'title': title, 'plot': film['info']})
		uri = sys.argv[0] + '?mode=VideoInfo&vod=%s' % film['id']
		item.setProperty('IsPlayable', 'true')
		xbmcplugin.addDirectoryItem(handle,uri,item,True)
	
	
	goahead_title = '[ %s ]' % __language__(30018)
	goahead = xbmcgui.ListItem(goahead_title)
	goahead.setLabel(goahead_title)
	goahead.setProperty('IsPlayable', 'false')
	goahead.setInfo( type='video', infoLabels={'title': goahead_title})
	uri = sys.argv[0] + '?mode=Video&mode=%s&page=%d' % (mode, page+1)
	xbmc.log(uri) 
	xbmcplugin.addDirectoryItem(handle,uri,goahead,True)
	
	xbmcplugin.endOfDirectory(handle,True,False)

def VideoInfo(plugin, params):
	vid = params['vod']
	film = plugin.getVideoInfo(vid)
	
	for video in film['videos']:
		xbmc.log('[%s] VODs list item: %s' % (PLUGIN_NAME, video))
		title = video['title']
		if title == '':
			title = __language__(30017)
		
		icon = 'http://iptv.kartina.tv%s' % film['poster']
		item=xbmcgui.ListItem(title, title, iconImage=icon, thumbnailImage=icon)
		item.setLabel(title)
		item.setIconImage(icon)
		item.setLabel2(film['description'])
		item.setInfo( type='video', infoLabels={'title': title, 'plot': film['description']})
		item.setProperty('IsPlayable', 'true')
		uri = sys.argv[0] + '?mode=WatchVOD&vod=%s&title=%s' % (video['id'], film['name'] + '. ' + video['title'])
		xbmcplugin.addDirectoryItem(handle,uri,item,False)
	
	xbmcplugin.endOfDirectory(handle)

def WatchVOD(plugin, params):
	vod = params['vod']
	url = plugin.getVideoUrl(vod)
	xbmc.log('[%s] WatchVOD: Opening video %s as %s' % (PLUGIN_NAME, id, url))
	item=xbmcgui.ListItem(params['title'], path=url)
	item.setInfo( type='video', infoLabels={'title': params['title']})
	if handle == -1:
		xbmc.Player().play(url, item)		
	else:
		xbmcplugin.setResolvedUrl(handle = handle, succeeded=True, listitem=item)

def WatchTV(plugin, id, params):
	if 'ts' in params:
		gmt = params['ts']
	else:
		gmt = None
	xbmc.log('[%s] WatchTV: Timestamp is %s, adjust setting is %s' % (PLUGIN_NAME, gmt, __settings__.getSetting('ask_adjust')))
	if gmt:
		if __settings__.getSetting('ask_adjust') == 'true':
			adjust_text = __language__(30009)
			dialogus = xbmcgui.Dialog()
			adjust = dialogus.numeric(2, adjust_text, "00:00")
			xbmc.log('[%s] WatchTV: Adjusting start for %s' % (PLUGIN_NAME, adjust))
			if adjust:
				xbmc.log('[%s] WatchTV: Old ts: %s' % (PLUGIN_NAME, gmt))
				a_hours, a_mins = adjust.split(':', 1)
				
				gmt = int(gmt) + (int(a_hours) * 3600 + int(a_mins) * 60)
				xbmc.log('[%s] WatchTV: New ts: %s' % (PLUGIN_NAME, gmt))
				
	if 'code' in params:
		code =  __settings__.getSetting('protected_code')
	else:
		code = None
	
	url = plugin.getStreamUrl(id, gmt, code)
	if url:
		xbmc.log('[%s] WatchTV: Opening channel %s as %s' % (PLUGIN_NAME, id, url))
		item=xbmcgui.ListItem(params['title'], path=url)
		item.setInfo( type='video', infoLabels={'title': params['title']})
		
		if 'as' in params:
			mode = params['as']
		else:
			mode = 'TV'
		
		favs = __settings__.getSetting('favourites').split(',')
		
		if len(favs) < 2:
			mode = 'TV'
		
		doVidInfo = False
		
		player = xbmc.Player()
		pls = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
		xbmcplugin.setContent(handle, 'Movies')
		if gmt:
			pls.clear()
		if not gmt and pls.size() < 2:
			pls.clear()
			
			xbmc.log('[%s] WatchTV: Generating playlist' % (PLUGIN_NAME))
			all = plugin.getLast()
			index = 0
			toplay = -1
			
			for channel in all:
				if mode == 'FAV' and str(channel['id']) not in favs:
					index += 1
					continue
				if channel['is_video']:
					if toplay > -1 or id == str(channel['id']):
						url2 = sys.argv[0] + '?mode=WatchTV&as=%s&channel=%s&title=%s' % (mode, channel['id'], channel['title'])
						if channel['is_protected']:
							url2 = '%s&code=xxx' % (url2)
						if id == str(channel['id']):
							path = url
						else:
							path = url2
						ch=xbmcgui.ListItem(channel['subtitle'], channel['title'], iconImage=channel['icon'], thumbnailImage=channel['icon'])
						ch.setIconImage(channel['icon'])
						ch.setInfo( type='video', infoLabels={'Studio': channel['title'], 'title': channel['subtitle'], 'plot': channel['info'], 'genre': channel['genre'], 'ChannelName': channel['title'], 'StartTime': datetime.datetime.fromtimestamp(channel['epg_start']).strftime('%H:%M'), 'EndTime': datetime.datetime.fromtimestamp(channel['epg_end']).strftime('%H:%M')})
						ch.setProperty('IsPlayable', 'true')
						if 'aspect_ratio' in channel and channel['aspect_ratio']:
							ch.setProperty('AspectRatio', channel['aspect_ratio'])
						elif __settings__.getSetting('guess_aspect_ratio'):
							if channel['subtitle'].find('16:9') > -1 or channel['info'].find('16:9') > -1:
								xbmc.log('[%s] WatchTV: guessing aspect ratio as 16:9' % (PLUGIN_NAME))
								ch.setProperty('AspectRatio', '1.20 : 1')
						pls.add(path, ch, index)
						if id == str(channel['id']):
							item.setIconImage(channel['icon'])
							item.setInfo( type='video', infoLabels={'Studio': channel['title'], 'title': channel['subtitle'], 'plot': channel['info'], 'genre': channel['genre'], 'ChannelName': channel['title'], 'StartTime': datetime.datetime.fromtimestamp(channel['epg_start']).strftime('%H:%M'), 'EndTime': datetime.datetime.fromtimestamp(channel['epg_end']).strftime('%H:%M')})
							if 'aspect_ratio' in channel and channel['aspect_ratio']:
								ch.setProperty('AspectRatio', channel['aspect_ratio'])
							elif __settings__.getSetting('guess_aspect_ratio'):
								if channel['subtitle'].find('16:9') > -1 or channel['info'].find('16:9') > -1:
									xbmc.log('[%s] WatchTV: guessing aspect ratio as 16:9' % (PLUGIN_NAME))
									item.setProperty('AspectRatio', '1.20 : 1')
									xbmc.log('[%s] WatchTV: forcing aspect ratio as 16:9' % (PLUGIN_NAME))
							toplay = index	
					index += 1
			
			for channel in all[0:toplay]:
				if mode == 'FAV' and str(channel['id']) not in favs:
					continue
				if channel['is_video']:
					url2 = sys.argv[0] + '?mode=WatchTV&as=%s&channel=%s&title=%s' % (mode, channel['id'], channel['title'])
					if channel['is_protected']:
						url2 = '%s&code=%s' % (url2, 'xxx')
					path = url2
					ch=xbmcgui.ListItem(channel['subtitle'], channel['title'], iconImage=channel['icon'], thumbnailImage=channel['icon'])
					ch.setIconImage(channel['icon'])
					ch.setInfo( type='video', infoLabels={'Studio': channel['title'], 'title': channel['subtitle'], 'plot': channel['info'], 'genre': channel['genre'], 'ChannelName': channel['title'], 'StartTime': datetime.datetime.fromtimestamp(channel['epg_start']).strftime('%H:%M'), 'EndTime': datetime.datetime.fromtimestamp(channel['epg_end']).strftime('%H:%M')})
					ch.setProperty('IsPlayable', 'true')
					if 'aspect_ratio' in channel and channel['aspect_ratio']:
						ch.setProperty('AspectRatio', channel['aspect_ratio'])
					elif __settings__.getSetting('guess_aspect_ratio'):
						if channel['subtitle'].find('16:9') > -1 or channel['info'].find('16:9') > -1:
							xbmc.log('[%s] WatchTV: guessing aspect ratio as 16:9' % (PLUGIN_NAME))
							ch.setProperty('AspectRatio', '1.20 : 1')
					pls.add(path, ch, index)
					index += 1
			doVidInfo = True
		elif not gmt:
			all = plugin.getLast()
			for channel in all:
				if id == str(channel['id']):
					item.setIconImage(channel['icon'])
					item.setInfo( type='video', infoLabels={'Studio': channel['title'], 'title': channel['subtitle'], 'plot': channel['info'], 'genre': channel['genre']})
					if 'aspect_ratio' in channel and channel['aspect_ratio']:
						ch.setProperty('AspectRatio', channel['aspect_ratio'])
					elif __settings__.getSetting('guess_aspect_ratio'):
						if channel['subtitle'].find('16:9') > -1 or channel['info'].find('16:9') > -1:
							xbmc.log('[%s] WatchTV: forsing aspect ratio as 16:9' % (PLUGIN_NAME))
							item.setProperty('AspectRatio', '1.20 : 1')
					break
			doVidInfo = True
		
		xbmc.executebuiltin("XBMC.PlayerControl(repeatall)")
		
		if handle == -1:		
			xbmc.log('[%s] WatchTV: handle is -1, starting player' % (PLUGIN_NAME))
			if pls and pls.size():
				player.play(pls)
			else:
				player.play(url, item)
		else:
			xbmc.log('[%s] WatchTV: handle is %s, setting resolved url' % (PLUGIN_NAME, handle))
			xbmcplugin.setResolvedUrl(handle = handle, succeeded=True, listitem=item)
		
		if __settings__.getSetting('showcurrent') == 'true' and not gmt and doVidInfo:
			SetupInfoTimer()
			#xbmc.sleep(5000)
			#dialog = xbmcgui.Window(10142)
			#dialog.show()
	else:
		xbmc.executebuiltin("XBMC.Notification(" + __language__(30025).encode('utf8') + ", " + __language__(30025).encode('utf8') + ", 8000)");

def resetInfoTimers():
	if INFOTIMER_SHOW:
		if INFOTIMER_SHOW.isAlive():
			INFOTIMER_SHOW.cancel()
	if INFOTIMER_HIDE:
		if INFOTIMER_HIDE.isAlive():
			INFOTIMER_HIDE.cancel()

def SetupInfoTimer():
	resetInfoTimers()
	INFOTIMER_SHOW = threading.Timer(10.0, ShowNowPlayingInfo)
	xbmc.log('[%s] Info timer is set' % (PLUGIN_NAME))
	INFOTIMER_SHOW.start()

def ShowNowPlayingInfo():
	resetInfoTimers()
	if xbmc.getCondVisibility('VideoPlayer.IsFullscreen'):
		INFOTIMER_HIDE = threading.Timer(6.0, HideNowPlayingInfo)
		xbmc.log('[%s] Showing info' % (PLUGIN_NAME))
		INFOTIMER_HIDE.start()
		dialog = xbmcgui.Window(10142)
		dialog.show()
	

def HideNowPlayingInfo():
	resetInfoTimers()
	xbmc.log('[%s] Hidding info' % (PLUGIN_NAME))
	xbmc.executebuiltin("Dialog.Close(10142)")


def ShowRoot(plugin):
	uri = sys.argv[0] + '?mode=%s'
	
	tv_title = ' [  %s  ] ' % __language__(30012)
	tv=xbmcgui.ListItem(tv_title)
	tv.setLabel(tv_title)
	tv.setProperty('IsPlayable', 'false')
	tv.setInfo( type='video', infoLabels={'title': tv_title, 'plot': __language__(30012)})
	xbmcplugin.addDirectoryItem(handle,uri % 'TV',tv,True)
	
	favs = __settings__.getSetting('favourites').split(',')
	if len(favs) > 1:
		fv_title = ' [  %s  ] ' % __language__(30041)
		fv=xbmcgui.ListItem(fv_title)
		fv.setLabel(fv_title)
		fv.setProperty('IsPlayable', 'false')
		fv.setInfo( type='video', infoLabels={'title': fv_title, 'plot': __language__(30041)})
		xbmcplugin.addDirectoryItem(handle,uri % 'FAV',fv,True)
	
	vod_title = ' [  %s  ] ' % __language__(30016)
	vod = xbmcgui.ListItem(vod_title)
	vod.setLabel(vod_title)
	vod.setProperty('IsPlayable', 'false')
	vod.setInfo( type='video', infoLabels={'title': vod_title, 'plot': __language__(30016)})
	xbmcplugin.addDirectoryItem(handle,uri % VIDEOTEKA,vod,True)
	
	set_title = ' [  %s  ] ' % __language__(30004)
	set = xbmcgui.ListItem(set_title)
	set.setLabel(set_title)
	set.setProperty('IsPlayable', 'false')
	set.setInfo( type='video', infoLabels={'title': set_title, 'plot': __language__(30004)})
	xbmcplugin.addDirectoryItem(handle,uri % 'Settings',set,True)
	
	set_title = ' [  %s  ] ' % __language__(30005)
	set = xbmcgui.ListItem(set_title)
	set.setLabel(set_title)
	set.setProperty('IsPlayable', 'false')
	set.setInfo( type='video', infoLabels={'title': set_title, 'plot': __language__(30005)})
	xbmcplugin.addDirectoryItem(handle,uri % 'openSettings',set,True)
	
	
#	set_title = ' [  Test  ] '
#	set = xbmcgui.ListItem(set_title)
#	set.setLabel(set_title)
#	set.setProperty('IsPlayable', 'false')
#	set.setInfo( type='video', infoLabels={'title': set_title, 'plot': "Test"})
#	xbmcplugin.addDirectoryItem(handle,uri % 'MovieLib&do=Update',set,True)
#	
#	
#	set_title = ' [  Test 2 ] '
#	set = xbmcgui.ListItem(set_title)
#	set.setLabel(set_title)
#	set.setProperty('IsPlayable', 'false')
#	set.setInfo( type='video', infoLabels={'title': set_title, 'plot': "Test 2"})
#	xbmcplugin.addDirectoryItem(handle,uri % 'MovieLib&do=Cleanup',set,True)
	
	xbmcplugin.endOfDirectory(handle,True,False)

def Favourite(plugin, id):
	favs = __settings__.getSetting('favourites').split(',')
	if not favs:
		favs = []
	if id not in favs:
		favs.append(id)
	else:
		favs.remove(id)
	__settings__.setSetting('favourites', ",".join(favs[:]))
	xbmc.executebuiltin("XBMC.Container.Refresh")

def ProcessSettings(plugin, params):
	if 'name' in params:
		value, options = plugin.getSettingCurrent(params['name'])
		dialog = xbmcgui.Dialog()
		selection = []
		for opval, opname in options:
			selection.append(opname)
  		ret = dialog.select(params['title'], selection)
  		counter = 0
  		for opval, opname in options:
  			if counter == ret:
  				plugin.setSettingCurrent(params['name'], opval)
  			counter = counter + 1
  		xbmc.executebuiltin('Container.Refresh')
  		
	else:
		settings = plugin.getSettingsList()
		
		uri = sys.argv[0] + '?mode=Settings&name=%s&title=%s'
		
		for setting in settings:
			sName = __language__(setting['language_key'])
			
			label = setting['value']
			if 'options' in setting:
				for k,v in setting['options']:
					if k == label:
						label = v
			
			sName = sName + ' (%s)' % label
			
			sItem = xbmcgui.ListItem(sName)
			sItem.setLabel(sName)
			sItem.setProperty('IsPlayable', 'false')
			sItem.setInfo( type='video', infoLabels={'title': sName, 'plot': sName})
			xbmcplugin.addDirectoryItem(handle,uri % (setting['name'], __language__(setting['language_key'])),sItem,True)
		
		xbmcplugin.endOfDirectory(handle,True,False)
	

def ShowNowNextHint(plugin, chid):
	current = plugin.getCurrentInfo(chid)
	hint = ''
	first = 1
	for prog in current:
		if first:
			first = 0
			if 'title' in prog and prog['title'] != None:
				titl =  __language__(30013)
				text = prog['title'].encode('utf8')
				xbmc.executebuiltin("XBMC.Notification(" + titl.encode('utf8') + ", " + text + ", 8000)");
				xbmc.sleep(8000)
		else:
			if 'title' in prog and prog['title'] != None:
				when = datetime.datetime.fromtimestamp(int(prog['time']))
				titl = __language__(30014) % (when.strftime('%H:%M'))
				text = prog['title'].encode('utf8')
				xbmc.executebuiltin("XBMC.Notification(" + titl.encode('utf8') + ", " + text + ", 12000)");

def VideoLib(plugin, params):
	
	do = ''
	if 'do' in params:
		do = params['do']
	
	uri = sys.argv[0] + '?mode=VideoLib&do=%s'
	
	tv_title = ' [  %s  ] ' % __language__(32011)
	tv=xbmcgui.ListItem(tv_title)
	tv.setLabel(tv_title)
	tv.setProperty('IsPlayable', 'false')
	tv.setInfo( type='video', infoLabels={'title': tv_title, 'plot': __language__(30012)})
	xbmcplugin.addDirectoryItem(handle,uri % 'Play',tv,True)
	
	vod_title = ' [  %s  ] ' % __language__(32003)
	vod = xbmcgui.ListItem(vod_title)
	vod.setLabel(vod_title)
	vod.setProperty('IsPlayable', 'false')
	vod.setInfo( type='video', infoLabels={'title': vod_title, 'plot': __language__(30016)})
	xbmcplugin.addDirectoryItem(handle,uri % 'Update',vod,True)
	
	set_title = ' [  %s  ] ' % __language__(32000)
	set = xbmcgui.ListItem(set_title)
	set.setLabel(set_title)
	set.setProperty('IsPlayable', 'false')
	set.setInfo( type='video', infoLabels={'title': set_title, 'plot': __language__(30004)})
	xbmcplugin.addDirectoryItem(handle,uri % 'Cleanup',set,True)
	
	xbmcplugin.endOfDirectory(handle,True,do != '')
	#xbmcplugin.endOfDirectory(handle,False,True)
	
	
	if do == 'Play':
	
		last_update = __settings__.getSetting('video_last_update') or '0000-00-00 00:00:00'
		if last_update == '0000-00-00 00:00:00':
			dialog = xbmcgui.Dialog()
			if dialog.yesno(__language__(32008), __language__(32010)):
				MovieLib(plugin, 'Update')
				
		elif last_update < datetime.datetime.fromtimestamp(time.time() - 60*60*24*7).strftime('%Y-%m-%d %H:%M:%S'):
			dialog = xbmcgui.Dialog()
			if dialog.yesno(__language__(32009), __language__(32010)):
				MovieLib(plugin, 'Update')
		
		smartPlsFile = xbmc.translatePath('special://profile/playlists/video') + '/' + str(PLUGIN_ID) + '.xsp'
		xbmc.log('[%s] checking smart playlist at %s' % (PLUGIN_NAME, smartPlsFile))
		if not os.path.exists(smartPlsFile):
			xbmc.log('[%s] smart playlist not found' % (PLUGIN_NAME))
			smartPls = open(smartPlsFile, "w")
			smartPls.write('''<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
	<smartplaylist type="movies">
		<name>%s</name>
		<match>all</match>
		<rule field="path" operator="is">plugin://%s/</rule>
	</smartplaylist>''' % (PLUGIN_NAME, PLUGIN_ID))
			smartPls.close()
	
		xbmc.executebuiltin("XBMC.ActivateWindow(VideoLibrary,Movies)")
	elif do != '':
		xbmc.log('[%s] calling movielib %s' % (PLUGIN_NAME, do))
		MovieLib(plugin, do)

	
def MovieLib(plugin, do):
	import movielib
	m = movielib.movielib()
	
	if do == 'Cleanup':
		dialog = xbmcgui.Dialog()
		if dialog.yesno(__language__(32000), __language__(32012)):
			m.vdbCleanUp(sys.argv[0])
			__settings__.setSetting('video_last_update', '0000-00-00 00:00:00')
			__settings__.setSetting('in_vod', 'false')
			dialog = xbmcgui.Dialog()
			dialog.ok( __language__(32000), __language__(32001))
	elif do == 'Update':
		__settings__.setSetting('in_vod', 'false')
		progress = xbmcgui.DialogProgress()
		progress.create(__language__(32003))
		progress.update(10, __language__(32004))
		vlist = plugin.getVideoList('last', 1, 'all')
		progress.update(20, __language__(32005))
		toprocess = []
		last_update = __settings__.getSetting('video_last_update') or '0000-00-00 00:00:00'
		for vod in vlist:
			info = sys.argv[0] + '?mode=VideoInfo&vod=%s' % vod['id']
			if m.vdbMovieByPathAndTrailer(sys.argv[0], info):
				xbmc.log('[%s] skipping %s?' % (PLUGIN_NAME, info), level=xbmc.LOGDEBUG)
				continue
			else:
				xbmc.log('[%s] new vod %s?' % (PLUGIN_NAME, info))
			toprocess.append(vod)
		if len(toprocess):
			stepSize = float(60.0 / len(toprocess))
		else:
			stepSize = 1
		xbmc.log('[%s] progress step size set to %s as 60 / %s' % (PLUGIN_NAME, stepSize, len(toprocess)), level=xbmc.LOGDEBUG)
		counter = 0
		for vod in toprocess:
			info = plugin.getVideoInfo(vod['id'])
			film = movielib.movielibmovie(sys.argv[0])
			film.setTitle(vod['title'])
			film.setDescription(vod['info'])
			film.setImage(vod['icon'])
			for genre in vod['genre'].split(', '):
				film.addGenre(genre)
			for actor in info['actors'].split(', '):
				film.addActor(actor)
			film.setYear(info['year'])
			if info['rate_imdb']:
				rating = info['rate_imdb']
			else:
				rating = info['rate_kinopoisk']
			film.setRating(rating)
			film.setDirector(info['director'])
			film.setWritter(info['scenario'])
			film.setStudio(info['studio'])
			film.setCountry(info['country'])
			film.setTrailer(sys.argv[0] + '?mode=VideoInfo&vod=%s' % vod['id'])
			for part in info['videos']:
				uri = '?mode=WatchVOD&vod=%s&title=%s' % (part['id'], vod['title'])
				film.addFile(uri, part['title'])
			m.addMovie(film)
			progress.update(40 + int(counter * stepSize), __language__(32006) % vod['title'])
			counter += 1
			xbmc.sleep(250)
			if progress.iscanceled():
				break
		progress.update(100, __language__(32001))
		if not progress.iscanceled():
			__settings__.setSetting('video_last_update', datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
		progress.close()
		dialog = xbmcgui.Dialog()
		dialog.ok( __language__(32003), __language__(32007) % counter)
	else:
		xbmc.log('[%s] unknown movie lib command: "%s"' % (PLUGIN_NAME, do))


xbmc.log('[%s] Loaded' % (PLUGIN_NAME))

params = get_params()
if '_s' in params and '_sn' in params:
	SID = params['_s']
	SID_NAME = params['_sn']
else:
	SID = None
	SID_NAME = None

PLUGIN_CORE = iptv.kartina(USERNAME, USERPASS, PLUGIN_ID, SID, SID_NAME)

if PLUGIN_CORE.testAuth() == False:
	dialog = xbmcgui.Dialog()
	dialog.ok( __language__(30023), __language__(30024))
	__settings__.openSettings()
else:
	
	if not __settings__.getSetting('ga_uid'):
		from random import randint
		from ga import get_visitor_id
		ga_uid = get_visitor_id(str(randint(0, 0x7fffffff)) + PLUGIN_NAME + PLUGIN_ID, None)
		__settings__.setSetting('ga_uid', ga_uid)
		xbmc.log('[%s] GA uid set to %s' % (PLUGIN_NAME, __settings__.getSetting('ga_uid')))
	
	#xbmc.executebuiltin( "Container.SetViewMode(51)")
	#TRANSSID = '&_s=%s&_sn=%s' % (PLUGIN_CORE.SID, PLUGIN_CORE.SID_NAME)
	
	if 'mode' in params:
		mode = params['mode']
	else:
		if __settings__.getSetting('start_with_tv') == 'false':
			mode = None
		else:
			mode = 'TV'
	
	if 'channel' in params:
		channel = params['channel']
	else:
		channel = None
	
	if 'title' in params:
		title = params['title']
	else:
		title = ''
	
	xbmc.log('[%s] mode: %s' % (PLUGIN_NAME, mode))
	
	resetAlarms(PLUGIN_CORE, mode)
	
	from ga import track_page_view
	what = mode
	if title:
		frmt = '[LIVE] %s/'
		if 'ts' in params:
			frmt = '[ARCH] %s/'
		if 'vod' in params:
			frmt = '[VOD] %s/'
		what = frmt % title
	if what == None:
		what = 'Root'
	urlpath = what + sys.argv[2]
	extras = {}
	extras['screen'] = xbmc.getInfoLabel('System.ScreenMode')
	try:
		track_page_view(__settings__.getSetting('ga_uid'), urlpath, PLUGIN_CORE.genUa(), extras) 
	except:
		xbmc.log('[%s] problems tracking GA' % PLUGIN_NAME)
	
	if mode == 'WatchTV':
		WatchTV(PLUGIN_CORE, channel, params)

	elif mode == 'Archive':
		Archive(PLUGIN_CORE, channel, params)

	elif mode == 'VideoLib':
		VideoLib(PLUGIN_CORE, params)

	elif mode == 'Video':
		Video(PLUGIN_CORE, params)

	elif mode == 'VideoInfo':
		VideoInfo(PLUGIN_CORE, params)

	elif mode == 'WatchVOD':
		WatchVOD(PLUGIN_CORE, params)
	
	elif mode == 'ShowNowNextHint':
		ShowNowNextHint(PLUGIN_CORE, channel)
	
	elif mode == 'openSettings':
		__settings__.openSettings()

	elif mode in ('TV', 'FAV'):
		ShowChannelsList(PLUGIN_CORE, mode)

	elif mode == 'Favourite':
		Favourite(PLUGIN_CORE, channel)
	
	elif mode == 'Settings':
		ProcessSettings(PLUGIN_CORE, params)
	
	elif mode == 'MovieLib':
		do = ''
		if 'do' in params:
			do = params['do']
		MovieLib(PLUGIN_CORE, do)
		
	elif mode == 'ExecURL':
		Get(url)
		xbmc.sleep(50)
		xbmc.executebuiltin('Container.Refresh')
	else:
		ShowRoot(PLUGIN_CORE)

