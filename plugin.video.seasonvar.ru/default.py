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

import json #as json
import subprocess, ConfigParser
import xbmc, xbmcgui, xbmcplugin, xbmcaddon, xbmcvfs

Addon = xbmcaddon.Addon(id='plugin.video.seasonvar.ru')
xbmcplugin.setContent(int(sys.argv[1]), 'movies')
icon = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'),'icon.png'))
fcookies = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'), r'pl_cookies.txt'))

# load XML library
lib_path = os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib')

sys.path.append(os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib'))
from BeautifulSoup  import BeautifulSoup

import xppod
Decoder = xppod.XPpod(Addon)

import HTMLParser
hpar = HTMLParser.HTMLParser()

h = int(sys.argv[1])

def showMessage(heading, message, times = 3000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))

#---------- HTPP interface -----------------------------------------------------
def get_HTML(url, post = None, ref = None, is_pl = False):
    request = urllib2.Request(url, post)

    host = urlparse.urlsplit(url).hostname
    if ref==None:
        ref='http://'+host

    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host',   host)
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Language', 'ru-RU')
    request.add_header('Referer',             ref)
    if is_pl:
        for c in cj:
            if c.name == 'sva' and c.domain == 'www.seasonvar.ru':
                request.add_header('Cookie', 'sva='+c.value)

    try:
        f = urllib2.urlopen(request, timeout=360)
    except IOError, e:
        if hasattr(e, 'reason'):
           print 'We failed to reach a server.'+str(e.reason)
        elif hasattr(e, 'code'):
           print 'The server couldn\'t fulfill the request.'+str(e.code)

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
    title           = ''
    full_name       = ''
    alphabet        = ''

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
    #-- title
    try:    p.title = urllib.unquote_plus(params['title'])
    except: p.title = ''
    #-- full_name
    try:    p.full_name = urllib.unquote_plus(params['full_name'])
    except: p.full_name = ''
    #-- genre
    try:    p.genre = urllib.unquote_plus(params['genre'])
    except: p.genre = 'all'
    try:    p.genre_name = urllib.unquote_plus(params['genre_name'])
    except: p.genre_name = 'Все'
    #-- country
    try:    p.country = urllib.unquote_plus(params['country'])
    except: p.country = 'all'
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
    #-- alphabet
    try:    p.alphabet = urllib.unquote_plus(params['alphabet'])
    except: p.alphabet = ''
    #-----

    return p

#----------- get Header string ---------------------------------------------------
def Get_Header(par, count):

    if par.search == '':
        info  = 'Сериалов: ' + '[COLOR FF00FF00]'+ str(count) +'[/COLOR] | '

        if par.alphabet != '':
            info += 'Буква: ' + '[COLOR FF00FFF0][B]'+ par.alphabet + '[/B][/COLOR] | '

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
    if par.genre == 'all' and par.search == '' and par.history == '':
        name    = '[COLOR FFFF00FF]'+ '[ЖАНР]' + '[/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=GENRE'
        #-- filter parameters
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&country=%s'%urllib.quote_plus(par.country)
        u += '&country_name=%s'%urllib.quote_plus(par.country_name)
        u += '&alphabet=%s'%urllib.quote_plus(par.alphabet)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- genre
    if par.country == 'all' and par.search == '' and par.history == '':
        name    = '[COLOR FFFFF000]'+ '[СТРАНА]' + '[/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=COUNTRY'
        #-- filter parameters
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&country=%s'%urllib.quote_plus(par.country)
        u += '&country_name=%s'%urllib.quote_plus(par.country_name)
        u += '&alphabet=%s'%urllib.quote_plus(par.alphabet)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- search & history
    if par.country == 'all' and par.genre == 'all' and par.search == '' and par.history == '':
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

def GetTag(soup):
    list = {}

    for rec in soup.findAll('div'):
        if len(rec.findAll('a')) > 0:
            try:
                try:
                    list[rec["class"]] = list[rec["class"]]+1
                except:
                    list[rec["class"]] = 1
            except:
                pass

    key = ''
    count = 0

    for l in list:
        if count < list[l]:
            count = list[l]
            key = l

    return key

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
            url = 'http://seasonvar.ru/autocomplete.php?query='+urllib.quote(SearchStr[0])
            par.search = SearchStr[0]
        else:
            return False
    else:
        url = 'http://seasonvar.ru/index.php?onlyjanrnew='+par.genre+'&&sortto=name&country='+par.country+'&nocache='+str(random.random())

    #== get movie list =====================================================
    html = get_HTML(url)

    # -- parsing web page --------------------------------------------------
    count = 1
    list  = []

    if par.search != '':                                #-- parsing search page
        s = json.loads(html)
        count = len(s['suggestions'])
        if count < 1: return False

        for i in range(0, count):
            name = s['suggestions'][i].encode('utf-8')
            list.append({'title':name, 'url':'http://seasonvar.ru/'+s['data'][i], 'img': icon})
    else:                                               #-- parsing serial list
        soup = BeautifulSoup(html, fromEncoding="utf-8")
        # -- get number of serials
        mtag = GetTag(soup)
        #with open('d:\\seasonvar.html', 'a') as the_file:
        #    the_file.write(html)

        if par.alphabet == '':
            count = 0
            for rec in soup.findAll('div', {'class':'alf-letter'}):
                a_name = u'[COLOR FF00FFF0][B]' +rec.text+u'[/B][/COLOR] сериалов: '+str(len(rec.parent.findAll('div', {'class':mtag})))
                list.append({'title'    : a_name.encode('utf-8'),
                             'alphabet' : rec.text.encode('utf-8')})
                count = count+len(rec.parent.findAll('div', {'class':mtag}))
        else:
            for reca in soup.findAll('div', {'class':'alf-letter'}):
                if reca.text.encode('utf-8') == par.alphabet:
                    for rec in reca.parent.findAll('div', {'class':mtag}):
                        list.append({'url'   : 'http://seasonvar.ru'+rec.find('a')['href'].encode('utf-8'),
                                     'title' : rec.find('a').text.encode('utf-8'),
                                     'img'   : 'http://cdn.seasonvar.ru/oblojka/'+rec['id'].replace('div','')+'.jpg'})
                        count = len(list)

    #-- add header info
    Get_Header(par, count)

    #-- get movie info
    #try:
    if par.alphabet != '' or par.search != '':
        for rec in list:
            i = xbmcgui.ListItem(rec['title'], iconImage=rec['img'], thumbnailImage=rec['img'])
            u = sys.argv[0] + '?mode=SERIAL'
            u += '&name=%s'%urllib.quote_plus(rec['title'])
            u += '&title=%s'%urllib.quote_plus(rec['title'])
            u += '&url=%s'%urllib.quote_plus(rec['url'])
            u += '&genre=%s'%urllib.quote_plus(par.genre)
            u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
            u += '&country=%s'%urllib.quote_plus(par.country)
            u += '&country_name=%s'%urllib.quote_plus(par.country_name)
            xbmcplugin.addDirectoryItem(h, u, i, True)
    else:
        for rec in list:
            i = xbmcgui.ListItem(rec['title'], iconImage=icon, thumbnailImage=icon)
            u = sys.argv[0] + '?mode=MOVIE'
            #u += '&name=%s'%urllib.quote_plus(rec['title'])
            #u += '&title=%s'%urllib.quote_plus(rec['title'])
            u += '&alphabet=%s'%urllib.quote_plus(rec['alphabet'])
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
    #-- checkif SWD decompiler set up properly
    if not Check_SWF():
        return False

    #-- get filter parameters
    par = Get_Parameters(params)
    #== get serial details =================================================
    tvshowtitle=par.title
    full_name=par.name
    url = par.url
    html = get_HTML(url)
    # -- parsing web page --------------------------------------------------
    soup = BeautifulSoup(html, fromEncoding="windows-1251")

    # -- check if serial has seasons and provide season list
    if par.is_season == '' and len(soup.findAll('div', {'class':'full-news-2-content'})) > 0:
        #-- generate list of seasons
        for rec in soup.find('div', {'class':'full-news-2-content'}).findAll('a'):
            s_url   = ('http://seasonvar.ru'+rec['href']).encode('utf-8')
            s_name  = rec.text.replace('>>>', '').replace(u'Сериал ', '')
            if s_name.find(u'сезон(') > -1:
                s_name = s_name.split(u'сезон(')[0]+u'сезон'
            s_name = s_name.encode('utf-8')
            s_id    = rec['href'].split('-')[1]
            s_image = 'http://cdn.seasonvar.ru/oblojka/'+s_id+'.jpg'

            i = xbmcgui.ListItem(s_name, iconImage=s_image, thumbnailImage=s_image)
            u = sys.argv[0] + '?mode=SERIAL'
            #-- filter parameters
            u += '&name=%s'%urllib.quote_plus(s_name)
            u += '&title=%s'%urllib.quote_plus(tvshowtitle)
            u += '&url=%s'%urllib.quote_plus(s_url)
            u += '&genre=%s'%urllib.quote_plus(par.genre)
            u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
            u += '&country=%s'%urllib.quote_plus(par.country)
            u += '&country_name=%s'%urllib.quote_plus(par.country_name)
            u += '&is_season=%s'%urllib.quote_plus('*')
            xbmcplugin.addDirectoryItem(h, u, i, True)
    else:
        #-- generate list of movie parts
        # -- get movie info
        for rec in soup.find('td', {'class':'td-for-content'}).findAll('p'):
            if len(rec.findAll('span', {'class':'videl'})) > 0:
                for j in str(rec).split('<br />'):
                    r = re.compile('<span class="videl">(.+?)<\/span>(.+?)<\/br>', re.MULTILINE|re.DOTALL).findall(str(j)+'</br>')
                    for s in r:
                        if s[0] == 'Жанр:':     mi.genre        = s[1].replace('</p>', '')
                        if s[0] == 'Страна:':   mi.country      = s[1].replace('</p>', '')
                        if s[0] == 'Вышел:':    mi.year         = s[1].replace('</p>', '')
                        if s[0] == 'Режисёр:':  mi.director     = s[1].replace('</p>', '')
                        if s[0] == 'Роли:':     mi.actors       = s[1].replace('</p>', '')
            else:
                mi.text = rec.text.encode('utf-8')

        mi.actors = mi.actors.split(',')

        mi.img = soup.find('td', {'class':'td-for-content'}).find('img')['src']

        # -- get serial parts info
        # -- mane of season
        i = xbmcgui.ListItem('[COLOR FFFFF000]'+par.name + '[/COLOR]', path='', thumbnailImage=icon)
        u = sys.argv[0] + '?mode=EMPTY'
        xbmcplugin.addDirectoryItem(h, u, i, False)
        pname=par.name
        # -- get list of season parts
        s_url = ''
        s_num = 0

        #---------------------------
        try:
            playlist, playlist_url, swf_player = Get_PlayList(soup, url)
        except:
            Initialize()
            playlist, playlist_url, swf_player = Get_PlayList(soup, url)
            if playlist == '':
                return False

        for rec in playlist:
            name    = rec['name']
            s_url   = rec['video']

            i = xbmcgui.ListItem(name, path = urllib.unquote(s_url), thumbnailImage=mi.img) # iconImage=mi.img
            u = sys.argv[0] + '?mode=PLAY'
            u += '&url=%s'%urllib.quote_plus(s_url)
            u += '&name=%s'%urllib.quote_plus(pname)
            u += '&full_name=%s'%urllib.quote_plus(full_name)
            u += '&title=%s'%urllib.quote_plus(tvshowtitle)
            u += '&img=%s'%urllib.quote_plus(mi.img)
            u += '&playlist=%s'%urllib.quote_plus(playlist_url)
            try:cast=re.compile(">(.+?)</a>").findall(mi.actors)
            except: cast=[]
            i.setInfo(type='video', infoLabels={    'title':       name,
                                                    'cast' :       cast,
                                                    'artist' :     mi.actors,
                            						'year':        int(mi.year),
                            						'director':    mi.director,
                            						'plot':        mi.text,
                            						'genre':       mi.genre})
            i.setProperty('fanart_image', mi.img)
            #i.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(h, u, i, False)

    xbmcplugin.endOfDirectory(h)

#-------------------------------------------------------------------------------
def int_xx(intxx):
    if intxx and intxx!='None':
        return '%02d' % (int(intxx))
    else:
        return '00'

def original_title(name, lenseason):
    if '/' in name:
        title=name.split('/')[1]
        if 'сезон' in title:
            title=title[:len(title)-len('  сезон')-lenseason]
        return title

def mynewtitle(title, sel, name):
    myshows={
                'episode': 1,
                'season': 1,
                'tvshowtitle': '',
                'title': sel}

    #print ('[mynewtitle]:'+str((title, sel, name)))

    #for repl in ['Сериал ', 'Смотреть ', 'Фильм ']:
    #    if title.startswith(repl): myshows['title']=title.replace(repl,'', 1)

    if sel:
        season,episode,orig=0,0,None
        match=re.compile('(\d+) (Cезон|cезон|Сезон|сезон|Season|season)').findall(sel)
        if match:
            season=int_xx(match[0][0])
        else:
            match=re.compile('(\d+) (Cезон|cезон|Сезон|сезон|Season|season)').findall(name)
            if match:
                season=int_xx(match[0][0])

        match=re.compile('(\d+) (Cерия|cерия|Серия|серия|Episod|episod)').findall(sel)
        if match:
            episode=int_xx(match[0][0])

        orig=original_title(name,len(str(int(season))))
        if not orig: orig=title

        #print ('[mynewtitle]:'+str((episode, season, title)))
        if episode:
            if not season: season=1
            myshows={
                    'episode': int(episode),
                    'season': int(season),
                    'tvshowtitle': orig,
                    'title':title+' S%sE%s.mp4'%(season,episode)}

    return myshows

#---------- get genre list -----------------------------------------------------
def Genre_List(params):
    #-- get filter parameters
    par = Get_Parameters(params)

    #-- get generes
    url = 'http://seasonvar.ru'
    html = get_HTML(url)

    # -- parsing web page ------------------------------------------------------
    soup = BeautifulSoup(html, fromEncoding="windows-1251")

    for rec in soup.find('select', {'id':'chkonlyjanr'}).findAll('option'):
        par.genre       = rec['value']
        par.genre_name  = rec.text.capitalize().encode('utf-8')

        i = xbmcgui.ListItem(par.genre_name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=MOVIE'
        #-- filter parameters
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&country=%s'%urllib.quote_plus(par.country)
        u += '&country_name=%s'%urllib.quote_plus(par.country_name)
        u += '&alphabet=%s'%urllib.quote_plus(par.alphabet)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    xbmcplugin.endOfDirectory(h)

#---------- get country list -----------------------------------------------------
def Country_List(params):
    #-- get filter parameters
    par = Get_Parameters(params)

    #-- get generes
    url = 'http://seasonvar.ru'
    html = get_HTML(url)

    # -- parsing web page ------------------------------------------------------
    soup = BeautifulSoup(html, fromEncoding="windows-1251")

    for rec in soup.find('select', {'id':'chkonlycountry'}).findAll('option'):
        par.country       = rec['value']
        par.country_name  = rec.text.capitalize().encode('utf-8')

        i = xbmcgui.ListItem(par.country_name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=MOVIE'
        #-- filter parameters
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&genre_name=%s'%urllib.quote_plus(par.genre_name)
        u += '&country=%s'%urllib.quote_plus(par.country)
        u += '&country_name=%s'%urllib.quote_plus(par.country_name)
        u += '&alphabet=%s'%urllib.quote_plus(par.alphabet)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    xbmcplugin.endOfDirectory(h)

#-------------------------------------------------------------------------------

def PLAY(params):
    #-- get filter parameters
    par = Get_Parameters(params)
    tvshowtitle=par.title
    full_name=par.full_name

    # -- if requested continious play
    if Addon.getSetting('continue_play') == 'true':
        # create play list
        pl=xbmc.PlayList(1)
        pl.clear()
        # -- get play list
        html = get_HTML(par.playlist, is_pl = True)

        #html = Decoder.Decode(html)

        if html == '':
            return False

        s_num = 0
        s_url = ''
        is_found = False

        video_name  = re.compile('"comment"\:"(.+?)"', re.MULTILINE|re.DOTALL).findall(html)
        video_url   = re.compile('"file"\:"(.+?)"', re.MULTILINE|re.DOTALL).findall(html)

        for i in range(len(video_name)):
            name    = video_name[i]
            s_url   = video_url[i]
            #-- add item to play list
            if s_url == par.url:
                is_found = True

            if is_found:
                myshows=mynewtitle(tvshowtitle,name,full_name)
                newtitle=myshows['title']
                i = xbmcgui.ListItem(newtitle, path = urllib.unquote(s_url), thumbnailImage=par.img)
                if 'tvshowtitle' in myshows and myshows['tvshowtitle']!='':
                    i.setInfo(type='video', infoLabels={    'title':      newtitle,
                                                    'episode': myshows['episode'],
                                                    'season': myshows['season'],
                                                    'tvshowtitle': myshows['tvshowtitle']})
                i.setProperty('IsPlayable', 'true')
                pl.add(s_url, i)
            s_num += 1

        xbmc.Player().play(pl)
    # -- play only selected item
    else:
        myshows=mynewtitle(tvshowtitle,par.name,full_name)
        newtitle=myshows['title']
        i = xbmcgui.ListItem(newtitle, path = urllib.unquote(par.url), thumbnailImage=par.img)
        if 'tvshowtitle' in myshows and myshows['tvshowtitle']!='':
                    i.setInfo(type='video', infoLabels={    'title':      newtitle,
                                                    'episode': myshows['episode'],
                                                    'season': myshows['season'],
                                                    'tvshowtitle': myshows['tvshowtitle']})
        i.setProperty('IsPlayable', 'true')
        xbmcplugin.setResolvedUrl(h, True, i)

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

#-------------------------------------------------------------------------------  !!!
#---------- cleanup javac code -------------------------------------------------
def Java_CleanUP(html):
    html = re.sub(re.compile("/\*.*?\*/",re.DOTALL ) ,"" ,html)
    txt = ''
    for rec in html.split('\n'):
        s = rec.split('//')[0]
        txt += s+'\n'

    return txt

#---------- set cookies --------------------------------------------------------
def Get_Cookies(url): #soup):

    config = ConfigParser.ConfigParser()
    config.read(os.path.join(Addon.getAddonInfo('path'),'cookie.txt'))

    sec = 'www.seasonvar.ru'
    cookie = ''
    for op in config.options(sec):
        if config.get(sec, op) != 'null':
            cookie += op+'=';
            cookie += config.get(sec, op)+';'

    return cookie

#---------- get play list ------------------------------------------------------
def Get_PlayList(soup, parent_url):
    #-- get play list url
    plcode = ''
    plcode = Run_Java(parent_url)
    #---
    soup = BeautifulSoup(plcode, fromEncoding="windows-1251")

    swf_player  = soup.find('object')['data']

    str = soup.find('param', {'name':"flashvars"})['value']
    plcode      = re.compile('pl=(.+?)&uid', re.MULTILINE|re.DOTALL).findall(str)[0]

    get_HTML(swf_player)


    url = Decoder.Decode(plcode, swf_player, parent_url, cj=cj)

    if url == '':
        xbmc.log('* Failed to decode url')
        return [],url, swf_player

    if url.find('seasonvar.ru') == -1:
        url = 'http://seasonvar.ru' + url
    if url.find('http') == -1:
        url = 'http:' + url

    # -- get play list
    html = get_HTML(url, None, swf_player, True)

    #html = Decoder.Decode(html)

    pl = []
    name    = re.compile('"comment"\:"(.+?)"', re.MULTILINE|re.DOTALL).findall(html)
    video   = re.compile('"file"\:"(.+?)"', re.MULTILINE|re.DOTALL).findall(html)

    for i in range(len(video)):
        pl.append({'name':name[i], 'video':video[i]})

    return pl, url, swf_player

#-------------------------------------------------------------------------------
def Initialize():
    #-- remote PhantomJS service
    if Addon.getSetting('External_PhantomJS') == 'true':
        url = 'http://'+Addon.getSetting('PhantomJS_IP')+':'+Addon.getSetting('PhantomJS_Port')
        try:
            str = get_HTML(url)
        except:
            str = get_HTML(url)
        f = open(os.path.join(Addon.getAddonInfo('path'),'ext_cookie.txt'), 'w')
        f.write(str)
        f.close()

        #-- load cookies
        cj.load(os.path.join(Addon.getAddonInfo('path'),'ext_cookie.txt'), True, True)
        return

    #-- local PhantomJS service
    startupinfo = None
    if os.name == 'nt':
        prog = '"'+os.path.join(Addon.getAddonInfo('path'),'phantomjs.exe" --cookies-file="')+os.path.join(Addon.getAddonInfo('path'),'cookie.txt')+'" "'+os.path.join(Addon.getAddonInfo('path'),'seasonvar.js"')
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= 1
    else:
        prog = [os.path.join(Addon.getSetting('PhantomJS_Path'),'phantomjs'), '--cookies-file='+os.path.join(Addon.getAddonInfo('path'),'cookie.txt'), os.path.join(Addon.getAddonInfo('path'),'seasonvar.js')]

    try:
        process = subprocess.Popen(prog, stdin= subprocess.PIPE, stdout= subprocess.PIPE, stderr= subprocess.PIPE,shell= False, startupinfo=startupinfo)
        process.wait()
    except:
        xbmc.log('*** PhantomJS is not found or failed.')

    #-- load cookies
    f = open(os.path.join(Addon.getAddonInfo('path'),'cookie.txt'), 'r')
    fcookie = f.read()
    f.close()

    group = ''
    for r in fcookie.split('\n'):
        r = r.strip()
        if group == '' and r != '':
            group = r
        elif r != '':
            ck = cookielib.Cookie(version=0, name=r.split('=',1)[0], value=r.split('=',1)[1], port=None, port_specified=False, domain=group.replace('[','').replace(']',''), domain_specified=False, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=None, discard=True, comment=None, comment_url=None, rest={'HttpOnly': None}, rfc2109=False)
            cj.set_cookie(ck)
        else:
            group = ''

def Run_Java(seasonvar_url):
    #-- remote PhantomJS service
    if Addon.getSetting('External_PhantomJS') == 'true':
        url = 'http://'+Addon.getSetting('PhantomJS_IP')+':'+Addon.getSetting('PhantomJS_Port')
        values = {'url' :	seasonvar_url}
        post = urllib.urlencode(values)
        try:
            fcode = get_HTML(url, post)
        except:
            fcode = get_HTML(url, post)

        return fcode

    #-- local PhantomJS service
    f1 = open(os.path.join(Addon.getAddonInfo('path'),'test.tpl'), 'r')
    f2 = open(os.path.join(Addon.getAddonInfo('path'),'test.js') , 'w')
    fcode = f1.read().replace('$url$', seasonvar_url)

    f2.write(fcode.encode('utf-8'))
    f1.close()
    f2.close()
    #--
    startupinfo = None
    if os.name == 'nt':
        prog = '"'+os.path.join(Addon.getAddonInfo('path'),'phantomjs.exe" "')+os.path.join(Addon.getAddonInfo('path'),'test.js"')
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= 1
    else:
        prog = [os.path.join(Addon.getSetting('PhantomJS_Path'),'phantomjs'), os.path.join(Addon.getAddonInfo('path'),'test.js')]

    output_f = open(os.path.join(Addon.getAddonInfo('path'),'test.txt'),'w')
    process = subprocess.Popen(prog, stdin= subprocess.PIPE, stdout= output_f, stderr= subprocess.PIPE,shell= False, startupinfo=startupinfo)
    process.wait()
    output_f.close()

    f1 = open(os.path.join(Addon.getAddonInfo('path'),'test.txt'), 'r')
    fcode = f1.read()
    f1.close()

    return fcode

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

def Check_SWF():
    #-- remote PhantomJS service
    if Addon.getSetting('External_PhantomJS') == 'true':
        return True

    if Addon.getSetting('SWF_Path') == '':
        swf_path = os.path.join(Addon.getAddonInfo('path'), r'resources', r'swf')
    else:
        swf_path = Addon.getSetting('SWF_Path')

    if os.name == 'nt':
            swf_path = os.path.join(swf_path, 'rabcdasm.exe')
    else:
            swf_path = os.path.join(swf_path,'rabcdasm')

    if not xbmcvfs.exists(swf_path):
        xbmcgui.Dialog().ok('SEASONVAR.RU', 'SWF decompiler not found at '+swf_path+'.')
        return False
    else:
        return True

#-------------------------------------------------------------------------------
params=get_params(sys.argv[2])

# get cookies from last session
cj = cookielib.MozillaCookieJar(fcookies)
try:
    cj.load(fcookies, True, True)
except:
    pass

hr  = urllib2.HTTPCookieProcessor(cj)
opener = urllib2.build_opener(hr)
urllib2.install_opener(opener)

p  = Param()
mi = Info()

mode = None

#---------------------------------
#Test(params)

try:
	mode = urllib.unquote_plus(params['mode'])
except:
	mode = '$'

if mode == '$':
    Initialize()
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

cj.save(fcookies, True, True)