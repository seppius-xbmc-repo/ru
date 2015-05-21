#!/usr/bin/python


import urllib2
import urllib
import json
import xbmcgui
import xbmcplugin
import xbmcaddon
import re,base64,random,time

from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
from urllib import unquote, quote, quote_plus
Addon = xbmcaddon.Addon( id = 'plugin.video.tushkan.net' )
__language__ = Addon.getLocalizedString

addon_icon    = Addon.getAddonInfo('icon')
addon_fanart  = Addon.getAddonInfo('fanart')
addon_path    = Addon.getAddonInfo('path')
addon_type    = Addon.getAddonInfo('type')
addon_id      = Addon.getAddonInfo('id')
addon_author  = Addon.getAddonInfo('author')
addon_name    = Addon.getAddonInfo('name')
addon_version = Addon.getAddonInfo('version')

import Cookie, cookielib
hos = int(sys.argv[1])
headers  = {
    'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)',
    'Accept'     :' text/html, application/xml, application/xhtml+xml, image/png, image/jpeg, image/gif, image/x-xbitmap, */*',
    'Accept-Language':'ru-RU,ru;q=0.9,en;q=0.8',
    'Accept-Charset' :'utf-8, utf-16, *;q=0.1',
    'Accept-Encoding':'identity, *;q=0'}
    
cook_file = xbmc.translatePath('special://temp/'+ 'truba.cookies')

def GET(target, post=None):
    target=target.replace('//page','/page')
    #print target
    try:
        cookiejar = cookielib.MozillaCookieJar()
        urlOpener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
        request = urllib2.Request(url = target, data = post, headers = headers)
        url = urlOpener.open(request)
        http=url.read()
        return http
    except Exception, e:
            xbmc.log( '[%s]: GET EXCEPT [%s]' % (addon_id, e), 4 )
            showMessage('HTTP ERROR', e, 5000)

def construct_request(params):
    return '%s?%s' % (sys.argv[0], urllib.urlencode(params))
    
def showMessage(heading, message, times = 3000, pics = addon_icon):
    try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading.encode('utf-8'), message.encode('utf-8'), times, pics.encode('utf-8')))
    except Exception, e:
        xbmc.log( '[%s]: showMessage: Transcoding UTF-8 failed [%s]' % (addon_id, e), 2 )
        try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, pics))
        except Exception, e:
            xbmc.log( '[%s]: showMessage: exec failed [%s]' % (addon_id, e), 3 )
            
def doSearch(params):
    try: 
        lnk=params['link']
        if 'tushkan.net' not in lnk: lnk='http://tushkan.net'+lnk
        http = GET(lnk)
    except: 
        lnk='http://tushkan.net/'
        http = GET(lnk)
    #print lnk
    beautifulSoup = BeautifulSoup(http)
    channels=beautifulSoup.findAll(id= re.compile('entryID_[0-9]+'))
    if channels:
        for ch in channels: 
            titl= ch.find('a').find('h3')#.string.encode('utf-8')
            #print titl.encode('utf-8')
            img= 'http://tushkan.net'+ch.find('img')['src']
            link=ch.find('a')['href']
            hh= re.compile('<b>Оригинальное название:</b>.+')
            #print ch
            tttl= (re.findall(hh,str(ch)))
            #print tttl
            try: tttl=tttl[0].split('</b>')[1]
            except: tttl=titl
            if tttl: 
                if len(tttl)<5: tttl=titl
                try:
                    li = xbmcgui.ListItem(tttl.replace('<br />',''), iconImage = addon_icon, thumbnailImage = img)
                
                    uri = construct_request({
                        'func': 'openitem',
                        'mpath': link
                    })
                    li.setProperty('fanart_image', addon_fanart)
                    xbmcplugin.addDirectoryItem(hos, uri, li, True)
                except: pass
    else:
        channels=beautifulSoup.findAll("table",attrs={"class":'eBlock'})
        for t in  channels: 
            link=t.find('a')['href']
            img=t.find('img')['src']
            titl=link.split('/')[-2]
            li = xbmcgui.ListItem(titl, iconImage = addon_icon, thumbnailImage = img)
                
            uri = construct_request({
                'func': 'openitem',
                'mpath': link
            })
            li.setProperty('fanart_image', addon_fanart)
            xbmcplugin.addDirectoryItem(hos, uri, li, True)
    
    gogers=beautifulSoup.findAll('a', attrs={'class': 'swchItem'})
    for n in gogers: 
        link= n['href']
        tt= n.find('span').string
        #print tt
        if tt==u'\xbb':
            li = xbmcgui.ListItem('Следующая страница', iconImage = addon_icon, thumbnailImage = addon_icon)
            uri = construct_request({
                'func': 'doSearch',
                'link':link
            })
            li.setProperty('fanart_image', addon_fanart)
            xbmcplugin.addDirectoryItem(hos, uri, li, True)
    
    xbmcplugin.endOfDirectory(hos)

def openitem(params):
    lk="http://tushkan.net"+params['mpath']
    http = GET(lk)
    #print lk
    beautifulSoup = BeautifulSoup(http)
    #print http
    titl= beautifulSoup.find('h1')#.string.encode('utf-8')
    #print titl.encode('utf-8')
    try: img= beautifulSoup.findAll('img', attrs={'width':'0'})[0]['src']
    except: img=addon_icon
    #print img
    hh= re.compile('<b>Оригинальное название:</b>.+')
    #print ch
    tttl= (re.findall(hh,str(beautifulSoup)))
    #print tttl
    try: ttt2=tttl[0].split('</b>')[1]
    except: ttt2=titl
    if len(ttt2)<5: ttt2=titl
    hh= re.compile('http://.+film/.+.flv')
    tttl= (re.findall(hh,str(http)))
    #img=addon_icon
    if tttl:
        link=tttl[0]
        li = xbmcgui.ListItem(ttt2, iconImage = addon_icon, thumbnailImage = img)
        uri = construct_request({
            'func': 'playitem',
            'mpath': link
        })
        li.setProperty('fanart_image', addon_fanart)
        li.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(hos, uri, li)
    else:
        hh= re.compile('http://.+.txt')
        tttl= (re.findall(hh,str(http)))
        link=tttl[0]
        http = GET(link)
        link=re.findall("pl:(.+), ",str(http))[0].replace("'",'"').replace(', st:"uppodvideo"})','').replace(', androidplayer:"1"','')
        if link:
            #print link
            json1=json.loads(link)
            pl= json1['playlist']
            for it in pl:
                try: pl0= it['playlist']
                except: pl0=None
                if pl0: 	
                    li = xbmcgui.ListItem(it['comment'].replace('<b>','[COLOR FF0FF000]').replace('</b>','[/COLOR]'), iconImage = addon_icon, thumbnailImage = img)
                    xbmcplugin.addDirectoryItem(hos, '', li)
                    for itt in pl0:
                        li = xbmcgui.ListItem(itt['comment'], iconImage = addon_icon, thumbnailImage = img)
                        uri = construct_request({
                            'func': 'payser',
                            'mpath': itt['file']
                        })
                        li.setProperty('fanart_image', addon_fanart)
                        li.setProperty('IsPlayable', 'true')
                        xbmcplugin.addDirectoryItem(hos, uri, li)
                else:
                    li = xbmcgui.ListItem(it['comment'], iconImage = addon_icon, thumbnailImage = img)
                    uri = construct_request({
                        'func': 'payser',
                        'mpath': it['file']
                    })
                    li.setProperty('fanart_image', addon_fanart)
                    li.setProperty('IsPlayable', 'true')
                    xbmcplugin.addDirectoryItem(hos, uri, li)

    xbmcplugin.endOfDirectory(hos)
    
def playitem(params):
    #print params['mpath']
    http = GET(params['mpath'])
    #print http
    hh= re.compile('http://.+.flv')
    link= re.findall(hh,str(http))[0]
    if link: item = xbmcgui.ListItem(path=link)
    #item = xbmcgui.ListItem(path=params['mpath'])
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

def payser(params):
    item = xbmcgui.ListItem(path=params['mpath'])
    #print params['mpath']
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

def _doSearch(params):
    kbd = xbmc.Keyboard()
    kbd.setDefault('')
    kbd.setHeading('Поиск')
    kbd.doModal()
    if kbd.isConfirmed():
        sts=kbd.getText()
        params={}
        params['link']='http://tushkan.net/search/?q='+urllib.quote(sts)+'&sfSbm=%D0%98%D1%81%D0%BA%D0%B0%D1%82%D1%8C&a=45'
        params['mode']='link'
        doSearch(params)
 
def run_settings(params):
    Addon.openSettings()

def mainScreen(params):

    li = xbmcgui.ListItem('Поиск', iconImage = addon_icon, thumbnailImage = addon_icon)
    uri = construct_request({
        'func': '_doSearch'
    })
    li.setProperty('fanart_image', addon_fanart)
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    
    li = xbmcgui.ListItem('Главная', iconImage = addon_icon, thumbnailImage = addon_icon)
    uri = construct_request({
        'func': 'doSearch',
        'mode':'news',
        'page':'1'
    })
    li.setProperty('fanart_image', addon_fanart)
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    
    http = GET('http://tushkan.net/')
    #print http
    beautifulSoup = BeautifulSoup(http)
    gogers=beautifulSoup.findAll('a', attrs={'class': 'catName'})
    for nn in gogers:
        link= nn['href']
        tt= nn.string
        li = xbmcgui.ListItem(tt, iconImage = addon_icon, thumbnailImage = addon_icon)
        uri = construct_request({
            'func': 'doSearch',
            'link':link
        })
        li.setProperty('fanart_image', addon_fanart)
        xbmcplugin.addDirectoryItem(hos, uri, li, True)
    
    
    xbmcplugin.endOfDirectory(handle=hos, succeeded=True, updateListing=False, cacheToDisc=True)
    
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

