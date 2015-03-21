import urllib, urllib2, re, sys, os
import xbmcplugin, xbmcgui
import urlparse
import codecs
import xbmcaddon
import xbmc
Addon = xbmcaddon.Addon( id = 'plugin.video.cScVOD' )
_ADDON_PATH =   xbmc.translatePath(Addon.getAddonInfo('path'))
sys.path.append( os.path.join( _ADDON_PATH, 'resources', 'lib') )
from YoutubeParser import youtube_url
from m3u8parser import parse_megogo, best_m3u8
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
from strings import *
import pickle
import xml.dom.minidom as mn
from urlparse import parse_qs
import hashlib
from urllib import unquote_plus
from SGParser import sg_parsers
from cScParser import cSc_parsers
from demjson3 import loads
hos = int(sys.argv[1])
addon_id = Addon.getAddonInfo('id')
xbmcplugin.setContent(hos, 'movies')
std_headers = {
	'User-Agent': 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.6) Gecko/20100627 Firefox/3.6.6',
	'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Language': 'en-us,en;q=0.5',
}

def construct_request(params):
	return '%s?%s' % (sys.argv[0], urllib.urlencode(params))
		
def _downloadUrl(target, post=None):
		req = urllib2.Request(url = target, data = post)
		req.add_header('User-Agent', 'XBMC 1.5')
		u = urllib2.urlopen(req)
		content = u.read()
		u.close()

		return content

def GET(target, post=None):
    try:
        req = urllib2.Request(url = target, data = post)
        req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
        req.add_header('Accept', '*/*')
        req.add_header('Accept-Language', 'ru-RU')
        req.add_header('Accept-Charset', 'utf-8')
        resp = urllib2.urlopen(req)
        http = resp.read()

        return http
    except Exception, e:
        xbmc.log( '[%s]: GET EXCEPT [%s]' % (addon_id, e), 4 )
        showMessage('HTTP ERROR', e, 5000)		
				
def Categories(params):
	start = 'http://185.25.119.98/vod/start.xml'
	if Addon.getSetting('mac') != None:
		box_mac = Addon.getSetting('mac')
	else:
		box_mac = None
	try: searchon = params['search']
	except: searchon = None
	try: 
		url=urllib.unquote(params['link'])
		if box_mac != None:
			sign = '?'
			if url.find('?') > -1:	
				sign = '&'
			url = url + sign + 'box_mac=' + box_mac
		else:
			url = url
	except:
		url = start
	xml = _downloadUrl(url)
	print 'HTTP LEN = [%s]' % len(xml)
	if url.find('m3u') > -1:
		m3u(xml)
	else:
			xml = mn.parseString(xml)
	n = 0
	if searchon == None:
		try: search = xml.getElementsByTagName('xbmc_search')[0].firstChild.data
		except: search = None
	if search != None:
		kbd = xbmc.Keyboard()
		kbd.setDefault('')
		kbd.setHeading('Search')
		kbd.doModal()
		if kbd.isConfirmed():
			sts=kbd.getText();
			sign = '?'
			if url.find('?') > -1:	
				sign = '&'
			sts = sts.replace(' ','%20')
			url2 = url + sign + 'search=' + sts
			print url2
			xml = _downloadUrl(url2)
		else:
			xml = _downloadUrl(url)
		print 'HTTP LEN = [%s]' % len(xml)
		xml = mn.parseString(xml)
		playlist(xml)
	else:
		if url.find('m3u') > -1:
			m3u(xml)
		else:
			playlist(xml)
		
	if start == url:
		uri = construct_request({
			'func': 'settings'
			})
		listitem=xbmcgui.ListItem('\xd0\x9d\xd0\xb0\xd1\x81\xd1\x82\xd1\x80\xd0\xbe\xd0\xb9\xd0\xba\xd0\xb8 \xd0\xb0\xd0\xb4\xd0\xb4\xd0\xbe\xd0\xbd\xd0\xb0', 'DefaultVideo.png', 'DefaultVideo.png')
		listitem.setInfo(type = 'settings', infoLabels = '')
		xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
	xbmc.executebuiltin('Container.SetViewMode(504)')
	xbmcplugin.endOfDirectory(hos)
	#print 'Channels = [%s]' % n

def playlist(xml):
	n = 0
	xml = xml
	for prev_page_url in xml.getElementsByTagName('prev_page_url'):
		prev_url = xml.getElementsByTagName('prev_page_url')[0].firstChild.data
		prev_title =  "[COLOR FFFFFF00]<-" + prev_page_url.getAttribute('text').encode('utf-8') +'[/COLOR]'
		uri = construct_request({
			'func': 'Categories',
			'link':prev_url 
			})	
		listitem=xbmcgui.ListItem(prev_title, 'DefaultVideo.png', 'DefaultVideo.png')
		xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
	for channel in xml.getElementsByTagName('channel'):
		try: title = channel.getElementsByTagName('title')[0].firstChild.data.encode('utf-8')
		except: title = 'No title or error'
		title = title.replace('<b>', '')
		title = title.replace('</b>', '')
		try:
			description = channel.getElementsByTagName('description')[0].firstChild.data.encode('utf-8')
			img_src_list = re.findall('img .*?src="(.*?)"', description)
			if len(img_src_list) > 0:
				img_src = img_src_list[0]
			else:
				img_src_list = re.findall("img .*?src='(.*?)'", description)
				if len(img_src_list) > 0:
					img_src = img_src_list[0]
				else:	
					img_src = 'DefaultVideo.png'
					
			description = description.replace('<br>', '\n')
			description = description.replace('<br/>', '\n')
			description = description.replace('</h1>', '</h1>\n')
			description = description.replace('</h2>', '</h2>\n')
			description = description.replace('&nbsp;', ' ')
			description4playlist_html = description
			text = re.compile('<[\\/\\!]*?[^<>]*?>')
			description = text.sub('', description)
			plot = description
		except: 
			description = 'No description'
			plot = description
			img_src = 'DefaultVideo.png'
		n = n+1
		try: 
			link = channel.getElementsByTagName('playlist_url')[0].firstChild.data
			mysetInfo={}
			mysetInfo['plot'] = plot
			mysetInfo['plotoutline'] = plot
			uri = construct_request({
				'func': 'Categories',
				'link':link 
				})	
			listitem=xbmcgui.ListItem(title, img_src, img_src)
			listitem.setInfo(type = 'video', infoLabels = mysetInfo)
			xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
		except: link = None
		try: 
			stream = channel.getElementsByTagName('stream_url')[0].firstChild.data
			mysetInfo={}
			mysetInfo['plot'] = plot
			mysetInfo['plotoutline'] = plot
			if img_src != None:
				uri = construct_request({
					'func': 'Play',
					'title':title,
					'img':img_src,
					'stream':stream 
					})	
			else:
				uri = construct_request({
					'func': 'Play',
					'title':title,
					'stream':stream 
					})
			listitem=xbmcgui.ListItem(title, img_src, img_src)
			listitem.setInfo(type = 'video', infoLabels = mysetInfo)
			xbmcplugin.addDirectoryItem(hos, uri, listitem, False)
		except: stream = None	
	for next_page_url in xml.getElementsByTagName('next_page_url'):
		next_url = xml.getElementsByTagName('next_page_url')[0].firstChild.data
		next_title =  "[COLOR FFFFFF00]->" + next_page_url.getAttribute('text').encode('utf-8') +'[/COLOR]'
		uri = construct_request({
			'func': 'Categories',
			'link':next_url 
			})	
		listitem=xbmcgui.ListItem(next_title, 'DefaultVideo.png', 'DefaultVideo.png')
		xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
	
def m3u(xml):
	m3u = xml
	regex = re.findall('#EXTINF.*,(.*\\s)\\s*(.*)', m3u)
	if not len(regex) > 0:
		regex = re.findall('((.*.+)(.*))', m3u)
	for text in regex:
		title = text[0].strip()
		url = text[1].strip()
		uri = construct_request({
			'func': 'Play',
			'title':title,
			'stream':url
			})
		listitem=xbmcgui.ListItem(title, '', '')
		listitem.setInfo(type = 'video', infoLabels = '')
		xbmcplugin.addDirectoryItem(hos, uri, listitem, True)		
	
def settings(params):
	Addon.openSettings()
	return None
	
def Play(params):
	global SG_PARSER
	global CSC_PARSER
	SG_PARSER = sg_parsers()
	CSC_PARSER = cSc_parsers()
	url = urllib.unquote(params['stream'])
	try: img = params['img']
	except: img = 'DefaultVideo.png'
	title = params['title']
	try:
		url = SG_PARSER.get_parsed_link(url)
		url = CSC_PARSER.get_parsed_link(url)
		if url.find('vk.com') > -1 or url.find('/vkontakte.php?video') > 0 or url.find('vkontakte.ru/video_ext.php') > 0 or url.find('/vkontakte/vk_kinohranilishe.php?id=') > 0:
			http=GET(params['stream'])
			soup = BeautifulSoup(http, fromEncoding="windows-1251")
			av=0
			for rec in soup.findAll('param', {'name':'flashvars'}):
			#print rec
				for s in rec['value'].split('&'):
					if s.split('=',1)[0] == 'uid':
						uid = s.split('=',1)[1]
					if s.split('=',1)[0] == 'vtag':
						vtag = s.split('=',1)[1]
					if s.split('=',1)[0] == 'host':
						host = s.split('=',1)[1]
					if s.split('=',1)[0] == 'vid':
						vid = s.split('=',1)[1]
					if s.split('=',1)[0] == 'oid':
						oid = s.split('=',1)[1]
					if s.split('=',1)[0] == 'hd':
						hd = s.split('=',1)[1]
				if Addon.getSetting('vk') == '1':
					url = host+'u'+uid+'/videos/'+vtag+'.240.mp4'
					if int(hd)==3:
						url = host+'u'+uid+'/videos/'+vtag+'.720.mp4'
					if int(hd)==2:
						url = host+'u'+uid+'/videos/'+vtag+'.480.mp4'
					if int(hd)==1:
						url = host+'u'+uid+'/videos/'+vtag+'.360.mp4'
				else:
					choices = []
					if int(hd)>=3:
						choices.append('720')
					if int(hd)>=2:
						choices.append('480')
					if int(hd)>=1:
						choices.append('360')
					choices.append('240')
	
					dialog = xbmcgui.Dialog()
					selected = dialog.select('Quality', choices)
	
					if selected>-1:
						url = host+'u'+uid+'/videos/'+vtag+'.'+choices[selected]+'.mp4'
					else:
						url = host+'u'+uid+'/videos/'+vtag+'.240.mp4'
						if int(hd)==3:
							url = host+'u'+uid+'/videos/'+vtag+'.720.mp4'
						if int(hd)==2:
							url = host+'u'+uid+'/videos/'+vtag+'.480.mp4'
						if int(hd)==1:
							url = host+'u'+uid+'/videos/'+vtag+'.360.mp4'
			#print video
				#video = url
		
		if url.find('youtube.com') > -1:
			try:
				video = youtube_url().get_youtube_link2(url)
				url = video
				print url
			except:
				print 'error youtube'
				
		if url.find('m3u8') > -1:
			best_m3u8(url)		
				
		if url.find('megogo') > -1:
			try:
				req = urllib2.Request(url, None, {'User-agent': 'QuickTime/7.6.2 (qtver=7.6.2;os=Windows NT 5.1 Service Pack 3)'})
				page = urllib2.urlopen(req).read()
			except Exception as ex:
				print ex
			
			print 'fillm url = ', url
			video = parse_megogo(url)
			url = video
			print '#'		
	except: 
		url = url
		
	i = xbmcgui.ListItem(title, url, img, img)
	xbmc.Player().play(url, i)
	
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
    Categories(params)
if func != None:
    try: pfunc = globals()[func]
    except:
        pfunc = None
        xbmc.log( '[%s]: Function "%s" not found' % (addon_id, func), 4 )
        showMessage('Internal addon error', 'Function "%s" not found' % func, 2000)
    if pfunc: pfunc(params)