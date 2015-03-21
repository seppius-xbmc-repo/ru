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
import re, os, urllib, cookielib, time
from time import gmtime, strftime
import urlparse
#from multiprocessing.process import Process
#-----------------------------------------------
import BaseHTTPServer, cgi
import subprocess, socket, threading
import random, sys, json
from time import gmtime, strftime
from datetime import datetime
import ConfigParser
import shutil

import binascii
import struct
import base64
import math
import xml.etree.ElementTree
import xml.sax
#from urlparse import urlparse, urlunparse
import string
import unicodedata
import Queue
import thread
#-----------------------------------------------

import urllib2
try:
    import urllib3
    from urllib3.exceptions import HTTPError
    hasUrllib3 = True
except ImportError:
    #import urllib2
    from urllib2 import HTTPError
    hasUrllib3 = False


import xbmc, xbmcgui, xbmcplugin, xbmcaddon

Addon = xbmcaddon.Addon(id='plugin.video.my-hit.ru')
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

host_url = 'https://my-hit.org'
movie_url = None

def showMessage(heading, message, times = 3000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))

#---------- parameter/info structure -------------------------------------------
class Param:
    page    = '1'
    genre   = ''
    genre_name = ''
    country  = ''
    country_name = ''
    year    = ''
    year_name = ''
    search  = ''

class Info:
    img         = ''
    url         = '*'
    title       = ''
    year        = ''
    genre       = ''
    country     = ''
    director    = ''
    text        = ''

#---------- get parameters -----------------------------------------------------
def Get_Parameters(params):
    #-- page
    try:    p.page = urllib.unquote_plus(params['page'])
    except: p.page = '1'
    #-- genre
    try:    p.genre = urllib.unquote_plus(params['genre'])
    except: p.genre = ''
    try:    p.genre_name = urllib.unquote_plus(params['genre_name'])
    except: p.genre_name = ''
    #-- country
    try:    p.country = urllib.unquote_plus(params['country'])
    except: p.country = ''
    try:    p.country_name = urllib.unquote_plus(params['country_name'])
    except: p.country_name = ''
    #-- year
    try:    p.year = urllib.unquote_plus(params['year'])
    except: p.year = ''
    try:    p.year_name = urllib.unquote_plus(params['year_name'])
    except: p.year_name = ''
    #--search
    try:    p.search = urllib.unquote_plus(params['search'])
    except: p.search = ''
    #-----
    return p

#---------- get web page -------------------------------------------------------
def get_HTML(url, post = None, ref = None):
    #xbmc.log(url)

    request = urllib2.Request(url, post)

    host = urlparse.urlsplit(url).hostname

    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host',   host)
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Language', 'ru-RU')
    request.add_header('Referer',             ref)

    try:
        f = urllib2.urlopen(request)
    except IOError, e:
        if hasattr(e, 'reason'):
           xbmc.log('We failed to reach a server.')
        elif hasattr(e, 'code'):
           xbmc.log('The server couldn\'t fulfill the request.')

    html = f.read()

    return html

#---------- get MY-HIT.RU URL --------------------------------------------------
def Get_URL(par):
    # http://my-hit.ru/index.php?module=search&func=view&result_orderby=score&result_order_asc=0&search_string=%EA%E8%ED&x=0&y=0

    url = 'https://my-hit.org/film/'

    par_div = ''
    filter  = ''
    #-- year
    if par.year <> '':
        if filter != '':
            filter += '-'
        filter += par.year
        par_div = '/'
    #-- genre
    if par.genre <> '':
        if filter != '':
            filter += '-'
        filter += par.genre
        par_div = '/'
    #-- country
    if par.country <> '':
        if filter != '':
            filter += '-'
        filter += par.country
        par_div = '/'
    #-- page
    url += filter+par_div+'?p='+par.page

    return url

#----------- get Header string ---------------------------------------------------
def Get_Header(par, mcount, pcount):

    info  = 'Фильмов: ' + '[COLOR FF00FF00]' + str(mcount) + '[/COLOR]'

    if pcount > 1:
        info += ' | Pages: ' + '[COLOR FF00FF00]'+ par.page + '/' + str(pcount) +'[/COLOR]'

    if par.genre <> '':
        info += ' | Жанр: ' + '[COLOR FF00FFF0]'+ par.genre_name + '[/COLOR]'

    if par.year <> '':
        info += ' | Год: ' + '[COLOR FFFFF000]'+ par.year_name + '[/COLOR]'

    if par.country <> '':
        info += ' | Страна: ' + '[COLOR FFFF00FF]'+ par.country_name + '[/COLOR]'

    if par.search <> '':
        info += ' | Поиск: ' + '[COLOR FFFF9933]'+ par.search + '[/COLOR]'

    #-- info line
    name    = info
    i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
    u = sys.argv[0] + '?mode=EMPTY'
    u += '&name=%s'%urllib.quote_plus(name)
    #-- filter parameters
    u += '&page=%s'%urllib.quote_plus(par.page)
    u += '&genre=%s'%urllib.quote_plus(par.genre)
    u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
    u += '&country=%s'%urllib.quote_plus(par.country)
    u += '&country_name=%s'%urllib.quote_plus(par.country_name)
    u += '&year=%s'%urllib.quote_plus(par.year)
    u += '&year_name=%s'%urllib.quote_plus(par.year_name)
    xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- search
    '''
    if par.genre == '' and par.country == '' and par.page == '1' and par.search == '':
        name    = '[COLOR FFFF9933][Поиск][/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=SEARCH'
        u += '&name=%s'%urllib.quote_plus(name)
        #-- filter parameters
        u += '&page=%s'%urllib.quote_plus(par.page)
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&country=%s'%urllib.quote_plus(par.country)
        u += '&country_name=%s'%urllib.quote_plus(par.country_name)
        u += '&year=%s'%urllib.quote_plus(par.year)
        u += '&year_name=%s'%urllib.quote_plus(par.year_name)
        xbmcplugin.addDirectoryItem(h, u, i, True)
    '''
    #-- genres
    if par.genre == '' and par.page == '1' and par.search == '':
        name    = '[COLOR FF00FFF0][Жанры][/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=GENRES'
        u += '&name=%s'%urllib.quote_plus(name)
        #-- filter parameters
        u += '&page=%s'%urllib.quote_plus(par.page)
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&country=%s'%urllib.quote_plus(par.country)
        u += '&country_name=%s'%urllib.quote_plus(par.country_name)
        u += '&year=%s'%urllib.quote_plus(par.year)
        u += '&year_name=%s'%urllib.quote_plus(par.year_name)
        xbmcplugin.addDirectoryItem(h, u, i, True)
    #-- alphabet
    if par.country == '' and par.page == '1' and par.search == '':
        name    = '[COLOR FFFF00FF][Страна][/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=COUNTRY'
        u += '&name=%s'%urllib.quote_plus(name)
        #-- filter parameters
        u += '&page=%s'%urllib.quote_plus(par.page)
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&country=%s'%urllib.quote_plus(par.country)
        u += '&country_name=%s'%urllib.quote_plus(par.country_name)
        u += '&year=%s'%urllib.quote_plus(par.year)
        u += '&year_name=%s'%urllib.quote_plus(par.year_name)
        xbmcplugin.addDirectoryItem(h, u, i, True)
    #-- year
    if par.year == '' and par.page == '1' and par.search == '':
        name    = '[COLOR FFFFF000][Год][/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=YEAR'
        u += '&name=%s'%urllib.quote_plus(name)
        #-- filter parameters
        u += '&page=%s'%urllib.quote_plus(par.page)
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&country=%s'%urllib.quote_plus(par.country)
        u += '&country_name=%s'%urllib.quote_plus(par.country_name)
        u += '&year=%s'%urllib.quote_plus(par.year)
        u += '&year_name=%s'%urllib.quote_plus(par.year_name)
        xbmcplugin.addDirectoryItem(h, u, i, True)

def Empty():
    return False

#---------- movie list ---------------------------------------------------------
def Movie_List(params):
        #-- get filter parameters
        par = Get_Parameters(params)

        #== get movie list =====================================================
        url = Get_URL(par)
        #print url
        html = get_HTML(url)

        # -- parsing web page --------------------------------------------------
        soup = BeautifulSoup(html)

        pcount = 1
        mcount = 0

        pinfo = soup.find('div', {'class':"col-sm-10 col-md-8"}).find('div', {'class':"col-sm-3"}).text.split(':')[1].replace('(','').replace(')','')
        mcount = int(pinfo.split(' ')[0])
        pfilm  = int(pinfo.split(' ')[1].split('-')[1])
        pcount = mcount/pfilm+1

        Get_Header(par, mcount, pcount)

        nav = soup.find("div", { "class" : "film-list" })

        for mov in nav.findAll("div", { "class" : "row" }):
			mi.title	= mov.find('div', {'class':'col-sm-3 text-center'}).find('a')['title'].encode('utf-8')
			mi.url		= host_url + mov.find('div', {'class':'col-sm-3 text-center'}).find('a')['href']
			mi.img		= host_url + mov.find('div', {'class':'col-sm-3 text-center'}).find('a').find('img')['src']

			for li in mov.find('ul', {'class':"list-unstyled"}).findAll('li'):
				if li.find('b').text == u'Год:':
					mi.year		= li.find('a').text.encode('utf-8')
				if li.find('b').text == u'Жанр:':
					mi.genre	= li.find('a').text.encode('utf-8')
				if li.find('b').text == u'Страна':
					mi.country	= li.find('a').text.encode('utf-8')
				if li.find('b').text == u'Режиссер:':
					mi.director	= li.find('a').text.encode('utf-8')
				if li.find('b').text == u'Краткое описание:':
					mi.text		= li.find('p').text.encode('utf-8')

            #-- add movie to the list ---------------------------------------
			if mi.url == '*':
				name = '[COLOR FFFF0000]'+mi.title+'[/COLOR]'
			else:
				name = '[COLOR FFC3FDB8]'+mi.title+'[/COLOR]'

			i = xbmcgui.ListItem(name, iconImage=mi.img, thumbnailImage=mi.img)
			u = sys.argv[0] + '?mode=PLAY_MODE'
			u += '&name=%s'%urllib.quote_plus(mi.title)
			u += '&url=%s'%urllib.quote_plus(mi.url)
			u += '&img=%s'%urllib.quote_plus(mi.img)
			i.setInfo(type='video', infoLabels={ 'title':      mi.title,
                        						'year':        mi.year,
                        						'director':    mi.director,
                        						'plot':        mi.text,
                        						'country':     mi.country,
                        						'genre':       mi.genre})
			i.setProperty('fanart_image', mi.img)
			xbmcplugin.addDirectoryItem(h, u, i, True)

        #-- next page link
        if int(par.page) < pcount :
            name    = '[NEXT PAGE]'
            i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
            u = sys.argv[0] + '?mode=MOVIE'
            u += '&name=%s'%urllib.quote_plus(name)
            #-- filter parameters
            u += '&page=%s'%urllib.quote_plus(str(int(par.page)+1))
            u += '&genre=%s'%urllib.quote_plus(par.genre)
            u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
            u += '&country=%s'%urllib.quote_plus(par.country)
            u += '&country_name=%s'%urllib.quote_plus(par.country_name)
            u += '&year=%s'%urllib.quote_plus(par.year)
            u += '&year_name=%s'%urllib.quote_plus(par.year_name)
            xbmcplugin.addDirectoryItem(h, u, i, True)

        xbmcplugin.endOfDirectory(h)

#---------- search movie list --------------------------------------------------
def Search_List(params):
        list = []
        #-- get filter parameters
        par = Get_Parameters(params)

        # show search dialog
        skbd = xbmc.Keyboard()
        skbd.setHeading('Поиск фильмов.')
        skbd.doModal()
        if skbd.isConfirmed():
            SearchStr = skbd.getText().split(':')
            par.search = SearchStr[0]
        else:
            return False

        #== get movie list =====================================================
        url = 'http://my-hit.org/index.php?module=search&func=view&result_orderby=score&result_order_asc=0&result_perpage=1000&search_string=%s&x=0&y=0'%urllib.quote(par.search.decode('utf-8').encode('cp1251'))
        #print url
        html = get_HTML(url)

        # -- parsing web page --------------------------------------------------
        soup = BeautifulSoup(html, fromEncoding="windows-1251")

        pcount = 1
        mcount = 0

        # -- get list of found movies
        flag = 0
        for rec in soup.findAll("tr"):
            try:
                if rec.find('a').text.find(u'(фильм)')<>-1:
                    m_name = rec.find('a').text.replace(u'(фильм)', '').encode('utf-8')
                    flag = 1
                elif flag==1:
                    m_url  = rec.find('a')['href']
                    m_url = 'http://my-hit.org/film/'+m_url.split('&id=')[1]+'/online'

                    m_img  = 'http://my-hit.org'+rec.find('img')['src']
                    m_text = unescape(rec.text).encode('utf-8')
                    flag = 0
                    list.append({'name':m_name, 'url':m_url, 'img':m_img, 'text':m_text})
            except:
                pass
        mcount = len(list)

        if mcount == 0:
            return False

        #-- add header info
        Get_Header(par, mcount, pcount)

        for mov in list:
            #-- add movie to the list ------------------------------------------
            name = '[COLOR FFC3FDB8]'+mov['name']+'[/COLOR]'

            i = xbmcgui.ListItem(name, iconImage=mi.img, thumbnailImage=mi.img)
            u = sys.argv[0] + '?mode=PLAY'
            u += '&name=%s'%urllib.quote_plus(mov['name'])
            u += '&url=%s'%urllib.quote_plus(mov['url'])
            u += '&img=%s'%urllib.quote_plus(mov['img'])
            i.setInfo(type='video', infoLabels={ 'title':      mov['name'],
                        						'plot':        mov['text']})
            i.setProperty('fanart_image', mov['img'])
            xbmcplugin.addDirectoryItem(h, u, i, False)

        xbmcplugin.endOfDirectory(h)

#---------- get genge list -----------------------------------------------------
def Genre_List(params):
    #-- get filter parameters
    par = Get_Parameters(params)

    #-- get generes
    url = 'https://my-hit.org/film/'
    html = get_HTML(url)

    # -- parsing web page ------------------------------------------------------
    soup = BeautifulSoup(html)
    nav = soup.find('div', {'class':"sidebar-nav"}).find('ul', {'class':"nav nav-list"})
    is_genre = False

    for item in nav.findAll('li'):
    	if item.get('class') == "nav-header":
    		if is_genre == False and item.text == u'Жанр :':
    			is_genre = True
    		else:
    			is_genre = False

        if is_genre:
            if item.find('a'):
                name = (item.find('a').text).encode('utf-8')
                genre_id = item.find('a').get('href').replace('/film/','').replace('/','')
    			#---
                i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
    	        u = sys.argv[0] + '?mode=MOVIE'
    	        u += '&name=%s'%urllib.quote_plus(name)
    	        #-- filter parameters
    	        u += '&page=%s'%urllib.quote_plus(par.page)
    	        u += '&genre=%s'%urllib.quote_plus(genre_id)
    	        u += '&genre_name=%s'%urllib.quote_plus(name)
    	        u += '&country=%s'%urllib.quote_plus(par.country)
    	        u += '&country_name=%s'%urllib.quote_plus(par.country_name)
    	        u += '&year=%s'%urllib.quote_plus(par.year)
                u += '&year_name=%s'%urllib.quote_plus(par.year_name)
    	        xbmcplugin.addDirectoryItem(h, u, i, True)

    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(h)

#---------- get year list -----------------------------------------------------
def Year_List(params):
    #-- get filter parameters
    par = Get_Parameters(params)

    #-- get generes
    url = 'https://my-hit.org/film/'
    html = get_HTML(url)

    # -- parsing web page ------------------------------------------------------
    soup = BeautifulSoup(html)
    nav = soup.find('div', {'class':"sidebar-nav"}).find('ul', {'class':"nav nav-list"})
    is_year = False
    is_Found = False

    for item in nav.findAll('li'):
    	if item.get('class') == "nav-header":
    		if is_year == False and item.text == u'Год :':
    			is_year = True
    		else:
    			is_year = False

        if is_year:
            if item.find('a'):
                if item.find('a')['href']=='#':
                    is_Found = True
                    continue

        if is_Found:
            if item.find('a'):
                name = (item.find('a').text).encode('utf-8')
                year_id = item.find('a').get('href').replace('/film/','').replace('/','')
    			#---
                i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
                u = sys.argv[0] + '?mode=MOVIE'
                u += '&name=%s'%urllib.quote_plus(name)
                #-- filter parameters
                u += '&page=%s'%urllib.quote_plus(par.page)
                u += '&genre=%s'%urllib.quote_plus(par.genre)
                u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
                u += '&country=%s'%urllib.quote_plus(par.country)
                u += '&country_name=%s'%urllib.quote_plus(par.country_name)
                u += '&year=%s'%urllib.quote_plus(year_id)
                u += '&year_name=%s'%urllib.quote_plus(name)
                xbmcplugin.addDirectoryItem(h, u, i, True)

    xbmcplugin.endOfDirectory(h)

#---------- get year list -----------------------------------------------------
def Country_List(params):
    #-- get filter parameters
    par = Get_Parameters(params)

    #-- get generes
    url = 'https://my-hit.org/film/'
    html = get_HTML(url)

    # -- parsing web page ------------------------------------------------------
    soup = BeautifulSoup(html)
    nav = soup.find('div', {'class':"sidebar-nav"}).find('ul', {'class':"nav nav-list"})
    is_year = False

    for item in nav.findAll('li'):
    	if item.get('class') == "nav-header":
    		if is_year == False and item.text == u'Страны :':
    			is_year = True
    		else:
    			is_year = False

        if is_year:
            if item.find('a'):
                name = (item.find('a').text).encode('utf-8')
                country_id = item.find('a').get('href').replace('/film/','').replace('/','')
    			#---
                i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
                u = sys.argv[0] + '?mode=MOVIE'
                u += '&name=%s'%urllib.quote_plus(name)
                #-- filter parameters
                u += '&page=%s'%urllib.quote_plus(par.page)
                u += '&genre=%s'%urllib.quote_plus(par.genre)
                u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
                u += '&country=%s'%urllib.quote_plus(country_id)
                u += '&country_name=%s'%urllib.quote_plus(name)
                u += '&year=%s'%urllib.quote_plus(par.year)
                u += '&year_name=%s'%urllib.quote_plus(par.year_name)
                xbmcplugin.addDirectoryItem(h, u, i, True)

    xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(h)

#---------- show availabl;e video sources --------------------------------------
def Play_Mode(params):
    #-- get filter parameters
    par = Get_Parameters(params)

    url  = urllib.unquote_plus(params['url'])+'online/'
    img  = urllib.unquote_plus(params['img'])
    name = urllib.unquote_plus(params['name'])

    #-- get play list
    html = get_HTML(url)
    pl = re.compile(u'var flashvars \= \{(.+?)\}', re.MULTILINE|re.DOTALL).findall(html)[0].replace("'",'')
    #xbmc.log(pl)
    for rec in pl.split(','):
        if rec.strip().split(':', 1)[0] == 'pl':
            url = 'https://my-hit.org'+ rec.split(':', 1)[1].strip()
            url_type = 'PL'
        if rec.strip().split(':')[0] == 'file':
            url = rec.split(':', 1)[1].strip()
            url_type = 'FILE'

    list = []
    #xbmc.log(url_type)
    try:
        if url_type == 'PL':
            html = get_HTML(url)

            for rec in json.loads(html)['playlist']:
                #xbmc.log('.....')
                #xbmc.log(rec['file'])
                _url = rec['file']
                _img = rec['poster']
                list.append({'url': _url, 'img': _img, 'type': 'AHDS'})
            '''
            mov = re.compile(u'\[\{"file":"(.+?)"', re.MULTILINE|re.DOTALL).findall(html)[0]

            mov =  mov.replace('\\','').replace('[','#').replace(']','#')
            mov_u = mov.split('#')

            xbmc.log(mov)
            '''
            mov_q_def = {'9':'1080p', '8':' 720p', '7':' 480p', '6':' 360p', '5':' 320p', '4':' 240p'}
        else:
            list.append({'url': url, 'img': img, 'type': 'AHDS'})

        #-- old movie format
        for mov in list:
            #xbmc.log('---')
            #xbmc.log(mov['url'])
            name_ = '[COLOR FFC3FDB8]'+name+'[/COLOR]'
            i = xbmcgui.ListItem(name_, iconImage=img, thumbnailImage=img)
            u = sys.argv[0] + '?mode=PLAY'
            u += '&name=%s'%urllib.quote_plus('[COLOR FFC3FDB8]'+name+'[/COLOR]')
            u += '&url=%s'%urllib.quote_plus(mov['url'])
            u += '&img=%s'%urllib.quote_plus(img)
            u += '&type=%s'%urllib.quote_plus(mov['type'])
            i.setProperty('fanart_image', img)
            xbmcplugin.addDirectoryItem(h, u, i, False)
    except:
        pass

    #xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(h)


#-------------------------------------------------------------------------------

def PLAY(params):
    global movie_url, IP_ADDRESS, PORT_NUMBER, PROXY_THREADS
    # -- parameters
    movie_url   = urllib.unquote_plus(params['url'])
    img         = urllib.unquote_plus(params['img'])
    name        = urllib.unquote_plus(params['name'])
    type_       = urllib.unquote_plus(params['type'])

    #xbmc.log('-------------')
    #xbmc.log(type_)

    if type_ == 'FLV':
        i = xbmcgui.ListItem(name, path = urllib.unquote(movie_url), thumbnailImage=img)
        xbmc.Player().play(movie_url, i)
    else:
        #-- get video proxy settings
        if Addon.getSetting('Proxy_IP') == '127.0.0.1':
            IP_ADDRESS      = 'localhost'
        else:
            IP_ADDRESS      = Addon.getSetting('Proxy_IP')

        PROXY_THREADS   = Addon.getSetting('Proxy_Thread')
        PORT_NUMBER     = Addon.getSetting('Proxy_Port')
        #-- run video Proxy server ---
        t = threading.Thread(target=VideoProxy)
        t.start()

        #-- wait and play video ------
        #time.sleep(5)
        player = AdobeHDS_Player()
        player.Init(movie_url, name, img)
        player.play_start()

#-------------------------------------------------------------------------------

class AdobeHDS_Player(xbmc.Player) :

    def __init__ (self):
            xbmc.Player.__init__(self)

    def Init(self, url, name, img):
            self.url    = url
            self.name   = name
            self.img    = img

    def play_start(self):
            video = 'http://'+IP_ADDRESS+':'+PORT_NUMBER+'/?video='+base64.urlsafe_b64encode(self.url)
            i = xbmcgui.ListItem(self.name, path = urllib.unquote(video), thumbnailImage=self.img)
            self.play(video, i)

    def __del__(self):
            pass

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
#-------------------------------------------------------------------------------
IP_ADDRESS          = '127.0.0.1'
PORT_NUMBER         = 88
PROXY_THREADS       = 7

pSocket = None

def get_local_ip_address(target):
  ipaddr = ''
  try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((target, 8000))
    ipaddr = s.getsockname()[0]
    s.close()
  except:
    pass

  return ipaddr

#-------------------------------------------------------------------------------
class GetUrl(object):
    def __init__(self, url, fragnum):
        self.url = url
        self.fragNum = fragnum
        self.data = None
        self.decode = None
        self.errCount = 0

QueueUrl = Queue.PriorityQueue()
QueueUrlDone = Queue.PriorityQueue()

M6Item = None
prevAudioTS = -1;
prevVideoTS = -1;
baseTS = 0;

def workerRun():
    global QueueUrl, QueueUrlDone, M6Item, PROXY_THREADS
    while not QueueUrl.empty() and M6Item.status == 'DOWNLOADING' and QueueUrlDone.qsize() < int(PROXY_THREADS)*3:
        item = QueueUrl.get()[1]
        #print 'Processing Fragment: ',item.fragNum
        fragUrl = item.url
        try:
            item.data = M6Item.getFile(fragUrl)
            QueueUrlDone.put((item.fragNum, item))
            #print fragUrl
        except HTTPError, e:
            xbmc.log(str(e))
            if item.errCount > 3:
                M6Item.status = 'STOPPED'
                # raise
            else:
                item.errCount += 1
                QueueUrl.put((item.fragNum, item))
        QueueUrl.task_done()
    # If we have exited the previous loop with error
    while not QueueUrl.empty():
        #print 'Ignore fragment', QueueUrl.get()[1].fragNum
        QueueUrl.get()

def worker():
    global M6Item
    try:
        workerRun()
    except Exception, e:
        #print 'ERROR worker'
        M6Item.status = 'STOPPED'
        thread.interrupt_main()

def workerqdRun():
    global QueueUrlDone, M6Item
    currentFrag = 1
    while currentFrag <= M6Item.nbFragments and M6Item.status == 'DOWNLOADING':
        item = QueueUrlDone.get()[1]
        #print 'Done Fragment: ' + str(item.fragNum)
        if currentFrag == item.fragNum:
            # M6Item.verifyFragment(item.data)
            if not M6Item.decodeFragment(item):
                raise Exception('decodeFrament')
            M6Item.videoFragment(item.fragNum, item.decode)
            #print 'Fragment', currentFrag, 'OK'
            currentFrag += 1
            requeue = False
        else:
            #print 'Requeue', item.fragNum
            QueueUrlDone.put((item.fragNum, item))
            requeue = True
        QueueUrlDone.task_done()
        if requeue:
            time.sleep(1)
    # If we have exited the previous loop with error
    if currentFrag > M6Item.nbFragments:
        M6Item.status = 'COMPLETED'
    else:
        while not QueueUrlDone.empty():
            #print 'Ignore fragment', QueueUrlDone.get()[1].fragNum
            pass

def workerqd():
    global M6Item
    try:
        workerqdRun()
    except Exception, e:
        #print 'ERROR workerqd'
        M6Item.status = 'STOPPED'
        thread.interrupt_main()

validFilenameChars = "-_.() %s%s" % (string.ascii_letters, string.digits)

def removeDisallowedFilenameChars(filename):
    "Remove invalid filename characters"
    filename = filename.decode('ASCII', 'ignore')
    cleanedFilename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore')
    cleanedFilename = cleanedFilename.replace(' ', '_')
    return ''.join(c for c in cleanedFilename if c in validFilenameChars)

class M6(object):
    def __init__(self, url, dest = '', proxy=None):
        self.status = 'INIT'
        self.url = url
        self.proxy = proxy
        self.bitrate = 0
        self.duration = 0
        self.nbFragments = 0
        self.tagHeaderLen = 11
        self.prevTagSize = 4

        urlp = urlparse.urlparse(url)

        fn = os.path.basename(urlp.path)
        self.localfilename = \
            os.path.join(dest, os.path.splitext(fn)[0]) + '.flv'
        self.localfilename = removeDisallowedFilenameChars(self.localfilename)
        self.urlbootstrap = ''
        self.bootstrapInfoId = ''
        self.baseUrl = urlparse.urlunparse((urlp.scheme, urlp.netloc,
                                            os.path.dirname(urlp.path),
                                            '', '', ''))
        if hasUrllib3:
            self.pm = urllib3.PoolManager(num_pools=100)

        self.html = self.getManifest(self.url)
        self.manifest = xml.etree.ElementTree.fromstring(self.html)
        self.parseManifest()
        # self.pm = urllib3.connection_from_url(self.urlbootstrap)
        #---
        global prevAudioTS
        global prevVideoTS
        global baseTS

        prevAudioTS = -1;
        prevVideoTS = -1;
        baseTS = 0;

        #print '#################'

    def download(self):
        global QueueUrl, QueueUrlDone, M6Item, PROXY_THREADS
        M6Item = self
        self.status = 'DOWNLOADING'
        #print self.status
        #print 'nbFragments:   '+ str(self.nbFragments)
        #print 'PROXY_THREADS: '+ str(PROXY_THREADS)
        # self.outFile = open(self.localfilename, "wb")

        for i in range(self.nbFragments):
            fragUrl = self.urlbootstrap + 'Seg1-Frag'+str(i + 1)
            #xbmc.log(fragUrl)
            QueueUrl.put((i + 1, GetUrl(fragUrl, i + 1)))

        #print '[Queue len]:   '+ str(QueueUrl.qsize())

        t = threading.Thread(target=workerqd)
        #t.daemon = True
        t.start()
        #print 'Proxy process run'

        for i in range(int(PROXY_THREADS)):
            #print 'Run downloader '+ str(i)
            t = threading.Thread(target=worker)
            #t.daemon = True
            t.start()

        # QueueUrl.join()
        # QueueUrlDone.join()
        while self.status == 'DOWNLOADING':
            try:
                #print '[Queue len]:   '+ str(QueueUrl.qsize())
                time.sleep(3)
            except (KeyboardInterrupt, Exception), e:
                print e
                self.status = 'STOPPED'
        # self.outFile.close()
        if self.status != 'STOPPED':
            self.status = 'COMPLETED'

    def getInfos(self):
        infos = {}
        infos['status']        = self.status
        infos['localfilename'] = self.localfilename
        infos['proxy']         = self.proxy
        infos['url']           = self.url
        infos['bitrate']       = self.bitrate
        infos['duration']      = self.duration
        infos['nbFragments']   = self.nbFragments
        infos['urlbootstrap']  = self.urlbootstrap
        infos['baseUrl']       = self.baseUrl
        infos['drmId']         = self.drmAdditionalHeaderId
        return infos

##    if hasUrllib3:
##        def getFile(self, url):
##            headers = urllib3.make_headers(
##                keep_alive=True,
##                user_agent='Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:17.0) Gecko/20100101 Firefox/17.0',
##                X-DevTools-Emulate-Network-Conditions-Client-Id = '22D8BD39-46AD-4AE2-8BCA-4FDDCD99E9B2',
##                accept_encoding=True)
##            r = self.pm.request('GET', url, headers=headers)
##            if r.status != 200:
##                print 'Error downloading', r.status, url
##                # sys.exit(1)
##            return r.data
##    else:
    def getFile(self, url):
        txheaders = {'User-Agent':
                     'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:17.0) Gecko/20100101 Firefox/17.0',
                     'X-DevTools-Emulate-Network-Conditions-Client-Id' : '22D8BD39-46AD-4AE2-8BCA-4FDDCD99E9B2',
                     'Keep-Alive' : '600',
                     'Connection' : 'keep-alive'
                     }
        request = urllib2.Request(url, None, txheaders)
        response = urllib2.urlopen(request)
        return response.read()

    def getManifest(self, url):
        self.status = 'GETTING MANIFEST'
        return self.getFile(url) #xml.etree.ElementTree.fromstring(self.getFile(url))

    def parseManifest(self):
        self.status = 'PARSING MANIFEST'
        try:
            root = self.manifest
            # Duration
            self.duration = float(root.find("{http://ns.adobe.com/f4m/1.0}duration").text)
            # nombre de fragment"
            self.nbFragments = int(math.ceil(self.duration/3))
            # streamid
            self.streamid = root.findall("{http://ns.adobe.com/f4m/1.0}media")[-1]
            # media
            self.media = None
            for media in root.findall('{http://ns.adobe.com/f4m/1.0}media'):
                if int(media.attrib['bitrate']) > self.bitrate:
                    self.media = media
                    self.bitrate = int(media.attrib['bitrate'])
                    self.bootstrapInfoId = media.attrib['bootstrapInfoId']

                    try:
                        self.drmAdditionalHeaderId = media.attrib['drmAdditionalHeaderId']
                    except:
                        self.drmAdditionalHeaderId = None

                    self.flvHeader = base64.b64decode(media.find("{http://ns.adobe.com/f4m/1.0}metadata").text)
            # Bootstrap URL
            self.urlbootstrap = self.media.attrib["url"]
            # urlbootstrap
            self.urlbootstrap = self.baseUrl + "/" + self.urlbootstrap
        except Exception, e:
            print("Not possible to parse the manifest")
            print e
            sys.exit(-1)

    def stop(self):
        self.status = 'STOPPED'

    def videoFragment(self, fragNum, data):
        global pSocket
        start = M6Item.videostart(fragNum, data)
        if fragNum == 1:
            self.videoBootstrap()
        pSocket.wfile.write(data[start:])

    def videoBootstrap(self):
        global pSocket
        bootstrap = "464c560105000000090000000012"
        bootstrap += "%06X" % (len(self.flvHeader),)
        bootstrap += "%06X%08X" % (0, 0)
        pSocket.wfile.write(binascii.a2b_hex(bootstrap))
        pSocket.wfile.write(self.flvHeader)
        pSocket.wfile.write(binascii.a2b_hex("%08X" % (len(self.flvHeader)+11)))
        #pSocket.wfile.write(binascii.a2b_hex("000002cf0800000400000000000000af0011900000000f0800020200000000")) # 00019209

    def videostart(self, fragNum, fragData):
        start = fragData.find("mdat") + 4
        '''
        if (fragNum == 1):
            start = fragData.find("mdat") + 12
            start += 0
        else:
            start = fragData.find("mdat") + 4

        start = fragData.find("mdat") + 12
        # For all fragment (except frag1)
        if (fragNum == 1):
            start += 0
        else:
            # Skip 2 FLV tags
            tagLen, = struct.unpack_from(">L", fragData, start)  # Read 32 bits (big endian)
            tagLen &= 0x00ffffff  # Take the last 24 bits
            start += tagLen + self.tagHeaderLen + 4 +18 # 11 = tag header len ; 4 = tag footer len  +18
        '''
        return start

    def readBoxHeader(self, data, pos=0):
        boxSize, = struct.unpack_from(">L", data, pos)  # Read 32 bits (big endian)struct.unpack_from(">L", data, pos)  # Read 32 bits (big endian)
        boxType = data[pos + 4 : pos + 8]
        if boxSize == 1:
            boxSize, = struct.unpack_from(">Q", data, pos + 8)  # Read 64 bits (big endian)
            boxSize -= 16
            pos += 16
        else:
            boxSize -= 8
            pos += 8
        if boxSize <= 0:
            boxSize = 0
        return (pos, boxType, boxSize)

    def verifyFragment(self, data):
        pos = 0
        fragLen = len(data)
        while pos < fragLen:
            pos, boxType, boxSize = self.readBoxHeader(data, pos)
            if boxType == 'mdat':
                slen = len(data[pos:])
                # print 'mdat %s' % (slen,)
                if boxSize and slen == boxSize:
                    return True
                else:
                    boxSize = fraglen - pos
            pos += boxSize
        return False

    def decodeFragment(self, item):
        item.decode = 'mdat'

        global prevAudioTS
        global prevVideoTS
        global baseTS

        fragPos = 0
        fragLen = len(item.data)
        if not self.verifyFragment(item.data):
            #print "Skipping fragment number", item.fragNum
            return false
        while fragPos < fragLen:
            fragPos, boxType, boxSize = self.readBoxHeader(item.data, fragPos)
            if boxType == 'mdat':
                #fragLen = fragPos + boxSize   # !!!
                break
            fragPos += boxSize

        cnt = 1
        while fragPos < fragLen:
            packetType = self.readInt8(item.data, fragPos)
            packetSize = self.readInt24(item.data, fragPos + 1)
            packetTS = self.readInt24(item.data, fragPos + 4)
            packetTS |= self.readInt8(item.data, fragPos + 7) << 24

            if packetTS & 0x80000000:
                packetTS &= 0x7FFFFFFF
                #---
                struct.pack_into(">L", item.data, fragPos, int(packetTS & 0x00FFFFFF))
                struct.pack_into(">c", item.data, fragPos, ((packetTS & 0xFF000000) >> 24))

            if (baseTS == 0 and ((packetType == 0x08) or (packetType == 0x09))):
                baseTS = packetTS

            if (baseTS > 1000):
                packetTS -= baseTS;
                #---
                struct.pack_into(">L", item.data, fragPos, int(packetTS & 0x00FFFFFF))
                struct.pack_into(">c", item.data, fragPos, ((packetTS & 0xFF000000) >> 24))

            totalTagLen = self.tagHeaderLen + packetSize + self.prevTagSize
            #-- save decoded data
            if packetSize > 32:
                if packetType == 0x08 and packetTS >= prevAudioTS - 8 * 5:      #-- AUDIO  (time_code duration = 8)
                    item.decode += item.data[fragPos:fragPos+totalTagLen]
                    cnt+=1
                    prevAudioTS = packetTS
                elif packetType == 0x09 and packetTS >= prevVideoTS - 8 * 5:      #-- VIDEO  (time_code duration = 8)
                    item.decode += item.data[fragPos:fragPos+totalTagLen] # +'#'+str(cnt)+'#'
                    cnt+=1
                    prevVideoTS = packetTS

            # time.sleep(1)
            if packetType in (10, 11):
                print "This stream is encrypted with Akamai DRM. Decryption of such streams isn't currently possible with this script."
                return False
            if packetType in (40, 41):
                print "This stream is encrypted with FlashAccess DRM. Decryption of such streams isn't currently possible with this script."
                return False
            fragPos += totalTagLen
        return True

    def readInt8(self, data, pos):
        return ord(struct.unpack_from(">c", data, pos)[0])

    def readInt24(self, data, pos):
        return struct.unpack_from(">L", "\0" + data[pos:pos + 3], 0)[0]
#-------------------------------------------------------------------------------
def VideoProxy():
    server_class = ProxyServer
    print '=== START VIDEO PROXY ===='
    print '= IP:    '+IP_ADDRESS
    print '= PORT:  '+PORT_NUMBER
    print '=========================='
    httpd = server_class((IP_ADDRESS, int(PORT_NUMBER)), MyHandler)

    httpd.serve_forever()

#-------------------------------------------------------------------------------
#------------- HTTP server -----------------------------------------------------
class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
     def do_HEAD(s):
         s.send_response(200)
         s.send_header("Content-type", "text/html")
         s.end_headers()

     #-- perform reinitialization of the session on GET request
     def do_GET(s):
         global QueueUrl, QueueUrlDone, M6Item
         CHUNKSIZE = 1024

         #-- get video info ----------------------------
         try:
            video_url = urlparse.parse_qs(urlparse.urlparse(s.path).query).get('video', None)[0]
            video_url = base64.urlsafe_b64decode(video_url)
         except:
            video_url=''

         if(video_url==''):
            s.send_response(200)
            s.send_header("Content-type", "text/html")
            s.end_headers()
         else:
             try:
                 print 'Play: '+video_url
                 s.send_response(200)
                 s.send_header("Connection", "keep-alive")
                 s.send_header("Content-Type", "video/mp4")
                 #s.send_header("Content-Type", "video/x-flv")
                 s.end_headers()
                 #--- send video
                 global PROXY_THREADS
                 global pSocket
                 pSocket = s

                 st = time.time()
                 x = M6(video_url)
                 infos = x.getInfos()
##                 for item in infos.items():
##                    print item[0]+' : '+str(item[1])
                 x.download()

                 while not QueueUrl.empty():
                    QueueUrl.get()
                    QueueUrl.task_done()

                 while not QueueUrlDone.empty():
                    QueueUrlDone.get()
                    QueueUrlDone.task_done()

                 M6Item = None

##                 print 'Download time:', time.time() - st
                 s.server.stop = True
             except:
                 s.server.stop = True
                 while not QueueUrl.empty():
                    QueueUrl.get()
                    QueueUrl.task_done()

                 while not QueueUrlDone.empty():
                    QueueUrlDone.get()
                    QueueUrlDone.task_done()

                 M6Item = None

#-------------------------------------------------------------------------------
class ProxyServer (BaseHTTPServer.HTTPServer):
    """http server that reacts to self.stop flag"""

    def serve_forever (self):
        """Handle one request at a time until stopped."""
        self.stop = False
        while not self.stop:
            try:
                self.handle_request()
            except:
                pass

        try:
            urllib2.urlopen(
                'http://%s:%s/' % (self.server_name, self.server_port))
        except urllib2.URLError:
            # If the server is already shut down, we receive a socket error,
            # which we ignore.
            pass
        self.server_close()

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
	Movie_List(params)

if mode == 'MOVIE':
	Movie_List(params)
if mode == 'SEARCH':
	Search_List(params)
elif mode == 'GENRES':
    Genre_List(params)
elif mode == 'YEAR':
    Year_List(params)
elif mode == 'COUNTRY':
	Country_List(params)
elif mode == 'EMPTY':
    Empty()
elif mode == 'PLAY_MODE':
	Play_Mode(params)
elif mode == 'PLAY':
	PLAY(params)


