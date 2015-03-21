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
import urllib,urllib2,cookielib,re,sys,os,time
import xbmcplugin,xbmcgui,xbmcaddon

__settings__ = xbmcaddon.Addon(id='plugin.video.ruhd.ru')
__language__ = __settings__.getLocalizedString
pluginhandle = int(sys.argv[1])
#fanart = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'fanart.jpg'))
thumb = os.path.join(os.getcwd().replace(';', ''), "icon.png" )

def showMessage(heading, message, times = 3000):
	#heading = heading.encode('utf-8')
	#message = message.encode('utf-8')
	xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, thumb))

def Get(url, ref=None, post = None):
	xbmc.output('Get  URL=%s'%url)
	xbmc.output('Get  ref=%s'%ref)
	xbmc.output('Get post=%s'%post)

	cj = cookielib.CookieJar()
	h  = urllib2.HTTPCookieProcessor(cj)
	opener = urllib2.build_opener(h)
	urllib2.install_opener(opener)
	request = urllib2.Request(url, post)
	request.add_header(     'User-Agent','Opera/10.60 (X11; openSUSE 11.3/Linux i686; U; ru) Presto/2.6.30 Version/10.60')
	request.add_header(         'Accept','text/html, application/xml, application/xhtml+xml, */*')
	request.add_header('Accept-Language','ru,en;q=0.9')
	request.add_header('Accept-Charset','utf-8,utf-16;q=0.9')
	if ref != None:
		request.add_header('Referer', ref)
	if post != None:
		request.add_header('Content-Type', 'application/x-www-form-urlencoded')
	phpsessid = __settings__.getSetting('cookie')
	if len(phpsessid) > 0:
		request.add_header('Cookie', 'PHPSESSID=' + phpsessid)
	o = urllib2.urlopen(request)
	for index, cookie in enumerate(cj):
		cookraw = re.compile('<Cookie PHPSESSID=(.*?) for.*/>').findall(str(cookie))
		if len(cookraw) > 0:
			__settings__.setSetting('cookie', cookraw[0])
	http = o.read()
	#print http
	o.close()
	return http

def clean(name):
	pname = re.sub('(?is)<.*?>', '', name, re.DOTALL|re.IGNORECASE)
	remove = [('\n\n',''),('\t',''),('<br/>','\n'),('<br />','\n'),('mdash;',''),('&ndash;',''),('hellip;','\n'),('&amp;',''),('&quot;','"'),
		  ('&#39;','\''),('&nbsp;',' '),('&laquo;','"'),('&raquo;','"'),('&#151;','-')]
	for trash, crap in remove:
		pname=pname.replace(trash, crap)
	return pname

def openROOT(url):
	http = Get(url)
	r1 = re.compile('<div class="CategoryBoxHorizontal">(.*?)</div>', re.DOTALL).findall(http)
	if len(r1) == 0:
		showMessage('ОШИБКА', 'Нет class=CategoryBoxHorizontal')
		return False
	for rb1 in r1:
		r2 = re.compile('<a href="(.*?)"><img border=".*" src="(.*?)".*/></a>').findall(rb1)
		if len(r2) > 0:
			(purl, pimg) = r2[0]
			url = 'http://ruhd.ru/' + purl
			img = 'http://ruhd.ru/' + pimg
			tit = re.compile('cid=(.*?)\n').findall(url+'\n')[0]
			url = urllib.quote_plus(url, '/:?=')
			uri = sys.argv[0] + '?mode=openCATEGORY'
			uri += '&url='+urllib.quote_plus(url)
			uri += '&name='+urllib.quote_plus(tit)
			uri += '&img='+urllib.quote_plus(img)
			item=xbmcgui.ListItem(tit, iconImage=img, thumbnailImage=img)
			item.setInfo(type='video', infoLabels={'title': tit})
			xbmcplugin.addDirectoryItem(pluginhandle,uri,item,True)
		else:
			showMessage('ОШИБКА', 'Шаблон поиска не сработал :(')
			return False
	uri = sys.argv[0] + '?mode=openSEARCH'
	uri += '&name='+urllib.quote_plus('videos')
	item=xbmcgui.ListItem('Поиск', iconImage=thumb, thumbnailImage=thumb)
	xbmcplugin.addDirectoryItem(pluginhandle,uri,item,True)
	xbmcplugin.endOfDirectory(pluginhandle)




'''
<div id="CategoryVideoDetails">(.*?)<div class="clearfix2">
<a href="(.*?)"><img src="(.*?)".*/></a>
<span class=".*">Просмотров:</span>.*\(\s(.*?)\s.*\)
<span class=".*">Длительность:</span>.*\(\s(.*?)\s.*\)
alt="(.*?) Star"

TITLE
Level 0
<a href="(.*?)">\s.[ ]*(.*?)\s.*</a></li>
Level 1
<a href="(.*?)">\s(.*?)\s.*</a></li>
*----------------

<div id="pagination">(.*?)</div>      DOTALL

<div id="pagination">
<ul>
<li><a href="category_home.php?page=1&cid=Разное">1</a></li>
<li><a href="category_home.php?page=2&cid=Разное">2</a></li>
<li><a href="category_home.php?page=9&cid=Разное">9</a></li>
<li><a href="category_home.php?page=10&cid=Разное">10</a></li>
<li><a href="category_home.php?page=11&cid=Разное">11</a></li>
<li><a href="category_home.php?page=2&cid=Разное">Вперёд >></a></li>
</ul>
</div>

'''
def openCATEGORY(url, CatName, fanart, ref = None, post = None):
	http = Get(url, ref, post)

	rnav1 = re.compile('<div id="pagination">(.*?)</div>', re.DOTALL).findall(http.replace('</li>', '\n'))
	if len(rnav1) > 0:
		rnav2 = re.compile('<a href.*?page=(.[0-9]*).*</a>').findall(rnav1[0])
		if len(rnav2) > 0:
			print rnav2
			for rnav3 in rnav2:
				NavName = CatName + ' / Страница ' + rnav3
				uri = sys.argv[0] + '?mode=openCATEGORY'
				uri += '&url='+urllib.quote_plus(url + '&page=' + rnav3)
				uri += '&name='+urllib.quote_plus(CatName)
				uri += '&img='+urllib.quote_plus(fanart)
				item=xbmcgui.ListItem(NavName, iconImage=fanart, thumbnailImage=fanart)
				item.setInfo(type='video', infoLabels={'title': NavName})
				xbmcplugin.addDirectoryItem(pluginhandle,uri,item,True)
		else:
			showMessage('ОШИБКА', 'rnav2 = 0')
	else:
		showMessage('ОШИБКА', 'rnav1 = 0')

	r1 = re.compile('<div id="CategoryVideoDetails">(.*?)<div class="clearfix2">', re.DOTALL).findall(http)
	if len(r1) == 0:
		xbmc.output('ERROR len(r1) == 0')
		return False
	for rb1 in r1:
		#xbmc.output('rb1 = %s' % rb1)
		r2 = re.compile('<a href="(.*?)"><img src="(.*?)".*/></a>').findall(rb1)
		if len(r2) > 0:
			(purl, pimg) = r2[0]
			url = 'http://ruhd.ru/' + purl
			img = 'http://ruhd.ru/' + pimg

			StarS = '0'
			try:
				StarS = re.compile('alt="(.*?) Star"').findall(rb1)[0]
			except:
				pass

			ShowsCount = '0'
			try:
				ShowsCount = re.compile('<span class=".*">Просмотров:</span>.*\(\s(.*?)\s.*\)').findall(rb1)[0]
			except:
				pass

			Duration = '00:00:00'
			try:
				Duration = re.compile('<span class=".*">Длительность:</span>.*\(\s(.*?)\s.*\)').findall(rb1)[0]
			except:
				pass

			Title = 'Название не найдено'

			try:
				Title = re.compile('<a href="(.*?)">\s(.*?)\s.*</a></li>').findall(rb1)[0][1]
			except:
				pass
			try:
				Title = re.compile('<a href="(.*?)">\s.[ ]*(.*?)\s.*</a></li>').findall(rb1)[0][1]
			except:
				pass


			xbmc.output('***        url = %s' % url)
			xbmc.output('***        img = %s' % img)
			xbmc.output('***      StarS = %s' % StarS)
			xbmc.output('*** ShowsCount = %s' % ShowsCount)
			xbmc.output('***   Duration = %s' % Duration)
			xbmc.output('***      Title = %s' % Title)


			uri = sys.argv[0] + '?mode=PLAY'
			uri += '&url='+urllib.quote_plus(url)
			uri += '&name='+urllib.quote_plus(Title)
			uri += '&img='+urllib.quote_plus(img)
			item=xbmcgui.ListItem(Title, iconImage=img, thumbnailImage=img)
			item.setInfo(type='video', infoLabels={'title': Title})

			#item.setInfo( type='video', infoLabels={'title': title, 'plot': description})
			item.setProperty('IsPlayable', 'true')
			item.setProperty('fanart_image',fanart)


			xbmcplugin.addDirectoryItem(pluginhandle,uri,item)


	xbmcplugin.endOfDirectory(pluginhandle)



def PLAY(url):
	http = Get(url)
	r1 = re.compile('\'(.*?)\.divx\'').findall(http)
	if len(r1) == 0:
		r1 = re.compile('"(.*?)\.divx"').findall(http)
		if len(r1) == 0:
			showMessage('ОШИБКА', 'Нет файла *.divx')
			return False

	src = r1[0] + '.divx'
	src += '|Referer=' + urllib.quote_plus(url)
	src += '&User-Agent=' + urllib.quote_plus('Opera/10.60 (X11; openSUSE 11.3/Linux i686; U; ru) Presto/2.6.30 Version/10.60')
	src += '&Accept=' + urllib.quote_plus('text/html, application/xml, application/xhtml+xml, */*')
	src += '&Accept-Language=' + urllib.quote_plus('ru,en;q=0.9')
	item=xbmcgui.ListItem(path = src)
	xbmcplugin.setResolvedUrl(pluginhandle, True, item)

def get_params(paramstring):
    param=[]
    if len(paramstring)>=2:
        params=paramstring
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

params = get_params(sys.argv[2])
url='http://ruhd.ru/category.php'
name=''
plot=''
mode=None
img=thumb

try: mode=params['mode']
except: pass

try:    url   = urllib.unquote_plus(params['url'])
except: pass

try: name=urllib.unquote_plus(params['name'])
except: pass

try: img =urllib.unquote_plus(params['img'])
except: pass


if mode=='openCATEGORY':
	openCATEGORY(url, name, img)

elif mode=='PLAY':
	PLAY(url)

elif mode=='openSEARCH':
	pass_keyboard = xbmc.Keyboard()
	pass_keyboard.setHeading('Что ищем?')
	pass_keyboard.doModal()
	if (pass_keyboard.isConfirmed()):
		SearchStr = pass_keyboard.getText()
		dialog  = xbmcgui.Dialog()
		qstring = 'keyword=%s&type=%s&B2=%s' % (urllib.quote_plus(SearchStr), urllib.quote_plus(name), urllib.quote_plus('Найти'))
		openCATEGORY('http://ruhd.ru/search.php', 'Поиск', thumb, url, qstring)
	else:
		exit

else:
	openROOT(url)

