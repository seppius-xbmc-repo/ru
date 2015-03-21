#!/usr/bin/python
# -*- coding: utf-8 -*-
#/*
# *      Copyright (C) 2011 Silen
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
import re, os, urllib, urllib2, cookielib, time, random, sys
from time import gmtime, strftime
import urlparse

fcookies = 'cookies.txt'

# get cookies from last session
cj = cookielib.MozillaCookieJar(fcookies)
hr  = urllib2.HTTPCookieProcessor(cj)
opener = urllib2.build_opener(hr)
urllib2.install_opener(opener)

import xbmc, xbmcgui, xbmcplugin, xbmcaddon

Addon = xbmcaddon.Addon(id='plugin.video.galileo-online.ru')
icon = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'),'icon.png'))
fcookies = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'), r'resources', r'data', r'cookies.txt'))

# load XML library
try:
    sys.path.append(os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib'))
    from BeautifulSoup  import BeautifulSoup
except:
    try:
        sys.path.insert(0, os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib'))
        from BeautifulSoup  import BeautifulSoup
    except:
        sys.path.append(os.path.join(os.getcwd(), r'resources', r'lib'))
        from BeautifulSoup  import BeautifulSoup
        icon = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'icon.png'))

import HTMLParser
hpar = HTMLParser.HTMLParser()

h = int(sys.argv[1])

def showMessage(heading, message, times = 3000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))

def get_HTML(url, post = None, ref = None):
    request = urllib2.Request(url, post)

    host = urlparse.urlsplit(url).hostname
    if ref==None:
        ref='http://'+host

    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host',   host)
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Language', 'ru-RU')
    request.add_header('Referer',             ref)

    try:
        f = urllib2.urlopen(request)
    except IOError, e:
        if hasattr(e, 'reason'):
           print 'We failed to reach a server.'
        elif hasattr(e, 'code'):
           print 'The server couldn\'t fulfill the request.'

    html = f.read()

    return html


#---------- parameter/info structure -------------------------------------------
class Param:
    name    = ''
    page    = '1'
    url     = ''
    season  = ''

class Info:
    img         = ''
    url         = '*'
    title       = ''
    text        = ''

#---------- get parameters -----------------------------------------------------
def Get_Parameters(params):
    #-- name
    try:    p.name = urllib.unquote_plus(params['name'])
    except: p.name = ''
    #-- url
    try:    p.url = urllib.unquote_plus(params['url'])
    except: p.url = ''
    #-- page
    try:    p.page = urllib.unquote_plus(params['page'])
    except: p.page = '1'
    #-- season
    try:    p.season = urllib.unquote_plus(params['season'])
    except: p.seasone = ''
    #-----
    return p

#----------- get Header string ---------------------------------------------------
def Get_Header(par, pcount):

    info = ''

    if pcount > 1:
        info += 'Pages: ' + '[COLOR FF00FF00]'+ par.page + '/' + str(pcount) +'[/COLOR]'

    if pcount > 1:
        info += ' | '
    info += par.season

    if info <> '':
        #-- info line
        name    = info
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=EMPTY'
        u += '&name=%s'%urllib.quote_plus(name)
        #-- filter parameters
        u += '&page=%s'%urllib.quote_plus(par.page)
        u += '&season=%s'%urllib.quote_plus(par.season)
        xbmcplugin.addDirectoryItem(h, u, i, True)

def Empty():
    return False

#---------- movie list ---------------------------------------------------------
def Movie_List(params):
        #-- get filter parameters
        par = Get_Parameters(params)

        #== get movie list =====================================================
        url = par.url

        html = get_HTML(url+'-'+par.page+'-1')

        # -- parsing web page --------------------------------------------------
        soup = BeautifulSoup(html, fromEncoding="windows-1251")

        pcount = 1
        # -- get number of pages
        try:
            for rec in soup.find("span", {"class":"pagesBlockuz1"}).findAll('span'):
                try:
                    if int(rec.text) > pcount:
                        pcount = int(rec.text)
                except:
                    pass
        except:
            pcount = 1

        #-- add header info
        Get_Header(par, pcount)

        #-- first page link
        if int(par.page) > 1:
            name    = '[FIRST PAGE]'
            i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
            u = sys.argv[0] + '?mode=MOVIE'
            u += '&name=%s'%urllib.quote_plus(name)
            #-- filter parameters
            u += '&page=%s'%urllib.quote_plus(str(1))
            u += '&season=%s'%urllib.quote_plus(par.season)
            u += '&url=%s'%urllib.quote_plus(url)
            xbmcplugin.addDirectoryItem(h, u, i, True)

        #-- previus page link
        if int(par.page) > 1 :
            name    = '[PREVIOUS PAGE]'
            i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
            u = sys.argv[0] + '?mode=MOVIE'
            u += '&name=%s'%urllib.quote_plus(name)
            #-- filter parameters
            u += '&page=%s'%urllib.quote_plus(str(int(par.page)-1))
            u += '&season=%s'%urllib.quote_plus(par.season)
            u += '&url=%s'%urllib.quote_plus(url)
            xbmcplugin.addDirectoryItem(h, u, i, True)

        #-- get movie info
        #try:
        for rec in soup.findAll("div", {"id":re.compile("entryID")}):
            title = rec.find("div", {"class":"eTitle"})
            mi.title = title.find('a').text.encode('utf-8')
            mi.url = title.find('a')['href']

            name = '[COLOR FFC3FDB8]'+mi.title+'[/COLOR]'

            detail = rec.find("div", {"class":"eMessage"})
            mi.text = detail.text.replace('?', '? ').encode('utf-8')

            mi.img   = icon #rec.find('img')['src']

            i = xbmcgui.ListItem('[COLOR FF00FFFF]'+mi.title+'[/COLOR]', iconImage=mi.img, thumbnailImage=mi.img)
            u = sys.argv[0] + '?mode=PLAY'
            u += '&name=%s'%urllib.quote_plus(mi.title)
            u += '&url=%s'%urllib.quote_plus(mi.url)
            u += '&img=%s'%urllib.quote_plus(mi.img)
            i.setInfo(type='video', infoLabels={ 'title':      mi.title,
                        						 'plot':       mi.text})
            i.setProperty('fanart_image', mi.img)
            xbmcplugin.addDirectoryItem(h, u, i, False)
        #except:
        #    pass

        #-- next page link
        if int(par.page) < pcount :
            name    = '[NEXT PAGE]'
            i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
            u = sys.argv[0] + '?mode=MOVIE'
            u += '&name=%s'%urllib.quote_plus(name)
            #-- filter parameters
            u += '&page=%s'%urllib.quote_plus(str(int(par.page)+1))
            u += '&season=%s'%urllib.quote_plus(par.season)
            u += '&url=%s'%urllib.quote_plus(url)
            xbmcplugin.addDirectoryItem(h, u, i, True)

        #-- last page link
        if int(par.page) < pcount :
            name    = '[LAST PAGE]'
            i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
            u = sys.argv[0] + '?mode=MOVIE'
            u += '&name=%s'%urllib.quote_plus(name)
            #-- filter parameters
            u += '&page=%s'%urllib.quote_plus(str(pcount))
            u += '&season=%s'%urllib.quote_plus(par.season)
            u += '&url=%s'%urllib.quote_plus(url)
            xbmcplugin.addDirectoryItem(h, u, i, True)

        xbmcplugin.endOfDirectory(h)

#---------- get season list -----------------------------------------------------
def Season_List(params):
    #-- get filter parameters
    par = Get_Parameters(params)

    #-- get generes
    url = 'http://www.galileo-online.ru'

    html = get_HTML(url)

    # -- parsing web page ------------------------------------------------------
    soup = BeautifulSoup(html, fromEncoding="windows-1251")

    flag = 0
    for rec in soup.findAll("td", {"class":"catsTd"}):
        if str(rec.find('a')).find('/load/smotret/1') <> -1:
            flag += 1
        else:
            if flag == 2:
                url  = 'http://www.galileo-online.ru'+rec.find('a')['href']
                name = rec.find('a').text.encode('utf-8')
                name = '[COLOR FFFFF000]'+name.split('(')[0]+'[/COLOR]('+name.split('(')[1]

                i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
                u = sys.argv[0] + '?mode=MOVIE'
                u += '&season=%s'%urllib.quote_plus(name)
                u += '&url=%s'%urllib.quote_plus(url)
                xbmcplugin.addDirectoryItem(h, u, i, True)

    xbmcplugin.endOfDirectory(h)

#-------------------------------------------------------------------------------
def PLAY(params):
    # -- parameters
    url  = urllib.unquote_plus(params['url'])
    img  = urllib.unquote_plus(params['img'])
    name = urllib.unquote_plus(params['name'])

    if url == '*':
        return False

    # -- get video link
    html = get_HTML(url).replace('amp;', '')
    soup = BeautifulSoup(html, fromEncoding="windows-1251")

    for rec in soup.findAll("iframe", {"src":re.compile("vkontakte.ru")}):
        url = rec['src']

    for rec in soup.findAll("iframe", {"src":re.compile("vk.com")}):
        url = rec['src']

    # -- get VKontakte video url
    video = VKontakte(url)

    if video == '':
        return False

    # -- play video
    i = xbmcgui.ListItem(name, path = urllib.unquote(video), thumbnailImage=img)
    xbmc.Player().play(video, i)

#-------------------------------------------------------------------------------
def VKontakte(url):
    url = url.replace('vkontakte.ru', 'vk.com')
    host = ''
    #-- get VKontakte parameters
    html = get_HTML(url)
    soup = BeautifulSoup(html, fromEncoding="windows-1251")
    for rec in soup.findAll('param', {'name':'flashvars'}):
        for s in rec['value'].split('&'):
            if s.split('=',1)[0] == 'uid':
                uid = s.split('=',1)[1]
            if s.split('=',1)[0] == 'vid':
                vid = s.split('=',1)[1]
            if s.split('=',1)[0] == 'oid':
                oid = s.split('=',1)[1]
            if s.split('=',1)[0] == 'vtag':
                vtag = s.split('=',1)[1]
            if s.split('=',1)[0] == 'ltag':
                ltag = s.split('=',1)[1]
            if s.split('=',1)[0] == 'vkid':
                vkid = s.split('=',1)[1]
            if s.split('=',1)[0] == 'host':
                host = s.split('=',1)[1]
            if s.split('=',1)[0] == 'hd':
                hd = s.split('=',1)[1]
            if s.split('=',1)[0] == 'no_flv':
                no_flv = s.split('=',1)[1]
            if s.split('=',1)[0] == 'hd_def':
                hd_def = s.split('=',1)[1]

    if host == '':
        return ''

    if host[:5] != 'http:':
        host = 'http://'+host
    if host[-1:] != '/':
        host += '/'

    #-- build video link
    if int(no_flv) == 0:            #-- FLV link
        rez = "240"
        if int(uid) <= 0:
            video = host+"assets/video/" + vtag + "" + vkid + ".vk.flv"
        else:
            video = host+ "u" + uid + "/videos/" + vtag + ".flv";
    else:                           #-- MP4
        #-- define resolution
        if int(hd) == 1:
            rez = "360"
        elif int(hd) == 2:
            rez = "480"
        elif int(hd) == 3:
            rez = "720"
        else:
            rez = "240"

        #-- build link
        video = '%s/u%s/videos/%s.%s.mp4'%(host, uid, vtag, rez)

    #-- initiate video stream
    url = 'http://vk.com/videostats.php?act=view&oid='+oid+'&vid='+vid+'&quality='+rez
    ref = soup.find('param',{'name':'movie'})['value']
    html = get_HTML(url, None, ref)

    return video

#-------------------------------------------------------------------------------

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

def get_url(url):
    return "http:"+urllib.quote(url.replace('http:', ''))

#-------------------------------------------------------------------------------
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
#-------------------------------------------------------------------------------
params=get_params(sys.argv[2])

# get cookies from last session
cj = cookielib.FileCookieJar(fcookies)
hr  = urllib2.HTTPCookieProcessor(cj)
opener = urllib2.build_opener(hr)
urllib2.install_opener(opener)

p  = Param()
mi = Info()

mode = None

try:
	mode = urllib.unquote_plus(params['mode'])
except:
	Season_List(params)

if mode == 'MOVIE':
	Movie_List(params)
elif mode == 'GENRES':
    Genre_List(params)
elif mode == 'YEAR':
    Year_List(params)
elif mode == 'SEASON':
	Season_List(params)
elif mode == 'EMPTY':
    Empty()
elif mode == 'PLAY':
	PLAY(params)


