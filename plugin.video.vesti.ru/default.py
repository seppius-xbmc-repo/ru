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
import urllib2, re, xbmcaddon, string, xbmc, xbmcgui, xbmcplugin, os, urllib

#__settings__ = xbmcaddon.Addon(id='plugin.video.vesti.rss')
#__language__ = __settings__.getLocalizedString

HEADER     = "Opera/10.60 (X11; openSUSE 11.3/Linux i686; U; ru) Presto/2.6.30 Version/10.60"
VESTI_URL  = 'http://www.vesti.ru'

handle = int(sys.argv[1])
vesti_thumb   = os.path.join( os.getcwd(), "default.tbn" )
import simplejson as json
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

def GET(target, post=None):
	try:
		req = urllib2.Request(url = target)
		req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 5.1; rv:16.0) Gecko/20100101 Firefox/16.0')
		req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
		resp = urllib2.urlopen(req)
		#CE = resp.headers.get('content-encoding')
		http = resp.read()
		resp.close()
		return http
	except: return None
	
def clean(name):
	remove=[('<span>',' '),('</span>',' '),('&amp;','&'),('&quot;','"'),('&#39;','\''),('&nbsp;',' '),('&laquo;','"'),('&raquo;', '"'),('&#151;','-'),('<nobr>',''),('</nobr>',''),('<P>',''),('</P>','')]
	for trash, crap in remove:
		name=name.replace(trash, crap)
	return name

def get_programs(isLive=False):
	try:
		req = urllib2.Request(VESTI_URL + '/vesti.rss')
		req.add_header('User-Agent', HEADER)
		f = urllib2.urlopen(req)
		a = f.read()
		f.close()
	except:
		return
	flv_url_array = []
	name_array = []
	plot_array = []
	Category_array = []
	PubDate_array = []
	ImageURL_array = []
	array_size = 0
	#print a
	#<enclosure url="http://www.vesti.ru/videos?vid=461367" type="video/x-flv" />
	
	
	start_prog = re.compile('<item>(.*?)</item>', re.DOTALL).findall(a)
	x = 2
	if len(start_prog) > 0:
		for Rss_data in start_prog:
			s_utf8 = Rss_data
			s_uni = s_utf8.decode('cp1251')
			Rss_data = s_uni.encode('utf8')
			item_data = re.compile('<title>(.+?)</title>\s.*<link>(.+?)</link>\s.*<pdalink>(.+?)</pdalink>\s.*<description>(.+?)</description>\s.*<pubDate>(.+?)</pubDate>\s.*<category>(.+?)</category>\s.*<enclosure url="(.+?)" type="image/jpeg" />\s.*<enclosure url="(.+?)" type="video/x-flv" />\s.*<yandex:full-text>(.+?)</yandex:full-text>', re.MULTILINE| re.DOTALL).findall(Rss_data)
			if len(item_data) > 0:
				for Title, Link, PDALink, Descr, PubDate, Category, ImageURL, VideoURL, FullText in item_data:
					vid_id = re.compile('.*vid=([0-9]*)').findall(VideoURL)[0]
					#print vid_id
					extvidlink='http://www.vesti.ru/xml/playlist.html?type=%s'%str(vid_id)
					http= GET(extvidlink)
					json1=json.loads(http)
					#print json1
					surl=''
					try: surl= json1[0]['video'].replace('/','\\').replace('www.vgtrk.cdnvideo.ru','cdn1.vesti.ru').replace(';','&').replace('&amp','')
					except: pass
					try: surl= json1['video'].replace('/','\\').replace('www.vgtrk.cdnvideo.ru','cdn1.vesti.ru').replace(';','&').replace('&amp','')
					except: pass
					#surl=surl.split('?')[0]
					flv_url =surl
					#var html5 = {"picture":"http:\/\/cdn1.vesti.ru\/vh\/pictures\/b\/230\/228.jpg","video":"http:\/\/cdn1.vesti.ru\/_cdn_auth\/secure\/v\/vh\/mp4\/medium\/176\/098.mp4?auth=vh&vid=176098"};
					#flv_url = '' #'http://www.vesti.ru/flv.html?vid='+str(vid_id)+'.flv'
					cln_title = clean(Title)
					Plot = clean(FullText)
					listitem=xbmcgui.ListItem(str(x)+'. '+cln_title,iconImage=ImageURL,thumbnailImage=ImageURL)
					listitem.setInfo(type="Video", infoLabels = {
						"Title": 	str(x)+'. '+cln_title,
						"Studio": 	'VESTI.RU',
						"Director": 	Link,
						"Plot": 	Plot,
						"Genre": 	Category + ' * ' + PubDate,
						"Date": 	PubDate } )
					if isLive:
						try:
							setindex = flv_url_array.index(flv_url)
							Plo = Category + ' * ' + PubDate + ' * ' + cln_title
							plot_array[setindex] += '\n\n' + Plo + '\n\n' + Plot
						except:
							flv_url_array.append(flv_url)
							name_array.append(cln_title)
							plot_array.append(Plot)
							Category_array.append(Category)
							PubDate_array.append(PubDate)
							ImageURL_array.append(ImageURL)

					else:
						try: xbmcplugin.addDirectoryItem(handle, flv_url, listitem, False)
						except: pass
					x += 1
	if isLive:
		i = 0
		for cur_url in flv_url_array:
			name = name_array[i]
			plot = plot_array[i]
			Cat = Category_array[i]
			PubDat = PubDate_array[i]
			img = ImageURL_array[i]
			listitem=xbmcgui.ListItem(name, iconImage=img, thumbnailImage=img)
			listitem.setInfo(type="Video", infoLabels = {
				"Title": 	name,
				"Studio": 	'VESTI.RU',
				"Plot": 	plot,
				"Genre": 	Cat + ' * ' + PubDat,
				"Date": 	PubDat } )
			playList.add(cur_url, listitem)
			i += 1


params = get_params()
mode  = None

try:
	mode  = urllib.unquote_plus(params["mode"])
except:
	pass

if mode == None:
	listitem = xbmcgui.ListItem('1. VESTI.Live!', iconImage=vesti_thumb, thumbnailImage=vesti_thumb)
	url = sys.argv[0] + "?mode=live"
	xbmcplugin.addDirectoryItem(handle, url, listitem, False)
	get_programs(False)

	xbmcplugin.setPluginCategory(handle, 'VESTI.RU')
	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_DATE)
	xbmcplugin.endOfDirectory(handle)

elif mode == 'live':
	playList = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	playList.clear()
	get_programs(True)
	player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
	player.play(playList)

