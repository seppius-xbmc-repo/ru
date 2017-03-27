#!/usr/bin/python


import urllib2,antizapret
import urllib
import json
import xbmcgui
import xbmcplugin
import xbmcaddon
import re,base64,random,time


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

headers2  = {
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language':'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4',
    'Connection':'keep-alive',
    'Host':'tushkan.club',
    'Referer':'http://tushkan.club/',
    'Upgrade-Insecure-Requests':'1',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}

def GET(target, post=None, method='post'):
    target=target.replace('//page','/page')
    #print target
    try:
        cookiejar = cookielib.MozillaCookieJar()
        if Addon.getSetting('antizapret') == 'true':
            import antizapret
            urlOpener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar),antizapret.AntizapretProxyHandler())
        else: 
            urlOpener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
        urllib2.install_opener(urlOpener)
        if method == 'post':
            request = urllib2.Request(url = target, data = post, headers = headers)
        else:
            request = urllib2.Request(url = target, data = post, headers = headers2)
            request.get_method = lambda: 'GET'
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
        if 'tushkan.club' not in lnk: lnk='http://tushkan.club'+lnk
        http = GET(lnk)
    except: 
        lnk='http://tushkan.club/'
        http = GET(lnk)

    #print http
    #beautifulSoup = BeautifulSoup(http)
    names=re.compile('Оригинальное название:<\/b>([^#<]+)<br').findall(http)
    descriptions=re.compile('Описание:<\/b>([^#<]+)<span').findall(http)
    #print names
    lnks=re.compile('<a\s*href="([^#<]+)"\s*title="([^"<]+)"[^>]+>\s*<img.*src="([^#<]+)"[^О]*><b>Оригинальное название:<\/b>([^#<]+)<').findall(http)

    i=0                                                                                   
    #print len(names), len(lnks)
    for ch in lnks:
        title=ch[3].strip()
        description = title
        try:
            description = descriptions[i].strip() + '...' if descriptions[i] else title
        except:
            pass
        url=ch[0]
        if 'tushkan.club' in ch[2]: img=ch[2]
        else:        img= 'http://tushkan.club'+ch[2]
        li = xbmcgui.ListItem(title, iconImage = img, thumbnailImage = img)
        uri = construct_request({
                        'func': 'openitem',
                        'mpath': url
        })
        li.setInfo(type='Video', infoLabels={'title': title, 'plot': description})
        li.setProperty('fanart_image', addon_fanart)
        xbmcplugin.addDirectoryItem(hos, uri, li, True)
        i=i+1
        if len(names)<i: i=0

    try:
        lnk=re.compile('<!-- Next page link -->\s*<a class="swchItem"\s*href="([^"<]+)">').findall(http)[0]
        li = xbmcgui.ListItem('Следующая страница', iconImage = addon_icon, thumbnailImage = addon_icon)
        uri = construct_request({
            'func': 'doSearch',
            'link':lnk
        })
        li.setProperty('fanart_image', addon_fanart)
        xbmcplugin.addDirectoryItem(hos, uri, li, True)
    except: pass
    xbmcplugin.setContent(hos, 'movies')
    xbmcplugin.endOfDirectory(hos)

def openitem(params):
    lk="http://tushkan.club"+params['mpath']
    http = GET(lk, method = 'get')
    #print lk

    #print titl.encode('utf-8')
    img=addon_icon
    #print img

    #ttt=re.compile('title="([^"]+)"\s*src="([^"]+)"><\/div>').findall(http)
    ttt=re.compile('title="([^"]+)"\s*src="([^"]+)">').findall(http)
    img="http://tushkan.club"+ttt[0][1]
    ttt2=ttt[0][0]
    hh= re.compile('http://.+film/.+.flv')
    tttl= (re.findall(hh,str(http)))
    #img=addon_icon
    if tttl:
        link=tttl[0]
        li = xbmcgui.ListItem(ttt2, iconImage = img, thumbnailImage = img)
        li.setInfo(type='Video', infoLabels={'title': ttt2, 'plot': ttt2})
        uri = construct_request({
            'func': 'playitem',
            'mpath': link
        })
        li.setProperty('fanart_image', addon_fanart)
        li.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(hos, uri, li)
    else:
        hh = re.compile('"http://.+.txt')
        tttl= (re.findall(hh,str(http)))
        link=tttl[1].replace('"', '')
        http = GET(link)
        #print http
        link=re.findall('pl :"(.+)"',str(http))[0].replace("'",'"')

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
                        li = xbmcgui.ListItem(itt['comment'], iconImage = img, thumbnailImage = img)
                        uri = construct_request({
                            'func': 'payser',
                            'mpath': itt['file'].replace('.xyz', '.net')
                        })
                        li.setInfo(type='Video', infoLabels={'title': itt['comment'], 'plot': itt['comment']})
                        li.setProperty('fanart_image', addon_fanart)
                        li.setProperty('IsPlayable', 'true')
                        xbmcplugin.addDirectoryItem(hos, uri, li)
                else:
                    li = xbmcgui.ListItem(it['comment'], iconImage = img, thumbnailImage = img)
                    uri = construct_request({
                        'func': 'payser',
                        'mpath': it['file']
                    })
                    li.setInfo(type='Video', infoLabels={'title': it['comment'], 'plot': it['comment']})
                    li.setProperty('fanart_image', addon_fanart)
                    li.setProperty('IsPlayable', 'true')
                    xbmcplugin.addDirectoryItem(hos, uri, li)

    xbmcplugin.setContent(hos, 'movies')
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
    usearch = params.get('usearch', False)
    if usearch:
        keyword = params['keyword']
        params={}
        params['link']='http://tushkan.club/search/?q='+urllib.quote(keyword)+'&sfSbm=%D0%98%D1%81%D0%BA%D0%B0%D1%82%D1%8C&a=45'
        params['mode']='link'
        doSearch(params)
        return
        
    kbd = xbmc.Keyboard()
    kbd.setDefault('')
    kbd.setHeading('Поиск')
    kbd.doModal()
    if kbd.isConfirmed():
        sts=kbd.getText()
        params={}
        params['link']='http://tushkan.club/search/?q='+urllib.quote(sts)+'&sfSbm=%D0%98%D1%81%D0%BA%D0%B0%D1%82%D1%8C&a=45'
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
    
    http = GET('http://tushkan.club/')
    #print http
    gogr=re.compile('"catName"\s*href="([^>]+)">([^"]+)<\/a>').findall(http)
    for nn in gogr:
        link= nn[0]
        tt= nn[1]
        li = xbmcgui.ListItem(tt, iconImage = addon_icon, thumbnailImage = addon_icon)
        li.setInfo(type='Video', infoLabels={'title': tt, 'plot': tt})
        uri = construct_request({
            'func': 'doSearch',
            'link':link
        })
        li.setProperty('fanart_image', addon_fanart)
        xbmcplugin.addDirectoryItem(hos, uri, li, True)
    
    xbmcplugin.setContent(hos, 'files')    
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

