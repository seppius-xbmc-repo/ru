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

icon = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''), 'icon.png'))
siteUrl = 'www.rutor.org'
httpSiteUrl = 'http://' + siteUrl
sid_file = os.path.join(xbmc.translatePath('special://temp/'), 'plugin.video.RuTor.cookies.sid')

h = int(sys.argv[1])

handle = int(sys.argv[1])

PLUGIN_NAME   = 'RuTor'

addon = xbmcaddon.Addon(id='plugin.video.RuTor')
__settings__ = xbmcaddon.Addon(id='plugin.video.RuTor')
xbmcplugin.setContent(int(sys.argv[1]), 'movies')


#---------tsengine----by-nuismons-----

from TSCore import TSengine as tsengine
prt_file= __settings__.getSetting('port_path')
aceport=62062
try:
	if prt_file: 
		gf = open(prt_file, 'r')
		aceport=int(gf.read())
		gf.close()
except: prt_file=None

if not prt_file:
	try:
		fpath= os.path.expanduser("~")
		pfile= os.path.join(fpath,'AppData\Roaming\TorrentStream\engine' ,'acestream.port')
		gf = open(pfile, 'r')
		aceport=int(gf.read())
		gf.close()
		__settings__.setSetting('port_path',pfile)
		print aceport
	except: aceport=62062



def play_url(params):
	torr_link=params['file']
	img=urllib.unquote_plus(params["img"])
	#showMessage('heading', torr_link, 10000)
	TSplayer=tsengine()
	out=TSplayer.load_torrent(torr_link,'TORRENT',port=aceport)
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
			xbmcplugin.addDirectoryItem(handle, uri, li, False)
	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_LABEL)
	xbmcplugin.endOfDirectory(handle)
	TSplayer.end()
	
def play_url2(params):
	#torr_link=params['torr_url']
	torr_link=urllib.unquote_plus(params["torr_url"])
	img=urllib.unquote_plus(params["img"])
	title=urllib.unquote_plus(params["title"])
	#showMessage('heading', torr_link, 10000)
	TSplayer=tsengine()
	out=TSplayer.load_torrent(torr_link,'TORRENT',port=aceport)
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
		self.bgread = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''), 'resources', 'img', 'background.png'))
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


def showtext(text):
	TextReader(txt_data = text).doModal()


def GET_old(target, referer, post_params = None, accept_redirect = True, get_redirect_url = False):
	try:
		connection = httplib.HTTPConnection(siteUrl)

		if post_params == None:
			method = 'GET'
			post = None
		else:
			method = 'POST'
			post = urllib.urlencode(post_params)
			headers['Content-Type'] = 'application/x-www-form-urlencoded'

		if os.path.isfile(sid_file):
			fh = open(sid_file, 'r')
			csid = fh.read()
			fh.close()
			headers['Cookie'] = 'session=%s' % csid

		headers['Referer'] = referer
		connection.request(method, target, post, headers = headers)
		response = connection.getresponse()

		if response.status == 403:
			raise Exception("Forbidden, check credentials")
		if response.status == 404:
			raise Exception("File not found")
		if accept_redirect and response.status in (301, 302):
			target = response.getheader('location', '')
			if target.find("://") < 0:
				target = httpSiteUrl + target
			if get_redirect_url:
				return target
			else:
				return GET(target, referer, post_params, False)

		try:
			sc = Cookie.SimpleCookie()
			sc.load(response.msg.getheader('Set-Cookie'))
			fh = open(sid_file, 'w')
			fh.write(sc['session'].value)
			fh.close()
		except: pass

		if get_redirect_url:
			return False
		else:
			http = response.read()
			return http

	except Exception, e:
		showMessage('Error', e, 5000)
		return None


def GET(target, referer, post=None):
	#print target
	try:
		req = urllib2.Request(url = target, data = post)
		req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
		resp = urllib2.urlopen(req)
		http = resp.read()
		resp.close()
		return http
	except Exception, e:
		showMessage('HTTP ERROR', e, 5000)


def ru(x):return unicode(x,'utf8', 'ignore')
def xt(x):return xbmc.translatePath(x)


dc={"1 канал" : "001", "1+1" : "002"}
#try:
#	from canal_list import*
#except:
#	pass

thumb = os.path.join( addon.getAddonInfo('path'), "icon.png" )
fanart = os.path.join( addon.getAddonInfo('path'), "fanart.jpg" )
LstDir = os.path.join( addon.getAddonInfo('path'), "playlists" )
dbDir = os.path.join( addon.getAddonInfo('path'), "db" )
ImgPath = os.path.join( addon.getAddonInfo('path'), "logo" )
playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)

#siteUrl = '109.95.47.77/BP-TV.m3u'
#httpSiteUrl = 'http://' + siteUrl
#httpSiteUrl = 'http://opensharing.org/download/43651'
#httpSiteUrl ='http://d.rutor.org/download/175775'

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



def GET2(url):
	try:
		urllib.urlretrieve(url,os.path.join(LstDir, "move4.torrent"))
		#print 'def GET(%s):'%url
		req = urllib2.Request(url)
		f = urllib2.urlopen(req)
		a = f.read()
		f.close()
		return a
	except:
		showMessage('Не могу открыть URL def GET', url)
		return None

def cleartext(str):
	str=str.replace('</td><td ><a class="downgif" href="',"', '")
	str=str.replace('"><img src="http://s.rutor.org/i/d.gif" alt="D" /></a><a href="magnet:?xt=',"', '")
	str=str.replace('alt="M" /></a><a href="/torrent/',"', '")
	str=str.replace('</a></td> <td align="right">',"', '")
	str=str.replace('<img src="http://s.rutor.org/i/com.gif" alt="C" /></td><td align="right">',"', '")
	str=str.replace('</td><td align="center"><span class="green"><img src="http://s.rutor.org/t/arrowup.gif" alt="S" />',"', '")
	str=str.replace('</span><img src="http://s.rutor.org/t/arrowdown.gif" alt="L" /><span class="red">',"', '")
	str=str.replace('">',"', '")
	str=str.replace('</span></td></tr>',"']")
	str=str.replace('</span>',"']")
	str=str.replace("</table>", "\r")
	return str

def formtext(http):
	http=http.replace(chr(10),"")#.replace(chr(13),"")
	
	http=http.replace('&#039;',"").replace('colspan = "2"',"").replace('&nbsp;',"") #исключить
	http=http.replace('</td></tr><tr class="gai"><td>',"\rflag1 ['") 
	http=http.replace('</td></tr><tr class="gai">',"\rflag1 ") #начало
	#http=http.replace('/></a>\r<a href',' *** ').replace('alt="C" /></td>\r<td align="right"',' *** ') #склеить
	http=http.replace('<tr class="tum"><td>',"\rflag1 ['").replace('<tr class="gai"><td>',"\rflag1 ['") #разделить
	http=cleartext(http)
	return http
	#fl = open(os.path.join( ru(LstDir),"test.txt"), "w")
	#fl.write(http)
	#fl.close()

def inputbox():
	skbd = xbmc.Keyboard()
	skbd.setHeading('Поиск:')
	skbd.doModal()
	if skbd.isConfirmed():
		SearchStr = skbd.getText()
		return SearchStr
	else:
		return ""

def upd(category, sort, text, n):
	try: n=str(int(n))
	except: n="0"
	if text=='0':stext=""
	elif text=='1':stext=inputbox()
	elif text<>'':stext=text
	stext=stext.replace("%", "%20").replace(" ", "%20").replace("?", "%20").replace("#", "%20")
	if stext=="":
		categoryUrl = xt('http://www.rutor.org/browse/'+n+'/'+category+'/0/'+sort)
	else:
		if text=='1':categoryUrl = 'http://www.rutor.org/search/'+n+'/'+category+'/000/'+sort+'/'+stext   #)xt( 0/1/110/0
		else: categoryUrl = 'http://www.rutor.org/search/'+n+'/'+category+'/110/'+sort+'/'+stext
	http = GET(categoryUrl, httpSiteUrl, None)
	if http == None:
		showMessage('RuTor:', 'Сервер не отвечает', 1000)
		return None
	else:
		http=formtext(http)
		LL=http.splitlines()
		return LL

def format(L):
	if L==None: 
		return ["","","","","","","","",""]
	else:
		Ln=[]
		i=0
		for itm in L:
			i+=1
			if len(itm)>6:
				if itm[:5]=="flag1": 
					try:Ln.append(eval(itm[6:]))
					except: pass
		return Ln


ru_film='5'
en_film='1'
nauka='12'
serial='4'
tv_video='6'
mult='7'
anime='10'
all_cat='0'

sort_data='0'
sort_sid='2'
sort_name='6'

tab="[COLOR 00000000]_[/COLOR]"

L=['1','2','3','4']
def ShowRoot2(AL, text):
		if text in AL:
				AL.remove(text)
		else: 
				AL.append(text)
		for i in L:
			#Title = i
				
			if i in AL:
				Title = '[_] '+i
			else: 
				Title = '[\/] '+i

			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Root'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus(repr(AL))\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus(i)
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)
			

#http://rutor.org/search/0/12/000/2/ -- Науч поп
#http://rutor.org/search/0/5/000/2/ -- ru
#http://rutor.org/search/0/1/000/2/ -- en
#http://rutor.org/search/0/4/000/2/ -- serial
#http://rutor.org/search/0/6/000/2/ -- tv
#http://rutor.org/search/0/7/000/2/ -- mult
#http://rutor.org/search/0/10/000/2/ -- anime
#http://rutor.org/search/0/0/000/2/ -- all

SLk1=["0","1","5","4","7","10","12","6"]
SLk2=["Все","Зарубежные фильмы","Русские фильмы","Сериалы","Мультфильмы","Аниме","Научно-популярное","ТВ"]
SLg=["Все","Арт-хаус","Биография","Боевик","Вестерн","Военный","Детектив","Детский","Драма","Исторический","Комедия","Короткометражка","Криминал","Мелодрама","Мистика","Мюзикл","Нуар","Пародия ","Приключения","Романтика","Семейный","Сказка","Спорт","Триллер","Ужасы","Фантастика","Фэнтези","Советское кино","СССР","Союзмультфильм","Disney","вампиры","война","детектив","история","киберпанк","меха","мистерия","музыкальный","паропанк","повседневность","полиция","постапокалиптика","психология","романтика","Эротика"]
SLy=["Все","2014", "2013", "2012", "2011", "2010", "2009", "2008", "2007", "2006", "2005", "2004", "2003", "2002", "2001", "2000", "1999", "1998", "1997", "1996", "1995", "1994", "1993", "1992", "1991", "1990", "1989", "1988", "1987", "1986", "1985", "1984", "1983", "1982", "1981", "1980", "1979", "1978", "1977", "1976", "1975", "1974", "1973", "1972", "1971", "1970", "1969", "1968", "1967", "1966", "1965", "1964", "1963", "1962", "1961", "1960", "1959", "1958", "1957", "1956", "1955", "1954", "1953", "1952", "1951", "1950", "1949", "1948", "1947", "1946", "1945", "1944", "1943", "1942", "1941", "1940", "1939", "1938", "1937", "1936", "1935", "1934", "1933", "1932", "1931", "1930"]
SLq=["Все","Blu-ray","BDRemux","BDRip","HDRip","WEB-DL","WEB-DLRip","HDTV","HDTVRip","DVD9","DVD5","DVDRip","DVDScr","DVB","SATRip","IPTVRip","TVRip","VHSRip","TS","CAMRip","720p","1080i"]

try:
	from akter import*
except:
	pass



def ShowA(spr,category):
	for Ki in SLa:
			Title = Ki
			row_url = Ki
			if Ki=="Все": Ki=""
			spr[5]=Ki
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Params'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus(category)\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus(repr(spr))
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

def ShowK(spr):
	i=-1
	for Ki in SLk2:
			i+=1
			Title = Ki
			row_url = SLk1[i]
			spr[0]=Ki
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Params'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus(row_url)\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus(repr(spr))
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

def ShowG(spr,category):
	for Ki in SLg:
			Title = Ki
			row_url = Ki
			if Ki=="Все": Ki=""
			spr[1]=Ki
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Params'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus(category)\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus(repr(spr))
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

def ShowY(spr,category):
	for Ki in SLy:
			Title = Ki
			row_url = Ki
			if Ki=="Все": Ki=""
			spr[2]=Ki
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Params'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus(category)\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus(repr(spr))
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

def ShowQ(spr,category):
	for Ki in SLq:
			Title = Ki
			row_url = Ki
			if Ki=="Все": Ki=""
			spr[3]=Ki
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Params'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus(category)\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus(repr(spr))
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)



def ShowPr(spr,category):

			sK="Все"
			sG="Все"
			sY="Все"
			sQ="Все"
			sT="Все"
			sA="Все"
			if spr[4]<>"": sT=spr[4]
			if spr[1]<>"": sG=spr[1]
			if spr[2]<>"": sY=spr[2]
			if spr[3]<>"": sQ=spr[3]
			if spr[5]<>"": sA=spr[5]
			
			Title = "[B][COLOR FFFFFF00][ПОПУЛЯРНЫЕ][/COLOR][/B]"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Root2'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus(category)\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus(repr(spr))
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)
			
			Title = "[B][COLOR FFFFFF00][НОВИНКИ][/COLOR][/B]"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=New'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus(category)\
				+ '&sort=' + urllib.quote_plus(sort_data)\
				+ '&text=' + urllib.quote_plus(repr(spr))
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)
			
			Title = "_______________________________________________________"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Root99'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus(category)\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus(repr(spr))
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)
			
			Title = "Категория: "+tab*2+spr[0]
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )#ParamK'
			purl = sys.argv[0] + '?mode=ParamK'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus(category)\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus(repr(spr))
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

			Title = "Жанр: "+tab*7+sG
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=ParamG'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus(category)\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus(repr(spr))
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

			Title = "Год: "+tab*9+sY
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=ParamY'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus(category)\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus(repr(spr))
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

			Title = "Качество:  "+tab*3+sQ
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=ParamQ'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus(category)\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus(repr(spr))
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

			Title = "Актер: "+tab*7+sA
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=ParamA'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus(category)\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus(repr(spr))
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)


			Title = "Название: "+tab*3+sT
			row_url = url
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=ParamT'\
				+ '&url=' + urllib.quote_plus('0')\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus(category)\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus(repr(spr))
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)
			

			Title = "[B][COLOR FF00FF00][ НАЙТИ ][/COLOR][/B]"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=SearchN'\
				+ '&url=' + urllib.quote_plus(repr(spr))\
				+ '&title=' + urllib.quote_plus(repr(spr))\
				+ '&category=' + urllib.quote_plus(category)\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus(spr[4]+" "+spr[1]+" "+spr[2]+" "+spr[3]+" "+spr[5])
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)
			
			


def ShowRoot():
#			Title = "[Категории]"
#			row_url = Title
#			listitem = xbmcgui.ListItem(Title)
#			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
#			purl = sys.argv[0] + '?mode=Params'\
#				+ '&url=' + urllib.quote_plus(row_url)\
#				+ '&title=' + urllib.quote_plus(Title)\
#				+ '&category=' + urllib.quote_plus(all_cat)\
#				+ '&sort=' + urllib.quote_plus(sort_sid)\
#				+ '&text=' + urllib.quote_plus('0')
#			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)
#			
#			Title = "[Все]"
#			row_url = Title
#			listitem = xbmcgui.ListItem(Title)
#			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
#			purl = sys.argv[0] + '?mode=Search'\
#				+ '&url=' + urllib.quote_plus(row_url)\
#				+ '&title=' + urllib.quote_plus(Title)\
#				+ '&category=' + urllib.quote_plus(all_cat)\
#				+ '&sort=' + urllib.quote_plus(sort_sid)\
#				+ '&text=' + urllib.quote_plus('0')
#			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

			Title = "[Иностранные фильмы]"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Search'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus(en_film)\
				+ '&sort=' + urllib.quote_plus('2')\
				+ '&text=' + urllib.quote_plus('0')
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

			Title = "[Русские фильмы]"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Search'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus(ru_film)\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus('0')
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

			Title = "[Сериалы]"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Search'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus(serial)\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus('0')
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

			Title = "[Мультфильмы]"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Search'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus(mult)\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus('0')
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

			Title = "[Аниме]"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Search'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus(anime)\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus('0')
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

			Title = "[Научно-Популярное]"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Search'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus(nauka)\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus('0')
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

			Title = "[Телепередачи]"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Search'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus(tv_video)\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus('0')
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)


def ShowNew():
			Title = "[Иностранные фильмы]"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Search'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus(en_film)\
				+ '&sort=' + urllib.quote_plus(sort_data)\
				+ '&text=' + urllib.quote_plus('0')
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

			Title = "[Русские фильмы]"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Search'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus(ru_film)\
				+ '&sort=' + urllib.quote_plus(sort_data)\
				+ '&text=' + urllib.quote_plus('0')
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

			Title = "[Сериалы]"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Search'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus(serial)\
				+ '&sort=' + urllib.quote_plus(sort_data)\
				+ '&text=' + urllib.quote_plus('0')
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

			Title = "[Мультфильмы]"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Search'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus(mult)\
				+ '&sort=' + urllib.quote_plus(sort_data)\
				+ '&text=' + urllib.quote_plus('0')
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

			Title = "[Аниме]"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Search'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus(anime)\
				+ '&sort=' + urllib.quote_plus(sort_data)\
				+ '&text=' + urllib.quote_plus('0')
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

			Title = "[Научно-Популярное]"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Search'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus(nauka)\
				+ '&sort=' + urllib.quote_plus(sort_data)\
				+ '&text=' + urllib.quote_plus('0')
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

			Title = "[Телепередачи]"
			row_url = Title
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Search'\
				+ '&url=' + urllib.quote_plus(row_url)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus(tv_video)\
				+ '&sort=' + urllib.quote_plus(sort_data)\
				+ '&text=' + urllib.quote_plus('0')
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)




#---- по сидам ----
#http://rutor.org/search/0/12/000/2/ -- Науч поп
#http://rutor.org/search/0/5/000/2/ -- ru
#http://rutor.org/search/0/1/000/2/ -- en
#http://rutor.org/search/0/4/000/2/ -- serial
#http://rutor.org/search/0/6/000/2/ -- tv
#http://rutor.org/search/0/7/000/2/ -- mult
#http://rutor.org/search/0/10/000/2/ -- anime
#http://rutor.org/search/0/0/000/2/ -- all

#------- по дате
#http://rutor.org/search/0/0/000/0/

#---- по сидам ---- 2  cn 0
#http://rutor.org/browse/0/0/0/2 - 1 str all
#http://rutor.org/browse/0/1/0/2 - en
#http://rutor.org/browse/0/4/0/2 - serial
#
#---- по дате ---
#http://rutor.org/browse/0/4/0/0 - serial

#abc
#http://rutor.org/browse/0/4/0/6
#
p = re.compile(r'<.*?>')
#p.sub('', html)

def clearinfo2(str):
	str=str.replace(chr(13)+chr(10),chr(10))
	str=str.replace(chr(10)+chr(13),chr(10))
	
	str=str.replace('<b>',"").replace('</b>',"")
	str=str.replace('<i>',"").replace('</i>',"")
	str=str.replace('<u>',"").replace('</u>',"")
	str=str.replace('<tr>',"").replace('</tr>',"")
	str=str.replace('<td>',"").replace('</td>',"")
	str=str.replace('<table>',"").replace('</table>',"")
	str=str.replace('<a',"").replace('</a>',"")
	str=str.replace('<br />',"")
	str=str.replace('<hr />',"")
	str=str.replace('<li> ',"")
	str=str.replace('</span>',"")
	str=str.replace('<font size="3">',"").replace('</font>',"")
	str=str.replace('<font size="4">',"")
	str=str.replace('<font size="5">',"")
	
	str=str.replace('<span style="color:chocolate;">',"")
	str=str.replace('<span style="color:green;">',"")
	str=str.replace('<span style="color:indigo;">',"")
	str=str.replace('<span style="color:blue;">',"")
	str=str.replace('<span style="color:maroon;">',"")
	str=str.replace('<span style="color:brown;">',"")
	str=str.replace('<span style="color:darkgreen;">',"")
	
	str=str.replace("<td class='header'>","")
	
	#str=str.replace('<img src="',chr(10)+'Обложка: "')
	#str=str.replace('<td style="vertical-align:top;"><img src="', 'Обложка: "')
	str=str.replace(' style="float:right;" />',"")
	str=str.replace('" />','"')
	
	str=str.replace('О фильме:'+chr(10), chr(10)+'О фильме: ')
	str=str.replace('О фильме: '+chr(10), chr(10)+'О фильме: ')
	str=str.replace('О фильме:  '+chr(10), chr(10)+'О фильме: ')
	str=str.replace('О фильме:   '+chr(10), chr(10)+'О фильме: ')
	
	str=str.replace('<div class="hidewrap"><div class="hidehead" onclick="hideshow($(this))">',"")
	str=str.replace('</div><div class="hidebody"></div><textarea class="hidearea"> href="',': ["')
	str=str.replace('<td class="header">',"")
	str=str.replace(' /></textarea></div>',"]")
	str=str.replace('</textarea></div>',"]")
	str=str.replace(' target="_blank"><img src=',",")
	str=str.replace('"'+chr(10)+'<img src="', "','")
	str=str.replace(' />  href=',",")
	str=str.replace('"  href="',",")
	str=str.replace('href="/tag/7/" target="_blank">',"")
	str=str.replace('href="/tag/6/" target="_blank">',"")
	str=str.replace('href="/tag/5/" target="_blank">',"")
	str=str.replace('href="/tag/4/" target="_blank">',"")
	str=str.replace('href="/tag/3/" target="_blank">',"")
	str=str.replace('href="/tag/2/" target="_blank">',"")
	str=str.replace('href="/tag/1/" target="_blank">',"")
	
	str=str.replace('О фильме:',chr(10)+"О фильме:")
	str=str.replace('Год выхода:',chr(10)+"Год выхода:")
	str=str.replace('Описание:',chr(10)+"Описание:")
	str=str.replace('Название:',chr(10)+"Название:")
	str=str.replace('Жанр:',chr(10)+"Жанр:")
	str=str.replace('Режиссер:',chr(10)+"Режиссер:")
	#n=str.find("http://mediaget.com/torrent")
	n=str.find('<table id="details">')
	k=str.rfind("Сидер замечен")
	str=str[n:k]
	try:
		i=str.find('Информация о фильме')
		j=str.find('.jpg')
		k=str.find('.png')
		if i>0: 
			tmp=str[:i]
			i2=tmp.rfind('.')+4
			i1=tmp.rfind('http:')
			tmp=tmp[i1:i2]
			ext=tmp[-3:]
			if ext=="jpe":tmp=tmp+"g"
			str=str.replace('Информация о фильме', chr(10)+'Обложка: "'+tmp+'"')
		elif j>0:
			tmp=str[:j+4]
			i1=tmp.rfind('http:')
			tmp=tmp[i1:]
			str=chr(10)+'Обложка: "'+tmp+'"'+chr(10)+str
		elif k>0:
			tmp=str[:k+4]
			i1=tmp.rfind('http:')
			tmp=tmp[i1:]
			str=chr(10)+'Обложка: "'+tmp+'"'+chr(10)+str
		else:
			str=str.replace('<img src="', chr(10)+'Обложка: "',1)
	except:
		str=str.replace('<img src="', chr(10)+'Обложка: "',1)
	str=p.sub('', str)
	return str


def clearinfo(str):
	n=str.find('<table id="details">')
	k=str.rfind("Сидер замечен")
	str=str[n:k]
	str=str.replace(chr(13)+chr(10),chr(10))
	str=str.replace(chr(10)+chr(13),chr(10))
	str=str.replace(chr(13),chr(10))
	
	str=str.replace('http://changecopyright.ru/bannersout/banner-468x60.png',"")
	str=str.replace('http://hq-video.org/images/1080-r.png',"")
	str=str.replace('http://hq-video.org/images/720-r.png',"")
	
	str=str.replace('Год выхода:',chr(10)+"Год выхода:")
	str=str.replace('Год выпуска',chr(10)+"Год выхода:")
	str=str.replace('Описание:',chr(10)+"Описание:")
	str=str.replace('Краткое описание:',chr(10)+"Описание:")
	str=str.replace('О фильме:',chr(10)+"Описание:")
	str=str.replace('Название:',chr(10)+"Название:")
	str=str.replace('Жанр:',chr(10)+"Жанр:")
	str=str.replace('Режиссер:',chr(10)+"Режиссер:")

	try:
		i=str.find('Информация о фильме')
		if i<0:
			m=str.find('Год выхода')
			if m>0:
				s=str[:m]
				j=s.find('.jpg')
				k=s.find('.png')
				n=s.find('jpeg')
			else:
				j=str.find('.jpg')
				k=str.find('.png')
				n=str.find('jpeg')
		if i>0:
			tmp=str[:i]
			i2=tmp.rfind('.')+4
			i1=tmp.rfind('http:')
			tmp=tmp[i1:i2]
			ext=tmp[-3:]
			if ext=="jpe":tmp=tmp+"g"
			str=str.replace('Информация о фильме', chr(10)+'Обложка: '+tmp+chr(10))
		elif j>0:
			tmp=str[:j+4]
			i1=tmp.rfind('http:')
			tmp=tmp[i1:]
			str=chr(10)+'Обложка: '+tmp+chr(10)+str
		elif k>0:
			tmp=str[:k+4]
			i1=tmp.rfind('http:')
			tmp=tmp[i1:]
			str=chr(10)+'Обложка: '+tmp+chr(10)+str
		elif n>0:
			tmp=str[:n+4]
			i1=tmp.rfind('http:')
			tmp=tmp[i1:]
			str=chr(10)+'Обложка: '+tmp+chr(10)+str
		else:
			str=str.replace('<img src="', chr(10)+'Обложка: ',1)
	except:
		str=str.replace('<img src="', chr(10)+'Обложка: ',1)

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
	return str




#move_info_db={}
#try:
#	if move_info_db=={}: from moveinfo_db import*
#except:pass

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


def debug(s):
	fl = open(os.path.join( ru(LstDir),"test.txt"), "w")
	fl.write(s)
	fl.close()

def get_qual(ntor):
	hp = GET('http://www.rutor.org/torrent/'+ntor, httpSiteUrl, None)
	n=hp.find('>Связанные раздачи<')
	k=hp.find('>Искать ещё похожие раздачи<')
	hp=hp[n:k]
	hp=hp.replace('"',"'")
	hp=hp.replace("class='gai'><td>",'\nflag1:"')
	hp=hp.replace("class='tum'><td>",'\nflag1:"')
	hp=hp.replace("</td><td ><a class='downgif' href='",'","')
	hp=hp.replace("'><img src='http://s.rutor.org/i/d.gif' alt='D'",'","')
	hp=hp.replace("'><img src='http://s.rutor.org/i/m.png' alt='M'",'')
	hp=hp.replace("</a></td> <td align='right'>",'","')
	hp=hp.replace("<img src='http://s.rutor.org/i/com.gif' alt='C' /></td>\n<td align='right'>",'","')
	hp=hp.replace("</td><td align='center'><span class='green'><img src='http://s.rutor.org/t/arrowup.gif' alt='S' />&nbsp;",'","')
	hp=hp.replace("</span>&nbsp;<img src='http://s.rutor.org/t/arrowdown.gif' alt='L' /><span class='red'>&nbsp;",'","')
	hp=hp.replace('</span></td>','"\n')
	hp=hp.replace("'>",'","')
	hp=hp.replace('&nbsp;',' ')
	hp=hp.replace("\n<a href='/torrent/",'","')
	LI=hp.splitlines()
	L=[]
	for itm in LI:
		nc=itm.find(':')
		flag=itm[:nc]
		if flag=='flag1': 
				cvr=itm.strip()
				try:L.append(eval("["+itm[nc+1:].strip()+"]"))
				except: pass
				
	#debug(str(L))
	return L
	

def get_minfo(ntor):
			
			try: dict=eval(xt(get_inf_db(ntor)[0][0]))#dbi = move_info_db[ntor]
			except: #dbi = None
			
			#if dbi == None:
				hp = GET('http://www.rutor.org/torrent/'+ntor, httpSiteUrl, None)
				hp=clearinfo(hp)
				LI=hp.splitlines()
				dict={}
				cover=''
				for itm in LI:
					nc=itm.find(':')
					flag=itm[:nc]
					if flag=='Обложка': 
						cvr=itm.strip()
						dict['cover']=itm[nc+1:].strip()
					elif flag=='Название': dict['title']=itm[nc+1:].strip()
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
					elif flag=='Жанр': dict['genre']=itm[nc+1:].strip()
					elif flag=='Режиссер': dict['director']=itm[nc+1:].strip()
					elif flag=='В ролях': 
						dict['cast']=itm[nc+1:].split(",")[:6]
					elif flag=='О фильме' or flag=='Описание': 
						dict['plot']=ru(formating(itm[nc+1:].strip())[:1000])
						
				#move_info_db[ntor]=dict
				try:add_to_db(ntor, repr(dict))
				except:
					try:add_to_db(ntor, repr(dict).replace('"',"'"))
					except: pass

				if 1==0:
					
					fl = open(os.path.join( ru(dbDir), ntor+".py"), "w")
					fl.write('move_info_db['+ntor+']='+str(dict))
					fl.close()
				
			#else:
				#dict=move_info_db[ntor]
			#print eval(get_inf_db(ntor)[0][0])
			return dict


def SearchN(category, sort, text, filtr, url='0'):
	if text=="   ": text="0"
	if text=="    ": text="0"
	#url='0'
	HideScr = __settings__.getSetting("Hide Scr")
	HideTSnd = __settings__.getSetting("Hide TSound")
	TitleMode = __settings__.getSetting("Title Mode")
	EnabledFiltr = __settings__.getSetting("EnabledFiltr")
	Filtr = __settings__.getSetting("Filtr")
	
	RL=upd(category, sort, text, url)
	RootList=format(RL)
	k=0
	TLD=[]
	defekt=0
	for tTitle in RootList:
		if len(tTitle)==9:
			tTitle.insert(6," ")
		
		if len(tTitle)==10 and int(tTitle[8])>0:
			
			size=tTitle[7]
			if size[-2:]=="MB":size=size[:-5]+"MB"
			
			if len(size)==3:size=size.center(10)
			elif len(size)==4:size=size.center(9)
			elif len(size)==5:size=size.center(8)
			elif len(size)==6:size=size.center(8)
			
			if len(tTitle[8])==1:sids=tTitle[8].center(9)
			elif len(tTitle[8])==2:sids=tTitle[8].center(8)
			elif len(tTitle[8])==3:sids=tTitle[8].center(7)
			elif len(tTitle[8])==4:sids=tTitle[8].center(6)
			else:sids=tTitle[8]
			
			#------------------------------------------------
			k+=1
			nnn=tTitle[1].rfind("/")+1
			ntor=xt(tTitle[1][nnn:])
			if k<115:
				#   nnn=tTitle[1].rfind("/")+1
				#   ntor=xt(tTitle[1][nnn:])
				#dict=get_minfo(ntor)
				#try:dict=get_minfo(ntor)
				#except:dict={}
				#try:cover=dict["cover"]
				#except:cover=""
				pass
			#-------------------------------------------------
			
			#Title = "|"+sids+"|"+size+"|  "+tTitle[5]
			Title = "|"+sids+"|  "+tTitle[5]
			
			flt4=0
			flt2=0
			flt3=0
			ltl=rulower(Title)
			if filtr[4]=="" or ltl.find(rulower(filtr[4]))>0: flt4=1
			if filtr[2]=="" or tTitle[5].find(filtr[2].replace("1990","199").replace("1980","198").replace("1970","197").replace("1960","196").replace("1950","195").replace("1940","194").replace("1930","193"))>0: flt2=1
			if filtr[3]=="" or Title.find(filtr[3])>0: flt3=1
			Sflt=flt4+flt2+flt3
			

			if HideScr == 'true':
				nH1=Title.find("CAMRip")
				nH2=Title.find(") TS")
				nH3=Title.find("CamRip")
				nH4=Title.find(" DVDScr")
				nH=nH1+nH2+nH3+nH4
			else:
				nH=-1
				
			if HideTSnd == 'true':
				sH=Title.find("Звук с TS")
			else:
				sH=-1
				
			if TitleMode == '1': 
				k1=Title.find('/')
				if k1<0: k1=Title.find('(')
				tmp1=Title[:k1]
				n1=Title.find('(')
				k2=Title.find(' от ')
				if k2<0: k2=None
				tmp2=Title[n1:k2]
				Title = tmp1+tmp2
				Title = Title.replace("| Лицензия","")
				Title = Title.replace("| лицензия","")
				Title = Title.replace("| ЛицензиЯ","")
			
			
			tTitle5=ru(tTitle[5].strip().replace("ё","е"))
			nc=tTitle5.find(") ")
			nc2=tTitle5.find("/ ")
			if nc2<nc and nc2 >0: nc=nc2
			CT=rulower(tTitle5[:nc]).strip()
			#Title=CT
			if Sflt==3 and nH<0 and sH<0 and (CT not in TLD):
				
				dict=get_minfo(ntor)
				try:dict=get_minfo(ntor)
				except:dict={}
				try:cover=dict["cover"]
				except:cover=""
				dict['ntor']=ntor
				UF=0
				if EnabledFiltr == 'true' and Filtr<>"":
					Fnu=Filtr.replace(",",'","')
					Fnu=Fnu.replace('" ','"')
					F1=eval('["'+Fnu+'", "4565646dsfs546546"]')
					Tlo=rulower(Title)
					try:Glo=rulower(dict['genre'])
					except: Glo="45664sdgd6546546"
					for Fi in F1:
						if Tlo.find(rulower(Fi))>=0:UF+=1
						if Glo.find(rulower(Fi))>=0:UF+=1
				Tresh=["Repack"," PC ","XBOX","RePack","FB2","TXT","DOC"," MP3"," JPG"," PNG"," SCR"]
				for TRi in Tresh:
					if tTitle[5].find(TRi)>=0:UF+=1
				
				if UF==0:
					TLD.append(CT)
					row_url = tTitle[1]
					Title=Title.replace("&quot;",'"')
					
					listitem = xbmcgui.ListItem(Title, thumbnailImage=cover, iconImage=cover)
					try:listitem.setInfo(type = "Video", infoLabels = dict)
					except: pass
					listitem.setProperty('fanart_image', cover)
					purl = sys.argv[0] + '?mode=OpenCat2'\
						+ '&url=' + urllib.quote_plus(row_url)\
						+ '&title=' + urllib.quote_plus(str(sids+"|"+size+"| "+tTitle[5]))\
						+ '&info=' + urllib.quote_plus(repr(dict))
					xbmcplugin.addDirectoryItem(handle, purl, listitem, True, totalItems=len(RootList)-defekt)
				else: defekt+=1
			else: defekt+=1


	Title = "[НАЙТИ ЕЩЕ]"
	row_url = url
	try: n=str(int(row_url)+1)
	except: n="1"
	listitem = xbmcgui.ListItem(Title)
	listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
	purl = sys.argv[0] + '?mode=SearchN'\
		+ '&url=' + urllib.quote_plus(n)\
		+ '&title=' + urllib.quote_plus(repr(filtr))\
		+ '&category=' + urllib.quote_plus(category)\
		+ '&sort=' + urllib.quote_plus(sort)\
		+ '&text=' + urllib.quote_plus(text)
	xbmcplugin.addDirectoryItem(handle, purl, listitem, True)



def Search(category, sort, text, url='0'):
	HideScr = __settings__.getSetting("Hide Scr")
	HideTSnd = __settings__.getSetting("Hide TSound")
	TitleMode = __settings__.getSetting("Title Mode")
	EnabledFiltr = __settings__.getSetting("EnabledFiltr")
	Filtr = __settings__.getSetting("Filtr")

	RL=upd(category, sort, text, url)
	RootList=format(RL)
	if text == '0':
			Title = "[Поиск]"
			row_url = url
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Search'\
				+ '&url=' + urllib.quote_plus('0')\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus(category)\
				+ '&sort=' + urllib.quote_plus(sort_sid)\
				+ '&text=' + urllib.quote_plus('1')
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)
			
#			Title = "[Новые]"
#			row_url = url
#			listitem = xbmcgui.ListItem(Title)
#			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
#			purl = sys.argv[0] + '?mode=Search'\
#				+ '&url=' + urllib.quote_plus('0')\
#				+ '&title=' + urllib.quote_plus(Title)\
#				+ '&category=' + urllib.quote_plus(category)\
#				+ '&sort=' + urllib.quote_plus(sort_data)\
#				+ '&text=' + urllib.quote_plus('0')
#			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)
			
			Title = "[Далее >]"
			row_url = url
			try: n=str(int(row_url)+1)
			except: n="1"
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Search'\
				+ '&url=' + urllib.quote_plus(n)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus(category)\
				+ '&sort=' + urllib.quote_plus(sort)\
				+ '&text=' + urllib.quote_plus('0')
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)

	k=0
	TLD=[]
	defekt=0
	for tTitle in RootList:
		if len(tTitle)==8:
			tTitle.insert(0," ")
			tTitle.insert(0," ")
		if len(tTitle)==9:
			tTitle.insert(6," ")
		
		if len(tTitle)==10 and int(tTitle[8])>0:
			#print tTitle
			size=tTitle[7]
			if size[-2:]=="MB":size=size[:-5]+"MB"
			
			if len(size)==3:size=size.center(10)
			elif len(size)==4:size=size.center(9)
			elif len(size)==5:size=size.center(8)
			elif len(size)==6:size=size.center(8)
			
			if len(tTitle[8])==1:sids=tTitle[8].center(9)
			elif len(tTitle[8])==2:sids=tTitle[8].center(8)
			elif len(tTitle[8])==3:sids=tTitle[8].center(7)
			elif len(tTitle[8])==4:sids=tTitle[8].center(6)
			else:sids=tTitle[8]
			
			#------------------------------------------------
			k+=1
			nnn=tTitle[4].find("/")
			ntor=xt(tTitle[4][:nnn])
			#print ntor
			if k<210:
				#nnn=tTitle[1].rfind("/")+1
				#ntor=xt(tTitle[1][nnn:])
				dict=get_minfo(ntor)
				try:dict=get_minfo(ntor)
				except:dict={}
				try:cover=dict["cover"]
				except:cover=""
				
			#-------------------------------------------------
			
			#Title = "|"+sids+"|"+size+"|  "+tTitle[5]
			Title = "|"+sids+"|  "+tTitle[5]
			UF=0
			if EnabledFiltr == 'true' and Filtr<>"":
				Fnu=Filtr.replace(",",'","')
				Fnu=Fnu.replace('" ','"')
				F1=eval('["'+Fnu+'", "4565646dsfs546546"]')
				Tlo=rulower(Title)
				try:Glo=rulower(dict['genre'])
				except: Glo="45664sdgd6546546"
				for Fi in F1:
					if Tlo.find(rulower(Fi))>=0:UF+=1
					if Glo.find(rulower(Fi))>=0:UF+=1
			Tresh=["Repack"," PC ","XBOX","RePack","FB2","TXT","DOC"," MP3"," JPG"," PNG"," SCR"]
			for TRi in Tresh:
				if tTitle[5].find(TRi)>=0:UF+=1
					
			if HideScr == 'true':
				nH1=Title.find("CAMRip")
				nH2=Title.find(") TS")
				nH3=Title.find("CamRip")
				nH4=Title.find(" DVDScr")
				nH=nH1+nH2+nH3+nH4
			else:
				nH=-1
				
			if HideTSnd == 'true':
				sH=Title.find("Звук с TS")
			else:
				sH=-1
				
			if TitleMode == '1': 
				k1=Title.find('/')
				if k1<0: k1=Title.find('(')
				tmp1=Title[:k1]
				n1=Title.find('(')
				k2=Title.find(' от ')
				if k2<0: k2=None
				tmp2=Title[n1:k2]
				Title = tmp1+tmp2
				Title = Title.replace("| Лицензия","")
				Title = Title.replace("| лицензия","")
				Title = Title.replace("| ЛицензиЯ","")
			
			dict['ntor']=ntor
			tTitle5=ru(tTitle[5].strip().replace("ё","е"))
			nc=tTitle5.find(") ")
			nc2=tTitle5.find("/ ")
			if nc2<nc and nc2 >0: nc=nc2
			CT=rulower(tTitle5[:nc].strip())
			#Title=CT
			if UF==0 and nH<0 and sH<0 and (CT not in TLD):
				TLD.append(CT)
				row_url = tTitle[1]
				Title=Title.replace("&quot;",'"')
				listitem = xbmcgui.ListItem(Title, thumbnailImage=cover, iconImage=cover)
				try:listitem.setInfo(type = "Video", infoLabels = dict)
				except: pass
				listitem.setProperty('fanart_image', cover)
				purl = sys.argv[0] + '?mode=OpenCat2'\
					+ '&url=' + urllib.quote_plus(row_url)\
					+ '&title=' + urllib.quote_plus(str(sids+"|"+size+"| "+tTitle[5]))\
					+ '&info=' + urllib.quote_plus(repr(dict))
				xbmcplugin.addDirectoryItem(handle, purl, listitem, True, totalItems=len(RootList)-defekt)
			else: defekt+=1

	if text == '0':
			Title = "[Далее >]"
			row_url = url
			try: n=str(int(row_url)+1)
			except: n="1"
			listitem = xbmcgui.ListItem(Title)
			listitem.setInfo(type = "Video", infoLabels = {"Title": Title} )
			purl = sys.argv[0] + '?mode=Search'\
				+ '&url=' + urllib.quote_plus(n)\
				+ '&title=' + urllib.quote_plus(Title)\
				+ '&category=' + urllib.quote_plus(category)\
				+ '&sort=' + urllib.quote_plus(sort)\
				+ '&text=' + urllib.quote_plus('0')
			xbmcplugin.addDirectoryItem(handle, purl, listitem, True)



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

def formating(str):
	
	str=str.replace('а','a')
	str=str.replace('е','e')
	str=str.replace('ё','e')
	str=str.replace('о','o')
	str=str.replace('р','p')
	str=str.replace('с','c')
	str=str.replace('х','x')
	
	str=str.replace('А','A')
	str=str.replace('Е','E')
	str=str.replace('К','K')
	str=str.replace('М','M')
	str=str.replace('Н','H')
	str=str.replace('О','O')
	str=str.replace('Р','P')
	str=str.replace('С','C')
	str=str.replace('Т','T')
	str=str.replace('Х','X')

	return str

def rulower(str):
	str=str.strip()
	str=xt(str).lower()
	str=str.replace('Й','й')
	str=str.replace('Ц','ц')
	str=str.replace('У','у')
	str=str.replace('К','к')
	str=str.replace('Е','е')
	str=str.replace('Н','н')
	str=str.replace('Г','г')
	str=str.replace('Ш','ш')
	str=str.replace('Щ','щ')
	str=str.replace('З','з')
	str=str.replace('Х','х')
	str=str.replace('Ъ','ъ')
	str=str.replace('Ф','ф')
	str=str.replace('Ы','ы')
	str=str.replace('В','в')
	str=str.replace('А','а')
	str=str.replace('П','п')
	str=str.replace('Р','р')
	str=str.replace('О','о')
	str=str.replace('Л','л')
	str=str.replace('Д','д')
	str=str.replace('Ж','ж')
	str=str.replace('Э','э')
	str=str.replace('Я','я')
	str=str.replace('Ч','ч')
	str=str.replace('С','с')
	str=str.replace('М','м')
	str=str.replace('И','и')
	str=str.replace('Т','т')
	str=str.replace('Ь','ь')
	str=str.replace('Б','б')
	str=str.replace('Ю','ю')
	return str


def OpenCat2(url, name, dict):
	ntor=dict["ntor"]
	L=get_qual(ntor)
	try:cover=dict["cover"]
	except:cover=""
		

	row_url = url
	Title=name
	listitem = xbmcgui.ListItem(Title, thumbnailImage=cover, iconImage=cover)
	try:listitem.setInfo(type = "Video", infoLabels = dict)
	except: pass
	listitem.setProperty('fanart_image', cover)
	purl = sys.argv[0] + '?mode=OpenCat'\
		+ '&url=' + urllib.quote_plus(row_url)\
		+ '&title=' + urllib.quote_plus(Title)\
		+ '&info=' + urllib.quote_plus(repr(dict))
	xbmcplugin.addDirectoryItem(handle, purl, listitem, True)



	for i in L:

				size=i[6]
				if size[-2:]=="MB":size=size[:-5]+"MB"
				if len(size)==3:size=size.center(10)
				elif len(size)==4:size=size.center(9)
				elif len(size)==5:size=size.center(8)
				elif len(size)==6:size=size.center(8)
			
				if len(i[8])==1:sids=i[8].center(9)
				elif len(i[8])==2:sids=i[8].center(8)
				elif len(i[8])==3:sids=i[8].center(7)
				elif len(i[8])==4:sids=i[8].center(6)
				else:sids=tTitle[8]


				row_url = i[1]
				n=i[4].find(")")
				qu=i[4]#[n+1:]
				Title=sids+"|"+size+"| "+qu#i[4]
				listitem = xbmcgui.ListItem(Title, thumbnailImage=cover, iconImage=cover)
				try:listitem.setInfo(type = "Video", infoLabels = dict)
				except: pass
				listitem.setProperty('fanart_image', cover)
				purl = sys.argv[0] + '?mode=OpenCat'\
					+ '&url=' + urllib.quote_plus(row_url)\
					+ '&title=' + urllib.quote_plus(Title)\
					+ '&info=' + urllib.quote_plus(repr(dict))
				xbmcplugin.addDirectoryItem(handle, purl, listitem, True)


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



xplayer=xbmc.Player(xbmc.PLAYER_CORE_AUTO)
if os.path.isdir("d:\\TorrentStream")==1: TSpath="d:\\TorrentStream\\"
elif os.path.isdir("c:\\TorrentStream")==1: TSpath="c:\\TorrentStream\\"
elif os.path.isdir("e:\\TorrentStream")==1: TSpath="e:\\TorrentStream\\"
elif os.path.isdir("f:\\TorrentStream")==1: TSpath="f:\\TorrentStream\\"
elif os.path.isdir("g:\\TorrentStream")==1: TSpath="g:\\TorrentStream\\"
elif os.path.isdir("h:\\TorrentStream")==1: TSpath="h:\\TorrentStream\\"
else: TSpath="C:\\"
	
	
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
spr=["Все","","","","",""]

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






#xplayer.play("torrentstream:")#C:\Users\Diman\AppData\Roaming\XBMC\addons\plugin.video.RuTor\playlists\179278.torrent 0")
#xplayer.stop()


if mode == None or mode == "None":
	#ShowRoot()
	if text<>"" and text<>"0": spr = eval(text)
	ShowPr(spr,category)

	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle)

if mode == 'Root':
	ShowPr(spr,category)
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle,True,True)
	
if mode == 'Root2':
	#if text<>"" and text<>"0":ShowRoot(AL, text)
	ShowRoot()
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle)#,True,True)

if mode == 'New':
	#if text<>"" and text<>"0":ShowRoot(AL, text)
	ShowNew()
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle)#,True,True)

elif mode == 'SearchN':
	spr = eval(title)
	SearchN(category, sort, text, spr, url)
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle)

	
elif mode == 'Search':
	#xbmcplugin.setContent(int(sys.argv[1]), 'musicvideos')
	#try: from moveinfo_db import*
	#except:pass
	Search(category, sort, text, url)
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle)
	
	#fl = codecs.open(os.path.join( ru(addon.getAddonInfo('path')), "moveinfo_db.py"), "w",'utf8','ignore')
	#fl.write('# -*- coding: utf-8 -*-'+chr(10))
	#elm=str(move_info_db).encode('utf8','ignore')
	#fl.write('move_info_db='+elm)
	#fl.close()

elif mode == 'play_url2':
	play_url2(params)

elif mode == 'OpenCat2':
	OpenCat2(url, title, info)
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle)

elif mode == 'OpenCat':
	Engine = __settings__.getSetting("Engine")
	if Engine=="0":
		try:img=info["cover"]
		except: img=icon
		play_url({'file':url,'img':img})
	else: OpenCat(url, title, info)
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_LABEL)
	xbmcplugin.endOfDirectory(handle)

#elif mode == 'OpenCat':
#	OpenCat(url, title, info)
#	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
#	xbmcplugin.endOfDirectory(handle)

elif mode == 'OpenPage':
	OpenPage(url, title, num, Lgl, info)


elif mode == 'Params':
	if text<>"" and text<>"0": spr = eval(text)
	ShowPr(spr,category)
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle,True,True)
	
elif mode == 'ParamK':
	if text<>"" and text<>"0" and text<>"1" and text<>"2": spr = eval(text)
	ShowK(spr)
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle,True,True)
	
elif mode == 'ParamG':
	if text<>"" and text<>"0" and text<>"1" and text<>"2": spr = eval(text)
	ShowG(spr,category)
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle,True,True)
	
elif mode == 'ParamY':
	if text<>"" and text<>"0" and text<>"1" and text<>"2": spr = eval(text)
	ShowY(spr,category)
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle,True,True)
	
elif mode == 'ParamQ':
	if text<>"" and text<>"0" and text<>"1" and text<>"2": spr = eval(text)
	ShowQ(spr,category)
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle,True,True)

elif mode == 'ParamA':
	if text<>"" and text<>"0" and text<>"1" and text<>"2": spr = eval(text)
	ShowA(spr,category)
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle,True,True)


elif mode == 'ParamT':
	stext=inputbox()
	if text<>"" and text<>"0" and text<>"1" and text<>"2": spr = eval(text)
	spr[4] = stext
	ShowPr(spr,category)
	xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
	xbmcplugin.endOfDirectory(handle,True,True)


c.close()