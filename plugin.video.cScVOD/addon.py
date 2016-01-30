#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib, urllib2, re, sys, os, random
import xbmcplugin, xbmcgui
import xbmcaddon
import xbmc
import codecs
Addon = xbmcaddon.Addon( id = 'plugin.video.cScVOD' )
_ADDON_PATH =   xbmc.translatePath(Addon.getAddonInfo('path'))
sys.path.append( os.path.join( _ADDON_PATH, 'resources', 'lib'))
addon_id = Addon.getAddonInfo('id')
import VseTV
from BeautifulSoup import BeautifulStoneSoup, MinimalSoup
from urllib import unquote_plus
from demjson3 import loads
import socket
import time
import imp
    
hos = int(sys.argv[1])
xbmcplugin.setContent(hos, 'movies')
busystring = xbmc.getLocalizedString(503).encode("utf8")
fanart  = _ADDON_PATH + '/fanart.jpg'
set_png = _ADDON_PATH + '/settings.png'
left = _ADDON_PATH + '/left.png'
right = _ADDON_PATH + '/right.png'
addon_icon = _ADDON_PATH + '/icon.png'
addon_v = Addon.getAddonInfo('version')
xbmc_headers = {'User-Agent':'cScVOD XBMC/Kodi ' + addon_v}

bckKey = _ADDON_PATH + '/bckeyb.bk'
if os.path.exists(bckKey) == False:
    os.path.dirname(bckKey)
    bckeyb = open(bckKey, 'w')
    bckeyb.write('')
    bckeyb.close()

	
def write_mac():
    mac_settings = Addon.getSetting('mac')
    print mac_settings
    if mac_settings == "":   
        mac_address = xbmc.getInfoLabel('Network.MacAddress')
        i = 1
        while mac_address == busystring:
            print "while: %s" % i
            i = i+1
            mac_address = xbmc.getInfoLabel('Network.MacAddress') 
            time.sleep(1)
            if i == 10:
                break
        Addon.setSetting('mac', mac_address)	
	
def makemodule(url, sourcestr='', modname = ''):
    modsource=urllib2.urlopen(urllib2.Request(url,data=None,headers=xbmc_headers)).read()
    obj = compile(modsource, sourcestr, 'exec')
    module = imp.new_module(modname)
    exec(obj,module.__dict__)
	
    return module

def showMessage(message = '', heading='', times = 3000, pics = addon_icon):
    try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading.encode('utf-8'), message.encode('utf-8'), times, pics.encode('utf-8')))
    except Exception, e:
        try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, pics))
        except Exception, e:
            xbmc.log( '[%s]: showMessage: exec failed [%s]' % (addon_id, e), 3 )

def construct_request(params):
    return '%s?%s' % (sys.argv[0], urllib.urlencode(params))
		
def Pars(url):
    try:
        if url.find('|') > -1:
            dolc = url.split('|')
            uri = dolc[0]
            pars1 = dolc[1]
            pars2 = dolc[2]
            req = urllib2.Request(uri, None, {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.1.2) Gecko/20090729 Firefox/3.5.2',
                                                     'Accept-Charset': 'windows-1251,utf-8;q=0.7,*;q=0.7',
                                                     'Accept': 'text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5',
                                                     'Accept-Language': 'ru,en-us;q=0.7,en;q=0.3'})
            html = urllib2.urlopen(req).read().replace('\t', '').replace('\r', '').replace('\n', '').replace(pars1, '@video=="').replace(pars2, '"==@')
            regex = re.findall('@video=="(.*?)"==@', html)
            if regex != []:
                return regex[0]
            else:
                return url
        else:
            return url
    except Exception as ex:
        print 'Pars error', ex
        return None
		
def Categories(params):
    s = ''
    start = 'http://185.25.119.98/vod/start.xml'
		
    if Addon.getSetting('mac') != None and Addon.getSetting('mac') != '':
        box_mac = Addon.getSetting('mac')
    else:
        box_mac = ''
		
    try:
        searchon = params['search']
    except:
        searchon = None
		
    try:
        url = urllib.unquote(params['link'])
    except Exception as ex:
        print 'error link = ', ex
        url = start

    try:
        parser = params['parser']
        if parser:
            strUrl = Pars(parser)
            if strUrl and url:
                if url.find('md5hash') > -1:
                    url = url.replace('md5hash', strUrl)
    except Exception as ex:
        print 'error parser = ', ex
        url = start

    sign = '?'
    if url.find('?') > -1:
        sign = '&'
    url = url + sign + 'box_mac=' + box_mac

    if searchon == 'search':
        kbd = xbmc.Keyboard()
        values = []
        searchtxt = ''
        bc = open(bckKey, 'r')
        lines = bc.readlines()
        bc.close()
        if lines != []:
            ask = xbmcgui.Dialog()
            qestion = ['Новый запрос', 'История запросов']
            sel = ask.select('История запросов', qestion)
            if sel == 1:
                dialog = xbmcgui.Dialog()
                for line in lines:
                    values.append(line)
                selected = dialog.select('История', values)
                if lines != [] and selected != -1:
                    searchtxt = lines[selected].strip('\n')
        kbd.setDefault(searchtxt)
        kbd.setHeading('Поиск')
        kbd.doModal()
        if kbd.isConfirmed():
            sts=kbd.getText();
            sts = sts.replace(' ','%20')
            count = 0
            bc = open(bckKey, 'w')
            bc.write(sts + '\n')
            count += 1
            for line in lines:
                count += 1
                if line.strip('\n') != sts and len(line) > 2 and count < 11:
                    bc.write(line)
            bc.close()
            url = url + '&search=' + sts

    print '==url==' + url
    http = ''
    #####################
    try:
        req = urllib2.Request(url, None, xbmc_headers)
        http = urllib2.urlopen(req).read()
    except Exception as ex:
        print 'urllib2 error -> ' , ex
    http = http.replace('&nbsp;', ' ').replace('&amp;', '&')
    #print '==http==' + http
    if http != None and http != '':
        if http.find('#EXT') > -1:
            m3u(http)
        else:
            xml = BeautifulStoneSoup(http)
            n = 0
            playlist(xml)
    if url == start + sign + 'box_mac=' + box_mac:
        uri = construct_request({
            'func': 'settings'
            })
        listitem=xbmcgui.ListItem('[COLOR FFFF8888]Настройки[/COLOR]', iconImage = set_png)
        listitem.setInfo(type = 'settings', infoLabels={})
        if Addon.getSetting('fanart') == '0':		
            listitem.setProperty('fanart_image', set_png)
        xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
    if Addon.getSetting('list') == '0':
        xbmc.executebuiltin('Container.SetViewMode(504)')
    if Addon.getSetting('list') == '1':
        xbmc.executebuiltin('Container.SetViewMode(500)')
    if Addon.getSetting('list') == '2':
        xbmc.executebuiltin('Container.SetViewMode(503)')
    if Addon.getSetting('list') == '3':
        xbmc.executebuiltin('Container.SetViewMode(515)')
    if Addon.getSetting('list') == '4':
        xbmc.executebuiltin('Container.SetViewMode(501)')
    xbmcplugin.endOfDirectory(hos)



def playlist(xml):
    n = 0
    link = None
    stream = None
    prev_title = ''
    next_title = ''
    construkt = {}
    prev_page_element = xml.find('prev_page_url')
    if prev_page_element:
        prev_url = prev_page_element.text.encode('utf-8')
        prev_page_text = prev_page_element.get('text')
        if prev_page_text:
            prev_page_text = prev_page_text.encode('utf-8')
            prev_title =  "[COLOR FFFFFF00]<-" + prev_page_text +'[/COLOR]'
            uri = construct_request({
                 'func': 'Categories',
                 'link':prev_url
                 })
            listitem=xbmcgui.ListItem(prev_title, left, left)
            if Addon.getSetting('fanart') == '0':			
                listitem.setProperty('Fanart_Image', left)
            xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
    next_page_element = xml.find('next_page_url')
    if next_page_element:
        next_url = next_page_element.text.encode('utf-8')
        next_page_text = next_page_element.get('text')
        if next_page_text:
            next_page_text = next_page_text.encode('utf-8')
            next_title =  "[COLOR FFFFFF00]->" + next_page_text +'[/COLOR]'
            uri = construct_request({
                'func': 'Categories',
                'link':next_url
                })
            listitem=xbmcgui.ListItem(next_title, right, right)
            if Addon.getSetting('fanart') == '0':			
                listitem.setProperty('fanart_image', right)
            xbmcplugin.addDirectoryItem(hos, uri, listitem, True)

    for channel in xml.findAll('channel'):
        img_src = ''
        img_logo = ''
        description = ''
        titl = ''
        YaID = ''
        title = channel.find('title').text.encode('utf-8')
        title = title.replace('&', ' and ')
        title = re.compile('<[\\/\\!]*?[^<>]*?>').sub('', title)
        description = channel.find('description')
        if description:
            description = description.text.encode('utf-8')
            img_src_list = re.findall('src="(.*?)"', description) or re.findall("src='(.*?)'", description)
            if len(img_src_list) > 0:
                img_src = img_src_list[0]
            if img_src == None or img_src == '' or img_src.find('http') < 0 :
                img_src = fanart
            description = description.replace('<br>', '\n')
            description = description.replace('<br/>', '\n')
            description = description.replace('</h1>', '</h1>\n')
            description = description.replace('</h2>', '</h2>\n')
            description = description.replace('&nbsp;', ' ')
            description = re.compile('<[\\/\\!]*?[^<>]*?>').sub('', description)
        else:
            description = title
        if description == '':
            description = title
        piconname = channel.find('logo_30x30') or channel.find('logo')
        if piconname:
            img_logo = piconname.text
            if img_src == None or img_src == '' or img_src == fanart :
                img_src = img_logo

        n = n+1

        searchon = channel.find('search_on')
        search = None
        if searchon:
            search = searchon.text.encode('utf-8')
            
        parser = channel.find('parser')
        stream_url = channel.find('stream_url')
        playlist_url = channel.find('playlist_url')
        
        if parser:
            parser = parser.text.encode('utf-8')
            if stream_url:
                strUrl = Pars(parser)
                if stream_url.find('md5hash') > -1 and strUrl:
                    stream_url = stream_url.replace('md5hash', strUrl)
        
        if playlist_url:
            link = playlist_url.text.encode('utf-8')
            titl = "[COLOR FFFFFFFF]" + title + "[/COLOR]"
            
            construkt = {
                'func': 'Categories',
                'link': link,
                'search': search,
                'parser': parser
                }
                    
        if stream_url:
            stream = stream_url.text.encode('utf-8')
            titl = "[COLOR FFB77D00]" + title + "[/COLOR]"
            
            id = VseTV.get_ch_id(title)
            if id != None:
                img_src = 'http://185.25.119.98/epg/logo/%s.png' % id				
			
            construkt = {
                'func': 'Play',
                'stream': stream,
                'img': img_src,
                'title': title,
                'epgid': id
                }
                
        listitem=xbmcgui.ListItem(titl, iconImage = img_src, thumbnailImage = img_src)
        if Addon.getSetting('fanart') == '0':  		
            listitem.setProperty('fanart_image', img_src)
        listitem.setInfo(type = 'video', infoLabels={'title': titl, 'plot': description})
        uri = construct_request(construkt)
        xbmcplugin.addDirectoryItem(hos, uri, listitem, True)


def m3u(xml):
    m3u = xml
    regex = re.findall('#EXTINF.*,(.*\\s)\\s*(.*)', m3u)
    if not len(regex) > 0:
        regex = re.findall('((.*.+)(.*))', m3u)
    for text in regex:
        img_src = ''
        description = ''
        YaID = ''
        id = ''
        title = text[0].strip()
        id = VseTV.get_ch_id(title)        
        title = "[COLOR FFFFB77D00]" + title + "[/COLOR]"
        img_src = fanart
        if id != None:
            img_src = 'http://185.25.119.98/epg/logo/%s.png' % id   
        else:
            img_src = 'http://185.25.119.98/epg/logo/0.png'
        url = text[1].strip()
        listitem=xbmcgui.ListItem(title, iconImage = img_src, thumbnailImage = img_src)
        if Addon.getSetting('fanart') == '0':		
            listitem.setProperty('fanart_image', fanart)
        listitem.setInfo(type = 'video', infoLabels={'title': title, 'plot': description})
        uri = construct_request({
            'func': 'Play',
            'title': title,
            'img': img_src,
            'stream': url,
            'epgid': id
            })
        xbmcplugin.addDirectoryItem(hos, uri, listitem, True)



def settings(params):
    Addon.openSettings()
    return None

def Play(params):
    try:
        url = urllib.unquote(params['stream']).replace('&amp;', '&').replace(';', '')
    except:
        url = ''
        
    try:
        title = params['title']
    except:
        title = ''
    
    try:
        epgid = params['epgid']
    except:
        epgid = None
		
    try:
        img = params['img']
    except:
        img = None
		
    if epgid != '' and epgid != None:
        epg = VseTV.get_ch_epg(epgid)
        if epg != '' and epg != None:
            title = epg
    try:	
        Parser = makemodule(url = 'http://185.25.119.98/xbmc/loadparsers.py', modname = 'loadparsers')
    except:
        Parser = makemodule(url = 'http://91.211.245.49/xbmc/loadparsers.py', modname = 'loadparsers')
    url = Parser.parse_play_url(url)			
		
    if url == 'youtube':
        pass	
    elif url != '' and url != None and url.find('.html') < 0 and url.find('md5hash') < 0:
        i = xbmcgui.ListItem(title, url, img, img)
        xbmc.Player().play(url, i)
    else:
        showMessage('Not playable stram', url, 2000)


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

if Addon.getSetting('mac') == None or Addon.getSetting('mac') == '':
	write_mac()	

if Addon.getSetting('requestTimeOut') != None and Addon.getSetting('requestTimeOut') != '':
    req_time = Addon.getSetting('requestTimeOut')
    if req_time == '0':
        sreq_time = 5
    elif req_time == '1':
        sreq_time = 10
    elif req_time == '2':
        sreq_time = 20
    else:
        sreq_time = 30
    
    socket.setdefaulttimeout(sreq_time)
else:
    socket.setdefaulttimeout(10)
    
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
    if pfunc:
        pfunc(params)
