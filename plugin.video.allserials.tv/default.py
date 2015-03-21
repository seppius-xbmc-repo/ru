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

from StringIO import StringIO
import gzip

import demjson3 as json

import subprocess, ConfigParser

import xbmc, xbmcgui, xbmcplugin, xbmcaddon

Addon = xbmcaddon.Addon(id='plugin.video.allserials.tv')
xbmcplugin.setContent(int(sys.argv[1]), 'movies')
icon = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'),'icon.png'))
fcookies = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'), r'resources', r'data', r'cookies.txt'))

# load XML library
lib_path = os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib')

sys.path.append(os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib'))
from BeautifulSoup  import BeautifulSoup
import xppod

import HTMLParser
hpar = HTMLParser.HTMLParser()

h = int(sys.argv[1])

def showMessage(heading, message, times = 3000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))

#---------- HTPP interface -----------------------------------------------------
def get_HTML(url, post = None, ref = None, get_url = False):
    request = urllib2.Request(url, post)

    host = urlparse.urlsplit(url).hostname
    if ref==None:
        ref='http://'+host

    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host',   host)
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Encoding',	'gzip, deflate')
    request.add_header('Accept-Language', 'ru-RU')
    request.add_header('Referer',             ref)

    try:
        f = urllib2.urlopen(request)
    except IOError, e:
        if hasattr(e, 'reason'):
           print 'We failed to reach a server.'
        elif hasattr(e, 'code'):
           print 'The server couldn\'t fulfill the request.'

    if get_url == True:
        html = f.geturl()
    else:
        if f.info().get('Content-Encoding') == 'gzip':
            buf = StringIO( f.read())
            f = gzip.GzipFile(fileobj=buf)
        html = f.read()

    return html

#---------- parameter/info structure -------------------------------------------
class Param:
    url             = ''
    genre           = ''
    genre_name      = ''
    country         = ''
    country_name    = ''
    is_season       = ''
    name            = ''
    img             = ''
    search          = ''
    history         = ''
    playlist        = ''

class Info:
    img         = ''
    url         = '*'
    title       = ''
    text        = ''
    director    = ''
    actors      = ''
    year        = ''
    country     = ''
    genre       = ''
    raiting     = 0
    pl_url      = ''
    season      = []

#---------- get parameters -----------------------------------------------------
def Get_Parameters(params):
    #-- url
    try:    p.url = urllib.unquote_plus(params['url'])
    except: p.url = ''
    #-- img
    try:    p.img = urllib.unquote_plus(params['img'])
    except: p.img = ''
    #-- is season flag
    try:    p.is_season = urllib.unquote_plus(params['is_season'])
    except: p.is_season = ''
    #-- name
    try:    p.name = urllib.unquote_plus(params['name'])
    except: p.name = ''
    #-- genre
    try:    p.genre = urllib.unquote_plus(params['genre'])
    except: p.genre = '0'
    try:    p.genre_name = urllib.unquote_plus(params['genre_name'])
    except: p.genre_name = 'Все'
    #-- country
    try:    p.country = urllib.unquote_plus(params['country'])
    except: p.country = '0'
    try:    p.country_name = urllib.unquote_plus(params['country_name'])
    except: p.country_name = 'Все'
    #-- search
    try:    p.search = urllib.unquote_plus(params['search'])
    except: p.search = ''
    #-- history
    try:    p.history = urllib.unquote_plus(params['history'])
    except: p.history = ''
    #-- playlist url
    try:    p.playlist = urllib.unquote_plus(params['playlist'])
    except: p.playlist = ''
    #-----
    return p

#----------- get Header string ---------------------------------------------------
def Get_Header(par, count):

    if par.search == '':
        info  = 'Сериалов: ' + '[COLOR FF00FF00]'+ str(count) +'[/COLOR] | '
        info += 'Жанр: ' + '[COLOR FFFF00FF]'+ par.genre_name + '[/COLOR] | '
        info += 'Страна: ' + '[COLOR FFFFF000]'+ par.country_name + '[/COLOR]'
    else:
        info  = 'Поиск: ' + '[COLOR FF00FFF0]'+ par.search +'[/COLOR]'

    if info <> '':
        #-- info line
        name    = info
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=EMPTY'
        #-- filter parameters
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&country=%s'%urllib.quote_plus(par.country)
        u += '&country_name=%s'%urllib.quote_plus(par.country_name)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- genre
    if par.genre == '0' and par.search == '' and par.history == '':
        name    = '[COLOR FFFF00FF]'+ '[ЖАНР]' + '[/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=GENRE'
        #-- filter parameters
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&country=%s'%urllib.quote_plus(par.country)
        u += '&country_name=%s'%urllib.quote_plus(par.country_name)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- genre
    if par.country == '0' and par.search == '' and par.history == '':
        name    = '[COLOR FFFFF000]'+ '[СТРАНА]' + '[/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=COUNTRY'
        #-- filter parameters
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&country=%s'%urllib.quote_plus(par.country)
        u += '&country_name=%s'%urllib.quote_plus(par.country_name)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- search & history
    if par.country == '0' and par.genre == '0' and par.search == '' and par.history == '':
        name    = '[COLOR FF00FFF0]' + '[ПОИСК]' + '[/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=MOVIE'
        #-- filter parameters
        u += '&search=%s'%urllib.quote_plus('Y')
        xbmcplugin.addDirectoryItem(h, u, i, True)

        name    = '[COLOR FF00FF00]'+ '[ИСТОРИЯ]' + '[/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=MOVIE'
        #-- filter parameters
        u += '&history=%s'%urllib.quote_plus('Y')
        xbmcplugin.addDirectoryItem(h, u, i, True)

def Empty():
    return False

#---------- movie list ---------------------------------------------------------
def Movie_List(params):
    #-- get filter parameters
    par = Get_Parameters(params)

    # show search dialog
    if par.search == 'Y':
        skbd = xbmc.Keyboard()
        skbd.setHeading('Поиск сериалов.')
        skbd.doModal()
        if skbd.isConfirmed():
            SearchStr = skbd.getText().split(':')
            print Translit(SearchStr[0])
            url = 'http://allserials.tv/search/node/'+urllib.quote(Translit(SearchStr[0]))
            par.search = Translit(SearchStr[0])
        else:
            return False
    else:
        url = 'http://allserials.tv/ajax/serials/get-filter/'+par.genre+'/'+par.country+'/0/name'

    #== get movie list =====================================================
    html = get_HTML(url)
    soup = BeautifulSoup(html, fromEncoding="utf-8")

    # -- parsing web page --------------------------------------------------
    count = 1
    list  = []

    if par.search != '':                                #-- parsing search page
        for rec in soup.findAll('li', {'class':'search-result'}):
            surl = get_HTML(rec.find('a')['href'], None, None, True)
            list.append({'url'   :  surl,
                         'title' : rec.find('a').text.encode('utf-8'),
                         'img'   : 'http://allserials.tv/sites/default/files/covers/'+re.compile('serial-(.+?)-', re.MULTILINE|re.DOTALL).findall(surl)[0]+'.jpg'})
        count = len(list)
    else:                                               #-- parsing serial list
        # -- get number of serials
        for rec in soup.findAll('div', {'class':'serial-item'}):
            list.append({'url'   : 'http://allserials.tv'+rec.find('a')['href'] ,
                         'title' : rec.find('a').text.encode('utf-8'),
                         'img'   : 'http://allserials.tv/sites/default/files/covers/'+re.compile('serial-(.+?)-', re.MULTILINE|re.DOTALL).findall(rec.find('a')['href'])[0]+'.jpg'})
        count = len(list)

    #-- add header info
    Get_Header(par, count)

    #-- get movie info
    #try:
    for rec in list:
        i = xbmcgui.ListItem(rec['title'], iconImage=rec['img'], thumbnailImage=rec['img'].replace('jpg','jpeg'))
        u = sys.argv[0] + '?mode=SERIAL'
        u += '&name=%s'%urllib.quote_plus(rec['title'])
        u += '&url=%s'%urllib.quote_plus(rec['url'])
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&country=%s'%urllib.quote_plus(par.country)
        u += '&country_name=%s'%urllib.quote_plus(par.country_name)
        xbmcplugin.addDirectoryItem(h, u, i, True)
    #except:
    #    pass

    xbmcplugin.endOfDirectory(h)


#---------- serial info ---------------------------------------------------------
def Serial_Info(params):
    #-- get filter parameters
    par = Get_Parameters(params)
    #== get serial details =================================================
    Get_Movie_Info(par.url)

    # -- check if serial has seasons and provide season list
    if par.is_season == '' and len(mi.season) > 0:
        #-- generate list of seasons
        season_list = mi.season

        for s_url in season_list:
            Get_Movie_Info(s_url)

            i = xbmcgui.ListItem(mi.title, iconImage=mi.img, thumbnailImage=mi.img)
            u = sys.argv[0] + '?mode=SERIAL'
            #-- filter parameters
            u += '&name=%s'%urllib.quote_plus(mi.title)
            u += '&url=%s'%urllib.quote_plus(s_url)
            u += '&genre=%s'%urllib.quote_plus(par.genre)
            u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
            u += '&country=%s'%urllib.quote_plus(par.country)
            u += '&country_name=%s'%urllib.quote_plus(par.country_name)
            u += '&is_season=%s'%urllib.quote_plus('*')
            i.setInfo(type='video', infoLabels={    'title':       mi.title,
                                                    'artist' :     mi.actors,
                            						'year':        int(mi.year),
                            						'director':    mi.director,
                            						'plot':        mi.text,
                            						'genre':       mi.genre})
            i.setProperty('fanart_image', mi.img)
            xbmcplugin.addDirectoryItem(h, u, i, True)
    else:
        # -- mane of season
        i = xbmcgui.ListItem('[COLOR FFFFF000]'+par.name + '[/COLOR]', path='', thumbnailImage=icon)
        u = sys.argv[0] + '?mode=EMPTY'
        xbmcplugin.addDirectoryItem(h, u, i, False)

        # -- get list of season parts
        s_url = ''
        s_num = 0

        #---------------------------
        playlist = Get_PlayList(mi.pl_url)

        for rec in playlist:
            name    = rec['comment'].encode('utf-8')
            s_url   = rec['file']
            s_num += 1

            i = xbmcgui.ListItem(name, path = urllib.unquote(s_url), thumbnailImage=mi.img) # iconImage=mi.img
            u = sys.argv[0] + '?mode=PLAY'
            u += '&url=%s'%urllib.quote_plus(s_url)
            u += '&name=%s'%urllib.quote_plus(name)
            u += '&img=%s'%urllib.quote_plus(mi.img)
            u += '&playlist=%s'%urllib.quote_plus(mi.pl_url)
            i.setInfo(type='video', infoLabels={    'title':       mi.title,
                                                    'artist' :     mi.actors,
                            						'year':        int(mi.year),
                            						'director':    mi.director,
                            						'plot':        mi.text,
                            						'genre':       mi.genre})
            i.setProperty('fanart_image', mi.img)
            #i.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(h, u, i, False)

    xbmcplugin.endOfDirectory(h)

#---------- movie detail info --------------------------------------------------
def Get_Movie_Info(url):
    html = get_HTML(url)
    soup = BeautifulSoup(html, fromEncoding="utf-8")
    main_rec = soup.find('div', {'id':'main'})
    # raiting
    try:
        mi.raiting = float(main_rec.find('div',{'class':" field field-serial-rates"}).find('span',{'class':"kp-rate"}).text)
    except:
        mi.raiting = 0
    #genre
    try:
        mi.genre = ''
        for g in main_rec.find('div', {'class':"field field-name-serial-genres field-type-taxonomy-term-reference field-label-inline"}).findAll('span', {'class':"field-item even"}):
            mi.genre += g.text+','
        mi.genre= mi.genre[:-1].encode('utf-8')
    except:
        mi.genre = ''
    # coutry
    try:
        mi.country = ''
        for c in main_rec.find('div', {'class':"field field-name-serial-country field-type-taxonomy-term-reference field-label-inline"}).findAll('span', {'class':"field-item even"}):
            mi.country += c.text+','
        mi.country= mi.country[:-1].encode('utf-8')
    except:
        mi.country = ''
    #year
    try:
        mi.year = main_rec.find('div', {'class':"field field-name-field-serial-date field-type-text field-label-inline"}).find('span', {'class':"field-item even"}).text.encode('utf-8')
        if mi.year[-4:].isnumeric():
            mi.year = mi.year[-4:]
        else:
            mi.year = mi.year[:4]
    except:
        mi.year = '0'

    # directors
    try:
        mi.director = main_rec.find('div', {'class':"field field-name-field-serial-producer field-type-text field-label-inline"}).find('span', {'class':"field-item even"}).text.encode('utf-8')
    except:
        mi.director = ''
    #actors
    try:
        mi.actors = main_rec.find('div', {'class':"field field-name-field-serial-actors field-type-text-long field-label-inline"}).find('span', {'class':"field-item even"}).text.encode('utf-8')
        mi.actors = mi.actors.split(',')
    except:
        mi.actors = ''
    #text
    try:
        mi.text = main_rec.find('div', {'class':"field field-name-body field-type-text-with-summary field-label-hidden"}).find('div', {'class':"field-item even"}).text.encode('utf-8')
    except:
        mi.text = ''
    # img
    try:
        mi.img = main_rec.find('div', {'class':"field field-name-field-serial-image field-type-image field-label-hidden"}).find('img')['src']
    except:
        mi.img = ''
    #playlist_url
    try:
        for rec in urllib.unquote_plus(main_rec.find('object', {'id':'videoplayer'}).find('param', {'name':'flashvars'})['value'].encode('utf-8')).split('&'):
            if rec.split('=')[0] == 'pl':
                mi.pl_url = rec.split('=',1)[1]


                #-- check if playlist should be decode
                if mi.pl_url[:4] != 'http':
                    mi.pl_url = xppod.Decode(mi.pl_url)
    except:
        mi.pl_url = ''

    # title
    str = main_rec.find('h1',{'class':'title'}).text
    str = str[:-len(main_rec.find('h1',{'class':'title'}).find('span').text)]+' '+str[-len(main_rec.find('h1',{'class':'title'}).find('span').text):]
    mi.title= str.replace(u'сериал ', '').replace(u' онлайн','').encode('utf-8')

    # season
    mi.season[:] = []
    if len(main_rec.findAll('div',{'class':'field field-seasons-list clearfix'})) > 0:
        #-- generate list of seasons
        season_rec = main_rec.find('div',{'class':'field field-seasons-list clearfix'})

        for rec in season_rec.findAll('div',{'class':'serial-season'}):
            mi.season.append('http://allserials.tv'+rec.find('a')['href'])

#---------- get genre list -----------------------------------------------------
def Genre_List(params):
    #-- get filter parameters
    par = Get_Parameters(params)

    #-- get generes
    html = get_HTML('http://allserials.tv/')
    soup = BeautifulSoup(html, fromEncoding="utf-8")
    # -- parsing web page ------------------------------------------------------
    for rec in soup.find('select', {'id':'filter_genre'}).findAll('option'):
        if rec['value'] <> '':
            par.genre       = rec['value']
            par.genre_name  = rec.text.capitalize().encode('utf-8')

            i = xbmcgui.ListItem(par.genre_name, iconImage=icon, thumbnailImage=icon)
            u = sys.argv[0] + '?mode=MOVIE'
            #-- filter parameters
            u += '&genre=%s'%urllib.quote_plus(par.genre)
            u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
            u += '&country=%s'%urllib.quote_plus(par.country)
            u += '&country_name=%s'%urllib.quote_plus(par.country_name)
            xbmcplugin.addDirectoryItem(h, u, i, True)

    xbmcplugin.endOfDirectory(h)

#---------- get country list -----------------------------------------------------
def Country_List(params):
    #-- get filter parameters
    par = Get_Parameters(params)

    #-- get countries
    html = get_HTML('http://allserials.tv/')
    soup = BeautifulSoup(html, fromEncoding="utf-8")
    # -- parsing web page ------------------------------------------------------
    for rec in soup.find('select', {'id':'filter_country'}).findAll('option'):
        if rec['value'] <> '':
            par.country       = rec['value']
            par.country_name  = rec.text.capitalize().encode('utf-8')

            i = xbmcgui.ListItem(par.country_name, iconImage=icon, thumbnailImage=icon)
            u = sys.argv[0] + '?mode=MOVIE'
            #-- filter parameters
            u += '&genre=%s'%urllib.quote_plus(par.genre)
            u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
            u += '&country=%s'%urllib.quote_plus(par.country)
            u += '&country_name=%s'%urllib.quote_plus(par.country_name)
            xbmcplugin.addDirectoryItem(h, u, i, True)

    xbmcplugin.endOfDirectory(h)

#-------------------------------------------------------------------------------

def PLAY(params):
    #-- get filter parameters
    par = Get_Parameters(params)

    # -- if requested continious play
    if Addon.getSetting('continue_play') == 'true':
        # create play list
        pl=xbmc.PlayList(1)
        pl.clear()
        # -- get play list
        playlist = Get_PlayList(par.playlist)
        is_found = False
        for rec in playlist:
            name  = rec['comment'].encode('utf-8')
            s_url = rec['file']
            #-- add item to play list
            if s_url == par.url:
                is_found = True

            if is_found:
                i = xbmcgui.ListItem(name, path = urllib.unquote(s_url), thumbnailImage=par.img)
                i.setProperty('IsPlayable', 'true')
                pl.add(s_url, i)

        xbmc.Player().play(pl)
    # -- play only selected item
    else:
        i = xbmcgui.ListItem(par.name, path = urllib.unquote(par.url), thumbnailImage=par.img)
        i.setProperty('IsPlayable', 'true')
        xbmcplugin.setResolvedUrl(h, True, i)


def Translit(srch):
    rez = srch

    if Addon.getSetting('translit') == 'true':
        url = 'http://translit.ru/classic/'
        #-- serach parameters ---------
        values = {
                        'direction'     :   'ru',
                        'transliterate' :   'транслит',
                        'subject'       :   srch,
                        'account'       :   ''
                    }

        post = urllib.urlencode(values)
        html = get_HTML(url, post)
        soup = BeautifulSoup(html, fromEncoding="UTF-8")

        for rec in soup.findAll('textarea', {'class' : "txtarea"}):
            rez = rec.text.encode('utf8')

    return rez
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


#---------- get play list ------------------------------------------------------
def Get_PlayList(url):
    plist = []

    #-- check if playlist should be decode
    if url[:4] != 'http':
        url = xppod.Decode(url)

    if url[:4] != 'http':
        return []

    html = get_HTML(url)

    try:
        pl = json.loads(html)
    except:
        pl = json.loads(xppod.Decode(html))

    for rec in pl['playlist']:
        plist.append({'comment':rec['comment'].encode('iso-8859-1').decode('utf-8'), 'file':rec['file']})

    return plist

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


def Test(params):
    #-- get filter parameters
    par = Get_Parameters(params)
    #-- add header info
    Get_Header(par, 1)

    xbmcplugin.endOfDirectory(h)

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

#---------------------------------
try:
	mode = urllib.unquote_plus(params['mode'])
except:
	mode = 'MOVIE'

if mode == 'MOVIE':
	Movie_List(params)
elif mode == 'GENRE':
    Genre_List(params)
elif mode == 'COUNTRY':
    Country_List(params)
elif mode == 'SERIAL':
	Serial_Info(params)
elif mode == 'EMPTY':
    Empty()
elif mode == 'PLAY':
	PLAY(params)



