#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib,urlparse,requests,contextlib
import re,cookielib,sys,os

import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmc
import xbmcaddon

from BeautifulSoup import BeautifulSoup

reload(sys)
sys.setdefaultencoding('utf8')

__addon__ = xbmcaddon.Addon(id = 'plugin.video.const.kinozal.tv')

if __addon__.getSetting('site_url') == '0':
	siteurl = 'https://kinozal-tv.appspot.com'
	urlpos = 2
else:
	siteurl = 'http://kinozal.tv'
	urlpos = 1
imgurl = siteurl
if __addon__.getSetting('use_proxy') == 'true' and __addon__.getSetting('img_appspot') == 'true':
	imgurl = 'https://kinozal-tv.appspot.com'

headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
		   'Accept' : '*/*','Accept-Language' : 'ru,en-US;q=0.7,en;q=0.3','Referer' : siteurl,
		   'Accept-Encoding' : 'gzip, deflate','Host' : siteurl.replace('https://','').replace('http://',''),'Connection' : 'Keep-Alive'}

def human(s):
	return s.decode('cp1251').encode('utf8')

def torrkill(params):
	if xbmcgui.Dialog().yesno('Очистка папки','Очистить папку торрентов ?',autoclose=15000):
		import shutil
		folder = os.path.join(__addon__.getAddonInfo('path'),'torrents')
		for filename in os.listdir(folder):
			file_path = os.path.join(folder, filename)
			try:
				if os.path.isfile(file_path) or os.path.islink(file_path):
					os.unlink(file_path)
				elif os.path.isdir(file_path):
					shutil.rmtree(file_path)
			except Exception as e:
				showMessage('Ошибка','Failed to delete %s. Reason: %s' % (file_path, e))
		showMessage('Информация','Папка торрентов очищена')

def PrepareStr(x):#('&#39;','’'), ('&#145;','‘')
	L=[('&quot;','"'),('&#039;',"'"),('&amp;',"&"),('&#133;','…'),('&#38;','&'),('&#34;','"'), ('&#39;','"'), ('&#145;','"'), ('&#146;','"'), ('&#147;','“'), ('&#148;','”'), ('&#149;','•'), ('&#150;','–'), ('&#151;','—'), ('&#152;','?'), ('&#153;','™'), ('&#154;','s'), ('&#155;','›'), ('&#156;','?'), ('&#157;',''), ('&#158;','z'), ('&#159;','Y'), ('&#160;',''), ('&#161;','?'), ('&#162;','?'), ('&#163;','?'), ('&#164;','¤'), ('&#165;','?'), ('&#166;','¦'), ('&#167;','§'), ('&#168;','?'), ('&#169;','©'), ('&#170;','?'), ('&#171;','«'), ('&#172;','¬'), ('&#173;',''), ('&#174;','®'), ('&#175;','?'), ('&#176;','°'), ('&#177;','±'), ('&#178;','?'), ('&#179;','?'), ('&#180;','?'), ('&#181;','µ'), ('&#182;','¶'), ('&#183;','·'), ('&#184;','?'), ('&#185;','?'), ('&#186;','?'), ('&#187;','»'), ('&#188;','?'), ('&#189;','?'), ('&#190;','?'), ('&#191;','?'), ('&#192;','A'), ('&#193;','A'), ('&#194;','A'), ('&#195;','A'), ('&#196;','A'), ('&#197;','A'), ('&#198;','?'), ('&#199;','C'), ('&#200;','E'), ('&#201;','E'), ('&#202;','E'), ('&#203;','E'), ('&#204;','I'), ('&#205;','I'), ('&#206;','I'), ('&#207;','I'), ('&#208;','?'), ('&#209;','N'), ('&#210;','O'), ('&#211;','O'), ('&#212;','O'), ('&#213;','O'), ('&#214;','O'), ('&#215;','?'), ('&#216;','O'), ('&#217;','U'), ('&#218;','U'), ('&#219;','U'), ('&#220;','U'), ('&#221;','Y'), ('&#222;','?'), ('&#223;','?'), ('&#224;','a'), ('&#225;','a'), ('&#226;','a'), ('&#227;','a'), ('&#228;','a'), ('&#229;','a'), ('&#230;','?'), ('&#231;','c'), ('&#232;','e'), ('&#233;','e'), ('&#234;','e'), ('&#235;','e'), ('&#236;','i'), ('&#237;','i'), ('&#238;','i'), ('&#239;','i'), ('&#240;','?'), ('&#241;','n'), ('&#242;','o'), ('&#243;','o'), ('&#244;','o'), ('&#245;','o'), ('&#246;','o'), ('&#247;','?'), ('&#248;','o'), ('&#249;','u'), ('&#250;','u'), ('&#251;','u'), ('&#252;','u'), ('&#253;','y'), ('&#254;','?'), ('&#255;','y'), ('&laquo;','"'), ('&raquo;','"'), ('&nbsp;',' '), ('&mdash;','-')]
	for i in L:
		x=x.replace(i[0], i[1])
	return x

where=['названии','имени актера','жанре','формула']
show=['везде','фильмы','мультфильмы','сериалы','шоу','музыку']
cshow=['0','1002','1003','1001','1006','1004']
form=['Все','DVD/BD/HD(Rip)','BD/HD(Rip)(1080|720)','Blu-Ray и BD Remux','TVRip','3D','4K']
cform=['0','1','3','4','5','6','7']
filter=['Все','Золото','Серебро']
cfilter=['0','11','12']
sorting=['Залит','Сидам','Пирам','Размер','Комментариям','Скачали']
csorting=['0','1','2','3','4','5']

try:
	iwhere=int(__addon__.getSetting('where'))
	ishow=int(__addon__.getSetting('show'))
	iform=int(__addon__.getSetting('form'))
	ifilter=int(__addon__.getSetting('filter'))
	isorting=int(__addon__.getSetting('sorting'))
	iyear = __addon__.getSetting('year')
	querry=__addon__.getSetting('querry')
except:
	__addon__.setSetting('where','0')
	__addon__.setSetting('show','0')
	__addon__.setSetting('form','0')
	__addon__.setSetting('filter','0')
	__addon__.setSetting('sorting','1')
	__addon__.setSetting('querry','')
	__addon__.setSetting('year', '')

hos = int(sys.argv[1])

xbmcplugin.setContent(int(hos), 'movies')

__language__ = __addon__.getLocalizedString

addon_icon	= __addon__.getAddonInfo('icon')
addon_fanart  = __addon__.getAddonInfo('fanart')
addon_path	= __addon__.getAddonInfo('path')
addon_type	= __addon__.getAddonInfo('type')
addon_id	  = __addon__.getAddonInfo('id')
addon_author  = __addon__.getAddonInfo('author')
addon_name	= __addon__.getAddonInfo('name')
addon_version = __addon__.getAddonInfo('version')

def showMessage(heading, message, times = 5000, pics = addon_icon):
	try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading.encode('utf-8'), message.encode('utf-8'), times, pics.encode('utf-8')))
	except Exception, e:
		xbmc.log( '[%s]: showMessage: Transcoding UTF-8 failed [%s]' % (addon_id, e), 2 )
		try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, pics))
		except Exception, e:
			xbmc.log( '[%s]: showMessage: exec failed [%s]' % (addon_id, e), 3 )

ktv_login = __addon__.getSetting('login')
ktv_password = __addon__.getSetting('password')
ktv_folder = __addon__.getSetting('download_path')
ktv_cookies_uid = __addon__.getSetting('cookies_uid')
ktv_cookies_pass = __addon__.getSetting('cookies_pass')

ktv_use_proxy = __addon__.getSetting("use_proxy")
ktv_proxy_host = __addon__.getSetting('proxy_host')
ktv_proxy_port = __addon__.getSetting('proxy_port')

ktv_proxy_user = ''
ktv_proxy_password = ''
ktv_use_proxy_auth = __addon__.getSetting('use_proxy_auth')
if ktv_use_proxy_auth == 'true':
	ktv_proxy_user = __addon__.getSetting('proxy_user')
	ktv_proxy_password = __addon__.getSetting('proxy_password')

if not ktv_login or not ktv_password: __addon__.openSettings()

ktv_proxy = None
if ktv_use_proxy == 'true':
	proxy_auth = ''
	if ktv_use_proxy_auth == 'true':
		proxy_auth = ktv_proxy_user + ':' + ktv_proxy_password + '@'
	ktv_proxy = {
		'http': 'http://'+proxy_auth+ktv_proxy_host+':'+ktv_proxy_port,
		'https': 'http://'+proxy_auth+ktv_proxy_host+':'+ktv_proxy_port,
		}

def login_or_none():
	cookiejar = requests.cookies.RequestsCookieJar()
	values = {'username': ktv_login, 'password':ktv_password}
	s = requests.Session()
	r = s.post(siteurl + "/takelogin.php",data=values,cookies=cookiejar,headers=headers,proxies=ktv_proxy,timeout=60)
	getted=True
	cookiejar.update(s.cookies)
	for cook in cookiejar:
		if cook.name=='pass':
			getted=True
			break
	if getted is None:
		return  None
	else:
		return cookiejar

if not ktv_cookies_uid or not ktv_cookies_pass:
	getted=None
	cookiejar = login_or_none()
	if cookiejar:
		for cook in cookiejar:
			if cook.name=='uid': ktv_cookies_uid=cook.value
			if cook.name=='pass': ktv_cookies_pass=cook.value
			if cook.name=='pass': getted=True
	if getted:
		__addon__.setSetting('cookies_pass',ktv_cookies_pass)
		__addon__.setSetting('cookies_uid',ktv_cookies_uid)
	else: 
		showMessage('Ошибка','Не верен логин или пароль', 5000)   
		__addon__.openSettings()
try:
	import json
except ImportError:
	try:
		import simplejson as json
		xbmc.log( '[%s]: Error import json. Uses module simplejson' % addon_id, 2 )
	except ImportError:
		try:
			import demjson3 as json
			xbmc.log( '[%s]: Error import simplejson. Uses module demjson3' % addon_id, 3 )
		except ImportError:
			xbmc.log( '[%s]: Error import demjson3. Sorry.' % addon_id, 4 )

def construct_request(params):
	return '%s?%s' % (sys.argv[0], urllib.urlencode(params))

def GET(target, post = None, needlogin = False):
	try:
		if needlogin:
			cookiejar = login_or_none()
		else:
			cookiejar = None
		if post is None:
			r = requests.get(target,headers=headers,cookies=cookiejar,proxies=ktv_proxy,timeout=60)
		else:
			r = requests.post(target,data=post,headers=headers,cookies=cookiejar,proxies=ktv_proxy,timeout=60)
		http = r.content
		return http
	except Exception, e:
		xbmc.log( '[%s]: GET EXCEPT [%s]' % (addon_id, e), 4 )
		showMessage('Ошибка', e, 5000)

def open_settings(params):
	__addon__.openSettings()

def mainScreen(params):
	PlaceFolder('Закладки', {'func':'get_bookmarks'})
	PlaceFolder('Главная',{'func': 'get_main', 'link':siteurl + '/'})
	PlaceFolder('Топ раздач',{'func': 'get_top'})
	PlaceFolder('Новинки',{'func': 'get_top1', 'link':siteurl + '/novinki.php'})
	PlaceFolder('Раздачи',{'func': 'get_search','from_person':'0'})
	PlaceFolder('Персоны',{'func': 'get_person','from_add_person':'0'})
	PlaceFolder('Поиск раздач',{'func': 'get_customsearch'})
	PlaceFolder('История',{'func': 'get_history'})
	PlaceFolder('Настройки',{'func': 'open_settings'})
	xbmcplugin.endOfDirectory(hos)

def PlaceLink(title,params):
	li = xbmcgui.ListItem(title)
	uri = construct_request(params)
	xbmcplugin.addDirectoryItem(hos, uri, li, False)
	
def get_custom(params):
	try:
		par=int(params['par'])
	except:
		par=None

	iwhere=int(__addon__.getSetting('where'))
	ishow=int(__addon__.getSetting('show'))
	iform=int(__addon__.getSetting('form'))
	ifilter=int(__addon__.getSetting('filter'))
	isorting=int(__addon__.getSetting('sorting'))
	dialog = xbmcgui.Dialog()
	if par==1:
		iwhere=dialog.select('Искать в', where)
	if par==2:
		ishow=dialog.select('Фильтр', show)
	if par==3:
		iform=dialog.select('Формат', form)
	if par==4:
		ifilter=dialog.select('Фильтр', filter)
	if par==5:
		isorting=dialog.select('Сортировка', sorting)

	__addon__.setSetting('where',str(iwhere))
	__addon__.setSetting('show',str(ishow))
	__addon__.setSetting('form',str(iform))
	__addon__.setSetting('filter',str(ifilter))
	__addon__.setSetting('sorting',str(isorting))
	xbmc.executebuiltin('Container.Refresh(%s?func=get_customsearch)' % sys.argv[0])

def get_person_search(params):
	keyboard = xbmc.Keyboard('','Поиск персоны')
	keyboard.doModal()
	if (keyboard.isConfirmed() == False):
		return
	http = human(GET(siteurl + '/personsearch.php?s=' + urllib.quote_plus(keyboard.getText())))
	http = http.replace('class="prs2"','class="prs"')
	f = '<div class="prs">'
	if f not in http:
		showMessage('Не найдено','Персоны не найдены')
		return
	http = http[http.find(f) + len(f):]
	http = http[:http.find('</div>')]
	all = BeautifulSoup(http)
	if all == None:
		return
	all = all.findAll('a')
	L = [[],[]]
	for aa in all:
		tit = aa.get('title')
		pu = aa.get('href')
		pu = pu.split('=')[2]
		#pi = aa.find('img').get('src')
		#li = xbmcgui.ListItem(tit,tit,pi,pi)
		L[0].append(tit)
		L[1].append(pu)

	dialog = xbmcgui.Dialog()
	ret = dialog.select('Найдено персон', L[0])
	if ret == -1:
		return
	http = GET(siteurl + '/bookmarks.php?type=4&add=' + L[1][ret],None,True)
	xbmc.executebuiltin("Container.Refresh")

def get_person_film_adv(ss,http):
	f = ss + '</div><div class=pad10x10>'
	http = http[http.find(f) + len(f):]
	http = http[:http.find('<div class="bx1">')-13]
	http = re.sub('\r\n', '', http)
	L = http.split('<br />')
	a = ["(сериал)", "(короткометражный)", "(ТВ)", "(видео, короткометражный)","(видео)"]
	for i in L:
		i = i.strip()
		if any(name in i[4:5] for name in (' ', '	')):
			year = i[0:13]
			if "–" in year.replace(' ','')[0:7]:
				if "..." in year:
					year = i[0:12]
			else:
				year = i[0:5]

			name = i[len(year):]
			serial = ''
			for s in a:
				if s in name:
					name = name.replace(' ' + s,'')
					serial = s + ' ';
			whom = ''
			idx = name.find("...")
			if idx > 0: whom = name[idx+3:].strip()
			name = name.replace("... " + whom,'')
			if whom != '': whom = '(%s)' % whom.replace('...','').strip()
			L1 = name.split('/')
			rname = ''
			oname = ''
			if len(L1) > 1:
				rname = L1[0].strip()
				oname = PrepareStr(L1[1].strip())
			else: 
				rname = name.strip()
			rname = PrepareStr(rname)
			pn = '[COLOR=FFDDDDDD]%s %s(%s)[/COLOR]\r\n[COLOR=FF008BEE]%s %s[/COLOR]\r\n' % (rname,serial,year.strip(),oname,whom)
			li = xbmcgui.ListItem(pn,pn,addon_icon,addon_icon)
			if oname == '': oname = rname;
			idx = oname.find('(')
			if idx > 0:
				oname = oname[0:idx].strip()
			uri = construct_request({
				'sname': oname,
				'syear': year[0:4],
				'from_person': '1',
				'func': 'get_search'
			})
			xbmcplugin.addDirectoryItem(hos, uri, li, True)

def get_person_film(params):
	http = human(GET(siteurl + '/' + params['url']))
	uri = construct_request({
		'func': 'get_search'
	})
	if 'Фильмография</div>' in http:
		s = 'Фильмография'
		li = xbmcgui.ListItem('------------ [UPPERCASE]' + s + '[/UPPERCASE] ------------')
		xbmcplugin.addDirectoryItem(hos,uri,li,False)
		get_person_film_adv(s,http)
	if 'Режиссер</div>' in http:
		s = 'Режиссер'
		li = xbmcgui.ListItem('------------ [UPPERCASE]' + s + '[/UPPERCASE] ------------')
		xbmcplugin.addDirectoryItem(hos,uri,li,False)
		get_person_film_adv(s,http)

	xbmcplugin.setContent(int(sys.argv[1]), 'movies')
	xbmcplugin.endOfDirectory(hos)
	xbmc.executebuiltin('Container.SetViewMode(%s)' % 51)

def get_person_info(params):
	http = human(GET(siteurl + '/' + params['url']))
	f = '<div class=b><span class="bulet"></span>Краткая биография</div>'
	http = http[http.find(f) - 17:]
	http = http[:http.find('<div class="clear"></div></div>')]
	http = http.replace('	',' ')
	if (http == None):
		showMessage("Ошибка", "Информация не найдена")
		return	
	replacements = [('\r\n',''),('</b><br /><br />','[/B]\r\n'),('<div class=b><span class="bulet"></span>','[B]\r\n'),('</div><div class=pad10x10>','[/B]\r\n'),
					(r'<div.*?>', ''), ('</div>', ''),(r'<a .*?>',''),('</a>',''),('<br />','\r\n'),('<b>','[B]'),('</b>','[/B]')]
	for pat,repl in replacements:
		http = re.sub(pat, repl, http)
	http = re.sub(r'<div.*?>', '', http)
	dialog = xbmcgui.Dialog()
	dialog.textviewer('Информация о персоне ' + params['name'], http)

def get_person(params):
	if params['from_add_person'] == '2':
		http = GET(siteurl + '/' + params['urldel'],None,True)
		xbmc.executebuiltin("Container.Refresh")
	http = human(GET(siteurl + '/bookmarks.php?type=4',None,True))
	all = BeautifulSoup(http)
	li = xbmcgui.ListItem('Добавить персону')
	uri = construct_request({
		'func': 'get_person_search',
	})
	xbmcplugin.addDirectoryItem(hos, uri, li, True)
	for div in all.findAll('div', attrs={'class':'bx5x5'}):
		nn = div.find('a',attrs = {'class': 'sbab'}).text
		pb = div.findAll('li')[1].text
		pn = '[COLOR=FFDDDDDD]%s[/COLOR]\r\n[COLOR=FF008BEE]%s[/COLOR]\r\n' % (nn,pb.replace('Дата рождения:',''))
		pi = div.find('img').get('src')
		pu = div.findAll('a')[1].get('href')
		pd = div.findAll('a')[0].get('href')
		li = xbmcgui.ListItem(pn, pn, pi, pi)
		menulist = []
		uri = construct_request({
			'name': nn,
			'func': 'get_person_info',
			'url': pu
		})
		menulist.append(('Информация о персоне', 'XBMC.RunPlugin(%s)' % uri))
		uri = construct_request({
			'from_add_person': '2',
			'urldel': pd,
			'func': 'get_person'
		})
		menulist.append(('Удалить из персон', 'XBMC.RunPlugin(%s)' % uri))
		uri = construct_request({
			'from_person': '2',
			'sname': nn,
			'func': 'get_search'
		})
		menulist.append(('Top раздач персоны', 'Container.Update(%s)' % uri))
		li.addContextMenuItems(menulist)
		uri = construct_request({
			'name': nn,
			'url': pu,
			'func': 'get_person_film'
		})
		xbmcplugin.addDirectoryItem(hos, uri, li, True)
	xbmcplugin.setContent(int(sys.argv[1]), 'movies')
	xbmcplugin.endOfDirectory(hos)
	xbmc.executebuiltin('Container.SetViewMode(%s)' % 51)

def get_history(params):
	http = human(GET(siteurl + '/hytorrents.php',None,True))
	f = '<td class="z">Залит</td></tr>'
	http = http[http.find(f) + len(f) + 1:]
	http = http[:http.find('</table></div>')]
	http = http.replace("class='first bg'","class='bg'")
	all = BeautifulSoup(http)
	for tr in all.findAll('tr', attrs={'class':'bg'}):
		ss = tr.find('td',attrs = {'class': 'sl_s'}).text
		sp = tr.find('td',attrs = {'class': 'sl_p'}).text
		sz = tr.findAll('td',attrs = {'class': 's'})[1].text
		gg = tr.find('a')['class']
		color = 'FFDDDDDD'
		if gg == 'r1': color = 'FFDCAF35'
		elif gg == 'r2': color = 'FFA0A7AD'
		elif gg == 'r5': color = 'maroon'		
		title = tr.find('a').contents[0]
		title = "[COLOR " + color + "]%s[/COLOR]" % (title)
		title = '%s\r\n[COLOR=FF008BEE](peers: %s seeds: %s size: %s)[/COLOR]' % (title, sp, ss, sz)
		url = tr.find('a')['href']
		li = xbmcgui.ListItem(title, title)
		menulist = []
		infouri = construct_request({
			'func': 'get_info2',
			'url': siteurl + "/" + url
		})
		commuri = construct_request({
			'func': 'get_comm',
			'url': siteurl + "/" + url
		})
		menulist.append(('Информация о раздаче', 'XBMC.RunPlugin(%s)' % infouri))
		menulist.append(('Комментарии', 'XBMC.RunPlugin(%s)' % commuri))
		li.addContextMenuItems(menulist)
		uri = construct_request({
			'func': 'get_info',
			'url': siteurl + "/" + url
		})
		xbmcplugin.addDirectoryItem(hos, uri, li, True)
	xbmcplugin.setContent(int(sys.argv[1]), 'movies')
	xbmcplugin.endOfDirectory(hos)
	xbmc.executebuiltin('Container.SetViewMode(%s)' % 51)
	
def get_customsearch(params):
	
	try:
		par = int(params['par'])
	except:
		par=None

	PlaceLink('Искать в %s'%where[iwhere],{'func': 'get_custom', 'par':'1'})
	PlaceLink('Искать %s'%show[ishow],{'func': 'get_custom', 'par':'2'})
	PlaceLink('Формат: %s'%form[iform],{'func': 'get_custom', 'par':'3'})
	PlaceLink('Фильтр: %s'%filter[ifilter],{'func': 'get_custom', 'par':'4'})
	PlaceLink('Сортровка: %s'%sorting[isorting],{'func': 'get_custom', 'par':'5'})
	PlaceLink('Год: %s' % iyear, {'func': 'get_querry', 'par':'year'})
	PlaceLink('Искать: %s'%querry,{'func': 'get_querry'})
	PlaceFolder('Поиск',{'func': 'get_search','s':'1','from_person':'0'})
	xbmcplugin.endOfDirectory(hos)   

def get_querry(params):
	import datetime
	if params.has_key("par"):
		iyear = __addon__.getSetting("year")
		if iyear == '':
			iyear = datetime.date.today().year
		
		iyear = xbmcgui.Dialog().numeric(int(iyear),'Год')
		
		if iyear == '':
			iyear = ""
		elif int(iyear) < 1900:
			iyear = 1900
		elif int(iyear) > int(datetime.date.today().year):
			showMessage('', '%s > %s' % (iyear, datetime.date.today().year))
			iyear = datetime.date.today().year
		__addon__.setSetting('year', str(iyear))
		
	else:	
		skbd = xbmc.Keyboard()
		skbd.setHeading('Поиск:')
		skbd.doModal()
		if skbd.isConfirmed():
			SearchStr = skbd.getText()
			params['search']=SearchStr.replace(' ','+').decode('utf-8').encode('cp1251')
		else:
			params['search']=''
		__addon__.setSetting('querry',str(SearchStr))
	xbmc.executebuiltin('Container.Refresh(%s?func=get_customsearch)' % sys.argv[0])
def PlaceFolder(title,params):
	li = xbmcgui.ListItem(title)
	uri = construct_request(params)
	xbmcplugin.addDirectoryItem(hos, uri, li, True)
	
def check_item_by_tytle(title):
	if ("ALAC" in title) or ("Lossless" in title) or ("FLAC" in title):
		return False
	else:
		return True

def get_main(params):
	http = GET(params['link'])
	beautifulSoup = BeautifulSoup(http)
	all = beautifulSoup.find('div',attrs={'class':'tp1_border'})
	cont = all.findAll('div',attrs={'class':'tp1_body'})
	for film in cont: 
		title = PrepareStr(film.find('a')['title'])
		if not check_item_by_tytle(title):
			continue
		img= film.find('a').find('img')['src']
		if 'http' not in img: img = imgurl + '/%s'%img
		lik =  str(film.find('a')['href']).split('=')
		torrlink = siteurl + '/download.php/%s/[kinozal.tv]id%s.torrent'%(lik[1],lik[1])
		info = {}
		desc = '%s' % film.find('div', attrs={'class':'tp1_desc1'})
		genre = desc[desc.find("<b>Жанр:</b>")+17:]
		genre = genre[:genre.find("<br />")]
		year = desc[desc.find("<b>Год выпуска:</b>") + 30:]
		year = year[:year.find("<br />")]
		director = desc[desc.find("<b>Режиссер:</b>") + 25:]
		director = director[:director.find("<br />")]
		xinfos = film.find('div', attrs={'class':'tp1_desc'}).findAll('div')
		plot = "";
		for xdesc in xinfos:
			for tag in xdesc.contents:
				if tag.__class__.__name__ == 'NavigableString':
					plot = plot + '%s' % tag
				elif tag.name == 'b':
					plot = plot + '[B]' + tag.getText() + '[/B]'
				elif tag.name == 'br':
					plot = plot + '\r'

		info["genre"] = genre
		info["year"] = year
		info["plot"] = plot
		info["plotoutline"] = plot
		info["title"] = title
		info["director"] = director

		li = xbmcgui.ListItem(title,title,img,img)
		li.setProperty('fanart_image', img)
		li.setInfo(type = "video", infoLabels = info)
		uri = construct_request({
			'func': 'get_info',
			'url': siteurl + "/" + film.find('a')["href"]
		})
		xbmcplugin.addDirectoryItem(hos, uri, li, True)
	xbmcplugin.endOfDirectory(hos)
	xbmc.executebuiltin('Container.SetViewMode(%s)' % 504)

def get_view_mode():
		view_mode = ""
		controls = (50,51,500,501,508,503,504,515,505,511,550,551,560)
		for id in controls:
			try:
				if xbmc.getCondVisibility( "Control.IsVisible(%i)" % id ):
					view_mode = id
					return view_mode
					break
			except:
				pass
		return view_mode

def get_plot(container):
	plot = ""
	for tag in container.contents:
		if tag.__class__.__name__ == 'NavigableString':
			plot = plot + '%s' % PrepareStr(tag)
		elif tag.name == 'b':
			plot = plot + '[B]' + tag.getText() + '[/B]'
		elif tag.name == 'br':
			plot = plot + '\r'
		elif tag.name == 'a':
			plot = plot + '[I]' + tag.getText() + "[/I]"
	
	return plot

def get_detail_torr_1(container):
	tds = container.findAll('td')
	sp = tds[3].getText() + "/" + tds[4].getText()
	title = '[%s]%s' % (sp, tds[0].getText())
	if tds[0].a['class'] == 'r1':
		title = '[COLOR=FFDCAF35]%s[/COLOR]' % title
	elif tds[0].a['class'] == 'r2':
		title = '[COLOR=FFF0A7AD]%s[/COLOR]' % title
	else:
		title = '[COLOR=FFDDDDDD]%s[/COLOR]' % title
	dict = {}
	dict['sp'] = sp
	dict['title'] = title
	dict['url'] = tds[0].a['href']
	return dict

def get_detail_torr_2(container):
	tds = container.findAll('td')
	sp = tds[4].getText() + "/" + tds[5].getText()
	title = '[%s]%s' % (sp, tds[1].getText())
	if tds[1].a['class'] == 'r1':
		title = '[COLOR=FFDCAF35]%s[/COLOR]' % title
	elif tds[1].a['class'] == 'r2':
		title = '[COLOR=FFF0A7AD]%s[/COLOR]' % title
	else:
		title = '[COLOR=FFDDDDDD]%s[/COLOR]' % title
	dict = {}
	dict['sp'] = sp
	dict['title'] = title
	dict['url'] = tds[1].a['href']
	return dict

def get_detail_torr3(container):
	tds = container.findAll('td')
	sp = tds[5].getText() + "/" + tds[6].getText()
	title = '[%s]%s' % (sp, tds[1].getText())
	if tds[1].a['class'] == 'r1':
		title = '[COLOR=FFDCAF35]%s[/COLOR]' % title
	elif tds[1].a['class'] == 'r2':
		title = '[COLOR=FFF0A7AD]%s[/COLOR]' % title
	else:
		title = '[COLOR=FFDDDDDD]%s[/COLOR]' % title
	dict = {}
	dict['sp'] = sp
	dict['title'] = title
	dict['url'] = tds[1].a['href']
	return dict

def get_by_genre(img, info, id):
	lis = []
	detail = GET(siteurl + '/ajax/details_get.php?id=%s&sr=101' % id) 
	bsdetail = BeautifulSoup(detail.decode('cp1251'))
	xdetails = bsdetail.findAll('tr', attrs={'class':'first'})

	for xdet in xdetails:
		det = get_detail_torr_1(xdet)
		sp = det['sp']
		title = det['title']
		url = det['url']
		li = xbmcgui.ListItem(PrepareStr(title))
		li.setProperty('fanart_image', img)
		li.setInfo(type='video', infoLabels=info)
		dict = {}
		dict['li'] = li
		dict['folder'] = True
		uri = construct_request({
			'func': 'get_info',
			'url': siteurl + "/" + url
		})
		dict['url'] = uri
		dict['id'] = ''
		lis.append(dict)
	return lis

def get_by_persone(img,info, id):
	lis = []
	detail = GET(siteurl + '/ajax/details_get.php?id=%s&sr=102' % id) 
	bsdetail = BeautifulSoup(detail.decode('cp1251'))
	xdetails = bsdetail.findAll('tr')
	xdetails = xdetails[1:]
	for xdet in xdetails:
		det = get_detail_torr_2(xdet)
		sp = det['sp']
		title = det['title']
		url = det['url']
		li = xbmcgui.ListItem(PrepareStr(title))
		li.setProperty('fanart_image', img)
		li.setInfo(type='video', infoLabels=info)
		dict = {}
		dict['li'] = li
		dict['folder'] = True
		uri = construct_request({
			'func': 'get_info',
			'url': siteurl + "/" + url
		})
		dict['url'] = uri
		dict['id'] = ''
		lis.append(dict)
	return lis

def get_by_seed(img, info, id):
	lis = []
	detail = GET(siteurl + '/ajax/details_get.php?id=%s&sr=103' % id) 
	bsdetail = BeautifulSoup(detail.decode('cp1251'))
	xdetails = bsdetail.findAll('tr')
	xdetails = xdetails[1:]
	for xdet in xdetails:
		det = get_detail_torr_2(xdet)
		sp = det['sp']
		title = det['title']
		url = det['url']
		li = xbmcgui.ListItem(PrepareStr(title))
		li.setProperty('fanart_image', img)
		li.setInfo(type='video', infoLabels=info)
		dict = {}
		dict['li'] = li
		dict['folder'] = True
		uri = construct_request({
			'func': 'get_info',
			'url': siteurl + "/" + url
		})
		dict['url'] = uri
		dict['id'] = ''
		lis.append(dict)
	return lis

def get_by_like(container, img, info, id):
	lis = []
	for torr in container.div.table.contents:
			if torr['class'] == 'mn':
				continue
			detail = get_detail_torr_1(torr)
			sp = detail['sp']
			title = detail['title']
			url = detail['url']

			li = xbmcgui.ListItem(PrepareStr(title))
			li.setProperty('fanart_image', img)
			li.setInfo(type='video', infoLabels=info)
			dict = {}
			dict['li'] = li
			dict['folder'] = True
			uri = construct_request({
				'func': 'get_info',
				'url': siteurl + "/" + url
			})
			dict['url'] = uri
			dict['id'] = ''
			lis.append(dict)
	return lis

def get_info2(params):  
	http = GET(params["url"])
	beautifulSoup = BeautifulSoup(http)
	all = beautifulSoup.find('div',attrs={'class':'mn_wrap'})

	if (all == None):
		showMessage("Ошибка", "Информация не найдена")
		return

	xinfo = all.find('div', attrs={'class':'mn1_content'}).findAll('div', attrs={'class' : 'bx1 justify'})
	if xinfo.__len__() == 4:
		xinfo = xinfo[2:]
	elif xinfo.__len__() > 2:
		xinfo = xinfo[1:]

	plot = "";
	plot = get_plot(xinfo[0].h2)
	plot = plot + '\n' + get_plot(xinfo[1].p)
	tech = all.find('div', attrs={'class':'justify mn2 pad5x5'})
	plot = plot + '\n' + get_plot(tech)
	dialog = xbmcgui.Dialog()
	dialog.textviewer('Информация о раздаче', plot)

def get_comm(params):  
	http = GET(params["url"])
	beautifulSoup = BeautifulSoup(http)

	if (all == None):
		showMessage("Ошибка", "Информация не найдена")
		return

	cms = beautifulSoup.findAll("div", attrs={'class': 'mn2 cmet_bx'})

	plot = ""
	for cmsa in cms: 
		plot = plot + '[COLOR red]' + get_plot(cmsa.a) + '[/COLOR]' + '\r\n' + get_plot(cmsa.find('div', attrs={'class':'tx'})).replace('\n',' ').replace('\r','') + '\r\n'
	dialog = xbmcgui.Dialog()
	dialog.textviewer('Комментарии', PrepareStr(plot))

def get_soup(http):
	beautifulSoup = BeautifulSoup(http)
	http = beautifulSoup.find('div',attrs={'class':'mn_wrap'})
	return http

def get_info(params):
	http = GET(params["url"])
	all = get_soup(http)

	if (all == None):
		http = GET(params["url"],None,True)
		all = get_soup(http)

	if (all == None):
		showMessage("Ошибка", "Торрент не найден")
		return

	img = all.find('img',attrs={'class':"p200"})["src"]
	if 'http' not in img: 
		img = imgurl + '%s'%img
	menu = all.find('ul', attrs={"class": "men w200"})
	mitems = menu.findAll('a')
	sp = "";
	fc = 1;
	bookmark = None
	for link in mitems:
		if "Раздают" in link.getText().encode('utf-8'):
			sp = link.find('span', attrs={'class': 'floatright'}).getText()
		elif 'Скачивают' in link.getText().encode('utf-8'):
			sp =  sp + '/' + link.find('span', attrs={'class': 'floatright'}).getText()
		elif "Список файлов" in link.getText().encode('utf-8'):
			fc = int(link.span.getText())
		elif "Добавить в закладки" in link.getText().encode('utf-8'):
			bookmark = link['href']

	star = menu.find('div', attrs={'class' : 'starbar'}).findAll('a')
	tag_title = None
	for tag in all.contents:
		if (tag.name == "div"):
			tag_title = tag
			break;
	fname = PrepareStr(tag_title.h1.a.getText().encode('utf-8'))
	title = "[COLOR=FF008BEE][%s][%s]%s[/COLOR]" % (star.__len__(),sp.encode('utf-8'),fname)
	id = params["url"].split('=')[urlpos]
	link = siteurl + '/download.php?id=%s' % id
	xinfo = all.find('div', attrs={'class':'mn1_content'}).findAll('div', attrs={'class' : 'bx1 justify'})
	isBlock = False
	if xinfo.__len__() == 4:
		isBlock = True
		title = '[COLOR=FFFF0000]%s[/COLOR]' % xinfo[0].b.getText()
		xinfo = xinfo[2:]
	elif xinfo.__len__() > 2:
		xinfo = xinfo[1:]
	sinfo = '%s' % xinfo[0]
	info = {}
	year = sinfo[sinfo.find('<b>Год выпуска:</b>')+30:]
	year = year[:year.find('<br />')].strip()
	genre = sinfo[sinfo.find('<b>Жанр:</b>') + 16:]
	genre = genre[:genre.find('<br />')].strip()
	ser = sinfo[sinfo.find('onclick="cat(') + 13:]
	ser = ser[:ser.find(')')].strip()
	ser = (ser == '45') or (ser == '46')
	info['year'] = year
	info['genre'] = genre
	plot = "";
	plot = get_plot(xinfo[0].h2)
	plot = plot + '\n' + get_plot(xinfo[1].p)
	tech = all.find('div', attrs={'class':'justify mn2 pad5x5'})
	plot = plot + '\n' + get_plot(tech)
	plot = plot.replace('[B]Год выпуска:[/B] ' + year + '\r\n','')
	plot = plot.replace('[B]Жанр:[/B] ' + genre + '\r\n','')
	info['plot'] = plot
	li = xbmcgui.ListItem(title, title, img, img)
	li.setProperty('fanart_image', img)
	info["title"] = fname
	info["cover"] = img
	li.setInfo(type = "Video", infoLabels=info)
	if isBlock:
		uri = ''
	else:
		uri = construct_request(
			{
				'func' : "play_torrent",
				'torr_id' : id,
				'img' : img
			})
	if (fc == 1) or not ser:
		li.setProperty('IsPlayable', 'true')

	menulist = []
	if bookmark:
		addbookmarkuri = construct_request({
			'func': 'http_request',
			'url': siteurl + "/" + bookmark
		})
		menulist.append(('[COLOR FF669933]Добавить[/COLOR][COLOR FFB77D00] в Закладки[/COLOR]', 'XBMC.RunPlugin(%s)' % (addbookmarkuri)))
	
	downloaduri = construct_request({
		'func': 'download',
		'url' : link,
		'filename' : '[kinozal.tv]id%s.torrent' % id
	})
	menulist.append(('[COLOR FF669933]Скачать[/COLOR]', 'XBMC.RunPlugin(%s)' % downloaduri))
	li.addContextMenuItems(menulist)
	li.select(True)
	xbmcplugin.addDirectoryItem(hos, uri, li, (fc > 1) and ser)

	all = all.find('div', attrs={'class':'mn1_content'})
	bx1 = all.findAll('div', attrs={'class':'bx1'})
	bx1 = bx1[2]
	lis = []
	for tabs in bx1.div.ul.contents:
		dict = {}
		li = xbmcgui.ListItem(PrepareStr(tabs.getText().upper().center(32,'-')))

		li.setProperty('fanart_image', img)
		li.setInfo(type='video', infoLabels=info)
		
		dict['li'] = li
		dict['folder'] = False
		dict['url'] = ''
		dict['id'] = tabs['id']
		lis.append(dict)

	bx20 = bx1.find('div', attrs={'class': 'justify mn2'})
	lis_like = []
	if (bx20.div.table != None):
		lis_like = get_by_like(bx20, img, info, id)
	lis_genre = get_by_genre(img, info, id)
	lis_persone = get_by_persone(img, info, id)
	lis_seed = get_by_seed(img, info, id)

	for li1 in lis:
		xbmcplugin.addDirectoryItem(hos, li1['url'], li1['li'], li1['folder'])
		if li1['id'].find('100') > 0:
			for li2 in lis_like:
				xbmcplugin.addDirectoryItem(hos, li2['url'], li2['li'], li2['folder'])
		elif li1['id'].find('101') > 0:
			for li2 in lis_genre:
				xbmcplugin.addDirectoryItem(hos, li2['url'], li2['li'], li2['folder'])
		elif li1['id'].find('102') > 0:
			for li2 in lis_persone:
				xbmcplugin.addDirectoryItem(hos, li2['url'], li2['li'], li2['folder'])
		elif li1['id'].find('103') > 0:
			for li2 in lis_seed:
				xbmcplugin.addDirectoryItem(hos, li2['url'], li2['li'], li2['folder'])
	xbmcplugin.setContent(int(sys.argv[1]), 'movies')
	xbmcplugin.endOfDirectory(hos)
	xbmc.executebuiltin('Container.SetViewMode(%s)' % 504)

def get_search(params):
	try:
		if params['from_person'] == '2':
			qu = params['sname']
			link = siteurl + '/browse.php?s=%s&g=1&t=1' % (urllib.quote_plus(qu))
		elif params['from_person'] == '1':
			qu = params['sname']
			iyear = params['syear']
			link = siteurl + '/browse.php?s=%s&d=%s&t=1' % (urllib.quote_plus(qu),iyear)
		else:
			if params.has_key('s'):
				g = int(__addon__.getSetting('where'))
				c = cshow[ishow]
				v = cform[iform]
				w = cfilter[ifilter]
				t = csorting[isorting]
				qu = querry.decode('utf-8').encode('cp1251')
				iyear = __addon__.getSetting('year')
			else:
				g = 0
				c = 0
				v = 0
				w = 0
				t = 0
				qu = ""
				iyear = "0"
			link = siteurl + '/browse.php?s=%s&g=%s&c=%s&v=%s&d=%s&w=%s&t=%s&f=0'%(urllib.quote_plus(qu),g,c,v,iyear,w,t)
	except Exception, e:
		return
		link = siteurl + '/browse.php?s=&g=0&c=0&v=0&d=0&w=0&t=0&f=0'
	http = GET(link)
	beautifulSoup = BeautifulSoup(http)
	cat = beautifulSoup.findAll('tr')
	leng = len(cat)
	for film in cat:
		try:
			size = film.findAll('td', attrs={'class':'s'})[1].string
			peers = film.findAll('td', attrs={'class':'sl_s'})[0].string
			seeds = film.findAll('td', attrs={'class':'sl_p'})[0].string
			xa = film.find('td', attrs={'class':'nam'}).find('a')
			title = PrepareStr(xa.string)
			if xa['class'] == 'r1':
				title = '[COLOR=FFDCAF35]%s[/COLOR]' % title
			elif xa['class'] == 'r2':
				title = '[COLOR=FFA0A7AD]%s[/COLOR]' % title
			else:
				title = '[COLOR=FFDDDDDD]%s[/COLOR]' % title
			link = xa['href']
			lik = link.split('=')
			#glink=siteurl + '%s'%link
			#data= GET(glink)
			#dataSoup = BeautifulSoup(data)
			#img= dataSoup.find('li', attrs={'class':'img'}).find('img')['src']
			#if 'http' not in img: img=siteurl + '%s'%img
			img = addon_icon
			torrlink = siteurl + '/download.php/%s/[kinozal.tv]id%s.torrent'%(lik[1],lik[1])
			li = xbmcgui.ListItem('%s\r\n[COLOR=FF008BEE](peers: %s seeds: %s size%s)[/COLOR]'%(title,peers,seeds,size),addon_icon,img)
			li.setProperty('fanart_image', img)
			#uri = construct_request({
			#	'func': 'play',
			#	'torr_url':torrlink,
			#	'filename':'[kinozal.tv]id%s.torrent'%lik[1],
			#	'img':addon_icon,
			#	'title':title
			#})
			menulist = []
			infouri = construct_request({
				'func': 'get_info2',
				'url': siteurl + "/" + xa["href"]
			})
			menulist.append(('Информация о раздаче', 'XBMC.RunPlugin(%s)' % infouri))
			li.addContextMenuItems(menulist)
			uri = construct_request({
				'func': 'get_info',
				'url': siteurl + "/" + xa["href"]
			})
			xbmcplugin.addDirectoryItem(hos, uri, li, True, totalItems=leng)
		except: pass
	xbmcplugin.endOfDirectory(hos)
	xbmc.executebuiltin('Container.SetViewMode(%s)' % 51)

def get_years(params):
	http = GET(siteurl + '/top.php')
	beautifulSoup = BeautifulSoup(http)
	years = beautifulSoup.find('select',attrs={"class":"w100 styled"})
	years = years.findAll('option')

	for n in years:
		li = xbmcgui.ListItem(n.string.encode('utf-8'),addon_icon,addon_icon)
		uri = construct_request({
			'func': 'get_top1',
			'link':siteurl + '/top.php?w=0&t=%s&d=%s&f=0&s=0' % (params['genre'], n['value'])
		})
		xbmcplugin.addDirectoryItem(hos, uri, li, True)
	xbmcplugin.endOfDirectory(hos)

def get_top(params):
	http = GET(siteurl + '/top.php')
	beautifulSoup = BeautifulSoup(http)
	cat = beautifulSoup.find('select',attrs={"class":"w100p styled"})
	cat = cat.findAll('option')

	for n in cat:
		if int(n['value']) not in [5,6,7,8,4,41,42,43,44]:
			li = xbmcgui.ListItem(n.string.encode('utf-8'),addon_icon,addon_icon)
			uri = construct_request({
				'func': 'get_years',
				'genre': n['value']
			})

			xbmcplugin.addDirectoryItem(hos, uri, li, True)
	xbmcplugin.endOfDirectory(hos)
  
def get_top1(params):
	http = GET(params['link'])
	beautifulSoup = BeautifulSoup(http)
	content = beautifulSoup.find('div', attrs={'class': 'bx1 stable'})
	cats=content.findAll('a')
	for m in cats: 
		tit = PrepareStr(m['title'])
		lik = str(m['href']).split('=')
		img = m.find('img')['src']
		if 'http' not in img: img = imgurl + '%s'%img
		#torrlink = siteurl + '/download.php/%s/[kinozal.tv]id%s.torrent'%(lik[1],lik[1])

		li = xbmcgui.ListItem(tit,addon_icon,img)
		li.setProperty('fanart_image', img)
		
		menulist = []
		infouri = construct_request({
			'func': 'get_info2',
			'url': siteurl + "/" + m['href']
		})
		commuri = construct_request({
			'func': 'get_comm',
			'url': siteurl + "/" + m['href']
		})
		menulist.append(('Информация о раздаче', 'XBMC.RunPlugin(%s)' % infouri))
		menulist.append(('Комментарии', 'XBMC.RunPlugin(%s)' % commuri))
		li.addContextMenuItems(menulist)
		uri = construct_request({
			'func': 'get_info',
			'url': siteurl + "/" + m['href']
		})
		xbmcplugin.addDirectoryItem(hos, uri, li, True)
	xbmcplugin.endOfDirectory(hos)
	xbmc.executebuiltin('Container.SetViewMode(%s)' % 500)
	

def http_request(params):
	http = GET(params['url'],None,True)
	return http

def del_bookmark(params):
	http_request(params)
	xbmc.executebuiltin("Container.Refresh")

def get_bookmarks(params):
	http = GET(siteurl + '/bookmarks.php?type=1',None,True)
	beautifulSoup = BeautifulSoup(http)
	bx20 = beautifulSoup.find('div', attrs={'class': 'content'}).find('div', attrs={'class':'bx2_0'});
	if bx20:
		table = bx20.table.findAll('tr');
		for line in table:
			if line.has_key('class') and line['class'] == 'mn':
				continue
			desc = get_detail_torr3(line)
			li = xbmcgui.ListItem(PrepareStr(desc['title']),addon_icon,addon_icon)
			uri = construct_request({
				'func': 'get_info',
				'url': siteurl + "/" + desc['url']
			})
			tds = line.findAll("td", attrs={'class': 's'})
			delbookmarkuri = construct_request({
				'func': 'del_bookmark',
				'url': siteurl + "/" + tds[tds.__len__()-1].a['href']
			})
			li.addContextMenuItems([('[COLOR FF669933]Удалить[/COLOR][COLOR FFB77D00] из Закладок[/COLOR]', 'XBMC.RunPlugin(%s)' % (delbookmarkuri),)])
			xbmcplugin.addDirectoryItem(hos, uri, li, True)
	xbmcplugin.endOfDirectory(hos)

def play_torrent(params):
	try:
		id = params['torr_id']
		fle = os.path.join(__addon__.getAddonInfo('path'),'torrents',id + '.torrent')
		if os.path.isfile(fle) and (__addon__.getSetting("use_save_torr") == 'true'):
			f = open(fle, "rb")
			torr_data = f.read()
		else:
			torr_data = GET(siteurl + '/download.php?id=%s' % id,None,True)
			if '<!DOCTYPE HTML>' in torr_data:
				showMessage('Ошибка','Проблема при скачивании (превышен лимит?)')
				return False
			f = open(fle, "wb")
			f.write(torr_data)
			f.close()

		if torr_data != None:
			import bencode
			dtorrent = bencode.bdecode(torr_data)
			try:
				L = dtorrent['info']['files']
			except:
				play(id,1)
				return

			tm = 0
			ind = 0
			cind= 0
			for i in L:
				name = i['path'][-1]
				if '.srt' not in name: 
					ind = cind
					tm += 1
				cind += 1

			if tm == 1: play(id,ind)
			elif tm > 1:
				ind = 0
				img = params["img"]
				for i in L:
					name = i['path'][-1]
					if name[-4:] != '.srt':
						li = xbmcgui.ListItem(name, iconImage=img, thumbnailImage=img)
						uri = construct_request({
						't': urllib.quote(fle),
						'tt': name.encode('utf-8'),
						'i':ind,
						'ii':urllib.quote(img),
						'func': 'addplist'
						})
						li.setProperty('IsPlayable', 'true')
						li.addContextMenuItems([('Добавить в плейлист', 'XBMC.RunPlugin(%s)' % uri),])
						li.setInfo(type = "Video", infoLabels = {'cover' : img, 'title' : name})
						uri = construct_request({
						'torr_id' : id,
						'ind' : ind,
						'func' : 'play_url'
						})
						xbmcplugin.addDirectoryItem(hos, uri, li)
					ind+=1
				xbmcplugin.addSortMethod(hos, xbmcplugin.SORT_METHOD_LABEL)
				xbmcplugin.setContent(int(sys.argv[1]), 'movies')
				xbmcplugin.endOfDirectory(hos)
	except Exception, e:
		showMessage('Ошибка',e)

def play_url(params):
	play(params["torr_id"],params["ind"])

def play(fle, ind):	
	fle = os.path.join(__addon__.getAddonInfo('path'),'torrents',fle + '.torrent')
	purl = "plugin://plugin.video.tam/?mode=play&url=" + urllib.quote_plus(fle) + "&ind=" + str(ind)
	item = xbmcgui.ListItem(path=purl)
	xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
	#xbmc.executebuiltin("Container.Refresh")

def debug(s):
	fl = open(os.path.join(__addon__.getAddonInfo('path'),"test.txt"), "a+")
	fl.write(s)
	fl.close()

def addplist(params):

	li = xbmcgui.ListItem(params['tt'])
	uri = construct_request({
		'torr_url': params['t'],
		'title': params['tt'].decode('utf-8'),
		'ind':urllib.unquote_plus(params['i']),
		'img':urllib.unquote_plus(params['ii']),
		'func': 'play_url'
	})
	xbmc.PlayList(xbmc.PLAYLIST_VIDEO).add(uri,li)

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
	if len(param) > 0:
		for cur in param:
			param[cur] = urllib.unquote_plus(param[cur])
	return param

params = get_params(sys.argv[2])
try:
	func = params['func']
	del params['func']
except:
	func = None
	xbmc.log( '[%s]: Primary input' % addon_id, 1 )
	mainScreen(params)

if func != None:
	try:
		pfunc = globals()[func]
	except:
		pfunc = None
		xbmc.log( '[%s]: Function "%s" not found' % (addon_id, func), 4 )
		showMessage('Internal addon error', 'Function "%s" not found' % func, 2000)
	if pfunc: pfunc(params)
