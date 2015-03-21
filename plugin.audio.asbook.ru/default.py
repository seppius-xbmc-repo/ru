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
import re, os, urllib, urllib2, cookielib, time, random
from time import gmtime, strftime
from urlparse import urlparse

#(------------- Add 12/03/2015 Evgenii S----------------------------------------
import string
digs = string.digits + string.letters
#-------------- End Add 12/03/2015 Evgenii S------------------------------------

import xbmc, xbmcgui, xbmcplugin, xbmcaddon
#import json
import demjson3 as json

Addon = xbmcaddon.Addon(id='plugin.audio.asbook.ru')
icon = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'),'icon.png'))
fcookies = xbmc.translatePath(os.path.join(Addon.getAddonInfo('path'), r'resources', r'data', r'cookies.txt'))

# load XML library
try:
    sys.path.append(os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib'))
    from BeautifulSoup  import BeautifulSoup
    lib_path = os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib')
except:
    try:
        sys.path.insert(0, os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib'))
        from BeautifulSoup  import BeautifulSoup
        lib_path = os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib')
    except:
        sys.path.append(os.path.join(os.getcwd(), r'resources', r'lib'))
        from BeautifulSoup  import BeautifulSoup
        icon = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'icon.png'))
        lib_path = os.path.join(os.getcwd(), r'resources', r'lib')

import HTMLParser
hpar = HTMLParser.HTMLParser()

h = int(sys.argv[1])

def showMessage(heading, message, times = 3000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))

#---------- parameter/info structure -------------------------------------------
class Param:
    url             = ''
    genre           = ''
    page            = '1'
    name            = ''
    img             = ''
    bcount          = ''
    pcount          = ''
    track           = ''
    search          = ''

#---------- get parameters -----------------------------------------------------
def Get_Parameters(params):
    #-- url
    try:    p.url = urllib.unquote_plus(params['url'])
    except: p.url = ''
    #-- track
    try:    p.track = urllib.unquote_plus(params['track'])
    except: p.track = ''
    #-- img
    try:    p.img = urllib.unquote_plus(params['img'])
    except: p.img = ''
    #-- name
    try:    p.name = urllib.unquote_plus(params['name'])
    except: p.name = ''
    #-- genre
    try:    p.genre = urllib.unquote_plus(params['genre'])
    except: p.genre = ''
    #-- page
    try:    p.page = urllib.unquote_plus(params['page'])
    except: p.page = '1'
    #-- bcount
    try:    p.bcount = urllib.unquote_plus(params['bcount'])
    except: p.bcount = ''
    #-- pcount
    try:    p.pcount = urllib.unquote_plus(params['pcount'])
    except: p.pcount = ''
    #-- search
    try:    p.search = urllib.unquote_plus(params['search'])
    except: p.search = ''
    #-----
    return p

#-- get page source ------------------------------------------------------------
def get_URL(url, post = None, ref = None):
    request = urllib2.Request(url, post)

    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host',	'asbook.net')
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Language', 'ru-RU')
    request.add_header('Referer',	'http://asbook.net')

    try:
        f = urllib2.urlopen(request)
    except IOError, e:
        if hasattr(e, 'reason'):
            xbmc.log('We failed to reach a server. Reason: '+ e.reason)
        elif hasattr(e, 'code'):
            xbmc.log('The server couldn\'t fulfill the request. Error code: '+ str(e.code))

    html = f.read()

    return html

#----------- get Header string ---------------------------------------------------
def Get_Header(par):

    info  = '' #'Книг: ' + '[COLOR FF00FF00]' + par.bcount + '[/COLOR]'

    if int(par.pcount) > 1:
        info += ' | Pages: ' + '[COLOR FF00FF00]'+ par.page + '/' + par.pcount +'[/COLOR]'

    if par.genre <> '':
        info += ' | Жанр: ' + '[COLOR FF00FFF0]'+ par.genre + '[/COLOR]'

    if par.search <> '':
        info += ' | Поиск: ' + '[COLOR FF00FFF0]'+ par.search + '[/COLOR]'

    if info <> '':
        #-- info line
        name    = info
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=EMPTY'
        #-- filter parameters
        xbmcplugin.addDirectoryItem(h, u, i, True)

    #--- page navigation
    #-- first page link
    if int(par.page) > 1 :
        name    = '[FIRST PAGE]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=BOOK_LIST'
        u += '&name=%s'%urllib.quote_plus(par.name)
        u += '&url=%s'%urllib.quote_plus(par.url)
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&page=%s'%urllib.quote_plus('1')
        u += '&pcount=%s'%urllib.quote_plus(par.pcount)
        u += '&search=%s'%urllib.quote_plus(par.search)
        #u += '&bcount=%s'%urllib.quote_plus(par.bcount)
        xbmcplugin.addDirectoryItem(h, u, i, True)
    #-- previous page link
    if int(par.page) > 1 :
        name    = '[PREVIOUS PAGE]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=BOOK_LIST'
        u += '&name=%s'%urllib.quote_plus(par.name)
        u += '&url=%s'%urllib.quote_plus(par.url)
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&page=%s'%urllib.quote_plus(str(int(par.page)-1))
        u += '&pcount=%s'%urllib.quote_plus(par.pcount)
        u += '&search=%s'%urllib.quote_plus(par.search)
        #u += '&bcount=%s'%urllib.quote_plus(par.bcount)
        xbmcplugin.addDirectoryItem(h, u, i, True)

#----------- get Footer string ---------------------------------------------------
def Get_Footer(par):
    #--- page navigation
    #-- next page link
    if int(par.page) < int(par.pcount) :
        name    = '[NEXT PAGE]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=BOOK_LIST'
        u += '&name=%s'%urllib.quote_plus(par.name)
        u += '&url=%s'%urllib.quote_plus(par.url)
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&page=%s'%urllib.quote_plus(str(int(par.page)+1))
        u += '&pcount=%s'%urllib.quote_plus(par.pcount)
        u += '&search=%s'%urllib.quote_plus(par.search)
        #u += '&bcount=%s'%urllib.quote_plus(par.bcount)
        xbmcplugin.addDirectoryItem(h, u, i, True)
    #-- last page link
    if int(par.page) < int(par.pcount) :
        name    = '[LAST PAGE]'
        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode=BOOK_LIST'
        u += '&name=%s'%urllib.quote_plus(par.name)
        u += '&url=%s'%urllib.quote_plus(par.url)
        u += '&genre=%s'%urllib.quote_plus(par.genre)
        u += '&page=%s'%urllib.quote_plus(par.pcount)
        u += '&pcount=%s'%urllib.quote_plus(par.pcount)
        u += '&search=%s'%urllib.quote_plus(par.search)
        #u += '&bcount=%s'%urllib.quote_plus(par.bcount)
        xbmcplugin.addDirectoryItem(h, u, i, True)

def Empty():
    return False

# ----- search on site --------------------------------------------------------
def get_Search_HTML(search_str, page):
    url = 'http://asbook.net/index.php?do=search'
    str = search_str#.decode('utf-8').encode('windows-1251')

    values = {
                 'do'            : 'search'
                ,'subaction'     : 'search'
                ,'search_start'  : page
                ,'full_search'   : 0
                ,'result_from'   : (page-1)*10+1
                ,'story'         : str
            }

    post = urllib.urlencode(values)
    html = get_URL(url, post)

    return html

#---------- movie list ---------------------------------------------------------
def Book_List(params):
    #-- get filter parameters
    par = Get_Parameters(params)

    # show search dialog
    if par.search != '':
        if par.search == 'Y':
            skbd = xbmc.Keyboard()
            skbd.setHeading('Поиск сериалов.')
            skbd.doModal()
            if skbd.isConfirmed():
                SearchStr = skbd.getText().split(':')
                par.search = SearchStr[0]
            else:
                return False

        #-- get result
        html = get_Search_HTML(par.search, int(par.page))
    else:
        #== get book list =====================================================
        url = par.url+'page/'+par.page+'/'
        html = get_URL(url)

    # -- parsing web page --------------------------------------------------
    soup = BeautifulSoup(html, fromEncoding="windows-1251")

    #-- get number of pages
    if par.pcount == '0':
        pc = 1
        try:
            for rec in soup.find('div', {'class':'b-paginator'}).findAll('a'):
                try:
                    if pc < int(rec.text):
                        pc = int(rec.text)
                except:
                    pass
            par.pcount = str(pc)
        except:
            par.pcount = '1'

    #-- add header info
    Get_Header(par)

    #-- get book info
    #try:
    if par.search != '':
        for rec in soup.findAll('div', {'class':'b-searchpost'}):
            b_name  = unescape(rec.find('div', {'class':'b-searchpost__title'}).find('a').text).encode('utf-8')

            b_name_s = b_name.split('"')
            try:
                if b_name_s[0] == '':
                    b_name   = b_name_s[2].strip()+' "'+b_name_s[1].strip()+'"'
                    b_name_f = '[COLOR FFFFF000]'+b_name_s[2].strip()+'[/COLOR] [COLOR FF00FFF0]"'+b_name_s[1].strip()+'"[/COLOR]'
                elif b_name_s[2] == '':
                    b_name = b_name_s[0].strip()+' "'+b_name_s[1].strip()+'"'
                    b_name_f = '[COLOR FFFFF000]'+b_name_s[0].strip()+'[/COLOR] [COLOR FF00FFF0]"'+b_name_s[1].strip()+'"[/COLOR]'
            except:
                b_name_s = b_name.split('-')
                try:
                    b_name = b_name_s[0].strip()+' "'+b_name_s[1].strip()+'"'
                    b_name_f = '[COLOR FFFFF000]'+b_name_s[0].strip()+'[/COLOR] [COLOR FF00FFF0]"'+b_name_s[1].strip()+'"[/COLOR]'
                except:
                    b_name_f = '[COLOR FF00FFF0]"'+b_name+'"[/COLOR]'
            #---
            b_url   = rec.find('div', {'class':'b-searchpost__title'}).find('a')['href']
            try:
                b_img   = rec.find('img')['src']
            except:
                b_img = icon
            b_descr = ''#unescape(rec.find('div', {'class':'b-searchpost__text'}).text).encode('utf-8')

            i = xbmcgui.ListItem(b_name_f, iconImage=b_img, thumbnailImage=b_img)
            u = sys.argv[0] + '?mode=BOOK'
            u += '&name=%s'%urllib.quote_plus(b_name)
            u += '&url=%s'%urllib.quote_plus(b_url)
            u += '&genre=%s'%urllib.quote_plus(par.genre)
            u += '&page=%s'%urllib.quote_plus(par.page)
            u += '&pcount=%s'%urllib.quote_plus(par.pcount)
            i.setInfo(type='music', infoLabels={    'title':       b_name,
                            						#'plot':        b_descr,
                            						'genre':       par.genre})
            xbmcplugin.addDirectoryItem(h, u, i, True)
    else:
        for rec in soup.findAll('div', {'class':'b-showshort'}):
            b_name  = unescape(rec.find('div', {'class':'b-showshort__title'}).find('a').text).encode('utf-8')

            b_name_s = b_name.split('"')
            try:
                if b_name_s[0] == '':
                    b_name   = b_name_s[2].strip()+' "'+b_name_s[1].strip()+'"'
                    b_name_f = '[COLOR FFFFF000]'+b_name_s[2].strip()+'[/COLOR] [COLOR FF00FFF0]"'+b_name_s[1].strip()+'"[/COLOR]'
                elif b_name_s[2] == '':
                    b_name = b_name_s[0].strip()+' "'+b_name_s[1].strip()+'"'
                    b_name_f = '[COLOR FFFFF000]'+b_name_s[0].strip()+'[/COLOR] [COLOR FF00FFF0]"'+b_name_s[1].strip()+'"[/COLOR]'
            except:
                b_name_s = b_name.split('-')
                try:
                    b_name = b_name_s[0].strip()+' "'+b_name_s[1].strip()+'"'
                    b_name_f = '[COLOR FFFFF000]'+b_name_s[0].strip()+'[/COLOR] [COLOR FF00FFF0]"'+b_name_s[1].strip()+'"[/COLOR]'
                except:
                    b_name_f = '[COLOR FF00FFF0]"'+b_name+'"[/COLOR]'
            #---
            b_url   = rec.find('div', {'class':'b-showshort__title'}).find('a')['href']
            try:
                b_img   = rec.find('img')['src']
            except:
                b_img = icon
            b_descr = '' #unescape(rec.find('div', {'class':'post_text clearfix'}).text).encode('utf-8')

            i = xbmcgui.ListItem(b_name_f, iconImage=b_img, thumbnailImage=b_img)
            u = sys.argv[0] + '?mode=BOOK'
            u += '&name=%s'%urllib.quote_plus(b_name)
            u += '&url=%s'%urllib.quote_plus(b_url)
            u += '&genre=%s'%urllib.quote_plus(par.genre)
            u += '&page=%s'%urllib.quote_plus(par.page)
            u += '&pcount=%s'%urllib.quote_plus(par.pcount)
            #u += '&bcount=%s'%urllib.quote_plus(par.bcount)
            i.setInfo(type='music', infoLabels={    'title':       b_name,
                            						#'plot':        b_descr,
                            						'genre':       par.genre})
            xbmcplugin.addDirectoryItem(h, u, i, True)
    #except:
    #    pass

    #-- add footer info
    Get_Footer(par)

    xbmcplugin.endOfDirectory(h)


#---------- serial info ---------------------------------------------------------
def Book_Info(params):
    #-- get filter parameters
    par = Get_Parameters(params)
    #== get book details =================================================
    url = par.url
    html = get_URL(url)

    # ----------------------------------------------------------------------
    b_name      = ''
    b_score     = ''
    b_img       = ''
    b_descr     = ''
    b_year      = 0
    b_autor     = ''
    b_genre     = ''
    b_actor     = ''
    b_publisher = ''
    b_bitrate   = ''
    b_duration  = 0

    # -- parsing web page --------------------------------------------------
    soup = BeautifulSoup(html, fromEncoding="windows-1251")

    b_name      = urllib.unquote(soup.find('h1', {'class':'b-maintitle'}).text)
    b_score     = soup.find('div' ,{'class':'mark'}).text.replace(',', '.')

    try:
        b_img       = soup.find('div', {'class':'b-searchpost__cover'}).find('img')['src']
    except:
        try:
            b_img = re.compile('\<img (.+?)\/>').findall(html)
            for e in b_img:
                if 'title=' in e:
                    b_img = re.compile('src=\"(.+?)\"').findall(e)[0]
                    break
        except:
            b_img = icon

    b_descr     = urllib.unquote(soup.find('div', {'class':'b-searchpost__text'}).text)

    for rec in soup.find('div', {'class':'b-searchpost__data'}).findAll('div', {'class': "row"}):
        if rec.find('i', {'class' : "b-sprt icon-10-2"}):
            b_year = int(rec.find('div', {'class' : "cell string"}).find('a').text)

        if rec.find('i', {'class' : "b-sprt icon-7-2"}):
            b_publisher = rec.find('div', {'class' : "cell string"}).find('a').text

        if rec.find('i', {'class' : "b-sprt icon-9-1"}):
            s = rec.find('div', {'class' : "cell string"}).text
            b_duration = int(s.split(':')[0])*60*60+int(s.split(':')[1])*60+int(s.split(':')[2])

        if rec.find('i', {'class' : "b-sprt icon-5-2"}):
            b_autor = rec.find('div', {'class' : "cell string"}).find('a').text

        if rec.find('i', {'class' : "b-sprt icon-6-2"}):
            b_actor = rec.find('div', {'class' : "cell string"}).find('a').text

    #(------------- Change 12/03/2015 Evgenii S----------------------------------------
    #for j in soup.findAll('script', {'type':'text/javascript'}):
    #    if 'var flashvars = {' in j.text:
    #        pl = re.compile('var flashvars = {(.+?)}', re.MULTILINE|re.DOTALL).findall(j.text)
    #        b_url = pl[0].split(',')[1].replace('pl:','').replace('"','')
    packed_flash_data = soup.find('div', {'class':'b-fullpost__player_wrapper clearfix'}).contents[1].text
    unpacked_flash_data = eval('unpack' + packed_flash_data[packed_flash_data.find('}(')+1:-1])
    b_url = re.compile("json_url=\\'(.+?)\'", re.MULTILINE|re.DOTALL).findall(unpacked_flash_data)[0]
    #-------------- End Change 12/03/2015 Evgenii S------------------------------------

    # -- parsing web page --------------------------------------------------
    html = get_URL(b_url)

    n=0

    playlist = json.loads(html)
    for rec in playlist['playlist']:
        n+=1
        s_name = rec['comment'].encode('utf-8')
        s_url  = rec['file']

        i = xbmcgui.ListItem(s_name, path = urllib.unquote(s_url), thumbnailImage=b_img)
        u = sys.argv[0] + '?mode=PLAY'
        u += '&url=%s'%urllib.quote_plus(url) #b_url)
        u += '&name=%s'%urllib.quote_plus(s_name)
        u += '&img=%s'%urllib.quote_plus(b_img)
        u += '&track=%s'%urllib.quote_plus(str(n))
        i.setInfo(type='music', infoLabels={    'album':       b_name,
                                                'title' :      s_name,
                        						'year':        b_year,
                        						'artist':      b_actor,
                        						'comment':     b_descr,
                        						'genre':       par.genre,
                                                'rating':      b_score})
        i.setProperty('fanart_image', b_img)
        xbmcplugin.addDirectoryItem(h, u, i, False)

    xbmcplugin.endOfDirectory(h)

#---------- get genre list -----------------------------------------------------
def Genre_List(params):
    #-- get filter parameters
    par = Get_Parameters(params)

    # -- search ----------------------------------------------------------------
    name    = '[COLOR FF00FFF0]' + '[ПОИСК]' + '[/COLOR]'
    mode = 'BOOK_LIST'

    i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
    u = sys.argv[0] + '?mode='+mode
    #-- filter parameters
    u += '&search=%s'%urllib.quote_plus('Y')
    u += '&page=%s'%urllib.quote_plus('1')
    u += '&pcount=%s'%urllib.quote_plus('0')

    xbmcplugin.addDirectoryItem(h, u, i, True)

    #-- get generes
    url = 'http://asbook.net/'

    html = get_URL(url)
    soup = BeautifulSoup(html, fromEncoding="windows-1251")

    for rec in soup.find('ul', {'class':'b-header__menu clearfix'}).findAll('li'):
        try:
            if rec['class'] == 'sub-item': continue
        except:
            pass

        is_parent = (rec.find('a', {'class' : "b-header__menu_item_link"}) != None)


        if is_parent:
            name = rec.find('a').text
            mode = 'EMPTY'
        else:
            name = '  [COLOR FF00FF00]'+rec.find('a').text +'[/COLOR]' # [COLOR FF00FFF0]'+rec.find('span').text+'[/COLOR]'
            mode = 'BOOK_LIST'

        url = 'http://asbook.net/'+rec.find('a')['href']
        genre  = rec.find('a').text.encode('utf-8')
        bcount = 0 #rec.find('span').text.replace('(','').replace(')','')

        i = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        u = sys.argv[0] + '?mode='+mode
        #-- filter parameters
        u += '&genre=%s'%urllib.quote_plus(genre)
        u += '&url=%s'%urllib.quote_plus(url)
        u += '&page=%s'%urllib.quote_plus('1')
        u += '&pcount=%s'%urllib.quote_plus('0')

        xbmcplugin.addDirectoryItem(h, u, i, True)

    xbmcplugin.endOfDirectory(h)

#-------------------------------------------------------------------------------

def PLAY(params):
    # create play list
    pl=xbmc.PlayList(1)
    pl.clear()

    # -- parameters
    url  = urllib.unquote_plus(params['url'])
    name = urllib.unquote_plus(params['name'])
    img = urllib.unquote_plus(params['img'])
    track = int(urllib.unquote_plus(params['track']))

    header = {  'Host'                  :urlparse(url).hostname,
                'Referer'               :'http://asbook.net/player/uppod.swf',
                'User-Agent'            :'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C; .NET4.0E)'
             }

    #------------------------------------------------
    html = get_URL(url)
    # -- parsing web page
    soup = BeautifulSoup(html, fromEncoding="windows-1251")

    #(------------- Change 12/03/2015 Evgenii S----------------------------------------
    #for j in soup.findAll('script', {'type':'text/javascript'}):
    #    if 'var flashvars = {' in j.text:
    #        pl = re.compile('var flashvars = {(.+?)}', re.MULTILINE|re.DOTALL).findall(j.text)
    #        b_url = pl[0].split(',')[1].replace('pl:','').replace('"','')
    packed_flash_data = soup.find('div', {'class':'b-fullpost__player_wrapper clearfix'}).contents[1].text
    unpacked_flash_data = eval('unpack' + packed_flash_data[packed_flash_data.find('}(')+1:-1])
    b_url = re.compile("json_url=\\'(.+?)\'", re.MULTILINE|re.DOTALL).findall(unpacked_flash_data)[0]
    #-------------- End Change 12/03/2015 Evgenii S------------------------------------
    #------------------------------------------------
    html = get_URL(b_url)

    n = 0
    playlist = json.loads(html)
    for rec in playlist['playlist']:
        n += 1
        if track <= n:
            s_name = rec['comment'].encode('utf-8')
            s_url  = rec['file']+'|'+urllib.urlencode(header)

            i = xbmcgui.ListItem(s_name, path = urllib.unquote(s_url), thumbnailImage=img)
            i.setInfo(type='music', infoLabels={    'title' :     s_name,
                                                    'tracknumber':      str(n)})
            pl.add(s_url, i)

    xbmc.Player().play(pl)

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


#(------------- Add 12/03/2015 Evgenii S----------------------------------------
def int2base(x, base):

    if x < 0: sign = -1
    elif x == 0: return digs[0]
    else: sign = 1

    x *= sign
    digits = []

    while x:
        digits.append(digs[x % base])
        x /= base

    if sign < 0:
        digits.append('-')
    digits.reverse()
    return ''.join(digits)

def unpack(p, a, c, k, e=None, d=None):
    ''' unpack
    Unpacker for the popular Javascript compression algorithm.

    @param  p  template code
    @param  a  radix for variables in p
    @param  c  number of variables in p
    @param  k  list of c variable substitutions
    @param  e  not used
    @param  d  not used
    @return p  decompressed string

    example of call:
        txt = '....'
        eval('unpack' + txt[txt.find('}(')+1:-1])

    '''
    # Paul Koppen, 2011
    for i in xrange(c-1,-1,-1):
        if k[i]:
            p = re.sub('\\b'+int2base(i,a)+'\\b', k[i], p)
    return p
#-------------- End Add 12/03/2015 Evgenii S------------------------------------

#-------------------------------------------------------------------------------
params=get_params(sys.argv[2])

# get cookies from last session
cj = cookielib.FileCookieJar(fcookies)
hr  = urllib2.HTTPCookieProcessor(cj)
opener = urllib2.build_opener(hr)
urllib2.install_opener(opener)

p  = Param()
mode = None

try:
	mode = urllib.unquote_plus(params['mode'])
except:
	Genre_List(params)

if mode == 'BOOK_LIST':
	Book_List(params)
elif mode == 'GENRE':
    Genre_List(params)
elif mode == 'BOOK':
    Book_Info(params)
elif mode == 'EMPTY':
    Empty()
elif mode == 'PLAY':
	PLAY(params)


