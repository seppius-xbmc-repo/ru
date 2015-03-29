#!/usr/bin/python
# -*- coding: utf-8 -*-


import urllib2
import urllib
import simplejson as json
import xbmcgui
import xbmcplugin
import xbmcaddon
import re,base64,random,time
import json
import array

from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
from urllib import unquote, quote, quote_plus
Addon = xbmcaddon.Addon( id = 'plugin.video.hdkinoteatr.com' )
__language__ = Addon.getLocalizedString

addon_icon    = Addon.getAddonInfo('icon')
addon_fanart  = Addon.getAddonInfo('fanart')
addon_path    = Addon.getAddonInfo('path')
addon_type    = Addon.getAddonInfo('type')
addon_id      = Addon.getAddonInfo('id')
addon_author  = Addon.getAddonInfo('author')
addon_name    = Addon.getAddonInfo('name')
addon_version = Addon.getAddonInfo('version')

VERSION = '1.0'
DOMAIN = '131896016'
GATrack= 'UA-46039715-1' #'UA-30985824-2'
try:
    import platform
    xbmcver=xbmc.getInfoLabel( "System.BuildVersion" ).replace(' ','_').replace(':','_')
    UA = 'XBMC/%s (%s; U; %s %s %s %s) %s/%s XBMC/%s'% (xbmcver,platform.system(),platform.system(),platform.release(), platform.version(), platform.machine(),addon_id,addon_version,xbmcver)
except:
    UA = 'XBMC/Unknown %s/%s/%s' % (urllib.quote_plus(addon_author), addon_version, urllib.quote_plus(addon_name))
hos = int(sys.argv[1])
headers  = {
    'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)',
    'Accept'     :' text/html, application/xml, application/xhtml+xml, image/png, image/jpeg, image/gif, image/x-xbitmap, */*',
    'Accept-Language':'ru-RU,ru;q=0.9,en;q=0.8',
    'Accept-Charset' :'utf-8, utf-16, *;q=0.1',
    'Accept-Encoding':'identity, *;q=0'
}


def GET(target, post=None):
    #print target
    #print post
    try:
        req = urllib2.Request(url = target, data = post)
        req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
        #req.add_header('Host',	'online.stepashka.com')
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
    
def showMessage(heading, message, times = 3000, pics = addon_icon):
    try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading.encode('utf-8'), message.encode('utf-8'), times, pics.encode('utf-8')))
    except Exception, e:
        xbmc.log( '[%s]: showMessage: Transcoding UTF-8 failed [%s]' % (addon_id, e), 2 )
        try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, pics))
        except Exception, e:
            xbmc.log( '[%s]: showMessage: exec failed [%s]' % (addon_id, e), 3 )
def doSearch(params):
    kbd = xbmc.Keyboard()
    kbd.setDefault('')
    kbd.setHeading("Поиск")
    kbd.doModal()
    out=''
    if kbd.isConfirmed():
        try:
            out = trans.detranslify(kbd.getText())
            out=str(out.encode("utf-8"))
        except:
            out = str(kbd.getText())
    
    par={}
    par['url']='http://www.hdkinoteatr.com/index.php?do=search'
    par['post']='dosearch=search&subaction=search&result_from=1&full_search=0&story=%s'%out
    GetSearch(par)
    
def GetSearch(params):
    try: search_start=(params['search_start'])
    except: search_start=1

    http=GET(params['url']+'&search_start='+str(search_start),params['post'])
    #print params['url']+'&search_start='+str(search_start)
    #href="(.+?)".+<span>(.+?)</span
    beautifulSoup = BeautifulSoup(http)
    #print str(beautifulSoup)
    content = beautifulSoup.findAll('div', attrs={'class': 'base shortstory'})
    for n in content:
        m= re.search('a href="(http://.+?)"',str(n))
        gg=re.findall('<div id="news-id[^.]+script(.+?)</',str(n))
        try: desk= gg[0][0]
        except: desk='Нет описания'
        url= m.group(1)
        p = re.compile( 'title="(.+?)"' )
        _p = re.findall('<h3 class="btl">([^\b]+)</h3>',str(n))
	#print str(_p)
        m = re.findall('<a[^\b]+>(.+?)?<span class="hilight">(.+?)</span>(.+?)</a>',str(_p[0]))
	if (m):
 	    title= m[0][0]+' '+m[0][1]+m[0][2]
	else:
	    m = re.findall('<a[^\b]+>(.+?)</a>',str(_p[0]))
	    #print str(m)
	    title= m[0]
        m= re.findall('img src="(.+?)"',str(n))
        pic= 'http://www.hdkinoteatr.com/'+m[0]#m[1]
        #title=title.replace(' смотреть онлайн в хорошем качестве HD 720p бесплатно','')
        listitem=xbmcgui.ListItem(title,iconImage = addon_icon, thumbnailImage = pic)
        listitem.setInfo(type='video', infoLabels = {'plot':desk,'plotoutline':desk})
        uri = construct_request({
            'func': 'get_movies',
            'url':url,
            'title':title,
            'img':pic
            })
        #listitem.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(hos, uri, listitem,True)

    listitem=xbmcgui.ListItem('Next',iconImage = addon_icon, thumbnailImage = addon_icon)
    uri = construct_request({
                'func': 'GetSearch',
                'search_start':int(int(search_start)+1),
                'url':params['url'],
		'post':params['post']
                })
    xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
    xbmcplugin.setContent(hos, 'movies')
    xbmcplugin.endOfDirectory(handle=hos, succeeded=True, updateListing=False, cacheToDisc=True)

    #m= re.findall('onclick="favor((.+?),(.+?),(.+?))"',str(beautifulSoup).replace("'",''))

    #for n in m: 
    #    url= n[2].split('"')[0]
    #    img= n[3][0:len(n[3])-1]
    #    listitem=xbmcgui.ListItem(n[1][1:len(n[1])].replace('<b>','').replace('</b>','').replace('смотреть онлайн',''),iconImage = img, thumbnailImage = img)
    #    uri = construct_request({
    #        'func': 'get_movies',
    #        'url':url,
    #        'title':n[1].replace('<b>','').replace('</b>',''),
    #        'img':None
    #        })
    #    listitem.setProperty('IsPlayable', 'true')
    #    xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
    #xbmcplugin.endOfDirectory(handle=hos, succeeded=True, updateListing=False, cacheToDisc=True)
def run_settings(params):
    Addon.openSettings()

def mainMain(params):
    http = GET('http://www.hdkinoteatr.com/')
    if http == None: return False
    listitem=xbmcgui.ListItem('[COLOR FFFFFF00]Поиск[/COLOR]',iconImage = addon_icon, thumbnailImage = addon_icon)
    uri = construct_request({
        'func': 'doSearch'
        })
    xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
    beautifulSoup = BeautifulSoup(http)
    content = beautifulSoup.find('ul',attrs={'class':'cats'})
    content=content.findAll('li')
    listitem=xbmcgui.ListItem('[COLOR FF00FF00]Главная[/COLOR]',iconImage = addon_icon, thumbnailImage = addon_icon)
    uri = construct_request({
        'func': 'mainScreen',
        'url':'http://www.hdkinoteatr.com/'
        })
    xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
    listitem=xbmcgui.ListItem('[COLOR FFFFFF00]Top[/COLOR]',iconImage = addon_icon, thumbnailImage = addon_icon)
    uri = construct_request({
        'func': 'top100',
        'url':'top'
        })
    xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
    b = False
    for num in content:	
	title=num.find('a').string
        url=num.find('a')['href']
        listitem=xbmcgui.ListItem(title,iconImage = addon_icon, thumbnailImage = addon_icon)
        uri = construct_request({
            'func': 'mainScreen',
            'url': 'http://www.hdkinoteatr.com'+url
            })
	b = True
	xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
    xbmcplugin.endOfDirectory(handle=hos, succeeded=True, updateListing=False, cacheToDisc=True)

def top100(params):
    host='http://www.hdkinoteatr.com/top/'
    http = GET(host)
    beautifulSoup = BeautifulSoup(http)
    content = beautifulSoup.findAll('td')
#    content = content.findAll('td')
    for n in content:
        try:
	    txt=str(n)
            tt=re.findall('<a href="(.+?)">(.+?)</a>',txt)
            url=tt[0][0]
            title=tt[0][1]
            desk=''#re.findall('<font size="1">(.+?)<hr /><font color="#ff9900">',txt)[0]
            pic=''#re.findall('<img src="(.+?)" vspace="0" width="120" align="left" border="0" hspace="0" />',txt)[0]
            listitem=xbmcgui.ListItem(title,iconImage = addon_icon, thumbnailImage = pic)
            listitem.setInfo(type='video', infoLabels = {'plot':desk,'plotoutline':desk})
	   # print url
            uri = construct_request({
                'func': 'get_movies',
                'url': url,
                'title': title,
                'img': pic
                })
   # xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
   # xbmcplugin.setContent(hos, 'movies')
   # xbmcplugin.endOfDirectory(handle=hos, succeeded=True, updateListing=False, cacheToDisc=True)

    	    xbmcplugin.addDirectoryItem(hos, uri, listitem,True)
        except: pass
    xbmcplugin.setContent(hos, 'movies')
    xbmcplugin.endOfDirectory(handle=hos, succeeded=True, updateListing=False, cacheToDisc=True)

def mainScreen(params):
    host=params['url'].strip()
    try:
        page=(params['page'])
    except:
        page=1
    if page==1:
        http = GET(host)
    else: 
        nhost=params['url'].strip()+'/page/'+str(page)+'/'
	#print nhost
        http = GET(nhost)
    
    if http == None: return False
    
    beautifulSoup = BeautifulSoup(http)
    #print beautifulSoup
    #<table width="100%" cellspacing="1" cellpadding="1" border="0" style="padding-bottom: 1px;">
    content = beautifulSoup.findAll('div', attrs={'class': 'base shortstory'})
    for n in content: 
        m= re.search('a href="(http://.+?)"',str(n))
        gg=re.findall('<div id="news-id[^.]+script(.+?)</',str(n))
        try: desk= gg[0][0]
        except: desk='Нет описания'
        url= m.group(1)
        p = re.compile( 'title="(.+?)"' )
	_p = re.findall('<h2 class="btl">([^\b]+)</h2>',str(n))
        m = re.findall('<a[^\b]+>(.+?)</a>',str(_p[0]))
        title= m[0]#m[1]
        m= re.findall('img src="(.+?)"',str(n))
        pic= 'http://www.hdkinoteatr.com/'+m[0]#m[1]
        #title=title.replace(' смотреть онлайн в хорошем качестве HD 720p бесплатно','')
        listitem=xbmcgui.ListItem(title,iconImage = addon_icon, thumbnailImage = pic)
        listitem.setInfo(type='video', infoLabels = {'plot':desk,'plotoutline':desk})
        uri = construct_request({
            'func': 'get_movies',
            'url':url,
            'title':title,
            'img':pic
            })
        #listitem.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(hos, uri, listitem,True)
    
    listitem=xbmcgui.ListItem('[COLOR FF00FF00][ДАЛЕЕ '+str(int(int(page)+1))+'][/COLOR]',iconImage = addon_icon, thumbnailImage = addon_icon)
    uri = construct_request({
                'func': 'mainScreen',
                'page':int(int(page)+1),
                'url':params['url']
                })
    xbmcplugin.addDirectoryItem(hos, uri, listitem, True)
    xbmcplugin.setContent(hos, 'movies')
    xbmcplugin.endOfDirectory(handle=hos, succeeded=True, updateListing=False, cacheToDisc=True)

from urllib import unquote, quote, quote_plus
    
    
def get_movies(params):
    http=GET(params['url'])
    #print params['url']
    beautifulSoup = BeautifulSoup(http)
    
    t=re.findall('<h1 class="btl">(.+?)<span',str(beautifulSoup))
    if not t:
       t=re.findall('<h1 class="btl">(.+?)</h1>',str(beautifulSoup))
    _m=re.findall('<div id="vid">[^\b]+',str(beautifulSoup))
    m=re.findall('makePlayer\(\'(.+?)\'\)',str(_m[0]))
    
    if m:
	m[0] = [t[0],m[0]]

    if not m:
	_k = re.findall('vkArr=(.+)\;',_m[0])
	_h = json.loads(_k[0])
	print str(_h)
	m = []
	for _p in _h:
	  if 'playlist' in _p: #_p['playlist']:
	     for _u in _p['playlist']:
	       m.append([_u['comment'].replace('&lt;br&gt;',' '),_u['file']]) 
	  else:
	      m.append([t[0].decode('utf-8')+' ['+_p['comment']+']',_p['file']])
    #print str(m)
    if m:
      for w in m:
	#g = re.findall('(^oid=)',m[0])
	#print str(w)
	if re.findall('(^oid=)', w[1]):
          url = w[1].replace('amp;','').replace(';','')
	  #print url
	  g = re.findall('code=code.replace\(\/(\(oid=.+)\/g,(.+)\).replace\(\/(.+)\/g,',_m[0])
	  g1 = g[0][0].replace('&amp;','&')+'([0-9a-z]+)'
	  g2 = g[0][2].replace('&amp;','&')+'([0-9a-z&=]+)'
	  #r = re.findall('(oid=[0-9a-z-]+&id=)([0-9]{2})([0-9]{2})([0-9]+&hash=)([0-9a-z]{3})([0-9a-z]{3})([0-9a-z]+)',url)
	  #print g1
	  r = re.findall(g1,url)
	  #print str(r)
	  url = r[0][0]+r[0][2]+r[0][1]+r[0][3]+r[0][5]+r[0][4]+r[0][6]
	  #print '[=== '+url
	  #r = re.findall('(oid=[0-9-]{1})([0-9]{2})([0-9]{2})([0-9a-z&=]+)',url)
	  r = re.findall(g2,url)
	  url = r[0][0]+r[0][2]+r[0][1]+r[0][3]
	  url = 'http://vk.com/video_ext.php?'+url.replace('amp;','')
	  #print '[=== '+url


 	  http=GET(url)
    	  soup = BeautifulSoup(http, fromEncoding="windows-1251")
	  #print soup
	  g = None
	  g = re.findall('url([0-9]+)\"',str(soup))
	  hd = 3
	  g.reverse()
    	  for rec in g:
	    #print str(rec)
	    if (str(rec) == '240'): hd = 6
	    elif (str(rec) == '360'): hd = 1
	    elif (str(rec) == '480'): hd = 2
	    elif (str(rec) == '720'): hd = 3
	    #print '================+'+str(hd)
  	    title = str(rec)+'p '+w[0]
	    if hd == 3: title = '[COLOR FF00FF00]'+ str(rec)+'p '+w[0]+'[/COLOR]'
	    listitem=xbmcgui.ListItem(title,iconImage = addon_icon)#, thumbnailImage = params['img'])
            uri = construct_request({
              'func': 'get_movie',
              'url': url+'&hd='+str(hd)
            })
	    print url+'&hd='+str(hd)
            listitem.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(hos, uri, listitem)

	  '''listitem=xbmcgui.ListItem('в HD 720p',iconImage = addon_icon)#, thumbnailImage = params['img'])
          uri = construct_request({
            'func': 'get_movie',
            'url': url+'&hd=3'
            })
          listitem.setProperty('IsPlayable', 'true')
          xbmcplugin.addDirectoryItem(hos, uri, listitem)
 
	  listitem=xbmcgui.ListItem('в 480p',iconImage = addon_icon)#, thumbnailImage = params['img'])
          uri = construct_request({
            'func': 'get_movie',
            'url': url+'&hd=2'
            })'''

 	  '''uri = construct_request({
                'func': 'get_movie',
                'url':url.replace('amp;','')
                })'''

          #listitem.setProperty('IsPlayable', 'true')
          #xbmcplugin.addDirectoryItem(hos, uri, listitem)
	  '''print url
	elif re.findall('(kset.kz)',w[1]):
	  print 22222222222222
	elif re.findall('<(object|embed)',w[1]):
          print 3333333333333
        elif re.findall('.(3gp|aac|f4v|flv|m4a|mp3|mp4)',w[1]):
	  print 4444444444444	
        elif re.findall('(video\.rutube\.ru)',w[1]):
	  print 555555555555
	else:
          print 555555555555'''

    #if not m: 

     #   m= re.findall('iframe src="(.+?)"',str(beautifulSoup))
     #   for n in m:
     #       listitem=xbmcgui.ListItem(params['title'].replace('смотреть онлайн',''),iconImage = addon_icon, thumbnailImage = params['img'])
     #       uri = construct_request({
     #           'func': 'get_movie',
     #           'url':n.replace('amp;','')
     #           })
     #       listitem.setProperty('IsPlayable', 'true')
     #       xbmcplugin.addDirectoryItem(hos, uri, listitem)
        
    xbmcplugin.endOfDirectory(handle=hos, succeeded=True, updateListing=False, cacheToDisc=True)
def get_movie(params):
    http=GET(params['url'])
    soup = BeautifulSoup(http, fromEncoding="windows-1251")
    av=0
    for rec in soup.findAll('param', {'name':'flashvars'}):
        #print rec
        for s in rec['value'].split('&'):
            if s.split('=',1)[0] == 'uid':
                uid = s.split('=',1)[1]
            if s.split('=',1)[0] == 'vtag':
                vtag = s.split('=',1)[1]
            if s.split('=',1)[0] == 'host':
                host = s.split('=',1)[1]
            if s.split('=',1)[0] == 'vid':
                vid = s.split('=',1)[1]
            if s.split('=',1)[0] == 'oid':
                oid = s.split('=',1)[1]
            if s.split('=',1)[0] == 'hd':
                hd = s.split('=',1)[1]
        host=host.replace('vk.me','vk.com')
        video = host+'u'+uid+'/videos/'+vtag+'.360.mp4'
        if int(hd)==3:
            video = host+'u'+uid+'/videos/'+vtag+'.720.mp4'
        if int(hd)==2:
            video = host+'u'+uid+'/videos/'+vtag+'.480.mp4'
        if int(hd)==1:
            video = host+'u'+uid+'/videos/'+vtag+'.360.mp4'
        #print video
        item = xbmcgui.ListItem(path=video)
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

            
    
def getinfo(param):
    info={}
    for infostring in param:
        try:
            m=re.search('[^<>]+<',str(infostring))
            comm = str( m.group(0)[:-1])
            m=re.search('[^<>]+</a',str(infostring))
            data = str( m.group(0)[:-3])
            #print "%s:%s"%(comm,data)
            if comm=="Год: ": info['year']=int(data)
            if comm=="Жанр: ": info['genre']=data
            if comm=="Режиссер: ": info['director']=data
            if comm=="Автор оригинала: ": info['writer']=data
        except: pass
    #print info
    return info

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
    mainMain(params)
if func != None:
    try: pfunc = globals()[func]
    except:
        pfunc = None
        xbmc.log( '[%s]: Function "%s" not found' % (addon_id, func), 4 )
        showMessage('Internal addon error', 'Function "%s" not found' % func, 2000)
    if pfunc: pfunc(params)

