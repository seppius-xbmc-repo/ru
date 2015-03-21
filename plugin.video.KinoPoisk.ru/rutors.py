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
siteUrl = 'www.rutor.org'
httpSiteUrl = 'http://' + siteUrl
sid_file = os.path.join(xbmc.translatePath('special://temp/'), 'rutors.cookies.sid')
 
cj = cookielib.FileCookieJar(sid_file) 
hr  = urllib2.HTTPCookieProcessor(cj) 
opener = urllib2.build_opener(hr) 
urllib2.install_opener(opener) 

def ru(x):return unicode(x,'utf8', 'ignore')
def xt(x):return xbmc.translatePath(x)


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
		print e


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


def Storr(category, sort, text, url='0'):
	HideScr = 'true'
	HideTSnd = 'true'
	TitleMode = 0
	EnabledFiltr = 'false'
	Filtr = ""

	RL=upd(category, sort, text, url)
	RootList=format(RL)
	Lout=[]
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
			dict={}
			cover=""
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
				#TLD.append(CT)
				row_url = tTitle[1]
				Title=Title.replace("&quot;",'"')
				Lout.append([sids,size,xt(Title),row_url])
				print Title
				
#				listitem = xbmcgui.ListItem(Title, thumbnailImage=cover, iconImage=cover)
#				purl = sys.argv[0] + '?mode=OpenCat2'\
#					+ '&url=' + urllib.quote_plus(row_url)\
#					+ '&title=' + urllib.quote_plus(str(sids+"|"+size+"| "+tTitle[5]))\
#					+ '&info=' + urllib.quote_plus(repr(dict))
#				xbmcplugin.addDirectoryItem(handle, purl, listitem, True, totalItems=len(RootList)-defekt)
			else: defekt+=1
	return Lout



class Tracker:
	def __init__(self):
		pass

	def Search(self, text="миля", category=0):
		Lout=Storr(category, "0", text, url='0')
		return Lout