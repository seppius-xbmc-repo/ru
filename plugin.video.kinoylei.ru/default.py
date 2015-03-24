#!/usr/bin/python
# -*- coding: utf-8 -*-


import urllib
import urllib2
import re
import sys
import os

import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmc



__addon__ = xbmcaddon.Addon( id = 'plugin.video.kinoylei.ru' )
__language__ = __addon__.getLocalizedString
sys.path.append( os.path.join( __addon__.getAddonInfo( 'path' ), 'resources', 'lib') )

addon_icon    = __addon__.getAddonInfo('icon')
addon_fanart  = __addon__.getAddonInfo('fanart')
addon_path    = __addon__.getAddonInfo('path')
addon_type    = __addon__.getAddonInfo('type')
addon_id      = __addon__.getAddonInfo('id')
addon_author  = __addon__.getAddonInfo('author')
addon_name    = __addon__.getAddonInfo('name')
addon_version = __addon__.getAddonInfo('version')

hos = int(sys.argv[1])
show_len=50


try:
    import simplejson as json
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

from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup

def construct_request(params):
    return '%s?%s' % (sys.argv[0], urllib.urlencode(params))


def showMessage(heading, message, times = 3000, pics = addon_icon):
    try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading.encode('utf-8'), message.encode('utf-8'), times, pics.encode('utf-8')))
    except Exception, e:
        xbmc.log( '[%s]: showMessage: Transcoding UTF-8 failed [%s]' % (addon_id, e), 2 )
        try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, pics))
        except Exception, e:
            xbmc.log( '[%s]: showMessage: exec failed [%s]' % (addon_id, e), 3 )



def GET(target, post=None):
    #print target
    #print post
    try:
        req = urllib2.Request(url = target, data = post)
        req.add_header('User-Agent', '	Mozilla/5.0 (Windows NT 6.1; rv:32.0) Gecko/20100101 Firefox/32.0')
        req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
        req.add_header('Accept-Language', 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3')
        req.add_header('Accept-Charset', 'utf-8')
        req.add_header('Referer',	'http://kinoylei.org/load/')
        resp = urllib2.urlopen(req)
        req.add_header('Content-Type','application/x-www-form-urlencoded')
        http = resp.read()

        return http
    except Exception, e:
        xbmc.log( '[%s]: GET EXCEPT [%s]' % (addon_id, e), 4 )
        showMessage('HTTP ERROR', e, 5000)

def mainScreen(params):

    addFolder('Премьеры',addon_icon,{'func': 'premiers'})
    addFolder('Поиск',addon_icon,{'func': 'doSearch'})

    http = GET('http://kinoylei.org')

    if http == None: return False
    
    beautifulSoup = BeautifulSoup(http)
    #genres=beautifulSoup.find('ul', attrs={'class':'clearfix'}).findAll('a')
    genres=beautifulSoup.find('div', attrs={'class':'bigblock filmcategory'}).findAll('a')
    for n in genres: 
        try: 
            title= n.string
            img=addon_icon
            addFolder(title,img,{'url': n['href'],'func': 'readgenre'})
        except: pass
    
    xbmcplugin.endOfDirectory(hos)

def premiers(params):

    http = GET('http://kinoylei.org')
    if http == None: return False
    beautifulSoup = BeautifulSoup(http)
    premiers=beautifulSoup.find('ul', attrs={'class':'clearfix'}).findAll('a')
    for n in premiers:
        txt=str(n)
        ou=re.findall('<a href="(.+?)"><img src="(.+?)" width="158" height="223" alt=.+<h3>(.+?)</h3></a>',txt)
        title=ou[0][2]
        href=ou[0][0]
        img=ou[0][1]
        addFolder(title,img,{'href': 'http://kinoylei.org%s'%href,'func': 'readmedia','img':img})
    xbmcplugin.endOfDirectory(hos)
    
def readgenre(params):
    host='http://kinoylei.org/'+params['url']
    #print host
    try:
        page=(params['page'])
    except:
        page=1
    if page==1:
        http = GET(host)
    else: 
        if params['url']=='board/0-1':
            nhost=host.split('-')[0]+'-'+host.split('-')[1]+'-'+str(page)
            
        else: nhost=host+'-'+str(page)+'-2'

        http = GET(nhost)
    
    
    if http == None: return False
    
    beautifulSoup = BeautifulSoup(http)
    content = beautifulSoup.findAll('div', attrs={'id': re.compile('entryID[0-9]+')})
    for n in content: 
        #try:
        txt=str(n)
        out=re.findall('<a class="film_link" href="(.+?)" title="(.+?)">',txt)
        href=out[0][0]
        title=out[0][1]
        out=re.findall('src="(.+?)"',txt)
        img= out[0]
        addFolder(title.replace('смотреть онлайн',''), img,{'href': href,'img':img,'func': 'readmedia'})
        #except: pass
    addFolder('Next',addon_icon,{'func': 'readgenre', 'page':int(int(page)+1),'url':params['url']})
    xbmcplugin.setContent(hos, 'movies')
    xbmcplugin.endOfDirectory(hos)
    
def addFolder(title,img,params):    
    listitem=xbmcgui.ListItem(title,iconImage = img, thumbnailImage = img)
    uri = construct_request(params)
    xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
    
def readmedia(params):
    print params['href']
    http=GET(params['href'])
    if http == None: return False
    #print http
    out=re.findall('<iframe class="myvideo" src="(.+?)">',http)
    #print out[0]
    http=GET(out[0])
    #print http
    #beautifulSoup = BeautifulSoup(str(http))
    #print beautifulSoup.prettify
    txt=http
    img=params['img']
    title=re.findall("comment: '(.+?)'",txt)
    ou1=re.findall('file:"(.+?)"}',txt)
    ou2=re.findall('pl."(.+?)",',txt)
    #print ou2
    if ou1:
        #print 'ou1'
        li = xbmcgui.ListItem(title[0], img, img)
        uri = construct_request({
            'href': ou1[0],
            'func': 'play'
        })
        li.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(hos, uri, li)
    if ou2:
        #print 'ou2;'
        http=GET(ou2[0])[3::]
        #print http
        
        flist=json.loads(http)
        for file in flist['playlist']:
            try:
                li = xbmcgui.ListItem(file['comment'], img, img)
                uri = construct_request({'href': file['file'],'func': 'play'})
                li.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(hos, uri, li)
            except: 
                try:
                    li = xbmcgui.ListItem(file['comment'], img, img)
                    uri = construct_request({})
                    xbmcplugin.addDirectoryItem(hos, uri, li)
                    for file2 in file['playlist']:
                        li = xbmcgui.ListItem(file2['comment'], img, img)
                        uri = construct_request({'href': file2['file'],'func': 'play'})
                        li.setProperty('IsPlayable', 'true')
                        xbmcplugin.addDirectoryItem(hos, uri, li)
                except: pass
    xbmcplugin.endOfDirectory(hos)
    
    
def play(params):
    params['href']=params['href'].split('",')[0]
    q=__addon__.getSetting('qual')
    if q=='0': 
        i = xbmcgui.ListItem(path = params['href'])
    else: 
        i = xbmcgui.ListItem(path = params['href'].replace('.mp4','.flv'))
    xbmcplugin.setResolvedUrl(hos, True, i)
    
def doSearch(params):
    
    kbd = xbmc.Keyboard()
    kbd.setDefault('')
    kbd.setHeading('Поиск')
    kbd.doModal()
    if kbd.isConfirmed():
        sts=kbd.getText();

	post={}
    
    
    
    
    
    post['sfSbm']="Искать фильм"
    post['query']=sts
    post['a']='2'
    http=GET('http://kinoylei.org/load/',urllib.urlencode(post))
    beautifulSoup = BeautifulSoup(http)
    #print beautifulSoup.prettify()
    content = beautifulSoup.findAll('div', attrs={'id': re.compile('entryID[0-9]+')})
    for n in content: 
        txt=str(n)
        out=re.findall('<a href="(.+?)" title="(.+?)">',txt)
        href=out[0][0]
        title=out[0][1]
        #<img class="material_img" alt="" src="(.+)" align="center" border="0" />
        out=re.findall('<img class="material_img" alt="" src="(.+)" align="center" border="0" />',txt)
        img= out[0]
        li = xbmcgui.ListItem(title, img, img)
            #li.setInfo(type='video', infoLabels = {'plot':desk,'plotoutline':desk})
        uri = construct_request({
            'href': href,
            'img':img,
            'func': 'readmedia'
        })
        xbmcplugin.addDirectoryItem(hos, uri, li, True)
    
    xbmcplugin.setContent(hos, 'movies')
    xbmcplugin.endOfDirectory(hos)
    
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
