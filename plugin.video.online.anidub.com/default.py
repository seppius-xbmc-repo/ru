#!/usr/bin/python
# -*- coding: utf-8 -*-
# /*
# *     
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

import urllib2
import urllib
import json
import xbmcgui
import xbmcplugin
import xbmcaddon
import re, base64, random, time

from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
from urllib import unquote, quote, quote_plus
Addon = xbmcaddon.Addon(id='plugin.video.online.anidub.com')
__language__ = Addon.getLocalizedString

addon_icon = Addon.getAddonInfo('icon')
addon_fanart = Addon.getAddonInfo('fanart')
addon_path = Addon.getAddonInfo('path')
addon_type = Addon.getAddonInfo('type')
addon_id = Addon.getAddonInfo('id')
addon_author = Addon.getAddonInfo('author')
addon_name = Addon.getAddonInfo('name')
addon_version = Addon.getAddonInfo('version')

VERSION = '4.3as'
DOMAIN = '131896016'
GATrack = 'UA-30985824-2'
try:
    import platform
    xbmcver = xbmc.getInfoLabel("System.BuildVersion").replace(' ', '_').replace(':', '_')
    UA = 'XBMC/%s (%s; U; %s %s %s %s) %s/%s XBMC/%s' % (xbmcver, platform.system(), platform.system(), platform.release(), platform.version(), platform.machine(), addon_id, addon_version, xbmcver)
except:
    UA = 'XBMC/Unknown %s/%s/%s' % (urllib.quote_plus(addon_author), addon_version, urllib.quote_plus(addon_name))
hos = int(sys.argv[1])
headers = {
    'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; rv:36.0) Gecko/20100101 Firefox/36.0',
    'Accept'     :'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language':'	ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Charset' :'utf-8, utf-16, *;q=0.1',

    'Referer':'http://online.anidub.com/'
}
headers2 = [
    ('User-Agent' , 'Mozilla/5.0 (Windows NT 6.1; rv:36.0) Gecko/20100101 Firefox/36.0'),
    ('Accept'     , 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
    ('Accept-Language', '	ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3'),
    ('Accept-Charset' , 'utf-8, utf-16, *;q=0.1'),

    ('Referer', 'http://online.anidub.com/')

]
try:
    from hashlib import md5
except:
    from md5 import md5
    
if not Addon.getSetting('GAcookie'):
    from random import randint
    GAcookie = "__utma%3D" + DOMAIN + "." + str(random.randint(0, 0x7fffffff)) + "." + str(random.randint(0, 0x7fffffff)) + "." + str(int(time.time())) + "." + str(int(time.time())) + ".1%3B"
    Addon.setSetting('GAcookie', GAcookie)
if not Addon.getSetting('uniq_id'):
    from random import randint
    uniq_id = random.random() * time.time()
    Addon.setSetting('uniq_id', str(uniq_id))

GAcookie = Addon.getSetting('GAcookie')
uniq_id = Addon.getSetting('uniq_id')
def send_request_to_google_analytics(utm_url, ua):

    try:

        req = urllib2.Request(utm_url, None, {'User-Agent':UA})
        response = urllib2.urlopen(req).read()
        # print utm_url
    except:
        ShowMessage('anidub', "GA fail: %s" % utm_url, 2000)
    return response

def track_page_view(path, nevent='', tevent='', UATRACK=GATrack):
    try:
        domain = DOMAIN
        document_path = unquote(path)
        utm_gif_location = "http://www.google-analytics.com/__utm.gif"
        extra = {}
        extra['screen'] = xbmc.getInfoLabel('System.ScreenMode')

        md5String = md5(str(uniq_id)).hexdigest()
        gvid = "0x" + md5String[:16]
        utm_url = utm_gif_location + "?" + \
            "utmwv=" + VERSION + \
            "&utmn=" + get_random_number() + \
            "&utmsr=" + quote(extra.get("screen", "")) + \
            "&utmt=" + nevent + \
            "&utme=" + tevent + \
            "&utmhn=localhost" + \
            "&utmr=" + quote('-') + \
            "&utmp=" + quote(document_path) + \
            "&utmac=" + UATRACK + \
            "&utmvid=" + gvid + \
            "&utmcc=" + GAcookie
        return send_request_to_google_analytics(utm_url, UA)
    except: return None

def GetMoonwalkUrl(url):
    token = re.findall('http://moonwalk.cc/video/(.+?)/', url)[0]

    req = urllib2.Request('http://moonwalk.cc/sessions/create_session', data='video_token=' + token + '&video_secret=HIV5')
    try:
        response = urllib2.urlopen(req)
        html = response.read()
        response.close()
    except Exception, e:
        print 'GET: Error getting page ' + url
        return None

    page = json.loads(html)
    url = page["manifest_m3u8"]
    return url

def getRealURL(url):    
    req = urllib2.Request(url)
    res = urllib2.urlopen(req)
    finalurl = res.geturl()
    return finalurl
    
def get_random_number():
    return str(random.randint(0, 0x7fffffff))

import Cookie, cookielib
if sys.platform == 'win32' or sys.platform == 'win64':
    cook_file = xbmc.translatePath('special://temp/' + 'anidub.cookies').decode('utf-8')
else: 
    cook_file = xbmc.translatePath('special://temp/' + 'anidub.cookies')

def GET(target, post=None):
    target = target.replace('//page', '/page')
    # print target
    # try:
    cookiejar = cookielib.MozillaCookieJar()
    urlOpener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
    urlOpener.addheaders = headers2
    auth = False
    if Addon.getSetting('auth') == '1':
        try:
                # print 'get from file'
                cookiejar.load(cook_file)
                for cook in cookiejar:
                    if cook.name == 'dle_user_id': auth = True
                    # print "%s=%s"%(cook.name,cook.value)
                # print 'get from file'
        except:
               

                values = {'login': 'submit', 'login_name':Addon.getSetting('login'), 'login_password':Addon.getSetting('password')}
                data = urllib.urlencode(values)
                request = urllib2.Request("http://online.anidub.com", data)
                url = urlOpener.open(request)
                http = url.read()
                # print http
                # print 'get new'
                for cook in cookiejar:
                    if cook.name == 'dle_user_id': auth = True
                    Addon.setSetting('auth', '1')
                    print "%s=%s" % (cook.name, cook.value)
                cookiejar.save(cook_file)
                # print 'get new saved'
                resp.close()
    if Addon.getSetting('auth') != '1' and Addon.getSetting('login'):
            print 'trying getting new cookies'
            req = urllib2.Request(url=target, data=post, headers=headers)
            resp = urllib2.urlopen(req)
            values = {'login': 'submit', 'login_name':Addon.getSetting('login'), 'login_password':Addon.getSetting('password')}
            data = urllib.urlencode(values)
            print data
            request = urllib2.Request("http://online.anidub.com", data)
            url = urlOpener.open(request)
            http = url.read()
            # print http
            # print 'get new'
            for cook in cookiejar:
                if cook.name == 'dle_user_id': auth = True
                # print "%s=%s"%(cook.name,cook.value)
            
            cookiejar.save(cook_file)
            # print 'get new saved'
            resp.close()
    if not auth: Addon.setSetting('auth', '0')
    else: Addon.setSetting('auth', '1')
    # cookiejar['dle_user_id']='188275'
    # cookiejar['dle_password']='91f13e2a4445cb2eae290b7339537e87'
    # cookiejar['dle_newpm']='0'
    request = urllib2.Request(url=target, data=post, headers=headers)
    
    try:
        url = urlOpener.open(request)
    # print url.read()
        http = url.read()
        url.close()
    except Exception, e:
        showMessage('Ошибка соединения', e)
        sys.exit()    
    # resp.headers['Set-Cookie']='dle_user_id=188275&dle_password=91f13e2a4445cb2eae290b7339537e87&dle_newpm=0'
    # CE = resp.headers.get('content-encoding')
    # http = resp.read()
    # resp.close()
    return http
    # except Exception, e:
    #        xbmc.log( '[%s]: GET EXCEPT [%s]' % (addon_id, e), 4 )
    #        showMessage('HTTP ERROR', e, 5000)

def construct_request(params):
    return '%s?%s' % (sys.argv[0], urllib.urlencode(params))
    
def showMessage(heading, message, times=3000, pics=addon_icon):
    try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading.encode('utf-8'), message.encode('utf-8'), times, pics.encode('utf-8')))
    except Exception, e:
        xbmc.log('[%s]: showMessage: Transcoding UTF-8 failed [%s]' % (addon_id, e), 2)
        try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, pics))
        except Exception, e:
            xbmc.log('[%s]: showMessage: exec failed [%s]' % (addon_id, e), 3)

def doSearch(params):
    track_page_view('search')
    kbd = xbmc.Keyboard()
    kbd.setDefault('')
    kbd.setHeading("Поиск")
    kbd.doModal()
    out = ''
    if kbd.isConfirmed():
        try:
            out = trans.detranslify(kbd.getText())
            out = str(out.encode("utf-8"))
        except:
            out = str(kbd.getText())
    url = 'http://online.anidub.com/index.php?do=search&story=%s&subaction=search' % out
    # print url
    par = {}
    par['url'] = url
    mainScreen(par)

def run_settings(params):
    Addon.openSettings()
    
def catalogue(paramas):
    li = xbmcgui.ListItem("Аниме по жанрам", iconImage=addon_icon, thumbnailImage=addon_icon)
    uri = construct_request({
        'func': 'custom',
        'mode': '1'
    })
    li.setProperty('fanart_image', addon_fanart)
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    
    li = xbmcgui.ListItem("Аниме по даберам", iconImage=addon_icon, thumbnailImage=addon_icon)
    uri = construct_request({
        'func': 'custom',
        'mode': '2'
    })
    li.setProperty('fanart_image', addon_fanart)
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    
    li = xbmcgui.ListItem("Аниме по годам", iconImage=addon_icon, thumbnailImage=addon_icon)
    uri = construct_request({
        'func': 'custom',
        'mode': '3'
    })
    li.setProperty('fanart_image', addon_fanart)
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    xbmcplugin.endOfDirectory(handle=hos, succeeded=True, updateListing=False, cacheToDisc=True)
    
def mainScreen(params):
    # xbmcplugin.setContent(hos,'movies')
    # Addon.getSetting('login')
    if Addon.getSetting('auth') == '0':
        li = xbmcgui.ListItem("Проверьте логин/пароль", iconImage=addon_icon, thumbnailImage=addon_icon)
        uri = construct_request({
            'func': 'run_settings'
        })
        li.setProperty('fanart_image', addon_fanart)
        xbmcplugin.addDirectoryItem(hos, uri, li, False)
    try:
        currpage = int(params['page'])
    except: currpage = 1
    # http://online.anidub.com/index.php?do=search&story=medaka&subaction=search
    track_page_view('main')
    
    
    try: 	
        link = params['url']
        
        # link=link.replace('//','/')
        # link=link.replace('http:/','http://')
    
    except: link = 'http://online.anidub.com/'
    try:
        page = params['page']
        newlink = link + '/page/' + page + '/'
        
    except:newlink = link
    # print newlink
    if newlink == 'http://online.anidub.com/':
        li = xbmcgui.ListItem("Поиск", iconImage=addon_icon, thumbnailImage=addon_icon)
        uri = construct_request({
            'func': 'doSearch'
            
        })
        li.setProperty('fanart_image', addon_fanart)
        xbmcplugin.addDirectoryItem(hos, uri, li, True)
        
        li = xbmcgui.ListItem("Каталог", iconImage=addon_icon, thumbnailImage=addon_icon)
        uri = construct_request({
            'func': 'catalogue'
        })
        li.setProperty('fanart_image', addon_fanart)
        xbmcplugin.addDirectoryItem(hos, uri, li, True)
        
        li = xbmcgui.ListItem("Ongoing", iconImage=addon_icon, thumbnailImage=addon_icon)
        uri = construct_request({
            'func': 'mainScreen',
            'url': 'http://online.anidub.com/anime_ongoing/'
        })
        li.setProperty('fanart_image', addon_fanart)
        xbmcplugin.addDirectoryItem(hos, uri, li, True)
        
        li = xbmcgui.ListItem("TV", iconImage=addon_icon, thumbnailImage=addon_icon)
        uri = construct_request({
            'func': 'mainScreen',
            'url': 'http://online.anidub.com/anime_tv/'
        })
        li.setProperty('fanart_image', addon_fanart)
        xbmcplugin.addDirectoryItem(hos, uri, li, True)
        
        li = xbmcgui.ListItem("Фильмы", iconImage=addon_icon, thumbnailImage=addon_icon)
        uri = construct_request({
            'func': 'mainScreen',
            'url': 'http://online.anidub.com/anime_movie/'
        })
        li.setProperty('fanart_image', addon_fanart)
        xbmcplugin.addDirectoryItem(hos, uri, li, True)
        
        li = xbmcgui.ListItem("OVA", iconImage=addon_icon, thumbnailImage=addon_icon)
        uri = construct_request({
            'func': 'mainScreen',
            'url': 'http://online.anidub.com/anime_ova/'
        })
        li.setProperty('fanart_image', addon_fanart)
        xbmcplugin.addDirectoryItem(hos, uri, li, True)
        
        li = xbmcgui.ListItem("Дорамы онлайн", iconImage=addon_icon, thumbnailImage=addon_icon)
        uri = construct_request({
            'func': 'mainScreen',
            'url': 'http://online.anidub.com/dorama/'
        })
        li.setProperty('fanart_image', addon_fanart)
        xbmcplugin.addDirectoryItem(hos, uri, li, True)
        
        li = xbmcgui.ListItem("Top 20", iconImage=addon_icon, thumbnailImage=addon_icon)
        uri = construct_request({
            'func': 'top20'
        })
        li.setProperty('fanart_image', addon_fanart)
        xbmcplugin.addDirectoryItem(hos, uri, li, True)
    
        li = xbmcgui.ListItem("Избранное", iconImage=addon_icon, thumbnailImage=addon_icon)
        uri = construct_request({
            'func': 'mainScreen',
            'url': 'http://online.anidub.com/favorites/'
        })
        li.setProperty('fanart_image', addon_fanart)
        xbmcplugin.addDirectoryItem(hos, uri, li, True)
        
    # link='http://online.anidub.com/'
    # print newlink
    http = GET(newlink.replace(' ', '%20'))
    # print http
    if http == None: return False
    
    beautifulSoup = BeautifulSoup(http)
    # print beautifulSoup
    content = beautifulSoup.find('div', attrs={'id': 'dle-content'})
    if content:
        cats = content.findAll('div', attrs={'class': 'maincont'})
        if not cats:
            cats = content.findAll('div', attrs={'class': 'news_short'})
            ttls = content.findAll('div', attrs={'class': 'newstitle'})
        for manga in cats:
            info = {}
            
            others = manga.findAll('li')
            info = getinfo(others)
            links = manga.find('div', attrs={'class': 'poster_img'})
            title = None
            if links:
                try: url = links.find('a')['href']
                except: 
                    try:
                        # <span class="newsmore">
                        url = manga.find('span', attrs={'class': 'newsmore'}).find('a')['href']
                        
                        if ttls[cats.index(manga) - 1]:
                            m = re.search('[^<>]+</a>', str(ttls[cats.index(manga) - 1]))
                            title = str(m.group(0)[:-4])
                            # print ttls[cats.index(manga)]
                            # print title
                            # print 
                        else:
                            m = re.search('[^<>]+</a>', str(ttls[len(ttls) - 1]))
                            title = str(m.group(0)[:-4])
                            # print '/alst'
                    except: url = ''
                # print links
                try:
                    img = links.find('img')['data-original']
                except:
                    img = ""
                # print img
                
                if not title: title = links.find('img')['alt']
                # print 'url %s'%url
                listitem = xbmcgui.ListItem(title, img, img)
                try:
                    uri = construct_request({
                    'func': 'get_anime',
                    'img':img,
                    'm_path':url
                    })
                except:
                    uri = construct_request({
                    'func': 'get_anime',
                    'img':img,
                    })
                try:
                    m = re.search('[^<>]+<', str(manga.findAll('div')[2]))
                    desc = str(m.group(0)[:-1])
                    # print desc
                    info['plot'] = str(desc)
                    info['plotoutline'] = str(desc)
                except: pass
                if info: listitem.setInfo(type='video', infoLabels=info)
                xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
                # print desc
            # except: pass
    try:
        currpage = int(params['page'])
        lastpage = int(params['last'])
    except:
        try:
            navi = beautifulSoup.find('span', attrs={'class': 'navigation'})
            currpage = 1
            pp = navi.findAll('a')
            lastpage = int(pp[len(pp) - 1].string)
        except:
            currpage = 1
            lastpage = 1
    
    if lastpage > currpage:
        li = xbmcgui.ListItem("Далее", iconImage=addon_icon, thumbnailImage=addon_icon)
        # print link+'page/'+str(currpage+1)
        uri = construct_request({
            'func': 'mainScreen',
            'page': str(currpage + 1),
            'last': lastpage,
            'url':link
        })
        li.setProperty('fanart_image', addon_fanart)
        xbmcplugin.addDirectoryItem(hos, uri, li, True)
    if lastpage > currpage + 10:
        li = xbmcgui.ListItem("Еще +10", iconImage=addon_icon, thumbnailImage=addon_icon)
        # print link+'page/'+str(currpage+10)
        uri = construct_request({
            'func': 'mainScreen',
            'page': str(currpage + 10),
            'last': lastpage,
            'url':link
        })
        li.setProperty('fanart_image', addon_fanart)
        xbmcplugin.addDirectoryItem(hos, uri, li, True)
    # print lastpage
    # xbmcplugin.addSortMethod(hos, xbmcplugin.SORT_METHOD_TITLE)
    xbmcplugin.endOfDirectory(handle=hos, succeeded=True, updateListing=False, cacheToDisc=True)

from urllib import unquote, quote, quote_plus
    
def custom(params):
    track_page_view('custom')
    
    link = 'http://online.anidub.com/'
    http = GET(link)
    if http == None: return False
    beautifulSoup = BeautifulSoup(http)
    zz = beautifulSoup.find('div', attrs={'class': 'l_col1'})
    content = zz.findAll('ul', attrs={'class': 'reset'})[int(params['mode'])]
    # aa=content.findAll('li')[int(params['mode'])]
    aa = content.findAll('a')
    # print aa
    for n in aa: 
        url = 'http://online.anidub.com' + str(n['href'].encode('utf-8'))  # .encode('utf-8').decode('utf-8')
        
        title = n.string.encode('utf-8')
        listitem = xbmcgui.ListItem(title, addon_icon)
        uri = construct_request({
            'func': 'mainScreen',
            'url':url
            })
        xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
    xbmcplugin.endOfDirectory(handle=hos, succeeded=True, updateListing=False, cacheToDisc=True)
def top20(params):
    track_page_view('top20')
    link = 'http://online.anidub.com/'
    http = GET(link)
    if http == None: return False
    beautifulSoup = BeautifulSoup(http)
    content = beautifulSoup.find('ul', attrs={'class': 'top20'})
    links = content.findAll('li')
    for lnks in links:
        url = lnks.find('a')['href']
        sc = str(lnks.find('script'))
        title = sc.split('"')[3]
        listitem = xbmcgui.ListItem(title, iconImage=addon_icon, thumbnailImage=addon_icon)
        uri = construct_request({
            'func': 'get_anime',
            'm_path':url
            })
        # listitem.setInfo(type='video')
        xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
        # m=re.search('str="[^/]+;',sc)
        # print str( m.group())
    xbmcplugin.endOfDirectory(handle=hos, succeeded=True, updateListing=False, cacheToDisc=True)

def get_anime(params):
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
    track_page_view('get')
    try: img = params['img']
    except: img = addon_icon
    # print params['m_path']
    http = GET(params['m_path'])
    if http == None: return False
    beautifulSoup = BeautifulSoup(http)
    # print beautifulSoup
    content = beautifulSoup.find('div', attrs={'id': 'vk1'})
    # print str(content)
    options = content.findAll('option')
    one = False
    if options:
        for list in options:
            # print list
            lnk = ''
            try:
                lnk = list['value'].split('|')[0]
            except: lnk = list['value']
            # print lnk
            links = beautifulSoup.find('div', attrs={'class': 'poster_img'})
            img = links.find('img')['src']
            listitem = xbmcgui.ListItem(list.string, img, img)
            listitem.setProperty('IsPlayable', 'true')
            uri = construct_request({
                    'func': 'play_anime',
                    'img':img,
                    'm_path':lnk
                    })
            if ('anidub.ru' in lnk)or ('anidub-online.ru' in lnk):
                xbmcplugin.addDirectoryItem(hos, uri, listitem)
                one = True
            elif 'moonwalk.cc' in lnk:
                print lnk
                '''lnk = GetMoonwalkUrl(lnk)''' 
                print lnk
                uri = construct_request({
                        'func': 'play_anime',
                        'img':img,
                        'm_path':lnk
                }) 
                xbmcplugin.addDirectoryItem(hos, uri, listitem)
            else:
                try:
                    link = beautifulSoup.findAll('iframe', attrs={'id':'film_main'})[0]['src']
                    uri = construct_request({
                        'func': 'play_anime',
                        'img':img,
                        'm_path':link
                        })
                    if not one: xbmcplugin.addDirectoryItem(hos, uri, listitem)
                    one = True
                except: pass
            # print lnk
    else: 
        links = beautifulSoup.find('div', attrs={'class': 'poster_img'})
        try:
            img = links.find('img')['data-original']
        except:
            img = ""
        listitem = xbmcgui.ListItem(beautifulSoup.find('h1', attrs={'class': 'titlfull'}).string, img, img)
        listitem.setProperty('IsPlayable', 'true')
        uri = construct_request({
                'func': 'play_anime',
                'img':img,
                'm_path':beautifulSoup.find('iframe', attrs={'id': 'film_main'})['src']
                })
        if 'anidub-online.ru' in beautifulSoup.find('iframe', attrs={'id': 'film_main'})['src']:
            xbmcplugin.addDirectoryItem(hos, uri, listitem)
    xbmcplugin.endOfDirectory(handle=hos, succeeded=True, updateListing=False, cacheToDisc=True)
    # m=re.search('http://vk.com/video_ext.php?oid=[^/]+',str(content))
    # desc = str( m.group())
    # print desc
def play_anime(params):
    track_page_view('', 'event', '5(Video*Play)')
    try: img = params['img']
    except: img = addon_icon
    # print params['m_path']
    if 'moonwalk.cc' in params['m_path'] :
        lnk = getRealURL(params['m_path'])
        #print lnk
        lnk = lnk.replace('iframe', 'index.m3u8')
        #print lnk  
        item = xbmcgui.ListItem(path=lnk)
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
    else :
        http = GET(params['m_path'].replace('anidub.ru', 'vk.com').replace('anidub-online.ru', 'vk.com'))
        # print http
        soup = BeautifulSoup(http, fromEncoding="windows-1251")
        av = 0
        for rec in soup.findAll('param', {'name':'flashvars'}):
            # print rec
            for s in rec['value'].split('&'):
                if s.split('=', 1)[0] == 'url240':
                   url240 = s.split('=', 1)[1]
                if s.split('=', 1)[0] == 'url360':
                   url360 = s.split('=', 1)[1]
                if s.split('=', 1)[0] == 'url480':
                   url480 = s.split('=', 1)[1]
                if s.split('=', 1)[0] == 'url720':
                   url720 = s.split('=', 1)[1]
                if s.split('=', 1)[0] == 'hd':
                   hd = s.split('=', 1)[1]
            video = url240
            qual = Addon.getSetting('qual')
            # print qual
            # print hd
            if int(hd) >= 3 and int(qual) == 3:
                video = url720
            elif int(hd) >= 2 and (int(qual) == 2 or int(qual) == 3):
                video = url480
            elif int(hd) >= 1 and (int(qual) == 1 or int(qual) == 2):
                video = url360
            # print video
            item = xbmcgui.ListItem(path=video)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
    
def getinfo(param):
    info = {}
    for infostring in param:
        try:
            m = re.search('[^<>]+<', str(infostring))
            comm = str(m.group(0)[:-1])
            m = re.search('[^<>]+</a', str(infostring))
            data = str(m.group(0)[:-3])
            # print "%s:%s"%(comm,data)
            if comm == "Год: ": info['year'] = int(data)
            if comm == "Жанр: ": info['genre'] = data
            if comm == "Режиссер: ": info['director'] = data
            if comm == "Автор оригинала: ": info['writer'] = data
        except: pass
    # print info
    return info

def get_params(paramstring):
    param = []
    if len(paramstring) >= 2:
        params = paramstring
        cleanedparams = params.replace('?', '')
        if (params[len(params) - 1] == '/'):
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]
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
    xbmc.log('[%s]: Primary input' % addon_id, 1)
    mainScreen(params)
if func != None:
    try: pfunc = globals()[func]
    except:
        pfunc = None
        xbmc.log('[%s]: Function "%s" not found' % (addon_id, func), 4)
        showMessage('Internal addon error', 'Function "%s" not found' % func, 2000)
    if pfunc: pfunc(params)

