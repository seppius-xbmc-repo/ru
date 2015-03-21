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
import urllib2, re, string, xbmc, xbmcgui, xbmcplugin, os, urllib, cookielib

handle = int(sys.argv[1])

PLUGIN_NAME   = 'TV-HERE.RU'
SITE_HOSTNAME = 'tv-here.ru'
SITEPREF      = 'http://%s' % SITE_HOSTNAME
SITE_URL      = SITEPREF + '/'

phpsessid_file = os.path.join(xbmc.translatePath('special://temp/'), 'plugin_video_tvhere.sess')
thumb = os.path.join( os.getcwd(), "icon.png" )

def clean(name):
	remove=[('&nbsp;', ''), ('&mdash;', '-'), ('&hellip;', '.'), ('&ndash;', '-'), ('&laquo;', '"'), ('&ldquo;', '"'), ('&ldquo;', '"'), ('&raquo;', '"'), ('&quot;', '"')]
	for trash, crap in remove:
		name=name.replace(trash, crap)
	return name

def Get(url, ref=None):
	cj = cookielib.CookieJar()
	h  = urllib2.HTTPCookieProcessor(cj)
	opener = urllib2.build_opener(h)
	urllib2.install_opener(opener)
	post = None
	request = urllib2.Request(url, post)
	request.add_header('User-Agent', 'Opera/10.60 (X11; openSUSE 11.3/Linux i686; U; ru) Presto/2.6.30 Version/10.60')
	request.add_header('Host', SITE_HOSTNAME)
	request.add_header('Accept', 'text/html, application/xml, application/xhtml+xml, */*')
	request.add_header('Accept-Language', 'ru,en;q=0.9')
	if ref != None:
		request.add_header('Referer', ref)
	if os.path.isfile(phpsessid_file):
		fh = open(phpsessid_file, 'r')
		phpsessid = fh.read()
		fh.close()
		request.add_header('Cookie', 'PHPSESSID=' + phpsessid)
	o = urllib2.urlopen(request)
	for index, cookie in enumerate(cj):
		cookraw = re.compile('<Cookie PHPSESSID=(.*?) for.*/>').findall(str(cookie))
		if len(cookraw) > 0:
			fh = open(phpsessid_file, 'w')
			fh.write(cookraw[0])
			fh.close()
	http = o.read()
	o.close()
	return http

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

def CheckHttp(data):
	if (data.find('http://') == -1):
		data = SITEPREF + data
	return data

def ShowRoot(url):
	http = Get(url)
	if http == None:
		xbmc.output('[%s] ShowRoot() Error 1: http == None URL=%s' % (PLUGIN_NAME, url))
		return
	raw1 = re.compile('<div class="menuheader expandable">(.+?)</div>(.*?)\s*</div>\s', re.DOTALL).findall(http)
	if len(raw1) == 0:
		xbmc.output('[%s] ShowRoot() Error 2: http == None URL=%s' % (PLUGIN_NAME, url))
		return
	for raw_block in raw1:
		block_name = raw_block[0]
		raw2 = re.compile('<a href="(.*?)" title="(.*?)">(.*?)</a>').findall(raw_block[1])
		if len(raw2) != 0:
			for row_url, row_title, row_name in raw2:
				row_url = CheckHttp(row_url)
				Title = block_name + ' : ' + row_title
				listitem = xbmcgui.ListItem(Title)
				listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
				if (row_url.find('.html') == -1):
					purl = sys.argv[0] + '?mode=OpenCat'\
						+ '&url=' + urllib.quote_plus(row_url)\
						+ '&title=' + urllib.quote_plus(Title)
					xbmcplugin.addDirectoryItem(handle, purl, listitem, True)
				else:
					purl = sys.argv[0] + '?mode=OpenPage'\
						+ '&url=' + urllib.quote_plus(row_url)\
						+ '&title=' + urllib.quote_plus(Title)
					xbmcplugin.addDirectoryItem(handle, purl, listitem, False)
		else:
			xbmc.output('[%s] ShowRoot() Error 3:len(raw2) == 0 raw_block[1]=%s' % (PLUGIN_NAME, raw_block[1]))

def OpenCat(url, name):
	xbmc.output('def OpenCat(%s, %s):' % (url, name))
	http = Get(url)
	if http == None:
		xbmc.output('[%s] OpenCat() Error 1: http == None URL=%s' % (PLUGIN_NAME, url))
		return
	http = http.replace('</tr><tr>', '\n')
	raw1 = re.compile('<img src=\"(.*?)\".*>(.*?)</td>.*<a href=\"(.*?)\".*title=\"(.*?)\">(.*?)</a>(.*?)</b></td>').findall(http)
	if len(raw1) == 0:
		xbmc.output('[%s] OpenCat() Error 2: len(raw1) == 0 URL=%s' % (PLUGIN_NAME, url))
		xbmc.output(http)
		return
	for row_img, row_blob, row_url, row_des, row_name, row_plot in raw1:
		row_url = CheckHttp(row_url)
		Title = name + ' : ' + row_name
		Plot  = clean(row_plot)
		Genre = clean(row_des)
		listitem = xbmcgui.ListItem(row_name)
		listitem.setInfo(type = "Video", infoLabels = {
			"Title": 	row_name,
			"Studio": 	row_url,
			"Plot": 	Plot,
			"Genre": 	Genre } )
		purl = sys.argv[0] + '?mode=OpenPage'\
			+ '&url=' + urllib.quote_plus(row_url)\
			+ '&title=' + urllib.quote_plus(Title)
		xbmcplugin.addDirectoryItem(handle, purl, listitem, False)

def OpenPage(url, name):
	xbmc.output('def OpenPage(%s, %s):' % (url, name))
	http = Get(url)
	if http == None:
		xbmc.output('[%s] OpenPage() Error 1: http == None URL=%s' % (PLUGIN_NAME, url))
		return
	raw1 = re.compile('<script language=\"JavaScript\">(.*?)\(\"(.*?)\"\);</script>').findall(http)
	if len(raw1) == 0:
		xbmc.output('[%s] OpenPage() Error 2: len(raw1) == 0 URL=%s' % (PLUGIN_NAME, url))
		xbmc.output(http)
		return
	play_link = raw1[0][1]
	if play_link[0] == '/':
		play_link = CheckHttp(play_link)

	if (raw1[0][0] == 'fr'):
		play_link = re.compile('__streamurl__=(.*?)\"').findall(raw1[0][1])
	xbmc.output('*** Play_MODE = %s' % raw1[0][0])
	xbmc.output('*** Play_LINK = %s' % play_link)
	item = xbmcgui.ListItem(name, iconImage = thumb, thumbnailImage = thumb)
	item.setInfo(type="Video", infoLabels={"Title": name})
	xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(play_link, item)


params = get_params()
mode  = None
url   = ''
title = ''
ref   = ''
img   = ''

try:
	mode  = urllib.unquote_plus(params["mode"])
except:
	pass

try:
	url  = urllib.unquote_plus(params["url"])
except:
	pass

try:
	title  = urllib.unquote_plus(params["title"])
except:
	pass
try:
	img  = urllib.unquote_plus(params["img"])
except:
	pass

if mode == None:
	ShowRoot(SITE_URL)
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle)

elif mode == 'OpenCat':
	OpenCat(url, title)
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle)

elif mode == 'OpenPage':
	OpenPage(url, title)


