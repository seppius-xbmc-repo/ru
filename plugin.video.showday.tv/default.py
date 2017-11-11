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
import demjson3 as json
import subprocess, ConfigParser
import xbmc, xbmcgui, xbmcplugin, xbmcaddon

Addon = xbmcaddon.Addon(id='plugin.video.showday.tv')
xbmcplugin.setContent(int(sys.argv[1]), 'movies')
icon = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'),'icon.png'))
fcookies = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'), r'resources', r'data', r'cookies.txt'))

BASE_URL = 'http://showday.tv'

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

#---------- HTTP interface -----------------------------------------------------
def get_HTML(url, post = None, ref = None, get_url = False):
    request = urllib2.Request(url, post)
    host = urlparse.urlsplit(url).hostname
    if ref==None:
        ref='http://'+host

    print url

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

    if get_url == True:
        html = f.geturl()
    else:
        html = f.read()

    return html

#---------- parameter/info structure -------------------------------------------
class Param:
    url             = ''
    page            = 1
    max_page        = 0
    count           = 0
    genre           = ''
    genre_name      = ''
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
    genre       = ''
    pl_url      = ''
    season      = []

#---------- get parameters -----------------------------------------------------
def Get_Parameters(params):
    #-- url
    try:    p.url = urllib.unquote_plus(params['url'])
    except: p.url = BASE_URL+'/'
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
    #-- search
    try:    p.search = urllib.unquote_plus(params['search'])
    except: p.search = ''
    #-- history
    try:    p.history = urllib.unquote_plus(params['history'])
    except: p.history = ''
    #-- playlist url
    try:    p.playlist = urllib.unquote_plus(params['playlist'])
    except: p.playlist = ''
    #-- page & count
    try:    p.page = int(urllib.unquote_plus(params['page']))
    except: p.page = 1
    try:    p.max_page = int(urllib.unquote_plus(params['max_page']))
    except: p.max_page = 0
    try:    p.count = urllib.unquote_plus(params['count'])
    except: p.count = 0
    #-----
    return p

#----------- get Header string ---------------------------------------------------
def Get_Header(par):

    info  = 'Сериалов: ' + '[COLOR FF00FF00]'+ str(par.count) +'[/COLOR] | '
    info += 'Жанр: ' + '[COLOR FFFF00FF]'+ par.genre_name + '[/COLOR]'
    if par.search <> '':
        info  += ' | Поиск: ' + '[COLOR FF00FFF0]'+ par.search +'[/COLOR]'
    if par.max_page > 1:
        info += ' | Pages: ' + '[COLOR FF00FF00]'+ str(par.page) + '/' + str(par.max_page) +'[/COLOR]'

    if info <> '':
        #-- info line
        name    = info
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=EMPTY'
        #-- filter parameters
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- genre
    if par.genre == '0' and par.search == '' and par.history == '':
        name    = '[COLOR FFFF00FF]'+ '[ЖАНР]' + '[/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=GENRE'
        #-- filter parameters
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- search & history
    if par.search == '' and par.history == '':
        name    = '[COLOR FF00FFF0]' + '[ПОИСК]' + '[/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=MOVIE'
        #-- filter parameters
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&search=%s'%urllib.quote_plus('Y')
        xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- previous page
    if par.page > 1 and par.search == '':
        name    = '[COLOR FF00FF00][PAGE -1][/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=MOVIE'
        u += '&name=%s'%urllib.quote_plus(name)
        #-- filter parameters
        u += '&page=%s'%urllib.quote_plus(str(par.page-1))
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&max_page=%s'%urllib.quote_plus(str(par.max_page))
        u += '&url=%s'%urllib.quote_plus(str(par.url))
        u += '&count=%s'%urllib.quote_plus(str(par.count))
        xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- previous page
    if par.page >= 10 and par.search == '':
        name    = '[COLOR FF00FF00][PAGE -10][/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=MOVIE'
        u += '&name=%s'%urllib.quote_plus(name)
        #-- filter parameters
        u += '&page=%s'%urllib.quote_plus(str(par.page-10))
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&max_page=%s'%urllib.quote_plus(str(par.max_page))
        u += '&url=%s'%urllib.quote_plus(str(par.url))
        u += '&count=%s'%urllib.quote_plus(str(par.count))
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
        skbd.setHeading('Поиск сериалов (минимум 4 символа).')
        skbd.doModal()
        if skbd.isConfirmed():
            SearchStr = skbd.getText().split(':')
            par.search = SearchStr[0]
            url = 'http://showday.tv/index.php?do=search'
            #-- serach parameters ---------
            values = {
                            'beforeafter'       :	'after',
                            'catlist[]'	        :   par.genre,
                            'do'                :	'search',
                            'full_search'       :	1,
                            'replyless'         :	0,
                            'replylimit'        :	0,
                            'resorder'          :	'asc',
                            'result_from'       :	1,
                            'result_num'        :	200,
                            'search_start'      :	1,
                            'searchdate'        :	0,
                            'searchuser'	    :   '',
                            'showposts'         :	0,
                            'sortby'            :	'title',
                            'story'         	:   (par.search).decode('utf-8').encode('cp1251'),
                            'subaction'         :	'search',
                            'titleonly'         :  	3
                        }

            post = urllib.urlencode(values)
        else:
            return False
    else:
        if par.max_page == 0:
            par.count, par.max_page = Get_Count(par.url)
        url = par.url+'page/'+str(par.page)+'/'
        post = None

    #== get movie list =====================================================
    html = get_HTML(url, post)
    soup = BeautifulSoup(html, fromEncoding="utf-8")

    if par.search <> '':
        par.count = len(soup.findAll('div', {'class':'description'}))
        par.max_page = 1

    #-- add header info
    Get_Header(par)

    # -- parsing web page --------------------------------------------------
    for rec in soup.findAll('div', {'class':'description'}):
        #try:
            m = Get_Info(rec)
            i = xbmcgui.ListItem(m.title, iconImage=m.img, thumbnailImage=m.img)
            u = sys.argv[0] + '?mode=SERIAL'
            u += '&name=%s'%urllib.quote_plus(m.title)
            u += '&url=%s'%urllib.quote_plus(m.url)
            u += '&genre=%s'%urllib.quote_plus(par.genre)
            u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
            xbmcplugin.addDirectoryItem(h, u, i, True)
        #except:
        #    pass

    #-- next page link
    if par.page < par.max_page :
        name    = '[COLOR FF00FF00][PAGE +1][/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=MOVIE'
        u += '&name=%s'%urllib.quote_plus(name)
        #-- filter parameters
        u += '&page=%s'%urllib.quote_plus(str(par.page+1))
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&max_page=%s'%urllib.quote_plus(str(par.max_page))
        u += '&url=%s'%urllib.quote_plus(str(par.url))
        u += '&count=%s'%urllib.quote_plus(str(par.count))
        xbmcplugin.addDirectoryItem(h, u, i, True)

    if par.page+10 <= par.max_page :
        name    = '[COLOR FF00FF00][PAGE +10][/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=MOVIE'
        u += '&name=%s'%urllib.quote_plus(name)
        #-- filter parameters
        u += '&page=%s'%urllib.quote_plus(str(par.page+10))
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&max_page=%s'%urllib.quote_plus(str(par.max_page))
        u += '&url=%s'%urllib.quote_plus(str(par.url))
        u += '&count=%s'%urllib.quote_plus(str(par.count))
        xbmcplugin.addDirectoryItem(h, u, i, True)

    xbmcplugin.endOfDirectory(h)


#---------- serial info ---------------------------------------------------------
def Serial_Info(params):
    #-- get filter parameters
    par = Get_Parameters(params)
    #== get serial details =================================================
    post = None
    html = get_HTML(par.url, post)
    soup = BeautifulSoup(html, fromEncoding="utf-8")

    mi = Get_Info(soup)
    #-- get play list url


    try:
	    flashvar = soup.find('object', {'id':'showday'}).find('param', {'name':'flashvars'})['value']
	    for rec in flashvar.split('&'):
		if rec.split('=',1)[0] == 'pl':
		    pl_url = xppod.Decode(rec.split('=',1)[1])
    except:
	#!!!!!!
	    data_link = soup.find('ul', {'class':'player-links'}).find('span')['data-link']
	    pl_url = xppod.Decode(data_link)
	    print data_link
	    print pl_url
	#!!!!!!

    #-- get play list
    season_list = Get_PlayList(pl_url, mode = 's')

    # -- check if serial has seasons and provide season list
    if par.is_season == '' and len(season_list) > 0:
        # -- mane of season
        i = xbmcgui.ListItem('[COLOR FFFFF000]'+mi.title + '[/COLOR]', path='', thumbnailImage=icon)
        u = sys.argv[0] + '?mode=EMPTY'
        xbmcplugin.addDirectoryItem(h, u, i, False)

        #-- generate list of seasons
        for s in season_list:
            i = xbmcgui.ListItem(s['comment'], iconImage=mi.img, thumbnailImage=mi.img)
            u = sys.argv[0] + '?mode=SERIAL'
            #-- filter parameters
            u += '&name=%s'%urllib.quote_plus(s['comment'])
            u += '&url=%s'%urllib.quote_plus(par.url)
            u += '&genre=%s'%urllib.quote_plus(par.genre)
            u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
            u += '&playlist=%s'%urllib.quote_plus(pl_url)
            u += '&is_season=%s'%urllib.quote_plus('*')
            i.setInfo(type='video', infoLabels={    'title':       mi.title,
                                                    'cast' :       mi.actors.split(','),
                            						'year':        int(mi.year[:4]),
                            						'director':    mi.director,
                            						'plot':        mi.text,
                            						'genre':       mi.genre.split(',')})
            i.setProperty('fanart_image', mi.img)
            xbmcplugin.addDirectoryItem(h, u, i, True)
    else:
        # -- mane of season
        name = '[COLOR FFFFF000]'+mi.title+'[/COLOR]'
        if len(season_list) > 0:
            name += ' [COLOR FF00FFF0]( '+par.name + ' )[/COLOR]'

        i = xbmcgui.ListItem(name, path='', thumbnailImage=icon)
        u = sys.argv[0] + '?mode=EMPTY'
        xbmcplugin.addDirectoryItem(h, u, i, False)

        # -- get list of season parts
        s_url = ''
        s_num = 0

        #---------------------------
        if len(season_list) == 0:
            sname = '-'
        else:
            sname  = par.name
            pl_url = par.playlist

        playlist = Get_PlayList(pl_url, season = sname, mode = 'e')

        for rec in playlist:
            name    = rec['comment']
            s_url   = rec['file']
            s_num += 1

            i = xbmcgui.ListItem(name, path = urllib.unquote(s_url), thumbnailImage=mi.img) # iconImage=mi.img
            u = sys.argv[0] + '?mode=PLAY'
            u += '&url=%s'%urllib.quote_plus(s_url)
            u += '&name=%s'%urllib.quote_plus(name)
            u += '&img=%s'%urllib.quote_plus(mi.img)
            u += '&playlist=%s'%urllib.quote_plus(pl_url)
            u += '&is_season=%s'%urllib.quote_plus(sname)
            i.setInfo(type='video', infoLabels={    'title':       mi.title,
                                                    'cast' :       mi.actors.split(','),
                            						#!!!'year':        int(mi.year),
                            						'year':        mi.year,
                            						'director':    mi.director,
                            						'plot':        mi.text,
                            						'genre':       mi.genre.split(',')})
            i.setProperty('fanart_image', mi.img)
            #i.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(h, u, i, False)

    xbmcplugin.endOfDirectory(h)

#---------- movie info ---------------------------------------------------------
def Get_Info(rec):
    i = Info()
    #-- title
    i.title = rec.find('div', {'class':'text'}).find('a').text.encode('utf-8')
    #-- url
    try:
        #!!!!! i.url = rec.find('div', {'class':'text'}).find('h4').find('a')['href']
        i.url = rec.find('div', {'class':'text'}).find('h2').find('a')['href']
    except:
        pass

    for p in rec.find('div', {'class':'text'}).findAll('p'):
        #-- text
        try:
            if p['class'] == '*':
                pass
        except:
            if not p.find('span'):
                i.text = p.text.encode('utf-8')
        #-- original name
        try:
            if p['class'] == 'eng-name':
                i.etitle = p.text.encode('utf-8')
        except:
            pass
        #-- genre/year/actors/director
        try:
            if p.find('span'):
                if p.text.split(':')[0] == u'Жанр':
                    i.genre = p.text.split(':')[1].encode('utf-8')
                if p.text.split(':')[0] == u'Год':
                    i.year = p.text.split(':')[1].encode('utf-8')
                if p.text.split(':')[0] == u'Режиссер':
                    i.director = p.text.split(':')[1].encode('utf-8')
                if p.text.split(':')[0] == u'В ролях':
                    i.actors = p.text.split(':')[1].encode('utf-8')
        except:
            pass
    #-- img
    i.img = BASE_URL + rec.find('div', {'class':'image'}).find('img')['src']

    #-- return movie info
    return i

#---------- get movie count and max page number --------------------------------
def Get_Count(p_url):
    url = p_url
    post = None
    html = get_HTML(url, post)
    soup = BeautifulSoup(html, fromEncoding="utf-8")

    max_page = 0
    for rec in soup.find('div', {'class':'pages'}).findAll('a'):
        try:
            if int(rec.text) > max_page:
                max_page = int(rec.text)
        except:
            pass
    p_count = len(soup.findAll('div', {'class':'description'}))

    url = p_url+'page/'+str(max_page)+'/'
    post = None
    html = get_HTML(url, post)
    soup = BeautifulSoup(html, fromEncoding="utf-8")

    p_count = p_count*(max_page-1)+len(soup.findAll('div', {'class':'description'}))

    return p_count, max_page

#---------- get genre list -----------------------------------------------------
def Genre_List(params):
    #-- get filter parameters
    par = Get_Parameters(params)

    #-- get generes
    url = 'http://showday.tv/index.php?do=search'
    values = {
                    'do'                :	'search',
                    'full_search'       :	1,
                    'result_from'       :	1,
                    'search_start'      :	1,
                    'subaction'         :	'search',
                    'story'             :  	''
             }

    post = urllib.urlencode(values)
    html = get_HTML(url, post)
    soup = BeautifulSoup(html, fromEncoding="utf-8")

    for g in soup.find('ul', {'class':'subcat'}).findAll('a'):
        for rec in soup.find('select', {'class':'rating'}).findAll('option'):
            if g.text == rec.text.replace('&nbsp;', ''):
                i = xbmcgui.ListItem(g.text.encode('utf-8'), iconImage=icon, thumbnailImage=icon)
                u = sys.argv[0] + '?mode=MOVIE'
                #-- filter parameters
                u += '&genre=%s'%urllib.quote_plus(rec['value'])
                u += '&genre_name=%s'%urllib.quote_plus(g.text.encode('utf-8'))
                u += '&url=%s'%urllib.quote_plus(BASE_URL+g['href'])
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
        playlist = Get_PlayList(par.playlist, par.is_season, par.name, 'e')
        for rec in playlist:
            name  = rec['comment']
            s_url = Check_Video_URL(rec['file'])
            #-- add item to play list
            i = xbmcgui.ListItem(name, path = urllib.unquote(s_url), thumbnailImage=par.img)
            i.setProperty('IsPlayable', 'true')
            pl.add(s_url, i)

        xbmc.Player().play(pl)
    # -- play only selected item
    else:
        s_url = Check_Video_URL(par.url)
        i = xbmcgui.ListItem(par.name, path = urllib.unquote(s_url), thumbnailImage=par.img)
        i.setProperty('IsPlayable', 'true')
        xbmcplugin.setResolvedUrl(h, True, i)

def Check_Video_URL(url):

    if '[' in url:
        p1 = url.split('[')[0]
        l  = url.split('[')[1].split(']')[0]
        p3 = url.split('[')[1].split(']')[1]

        i = 0
        for r in l.split(','):
            if len(r.replace(' ','')) > 0:
                if i < int(r):
                    p2 = r.replace(' ','')
                    i = int(r)

        vlink = p1+p2+p3
    else:
        vlink = url

    return vlink

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
def Get_PlayList(pl_url, season = '', start_item = '', mode = 's'): #-- mode: s - seasons, e - episodes
    plist = []
    #-- get playlist items
    post = None
    html = get_HTML(pl_url, post)
    pl = xppod.Decode(html)
    pl = pl.encode('iso-8859-1').decode('utf-8').replace('\r','')
    is_found = False

    for r in json.loads(pl)['playlist']:
        if mode == 's':
            try:
                x = r['playlist']
            except:
                pl = []
                return pl
            plist.append({'comment':r['comment'].lstrip().encode('utf-8'), 'file':pl_url})
        else:
            if r['comment'].lstrip().encode('utf-8') == season or season == '' or season == '-':
                if season == '-':
                    if r['comment'].lstrip().encode('utf-8') == start_item or start_item == '':
                        is_found = True
                    if is_found:
                        plist.append({'comment':r['comment'].lstrip().encode('utf-8'), 'file':r['file']})
                else:
                    for rec in r['playlist']:
                        if rec['comment'].lstrip().encode('utf-8') == start_item or start_item == '':
                            is_found = True
                        if is_found:
                            plist.append({'comment':rec['comment'].lstrip().encode('utf-8'), 'file':rec['file']})


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
elif mode == 'SERIAL':
	Serial_Info(params)
elif mode == 'EMPTY':
    Empty()
elif mode == 'PLAY':
	PLAY(params)



