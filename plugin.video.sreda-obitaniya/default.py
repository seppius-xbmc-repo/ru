#!/usr/bin/python
# -*- coding: utf-8 -*-


import urllib2
import urllib
import simplejson as json
import xbmcgui
import xbmcplugin
import xbmcaddon
import re,base64,random,time

from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
from urllib import unquote, quote, quote_plus
Addon = xbmcaddon.Addon( id = 'plugin.video.sreda-obitaniya' )
__language__ = Addon.getLocalizedString

addon_icon    = Addon.getAddonInfo('icon')
addon_fanart  = Addon.getAddonInfo('fanart')
addon_path    = Addon.getAddonInfo('path')
addon_type    = Addon.getAddonInfo('type')
addon_id      = Addon.getAddonInfo('id')
addon_author  = Addon.getAddonInfo('author')
addon_name    = Addon.getAddonInfo('name')
addon_version = Addon.getAddonInfo('version')
hos = int(sys.argv[1])
xbmcplugin.setContent(hos, 'movies')

def showMessage(heading, message, times = 3000, pics = addon_icon):
    try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading.encode('utf-8'), message.encode('utf-8'), times, pics.encode('utf-8')))
    except Exception, e:
        xbmc.log( '[%s]: showMessage: Transcoding UTF-8 failed [%s]' % (addon_id, e), 2 )
        try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, pics))
        except Exception, e:
            xbmc.log( '[%s]: showMessage: exec failed [%s]' % (addon_id, e), 3 )

def GET(target, post=None):

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
def construct_request(params):
    return '%s?%s' % (sys.argv[0], urllib.urlencode(params))

def main(params):
    
    listitem=xbmcgui.ListItem("Среда Обитания",addon_icon, addon_icon)
    uri = construct_request({
            'func': 'mainMain',
            'link':'http://www.1tv.ru/sfilms_editions/si6222'
            })
    xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
    
    listitem=xbmcgui.ListItem("Время обедать",addon_icon, addon_icon)
    uri = construct_request({
            'func': 'mainMain',
            'link':'http://www.1tv.ru/sprojects_editions/si=5871'
            })
    xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
    
    
    listitem=xbmcgui.ListItem("Контрольная Закупка",addon_icon, addon_icon)
    uri = construct_request({
            'func': 'mainMain',
            'link':'http://www.1tv.ru/sprojects_editions/si=5716'
            })
    xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
    
    listitem=xbmcgui.ListItem("О самом главном",addon_icon, addon_icon)
    uri = construct_request({
            'func': 'samMain',
            'link':'http://urgantshow.ru/episodes'
            })
    xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
    
    listitem=xbmcgui.ListItem("Вечерний Ургант",addon_icon, addon_icon)
    uri = construct_request({
            'func': 'mainMain',
            'link':'http://www.1tv.ru/sprojects_editions/si=5856'
            })
    xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
    
    listitem=xbmcgui.ListItem("ЖКХ",addon_icon, addon_icon)
    uri = construct_request({
            'func': 'mainMain',
            'link':'http://www.1tv.ru/sprojects_editions/si=5806'
            })
    xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
    
    listitem=xbmcgui.ListItem("Истина где-то рядом",addon_icon, addon_icon)
    uri = construct_request({
            'func': 'mainMain',
            'link':'http://www.1tv.ru/sprojects_editions/si=5917'
            })
    xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
    

    
    xbmcplugin.endOfDirectory(handle=hos, succeeded=True, updateListing=False, cacheToDisc=True)

    
def samMain(params):
    link='http://russia.tv/video/show/brand_id/5214'
    http = GET(link)
    if http == None: return False
    beautifulSoup = BeautifulSoup(http)
    #print beautifulSoup
    content = beautifulSoup.find('div',attrs={'class':'content'})
    link= content.find('iframe')['src']
    link='http://russia.tv/video/show/brand_id/5214'
    #<meta content="Новогоднее желание: бросить курить. Часть 2" itemprop="name" />
    #<meta content="http://cdn.static4.rtr-vesti.ru/vh/pictures/md/507/521.jpg" itemprop="image" />
    title= content.find('meta',attrs={'itemprop':'name'})['content'].encode('utf-8')
    img= content.find('meta',attrs={'itemprop':'image'})['content'].encode('utf-8')
    listitem=xbmcgui.ListItem(title,img, img)
    uri = construct_request({
            'func': 'plsam',
            'link':link
            })
    listitem.setProperty('IsPlayable', 'true')
    xbmcplugin.addDirectoryItem(hos, uri, listitem)
    content = beautifulSoup.findAll('li',attrs={'class':'item '})
    for vid in content:
        print vid
        img= vid.find('img', attrs={'class':'lazyload'})['data-original']
        link="http://russia.tv"+ vid.find('a', attrs={'class':'pic '})['href'].replace('/viewtype/picture','')
        title= vid.find('img', attrs={'class':'lazyload'})['alt']
        duration= vid.find('div', attrs={'class':'duration'}).string.encode('utf-8')
        dur=int(duration.split(':')[0])*60+int(duration.split(':')[1])
        if dur>20: title='[COLOR=FF00FF00]%s[/COLOR]'%title
        listitem=xbmcgui.ListItem(title,img, img)
        uri = construct_request({
                'func': 'plsam',
                'link':link
                })
        listitem.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(hos, uri, listitem)
        
    xbmcplugin.endOfDirectory(handle=hos, succeeded=True, updateListing=False, cacheToDisc=True)
    
    
def plsam(params):
    link=params['link']
    #print link
    http = GET(link)
    beautifulSoup = BeautifulSoup(http)
    #print beautifulSoup
    link= beautifulSoup.find('link',attrs={'rel':'video_src'})['href'].replace('/swf/','/video/')
    http1 = GET(link)
    #print link
    #print http1
    #"video":"http:\/\/cdn.v.rtr-vesti.ru\/_cdn_auth\/secure\/v\/vh\/vod_hls\/definst\/smil:vh\/smil\/094\/727_d20130619232958.smil\/playlist.m3u8?auth=mh&vid=94727"
    vid=re.findall('"video":"(.+?)"',str(http1))[0].replace('\/','/')
    #print vid
    item = xbmcgui.ListItem(path=vid)
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
def urgMain(params):
    try: link=params['link']
    except: link='http://www.1tv.ru/sfilms_editions/si6222'
    http = GET(link)
    if http == None: return False
    beautifulSoup = BeautifulSoup(http)
    content = beautifulSoup.findAll('div',attrs={'class':'preview'})
    for n in content:
        img=re.findall("'image': '(.+?)',",str(n))[0]
        link=re.findall("'file': '(.+?)',",str(n))[0]
        title2=re.findall("'title': '(.+?)'",str(n))[0].replace('Вечерний Ургант. ','')
        text=str(n.find('p'))
        plot= text.split('>')[1].split('<')[0]
        mysetInfo={}
        mysetInfo['plot'] = plot
        mysetInfo['plotoutline'] = plot
        title=n.find('h3').find('a').string
        listitem=xbmcgui.ListItem("%s (%s)"%(title.encode('utf-8'),title2),img, img)
        #listitem.setInfo(type='video', infoLabels = mysetInfo)
        uri = construct_request({
            'func': 'playlink',
            'img':img,
            'path':link
            })
        listitem.setProperty('IsPlayable', 'true')
        listitem.setInfo(type='video', infoLabels = mysetInfo)
        xbmcplugin.addDirectoryItem(hos, uri, listitem)
    try:    
        next = beautifulSoup.find('a',attrs={'id':'getContent'})
        ttl= next.string
    except:
        next = beautifulSoup.find('a',id=re.compile('getContent[\d]+'))
        ttl= next.string
    link=next['href']
    print ttl.encode('utf-8')
    print link.encode('utf-8')
    listitem=xbmcgui.ListItem(ttl,addon_icon, addon_icon)
        #listitem.setInfo(type='video', infoLabels = mysetInfo)
    uri = construct_request({
        'func': 'urgMain',
        'link':link
        })
    xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
    xbmcplugin.endOfDirectory(handle=hos, succeeded=True, updateListing=False, cacheToDisc=True)

def playlink(params):
    item = xbmcgui.ListItem(path=params['path'])
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
    
def mainMain(params):
    try: link=params['link']
    except: link='http://www.1tv.ru/sfilms_editions/si6222'
    http = GET(link)
    if http == None: return False
    beautifulSoup = BeautifulSoup(http)
    content = beautifulSoup.find('div',attrs={'class':'p_release first'})
    content=content.findAll('li')
    for num in content:	
        mysetInfo={}
        title=num.find('h3').find('a').string
        img=num.find('img')['src']
        url=num.find('a')['href']
        fdate=num.find('div', attrs={'class':'date'})
        fdate= str(fdate)
        fdate=fdate.replace('\r','').replace('\n','').split('>')[1].split('<')[0].split('года')[0].decode('utf-8','ignore').encode('utf-8','ignore')
        plt=num.find('p').find('a').string
        mysetInfo['plot'] = plt
        mysetInfo['plotoutline'] = plt
        listitem=xbmcgui.ListItem("%s, (%s)"%(title.encode('utf-8'),fdate),img, img)
        listitem.setInfo(type='video', infoLabels = mysetInfo)
        uri = construct_request({
            'func': 'mainScreen',
            'url':url
            })
        listitem.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(hos, uri, listitem)
    nxtpage = beautifulSoup.find('div',attrs={'class':'all_pages'})
    allstr=nxtpage.findAll('a')
    link=None
    for n in allstr:
        link=n['href']
    print link
    listitem=xbmcgui.ListItem('Еще',img, img)
    uri = construct_request({
        'func': 'mainMain',
        'link':link
        })
    xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
    xbmcplugin.endOfDirectory(handle=hos, succeeded=True, updateListing=False, cacheToDisc=True)
   
def mainScreen(params):
    if 'www.1tv.ru' in params['url']: link=params['url']
    else: link='http://www.1tv.ru/%s'%params['url']
    http = GET(link)
    print http
    beautifulSoup = BeautifulSoup(http)
    print beautifulSoup
    cot=beautifulSoup.find('meta',attrs={'property':'og:video'})
    url= cot['content'].split('file=')[1]
    url= urllib.unquote(url)
    http2=GET(url)
    be2=BeautifulSoup(http2)
    furl= be2.find('media:content')['url']
    item = xbmcgui.ListItem(path=furl)
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
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
    main(params)
if func != None:
    try: pfunc = globals()[func]
    except:
        pfunc = None
        xbmc.log( '[%s]: Function "%s" not found' % (addon_id, func), 4 )
        showMessage('Internal addon error', 'Function "%s" not found' % func, 2000)
    if pfunc: pfunc(params)

