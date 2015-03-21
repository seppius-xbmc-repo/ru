#!/usr/bin/python
# -*- coding: utf-8 -*-

# *      Copyright (C) 2011 TDW
# *
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
import time

import httplib
import urllib
import urllib2
import re
import sys
import os
import Cookie

import string, xbmc, xbmcgui, xbmcplugin, os, urllib, cookielib, xbmcaddon, time, codecs

from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
import socket
socket.setdefaulttimeout(50)
try:
	import krasfs
	tft=krasfs.Tracker()
except: pass
	
def stft(text):
	RL=tft.Search(text, 4)
	if len(RL)>0:
		Title = "[COLOR F050F050]"+"[-------  Мультимедийный портал «KrasFS.ru»  ---------]"+"[/COLOR]"
		row_url = Title
		listitem = xbmcgui.ListItem(Title)
		listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
		purl = sys.argv[0] + '?mode=Search'\
			+ '&url=' + urllib.quote_plus(row_url)\
			+ '&title=' + urllib.quote_plus(Title)\
			+ '&text=' + urllib.quote_plus('0')
		xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

	for itm in RL:
		n=0
		for i in ["PDF","pdf","FLAC","flac","FB2","fb2","MP3","mp3"]:
			filtr=itm[2].find(i)
			if filtr>0:n+=1
		if n==0:
				Title = itm[0]+"|"+itm[1]+"|  "+itm[2]
				row_url = itm[3]
				cover=""
				dict={}
				listitem = xbmcgui.ListItem(Title, thumbnailImage=cover, iconImage=cover)
				listitem.setProperty('fanart_image', cover)
				purl = sys.argv[0] + '?mode=OpenCat'\
					+ '&url=' + urllib.quote_plus(row_url)\
					+ '&title=' + urllib.quote_plus(Title)\
					+ '&info=' + urllib.quote_plus(repr(dict))
				xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

siteUrl = 'www.lostfilm.tv'
httpSiteUrl = 'http://' + siteUrl
httpSiteUrl = 'https://' + siteUrl
sid_file = os.path.join(xbmc.translatePath('special://temp/'), 'plugin.video.LostFilm.cookies.sid')

h = int(sys.argv[1])
handle = int(sys.argv[1])

PLUGIN_NAME   = 'LostFilm'

addon = xbmcaddon.Addon(id='plugin.video.LostFilm')
__settings__ = xbmcaddon.Addon(id='plugin.video.LostFilm')
xbmcplugin.setContent(int(sys.argv[1]), 'movies')

icon = os.path.join(addon.getAddonInfo('path'), 'icon.png')
thumb = os.path.join( addon.getAddonInfo('path'), "icon.png" )
fanart = os.path.join( addon.getAddonInfo('path'), "fanart.jpg" )
LstDir = os.path.join( addon.getAddonInfo('path'), "playlists" )
dbDir = os.path.join( addon.getAddonInfo('path'), "db" )
ImgPath = os.path.join( addon.getAddonInfo('path'), "logo" )
playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)

#---------libtorrents-torrenter-by-slng---
import Downloader
try:import Downloader
except: pass
def playTorrent(url, StorageDirectory):
		torrentUrl = url#__settings__.getSetting("lastTorrent")
		if 0 != len(torrentUrl):
			contentId = 0#int(urllib.unquote_plus(url))
			torrent = Downloader.Torrent(torrentUrl, StorageDirectory)
			torrent.startSession(contentId)
			iterator = 0
			progressBar = xbmcgui.DialogProgress()
			progressBar.create('Подождите', 'Идёт поиск сидов.')
			downloadedSize = 0
			while downloadedSize < (44 * 1024 * 1024): #not torrent.canPlay:
				time.sleep(0.1)
				progressBar.update(iterator)
				iterator += 1
				if iterator == 100:
					iterator = 0
				downloadedSize = torrent.torrentHandle.file_progress()[contentId]
				dialogText = 'Preloaded: ' + str(downloadedSize / 1024 / 1024) + ' MB / ' + str(torrent.getContentList()[contentId].size / 1024 / 1024) + ' MB'
				peersText = ' [%s: %s; %s: %s]' % ('Seeds', str(torrent.torrentHandle.status().num_seeds), 'Peers', str(torrent.torrentHandle.status().num_peers))
				speedsText = '%s: %s Mbit/s; %s: %s Mbit/s' % ('Downloading', str(torrent.torrentHandle.status().download_payload_rate * 8/ 1000000), 'Uploading', str(torrent.torrentHandle.status().upload_payload_rate * 8 / 1000000))
				progressBar.update(iterator, 'Seeds searching.' + peersText, dialogText, speedsText)
				if progressBar.iscanceled():
					progressBar.update(0)
					progressBar.close()
					torrent.threadComplete = True
					return
			progressBar.update(0)
			progressBar.close()
			playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
			playlist.clear()
			listitem = xbmcgui.ListItem(torrent.getContentList()[contentId].path)
			playlist.add('file:///' + torrent.getFilePath(contentId), listitem)
			progressBar.close()
			xbmc.Player().play(playlist)
			progressBar.close()
			time.sleep(15)
			while 1 == xbmc.Player().isPlayingVideo():
				torrent.fetchParts()
				torrent.checkThread()
				time.sleep(1)
			xbmc.executebuiltin("Notification(%s, %s)" % ('Информация', 'Загрузка торрента прекращена.'))
			torrent.threadComplete = True
		else:
			print " Unexpected access to method playTorrent() without torrent content"


#---------tsengine----by-nuismons-----


from TSCore import TSengine as tsengine

def play_url(params):
	torr_link=params['file']
	img=urllib.unquote_plus(params["img"])
	#showMessage('heading', torr_link, 10000)
	TSplayer=tsengine()
	out=TSplayer.load_torrent(torr_link,'TORRENT')
	if out=='Ok':
		for k,v in TSplayer.files.iteritems():
			li = xbmcgui.ListItem(urllib.unquote(k))
			uri = construct_request({
				'torr_url': torr_link,
				'title': k,
				'ind':v,
				'img':img,
				'mode': 'play_url2'
			})
			try:
				if k in eval(__settings__.getSetting("History")): li.select(True)
			except:
				pass
			li.addContextMenuItems([('Hайти на KrasFS', 'XBMC.ActivateWindow(10025,"plugin://plugin.video.LostFilm/?mode=KFS&text='+k+'")', 'XBMC.ActivateWindow(10025,"plugin://plugin.video.LostFilm/?mode=OpenCat&text=0&file='+url+'&img='+img+'")')])
			#crt=construct_request({'mode': 'KFS','text': k})
			#li.addContextMenuItems([('Hайти на KrasFS', 'XBMC.RunPlugin("plugin://plugin.video.LostFilm/?mode=KFS&text='+k+'")')])
			xbmcplugin.addDirectoryItem(handle, uri, li, False)

	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_LABEL)
	xbmcplugin.endOfDirectory(handle)
	TSplayer.end()
	
def play_url2(params):
	#torr_link=params['torr_url']
	torr_link=urllib.unquote_plus(params["torr_url"])
	img=urllib.unquote_plus(params["img"])
	title=urllib.unquote_plus(params["title"])
	H=__settings__.getSetting("History")
	if H=='': HL=[]
	else: HL=eval(H)
	if title not in HL: 
		HL.append(title)
		__settings__.setSetting("History", repr(HL))
	#showMessage('heading', torr_link, 10000)
	TSplayer=tsengine()
	out=TSplayer.load_torrent(torr_link,'TORRENT')
	if out=='Ok':
		TSplayer.play_url_ind(int(params['ind']),title, icon, img)
	TSplayer.end()

#===================old=========================


def construct_request(params):
	return '%s?%s' % (sys.argv[0], urllib.urlencode(params))

def htmlEntitiesDecode(string):
	return BeautifulStoneSoup(string, convertEntities=BeautifulStoneSoup.HTML_ENTITIES).contents[0]

def showMessage(heading, message, times = 3000):
	xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))

headers  = {
	'User-Agent' : 'Opera/9.80 (X11; Linux i686; U; ru) Presto/2.7.62 Version/11.00',
	'Accept'     :' text/html, application/xml, application/xhtml+xml, image/png, image/jpeg, image/gif, image/x-xbitmap, */*',
	'Accept-Language':'ru-RU,ru;q=0.9,en;q=0.8',
	'Accept-Charset' :'utf-8, utf-16, *;q=0.1',
	'Accept-Encoding':'identity, *;q=0'
}

headers = {'User-Agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; ru; rv:1.9.0.13) Gecko/2009073022 Firefox/3.0.13',
	'Host' : 'vkontakte.ru',
	'Content-Type' : 'application/x-www-form-urlencoded; charset=UTF-8',
	'Connection' : 'close',
}

class TextReader(xbmcgui.Window):
	def __init__(self, txt_data):
		self.bgread = xbmc.translatePath(os.path.join(addon.getAddonInfo('path').replace(';', ''), 'resources', 'img', 'background.png'))
		self.setCoordinateResolution(1) # 0 for 1080
		self.addControl(xbmcgui.ControlImage(0, 0, 1280, 720, self.bgread))
		self.NewsTextBox = xbmcgui.ControlTextBox(10,10,1260,700)
		self.addControl(self.NewsTextBox)
		self.NewsTextBox.setText(txt_data)
		self.scroll_pos = 0
	def onAction(self, action):
		aID = action.getId()
		if aID in [1,3,5]:
			self.scroll_pos -= 5
			self.NewsTextBox.scroll(self.scroll_pos)
		elif aID in [2,4,6]:
			self.scroll_pos += 5
			self.NewsTextBox.scroll(self.scroll_pos)
		elif aID in [9,10]: self.close()


def GET(target, referer, post=None):
	try:
		req = urllib2.Request(url = target, data = post)
		req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
		resp = urllib2.urlopen(req)
		http = resp.read()
		resp.close()
		return http
	except Exception, e:
		#xbmc.log( '[%s]: GET EXCEPT [%s]' % (addon_id, e), 4 )
		showMessage('HTTP ERROR', e, 5000)


def ru(x):return unicode(x,'utf8', 'ignore')
def xt(x):return xbmc.translatePath(x)
	

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

def showMessage(heading, message, times = 50000):
	xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, thumb))

def inputbox():
	skbd = xbmc.Keyboard()
	skbd.setHeading('Поиск:')
	skbd.doModal()
	if skbd.isConfirmed():
		SearchStr = skbd.getText()
		return SearchStr
	else:
		return ""


def debug(s):
	fl = open(os.path.join( ru(LstDir),"test.txt"), "w")
	fl.write(s)
	fl.close()

def GETimg(target, referer=None, post=None):
	lfimg=os.listdir(ru(LstDir))
	nmi =os.path.basename(target)
	if nmi in lfimg:
		return os.path.join( ru(LstDir),nmi)
	else:
		try:
			req = urllib2.Request(url = target, data = post)
			req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
			resp = urllib2.urlopen(req)
			fl = open(os.path.join( ru(LstDir),nmi), "wb")
			fl.write(resp.read())
		#resp.close()
			fl.close()
			return os.path.join( ru(LstDir),nmi)
		except Exception, e:
			#xbmc.log( '[%s]: GET EXCEPT [%s]' % (addon_id, e), 4 )
			return ''
			showMessage('HTTP ERROR', e, 5000)
	
	
	


import re, os, urllib, urllib2, cookielib, time, sys
from time import gmtime, strftime
import urlparse

fcookies = os.path.join(addon.getAddonInfo('path'), r'cookies.txt')

sys.path.append(os.path.join(addon.getAddonInfo('path'), r'resources', r'lib'))
from BeautifulSoup  import BeautifulSoup

import HTMLParser
hpar = HTMLParser.HTMLParser()

#---------- get web page -------------------------------------------------------
def get_HTML(url, post = None, ref = None, get_redirect = False):
    if url.find('http')<0 :url='https:'+url
    #url=url.replace('www.lostfilm.tv','www.lostfilm.tv.3s3s.org')
    request = urllib2.Request(url, post)

    host = urlparse.urlsplit(url).hostname
    if ref==None:
        try:
           ref='http://'+host
        except:
            ref='localhost'

    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host',   host)
    request.add_header('Accept', 'text/html, application/xhtml+xml, */*')
    request.add_header('Accept-Language', 'ru-RU')
    request.add_header('Referer',             ref)
    request.add_header('Content-Type','application/x-www-form-urlencoded')

    try:
        f = urllib2.urlopen(request)
    except IOError, e:
        if hasattr(e, 'reason'):
           print('We failed to reach a server.')
        elif hasattr(e, 'code'):
           print('The server couldn\'t fulfill the request.')
        return 'We failed to reach a server.'

    if get_redirect == True:
        html = f.geturl()
    else:
        html = f.read()

    return html

#-------------------------------------------------------------------------------
# get cookies from last session
import antizapret
cj = cookielib.FileCookieJar(fcookies)
hr  = urllib2.HTTPCookieProcessor(cj)
if __settings__.getSetting("immunicity") == "true": 
	opener = urllib2.build_opener(antizapret.AntizapretProxyHandler(), hr)
else: 
	opener = urllib2.build_opener(hr)
urllib2.install_opener(opener)

#----------- LOGIN to lostfilm.tv ----------------------------------------------
#-- step 1

url1 = 'http://login1.bogi.ru/login.php?referer=http%3A%2F%2Fwww.lostfilm.tv%2F'

#-- enter your login/pass
login = __settings__.getSetting("login")
passw = __settings__.getSetting("password")
if login =="" or passw == '': showMessage('lostfilm', "Проверьте логин и пароль", times = 50000)



values = {
				'login'     : login,
				'password'  : passw,
				'module'    : 1,
				'target'    : 'http://lostfilm.tv/',
				'repage'    : 'user',
				'act'       : 'login'
		}





def Allcat(http):
	#http=xt(http)
	n=http.find('<div class="content_head">')
	k=http.find('<div class="prof" style="height:70px;">')
	http=http[n:k]
	#http=http.replace(chr(10),"")#.replace(chr(13),"")
	http=http.replace("'","*")
	http=http.replace('\t\t<a href="/browse.php?cat=',"Flag1:['")
	http=http.replace('" class="bb_a">',"','")
	http=http.replace('<br><span>(',"','")
	http=http.replace(')</span></a>',"']")
	L=http.splitlines()
	LL=[]
	for i in L:
		if len(i)>6:
			if i[:6]=='Flag1:': 
				LL.append(eval(i[6:]))
	return LL
	
def Allsr(http):
	http=http.replace(chr(13),"")
	http=http.replace("'",'"')
	http=http.replace("\t","")
	http=http.replace('</span>, <span>',chr(10)+"Flag1:['")
	http=http.replace('</span></td>'+chr(10)+'<td class="" nowrap align="right">',"','"+chr(10))
	http=http.replace('<nobr><span style="color:#4b4b4b">',chr(10)+"Flag3:'")
	http=http.replace(')" onMouseOver="StartScrollTitle',")',"+chr(10))
	http=http.replace('</span><br />(',"','")
	http=http.replace(' PROPER', '')
	http=http.replace(')</nobr></div></div></td>',"']"+chr(10))
	http=http.replace('</span><br /></nobr></div></div></td>',"']"+chr(10))
	http=http.replace(').</nobr></div></div></td>',"']"+chr(10))
	http=http.replace('<td class="t_episode_title" onClick="$(document).scrollTop(0);$("#claim-window").show();$("#login-window").hide();$("#register-window").hide();return false;ShowAllReleases',chr(10)+"Flag2:")
	http=http.replace('<td class="t_episode_title" onClick="ShowAllReleases',chr(10)+"Flag2:")
	L=http.splitlines()
	LL=[]
	for i in L:
		if len(i)>6:
			if i[:6]=='Flag1:': tp=i[6:]
			if i[:6]=='Flag2:': tp=tp+i[6:]
			if i[:6]=='Flag3:': 
				tp=tp+i[6:]
				try:LL.append(eval(tp))
				except: print tp
	return LL

def mfindal(http, ss, es):
	L=[]
	while http.find(es)>0:
		s=http.find(ss)
		e=http.find(es)
		i=http[s:e]
		L.append(i)
		http=http[e+2:]
	return L

def Allre(http):
	http=http.replace(chr(10),"")
	ss='valign="top"><img src="img'
	es='</a></nobr></div>'
	L=mfindal(http, ss, es)
	LL=[]
	for i in L:
		ss='src="img'
		es='.png"'
		pic=mfindal(i, ss, es)[0][len(ss):]
		fpic="http://retre.org/img"+pic+".png"
		#print pic
		
		ss='href="http://tracktor'
		es='" style="font-size:18px;font-weight:bold;'
		tor=mfindal(i, ss, es)[0][6:]
		#print tor
		
		#ss='style="font-size:18px;font-weight:bold;">'
		#es='</a><br />\t<span style="font-size:12px; color:black;">'
		#label=mfindal(i, ss, es)[0][len(ss):]
		
		ss='</a><br />\t<span style="font-size:12px; color:black;">'
		es='<br />\t<div style="overflow:'
		label=mfindal(i, ss, es)[0][len(ss):]#+" "+ label
		
		#print label
		LL.append([label, tor, fpic])

	#debug(L[0])
	return LL

def Alln(http):
	n=http.find('<div class="content_head')
	k=http.find('<div style="text-align:center">')
	http=http[n:k]
	#print http
	http=http.replace(chr(10),"")
	http=http.replace(chr(13),"")
	http=http.replace("\t","")
	http=http.replace("'",'"')
	
	http=http.replace("</a>//-->",'')
	http=http.replace('//-->',chr(10)+"Flag1:['")
	http=http.replace('</div><span style="font-family:arial;font-size:14px;color:#000000">',"','")
	http=http.replace('</span><br clear=both><a href="/browse.php?cat=',"','")
	http=http.replace('"><img src="/Static',"','")
	http=http.replace('" alt="',"','")
	
	http=http.replace('" title="',"','")
	http=http.replace('" align="left" class="category_icon" border="0" /></a><span class="torrent_title"><b>',"','")
	http=http.replace('</b></span><br />',"','")
	http=http.replace('</b></span><br clear=both><a href="javascript:{}" onClick="SayThanks',"','")
	http=http.replace('" class="a_thanks"></a><a href=',"','(")
	http=http.replace('/discuss.php?cat=','')
	http=http.replace('&s=','","')
	http=http.replace('&e=','","')
	http=http.replace(' class="a_discuss">',")']"+chr(10))
	http=http.replace("<b>",'')
	http=http.replace('</b><br />',"','")
	http=http.replace('</b></span><br clear=both><a href=',"','--','(")
	#debug(http)
	#print http
	L=http.splitlines()
	LL=[]
	for i in L:
		if len(i)>6:
			if i[:6]=='Flag1:': 
				LL.append(eval(i[6:]))
	#print str(LL)
	return LL

def format_s(s):
	s=str(repr(s))[1:-1]
	s=s.replace('\\xb8','ё')
	s=s.replace('\\xe0','a')
	s=s.replace('\\xe1','б')
	s=s.replace('\\xe2','в')
	s=s.replace('\\xe3','г')
	s=s.replace('\\xe4','д')
	s=s.replace('\\xe5','е')
	s=s.replace('\\xe6','ж')
	s=s.replace('\\xe7','з')
	s=s.replace('\\xe8','и')
	s=s.replace('\\xe9','й')
	s=s.replace('\\xea','к')
	s=s.replace('\\xeb','л')
	s=s.replace('\\xec','м')
	s=s.replace('\\xed','н')
	s=s.replace('\\xee','о')
	s=s.replace('\\xef','п')
	s=s.replace('\\xf0','р')
	s=s.replace('\\xf1','с')
	s=s.replace('\\xf2','т')
	s=s.replace('\\xf3','у')
	s=s.replace('\\xf4','ф')
	s=s.replace('\\xf5','х')
	s=s.replace('\\xf6','ц')
	s=s.replace('\\xf7','ч')
	s=s.replace('\\xf8','ш')
	s=s.replace('\\xf9','щ')
	s=s.replace('\\xfa','ъ')
	s=s.replace('\\xfb','ы')
	s=s.replace('\\xfc','ь')
	s=s.replace('\\xfd','э')
	s=s.replace('\\xfe','ю')
	s=s.replace('\\xff','я')

	s=s.replace('\\xc0','А')
	s=s.replace('\\xc1','Б')
	s=s.replace('\\xc2','В')
	s=s.replace('\\xc3','Г')
	s=s.replace('\\xc4','Д')
	s=s.replace('\\xc5','Е')
	s=s.replace('\\xc6','Ж')
	s=s.replace('\\xc7','З')
	s=s.replace('\\xc8','И')
	s=s.replace('\\xc9','Й')
	s=s.replace('\\xca','К')
	s=s.replace('\\xcb','Л')
	s=s.replace('\\xcc','М')
	s=s.replace('\\xcd','Н')
	s=s.replace('\\xce','О')
	s=s.replace('\\xcf','П')
	s=s.replace('\\xd0','Р')
	s=s.replace('\\xd1','С')
	s=s.replace('\\xd2','Т')
	s=s.replace('\\xd3','У')
	s=s.replace('\\xd4','Ф')
	s=s.replace('\\xd5','Х')
	s=s.replace('\\xd6','Ц')
	s=s.replace('\\xd7','Ч')
	s=s.replace('\\xd8','Ш')
	s=s.replace('\\xd9','Щ')
	s=s.replace('\\xda','Ъ')
	s=s.replace('\\xdb','Ы')
	s=s.replace('\\xdc','Ь')
	s=s.replace('\\xdd','Э')
	s=s.replace('\\xde','Ю')
	s=s.replace('\\xdf','Я')
	
	s=s.replace('\\xab','"')
	s=s.replace('\\xbb','"')
	s=s.replace('\\r','')
	s=s.replace('\\n','\n')
	s=s.replace('\\t','\t')
	s=s.replace("\\x97",'-')
	
	return s


def LF():
	categoryUrl = xt(httpSiteUrl + '/serials.php')
	http =  get_HTML(categoryUrl)
	if http == None:
		showMessage('lostfilm:', 'Сервер не отвечает', 1000)
		return None
	else:
		LL=Allcat(http)
		#debug(http)
		AllList(LL)
		#return LL

def GET_C(c):
	categoryUrl = xt(httpSiteUrl + '/browse.php?cat='+c)
	http =  get_HTML(categoryUrl)
	if http == None:
		showMessage('lostfilm:', 'Сервер не отвечает', 1000)
		return None
	else:
		#debug(http)
		LL=Allsr(http)
		AllListS(LL)
		#return LL

def mfindal(http, ss, es):
	L=[]
	while http.find(es)>0:
		s=http.find(ss)
		e=http.find(es)
		i=http[s:e]
		L.append(i)
		http=http[e+2:]
	return L

def Alln2(h):
	kc=h.find('span class="d_pages_link_selected"')
	nc=h.find('div class="content_head"')
	h=h[nc:kc].replace('\r','').replace('\n','').replace('\t','')
	s='font-size:18px;color:#000000'
	e='float:right;font-family:arial;'
	l=mfindal(h,s,e)[1:]
	LL=[]
	for i in l:
		s='//-->'
		e='</div>'
		n1=mfindal(i,s,e)[0][len(s):]
		
		s='font-size:14px;color:#000000">'
		e='</span>'
		n2=mfindal(i,s,e)[0][len(s):]
		
		s='<a href="/browse.php?cat='
		e='"><img src="/Static'
		n3=mfindal(i,s,e)[0][len(s):]
		
		s='<img src="/Static/icons/'
		e='" alt="'
		n4=mfindal(i,s,e)[0][len(s):]
		
		s='<span class="torrent_title"><b>'
		e='</b></span><br />'
		n5=mfindal(i,s,e)[0][len(s):]
		
		s='howAllReleases'
		e='"></a><br clear=both>'
		try:
			n6=mfindal(i,s,e)[0][len(s):]
		except:
			e='"></a></div><br clear=both>'
			n6=mfindal(i,s,e)[0][len(s):]
		#print n6
		LL.append([n1,n2,n3,n4,n5,n6])
	return LL

	
def GET_N():
	categoryUrl = xt(httpSiteUrl + '/browse.php')
	http =  get_HTML(categoryUrl)
	if http == None:
		showMessage('lostfilm:', 'Сервер не отвечает', 1000)
		return None
	else:
		
		LL=Alln2(http)
		#debug(http)
		
		#LL=Alln(http)
		AllListN(LL)
		#return LL

def GET_R(cse):
	#print cse
	c,s,e=eval(cse)
	categoryUrl = xt(httpSiteUrl + '/nrdr.php?c='+c+'&s='+s+'&e='+e)
	url = get_HTML(url = categoryUrl, get_redirect = True) #-- do not redirect
	http = get_HTML(url)
	if http == None:
		showMessage('lostfilm:', 'Сервер не отвечает', 1000)
		return None
	else:
		H=__settings__.getSetting("History")
		if H=='': HL=[]
		else: HL=eval(H)
		if cse not in HL: HL.append(cse)
		__settings__.setSetting("History", repr(HL))
		LL=Allre(http)
		#debug(http)
		Allrelis(LL)

def AllList(L):
		for i in L:
			#nm=i[2].lower()
			Title = format_s(i[1])
			row_url = i[0]
			dict=get_minfo(row_url)
			try:
				cover=dict["cover"].replace('http:','https:')
				if __settings__.getSetting("immunicity") == "true": cover=GETimg(cover)
			except:cover=""
			listitem = xbmcgui.ListItem(Title, thumbnailImage=cover, iconImage=cover)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			try:listitem.setInfo(type="Video", infoLabels=dict)
			except: pass
			listitem.setProperty('fanart_image', cover)
			purl = sys.argv[0] + '?mode=OpenPage'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&text=' + urllib.quote_plus('0')
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

def AllListN(L):
		if 1==1:
			Title = "[COLOR FF00FF00][Все сериалы][/COLOR]"
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			listitem.addContextMenuItems([('Обновить список', 'Container.Refresh')])
			purl = sys.argv[0] + '?mode=OpenLF'\
				+ '&url=' + urllib.quote_plus('0')\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&text=' + urllib.quote_plus('0')
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)
		#print L
		for i in L:
			#nm=i[2].lower()
			Title = format_s(i[0]+" [B][COLOR FFFFFFFF]"+i[1]+":[/COLOR][/B] "+i[4])
			row_url = i[2]
			sn = i[5]
			dict=get_minfo(row_url)
			try:
				cover=dict["cover"].replace('http:','https:')#"http://www.lostfilm.tv/Static/icons/"+i[3]
				if __settings__.getSetting("immunicity") == "true": cover=GETimg(cover)
				#catcover=cover.replace('/posters/poster_','/icons/cat_')
			except:cover=""
			
			listitem = xbmcgui.ListItem(Title, thumbnailImage=cover, iconImage=cover)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			try:listitem.setInfo(type="Video", infoLabels=dict)
			except: pass
			listitem.setProperty('fanart_image', cover)
			try:
				if sn in eval(__settings__.getSetting("History")): listitem.select(True)
			except:
				pass
			listitem.addContextMenuItems([('Обновить список', 'Container.Refresh')])
			purl = sys.argv[0] + '?mode=OpenRel'\
				+ '&url=' + urllib.quote_plus(sn)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&text=' + urllib.quote_plus('0')
			#parametr='UpdateLibrary("video",'+purl+')'
			#xbmc.executebuiltin(parametr)
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

def AllListS(L):
		#print L
		for i in L:
			nm=i[0].replace(" \xf1\xe5\xe7\xee\xed ","_").replace(" \xf1\xe5\xf0\xe8\xff"," ").replace("\xf1\xe5\xe7\xee\xed","_").replace(" _","[COLOR FF00FF00]")
			if len(nm)==4: nm=nm+"  "
			try:
				Title = nm+" [B][COLOR FFFFFFFF]"+i[2]+"[/COLOR][/B] / "+i[3]
				Title2 = nm+" "+i[2]+" / "+i[3]
				fnd=nm.find("[COLOR")
				if fnd>0: Title = Title2+"[/COLOR]"
			except:Title = i[0]
			row_url = i[1]
			listitem = xbmcgui.ListItem(format_s(Title))#, thumbnailImage=cover, iconImage=cover)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title})
			try:
				if row_url in eval(__settings__.getSetting("History")): listitem.select(True)
			except:
				pass
			purl = sys.argv[0] + '?mode=OpenRel'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus('Title')\
				+ '&text=' + urllib.quote_plus('0')
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)


def Allrelis(L):
		for i in L:
			#print i
			Title = format_s(i[0])#+" "+i[1]+" "+i[2]+" "+i[3]
			cover=i[2]
			row_url = i[1]
			listitem = xbmcgui.ListItem(Title, thumbnailImage=cover, iconImage=cover)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=OpenCat'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus('Title')\
				+ '&text=' + urllib.quote_plus('0')
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)


p = re.compile(r'<.*?>')

def mfindal(http, ss, es):
	L=[]
	while http.find(es)>0:
		s=http.find(ss)
		e=http.find(es)
		i=http[s:e]
		L.append(i)
		http=http[e+2:]
	return L

def clearinfo2(http):
	n=http.find("window.open('/rdr.php?c=")
	k=http.rfind('</span>\n</div>\n<div>')
	http=xt(http[n:k])
	s='Год выхода:'
	e='Страна: '
	l=mfindal(http, ss, es)
	

def clearinfo(str):
	n=str.find("window.open('/rdr.php?c=")
	k=str.rfind('t_row even')
	k=str.rfind('</span>\n</div>\n<div>')
	str=xt(str[n:k])
	str=format_s(str)
	
	#str=str.replace(chr(13)+chr(10),chr(10))
	#str=str.replace(chr(10)+chr(13),chr(10))
	str=str.replace(chr(13),chr(10))
	str=str.replace(chr(10),'')
	str=str.replace('\t','')
	str=str.replace("'",'"')
	str=str.replace('" alt="" title',chr(10))
	str=str.replace('Год выходa:',chr(10)+"Год выхода:")
	str=str.replace('О сериaле',chr(10)+"Описание:")
	str=str.replace('</h1><br /><img src="',chr(10)+"Обложка:")
	str=str.replace('<span>',"")
	str=str.replace('</span>',"")
	str=str.replace("<br />",chr(10))
	str=str.replace("</h2></div></div>"," ")
	
	str=str.replace('</script><div><h1>',chr(10)+"Название:")
	str=str.replace('Жaнр:',chr(10)+"Жанр:")
	str=str.replace('Режиссер:',chr(10)+"Режиссер:")
	str=str.replace('Страна:',chr(10)+"Страна:")
	
	str=p.sub('', str)
	
	str=str.replace(chr(10)+chr(10)+chr(10),chr(10))
	str=str.replace(chr(10)+chr(10),chr(10))
	str=str.replace('   ',' ')
	str=str.replace('  ',' ')
	str=str.replace('О фильме:'+chr(10), chr(10)+'О фильме: ')
	str=str.replace('О фильме: '+chr(10), chr(10)+'О фильме: ')
	str=str.replace('Описание:'+chr(10), chr(10)+'Описание: ')
	str=str.replace('Описание: '+chr(10), chr(10)+'Описание: ')
	str=str.replace('Оценка',chr(10)+"Оценка: ")
	str=str.replace('.jpg', ".jpg"+chr(10))
	str=str.replace('.jpeg', ".jpeg"+chr(10))
	str=str.replace('.png', ".png"+chr(10))
	#debug(str)
	return str


import sqlite3 as db
db_name = os.path.join( addon.getAddonInfo('path'), "move_info.db" )
c = db.connect(database=db_name)
cu = c.cursor()

def add_to_db(n, item):
		err=0
		tor_id="n"+n
		litm=str(len(item))
		try:
			cu.execute("CREATE TABLE "+tor_id+" (db_item VARCHAR("+litm+"), i VARCHAR(1));")
			c.commit()
		except: err=1
			#print "Ошибка БД"
		if err==0:
			cu.execute('INSERT INTO '+tor_id+' (db_item, i) VALUES ("'+item+'", "1");')
			c.commit()
			#c.close()

def get_inf_db(n):
		#import sqlite3 as db
		#db_name = os.path.join( addon.getAddonInfo('path'), "move_info.db" )
		#c = db.connect(database=db_name)
		#cu = c.cursor()
		tor_id="n"+n
		cu.execute(str('SELECT db_item FROM '+tor_id+';'))
		c.commit()
		info = cu.fetchall()
		#c.close()
		return info


def get_minfo(ntor):
			
			try: dict=eval(xt(get_inf_db(ntor)[0][0]))#dbi = move_info_db[ntor]
			except: #dbi = None
				#debug (eval(get_inf_db(ntor)[0][0]))
			#if dbi == None:
				hp =  get_HTML(httpSiteUrl + '/browse.php?cat='+ntor)
				hp=clearinfo(hp)
				LI=hp.splitlines()
				dict={}
				cover=''
				for itm in LI:
					#print itm
					nc=itm.find(':')
					flag=itm[:nc]
					if flag=='Обложка': 
						cvr=itm.strip()
						dict['cover']=httpSiteUrl + itm[nc+1:].strip()
					elif flag=='Название': dict['title']=itm[nc+1:].strip().replace("&#960;",'п')
					elif flag=='Оценка': 
						nr=itm.find('из')
						try:
							dict['rating']=float(itm[nc+2:nr])
							#dict['votes']=str(int(int(itm[nc+2:nr])/2))
						except: pass
					elif flag=='Год выхода':
						try:dict['year']=int(itm.strip()[nc+1:])
						except: 
							try:dict['year']=int(itm.strip()[nc+1:nc+6])
							except: pass
					elif flag=='Жанр': dict['genre']=xt(itm[nc+1:].strip())
					#elif flag=='Режиссер': dict['director']=itm[nc+1:].strip()
					#elif flag=='В ролях': 
					#	dict['cast']=itm[nc+1:].split(",")[:6]
					elif flag=='О фильме' or flag=='Описание':
						jjk=itm.replace("'",'`').replace('"',"``")[nc+1:].strip()
						#debug (jjk)#[:10]
						
						dict['plot']=jjk#[1:-1]
						
				#move_info_db[ntor]=dict
				try:add_to_db(ntor, repr(dict))
				except: pass
					#try:add_to_db(ntor, repr(dict).replace('"',"'"))
					#except: pass

			return dict


def open_pl(pl_name):
	line=""
	Lurl=[]
	Ltitle=[]
	Lnum=[]
	tvlist = os.path.join(LstDir, pl_name+'.txt')
	fl = open(tvlist, "r")
	n=0
	for line in fl.xreadlines():
		n+=1
		if len(line)>5:
			pref=line[:5]
			Lurl.append(ru(line).replace(u'\n','').replace(u'\r',''))
			Lurl.append(ru(line).replace(u'\n','').replace(u'\r',''))
			Lnum.append(len(Lurl)-1)
	fl.close()
	return (Ltitle, Lurl, Lnum)


def OpenCat(url, name, dict):
	nnn=url.rfind("/")+1
	ntor=xt(url[nnn:]+".torrent")
	rtpath=ru(os.path.join(LstDir, ntor))
	xtpath=xt(os.path.join(LstDir, ntor))
	try:
		urllib.urlretrieve(xt(url),rtpath)
	except:
		urllib.urlretrieve(xt(url),xtpath)
	playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	playlist.load(xtpath)
	Ltitle, Lurl, Lnum = [],[],[]
	n=0
	
	for i in range (len(playlist)):
		p=playlist[i]
		n+=1
		Ltitle.append(p.getdescription())
		Lurl.append(p.getfilename())
		Lnum.append(n-1)
		
	lgl=(Ltitle, Lurl, Lnum)
	for i in range (len(Ltitle)):
		#Title = formating(Ltitle[i])
		row_name = Ltitle[i]
		row_url = Lurl[i]
		try:cover=dict["cover"]
		except:cover=""
		listitem = xbmcgui.ListItem(row_name, thumbnailImage=cover, iconImage=cover )
		try:listitem.setInfo(type = "Video", infoLabels = dict)
		except: pass
		listitem.setProperty('fanart_image',cover)
		purl = sys.argv[0] + '?mode=OpenPage'\
			+ '&url=' + urllib.quote_plus(row_url)\
			+ '&fanart_image=' + urllib.quote_plus(cover)\
			+ '&num=' + urllib.quote_plus(str(Lnum[i]))\
			+ '&lgl=' + urllib.quote_plus(repr(lgl))\
			+ '&title=' + urllib.quote_plus(Ltitle[i])\
			+ '&info=' + urllib.quote_plus(repr(dict))
		xbmcplugin.addDirectoryItem(handle, purl, listitem, False)



#xplayer=xbmc.Player(xbmc.PLAYER_CORE_AUTO)
#if os.path.isdir("d:\\TorrentStream")==1: TSpath="d:\\TorrentStream\\"
#elif os.path.isdir("c:\\TorrentStream")==1: TSpath="c:\\TorrentStream\\"
#elif os.path.isdir("e:\\TorrentStream")==1: TSpath="e:\\TorrentStream\\"
#elif os.path.isdir("f:\\TorrentStream")==1: TSpath="f:\\TorrentStream\\"
#elif os.path.isdir("g:\\TorrentStream")==1: TSpath="g:\\TorrentStream\\"
#elif os.path.isdir("h:\\TorrentStream")==1: TSpath="h:\\TorrentStream\\"
#else: TSpath="C:\\"
	
	
def OpenPage(url, name, num, Lgl, dict):
	Ltitle, Lurl, Lnum = Lgl
	playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	playlist.clear()
	try:thumb2=dict["cover"]
	except:thumb2=""
	for i in range(num,len(Lnum)):
		item = xbmcgui.ListItem(Ltitle[i], iconImage = thumb2, thumbnailImage = thumb2)
		item.setInfo(type="Video", infoLabels=dict)
		playlist.add(url=Lurl[i], listitem=item, index=-1)
	xplayer.play(playlist)
	showMessage('RuTor:', "Соединение...", 100)
	time.sleep(0.3)
	
	for i in range(0,num):
		item = xbmcgui.ListItem(Ltitle[i], iconImage = thumb2, thumbnailImage = thumb2)
		item.setInfo(type="Video", infoLabels=dict)
		playlist.add(url=Lurl[i], listitem=item, index=-1)
	p = xplayer.isPlayingVideo()
	ttl=0
	bsz=0
	while xplayer.isPlayingVideo() == 0 and ttl<20 :
	#for i in range(0,30):
		p = xplayer.isPlayingVideo()
		d = os.path.isfile(TSpath+name)
		
		if d==0:
			showMessage('RuTor:', "[COLOR FFFFF000]Поиск пиров...[/COLOR]", 100)
			ttl+=1
		elif p==0:
			sz=os.path.getsize(TSpath+name)
			pbr="I"*int(sz/(1048576*1.5))
			showMessage("[COLOR FF00FF00]Буферизация: "+str(int(sz/1048576))+" Mb[/COLOR]", "[COLOR FF00FFFF]"+pbr[:51]+"[/COLOR]",100)
			if bsz==sz: ttl+=1
			else: ttl=0
			bsz=sz
		elif p==1:
			return 0
		time.sleep(1)
		


params = get_params()
mode     = None
url      = '0'
title    = ''
ref      = ''
img      = ''
num      = 0
category = '0'
sort     = '2'
text     = '0'
Lgl      = ()
info  = {}
move_info_db={}
AL=[]

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
try:
	num  = int(urllib.unquote_plus(params["num"]))
except:
	pass
	
try:
	category  = urllib.unquote_plus(params["category"])
except:
	pass
	
try:
	AL  = eval(urllib.unquote_plus(params["category"]))
except:
	pass
	
try:
	sort  = urllib.unquote_plus(params["sort"])
except:
	pass

try:
	text  = urllib.unquote_plus(params["text"])
except:
	pass

try:
	Lgl  = eval(urllib.unquote_plus(params["lgl"]))
except:
	pass

try:
	info  = eval(urllib.unquote_plus(params["info"]))
except:
	pass



#try:
if  mode == "OpenRel":#mode == None or
		post = urllib.urlencode(values)
		html = get_HTML(url1, post, 'http://www.lostfilm.tv/')
		soup = BeautifulSoup(html, fromEncoding="utf-8")
		#-- step 2url=url.replace('www.lostfilm.tv','www.lostfilm.tv.3s3s.org')
		ref = url1
		url1 = soup.find('form')['action']
		values={}
		for rec in soup.findAll('input'):
			try:
				values[rec['name'].encode('utf-8')] = rec['value'].encode('utf-8')
			except:
				print "err: value"
		post = urllib.urlencode(values)
		html = get_HTML(url1, post, ref)
#except:'https:'+
#		print 'lostfilm: Ошибка доступа'
		#showMessage('lostfilm', "Ошибка доступа", times = 50000)




if mode == None or mode == "None":
	#LF()
	GET_N()
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle)
	
elif mode == 'OpenLF':
	
	LF()
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle)

elif mode == 'KFS':
	#print text
	stft(text)
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle)

elif mode == 'OpenCat':
	Engine = __settings__.getSetting("Engine")
	if Engine=="0":
		try:img=info["cover"]
		except: img=icon
		play_url({'file':url,'img':img})
		xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
		xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_LABEL)
		xbmcplugin.endOfDirectory(handle)
	elif Engine=="1":
		DownloadDirectory = __settings__.getSetting("DownloadDirectory")
		if DownloadDirectory=="":DownloadDirectory=LstDir
		playTorrent(url, DownloadDirectory)

elif mode == 'OpenPage':
	GET_C(url)
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_LABEL)
	xbmcplugin.endOfDirectory(handle)

elif mode == 'OpenRel':
	GET_R(url)
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_LABEL)
	xbmcplugin.endOfDirectory(handle)
	
elif mode == 'play_url2':
		play_url2(params)


c.close()