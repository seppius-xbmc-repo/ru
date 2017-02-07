#!/usr/bin/python
# -*- coding: utf-8 -*-


import urllib2
import urllib
import json
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
    
    
    listitem=xbmcgui.ListItem("Естественный Отбор ТВЦ",addon_icon, addon_icon)
    uri = construct_request({
            'func': 'tvcMain',
            'link':'http://www.tvc.ru/channel/brand/id/2723/show/episodes'
            })
    xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
    
    listitem=xbmcgui.ListItem("Без обмана ТВЦ",addon_icon, addon_icon)
    uri = construct_request({
            'func': 'tvcMain',
            'link':'http://www.tvc.ru/channel/brand/id/73/show/episodes'
            })
    xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
    
    listitem=xbmcgui.ListItem("Вечерний Ургант 1 Канал",addon_icon, addon_icon)
    uri = construct_request({
            'func': 'mainMain',
            'link':'http://www.1tv.ru/video_materials.json?collection_id=41&index=1'
            })
    xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
    
    listitem=xbmcgui.ListItem("Теория заговора 1 Канал",addon_icon, addon_icon)
    uri = construct_request({
            'func': 'mainMain',
            'link':'http://www.1tv.ru/video_materials.json?collection_id=627&index=1'
            })
    xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
    
    
    listitem=xbmcgui.ListItem("Контрольная Закупка 1 Канал",addon_icon, addon_icon)
    uri = construct_request({
            'func': 'mainMain',
            'link':'http://www.1tv.ru/video_materials.json?collection_id=78&index=1'
            })
    xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
    
    listitem=xbmcgui.ListItem("О самом главном Россия",addon_icon, addon_icon)
    uri = construct_request({
            'func': 'samMain',
            'link':'http://urgantshow.ru/episodes'
            })
    xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
    '''
    listitem=xbmcgui.ListItem("Вечерний Ургант",addon_icon, addon_icon)
    uri = construct_request({
            'func': 'mainMain',
            'link':'http://www.1tv.ru/shows/vecherniy-urgant'
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
    

    '''
    xbmcplugin.endOfDirectory(handle=hos, succeeded=True, updateListing=False, cacheToDisc=True)

def tvcMain(params):
    link=params['link']
    #print link, params
    http = GET(link)
    if http == None: return False
    '''<a href="/channel/brand/id/2723/show/episodes/episode_id/47302/" class="b-image-wrap" data-url="http://www.tvc.ru/video/iframe/id/102606/id_stat/channel/?acc_video_id=/channel/brand/id/2723/show/episodes/episode_id/47302/">
        <img src="http://cdn.tvc.ru/pictures/tb/243/523.jpg" alt="&quot;Мука пшеничная&quot;">
                    <div class="video-ico"></div>
            </a>'''
    #print http
    lnks=re.compile('episodes__item\">[^\"]+\"([^\"<]+)\".+url=\"?(.+)\">[^<]*[^=]+=\"([^\"<]+)\"').findall(http)
    ttls=re.compile('class=\"b-brand-episode__anons\">[\s]+([^<]+)[\s^<]*<').findall(http)
    
        
    tt=[]
    
    for ttl in ttls:
        if "Анонс" not in ttl: tt.append(ttl)
    #print "tt=%s"%tt
    #ttls=tt    
    i=1
    #print len(lnks)
    #print len(ttls)
    for vid in lnks:
        #print vid
        img= vid[2]
        link=vid[0]
        flink=vid[1]
        title= ttls[i].replace("&quot;","")
        i=i+1
        #duration= vid.find('div', attrs={'class':'duration'}).string.encode('utf-8')
        #dur=int(duration.split(':')[0])*60+int(duration.split(':')[1])
        #/if dur>20: title='[COLOR=FF00FF00]%s[/COLOR]'%title
        listitem=xbmcgui.ListItem(title,img, img)
        uri = construct_request({
                'func': 'tvcsam',
                'link':link,
                'flink':flink,
                'title':title
                })
        listitem.setProperty('IsPlayable', 'true')
        if "Анонс" not in title: xbmcplugin.addDirectoryItem(hos, uri, listitem)
        
    nxt=re.compile('<li class=\"b-paging__item b-paging__next\">\s+<a\shref=\"([^\"<]+)\" title=\"(.+)\"></a').findall(http)
    if len(nxt)>0:
        nxntt=nxt[0][1]
        nxlnk="http://www.tvc.ru"+nxt[0][0]
        listitem=xbmcgui.ListItem("Еще",addon_icon, addon_icon)
        uri = construct_request({
                'func': 'tvcMain',
                'link':nxlnk
                })
        xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
    xbmcplugin.endOfDirectory(handle=hos, succeeded=True, updateListing=False, cacheToDisc=True)  

def tvcsam(params):
    #http://www.tvc.ru/video/iframe/id/101797/isPlay/true/id_stat/channel/?acc_video_id=/channel/brand/id/2723/show/episodes/episode_id/47027
    #print "%s: url=%s"%(params['title'],params['flink'])
    http=GET("http:"+params['flink'])

    #window.pl.data.dataUrl = 'http://www.tvc.ru/video/json/id/102174';
    lnk=re.compile('//www.tvc.ru/video/json/id/([0-9]+)').findall(http)
	
    #print lnk[0]
    jso=json.loads(GET('http://www.tvc.ru/video/json/id/'+lnk[0]))
    url="http:"+jso['path']['quality'][0]['url']
    item = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
  
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
    link= beautifulSoup.find('iframe',attrs={'allowfullscreen':'allowfullscreen'})['src']#.replace('/swf/','/video/')
    http1 = GET(link)
    #print link
    #print http1
    #" window.pl.data = {video:{"mp4":"https://cdnng-v.rtr-vesti.ru/_cdn_auth/secure/v/vh/mp4/hd-wide/001/545/021.mp4?auth=mh&vid=1545021","m3u8":"
    vid=re.findall('"m3u8":"(.+)"},picture',str(http1))[0].replace('\/','/')
    print GET(vid)
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
    #print ttl.encode('utf-8')
    #print link.encode('utf-8')
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
    mjson=json.loads(http)
    for  lind in mjson:
        linkA="http:"+ lind['mbr'][0]['src']
        img="http:"+ lind['poster']
        title=lind['title']
        listitem=xbmcgui.ListItem(title,img, img)
        #listitem.setInfo(type='video', infoLabels = mysetInfo)
        uri = construct_request({
            'func': 'mainScreen',
            'url':linkA
            })
        listitem.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(hos, uri, listitem)
    '''nxtpage = beautifulSoup.find('div',attrs={'class':'all_pages'})
    allstr=nxtpage.findAll('a')
    link=None
    for n in allstr:
        link=n['href']
    #print link
    listitem=xbmcgui.ListItem('Еще',img, img)
    uri = construct_request({
        'func': 'mainMain',
        'link':link
        })
    xbmcplugin.addDirectoryItem(hos, uri, listitem, True)'''
    xbmcplugin.endOfDirectory(handle=hos, succeeded=True, updateListing=False, cacheToDisc=True)
   
def mainScreen(params):
    link=params['url']
    
    
    item = xbmcgui.ListItem(path=link)
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

