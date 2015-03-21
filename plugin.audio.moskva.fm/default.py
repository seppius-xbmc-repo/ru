#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib,urllib2,re,sys,os,random
import xbmcplugin,xbmcgui,xbmcaddon
import time

pluginhandle = int(sys.argv[1])
thumb = os.path.join(os.getcwd().replace(';', ''), "icon.png" )
xbmcplugin.setContent(int(sys.argv[1]), 'music')
__settings__ = xbmcaddon.Addon(id='plugin.audio.moskva.fm')

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


def mfindal(http, ss, es):
	L=[]
	while http.find(es)>0:
		s=http.find(ss)
		#sn=http[s:]
		e=http.find(es)
		i=http[s:e]
		L.append(i)
		http=http[e+2:]
	return L


def OpenStations(ci):
	url="http://www.moskva.fm/stations/order:name"
	http = getURL(url)
	ss = '<div class="thumbnail msk-thumbnail-station msk-thumbnail-big msk-thumbnail-mount'
	es = 'onclick="return openPlr(this)"'
	L1=mfindal(http, ss, es)
	for i in L1:
			i=i.replace(chr(10),"").replace(chr(13),"").replace('	',"").replace('<div class="thumbnail msk-thumbnail-station msk-thumbnail-big msk-thumbnail-mount',"['").replace('" class="logo" style="display:block;" title="',"','").replace('"><img src="',"','").replace('" title="',"','").replace('class="station"><b>',"','").replace('</b></a><small class="meta">',"','").replace('&nbsp;FM</small></h4><!--p><span class="button_item"><a href="http://www.moskva.fm/play/',"','").replace('/translation"',"']")
			#print i
			try:
				Li=eval(i)
				url = Li[6]
				img = Li[2]
				if len(Li[5])<5: dbr="  "
				else:dbr=""
				title=dbr+Li[5]+" FM"+"  -  [B]"+Li[4] +"[/B]"
				uri = sys.argv[0] + '?mode=PlayStation'
				uri += '&url='  + urllib.quote_plus(url)
				uri += '&name='  + urllib.quote_plus(title)
				uri += '&img='  + urllib.quote_plus(img)
				item = xbmcgui.ListItem(title, iconImage = img, thumbnailImage = img)
				item.setInfo(type="Music", infoLabels={"Title": title})
				xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
			except:
				print "err: " +i
	xbmcplugin.endOfDirectory(pluginhandle)


def GetHash(id):
	ltm=str(time.time())
	link='http://www.moskva.fm/player_xml.html?type=full&time='+ltm+'&station='+id
	http=getURL(link)
	#print http
	ss="timestamp?format=flv&amp;hash="
	es='<channels>'
	
	hashs=mfindal(http, ss, es)[0]
	hash=hashs[len(ss):hashs.find('" />')]
	return hash

def PlayStation(id,name,img):
	tzn= float(__settings__.getSetting('tm'))
	item = xbmcgui.ListItem(name, iconImage = img, thumbnailImage = img)
	item.setInfo(type="Music", infoLabels={"Title": name})
	ltm=str(time.time() + tzn*3600 - 120)
	#ltm=str(time.time())- time.timezone
	hash=GetHash(id)
	link='http://extstreamer.moskva.fm/stream/'+id+'/'+ltm+'?format=mp3'+"&hash="+hash#flv
	xbmc.Player(xbmc.PLAYER_CORE_AUTO).play(link, item)



params = get_params()
url  =	'http://www.moskva.fm/rss/onair.xml'
mode =	None
name =	''
img =	' '

try: url = urllib.unquote_plus(params["url"])
except: pass
try: mode = urllib.unquote_plus(params["mode"])
except: pass
try: name = urllib.unquote_plus(params["name"])
except: pass
try: img = urllib.unquote_plus(params["img"])
except: pass



if   mode == None:OpenStations(url)
elif mode == 'PlayStation':PlayStation(url,name,img)

