#!/usr/bin/python
# -*- coding: utf-8 -*-
# Writer (c) 2013, Silhouette, E-mail: 
# Rev. 0.5.2


import urllib,urllib2,re,sys
import xbmcplugin,xbmcgui,xbmcaddon
from BeautifulSoup import BeautifulSoup

try:
  # Import UnifiedSearch
  sys.path.append(os.path.dirname(__file__)+ '/../plugin.video.unified.search')
  from unified_search import UnifiedSearch
except: pass

__settings__ = xbmcaddon.Addon(id='plugin.video.kinoxa-x.ru')
use_translit = __settings__.getSetting('translit')

try:  
  import Translit as translit
  translit = translit.Translit()  
except: use_translit = 'false'



dbg = 0

pluginhandle = int(sys.argv[1])

start_pg = "http://www.kinoxa-x.ru"
#page_pg = start_pg + "/load/0-"
page_pg = start_pg + "/page/"
# fdpg_pg = ";t=0;md=;p="
# find_pg = start_pg + "/search/?q="
find_pg = start_pg + "/index.php?do=search"
find_dt = "do=search&subaction=search&search_start="
# find_str = "&full_search=0&result_from=25&story="
find_str = "&full_search=0&story="
# do=search&subaction=search&search_start=3&full_search=0&result_from=25&story=mama
# do=search&subaction=search&story=test&sfSbm=&a=2

def gettranslit(msg):
    if use_translit == 'true': 
        try: return translit.rus(msg)
        except: return msg
    else: return msg
    

def dbg_log(line):
    if dbg: print line

def get_url(url, data = None, cookie = None, save_cookie = False, referrer = None):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Opera/9.80 (X11; Linux i686; U; ru) Presto/2.7.62 Version/11.00')
    req.add_header('Accept', 'text/html, application/xml, application/xhtml+xml, */*')
    req.add_header('Accept-Language', 'ru,en;q=0.9')
    if cookie: req.add_header('Cookie', cookie)
    if referrer: req.add_header('Referer', referrer)
    if data: 
        response = urllib2.urlopen(req, data,timeout=30)
    else:
        response = urllib2.urlopen(req,timeout=30)
    link=response.read()
    if save_cookie:
        setcookie = response.info().get('Set-Cookie', None)
        if setcookie:
            setcookie = re.search('([^=]+=[^=;]+)', setcookie).group(1)
            link = link + '<cookie>' + setcookie + '</cookie>'
    
    response.close()
    return link

def KNX_list(url, page, type, fdata):
    dbg_log('-KNX_list:' + '\n')
    dbg_log('- url:'+  url + '\n')
    dbg_log('- page:'+  page + '\n')
    dbg_log('- type:'+  type + '\n')
    dbg_log('- fdata:'+  fdata + '\n')
    
    if type == 'ctlg':
        n_url = url + 'page/' + page + '/'
        pdata = ''
    elif fdata != '':
        n_url = url
        pdata = find_dt + page + find_str + fdata
    else:
        n_url = url + page + '/'
        pdata = ''

                
        
    dbg_log('- n_url:'+  n_url + '\n')
    dbg_log('- pdata:'+  pdata + '\n')
    
    if type != 'unis':
        xbmcplugin.setContent(int(sys.argv[1]), 'episodes')#movies episodes tvshows
    
#     try:
    http = get_url(n_url, data=pdata)
#     except:
#         return
    
    i = 0
    
    
    if type == '':
        ext_ls = [('<КАТАЛОГ>', '?mode=ctlg'),
                  ('<ПОИСК>', '?mode=find')]
        for ctTitle, ctMode  in ext_ls:
            item = xbmcgui.ListItem(ctTitle)
            uri = sys.argv[0] + ctMode
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  
            dbg_log('- uri:'+  uri + '\n')    


        
    entrys = BeautifulSoup(http).findAll('div',{"class":"eTitle"})
    msgs = BeautifulSoup(http).findAll('div',{"class":"eMessage"}) 

    for eid in entrys:

#             print eid
#             print msgs[i]

            href = re.compile('<a href="(.*?)">').findall(str(eid))[0]
            try:
                plot = re.compile('<span class="nazvanie">(.*?)</div>').findall(re.sub('[\n\r\t]', ' ',str(msgs[i])))[0]
                plot = plot.replace('</span>','').replace('</a>','')
                plot = re.sub('<a href=".*?">','',plot)
            except:
                plot = ''
            try:
                img = start_pg + re.compile('<img.*?src="(.*?)"').findall(str(msgs[i]))[0]
            except:
                img = ''
            try:
                title = re.compile('<div class="title-short">(.*?)</div>').findall(str(eid))[0]
            except:
                title = re.compile('<a href=".*?">(.*?)</a>').findall(str(eid))[0]
                


            dbg_log('-HREF %s'%href)
            dbg_log('-TITLE %s'%title)
            dbg_log('-IMG %s'%img)
            dbg_log('-PLOT %s'%plot)

            if type != 'unis':
                item = xbmcgui.ListItem(title, iconImage=img, thumbnailImage=img)
                item.setInfo( type='video', infoLabels={'title': title, 'plot': plot})
                uri = sys.argv[0] + '?mode=play' \
                + '&url=' + urllib.quote_plus(href)
                item.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(pluginhandle, uri, item, False)  
                dbg_log('- uri:'+  uri + '\n')
                i = i + 1
            else:
              try:
                unis_res.append({'title':  title, 'url': href, 'image': img, 'plugin': 'plugin.video.kinoxa-x.ru'})
              except: pass

    if type == 'unis':
      try: UnifiedSearch().collect(unis_res)
      except:  pass
    else:
      if i :
          item = xbmcgui.ListItem('<NEXT PAGE>')
          uri = sys.argv[0] + '?page=' + str(int(page) + 1) + '&url=' + urllib.quote_plus(url) + '&type=' + type + '&find=' + urllib.quote_plus(fdata)
          xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
          dbg_log('- uri:'+  uri + '\n')
          if type != 'find':
              item = xbmcgui.ListItem('<NEXT PAGE +5>')
              uri = sys.argv[0] + '?page=' + str(int(page) + 5) + '&url=' + urllib.quote_plus(url) + '&type=' + type + '&find=' + urllib.quote_plus(fdata)
              xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
              dbg_log('- uri:'+  uri + '\n')        
     
      xbmcplugin.endOfDirectory(pluginhandle) 


def KNX_show(url):
    dbg_log('-KNX_show:' + '\n')
    dbg_log('- url:'+  url + '\n')
    
    item = xbmcgui.ListItem('Play Video')
    uri = sys.argv[0] + '?mode=play&url=' + urllib.quote_plus(url)
    item.setProperty('IsPlayable', 'true')
    xbmcplugin.addDirectoryItem(pluginhandle, uri, item, False)  
    dbg_log('- uri:'+  uri + '\n')    
    xbmcplugin.endOfDirectory(pluginhandle) 

def KNX_list2(url, page):
    dbg_log('-KNX_list:' + '\n')
    dbg_log('- url:'+  url + '\n')
    dbg_log('- page:'+  page + '\n')


    n_url = url + page
        
    dbg_log('- n_url:'+  n_url + '\n')
    
    xbmcplugin.setContent(int(sys.argv[1]), 'episodes')#movies episodes tvshows
    
    http = get_url(n_url)
    i = 0
    
    entrys = BeautifulSoup(http).findAll('div',{"class":"eTitle"})
    msgs = BeautifulSoup(http).findAll('div',{"class":"eMessage"})

    for eid in entrys:

        films = re.compile('<a href="(.*?)">(.*?)</a>').findall(str(eid))
        plots = re.compile('style=".*?">(.*?)</div>').findall(re.sub('[\n\r\t]', ' ',str(msgs[i])))
        
        for href, title in films:
            img = ''
            title = re.sub('<.*?>', '',title)
            try: plot = re.sub('<.*?>', '',plots[0])
            except: plot = title
            dbg_log('-TITLE %s'%title)
            dbg_log('-PLOT %s'%plot)

            item = xbmcgui.ListItem(title, iconImage=img, thumbnailImage=img)
            item.setInfo( type='video', infoLabels={'title': title, 'plot': plot})
            uri = sys.argv[0] + '?mode=play' \
            + '&url=' + urllib.quote_plus(href)
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, False)  
            dbg_log('- uri:'+  uri + '\n')
            i = i + 1
                
    if i:
        item = xbmcgui.ListItem('<NEXT PAGE>')
        uri = sys.argv[0] + '?mode=list&page=' + str(int(page) + 1) + '&url=' + urllib.quote_plus(url)
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
        dbg_log('- uri:'+  uri + '\n')
      
 
    xbmcplugin.endOfDirectory(pluginhandle) 
    
def KNX_play(url):     
    dbg_log('-NKN_play:'+ '\n')
    dbg_log('- url:'+  url + '\n')
    
    http = get_url(url)
#    print http
    iframes = re.compile('<iframe itemprop="video" src="(.*?)"').findall(http)
    
#    print iframes
    
    if len(iframes) > 0:
        http = get_url(iframes[0])
#    elif len(iframes):
#        http = get_url(iframes[0])
    else:
        return
        
#    print http
    
    flvs = re.compile('src="http(.*?)"').findall(http)
    hrefs = re.compile('<a href="(.*?)">').findall(http)
#    print flvs
#    print hrefs
    
    if len(flvs) > 1:
        item = xbmcgui.ListItem(path = "http" + flvs[1])
        xbmcplugin.setResolvedUrl(pluginhandle, True, item)
    elif len(flvs):
        item = xbmcgui.ListItem(path = "http" + flvs[0])
        xbmcplugin.setResolvedUrl(pluginhandle, True, item)
    elif len(hrefs):
        item = xbmcgui.ListItem(path = hrefs[0])
        xbmcplugin.setResolvedUrl(pluginhandle, True, item)

def KNX_ctlg(url):
    dbg_log('-KNX_ctlg:' + '\n')
    dbg_log('- url:'+  url + '\n')
               
    catalog  = [( "/filmy_2015_goda/", '2015 год'),
                ( "/filmy_2014_goda/", '2014 год'),
                ( "/filmy_2013_goda/", '2013 год'),
                ( "/filmy_2012_goda/", '2012 год'),
                ( "/filmy_2011_goda/", '2011 год'),
                ( "/filmy_2010_goda/", '2010 год'),
                ( "/filmy_2009_goda/", '2009 год'),
                ( "/komedii/", 'Комедии'),
                ( "/boeviki/", 'Боевики'),
                ( "/dramy/", 'Драмы'),
                ( "/uzhasy/", 'Ужасы'),
                ( "/fantastika/", 'Фантастика'),
                ( "/trillery/", 'Триллеры'),
                ( "/detektivy/", 'Детективы'),
                ( "/dokumentalnye/", 'Документальные'),
                ( "/multfilmy/", 'Мультфильмы'),
                ( "/mistika/", 'Мистика'),
                ( "/sovetskie_filmy/", 'Советские фильмы'),
                ( "/semejnye/", 'Семейные'),
                ( "/sportivnye/", 'Спортивные'),
                ( "/melodramy/", 'Мелодрамы'),
                ( "/russkie_melodramy/", 'Русские Мелодрамы'),
                ( "/russkie_filmy/", 'Русские фильмы'),
                ( "/russkie_serialy/", 'Русские сериалы'),
                ( "/zarubezhnye_serialy/", 'Зарубежные сериалы'),
                ( "/trejlery/", 'Трейлеры'),
                ( "/fehntezi/", 'Фэнтези'),
                ( "/prikljuchenija/", 'Приключения'),
                ( "/istoricheskie/", 'Исторические'),
                ( "/vestern/", 'Вестерн'),#         stxt = uni2enc(gettranslit(kbd.getText()))
                ( "/animeh/", 'Аниме'),
                ( "/kriminal/", 'Криминал'),
                ( "/voennye/", 'Военные'),
                ( "/goblinskij_perevod/", 'Гоблинский перевод'),
                ( "/poznaem_mir/", 'Познаем мир'),
                ( "/biografija/", 'Биография'),
                ( "/xxx/", 'XXX'),
                ( "/jumoristicheskie_peredachi/", 'Юмористические передачи'),
                ( "/teleshou/", 'Передачи'),
                ( "/filmy_v_vysokom_kachestve_hd/", 'В высоком качестве HD'),
                ( "/novinki_kino/", 'Новинки кино')]
               
               
    for ctLink, ctTitle  in catalog:
        item = xbmcgui.ListItem(ctTitle)
        uri = sys.argv[0] \
        + '?url=' + urllib.quote_plus(start_pg + ctLink) + '&type=ctlg&page=1'
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  
        dbg_log('- uri:'+  uri + '\n')
        
    xbmcplugin.endOfDirectory(pluginhandle)

def uni2enc(ustr):
    raw = ''
    uni = unicode(ustr, 'utf8')
    uni_sz = len(uni)
    for i in xrange(len(ustr)):
        raw += ('%%%02X') % ord(ustr[i])        
    return raw
    
def uni2cp(ustr):
    raw = ''
    uni = unicode(ustr, 'utf8')
    uni_sz = len(uni)
    for i in range(uni_sz):
        raw += ('%%%02X') % ord(uni[i].encode('cp1251'))
    return raw  
        
def KNX_find():     
    dbg_log('-KNX_find:'+ '\n')
    
    kbd = xbmc.Keyboard()
    kbd.setHeading('ПОИСК')
    kbd.doModal()
    if kbd.isConfirmed():
        stxt = uni2cp(gettranslit(kbd.getText()))
#         stxt = kbd.getText()
#         furl = find_pg + stxt + fdpg_pg
        furl = find_pg
        dbg_log('- furl:'+  furl + '\n')
        KNX_list(furl, '1', 'find', stxt)

def lsChan():
    xbmcplugin.endOfDirectory(pluginhandle)

def get_params():
    param=[]
    #print sys.argv[2]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
        params=sys.argv[2]
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

params=get_params()


type = ''
mode = ''
url = ''
find = ''

try:
    mode=params['mode']
    dbg_log('-MODE:'+ mode + '\n')
except: pass
try: 
    url=urllib.unquote_plus(params['url'])
    dbg_log('-URL:'+ url + '\n')
except: pass  
try: 
    page=urllib.unquote_plus(params['page'])
    dbg_log('-PAGE:'+ page + '\n')
except: page = '1'
try: 
    type=urllib.unquote_plus(params['type'])
    dbg_log('-TYPE:'+ type + '\n')
except: pass
try: 
    find=urllib.unquote_plus(params['find'])
    dbg_log('-FIND:'+ find + '\n')
except: pass

keyword = params['keyword'] if 'keyword' in params else None
unified = params['unified'] if 'unified' in params else None

if url=='':
    url = page_pg

if mode == '': KNX_list(url, page, type, find)
elif mode == 'ctlg': KNX_ctlg(url)
elif mode == 'play': KNX_play(url)
elif mode == 'find': KNX_find()
elif mode == 'show': KNX_show(url)
elif mode == 'search': 
    url = find_pg
    KNX_list(url, '1', 'unis', uni2cp(gettranslit(keyword)))
    
#elif mode == 'list': KNX_list(url, page)


