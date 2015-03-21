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
import xbmc, xbmcgui, xbmcaddon
import urllib2, urllib, re, cookielib, sys, time, os
from datetime import date

Addon = xbmcaddon.Addon(id='plugin.video.igru.net.ua')

# load XML library
try:
    sys.path.append(os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib'))
    from BeautifulSoup  import BeautifulSoup
    import moviedb
except:
    try:
        sys.path.insert(0, os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib'))
        from BeautifulSoup  import BeautifulSoup
        import moviedb
    except:
        sys.path.append(os.path.join(os.getcwd(), r'resources', r'lib'))
        from BeautifulSoup  import BeautifulSoup
        import moviedb

import HTMLParser
hpar = HTMLParser.HTMLParser()

#---------- get movies info and save to XML --------------------------------------------------
def Update_Movie_XML(myDB, mode, url, header, dp, id):
    #-- grab serial's info from site
    count  = 0
    mcount = 0

    #-- get number of pages
    pages = get_Number_of_Pages(url)

    if myDB.isUpdate == 1:
        page_num = min(pages, max(10, pages - myDB.Get_Loaded_Pages(id)))
    else:
        page_num = pages

    xbmc.log('*** START UPLOAD FEPCOM.NET ('+ header +') Pages: '+str(page_num))
    header = '[COLOR FF00FF00]' + header + '[/COLOR]'

    percent = min(count*100/page_num, 100)
    dp.update(percent, header, 'Загружено: '+ str(count)+' из '+str(page_num)+' страниц','Кол-во фильмов: '+str(mcount))

    #-- process movie load
    for count in range(1, page_num+1):
        if (dp.iscanceled()): return
        percent = min(count*100/page_num, 100)

        xbmc.log('*** Page: '+str(count))

        try:
            mcount = get_Movie(url+'page/'+str(count)+'/', myDB, mcount, dp, percent, count, page_num, header)
        except:
            xbmc.log('*** failed page '+str(count))

        dp.update(percent, header, 'Загружено: '+ str(count)+' из '+str(page_num)+' страниц','Кол-во фильмов: '+str(mcount))
    #-- save number of loaded pages
    myDB.Set_Loaded_Pages(id, pages)

#------ get number of pages ----------------------------------------------------
def get_Number_of_Pages(url):
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

    # -- parsing web page --------------------------------------------------
    soup = BeautifulSoup(html, fromEncoding="windows-1251")

    page = 1

    for rec in soup.find('div', {'class':'navigation'}).findAll('a'):
        try:
            if int(rec.text) > page:
                page = int(rec.text)
        except:
            pass

    return page

#------ process page -----------------------------------------------------------
def get_Movie(url, myDB, mcount, dp, percent, count, page_num, header):
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

    try:
        html = f.read()
    except:
        try:
            html = f.read()
        except:
            xbmc.log('*** Can not open: '+url)
            return mcount


    # -- parsing web page --------------------------------------------------
    soup = BeautifulSoup(html, fromEncoding="windows-1251")

    for rec in soup.findAll('div', {'class':'short_post_link'}):
        if (dp.iscanceled()): return
        try:
            movie = get_Movie_Info(myDB, rec.find('a')['href'])
            if len(movie) > 0:
                myDB.Add_Movie(movie)
                mcount = mcount + 1
                dp.update(percent, header, 'Загружено: '+ str(count)+' из '+str(page_num)+' страниц','Кол-во фильмов: '+str(mcount))
        except:
            pass

    return mcount

#------ get movie detail info --------------------------------------------------
def get_Movie_Info(myDB, url):
    empty = []
    empty = {}

    #-- check if movie already in MovieDB
    if myDB.isUpdate == 1:
        if myDB.Is_Movie_Exists(url) == 1:
            return empty

    #-- get movie
    try:
    #-- get movie info
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

        try:
            html = f.read()
        except:
            try:
                html = f.read()
            except:
                xbmc.log('*** Failed to open: '+url)
                return empty

        #-- parsing web page
        soup = BeautifulSoup(html, fromEncoding="windows-1251")

        #-- check if page have video
        try:
            if len(soup.findAll('object', {'type':'application/x-shockwave-flash'})) < 1:
                return empty
        except:
            return empty

        #-- get movie info
        rec = soup.find('div', {'class' : 'post'})
        #-- retrieve movie info from page
        movie = []
        movie = {}
        #-- get and check categories
        movie_cat = []
        is_film = 0
        for cat in rec.find('div', {'class' : 'category'}).findAll('a'):
            if  cat.text == u'Документальное кино':
                is_film = 1
                if movie_cat.count(u'Документальное кино') == 0:
                    movie_cat.append(u'Документальное кино')
            elif cat.text == u'Ретро онлайн':
                is_film = 2
            elif cat.text == u'Фильмы онлайн':
                is_film = 3
            else:
                movie_cat.append( unescape(cat.text).capitalize())
                if cat.text == u'Юмор':
                    is_film = 4

        if is_film == 0: return empty               #-- film not found

        if is_film == 2:                            #-- add retro prefix for retro films
            for idx in range(0, len(movie_cat)):
                movie_cat[idx] = u'Ретро: ' + movie_cat[idx]

        movie['category'] = movie_cat
        #-- get image
        try:
            movie['image'] = rec.find('div', {'class' : 'post_content'}).find('img', {'class':'m_pic'})['src']
        except:
            try:
                movie['image'] = re.compile('src="(.+?)"', re.MULTILINE|re.DOTALL).findall(str(rec.find('div', {'class' : 'post_content'}).find('img', {'class':'m_pic'})))
            except:
                xbmc.log('**** IMG!!')
                return empty

        #-- get name
        movie['name'] = unescape(rec.find('h1').text)
        #-- get url
        movie['url'] = url

        #-- get movie info
        info_list = []
        info_list = {}
        info = rec.find('div', {'class' : 'post_content'})
        try:
            match=re.compile('<strong>(.+?)<\/strong>(.+?)<br \/>', re.MULTILINE|re.DOTALL).findall(str(info)+'<br />')

            for i in match:
                info_list[i[0].strip()] = i[1].strip()
        except:
            pass

        #-- get genres
        if is_film == 1:
            movie['genre'] = u'Документальное кино'
        elif is_film == 4:
            movie['genre'] = u'Юмор'
        else:
            try:
                movie['genre'] = unescape(info_list['Фильм относится к жанру:'])
            except:
                movie['genre'] = u''

        try:
            movie['origin'] = unescape(info_list['Оригинальное название:'])
        except:
            movie['origin'] = u''
        #-- year
        try:
            movie['year'] = unescape(info_list['Год выхода на экран:'])
        except:
            movie['year'] = u'0000'

        if unicode(movie['year']).isnumeric():
            pass
        else:
            try:
                 movie['year'] = re.compile('([0-9][0-9][0-9][0-9]?)', re.MULTILINE|re.DOTALL).findall( movie['year'])[0]
            except:
                 movie['year'] = '0000'

        try:
            movie['director'] = unescape(info_list['Постановщик:'])
        except:
            try:
                movie['director'] = unescape(info_list['Постановщик'])
            except:
                movie['director'] = ''

        try:
            movie['actor'] = unescape(info_list['Актеры, принявшие участие в съемках:'])
        except:
            movie['actor'] = u''

        try:
            movie['descr'] = unescape(info_list['Краткое описание:'])
        except:
            movie['descr'] = u''

        return movie
    except:
        return empty

#-- system functions -----------------------------------------------------------
def unescape(text):
    try:
        text = hpar.unescape(text)
    except:
        text = hpar.unescape(text.decode('utf8'))

    try:
        text = unicode(text, 'utf-8')
    except:
        text = text

    return text.strip()

#-------------------------------------------------------------------------------

if len(sys.argv) > 1:
    mode = sys.argv[1]
else:
    mode = 'UPDATE'

ret = 'NO'

if mode != 'UPDATE' and mode != 'INFO':
    dialog = xbmcgui.Dialog()
    if dialog.yesno('Внимание!', 'Пересоздание списка фильмов требует','значительного времени (0.5-2 часа).', 'Пересоздать список?'):
        ret = 'YES'
    else:
        ret = 'NO'

if mode == 'UPDATE' or ret == 'YES':
    #-- create MovieDB interface
    myDB = moviedb.MovieDB(mode)

    #-- show Dialog
    dp = xbmcgui.DialogProgress()
    dp.create(myDB.info)

    #-- films online
    Update_Movie_XML(myDB, mode, 'http://fepcom.net/filmy-onlajn/', '1. Фильмы онлайн', dp, 1)
    #-- documentary
    if dp.iscanceled() == False:
        Update_Movie_XML(myDB, mode, 'http://fepcom.net/dokumentalnoe-kino/', '2. Документальное кино', dp, 2)
    #-- retro films
    if dp.iscanceled() == False:
        Update_Movie_XML(myDB, mode, 'http://fepcom.net/retro-onlajn/', '3. Ретро онлайн',dp, 3)
    #-- humor
    if dp.iscanceled() == False:
        Update_Movie_XML(myDB, mode, 'http://fepcom.net/yumor/', '4. Юмор', dp, 4)
    #-- save loaded data
    if dp.iscanceled() == False:
        myDB.Save_to_XML()

    #-- close dialog
    dp.close()
else:
    if mode == 'INFO':
        #-- create MovieDB interface
        myDB = moviedb.MovieDB('READ')
        #-- open dialog
        dialog = xbmcgui.Dialog()
        dialog.ok('Информация', 'Список фильмов создан: ' + myDB.last_update, 'Кол-во фильмов: ' + str(len(myDB.movies)))


