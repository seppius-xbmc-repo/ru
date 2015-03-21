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
import urllib,urllib2,re,sys,os,random
import xbmcplugin,xbmcgui
import time
from datetime import datetime, timedelta

pluginhandle = int(sys.argv[1])
thumb = os.path.join(os.getcwd().replace(';', ''), "icon.png" )


def showMessage(heading, message, times = 3000):
	heading = heading.encode('utf-8')
	message = message.encode('utf-8')
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



def getURL(url,Referer = 'http://www.moskva.fm/'):
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Opera/10.60 (X11; openSUSE 11.3/Linux i686; U; ru) Presto/2.6.30 Version/10.60')
	req.add_header('Accept', 'text/html, application/xml, application/xhtml+xml, */*')
	req.add_header('Accept-Language', 'ru,en;q=0.9')
	req.add_header('Referer', Referer)
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	return link


def get_root():

	uri = sys.argv[0] + '?mode=OpenArtists'
	uri += '&url='  + urllib.quote_plus('http://www.moskva.fm/artists')
	item = xbmcgui.ListItem('Исполнители', iconImage = thumb, thumbnailImage = thumb)
	xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

#	uri = sys.argv[0] + '?mode=OpenStations'
#	uri += '&url='  + urllib.quote_plus('http://www.moskva.fm/stations')
#	item = xbmcgui.ListItem('Станции', iconImage = thumb, thumbnailImage = thumb)
#	xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

#	uri = sys.argv[0] + '?mode=OpenPrograms'
#	uri += '&url='  + urllib.quote_plus('http://www.moskva.fm/programs')
#	item = xbmcgui.ListItem('Передачи', iconImage = thumb, thumbnailImage = thumb)
#	xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

#	uri = sys.argv[0] + '?mode=OpenCharts'
#	uri += '&url='  + urllib.quote_plus('http://www.moskva.fm/charts')
#	item = xbmcgui.ListItem('Хит-парады', iconImage = thumb, thumbnailImage = thumb)
#	xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

#	uri = sys.argv[0] + '?mode=OpenEvents'
#	uri += '&url='  + urllib.quote_plus('http://www.moskva.fm/events')
#	item = xbmcgui.ListItem('Концерты', iconImage = thumb, thumbnailImage = thumb)
#	xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

	xbmcplugin.endOfDirectory(pluginhandle)


def add_alphabet(http):
	r1 = re.compile('<div class="alphabet">(.*?)</div>', re.DOTALL).findall(http)
	if len(r1) > 0:
		r2 = re.compile('<a href="(.*?)">(.*?)</a>').findall(r1[0])
		if len(r2) > 0:
			for new_target, alphabet in r2:
				alphabet = alphabet.replace('&nbsp;', ' ')
				uri = sys.argv[0] + '?mode=OpenArtists'
				uri += '&url='  + urllib.quote_plus(new_target)
				item = xbmcgui.ListItem('Навигатор -> ' + alphabet, iconImage = thumb, thumbnailImage = thumb)
				xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

def OpenArtists(target):
	http = getURL(url)

	rr1 = re.compile('<ul class="list_artist">(.*?)</ul>', re.DOTALL).findall(http)
	if len(rr1) > 0:
		for rr2 in rr1:
			rr3 = re.compile('<a href="(.*?)">(.*?)</a>').findall(rr2)
			for new_target, alphabet in rr3:
				#xbmc.output(' new_target = %s'%new_target)
				#xbmc.output('   alphabet = %s'%alphabet)

				uri = sys.argv[0] + '?mode=OpenArtist'
				uri += '&url='  + urllib.quote_plus(new_target)
				item = xbmcgui.ListItem(alphabet, iconImage = thumb, thumbnailImage = thumb)
				xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
	else: showMessage('Ой, Ошибка!', 'list_artist не найден!')

	add_alphabet(http)

	xbmcplugin.endOfDirectory(pluginhandle)


def OpenArtist(target):
	http = getURL(url)

	r1 = re.compile('<table id="list_song">(.*?)</table>', re.DOTALL).findall(http)
	if len(r1) > 0:
		r2 = re.compile('<tr>(.*?)</tr>', re.DOTALL).findall(r1[0])
		for r3 in r2:
			try:	number = re.compile('<td class="number">(.*?)</td>').findall(r3)[0] + '. '
			except:	number = ''

			try:	img = re.compile('<img title="(.*?)" alt="(.*?)" src="(.*?)" />').findall(r3)[0][2]
			except:	img = thumb

			try:
				r4 = re.compile('<br />\s(.*?)<span class="date">(.*?)</span>').findall(r3)
				Track = r4[0][0]
				Year  = r4[0][1]
			except:
				Track = 'Unknown track'
				Year  = '1900'

			try:
				r5 = re.compile('<a href="(.*?)" class="song">(.*?)</a>').findall(r3)
				href  = r5[0][0]
				Title = r5[0][1]

				#xbmc.output(' new_target = %s'%new_target)
				#xbmc.output('   alphabet = %s'%alphabet)

				uri = sys.argv[0] + '?mode=PlayTrack'
				uri += '&url='  + urllib.quote_plus(href)
				item = xbmcgui.ListItem(Title, iconImage = thumb, thumbnailImage = thumb)
				xbmcplugin.addDirectoryItem(pluginhandle, uri, item)


			except:	showMessage('Ой, Ошибка!', 'Не пригодный элемент!')
	else: showMessage('Ой, Ошибка!', 'list_song не найден!')

	add_alphabet(http)

	xbmcplugin.endOfDirectory(pluginhandle)



def GetRegion(data, region, modeall=False, defval=None):
	try:
		ret_val = re.compile('<%s>(.*?)</%s>'%(region,region),re.DOTALL|re.IGNORECASE).findall(data)
		if modeall: return ret_val
		else: return ret_val[0]
	except: return defval




def PlayTranslation(target):
	http = getURL(url)

	r1 = re.compile('swfobject.embedSWF\(\'(.*?)\'(.*?)\);', re.DOTALL).findall(http)
	if len(r1) == 0:
		showMessage('Ой, Ошибка!', 'swfobject.embedSWF не найден!')
		return False

	try:
		swfobject = r1[0][0]
		swfparams = r1[0][1]
		xbmc.output('PlayTrack -> swfobject = %s'%swfobject)

		stat_id = re.compile('station: \'(.*?)\',').findall(swfparams)[0]
		xbmc.output('PlayTrack ->   stat_id = %s'%stat_id)

		stat_ti = re.compile('time: \'(.*?)\',').findall(swfparams)[0]
		xbmc.output('PlayTrack ->   stat_ti = %s'%stat_ti)

		stat_ST = re.compile('servertime: \'(.*?)\',').findall(swfparams)[0]
		xbmc.output('PlayTrack ->   stat_ST = %s'%stat_ST)

		stat_SU = re.compile('siteurl: \'(.*?)\',').findall(swfparams)[0]
		xbmc.output('PlayTrack ->   stat_SU = %s'%stat_SU)

		stat_XF = re.compile('playerxml: \'(.*?)\',').findall(swfparams)[0]
		xbmc.output('PlayTrack ->   stat_XF = %s'%stat_XF)

	except:
		showMessage('Ой, Ошибка!', 'Не разобраны параметры плеера!')
		return False

	d = datetime.fromtimestamp(int(stat_ti) + 10800) # GMT + 3 (3600 * 3)
	seek_sec = int(d.strftime('%S'))

	playList = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
	playList.clear()

	x = 60
	min_delta = timedelta(minutes = 1)
	while x >= 0:
		x -= 1
		Playable_URL = 'http://dt.moskva.fm/files/%s/mp4/%s.mp4?%s'%(stat_id, d.strftime('%Y/%m/%d/%H%M'), random.random())
		xbmc.output(' + Playable_URL %s' % Playable_URL)

		playList.add(Playable_URL)
		d += min_delta

	p = xbmc.Player()
	p.play(playList)
	p.seekTime(seek_sec)







def PlayTrack(target, Translation = False):

	http = getURL(url)

	r1 = re.compile('swfobject.embedSWF\(\'(.*?)\'(.*?)\);', re.DOTALL).findall(http)
	if len(r1) == 0:
		showMessage('Ой, Ошибка!', 'swfobject.embedSWF не найден!')
		return False



	try:
		swfobject = r1[0][0]
		swfparams = r1[0][1]
		xbmc.output('PlayTrack -> swfobject = %s'%swfobject)

		stat_id = re.compile('station: \'(.*?)\',').findall(swfparams)[0]
		xbmc.output('PlayTrack ->   stat_id = %s'%stat_id)

		stat_ti = re.compile('time: \'(.*?)\',').findall(swfparams)[0]
		xbmc.output('PlayTrack ->   stat_ti = %s'%stat_ti)

		stat_ST = re.compile('servertime: \'(.*?)\',').findall(swfparams)[0]
		xbmc.output('PlayTrack ->   stat_ST = %s'%stat_ST)

		stat_SU = re.compile('siteurl: \'(.*?)\',').findall(swfparams)[0]
		xbmc.output('PlayTrack ->   stat_SU = %s'%stat_SU)

		stat_XF = re.compile('playerxml: \'(.*?)\',').findall(swfparams)[0]
		xbmc.output('PlayTrack ->   stat_XF = %s'%stat_XF)

	except:
		showMessage('Ой, Ошибка!', 'Не разобраны параметры плеера!')
		return False

	d = datetime.fromtimestamp(int(stat_ti) + 10800) # GMT + 3 (3600 * 3)
	seek_sec = int(d.strftime('%S'))

	playList = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
	playList.clear()

	x = 60
	min_delta = timedelta(minutes = 1)
	while x >= 0:
		x -= 1
		Playable_URL = 'http://dt.moskva.fm/files/%s/mp4/%s.mp4?%s'%(stat_id, d.strftime('%Y/%m/%d/%H%M'), random.random())
		xbmc.output(' + Playable_URL %s' % Playable_URL)

		playList.add(Playable_URL)
		d += min_delta

	p = xbmc.Player()
	p.play(playList)
	p.seekTime(seek_sec)

	return True
	#*******************************************************************#
	#		Код ниже - отключен
	#*******************************************************************#

#	pos_year   = d.year
#	pos_month  = d.month
#	pos_day    = d.day
#	pos_hour   = d.hour
#	pos_minute = d.minute
#	pos_second = d.second
#	xbmc.output('PlayTrack ->   Year = %s'%pos_year)
#	xbmc.output('PlayTrack ->    Mon = %s'%pos_month)
#	xbmc.output('PlayTrack ->    Day = %s'%pos_day)
#	xbmc.output('PlayTrack ->   hour = %s'%pos_hour)
#	xbmc.output('PlayTrack -> minute = %s'%pos_minute)
#	xbmc.output('PlayTrack -> second = %s'%pos_second)



	new_target = 'http://%s/%s?rnd=%s&time=%s&station=%s&startat=%s'%('www.moskva.fm',stat_XF,rnd,stat_ti,stat_id,stat_ti)
	xbmc.output('PlayTrack ->   new_target = %s'%new_target)
	http2 = getURL(new_target, swfobject)
	xbmc.output('PlayTrack ->   http2 = %s'%http2)
	#except:	pass

	xbmc.output('*** PARSING XML ***')

	Reg_station = GetRegion(http2, 'station', True)
	if Reg_station <> None:
		station_id    = GetRegion(Reg_station[0], 'id')    # <id>4010</id>
		station_name  = GetRegion(Reg_station[0], 'name')  # <name>Радио Classic</name>
		station_freq  = GetRegion(Reg_station[0], 'freq')  # <freq>100.9 FM</freq>
		station_url   = GetRegion(Reg_station[0], 'url')   # <url>http://www.moskva.fm/stations/FM_100.9</url>
		station_file  = GetRegion(Reg_station[0], 'file')  # <file>http://dt.moskva.fm/files/4010/mp4/YYYY/MM/DD/HHNN.mp4</file>
		station_image = GetRegion(Reg_station[0], 'image') # <image>http://css.moskva.fm/img/stations/msk/100_9_60x60.png</image>

		xbmc.output('PlayTrack ->      station_id = %s' % station_id)
		xbmc.output('PlayTrack ->    station_name = %s' % station_name)
		xbmc.output('PlayTrack ->    station_freq = %s' % station_freq)
		xbmc.output('PlayTrack ->     station_url = %s' % station_url)
		xbmc.output('PlayTrack ->    station_file = %s' % station_file)
		xbmc.output('PlayTrack ->   station_image = %s' % station_image)


	else:
		showMessage('Ой, Ошибка!', 'Регион \'station\' не найден!')
		return False


	Reg_tracks = GetRegion(http2, 'tracks', True)
	if Reg_tracks <> None:
		Reg_track = re.compile('<track (.*?)</track>', re.DOTALL).findall(Reg_tracks[0])
		if len(Reg_track) == 0:
			showMessage('Ой, Ошибка!', 'track не найден!')
			return False
		for cur_track in Reg_track:
			trackinfo_artistname  = GetRegion(cur_track, 'artistname') # Andrea Bocelli
			trackinfo_artisturl   = GetRegion(cur_track, 'artisturl')  # http://www.moskva.fm/artist/andrea_bocelli/
			trackinfo_trackname   = GetRegion(cur_track, 'trackname') # >Caro Gesu' Bambino
			trackinfo_trackurl    = GetRegion(cur_track, 'trackurl')  # http://www.moskva.fm/artist/andrea_bocelli/song_1956215
			trackinfo_duration    = GetRegion(cur_track, 'duration') # 01:48
			trackinfo_time        = GetRegion(cur_track, 'time') # 2010:02:24:13:37:12
			trackinfo_timestamp   = GetRegion(cur_track, 'timestamp') #  1267007832
			trackinfo_cover       = GetRegion(cur_track, 'cover') # http://img.moskva.fm/covers/80/60/1946960.gif
			trackinfo_playcount   = GetRegion(cur_track, 'playcount') # 30
			trackinfo_artistsongs = GetRegion(cur_track, 'artistsongs') # 10437
			trackinfo_comments    = GetRegion(cur_track, 'comments') # 1
			trackinfo_file        = GetRegion(cur_track, 'file')
			# http://dt.moskva.fm/files/4010/mp4/YYYY/MM/DD/HHNN.mp4

			xbmc.output('PlayTrack ->       trackinfo_artistname = %s' % trackinfo_artistname)
			xbmc.output('PlayTrack ->        trackinfo_artisturl = %s' % trackinfo_artisturl)
			xbmc.output('PlayTrack ->        trackinfo_trackname = %s' % trackinfo_trackname)
			xbmc.output('PlayTrack ->         trackinfo_trackurl = %s' % trackinfo_trackurl)
			xbmc.output('PlayTrack ->         trackinfo_duration = %s' % trackinfo_duration)
			xbmc.output('PlayTrack ->             trackinfo_time = %s' % trackinfo_time)
			xbmc.output('PlayTrack ->        trackinfo_timestamp = %s' % trackinfo_timestamp)
			xbmc.output('PlayTrack ->            trackinfo_cover = %s' % trackinfo_cover)
			xbmc.output('PlayTrack ->        trackinfo_playcount = %s' % trackinfo_playcount)
			xbmc.output('PlayTrack ->      trackinfo_artistsongs = %s' % trackinfo_artistsongs)
			xbmc.output('PlayTrack ->         trackinfo_comments = %s' % trackinfo_comments)
			xbmc.output('PlayTrack ->             trackinfo_file = %s' % trackinfo_file)

			YYYY = trackinfo_time[0:4]
			MM = trackinfo_time[5:7]
			DD = trackinfo_time[8:10]
			HH = trackinfo_time[11:13]
			MM = trackinfo_time[14:16]
			SS = trackinfo_time[17:19]

			trackinfo_file_work = trackinfo_file
			trackinfo_file_work = trackinfo_file_work.replace('YYYY', YYYY)
			trackinfo_file_work = trackinfo_file_work.replace('MM', MM)
			trackinfo_file_work = trackinfo_file_work.replace('DD', DD)
			trackinfo_file_work = trackinfo_file_work.replace('HH', HH)
			trackinfo_file_work = trackinfo_file_work.replace('NN', MM)
			trackinfo_file_work = trackinfo_file_work + '?' + str(random.random())

			xbmc.output('PlayTrack -> XXXXXX trackinfo_file_work = %s' % trackinfo_file_work)

			playList.add(trackinfo_file_work)
			# playList.add(cur_url, listitem)

			#xbmc.Player().play(trackinfo_file_work)

	else:
		showMessage('Ой, Ошибка!', 'Регион "tracks" не найден!')
		return False


	xbmc.Player(xbmc.PLAYER_CORE_AUTO).play(playList)




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
xbmc.output('START PLUGIN mode= %s'%mode)


if   mode == None:
	get_root()

elif mode == 'OpenArtists':
	OpenArtists(url)

elif mode == 'OpenArtist':
	OpenArtist(url)

elif mode == 'PlayTrack':
	PlayTrack(url)

elif mode == 'OpenStations':
	OpenStations(url)

elif mode == 'OpenPrograms':
	OpenPrograms(url)

elif mode == 'OpenCharts':
	OpenCharts(url)

elif mode == 'OpenEvents':
	OpenEvents(url)

