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
import re, os, urllib, urllib2, cookielib
try:
    from hashlib import md5 as md5
except:
    import md5

import xbmc, xbmcgui, xbmcplugin, xbmcaddon

Addon = xbmcaddon.Addon(id='plugin.video.igru.net.ua')
xbmcplugin.setContent(int(sys.argv[1]), 'movies')

h = int(sys.argv[1])

# load XML library
try:
    sys.path.append(os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib'))
    from BeautifulSoup  import BeautifulSoup
    import moviedb
    import xppod
    icon = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'),'icon.png'))
    fcookies = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'), r'resources', r'data', r'cookies.txt'))
except:
    try:
        sys.path.insert(0, os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib'))
        from BeautifulSoup  import BeautifulSoup
        import moviedb
        import xppod
        icon = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'),'icon.png'))
        fcookies = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'), r'resources', r'data', r'cookies.txt'))
    except:
        sys.path.append(os.path.join(os.getcwd(), r'resources', r'lib'))
        from BeautifulSoup  import BeautifulSoup
        import moviedb
        import xppod
        icon = xbmc.translatePath(os.path.join(os.getcwd(),'icon.png'))
        fcookies = xbmc.translatePath(os.path.join(os.getcwd(), r'resources', r'data', r'cookies.txt'))

import HTMLParser
hpar = HTMLParser.HTMLParser()

def showMessage(heading, message, times = 3000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))


#---------- parameter/info structure -------------------------------------------
class Param:
    type        = ''
    type_hash   = ''
    year        = ''
    tag         = ''
    mode        = 'TYPES'

class Info:
    origin      = ''
    img         = ''
    url         = ''
    name        = ''
    year        = ''
    genre       = ''
    director    = ''
    actors      = ''
    text        = ''

#---------- get parameters -----------------------------------------------------
def Get_Parameters(params):
    #-- mode
    try:    p.mode = urllib.unquote_plus(params['mode'])
    except: p.mode = 'TYPES'
    #-- search tag
    try:    p.tag  = urllib.unquote_plus(params['tag'])
    except: p.tag  = ''
    #-- type
    try:    p.type = urllib.unquote_plus(params['type'])
    except: p.type = ''
    try:    p.type_hash = urllib.unquote_plus(params['type_hash'])
    except: p.type_hash = ''
    #-- year
    try:    p.year = urllib.unquote_plus(params['year'])
    except: p.year = ''
    #-----
    return p

#---------- get movie info -----------------------------------------------------
def Get_Movie_Info(rec):
    #-- name
    mi.name     = rec.text.encode('utf8')
    #-- origin name
    try:    mi.origin      = rec.find('origin').text.encode('utf8')
    except: mi.origin      = ''
    #-- image
    try:    mi.img          = rec.find('img').text.encode('utf8')
    except: mi.img          = ''
    #-- url
    try:    mi.url          = rec.find('url').text.encode('utf8')
    except: mi.url          = ''
    #-- year
    try:    mi.year         = rec.find('year').text.encode('utf8')
    except: mi.year         = ''
    if unicode(mi.year.decode('utf8')).strip().isnumeric(): pass
    else:
        try:
            mi.year = re.compile('([0-9][0-9][0-9][0-9])', re.MULTILINE|re.DOTALL).findall(mi.year)[0]
        except:
            mi.year= '1900'
    #-- genre
    try:    mi.genre        = rec.find('genre').text.encode('utf8')
    except: mi.genre        = ''
    #-- director
    try:    mi.director     = rec.find('director').text.encode('utf8')
    except: mi.director     = ''
    #-- actors
    try:    mi.actors       = rec.find('actors').text.encode('utf8')
    except: mi.actors       = ''
    #-- description
    try:    mi.text         = rec.find('text').text.encode('utf8')
    except: mi.text         = ''
    #-----
    return mi

#----------- get Header string ---------------------------------------------------
def Get_Header(par, mcount):

    info  = 'Фильмов: ' + '[COLOR FF00FF00]' + str(mcount) + '[/COLOR]'

    if par.type <> '':
        info += ' | Тип: ' + '[COLOR FF00FFF0]'+ par.type + '[/COLOR]'

    if par.tag <> '':
        info += ' | Поиск: ' + '[COLOR FF00FFF0]'+ par.tag + '[/COLOR]'

    if par.year <> '':
        info += ' | Год: ' + '[COLOR FFFFF000]'+ par.year + '[/COLOR]'

    #-- info line
    name    = info
    i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
    u = sys.argv[0] + '?mode=EMPTY'
    u += '&name=%s'%urllib.quote_plus(name)
    #-- filter parameters
    u += '&type=%s'%urllib.quote_plus(par.type)
    u += '&type_hash=%s'%urllib.quote_plus(par.type_hash)
    u += '&tag=%s'%urllib.quote_plus(par.tag)
    u += '&year=%s'%urllib.quote_plus(par.year)
    xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- year
    if par.year == '' and par.mode == 'MOVIE':
        name    = '[COLOR FFFFF000]'+ '[Год]' + '[/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=YEAR'
        u += '&name=%s'%urllib.quote_plus(name)
        #-- filter parameters
        u += '&type=%s'%urllib.quote_plus(par.type)
        u += '&type_hash=%s'%urllib.quote_plus(par.type_hash)
        u += '&tag=%s'%urllib.quote_plus(par.tag)
        u += '&year=%s'%urllib.quote_plus(par.year)
        xbmcplugin.addDirectoryItem(h, u, i, True)

def Empty():
    return False

#---------- get movie types --------------------------------------------------
def Get_Movie_Type(params):
    #-- get filter parameters
    par = Get_Parameters(params)
    #-- create MovieDB interface
    myDB = moviedb.MovieDB('READ')

    # add search to the list
    name = '[COLOR FF00FF00]' + '[ПОИСК]' + '[/COLOR]'
    tag = '*'
    i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
    u = sys.argv[0] + '?mode=MOVIE'
    u += '&name=%s'%urllib.quote_plus(name)
    u += '&tag=%s'%urllib.quote_plus(tag)
    xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- year
    if par.year == '':
        name    = '[COLOR FFFFF000]'+ '[Год]' + '[/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=YEAR'
        u += '&name=%s'%urllib.quote_plus(name)
        #-- filter parameters
        u += '&type=%s'%urllib.quote_plus(par.type)
        u += '&type_hash=%s'%urllib.quote_plus(par.type_hash)
        u += '&tag=%s'%urllib.quote_plus(par.tag)
        u += '&year=%s'%urllib.quote_plus(par.year)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    # add movie type to the list
    for rec in myDB.Get_List_Type():
            name = rec.find('name').text.encode('utf-8')
            tag  = rec.tag.encode('utf-8')
            i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
            u = sys.argv[0] + '?mode=MOVIE'
            u += '&name=%s'%urllib.quote_plus(name)
            #-- filter parameters
            u += '&type=%s'%urllib.quote_plus(name)
            u += '&type_hash=%s'%urllib.quote_plus(tag)
            u += '&tag=%s'%urllib.quote_plus(par.tag)
            u += '&year=%s'%urllib.quote_plus(par.year)
            xbmcplugin.addDirectoryItem(h, u, i, True)
    xbmcplugin.endOfDirectory(h)

#---------- get movie year -----------------------------------------------------
def Get_Movie_Year(params):
    #-- get filter parameters
    par = Get_Parameters(params)
    #-- create MovieDB interface
    myDB = moviedb.MovieDB('READ')

    # add movie type to the list
    for rec in myDB.Get_List_Year():
            name = rec.find('name').text.encode('utf-8')
            i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
            u = sys.argv[0] + '?mode=MOVIE'
            u += '&name=%s'%urllib.quote_plus(name)
            #-- filter parameters
            u += '&type=%s'%urllib.quote_plus(par.type)
            u += '&type_hash=%s'%urllib.quote_plus(par.type_hash)
            u += '&tag=%s'%urllib.quote_plus(par.tag)
            u += '&year=%s'%urllib.quote_plus(name)
            xbmcplugin.addDirectoryItem(h, u, i, True)
    xbmcplugin.endOfDirectory(h)
#-------------------------------------------------------------------------------

#---------- get movies for selected type --------------------------------------
def Get_Movie_List(params):
    #-- get filter parameters
    par = Get_Parameters(params)

    if par.type == None: return False

    # show search dialog
    if par.tag == '*':
        skbd = xbmc.Keyboard()
        skbd.setHeading('Поиск фильмов. Формат: name[:yyyy]')
        skbd.doModal()
        if skbd.isConfirmed():
            SearchStr = skbd.getText().split(':')
            par.tag = SearchStr[0]
            if len(SearchStr) > 1:
                par.year = SearchStr[1]
            else:
                par.year = ''
        else:
            return False
        #--
        if not unicode(par.year).isnumeric() and (par.tag == '' or par.year <> ''):
            xbmcgui.Dialog().ok('Ошибка поиска',
            'Неверно задан формат поиска фильма.',
            'Используйте формат: ',
            '    <поиск по имени>[:<поиск по году YYYY>]')
            return False

    #-- create MovieDB interface
    myDB = moviedb.MovieDB('READ')
    movie_list, mcount = myDB.Get_List_Movie(par.tag, par.year, par.type_hash)

    #-- show header
    Get_Header(par, mcount)

    #-- load movies
    for i in movie_list:
        try:
            # set serial to XBMC
            item = xbmcgui.ListItem(i['name'], iconImage=i['img'], thumbnailImage=i['img'])
            u = sys.argv[0] + '?mode=MOVIE_DETAIL'
            u += '&name=%s'%urllib.quote_plus(i['name'])
            u += '&url=%s'%urllib.quote_plus(i['url'])
            u += '&img=%s'%urllib.quote_plus(i['img'])
            item.setInfo(type='video', infoLabels={ 'title':       i['name'],
                                                    'cast' :       i['actors'].split(','),
                            						'year':        int(i['year']),
                            						'director':    i['director'],
                            						'plot':        i['text'],
                            						'genre':       i['genre']})
            item.setProperty('fanart_image', i['img'])
            xbmcplugin.addDirectoryItem(h, u, item, True)
        except:
            xbmc.log('***   ERROR ')


    xbmcplugin.endOfDirectory(h)


#---------- get movie ---------------------------------------------------------
def Get_Movie(params):

    url = urllib.unquote_plus(params['url'])

    #-- replace from old domain to new one
    url = url.replace('igru.net.ua', 'fepcom.net')
    xbmc.log(url)

    if url == None:
        return False

    image = urllib.unquote_plus(params['img'])
    name  = urllib.unquote_plus(params['name'])

    # -- get iframe link to flash player
    post = None
    request = urllib2.Request(url, post)

    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host',	'fepcom.net')
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Language', 'ru-RU')
    request.add_header('Referer',	'http://fepcom.net')

    try:
        f = urllib2.urlopen(request)
    except IOError, e:
        if hasattr(e, 'reason'):
            xbmc.log('We failed to reach a server. Reason: '+ e.reason)
        elif hasattr(e, 'code'):
            xbmc.log('The server couldn\'t fulfill the request. Error code: '+ e.code)

    html = f.read()

    soup = BeautifulSoup(html, fromEncoding="windows-1251")

    all_video = soup.findAll('object', {'type' : 'application/x-shockwave-flash'})
    part = 1

    if len(all_video) == 0:
        showMessage('ПОКАЗАТЬ НЕЧЕГО', 'Нет элементов id,name,link,numberOfMovies')
        return False

    for rec in all_video:
        i_name = name
        if len(all_video) > 1:
            i_name = i_name + ' (часть '+str(part)+')'
            part = part+1
        #--- get UPPOD flash parameters
        flash_param = str(rec.find('param', {'name' : 'flashvars'})['value'])
        video = re.compile('file=(.+?)&', re.MULTILINE|re.DOTALL).findall(flash_param)

        video_url = video[0]

        if video_url.find('http:') == -1:
            video_url = xppod.Decode(video_url)
        #---
        i = xbmcgui.ListItem(i_name, iconImage=image, thumbnailImage=image)
        u = sys.argv[0] + '?mode=PLAY'
        u += '&name=%s'%urllib.quote_plus(i_name)
        u += '&url=%s'%urllib.quote_plus(video_url)
        u += '&img=%s' %urllib.quote_plus(image)
        #i.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(h, u, i, False)

    xbmcplugin.endOfDirectory(h)

#-------------------------------------------------------------------------------

def PLAY(params):
    url     = urllib.unquote_plus(params['url'])
    image   = urllib.unquote_plus(params['img'])
    name    = urllib.unquote_plus(params['name'])

    #--- create HTML page to play video
    i = xbmcgui.ListItem(name, path = urllib.unquote(url), thumbnailImage=image)
    xbmc.Player().play(url, i)

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

mode    = None
p       = Param()
mi      = Info()

try:
	mode = urllib.unquote_plus(params['mode'])
except:
	Get_Movie_Type(params)

if mode == 'MOVIE':
	Get_Movie_List(params)
elif mode == 'MOVIE_DETAIL':
	Get_Movie(params)
elif mode == 'TYPES':
    Get_Movie_Type(params)
elif mode == 'YEAR':
    Get_Movie_Year(params)
elif mode == 'EMPTY':
    Empty()
elif mode == 'PLAY':
	PLAY(params)


