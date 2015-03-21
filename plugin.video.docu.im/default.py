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
import re, os, urllib, urllib2, cookielib, time, datetime
from time import gmtime, strftime
import urlparse
import demjson3

import xbmc, xbmcgui, xbmcplugin, xbmcaddon

Addon = xbmcaddon.Addon(id='plugin.video.docu.im')
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

#---------- parameter/info structure -------------------------------------------
class Param:
    url     = ''
    type    = ''
    page    = '1'
    genre   = ''
    genre_name = ''
    country = ''
    country_name = ''
    year    = ''
    search  = ''
    max_page    = 0
    count       = 0
    img     = ''

class Info:
    name        = ''
    alter       = ''
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
    #-- name
    try:    p.name = urllib.unquote_plus(params['name'])
    except: p.name = ''
    #-- url
    try:    p.url = urllib.unquote_plus(params['url'])
    except: p.url = ''
    #-- img
    try:    p.img = urllib.unquote_plus(params['img'])
    except: p.img = ''
    #-- type
    try:    p.type = urllib.unquote_plus(params['type'])
    except: p.type = ''
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
    #--search
    try:    p.search = urllib.unquote_plus(params['search'])
    except: p.search = ''
    #-- max_pages
    try:    p.max_page = int(urllib.unquote_plus(params['max_page']))
    except: p.max_page =0
    #--movie count
    try:    p.count = int(urllib.unquote_plus(params['count']))
    except: p.count = 0
    #-----
    return p

#---------- get filters --------------------------------------------------------
def get_Filter( fname = None, url = None, type = None, page = None, genre = None,
                genre_name =None, country = None, country_name = None, year = None,
                search = None, max_page = None, count = None, img = None):

    #-- set default values
    if fname == None:       fname = par.name
    if url == None:         url = par.url
    if type == None:        type = par.type
    if page == None:        page = par.page
    if genre == None:       genre = par.genre
    if genre_name == None:  genre_name = par.genre_name
    if country == None:     country = par.country
    if country_name == None: country_name = par.country_name
    if year == None:        year = par.year
    if search == None:      search = par.search
    if max_page == None:    max_page = par.max_page
    if count == None:       count = par.count
    if img == None:         img = par.img

    #-- collect filter
    u =  '&name=%s'%urllib.quote_plus(fname)
    u += '&url=%s'%urllib.quote_plus(url)
    u += '&type=%s'%urllib.quote_plus(type)
    u += '&page=%s'%urllib.quote_plus(page)
    u += '&genre=%s'%urllib.quote_plus(genre)
    u += '&genre_name=%s'%urllib.quote_plus(genre_name)
    u += '&country=%s'%urllib.quote_plus(country)
    u += '&country_name=%s'%urllib.quote_plus(country_name)
    u += '&year=%s'%urllib.quote_plus(year)
    u += '&search=%s'%urllib.quote_plus(search)
    u += '&max_page=%s'%urllib.quote_plus(str(max_page))
    u += '&count=%s'%urllib.quote_plus(str(count))
    u += '&img=%s'%urllib.quote_plus(img)

    return u

#---------- get web page -------------------------------------------------------
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
    request.add_header('X-Requested-With','XMLHttpRequest')
    request.add_header('Content-Type','application/x-www-form-urlencoded')

    try:
        f = urllib2.urlopen(request)
    except IOError, e:
        if hasattr(e, 'reason'):
           xbmc.log('We failed to reach a server.')
        elif hasattr(e, 'code'):
           xbmc.log('The server couldn\'t fulfill the request.')

    html = f.read()

    return html

#-------------------------------------------------------------------------------
def Decode(param):
    #-- define variables
    loc_3 = [0,0,0,0]
    loc_4 = [0,0,0]
    loc_2 = ''
    #-- define hash parameters for decoding
    dec = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='
    hash1 = ["Z", "v", "6", "W", "m", "y", "g", "X", "b", "o", "V", "d", "k", "t", "M", "Q", "u", "5", "D", "e", "J", "s", "z", "f", "L", "="];
    hash2 = ["a", "G", "9", "w", "1", "N", "l", "T", "I", "R", "7", "2", "n", "B", "4", "H", "3", "U", "0", "p", "Y", "c", "i", "x", "8", "q"];

    #-- decode
    for i in range(0, len(hash1)):
        re1 = hash1[i]
        re2 = hash2[i]

        param = param.replace(re1, '___')
        param = param.replace(re2, re1)
        param = param.replace('___', re2)

    i = 0
    while i < len(param):
        j = 0
        while j < 4 and i+j < len(param):
            loc_3[j] = dec.find(param[i+j])
            j = j + 1

        loc_4[0] = (loc_3[0] << 2) + ((loc_3[1] & 48) >> 4);
        loc_4[1] = ((loc_3[1] & 15) << 4) + ((loc_3[2] & 60) >> 2);
        loc_4[2] = ((loc_3[2] & 3) << 6) + loc_3[3];

        j = 0
        while j < 3:
            if loc_3[j + 1] == 64:
                break
            try:
                loc_2 += unichr(loc_4[j])
            except:
                pass
            j = j + 1

        i = i + 4;

    return loc_2

#---------- get MY-HIT.RU URL --------------------------------------------------
def Get_Movie_HTML():
    url = 'http://docu.im/search/result'

    #-- split years
    if '-' in par.year:
        year1 = par.year.split('-')[0]
        year2 = par.year.split('-')[1]
    else:
        year1 = ''
        year2 = ''

    #-- get country code
    if par.country <> '':
        country = '{"id":"%s","name": "%s"}'%(par.country, par.country_name)
    else:
        country = ''

    #-- assemble filter
    search_filter = '{"title":"%s","fyear":"%s","tyear":"%s","genres":[%s],"directors":[],"actors":[],"countries":[%s],"studios":[]}'%(par.search, year1, year2, par.genre, country)
    #-- get count
    if par.count == 0:
        values = {
                    't'         : 'count',
                    'f'         : search_filter
                 }

        post = urllib.urlencode(values)
        html = get_HTML(url, post, 'http://docu.im/search')
        list = demjson3.loads(html)

        par.count = int(list['count'])

    #-- get HTML
    values = {
                'viewAs'    : 'list',
                'p'         : par.page,
                'f'         : search_filter
             }

    post = urllib.urlencode(values)
    html = get_HTML(url, post, 'http://docu.im/search')
    list = demjson3.loads(html)

    par.max_page = int(list['pagination']['totalPages'])

    html = ''
    if par.max_page > 0:
        for rec in list['items']:
            html +=  rec['html']

    return html

#----------- get Header string ---------------------------------------------------
def Get_Header():

    info  = 'Фильмов: ' + '[COLOR FF00FF00]' + str(par.count) + '[/COLOR]'

    if par.max_page > 1:
        info += ' | Pages: ' + '[COLOR FF00FF00]'+ par.page + '/' + str(par.max_page) +'[/COLOR]'

    if par.genre <> '':
        info += ' | Жанр: ' + '[COLOR FF00FFF0]'+ par.genre_name + '[/COLOR]'

    if par.year <> '':
        info += ' | Год: ' + '[COLOR FFFFF000]'+ par.year + '[/COLOR]'

    if par.country <> '':
        info += ' | Страна: ' + '[COLOR FFFF00FF]'+ par.country_name + '[/COLOR]'

    if par.search <> '':
        info += ' | Поиск: ' + '[COLOR FFFF9933]'+ par.search + '[/COLOR]'


    #-- info line
    name    = info
    i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
    u = sys.argv[0] + '?mode=EMPTY' + get_Filter(fname = name)
    xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- search
    if par.page == '1' and par.search == '':
        name    = '[COLOR FFFF9933][Поиск][/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=SEARCH' + get_Filter(fname = name)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- genres
    if par.genre == '' and par.page == '1' and par.search == '':
        name    = '[COLOR FF00FFF0][Жанры][/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=GENRES' + get_Filter(fname = name)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- year
    if par.year == '' and par.page == '1' and par.search == '':
        name    = '[COLOR FFFFF000][Год][/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=YEAR' + get_Filter(fname = name)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- country
    if par.country == '' and par.page == '1' and par.search == '':
        name    = '[COLOR FFFF00FF][Страна][/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=COUNTRY' + get_Filter(fname = name)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- previous page
    if int(par.page) > 1 :
        name    = '[COLOR FF00FF00][PAGE -1][/COLOR]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=MOVIE' + get_Filter(fname = name, page = str(int(par.page)-1))
        xbmcplugin.addDirectoryItem(h, u, i, True)

def Empty():
    return False

#---------- movie list ---------------------------------------------------------
def Movie_List():
        #--
        html = Get_Movie_HTML().replace("<span class='heading'>", "|<span class='heading'>").replace('<p>', '|Text:<p>')

        if html == '':
            return False
        # -- parsing web page --------------------------------------------------
        soup = BeautifulSoup(html, fromEncoding="utf-8")

        # -- add header info
        Get_Header()
        for rec in soup.findAll('div', {'class':'movie full clearfix'}):
            try:
                mi.title    = rec.find('div', {'class':'title'}).text.encode('utf-8')
                mi.url      = ('http://docu.im'+rec.find('div', {'class':'title'}).find('a')['href']).encode('utf-8')
                mi.alter    = rec.find('div', {'class':'alt-title'}).text.encode('utf-8')
                mi.img      = rec.find('img')['src']
                for sp in rec.find('div', {'class':'description'}).text.split('|'):
                   info = sp.split(':',1)
                   try:
                        if info[0].replace(' ','') == u'Страна':
                            mi.country = info[1].replace(',', ', ').encode('utf-8')
                        elif info[0].replace(' ','') == u'Жанры':
                            mi.genre = info[1].replace(',', ', ').encode('utf-8')
                        elif info[0].replace(' ','') == u'Режиссеры':
                            mi.director = info[1].replace(',', ', ').encode('utf-8')
                        elif info[0].replace(' ','') == u'Text':
                            mi.text = hpar.unescape(info[1]).encode('utf-8')
                        elif info[0].replace(' ','') == u'Год':
                            mi.year = int(info[1])
                   except:
                        pass

                #-- add movie to the list ------------------------------------------
                name = '[COLOR FFC3FDB8]'+mi.title+'[/COLOR]'

                i = xbmcgui.ListItem(name, iconImage=mi.img, thumbnailImage=mi.img)
                u = sys.argv[0] + '?mode=MOVIE_DETAIL' + get_Filter(fname = mi.title, url = mi.url, img = mi.img)
                i.setInfo(type='video', infoLabels={'title':       mi.title,
                                                    'originaltitle': mi.alter,
                            						'year':        mi.year,
                            						'director':    mi.director,
                            						'plot':        mi.text,
                            						'country':     mi.country,
                            						'genre':       mi.genre})
                #i.setProperty('fanart_image', mi.img)
                xbmcplugin.addDirectoryItem(h, u, i, True)
            except:
                pass

        #-- next page link
        if int(par.page) < par.max_page :
            name    = '[NEXT PAGE]'
            i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
            u = sys.argv[0] + '?mode=MOVIE' + get_Filter(fname = name, page = str(int(par.page)+1))
            xbmcplugin.addDirectoryItem(h, u, i, True)

        xbmcplugin.endOfDirectory(h)

#---------- movie detail list --------------------------------------------------
def Movie_Detail_List():
        #-- get movie detail
        url  = par.url
        html = get_HTML(url).replace("<span class='heading'>", "|<span class='heading'>").replace('<p>', '|Text:<p>')
        soup = BeautifulSoup(html, fromEncoding="utf-8", convertEntities=BeautifulSoup.HTML_ENTITIES)

        rec = soup.find('div', {'class':'movie full clearfix'})
        mi.title    = rec.find('div', {'class':'title'}).text.encode('utf-8')
        mi.url      = rec.find('div', {'class':'title'}).find('a')['href']
        mi.alter    = rec.find('div', {'class':'alt-title'}).text.encode('utf-8')
        mi.img      = rec.find('img')['src']
        for sp in rec.find('div', {'class':'description'}).text.split('|'):
           info = sp.split(':',1)
           try:
                if info[0].replace(' ','') == u'Страна':
                    mi.country = info[1].replace(',', ', ').encode('utf-8')
                elif info[0].replace(' ','') == u'Жанры':
                    mi.genre = info[1].replace(',', ', ').encode('utf-8')
                elif info[0].replace(' ','') == u'Режиссеры':
                    mi.director = info[1].replace(',', ', ').encode('utf-8')
                elif info[0].replace(' ','') == u'Text':
                    mi.text = hpar.unescape(info[1]).encode('utf-8')
                elif info[0].replace(' ','') == u'Год':
                    mi.year = int(info[1])
           except:
                pass

        movie_id = soup.find('div', {'class':'player-wrapper'}).find('div', {'id':'player'})['movie-id'].encode('utf-8')
        video_id = soup.find('div', {'class':'player-wrapper'}).find('div', {'id':'player'})['video-id'].encode('utf-8')

        try:
            if len(soup.find('div', {'id':'season-switch-items'})) > 0:
                is_Serial = True
            else:
                is_Serial = False
        except:
            is_Serial = False

        if is_Serial == True:
            for rec in soup.find('div', {'id':'season-switch-items'}).findAll('div', {'class':'switch-item'}):
                season_name = rec.find('a').text
                season_id = rec.find('a').text.replace(u'сезон', '').replace(u'Сезон', '').replace(u' ', '').encode('utf-8')

                url  = 'http://docu.im/movie/player/%s/playlist.txt?season=%s'%(movie_id, season_id)
                html = get_HTML(url)
                info = Decode(html)
                rec = demjson3.loads(info)
                try:
                    rec = demjson3.loads(rec['pl'])
                except:
                    pass

                for t in rec['playlist']:
                    name = season_name.encode('utf-8')+'  [COLOR FFC3FDB8]'+t['comment'].encode('utf-8')+'[/COLOR]'
                    mi.url   = t['file']

                    #-- add movie to the list ------------------------------------------
                    i = xbmcgui.ListItem(name, iconImage=par.img, thumbnailImage=par.img)
                    u = sys.argv[0] + '?mode=PLAY' + get_Filter(fname = mi.title, url = par.url+'|'+mi.url)

                    i.setInfo(type='video', infoLabels={'title':       mi.title,
                                                        'originaltitle': mi.alter,
                                						'year':        mi.year,
                                						'director':    mi.director,
                                						'plot':        mi.text,
                                						'country':     mi.country,
                                						'genre':       mi.genre})

                    #i.setProperty('fanart_image', mi.img)
                    xbmcplugin.addDirectoryItem(h, u, i, False)
            #xbmcplugin.endOfDirectory(h)
        else:
            url  = 'http://docu.im/movie/player/%s/style.txt'%(movie_id)
            html = get_HTML(url)
            info = Decode(html)

            rec = demjson3.loads(info)
            rec = demjson3.loads(rec['pl'])
            '''
            for t in rec['playlist']:
                par.name    = '[COLOR FFC3FDB8]'+t['comment'].encode('utf-8')+'[/COLOR]'
                par.url     = par.url+'|'+t['file']
                #-- add movie to the list ------------------------------------------
                i = xbmcgui.ListItem(name, iconImage=par.img, thumbnailImage=par.img)
                u = sys.argv[0] + '?mode=PLAY' + get_Filter(fname = mi.title, url = par.url+'|'+mi.url)
                xbmcplugin.addDirectoryItem(h, u, i, False)
            '''
            for t in rec['playlist']:
                    name = '[COLOR FFC3FDB8]'+t['comment'].encode('utf-8')+'[/COLOR]'
                    mi.url   = t['file']

                    #-- add movie to the list ------------------------------------------
                    i = xbmcgui.ListItem(name, iconImage=par.img, thumbnailImage=par.img)
                    u = sys.argv[0] + '?mode=PLAY' + get_Filter(fname = mi.title, url = par.url+'|'+mi.url)

                    i.setInfo(type='video', infoLabels={'title':       mi.title,
                                                        'originaltitle': mi.alter,
                                						'year':        mi.year,
                                						'director':    mi.director,
                                						'plot':        mi.text,
                                						'country':     mi.country,
                                						'genre':       mi.genre})

                    #i.setProperty('fanart_image', mi.img)
                    xbmcplugin.addDirectoryItem(h, u, i, False)

        xbmcplugin.endOfDirectory(h)

#---------- search movie list --------------------------------------------------
def Search_List():
    # show search dialog
    skbd = xbmc.Keyboard()
    skbd.setHeading('Поиск фильмов/сериалов.')
    skbd.doModal()
    if skbd.isConfirmed():
        SearchStr = skbd.getText().split(':')
        par.search = SearchStr[0]
        par.count = 0
        par.page  = '1'
    else:
        return False

    # show movies/serials
    Movie_List()

#---------- get genge list -----------------------------------------------------
def Genre_List():

    #-- get generes
    url = 'http://docu.im/search'
    html = get_HTML(url, None, 'http://docu.im/search')

    soup = BeautifulSoup(html, fromEncoding="utf-8")

    for rec in soup.find('div', {'id':'avaliable-genres'}).findAll('span', {'class':"genre-item "}):
        name = rec.text.replace("= 0}'>", '').encode('utf-8')
        genre_id = rec['id'].replace('genre_', '').encode('utf-8')
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=MOVIE' + get_Filter(genre = genre_id, genre_name = name, count = 0)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(h)

#---------- get country list -----------------------------------------------------
def Country_List():

    #-- get generes
    url = 'http://docu.im/country/autocomplete'
    html = get_HTML(url)

    list = demjson3.loads(html)

    for rec in list:
        name = rec['name'].encode('utf-8')
        country_id = rec['id'].encode('utf-8')
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=MOVIE' + get_Filter(country = country_id, country_name = name, count = 0)
        xbmcplugin.addDirectoryItem(h, u, i, True)

    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(h)

#---------- get year list -----------------------------------------------------
def Year_List():
    # show search dialog
    skbd = xbmc.Keyboard()
    skbd.setHeading('Фильтр по годам (<начало>-<конец>)')
    skbd.doModal()

    if skbd.isConfirmed():
        try:
            #-- начало
            try:
                year1 = int(skbd.getText().split('-')[0].replace(' ',''))
                if year1 < 1897:
                    year1 = 1897
                elif year1 > datetime.date.today().year:
                    year1 = datetime.date.today().year
            except:
                year1 = 1897

            #-- конец
            try:
                year2 = int(skbd.getText().split('-')[1].replace(' ',''))
                if year2 < 1897:
                    year2 = 1897
                elif year2 > datetime.date.today().year:
                    year2 = datetime.date.today().year
            except:
                year2 = datetime.date.today().year

            #-- сборка фильтра
            par.year = str(year1) + '-' + str(year2)
        except:
            par.year=''

        par.count = 0
        par.page  = '1'
    else:
        return False

    # show movies/serials
    Movie_List()

#-------------------------------------------------------------------------------

def PLAY():
    # -- parameters
    url  = par.url.split('|')[0]
    img  = par.img
    name = par.name

    # -- assemble RTMP link
    video_url = par.url.split('|')[1]

    v_host = video_url[:video_url.find('/[')+1]
    if v_host == '':
        v_host = video_url[:video_url.find('/docu')+1]


    v_quality = re.compile('\[(.+?)\]').findall(video_url)[0].split(',')
    try:
        v_audio = re.compile('aindex={(.+?)}').findall(video_url)[0]
    except:
        v_audio = re.compile('audioIndex={(.+?)}').findall(video_url)[0]

    if v_audio[0] == ';': v_audio = v_audio[1:]
    v_audio   = v_audio.split(';')

    v_auth = video_url[video_url.find('&wmsAuthSign='):]

    if len(v_quality) > 1 and Addon.getSetting('HQ') == 'false':
        qual_id = 1
    else:
        qual_id = 0

    if len(v_audio) > 1 and Addon.getSetting('LNG') == 'true':
        audio_id = 1
    else:
        audio_id = 0
    '''
    v_param = video_url[video_url.find('?'):video_url.find('{')]

    if Addon.getSetting('Ext_Player') == 'false':
        video = '%s app=docu swfUrl=http://docu.im/player/uppod.swf pageUrl=%s playpath=mp4:%s%s%s swfVfy=1 live=1'%(v_host, url, v_quality[0], v_param, v_audio[0])
        #video = '%s app=docu swfUrl=http://docu.im/player/uppod.swf pageUrl=%s playpath=mp4:%s?audioIndex=%s%s swfVfy=1 live=1'%(v_host, url, v_quality[0], v_audio[0], v_auth)
    '''
    v_param = video_url[video_url.find('?'):video_url.find('{')]

    v_auth1 = v_param.split('/',1)[0]

    if Addon.getSetting('Ext_Player') == 'false':
        video = '%s app=docu%s swfUrl=http://docu.im/player/uppod.swf pageUrl=%s playpath=mp4:%s%s%s swfVfy=1 live=1'%(v_host, v_auth1, url, v_quality[0], v_param, v_audio[0])
    else:
        rtmp = xbmc.translatePath(Addon.getSetting('RTMP'))
        vlc =  xbmc.translatePath(Addon.getSetting('VLC'))
        video = '"%srtmpdump.exe" "%svlc.exe" "%s"  "%s" "mp4:%s%s%s"'%(rtmp, vlc, v_host, url, v_quality[0], v_param, v_audio[0])

    i = xbmcgui.ListItem(name, path = urllib.unquote(video), thumbnailImage=img)
    xbmc.Player().play(video, i)

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

#-- get filter parameters
par = Get_Parameters(params)

try:
	mode = urllib.unquote_plus(params['mode'])
except:
	Movie_List()

if mode == 'MOVIE':
	Movie_List()
if mode == 'MOVIE_DETAIL':
	Movie_Detail_List()
if mode == 'SEARCH':
	Search_List()
elif mode == 'GENRES':
    Genre_List()
elif mode == 'COUNTRY':
    Country_List()
elif mode == 'YEAR':
    Year_List()
elif mode == 'EMPTY':
    Empty()
elif mode == 'PLAY':
	PLAY()


