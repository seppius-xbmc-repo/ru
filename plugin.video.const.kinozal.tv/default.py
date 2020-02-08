#!/usr/bin/python

import httplib
import urllib
import urllib2
import re, cookielib, base64
import sys
import os
import socket

import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmc
import xbmcaddon

import threading
import time
import random
import datetime
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
from ASCore import TSengine,_TSPlayer
from urllib import unquote, quote

    
__addon__ = xbmcaddon.Addon( id = 'plugin.video.const.kinozal.tv' )

where=['названии','имени актера','жанре','формула']
show=['везде','фильмы','мультфильмы','сериалы','шоу','музыку']
cshow=['0','1002','1003','1001','1006','1004']
form=['Все','DVDRip','HDRip','HD Blu-Ray и Remux', 'TVRip']
cform=['0','1','3','4','5']
filter=['Все','Золото','Серебро']
cfilter=['0','11','12']
print 'YEAR' 
try:
    iwhere=int(__addon__.getSetting('where'))
    ishow=int(__addon__.getSetting('show'))
    iform=int(__addon__.getSetting('form'))
    ifilter=int(__addon__.getSetting('filter'))
    iyear = __addon__.getSetting('year')
    print 'YEAR %s' %  iwhere
    querry=__addon__.getSetting('querry')
except:
    __addon__.setSetting('where','0')
    __addon__.setSetting('show','0')
    __addon__.setSetting('form','0')
    __addon__.setSetting('filter','1')
    __addon__.setSetting('querry','')
    import datetime
    __addon__.setSetting('year', str(datetime.date.today().year))


hos = int(sys.argv[1])
           
xbmcplugin.setContent(int(hos), 'movies')

__language__ = __addon__.getLocalizedString

addon_icon    = __addon__.getAddonInfo('icon')
addon_fanart  = __addon__.getAddonInfo('fanart')
addon_path    = __addon__.getAddonInfo('path')
addon_type    = __addon__.getAddonInfo('type')
addon_id      = __addon__.getAddonInfo('id')
addon_author  = __addon__.getAddonInfo('author')
addon_name    = __addon__.getAddonInfo('name')
addon_version = __addon__.getAddonInfo('version')


def showMessage(heading, message, times = 3000, pics = addon_icon):
    try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading.encode('utf-8'), message.encode('utf-8'), times, pics.encode('utf-8')))
    except Exception, e:
        xbmc.log( '[%s]: showMessage: Transcoding UTF-8 failed [%s]' % (addon_id, e), 2 )
        try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, pics))
        except Exception, e:
            xbmc.log( '[%s]: showMessage: exec failed [%s]' % (addon_id, e), 3 )

ktv_login=__addon__.getSetting('login')
ktv_password=__addon__.getSetting('password')
ktv_folder=__addon__.getSetting('download_path')
ktv_cookies_uid=__addon__.getSetting('cookies_uid')
ktv_cookies_pass=__addon__.getSetting('cookies_pass')

if not ktv_login or not ktv_password: __addon__.openSettings()

if not ktv_cookies_uid or not ktv_cookies_pass:
    cookiejar = cookielib.CookieJar()
    urlOpener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
    values = {'username': ktv_login, 'password':ktv_password}
    data = urllib.urlencode(values)
    request = urllib2.Request("http://kinozal.tv/takelogin.php", data)
    url = urlOpener.open(request)
    getted=None
    for cook in cookiejar:
        if cook.name=='uid': ktv_cookies_uid=cook.value
        if cook.name=='pass': ktv_cookies_pass=cook.value
        if cook.name=='pass': getted=True
    if getted:
        __addon__.setSetting('cookies_pass',ktv_cookies_pass)
        __addon__.setSetting('cookies_uid',ktv_cookies_uid)
    else: 
        showMessage('Ошибка','Не верен логин или пароль', 5000)   
        __addon__.openSettings()
# JSON понадобится, когда будет несколько файлов в торренте
try:
    import json
except ImportError:
    try:
        import simplejson as json
        xbmc.log( '[%s]: Error import json. Uses module simplejson' % addon_id, 2 )
    except ImportError:
        try:
            import demjson3 as json
            xbmc.log( '[%s]: Error import simplejson. Uses module demjson3' % addon_id, 3 )
        except ImportError:
            xbmc.log( '[%s]: Error import demjson3. Sorry.' % addon_id, 4 )

def construct_request(params):
    return '%s?%s' % (sys.argv[0], urllib.urlencode(params))

def GE3T(target, post=None):
    target=target.replace(' ','+')
    print target
    result = cache.cacheFunction(GET2, target, post)
    return result
    
def GET(target, post=None):
    #print target
    try:
        req = urllib2.Request(url = target, data = post)
        req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
        req.add_header('Accept', '*/*')
        req.add_header('Accept-Language', 'ru-RU')
        resp = urllib2.urlopen(req)
        CE = resp.headers.get('content-encoding')
        http = resp.read()
        resp.close()
        return http
    except Exception, e:
        xbmc.log( '[%s]: GET EXCEPT [%s]' % (addon_id, e), 4 )
        showMessage('HTTP ERROR', e, 5000)

        
def mainScreen(params):
    PlaceFolder('Закладки', {'func':'get_bookmarks'})
    PlaceFolder('Главная',{'func': 'get_main', 'link':'http://kinozal.tv/'})
    PlaceFolder('Топ раздач',{'func': 'get_top'})
    PlaceFolder('Раздачи',{'func': 'get_search'})
    PlaceFolder('Поиск раздач',{'func': 'get_customsearch'})
    xbmcplugin.endOfDirectory(hos)

def PlaceLink(title,params):
    li = xbmcgui.ListItem(title)
    uri = construct_request(params)
    xbmcplugin.addDirectoryItem(hos, uri, li, False)
    
def get_custom(params):
    try:
        par=int(params['par'])
    except:
        par=None

    iwhere=int(__addon__.getSetting('where'))
    ishow=int(__addon__.getSetting('show'))
    iform=int(__addon__.getSetting('form'))
    ifilter=int(__addon__.getSetting('filter'))
    dialog = xbmcgui.Dialog()
    if par==1:
        iwhere=dialog.select('Фильтр', where)
    if par==2:
        ishow=dialog.select('Фильтр', show)
    if par==3:
        iform=dialog.select('Фильтр', form)
    if par==4:
        ifilter=dialog.select('Фильтр', filter)

    __addon__.setSetting('where',str(iwhere))
    __addon__.setSetting('show',str(ishow))
    __addon__.setSetting('form',str(iform))
    __addon__.setSetting('filter',str(ifilter))

    xbmc.executebuiltin('Container.Refresh(%s?func=get_customsearch)' % sys.argv[0])
def get_customsearch(params):
    
    try:
        par=int(params['par'])
    except:
        par=None
        

    PlaceLink('Искать в %s'%where[iwhere],{'func': 'get_custom', 'par':'1'})
    PlaceLink('Искать %s'%show[ishow],{'func': 'get_custom', 'par':'2'})
    PlaceLink('Формат: %s'%form[iform],{'func': 'get_custom', 'par':'3'})
    PlaceLink('Фильтр: %s'%filter[ifilter],{'func': 'get_custom', 'par':'4'})
    PlaceLink('Год: %s' % iyear, {'func': 'get_querry', 'par':'year'})
    PlaceLink('Искать: %s'%querry,{'func': 'get_querry'})
    PlaceFolder('Поиск',{'func': 'get_search','s':'1'})
    xbmcplugin.endOfDirectory(hos)

    

def get_querry(params):
    if params.has_key("par"):
        iyear = __addon__.getSetting("year")
        if iyear == '':
            iyear = datetime.date.today().year
        
        iyear = xbmcgui.Dialog().numeric(int(iyear),'Год')
        
        if iyear == '':
            iyear = ""
        elif int(iyear) < 1900:
            iyear = 1900
        elif int(iyear) > int(datetime.date.today().year):
            showMessage('', '%s > %s' % (iyear, datetime.date.today().year))
            iyear = datetime.date.today().year
        __addon__.setSetting('year', str(iyear))
        
        
    else:    
        skbd = xbmc.Keyboard()
        skbd.setHeading('Поиск:')
        skbd.doModal()
        if skbd.isConfirmed():
            SearchStr = skbd.getText()
            params['search']=SearchStr.replace(' ','+').decode('utf-8').encode('cp1251')
            #print params['search']
        else:
            params['search']=''
        __addon__.setSetting('querry',str(SearchStr))
    xbmc.executebuiltin('Container.Refresh(%s?func=get_customsearch)' % sys.argv[0])
def PlaceFolder(title,params):
    li = xbmcgui.ListItem(title)
    uri = construct_request(params)
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    
def check_item_by_tytle(title):
	if ("ALAC" in title) or ("Lossless" in title) or ("FLAC" in title):
		return False
	else:
		return True

def get_main(params):
    http = GET(params['link'])
    beautifulSoup = BeautifulSoup(http)
    all= beautifulSoup.find('div',attrs={'class':'tp1_border'})
    cont= all.findAll('div',attrs={'class':'tp1_body'})
    for film in cont: 
        title= film.find('a')['title']
        if not check_item_by_tytle(title):
            continue
        img= film.find('a').find('img')['src']
        if 'http' not in img: img='http://kinozal.tv%s'%img
        lik=  str(film.find('a')['href']).split('=')
        torrlink= 'http://kinozal.tv/download.php/%s/[kinozal.tv]id%s.torrent'%(lik[1],lik[1])
        print torrlink
        info = {}
        desc = '%s' % film.find('div', attrs={'class':'tp1_desc1'})
        genre = desc[desc.find("<b>Жанр:</b>")+17:]
        genre = genre[:genre.find("<br />")]
        year = desc[desc.find("<b>Год выпуска:</b>") + 30:]
        year = year[:year.find("<br />")]
        director = desc[desc.find("<b>Режиссер:</b>") + 25:]
        director = director[:director.find("<br />")]
        xinfos = film.find('div', attrs={'class':'tp1_desc'}).findAll('div')
        plot = "";
        for xdesc in xinfos:
            for tag in xdesc.contents:
                if tag.__class__.__name__ == 'NavigableString':
                    plot = plot + '%s' % tag
                elif tag.name == 'b':
                    plot = plot + '[B]' + tag.getText() + '[/B]'
                elif tag.name == 'br':
                    plot = plot + '\r'

        info["genre"] = genre
        info["year"] = year
        info["plot"] = plot
        info["plotoutline"] = plot
        info["title"] = title
        info["director"] = director

        li = xbmcgui.ListItem(title,title,img,img)
        li.setProperty('fanart_image', img)
        li.setInfo(type = "video", infoLabels = info)
        uri = construct_request({
            'func': 'get_info',
            'url': "http://kinozal.tv/" + film.find('a')["href"],
        })
        xbmcplugin.addDirectoryItem(hos, uri, li, True)
    xbmcplugin.endOfDirectory(hos)

    xbmc.executebuiltin('Container.SetViewMode(%s)' % 503)
    

def get_view_mode():
        view_mode = ""
        controls = (50,51,500,501,508,503,504,515,505,511,550,551,560)
        for id in controls:
            try:
                if xbmc.getCondVisibility( "Control.IsVisible(%i)" % id ):
                    view_mode = id
                    return view_mode
                    break
            except:
                print 'error'
                pass
        return view_mode

def get_plot(container):
    plot = ""
    for tag in container.contents:
        if tag.__class__.__name__ == 'NavigableString':
            plot = plot + '%s' % tag
        elif tag.name == 'b':
            plot = plot + '[B]' + tag.getText() + '[/B]'
        elif tag.name == 'br':
            plot = plot + '\r'
        elif tag.name == 'a':
            plot = plot + '[I]' + tag.getText() + "[/I]"
    
    return plot

def get_detail_torr_1(container):
    tds = container.findAll('td')
    sp = tds[3].getText() + "/" + tds[4].getText()
    title = '[%s]%s' % (sp, tds[0].getText())
    if tds[0].a['class'] == 'r1':
        title = '[COLOR=FFDCAF35]%s[/COLOR]' % title
    elif tds[0].a['class'] == 'r2':
        title = '[COLOR=FFF0A7AD]%s[/COLOR]' % title
    else:
        title = '[COLOR=FFDDDDDD]%s[/COLOR]' % title
    dict = {}
    dict['sp'] = sp
    dict['title'] = title
    dict['url'] = tds[0].a['href']
    return dict

def get_detail_torr_2(container):
    tds = container.findAll('td')
    sp = tds[4].getText() + "/" + tds[5].getText()
    title = '[%s]%s' % (sp, tds[1].getText())
    if tds[1].a['class'] == 'r1':
        title = '[COLOR=FFDCAF35]%s[/COLOR]' % title
    elif tds[1].a['class'] == 'r2':
        title = '[COLOR=FFF0A7AD]%s[/COLOR]' % title
    else:
        title = '[COLOR=FFDDDDDD]%s[/COLOR]' % title
    dict = {}
    dict['sp'] = sp
    dict['title'] = title
    dict['url'] = tds[1].a['href']
    return dict

def get_detail_torr3(container):
    tds = container.findAll('td')
    sp = tds[5].getText() + "/" + tds[6].getText()
    title = '[%s]%s' % (sp, tds[1].getText())
    if tds[1].a['class'] == 'r1':
        title = '[COLOR=FFDCAF35]%s[/COLOR]' % title
    elif tds[1].a['class'] == 'r2':
        title = '[COLOR=FFF0A7AD]%s[/COLOR]' % title
    else:
        title = '[COLOR=FFDDDDDD]%s[/COLOR]' % title
    dict = {}
    dict['sp'] = sp
    dict['title'] = title
    dict['url'] = tds[1].a['href']
    return dict

def get_by_genre(img, info, id):
    lis = []
    detail = GET('http://kinozal.tv/ajax/details_get.php?id=%s&sr=101' % id) 
    bsdetail = BeautifulSoup(detail.decode('cp1251'))
    xdetails = bsdetail.findAll('tr', attrs={'class':'first'})

    for xdet in xdetails:

        det = get_detail_torr_1(xdet)
        sp = det['sp']
        title = det['title']
        url = det['url']
        li = xbmcgui.ListItem(title)
        li.setProperty('fanart_image', img)
        li.setInfo(type='video', infoLabels=info)
        dict = {}
        dict['li'] = li
        dict['folder'] = True
        uri = construct_request({
            'func': 'get_info',
            'url': "http://kinozal.tv/" + url,
        })
        dict['url'] = uri
        dict['id'] = ''
        lis.append(dict)
    return lis

def get_by_persone(img,info, id):
    lis = []
    detail = GET('http://kinozal.tv/ajax/details_get.php?id=%s&sr=102' % id) 
    bsdetail = BeautifulSoup(detail.decode('cp1251'))
    xdetails = bsdetail.findAll('tr')
    xdetails = xdetails[1:]
    for xdet in xdetails:
        det = get_detail_torr_2(xdet)
        sp = det['sp']
        title = det['title']
        url = det['url']
        li = xbmcgui.ListItem(title)
        li.setProperty('fanart_image', img)
        li.setInfo(type='video', infoLabels=info)
        dict = {}
        dict['li'] = li
        dict['folder'] = True
        uri = construct_request({
            'func': 'get_info',
            'url': "http://kinozal.tv/" + url,
        })
        dict['url'] = uri
        dict['id'] = ''
        lis.append(dict)
    return lis

def get_by_seed(img, info, id):
    lis = []
    detail = GET('http://kinozal.tv/ajax/details_get.php?id=%s&sr=103' % id) 
    bsdetail = BeautifulSoup(detail.decode('cp1251'))
    xdetails = bsdetail.findAll('tr')
    xdetails = xdetails[1:]
    for xdet in xdetails:
        det = get_detail_torr_2(xdet)
        sp = det['sp']
        title = det['title']
        url = det['url']
        li = xbmcgui.ListItem(title)
        li.setProperty('fanart_image', img)
        li.setInfo(type='video', infoLabels=info)
        dict = {}
        dict['li'] = li
        dict['folder'] = True
        uri = construct_request({
            'func': 'get_info',
            'url': "http://kinozal.tv/" + url,
        })
        dict['url'] = uri
        dict['id'] = ''
        lis.append(dict)
    return lis

def get_by_like(container, img, info, id):
    lis = []
    for torr in container.div.table.contents:
            if torr['class'] == 'mn':
                continue
            detail = get_detail_torr_1(torr)
            sp = detail['sp']
            title = detail['title']
            url = detail['url']

            li = xbmcgui.ListItem(title)
            li.setProperty('fanart_image', img)
            li.setInfo(type='video', infoLabels=info)
            dict = {}
            dict['li'] = li
            dict['folder'] = True
            uri = construct_request({
                'func': 'get_info',
                'url': "http://kinozal.tv/" + url,
            })
            dict['url'] = uri
            dict['id'] = ''
            lis.append(dict)
    return lis

def get_info(params):
    current_view = get_view_mode();

    http = GET(params["url"])
    beautifulSoup = BeautifulSoup(http)
    all = beautifulSoup.find('div',attrs={'class':'mn_wrap'})

    if (all == None):
        showMessage("Ошибка", "Торрент не найден")
        return
    img = all.find('img',attrs={'class':"p200"})["src"]
    if 'http' not in img: 
        img='http://kinozal.tv%s'%img
    menu = all.find('ul', attrs={"class": "men w200"})
    mitems = menu.findAll('a')
    sp = "";
    fc = 1;
    bookmark = None
    for link in mitems:
        if "Раздают" in link.getText().encode('utf-8'):
            sp = link.find('span', attrs={'class': 'floatright'}).getText()
        elif 'Скачивают' in link.getText().encode('utf-8'):
            sp =  sp + '/' + link.find('span', attrs={'class': 'floatright'}).getText()
        elif "Список файлов" in link.getText().encode('utf-8'):
            fc = int(link.span.getText())
        elif "Добавить в закладки" in link.getText().encode('utf-8'):
            bookmark = link['href']

    star = menu.find('div', attrs={'class' : 'starbar'}).findAll('a')
    tag_title = None
    for tag in all.contents:
        if (tag.name == "div"):
            tag_title = tag
            break;
    
    title = "[COLOR=FF008BEE][%s][%s]%s[/COLOR]" % (star.__len__(),sp.encode('utf-8'),tag_title.h1.a.getText().encode('utf-8'))
    id = params['url'].split('=')[1]
    #link = 'http://kinozal.tv/download.php/%s/[kinozal.tv]id%s.torrent' % (id, id)
    link = 'http://kinozal.tv/download.php?id=%s' % id
    xinfo = all.find('div', attrs={'class':'mn1_content'}).findAll('div', attrs={'class' : 'bx1 justify'})
    isBlock = False
    if xinfo.__len__() == 4:
        isBlock = True
        title = '[COLOR=FFFF0000]%s[/COLOR]' % xinfo[0].b.getText()
        xinfo = xinfo[2:]
    elif xinfo.__len__() > 2:
        xinfo = xinfo[1:]
    sinfo = '%s' % xinfo[0]
    info = {}
    year = sinfo[sinfo.find('<b>Год выпуска:</b>')+30:]
    year = year[:year.find('<br />')]
    genre = sinfo[sinfo.find('<b>Жанр:</b>') + 16:]
    genre = genre[:genre.find('<br />')]
    info['year'] = year
    info['genre'] = genre
    plot = "";

    plot = get_plot(xinfo[0].h2)
    plot = plot + '\n' + get_plot(xinfo[1].p)
    
    tech = all.find('div', attrs={'class':'justify mn2 pad5x5'})
    plot = plot + '\n' + get_plot(tech)
    info['plot'] = plot
    
    li = xbmcgui.ListItem(title, title, img, img)

    li.setProperty('fanart_image', img)
    li.setInfo(type='video', infoLabels=info)
    if isBlock:
        uri = ''
    else:
        uri = construct_request(
            {
                'func' : "play",
                'torr_url':link,
                'filename':'[kinozal.tv]id%s.torrent' % id,
                'img':img,
                'title':title
            })
        if fc == 1:
            li.setProperty('IsPlayable', 'true')

    menulist = []
    if bookmark:
        addbookmarkuri = construct_request({
            'func': 'http_request',
            'url': "http://kinozal.tv/" + bookmark
        })
        menulist.append(('[COLOR FF669933]Добавить[/COLOR][COLOR FFB77D00] в Закладки[/COLOR]', 'XBMC.RunPlugin(%s)' % (addbookmarkuri)))
    
    downloaduri = construct_request({
        'func': 'download',
        'url' : link,
        'filename' : '[kinozal.tv]id%s.torrent' % id
    })
    menulist.append(('[COLOR FF669933]Скачать[/COLOR]', 'XBMC.RunPlugin(%s)' % downloaduri))
    li.addContextMenuItems(menulist)

    xbmcplugin.addDirectoryItem(hos, uri, li, fc > 1)
    
    all = all.find('div', attrs={'class':'mn1_content'})
    bx1 = all.findAll('div', attrs={'class':'bx1'})
    bx1 = bx1[2]
    lis = []
    for tabs in bx1.div.ul.contents:
        dict = {}
        li = xbmcgui.ListItem(tabs.getText().upper().center(32,'-'))

        li.setProperty('fanart_image', img)
        li.setInfo(type='video', infoLabels=info)
        dict['li'] = li
        dict['folder'] = False
        dict['url'] = ''
        dict['id'] = tabs['id']
        lis.append(dict)

    bx20 = bx1.find('div', attrs={'class': 'justify mn2'})
    lis_like = []
    if (bx20.div.table != None):
        lis_like = get_by_like(bx20, img, info, id)
    lis_genre = get_by_genre(img, info, id)
    lis_persone = get_by_persone(img, info, id)
    lis_seed = get_by_seed(img, info, id)

    for li1 in lis:
        xbmcplugin.addDirectoryItem(hos, li1['url'], li1['li'], li1['folder'])
        if li1['id'].find('100') > 0:
            for li2 in lis_like:
                xbmcplugin.addDirectoryItem(hos, li2['url'], li2['li'], li2['folder'])
        elif li1['id'].find('101') > 0:
            for li2 in lis_genre:
                xbmcplugin.addDirectoryItem(hos, li2['url'], li2['li'], li2['folder'])
        elif li1['id'].find('102') > 0:
            for li2 in lis_persone:
                xbmcplugin.addDirectoryItem(hos, li2['url'], li2['li'], li2['folder'])
        elif li1['id'].find('103') > 0:
            for li2 in lis_seed:
                xbmcplugin.addDirectoryItem(hos, li2['url'], li2['li'], li2['folder'])
    xbmcplugin.endOfDirectory(hos)

    xbmc.executebuiltin('Container.SetViewMode(%s)' % 504)

def get_search(params):

    try:
        if params.has_key('s'):
            g=int(__addon__.getSetting('where'))
            c=cshow[ishow]
            v=cform[iform]
            w=cfilter[ifilter]
            qu= querry.decode('utf-8').encode('cp1251')
            iyear=__addon__.getSetting('year')
        else:
            g = 0
            c = 0
            v = 0
            w = 0
            qu = ""
            iyear = "0"

        link='http://kinozal.tv/browse.php?s=%s&g=%s&c=%s&v=%s&d=%s&w=%s&t=0&f=0'%(urllib.quote_plus(qu),g,c,v,iyear, w)

    except Exception, e:
        print 'Error %s' % e
        return
        link='http://kinozal.tv/browse.php?s=&g=0&c=0&v=0&d=0&w=0&t=0&f=0'
    print link
    http = GET(link)
    beautifulSoup = BeautifulSoup(http)
    cat= beautifulSoup.findAll('tr')
#	print cat
    leng=len(cat)
    for film in cat:
        try:
            
            size= film.findAll('td', attrs={'class':'s'})[1].string
            peers= film.findAll('td', attrs={'class':'sl_s'})[0].string
            seeds= film.findAll('td', attrs={'class':'sl_p'})[0].string
            xa = film.find('td', attrs={'class':'nam'}).find('a')
            title= xa.string
            if xa['class'] == 'r1':
                title = '[COLOR=FFDCAF35]%s[/COLOR]' % title
            elif xa['class'] == 'r2':
                title = '[COLOR=FFA0A7AD]%s[/COLOR]' % title
            else:
                title = '[COLOR=FFDDDDDD]%s[/COLOR]' % title
            link=xa['href']
            lik=  link.split('=')
            #glink='http://kinozal.tv%s'%link
            #data= GET(glink)
            #dataSoup = BeautifulSoup(data)
            #img= dataSoup.find('li', attrs={'class':'img'}).find('img')['src']
            #if 'http' not in img: img='http://kinozal.tv%s'%img
            img = addon_icon
            torrlink= 'http://kinozal.tv/download.php/%s/[kinozal.tv]id%s.torrent'%(lik[1],lik[1])
            li = xbmcgui.ListItem('%s\r\n[COLOR=FF008BEE](peers: %s seeds:%s size%s)[/COLOR]'%(title,peers, seeds, size),addon_icon,img)
            li.setProperty('fanart_image', img)
            #uri = construct_request({
            #    'func': 'play',
            #    'torr_url':torrlink,
            #    'filename':'[kinozal.tv]id%s.torrent'%lik[1],
            #    'img':addon_icon,
            #    'title':title
            #})
            uri = construct_request({
                'func': 'get_info',
                'url': "http://kinozal.tv/" + xa["href"],
            })
            xbmcplugin.addDirectoryItem(hos, uri, li, True, totalItems=leng)
    
        except: pass
    xbmcplugin.endOfDirectory(hos)
    #(50,51,500,501,508,503,504,515,505,511,550,551,560)
    xbmc.executebuiltin('Container.SetViewMode(%s)' % 51)

def get_top(params):

    http=GET('http://kinozal.tv/top.php')
    beautifulSoup = BeautifulSoup(http)
    cat= beautifulSoup.find('select',attrs={"class":"w100p styled"})
    cat=cat.findAll('option')
    for n in cat:
        if int(n['value']) not in [5,6,7,8,4,41,42,43,44]:
            li = xbmcgui.ListItem(n.string.encode('utf-8'),addon_icon,addon_icon)
            uri = construct_request({
                'func': 'get_top1',
                'link':'http://kinozal.tv/top.php?w=0&t=%s&d=0&f=0&s=0'%n['value']
            })
            xbmcplugin.addDirectoryItem(hos, uri, li, True)
    
   
    xbmcplugin.endOfDirectory(hos)
    
def get_top1(params):
    http = GET(params['link'])
    beautifulSoup = BeautifulSoup(http)
    content = beautifulSoup.find('div', attrs={'class': 'bx1 stable'})
    cats=content.findAll('a')
    #print cats
    for m in cats: 
        tit= m['title']
        lik=  str(m['href']).split('=')
        img=m.find('img')['src']
        if 'http' not in img: img='http://kinozal.tv%s'%img
        torrlink= 'http://kinozal.tv/download.php/%s/[kinozal.tv]id%s.torrent'%(lik[1],lik[1])

        li = xbmcgui.ListItem(tit,addon_icon,img)
        li.setProperty('fanart_image', img)
        #uri = construct_request({
        #    'func': 'play',
        #    'torr_url':torrlink,
        #    'filename':'[kinozal.tv]id%s.torrent'%lik[1],
        #    'img':img,
        #    'title':tit.encode('utf-8')
        #})
        uri = construct_request({
            'func': 'get_info',
            'url': "http://kinozal.tv/" + m['href'],
        })
        xbmcplugin.addDirectoryItem(hos, uri, li, True)
        #print tit
    xbmcplugin.endOfDirectory(hos)
    xbmc.executebuiltin('Container.SetViewMode(%s)' % 500)
    
def get_folder(params):
    path=ktv_folder
    dirList=os.listdir(path)
    for fname in dirList:
        if re.search('[^/]+.torrent', fname):
            tit=fname
            torrlink='a'
            li = xbmcgui.ListItem(fname)
            uri = construct_request({
                'func': 'play',
                'file':fname,
                'img':None,
                'title':tit
            })
            xbmcplugin.addDirectoryItem(hos, uri, li, True)
    xbmcplugin.endOfDirectory(hos)

def login():
    cookiejar = cookielib.CookieJar()
    urlOpener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
    values = {'username': ktv_login, 'password':ktv_password}
    data = urllib.urlencode(values)
    request = urllib2.Request("http://kinozal.tv/takelogin.php", data)
    url = urlOpener.open(request)
    return cookiejar

def http_request(params):
    cookie = login()
    req = params['url']
    urlOpener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
    url = urlOpener.open(req)
    http = url.read()
    return http

def del_bookmark(params):
    http_request(params)
    xbmc.executebuiltin("Container.Refresh")

def get_bookmarks(params):
    cookie = login()
    req = 'http://kinozal.tv/bookmarks.php?type=1'
    urlOpener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
    url = urlOpener.open(req)
    http = url.read()
    beautifulSoup = BeautifulSoup(http)
    
    bx20 = beautifulSoup.find('div', attrs={'class': 'content'}).find('div', attrs={'class':'bx2_0'});
    if bx20:
        table = bx20.table.findAll('tr');

        for line in table:
            if line.has_key('class') and line['class'] == 'mn':
                continue
            desc = get_detail_torr3(line)

            li = xbmcgui.ListItem(desc['title'],addon_icon,addon_icon)
            uri = construct_request({
                'func': 'get_info',
                'url': "http://kinozal.tv/" + desc['url'],
            })
            tds = line.findAll("td", attrs={'class': 's'})
            delbookmarkuri = construct_request({
                'func': 'del_bookmark',
                'url': "http://kinozal.tv/" + tds[tds.__len__()-1].a['href']
            })
            li.addContextMenuItems([('[COLOR FF669933]Удалить[/COLOR][COLOR FFB77D00] из Закладок[/COLOR]', 'XBMC.RunPlugin(%s)' % (delbookmarkuri),)])
            xbmcplugin.addDirectoryItem(hos, uri, li, True)
    xbmcplugin.endOfDirectory(hos)

def download(params):
    cookiejar = login();
    torr_link = params['url']
    urlOpener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
    request = urllib2.Request(torr_link)
    url = urlOpener.open(request)
    red = url.read()
    if '<!DOCTYPE HTML>' in red:
      showMessage('Ошибка', 'Проблема при скачивании ')
    filename=xbmc.translatePath(ktv_folder + params['filename'])
    f = open(filename, 'wb')
    f.write(red)
    f.close()
    showMessage('Kinozal.TV', 'Торрент-файл скачан') 

def play(params):
    print 'palyyy'
    filename=xbmc.translatePath(ktv_folder + params['filename'])
    ''' if os.path.isfile(filename): 
        try: 
            #f = open(filename, 'rb').read()
            yel=base64.b64encode(open(filename, 'rb').read())
            #red=f.read
            #f.close
            #print red.encode('utf-8')
        except: pass
    else:	'''
    
    cookiejar = login()
    torr_link=params['torr_url']
    urlOpener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
    request = urllib2.Request(torr_link)
    print torr_link
    url = urlOpener.open(request)
    red = url.read()
    if '<!DOCTYPE HTML>' in red:
        showMessage('Ошибка','Проблема при скачивании (превышен лимит?)')
        return False
    filename=xbmc.translatePath(ktv_folder + params['filename'])
    #f = open(filename, 'wb')
    #f.write(red)
    #f.close
    yel=base64.b64encode(red)
    torr_link=yel
    start_torr(torr_link, params['img'])
    
def start_torr(torr_link,img):

    TSplayer=TSengine()
    out=TSplayer.load_torrent(torr_link,'RAW')
    if out=='Ok':
        if TSplayer.files.__len__() == 1:
            for k,v in TSplayer.files.iteritems():
                play_url2({'torr_url':urllib.quote(torr_link),
                           'title': k.encode('utf-8'),
                           'ind': v,
                           'img': img})
                return
        for k,v in TSplayer.files.iteritems():
            li = xbmcgui.ListItem(urllib.unquote(k))
            
            uri = construct_request({
                't': urllib.quote(torr_link),
                'tt': k.encode('utf-8'),
                'i':v,
                'ii':urllib.quote(img),
                'func': 'addplist'
            })
            li.setProperty('IsPlayable', 'true')
            
            li.addContextMenuItems([('Добавить в плейлист', 'XBMC.RunPlugin(%s)' % uri),])
            uri = construct_request({
                'torr_url': urllib.quote(torr_link),
                'title': k,
                'ind':v,
                'img':img,
                'func': 'play_url2'
            })
            #li.addContextMenuItems([('Добавить в плейлист', 'XBMC.RunPlugin(%s?func=addplist&torr_url=%s&title=%s&ind=%s&img=%s&func=play_url2)' % (sys.argv[0],urllib.quote(torr_link),k,v,img  )),])
            xbmcplugin.addDirectoryItem(hos, uri, li)
    xbmcplugin.addSortMethod(hos, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    xbmcplugin.endOfDirectory(hos)
    TSplayer.end()

def addplist(params):

    li = xbmcgui.ListItem(params['tt'])
    uri = construct_request({
        'torr_url': params['t'],
        'title': params['tt'].decode('utf-8'),
        'ind':urllib.unquote_plus(params['i']),
        'img':urllib.unquote_plus(params['ii']),
        'func': 'play_url2'
    })
    xbmc.PlayList(xbmc.PLAYLIST_VIDEO).add(uri,li)
def play_url2(params):
    print 'play'
    torr_link=urllib.unquote(params["torr_url"])
    img=urllib.unquote_plus(params["img"])
    title=urllib.unquote_plus(params["title"])
    #showMessage('heading', torr_link, 10000)
    TSplayer=TSengine()
    out=TSplayer.load_torrent(torr_link,'RAW')
    if out=='Ok':
        lnk=TSplayer.get_link(int(params['ind']),title, img, img)
        if lnk:
           
            item = xbmcgui.ListItem(path=lnk)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)  

            while not xbmc.Player().isPlaying:
                xbmc.sleep(300)
            while TSplayer.player.active and not TSplayer.local: 
                TSplayer.loop()
                xbmc.sleep(300)
                if xbmc.abortRequested:
                    TSplayer.log.out("XBMC is shutting down")
                    break
            if TSplayer.local and xbmc.Player().isPlaying: 
                try: time1=TSplayer.player.getTime()
                except: time1=0
                
                i = xbmcgui.ListItem("***%s"%title)
                i.setProperty('StartOffset', str(time1))
                xbmc.Player().play(TSplayer.filename.decode('utf-8'),i)

        else:
            item = xbmcgui.ListItem(path='')
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), False, item) 
    TSplayer.end()
    xbmc.Player().stop
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
try:
    func = params['func']
    del params['func']
except:
    func = None
    xbmc.log( '[%s]: Primary input' % addon_id, 1 )
    mainScreen(params)
if func != None:
    try: pfunc = globals()[func]
    except:
        pfunc = None
        xbmc.log( '[%s]: Function "%s" not found' % (addon_id, func), 4 )
        showMessage('Internal addon error', 'Function "%s" not found' % func, 2000)
    if pfunc: pfunc(params)