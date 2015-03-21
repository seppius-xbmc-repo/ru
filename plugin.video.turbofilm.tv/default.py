#!/usr/bin/python
# -*- coding: utf-8 -*-
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


import urllib, urllib2, cookielib, re, xbmcaddon, string, xbmc, xbmcgui, xbmcplugin, os, httplib, socket
import base64
import random
import sha


__settings__ = xbmcaddon.Addon(id='plugin.video.turbofilm.tv')
__language__ = __settings__.getLocalizedString
USERNAME = __settings__.getSetting('username')
USERPASS = __settings__.getSetting('password')
handle = int(sys.argv[1])

PLUGIN_NAME = 'Turbofilm.TV'
SITE_HOSTNAME = 'turbofilm.tv'
SITEPREF      = 'http://%s' % SITE_HOSTNAME
SITE_URL      = SITEPREF + '/'

phpsessid_file = os.path.join(xbmc.translatePath('special://temp/'), 'plugin_video_turbofilmtv.sess')
plotdescr_file = os.path.join(xbmc.translatePath('special://temp/'), 'plugin_video_turbofilmtv.plot')
thumb = os.path.join( os.getcwd(), "icon.png" )


def run_once():
	global USERNAME, USERPASS
	while (Get('/') == None):
		user_keyboard = xbmc.Keyboard()
		user_keyboard.setHeading(__language__(30001))
		user_keyboard.doModal()
		if (user_keyboard.isConfirmed()):
			USERNAME = user_keyboard.getText()
			pass_keyboard = xbmc.Keyboard()
			pass_keyboard.setHeading(__language__(30002))
			pass_keyboard.setHiddenInput(True)
			pass_keyboard.doModal()
			if (pass_keyboard.isConfirmed()):
				USERPASS = pass_keyboard.getText()
				__settings__.setSetting('username', USERNAME)
				__settings__.setSetting('password', USERPASS)
			else:
				return False
		else:
			return False
	return True

def Get(url, ref=None):
	use_auth = False
	inter = 2
	while inter:
		wurl = SITEPREF + url
		cj = cookielib.CookieJar()
		h  = urllib2.HTTPCookieProcessor(cj)
		opener = urllib2.build_opener(h)
		urllib2.install_opener(opener)
		post = None
		if use_auth:
			post = urllib.urlencode({'login': USERNAME, 'passwd': USERPASS})
			url = SITE_URL
		request = urllib2.Request(wurl, post)
		request.add_header('User-Agent', 'Opera/9.80 (X11; Linux i686; U; ru) Presto/2.6.30 Version/10.70')
		request.add_header('Host', SITE_HOSTNAME)
		request.add_header('Accept', 'text/html, application/xml, application/xhtml+xml, */*')
		request.add_header('Accept-Language', 'ru,en;q=0.9')
		if ref != None:
			request.add_header('Referer', ref)
		if (os.path.isfile(phpsessid_file) and (not use_auth)):
			fh = open(phpsessid_file, 'r')
			phpsessid = fh.read()
			fh.close()
			request.add_header('Cookie', 'IAS_ID=' + phpsessid)
		o = urllib2.urlopen(request)
		for index, cookie in enumerate(cj):
			cookraw = re.compile('<Cookie IAS_ID=(.*?) for.*/>').findall(str(cookie))
			if len(cookraw) > 0:
				fh = open(phpsessid_file, 'w')
				fh.write(cookraw[0])
				fh.close()
		http = o.read()
		o.close()
		if (http.find('<div class="loginblock" id="loginblock">') == -1):
			return http
		else:
			use_auth = True
			url = '/Signin/'
		inter = inter - 1
	return None

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

def ShowSeries(url):
	http = Get(url)
	if http == None:
		xbmc.output('[%s] ShowSeries() Error 1: Not received data when opening URL=%s' % (PLUGIN_NAME, url))
		return
	#xbmc.output(http)

	raw1 = re.compile('<div id="series">(.*?)<div id="footer">', re.DOTALL).findall(http)
	if len(raw1) == 0:
		xbmc.output('[%s] ShowSeries() Error 2: r.e. not found it necessary elements. URL=%s' % (PLUGIN_NAME, url))
		xbmc.output(http)
		return

	#xbmc.output(raw1[0])

	raw2 = re.compile('\s<a href="(.*?)">\s(.*?)</a>', re.DOTALL).findall(raw1[0])
	if len(raw1) == 0:
		xbmc.output('[%s] ShowSeries() Error 3: r.e. not found it necessary elements. URL=%s' % (PLUGIN_NAME, url))
		xbmc.output(raw1[0])
		return

	x = 1;
	for wurl, http2 in raw2:

		raw_img = re.compile('<img src="(.*?)".*/>').findall(http2)
		if len(raw_img) == 0:
			Thumb = thumb
		else:
			Thumb = SITEPREF + raw_img[0]
		raw_en = re.compile('<span class="serieslistboxen">(.*?)</span>').findall(http2)
		if len(raw_en) == 0:
			TitleEN = 'No title'
		else:
			TitleEN = raw_en[0]
		raw_ru = re.compile('<span class="serieslistboxru">(.*?)</span>').findall(http2)
		if len(raw_ru) == 0:
			TitleRU = 'No title'
		else:
			TitleRU = raw_ru[0]
		Descr = ''
		raw_des = re.compile('<span class="serieslistboxperstext">(.*?)</span>').findall(http2)
		if len(raw_des) != 0:
			for cur_des in raw_des:
				Descr = Descr + cur_des + '\n'
		raw_des2 = re.compile('<span class="serieslistboxdesc">(.*?)</span>').findall(http2)
		if len(raw_des2) > 0:
			Descr = Descr + raw_des2[0]
		sindex = str(x)
		#xbmc.output('*** %s Thumb   = %s' % (sindex, Thumb))
		#xbmc.output('*** %s TitleEN = %s' % (sindex, TitleEN))
		#xbmc.output('*** %s TitleRU = %s' % (sindex, TitleRU))
		#xbmc.output('*** %s Descr   = %s' % (sindex, Descr))
		#xbmc.output('*** %s wurl   = %s' %  (sindex, wurl))

		Title = '%s. %s (%s)' % (sindex, TitleRU, TitleEN)

		listitem = xbmcgui.ListItem(Title, iconImage = Thumb, thumbnailImage = Thumb)
		listitem.setInfo(type = "Video",
		    infoLabels = {
				"Title": Title,
				"Plot": Descr,
				"FolderName": TitleRU
			}
		);
		listitem.setProperty("Fanart_Image", Thumb);
		url = sys.argv[0] + '?mode=OpenSeries&url=' + urllib.quote_plus(wurl) \
			+ '&title=' + urllib.quote_plus(Title)
		xbmcplugin.addDirectoryItem(handle, url, listitem, True)

		x += 1

def OpenSeries(url, title):
	http = Get(url, SITEPREF + '/Series/')
	if http == None:
		xbmc.output('[%s] OpenSeries() Error 1: Not received data when opening URL=%s' % (PLUGIN_NAME, url))
		return

	raw_topimg = re.compile('<div class="topimgseries">\s*<img src="(.*?)"').findall(http)
	if len(raw_topimg) == 0:
		TopIMG = thumb
	else:
		TopIMG = SITEPREF + raw_topimg[0]

	raw1 = re.compile('<div class="sserieslistbox">(.*?)<div class="sseriesrightbox">', re.DOTALL).findall(http)
	if len(raw1) == 0:
		xbmc.output('[%s] OpenSeries() Error 2: r.e. not found it necessary elements. URL=%s' % (PLUGIN_NAME, url))
		xbmc.output(http)
		return

	raw2 = re.compile('<a href="(.+?)">\s(.*?)</a>', re.DOTALL).findall(raw1[0])
	if len(raw1) == 0:
		xbmc.output('[%s] OpenSeries() Error 3: r.e. not found it necessary elements. URL=%s' % (PLUGIN_NAME, url))
		xbmc.output(raw1[0])
		return

	x = 1
	for wurl, http2 in raw2:
		#xbmc.output('************** wurl = %s' % wurl)
		#xbmc.output('http2 = %s' % http2)

		raw_img = re.compile('<img src="(.*?)".*/>').findall(http2)
		if len(raw_img) == 0:
			Thumb = TopIMG
		else:
			Thumb = raw_img[0]
		raw_en = re.compile('<span class="sserieslistonetxten">(.*?)</span>').findall(http2)
		if len(raw_en) == 0:
			TitleEN = 'No title'
		else:
			TitleEN = raw_en[0]
		raw_ru = re.compile('<span class="sserieslistonetxtru">(.*?)</span>').findall(http2)
		if len(raw_ru) == 0:
			TitleRU = 'No title'
		else:
			TitleRU = raw_ru[0]

		raw_se = re.compile(u'<span class="sserieslistonetxtse">Сезон: (.*?)</span>').findall(http2)
		if len(raw_se) == 0:
			SeaNUM = 'Season not specified'
		else:
			SeaNUM = raw_se[0]

		raw_ep = re.compile('<span class="sserieslistonetxtep">Эпизод: (.*?)</span>').findall(http2)
		if len(raw_ep) == 0:
			EpiNUM = 'The episode is not specified'
		else:
			EpiNUM = raw_ep[0]

		sindex = str(x)
		xbmc.output('*** %s Thumb   = %s' % (sindex, Thumb))
		xbmc.output('*** %s TitleEN = %s' % (sindex, TitleEN))
		xbmc.output('*** %s TitleRU = %s' % (sindex, TitleRU))
		xbmc.output('*** %s SeaNUM  = %s' % (sindex, SeaNUM))
		xbmc.output('*** %s EpiNUM  = %s' % (sindex, EpiNUM))
		xbmc.output('*** %s wurl    = %s' % (sindex, wurl))

		Title = 'Episode %s: %s / %s' % (EpiNUM, TitleRU, TitleEN)
		Descr = 'Season: %s\nEpisode: %s' % (SeaNUM, EpiNUM)

		listitem = xbmcgui.ListItem(Title, iconImage = Thumb, thumbnailImage = Thumb)
		listitem.setInfo(type = "Video",
			infoLabels = {
				"title":	Title,
				"tvshowtitle": title,
				"plot":		"",
				"episode":  EpiNUM,
				"season":   SeaNUM,
				"VideoCodec": "h264"
			}
		)
		listitem.setProperty("Fanart_Image", Thumb)
		url = sys.argv[0] + '?mode=Watch&url=' + urllib.quote_plus(wurl) \
			+ '&title=' + urllib.quote_plus(Title)
		xbmcplugin.addDirectoryItem(handle, url, listitem, False)

		x += 1

	raw3 = re.compile('<div class="seasonnum">(.*?)</div>', re.DOTALL).findall(http)
	if len(raw3) == 0:
		xbmc.output('[%s] OpenSeries() Error 4: r.e. not found it necessary elements. URL=%s' % (PLUGIN_NAME, url))
		xbmc.output(http)
		return

	raw4 = re.compile('<a href="(.*?)"><span class=".*">(.*?)</span></a>').findall(raw3[0])
	if len(raw4) == 0:
		xbmc.output('[%s] OpenSeries() Error 5: r.e. not found it necessary elements. URL=%s' % (PLUGIN_NAME, url))
		xbmc.output(raw3[0])
		return

	for row_url, row_name in raw4:
		xbmc.output('*** row_url  = %s' % row_url)
		xbmc.output('*** row_name = %s' % row_name)

		listitem = xbmcgui.ListItem(row_name, iconImage = TopIMG, thumbnailImage = TopIMG)
		listitem.setInfo(type = "Video", infoLabels = {
			"Title":	row_name
			} )
		url = sys.argv[0] + '?mode=OpenSeries&url=' + urllib.quote_plus(row_url) \
			+ '&title=' + urllib.quote_plus(title + ' : ' + row_name)
		xbmcplugin.addDirectoryItem(handle, url, listitem, True)


def Watch(url, title, img):

	def meta_decoder(param1):
		def enc_replace(param1, param2):
			loc_4 = []
			loc_5 = []
			loc_6 = ['2','I','0','=','3','Q','8','V','7','X','G','M','R','U','H','4','1','Z','5','D','N','6','L','9','B','W'];
			loc_7 = ['x','u','Y','o','k','n','g','r','m','T','w','f','d','c','e','s','i','l','y','t','p','b','z','a','J','v'];
			if (param2 == 'e'):
				loc_4 = loc_6
				loc_5 = loc_7
			if (param2 == 'd'):
				loc_4 = loc_7
				loc_5 = loc_6
			loc_8 = 0
			while (loc_8 < len(loc_4)):
				param1 = param1.replace(loc_4[loc_8], '___')
				param1 = param1.replace(loc_5[loc_8], loc_4[loc_8])
				param1 = param1.replace('___', loc_5[loc_8])
				loc_8 += 1
			return param1
		param1 = param1.replace('%2b', '+')
		param1 = param1.replace('%3d', '=')
		param1 = param1.replace('%2f', '/')
		param1 = enc_replace(param1, 'd')
		return base64.b64decode(param1)

	http = Get(url)
	if http == None:
		xbmc.output('[%s] Watch() Error 1: Not received data when opening URL=%s' % (PLUGIN_NAME, url))
		return

	raw1 = re.compile('<input type="hidden" id="metadata" value="(.*)" />').findall(http)
	if len(raw1) == 0:
		xbmc.output('[%s] Watch() Error 2: r.e. not found it necessary elements. URL=%s' % (PLUGIN_NAME, url))
		xbmc.output(http)
		return
	Metadata = raw1[0]

	Plot = 'No plot'
	raw2 = re.compile('<span class="textdesc">(.*?)</span>', re.DOTALL).findall(http)
	if len(raw2)> 0:
		Plot = raw2[0]

	eid = '0'
	raw3 = re.compile('<input type="hidden" id="eid" value="(.*?)" />').findall(http)
	if len(raw3) > 0:
		eid = raw3[0]

	pid = '0'
	raw4 = re.compile('<input type="hidden" id="pid" value="(.*?)" />').findall(http)
	if len(raw4) > 0:
		pid = raw4[0]

	sid = '0'
	raw5 = re.compile('<input type="hidden" id="sid" value="(.*?)" />').findall(http)
	if len(raw5) > 0:
		sid = raw5[0]

	epwatch = '0'
	raw6 = re.compile('<input type="hidden" id="epwatch" value="(.*?)" />').findall(http)
	if len(raw6) > 0:
		epwatch = raw6[0]

	sewatch = '0'
	raw7 = re.compile('<input type="hidden" id="sewatch" value="(.*?)" />').findall(http)
	if len(raw7) > 0:
		sewatch = raw7[0]

	h1 = '0'
	raw8 = re.compile('<input type="hidden" id="h1" value="(.*?)" />').findall(http)
	if len(raw8) > 0:
		h1 = raw8[0]

	Hash = '0'
	raw9 = re.compile('<input type="hidden" id="hash" value="(.*?)" />').findall(http)
	if len(raw9) > 0:
		Hash = raw9[0]

	xbmc.output('*** eid      = %s' % eid)
	xbmc.output('*** pid      = %s' % pid)
	xbmc.output('*** sid      = %s' % sid)
	xbmc.output('*** epwatch  = %s' % epwatch)
	xbmc.output('*** sewatch  = %s' % sewatch)
	xbmc.output('*** h1       = %s' % h1)
	xbmc.output('*** Hash     = %s' % Hash)
	xbmc.output('*** Metadata = %s' % Metadata)
	xbmc.output('*** Plot     = %s' % Plot)


	Meta = meta_decoder(Metadata)
	sources2_default = ''
	sources2_hq = ''
	aspect = '0'
	duration = '0'
	hq = '1'
	Eid = '0'
	screen = ''
	sizes_default = '0'
	sizes_hq = '0'
	langs_en = '0'
	langs_ru = '0'
	subtitles_en = '0'
	subtitles_ru = '0'
	subtitles_en_sources = ''
	subtitles_ru_sources = ''

	r1 = re.compile('<movie>(.*?)</movie>', re.DOTALL).findall(Meta)
	if len(r1) > 0:
		r2 = re.compile('<sources2>(.*?)</sources2>', re.DOTALL).findall(r1[0])
		if len(r2) > 0:
			r3 = re.compile('<default>(.*?)</default>').findall(r2[0])
			if len(r3) > 0:
				sources2_default = r3[0]
			r3 = re.compile('<hq>(.*?)</hq>').findall(r2[0])
			if len(r3) > 0:
				sources2_hq = r3[0]
		r2 = re.compile('<aspect>(.*?)</aspect>').findall(r1[0])
		if len(r2) > 0:
			aspect = r2[0]
		r2 = re.compile('<duration>(.*?)</duration>').findall(r1[0])
		if len(r2) > 0:
			duration = r2[0]
		r2 = re.compile('<hq>(.*?)</hq>').findall(r1[0])
		if len(r2) > 0:
			hq = r2[0]
		r2 = re.compile('<eid>(.*?)</eid>').findall(r1[0])
		if len(r2) > 0:
			Eid = r2[0]
		r2 = re.compile('<screen>(.*?)</screen>').findall(r1[0])
		if len(r2) > 0:
			screen = r2[0]
		r2 = re.compile('<sizes>(.*?)</sizes>', re.DOTALL).findall(r1[0])
		if len(r2) > 0:
			r3 = re.compile('<default>(.*?)</default>').findall(r2[0])
			if len(r3) > 0:
				sizes_default = r3[0]
			r3 = re.compile('<hq>(.*?)</hq>').findall(r2[0])
			if len(r3) > 0:
				sizes_hq = r3[0]
		r2 = re.compile('<langs>(.*?)</langs>', re.DOTALL).findall(r1[0])
		if len(r2) > 0:
			r3 = re.compile('<en>(.*?)</en>').findall(r2[0])
			if len(r3) > 0:
				langs_en = r3[0]
			r3 = re.compile('<ru>(.*?)</ru>').findall(r2[0])
			if len(r3) > 0:
				langs_ru = r3[0]
		r2 = re.compile('<subtitles>(.*?)</subtitles>', re.DOTALL).findall(r1[0])
		if len(r2) > 0:
			r3 = re.compile('<en>(.*?)</en>').findall(r2[0])
			if len(r3) > 0:
				subtitles_en = r3[0]
			r3 = re.compile('<ru>(.*?)</ru>').findall(r2[0])
			if len(r3) > 0:
				subtitles_ru = r3[0]
			r3 = re.compile('<sources>(.*?)</sources>', re.DOTALL).findall(r2[0])
			if len(r3) > 0:
				r4 = re.compile('<en>(.*?)</en>').findall(r3[0])
				if len(r4) > 0:
					subtitles_en_sources = r4[0]
				r4 = re.compile('<ru>(.*?)</ru>').findall(r3[0])
				if len(r4) > 0:
					subtitles_ru = r4[0]

	xbmc.output('    sources2_default = %s' % sources2_default)
	xbmc.output('         sources2_hq = %s' % sources2_hq)
	xbmc.output('              aspect = %s' % aspect)
	xbmc.output('            duration = %s' % duration)
	xbmc.output('                  hq = %s' % hq)
	xbmc.output('                 Eid = %s' % Eid)
	xbmc.output('              screen = %s' % screen)
	xbmc.output('       sizes_default = %s' % sizes_default)
	xbmc.output('            sizes_hq = %s' % sizes_hq)
	xbmc.output('            langs_en = %s' % langs_en)
	xbmc.output('            langs_ru = %s' % langs_ru)
	xbmc.output('        subtitles_en = %s' % subtitles_en)
	xbmc.output('        subtitles_ru = %s' % subtitles_ru)
	xbmc.output('subtitles_en_sources = %s' % subtitles_en_sources)
	xbmc.output('subtitles_ru_sources = %s' % subtitles_ru_sources)


	Hash = Hash[::-1]

	Lang = 'ru'
	Time = '0'
	#p0 = 'http://cdn.turbofilm.tv'
	#p0 = 'http://217.199.218.60'

	p1 = sha.new(Lang).hexdigest()
	p2 = str(eid)
	p3 = str(sources2_default)
	p4 = str(Time)
	p5 = Hash
	p6 = sha.new(Hash + str(random.random())).hexdigest()
	p7 = sha.new(p6 + eid + 'A2DC51DE0F8BC1E9').hexdigest()
	retval = '/%s/%s/%s/%s/%s/%s/%s' % (p1,p2,p3,p4,p5,p6,p7)


	xbmc.output ('SRC file retval = %s' % retval)
	rurl = url.replace('/', '_')
	#dest = os.path.join(xbmc.translatePath('special://temp/'), rurl)
	#xbmc.output ('Dest file = %s' % dest)

	phpsessid = ''
	#req = urllib2.Request(durl)
	if os.path.isfile(phpsessid_file):
		fh = open(phpsessid_file, 'r')
		phpsessid = fh.read()
		fh.close()


	def PlayURL(path):
		conn =   httplib.HTTPConnection('cdn.turbofilm.tv', 80, 10)

		headers =  {'User-Agent':      'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.54 Safari/535.2',\
			    'Host':            'cdn.turbofilm.tv',\
			    'Accept':          '*/*',\
			    'Accept-Language': 'ru,en;q=0.9',\
			    'Accept-Charset':  'iso-8859-1, utf-8, utf-16, *;q=0.1',\
			    'Accept-Encoding': 'deflate, gzip, x-gzip, identity, *;q=0',\
			    'Referer':         'http://turbofilm.tv/media/swf/Player20.swf',\
			    'Cookie':          'IAS_ID='+str(phpsessid)+'; _',\
			    'Cookie2':         '$Version=1',\
			    'Connection':      'Keep-Alive' }

		conn.request("GET", path, '', headers)
		response = conn.getresponse()
		conn.close()
		if(response.status == 302):
			xbmc.output('OK - response.status == 302')
			Location = response.getheader('Location') # + '@'
			xbmc.output('Location: %s' % Location)

			#item = xbmcgui.ListItem(title, iconImage = thumb, thumbnailImage = thumb)
			#item.setInfo(type="Video", infoLabels = {
			#	"Title":	title,
			#	"Plot":		Plot
			#	} )

			h_1 = '|Referer=' + urllib.quote_plus('http://turbofilm.tv/media/swf/Player20.swf')
			h_2 = '&User-Agent=' + urllib.quote_plus('Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.54 Safari/535.2')
			h_3 = '&Accept=' + urllib.quote_plus('*/*')
			h_4 = '&Accept-Language=' + urllib.quote_plus('ru,en;q=0.9')
			h_5 = '&Accept-Charset=' + urllib.quote_plus('iso-8859-1, utf-8, utf-16, *;q=0.1')
			h_6 = '&Accept-Encoding=' + urllib.quote_plus('deflate, gzip, x-gzip, identity, *;q=0')
			h_7 = '&Connection=' + urllib.quote_plus('Keep-Alive')
			#
			finalUrl = Location + h_1 + h_2 + h_3 + h_4 + h_5 + h_6 + h_7
			item = xbmcgui.ListItem(title, iconImage = thumb, thumbnailImage = thumb, path = finalUrl)
			item.setInfo(type="Video", infoLabels = {
				"Title":	title,
				"Plot":		Plot
				} )
			item.setProperty("IsPlayable", "true")
			item.setProperty('mimetype', 'video/mp4');

			xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

			xbmc.Player().play(finalUrl, item)
			#xbmc.Player().play(finalItem)

			return
		return


	PlayURL(retval)


if run_once():
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
		ShowSeries('/Series/')
		xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
		xbmcplugin.endOfDirectory(handle)

	elif mode == 'OpenSeries':
		OpenSeries(url, title)
		xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
		xbmcplugin.endOfDirectory(handle)

	elif mode == 'Watch':
		Watch(url, title, img)
		#xbmcplugin.setPluginCategory(handle, PLUGIN_NAME)
		#xbmcplugin.endOfDirectory(handle)