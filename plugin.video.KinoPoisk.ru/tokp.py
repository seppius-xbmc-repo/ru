#!/usr/bin/python
# -*- coding: utf-8 -*-

import httplib
#import re
#import sys
import os
import Cookie

import string, xbmc, xbmcgui, xbmcplugin, urllib, cookielib, xbmcaddon
#-------------------------------
import urllib, urllib2, time, random
#from time import gmtime, strftime 
#from urlparse import urlparse 

import HTMLParser 
hpar = HTMLParser.HTMLParser()
#-----------------------------------------
import socket
socket.setdefaulttimeout(50)

icon = ""
siteUrl = 'www.KinoPoisk.ru'
httpSiteUrl = 'http://' + siteUrl
sid_file = os.path.join(xbmc.translatePath('special://temp/'), '2kp.cookies.sid')#'plugin.video.krasfs.ru.cookies.sid'

#h = int(sys.argv[1])


#--------------- 
cj = cookielib.FileCookieJar(sid_file) 
hr  = urllib2.HTTPCookieProcessor(cj) 
opener = urllib2.build_opener(hr) 
urllib2.install_opener(opener) 

def unescape(text): 
    try: 
        text = hpar.unescape(text) 
    except: 
        text = hpar.unescape(text.decode('utf8')) 

    try: 
        text = unicode(text, 'utf-8') 
    except: 
        text = text 

    return text 
#--------------- 
url='http://www.KinoPoisk.ru/' 


def showMessage(heading, message, times = 3000):
	xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))

def ru(x):return unicode(x,'utf8', 'ignore')
def xt(x):return xbmc.translatePath(x)

def mfindal(http, ss, es):

	L=[]
	while http.find(es)>0:
		s=http.find(ss)
		e=http.find(es)
		i=http[s:e]
		L.append(i)
		http=http[e+2:]
	return L
	
def VK(url):
	try:
		http2 = GET(url,url,siteUrl='www.vk.com')
		if http2 == None:
			#showMessage('fast-torrent:', 'Сервер не отвечает', 1000)
			return None
		else:
			#debug(http2)
			ss='url240='
			es='240.mp4'
			L3=mfindal(http2, ss, es)
			#print L3
			url720=L3[0][7:]+"720.mp4"
			return url720
	except:
			return None

def formvk(http):
	ss='http://vk.com/video_ext'
	es='" width="607" height="360" frameborder="0"'
	Lvk=mfindal(http,ss,es)
	Lv=[]
	for i in Lvk:
		#print i
		v=VK(i)
		if v !=None: 
			#print v
			Lv.append(v)
	return Lv


def formtext(http):
	ss='<table class="table" id="torrents_result">'
	es='<div class="col-md-3 right-block">'
	#http=mfindal(http,ss,es)[0]
	
	ss='<tr><td><a href="'
	es='</td></tr>'
	Lt=mfindal(http,ss,es)
	Lr=[]
	
	for i in Lt:
		ss='/get_torrent/'
		es='.torrent'
		try:torr="http://www.2kinopoisk.ru"+mfindal(i,ss,es)[0]+'.torrent'
		except:torr=""
		#print torr
		
		if torr != "":
			ss='/images/'
			es='.ico'
			img="http://www.2kinopoisk.ru"+mfindal(i,ss,es)[0]+'.ico'
			#print img
		
			ss='green"></span>'
			es='</td><td><span'
			sids=mfindal(i,ss,es)[0][len(ss):]
			if len(sids)==1:sids="       "+sids+"      "
			if len(sids)==2:sids="      "+sids+"     "
			if len(sids)==3:sids="    "+sids+"    "
			if len(sids)==4:sids="   "+sids+"   "
			if len(sids)==5:sids="  "+sids+"  "
			if len(sids)==6:sids=" "+sids+" "

			#print sids
		
			ss='.torrent" >'
			es='</td>  <td style="text-align: right; white-space:nowrap;">'
			label=mfindal(i,ss,es)[0][len(ss):].replace("</a>","").replace(chr(10),"").replace(chr(13),"").replace("   "," ").replace("  "," ")
			#print label
			
			size=i[i.find(es)+len(es):]
			if len(size)==4:size="     "+size+"     "
			if len(size)==5:size="    "+size+"   "
			if len(size)==6:size="   "+size+"   "
			if len(size)==7:size="  "+size+"  "
			if len(size)==8:size=" "+size+" "
			if len(size)==9:size=size.replace(" ","")
			if len(size)==10:size=size

			#print size
			Lr.append([sids,size,label,torr,img])
	return Lr

def formating(str):
	str=str.strip()
	str=str.replace('%','%25')
	str=str.replace('&','%26')
	str=str.replace('?','%3F')
	str=str.replace('&','%26')
	str=str.replace('!','%21')
	str=str.replace(':','%3A')
	str=str.replace('#','%23')
	str=str.replace(',','%2C')
	str=str.replace(';','%3B')
	str=str.replace('@','%40')
	str=str.replace('(','%28')
	str=str.replace(')','%29')
	str=str.replace('"','%22')
	
	str=str.replace('а','%E0')
	str=str.replace('б','%E1')
	str=str.replace('в','%E2')
	str=str.replace('г','%E3')
	str=str.replace('д','%E4')
	str=str.replace('е','%E5')
	str=str.replace('ё','%b8')
	str=str.replace('ж','%E6')
	str=str.replace('з','%E7')
	str=str.replace('и','%E8')
	str=str.replace('й','%E9')
	str=str.replace('к','%EA')
	str=str.replace('л','%EB')
	str=str.replace('м','%EC')
	str=str.replace('н','%ED')
	str=str.replace('о','%EE')
	str=str.replace('п','%EF')
	str=str.replace('р','%F0')
	str=str.replace('с','%F1')
	str=str.replace('т','%F2')
	str=str.replace('у','%F3')
	str=str.replace('ф','%F4')
	str=str.replace('х','%F5')
	str=str.replace('ц','%F6')
	str=str.replace('ч','%F7')
	str=str.replace('ш','%F8')
	str=str.replace('щ','%F9')
	str=str.replace('ь','%FA')
	str=str.replace('ы','%FB')
	str=str.replace('ъ','%FC')
	str=str.replace('э','%FD')
	str=str.replace('ю','%FE')
	str=str.replace('я','%FF')
	
	str=str.replace('А','%C0')
	str=str.replace('Б','%C1')
	str=str.replace('В','%C2')
	str=str.replace('Г','%C3')
	str=str.replace('Д','%C4')
	str=str.replace('Е','%C5')
	str=str.replace('Ё','%A8')
	str=str.replace('Ж','%C6')
	str=str.replace('З','%C7')
	str=str.replace('И','%C8')
	str=str.replace('Й','%C9')
	str=str.replace('К','%CA')
	str=str.replace('Л','%CB')
	str=str.replace('М','%CC')
	str=str.replace('Н','%CD')
	str=str.replace('О','%CE')
	str=str.replace('П','%CF')
	str=str.replace('Р','%D0')
	str=str.replace('С','%D1')
	str=str.replace('Т','%D2')
	str=str.replace('У','%D3')
	str=str.replace('Ф','%D4')
	str=str.replace('Х','%D5')
	str=str.replace('Ц','%D6')
	str=str.replace('Ч','%D7')
	str=str.replace('Ш','%D8')
	str=str.replace('Щ','%D9')
	str=str.replace('Ь','%DA')
	str=str.replace('Ы','%DB')
	str=str.replace('Ъ','%DC')
	str=str.replace('Э','%DD')
	str=str.replace('Ю','%DE')
	str=str.replace('Я','%DF')
	str=str.replace(' ','+')
	return str

def inputbox():
	skbd = xbmc.Keyboard()
	skbd.setHeading('Поиск:')
	skbd.doModal()
	if skbd.isConfirmed():
		SearchStr = skbd.getText()
		return SearchStr
	else:
		return ""

headers  = {
	'User-Agent' : 'Opera/9.80 (X11; Linux i686; U; ru) Presto/2.7.62 Version/11.00',
	'Accept'     :' text/html, application/xml, application/xhtml+xml, image/png, image/jpeg, image/gif, image/x-xbitmap, */*',
	'Accept-Language':'ru-RU,ru;q=0.9,en;q=0.8',
	'Accept-Charset' :'utf-8, utf-16, *;q=0.1',
	'Accept-Encoding':'identity, *;q=0'
}
def GET(target, referer, post_params = None, accept_redirect = True, get_redirect_url = False, siteUrl='www.2KinoPoisk.ru'):
	try:
		connection = httplib.HTTPConnection(siteUrl)

		if post_params == None:
			method = 'GET'
			post = None
		else:
			method = 'POST'
			post = urllib.urlencode(post_params)
			headers['Content-Type'] = 'application/x-www-form-urlencoded'
		
		sid_file = os.path.join(xbmc.translatePath('special://temp/'), 'plugin.video.2KinoPoisk.ru.cookies.sid')
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



			
class Tracker:
	def __init__(self):
		pass

	def Search(self, idkp):
		html=GET('http://www.2kinopoisk.ru/film/'+idkp,'http://www.2kinopoisk.ru/film/'+idkp)
		VL=formvk(html)
		RL=formtext(html)
		return RL, VL