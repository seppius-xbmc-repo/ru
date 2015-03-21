#!/usr/bin/python
# -*- coding: utf-8 -*-
# Writer (c) 2012, Silhouette, E-mail: 
# Rev. 0.7.4


import urllib,urllib2,re,sys
import xbmcplugin,xbmcgui,xbmcaddon
from BeautifulSoup import BeautifulSoup


try:
  # Import UnifiedSearch
  sys.path.append(os.path.dirname(__file__)+ '/../plugin.video.unified.search')
  from unified_search import UnifiedSearch
except: pass

__settings__ = xbmcaddon.Addon(id='plugin.video.new-kino.net')
use_translit = __settings__.getSetting('translit')

try:  
  import Translit as translit
  translit = translit.Translit()  
except: use_translit = 'false'

dbg = 0

pluginhandle = int(sys.argv[1])

start_pg = "http://new-kino.net/"
page_pg = "page/"
find_pg = "http://new-kino.net/?do=search&subaction=search&story="
search_start = "&search_start="

def gettranslit(msg):
    if use_translit == 'true': 
        return translit.rus(msg)
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

def NKN_start(url, page, cook):
    dbg_log('-NKN_start:' + '\n')
    dbg_log('- url:'+  url + '\n')
    dbg_log('- page:'+  page + '\n')
    dbg_log('- cook:'+  cook + '\n')    
    ext_ls = [('<КАТАЛОГ>', '?mode=ctlg'),
              ('<ПОИСК>', '?mode=find')]
    unis_res = []
    unis_en = False
    
    if cook == "unis":
        cook = ""
        unis_en = True
        
              
    if url.find(find_pg) != -1:
        n_url = url + search_start + page
    else:
        n_url = url + page_pg + page + '/'
        
    dbg_log('- n_url:'+  n_url + '\n')
    horg = get_url(n_url, cookie = cook, save_cookie = True)
    if cook=='':
        cook = re.search('<cookie>(.+?)</cookie>', horg).group(1)
    i = 0
    
    if unis_en == False:
      for ctTitle, ctMode  in ext_ls:
        item = xbmcgui.ListItem(ctTitle)
        uri = sys.argv[0] + ctMode + '&cook=' + urllib.quote_plus(cook)
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  
        dbg_log('- uri:'+  uri + '\n')    
    

    http = re.sub('<br />', '', horg)
    hrefs = re.compile('<a href="(.*?)(#|">|" >)(.*?)</a></h4>').findall(http)

    if len(hrefs):
        news_id = re.compile("news-id-[0-9]")
        news = BeautifulSoup(http).findAll('div',{"id":news_id})
        
        if (len(hrefs) == len(news)):
            for sa in news:

                href = hrefs[i][0]
                dbg_log('-HREF %s'%href)
#                infos = re.compile('<img src="/(.*?)" alt="(.*?)" title="(.*?)" />(</a><!--TEnd--></div>|<!--dle_image_end-->)(.*?)<').findall(str(sa))
                infos = re.compile('<img src="/(.*?)" alt="(.*?)" title="(.*?)" />').findall(str(sa))
                print infos
#                 for logo, alt, title, plot in infos:
                for logo, alt, title in infos:
                  img = start_pg + logo
                  dbg_log('-TITLE %s'%title)
                  dbg_log('-IMG %s'%img)
#                   dbg_log('-PLOT %s'%plot)
                  
                  if unis_en == False:
                    item = xbmcgui.ListItem(title, iconImage=img, thumbnailImage=img)
#                     item.setInfo( type='video', infoLabels={'title': title, 'plot': plot})
                    item.setInfo( type='video', infoLabels={'title': title})
                    uri = sys.argv[0] + '?mode=view' \
                    + '&url=' + urllib.quote_plus(href) + '&img=' + urllib.quote_plus(img) \
                     + '&name=' + urllib.quote_plus(title)+ '&cook=' + urllib.quote_plus(cook)
                    xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  
                    dbg_log('- uri:'+  uri + '\n')
                    i = i + 1
                  else:
                    try: unis_res.append({'title':  title, 'url': href, 'image': img, 'plugin': 'plugin.video.new-kino.net'})
                    except: pass
    
    if unis_en == True:
      try: UnifiedSearch().collect(unis_res)
      except:  pass
    else:
      if i:
        item = xbmcgui.ListItem('<NEXT PAGE>')
        uri = sys.argv[0] + '?page=' + str(int(page) + 1) + '&url=' + urllib.quote_plus(url)+ '&cook=' + urllib.quote_plus(cook)
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
        dbg_log('- uri:'+  uri + '\n')
        item = xbmcgui.ListItem('<NEXT PAGE +10>')
        uri = sys.argv[0] + '?page=' + str(int(page) + 10) + '&url=' + urllib.quote_plus(url)+ '&cook=' + urllib.quote_plus(cook)
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
        dbg_log('- uri:'+  uri + '\n')        
 
      xbmcplugin.endOfDirectory(pluginhandle) 


def NKN_view(url, img, name, cook):     
    dbg_log('-NKN_view:'+ '\n')
    dbg_log('- url:'+  url + '\n')
    dbg_log('- img:'+  img + '\n')
    dbg_log('- name:'+  name + '\n')
        
    http = get_url(url, cookie = cook)
#    news_id = re.compile("news-id-[0-9]")
#    news = BeautifulSoup(http).findAll('div',{"id":news_id})

#    for sa in news:    
        #print str(sa)
#        flvars = re.compile('<param name="flashvars" value="(.*?)"').findall(str(sa))
        #print urllib.unquote_plus(flvars[0])
#        files = re.compile('file=(.*?)"').findall(str(sa))

    frames = re.compile('<iframe (.*?)</iframe>').findall(http)
    if len(frames) > 0:
        
#         files = re.compile('src="(.*?)"').findall(frames[0])
        
#         print files

        i = 1
#         for file in files:

        for frame in frames:
            files = re.compile('src="(.*?)"').findall(frame)
            for file in files:
                if 'facebook' not in file:
                    if len(frames) > 1:
                        title = str(i) + ' - ' + name
                    else:
                        title = name
                    i += 1
                    
                    if 'http' not in file:
                        file = 'http:' + file 
        
                    item = xbmcgui.ListItem(title, iconImage=img, thumbnailImage=img)
                    uri = sys.argv[0] + '?mode=play' \
                    + '&name=' + urllib.quote_plus(name) \
                    + '&url=' + urllib.quote_plus(file) + '&cook=' + urllib.quote_plus(cook)
                    item.setProperty('IsPlayable', 'true')
                    xbmcplugin.addDirectoryItem(pluginhandle, uri, item)  
                    dbg_log('- uri:'+  uri + '\n')

        xbmcplugin.endOfDirectory(pluginhandle)


def Decode2(param):
        try:
            hk = ("0123456789WGXMHRUZID=NQVBLihbzaclmepsJxdftioYkngryTwuvihv7ec41D6GpBtXx3QJRiN5WwMf=ihngU08IuldVHosTmZz9kYL2bayE").split('ih')
            hash_key = hk[0]+'\n'+hk[1]

            #-- define variables
            loc_3 = [0,0,0,0]
            loc_4 = [0,0,0]
            loc_2 = ''

            #-- define hash parameters for decoding
            dec = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='
            hash1 = hash_key.split('\n')[0]
            hash2 = hash_key.split('\n')[1]

            #-- decode
            for i in range(0, len(hash1)):
                re1 = hash1[i]
                re2 = hash2[i]

                param = param.replace(re1, '___')
                param = param.replace(re2, re1)
                param = param.replace('___', re2)

            i = 0
            while i < len(param):
                j = 0
                while j < 4 and i+j < len(param):
                    loc_3[j] = dec.find(param[i+j])
                    j = j + 1

                loc_4[0] = (loc_3[0] << 2) + ((loc_3[1] & 48) >> 4);
                loc_4[1] = ((loc_3[1] & 15) << 4) + ((loc_3[2] & 60) >> 2);
                loc_4[2] = ((loc_3[2] & 3) << 6) + loc_3[3];

                j = 0
                while j < 3:
                    if loc_3[j + 1] == 64 or loc_4[j] == 0:
                        break

                    loc_2 += unichr(loc_4[j])

                    j = j + 1
                i = i + 4;
        except:
            loc_2 = ''

        return loc_2

def DecodeUppodText2(sData):
  hash = "0123456789WGXMHRUZID=NQVBLihbzaclmepsJxdftioYkngryTwuvihv7ec41D6GpBtXx3QJRiN5WwMf=ihngU08IuldVHosTmZz9kYL2bayE"

#  Проверяем, может не нужно раскодировать (json или ссылка)
#  if ((Pos("{", sData)>0) || (LeftCopy(sData, 4)=="http")) return HmsUtf8Decode(sData);

  sData = DecodeUppod_tr(sData, "r", "A")
  
  hash = hash.replace('ih', '\n')
  if sData[-1] == '!' :
    sData = sData[:len(sData)-1]
    tab_a = hash.split('\n')[3]
    tab_b = hash.split('\n')[2]
  else:
    tab_a = hash.split('\n')[1]
    tab_b = hash.split('\n')[0]

  sData = sData.replace("\n", "")
  
  for i in range(1, len(tab_a)):
    char1 = tab_b[i]
    char2 = tab_a[i]
    sData = sData.replace(char1, "___")
    sData = sData.replace(char2, char1)
    sData = sData.replace("___", char2)

  sData = DecodeUppod_Base64(sData)
  sData = sData.replace("hthp:", "http:")
  return sData

def DecodeUppod_tr(sData, ch1, ch2):
  s = ""
  if (sData[len(sData)-1] == ch1) and (sData[3] == ch2):
    nLen = len(sData);
    for i in range(nLen, 1, -1): s += sData[i]
    loc3 = Int(Int(s[nLen-1:nLen])/2)
    s = s[3, nLen-2]
    i = loc3
    if loc3 < len(s):
      while (i < len(s)):
        s = s[:i] + s[i+2:]
        i+= loc3
    sData = s + "!"

  return sData
  
  
def DecodeUppod_Base64(param):
    #-- define variables
    loc_3 = [0,0,0,0]
    loc_4 = [0,0,0]
    loc_2 = ''
    #-- define hash parameters for decoding
    dec = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='
    i = 0
    while i < len(param):
        j = 0
        while j < 4 and i+j < len(param):
            loc_3[j] = dec.find(param[i+j])
            j = j + 1

        loc_4[0] = (loc_3[0] << 2) + ((loc_3[1] & 48) >> 4);
        loc_4[1] = ((loc_3[1] & 15) << 4) + ((loc_3[2] & 60) >> 2);
        loc_4[2] = ((loc_3[2] & 3) << 6) + loc_3[3];

        j = 0
        while j < 3:
            if loc_3[j + 1] == 64: break
            loc_2 += unichr(loc_4[j])
            j = j + 1
        i = i + 4

    return loc_2        

def VK(html):

    soup = BeautifulSoup(html, fromEncoding="windows-1251")
    video = []

    for rec in soup.findAll('script', {'type':'text/javascript'}):
        if 'video_host' in rec.text:
            
            vars = re.compile('var vars = {(.+?)"}').findall(html)
#            if 0:
            if len(vars):
                var = re.compile('"(.+?)":(.+?),').findall(vars[0] + '"')
                for r in var:
                    if r[0] == 'url240': video.append(r[1].strip('"').split('?')[0].replace('\\/','/'))
                    elif r[0] == 'url360': video.append(r[1].strip('"').split('?')[0].replace('\\/','/'))
                    elif r[0] == 'url480': video.append(r[1].strip('"').split('?')[0].replace('\\/','/'))
                    elif r[0] == 'url720': video.append(r[1].strip('"').split('?')[0].replace('\\/','/'))
                    
                video.sort()
                video.reverse()

            else:
                var = re.compile('var (.+?) = \'(.+?)\';').findall(html)
                for r in var:
                    if r[0] == 'video_host':
                        video_host = r[1]#.replace('userapi', 'vk')
                    if r[0] == 'video_uid':
                        video_uid = r[1]
                    if r[0] == 'video_vtag':
                        video_vtag = r[1]

                video.append('%su%s/videos/%s.%s.mp4'%(video_host, video_uid, video_vtag, '720'))
                video.append('%su%s/videos/%s.%s.mp4'%(video_host, video_uid, video_vtag, '480'))
                video.append('%su%s/videos/%s.%s.mp4'%(video_host, video_uid, video_vtag, '360'))
                video.append('%su%s/videos/%s.%s.mp4'%(video_host, video_uid, video_vtag, '240'))

    return video
    


def NKN_play(url, cook, name):     
    dbg_log('-NKN_play:'+ '\n')
    dbg_log('- url:'+  url.replace('&amp;', '&') + '\n')
    url = url.replace('&amp;', '&')
    furls = []
    http = get_url(url, cookie = cook)
#    print urllib.unquote_plus(http)
    if 'kinolot.com/get.php' in url:
        files = re.compile('file=(.*?)&').findall(http)
        if len(files):
#            print 'file'
#            print files[0]
            furls.append(Decode2(Decode2(urllib.unquote_plus(files[0]))))
    elif 'vk.com' in url:
        print 'vk.com'
        furls = VK(http)
    elif 'vkontakte.ru' in url:
        print 'vkontakte.ru'
        furls = VK(http)
        
    if len(furls) == 1:
        dbg_log('- furl:'+  furls[0] + '\n')
        item = xbmcgui.ListItem(path = furls[0])
        xbmcplugin.setResolvedUrl(pluginhandle, True, item)
    elif len(furls):
        sPlayList   = xbmc.PlayList(xbmc.PLAYLIST_VIDEO) 
        sPlayer     = xbmc.Player()
        sPlayList.clear()
        runRes = False
        for furl in furls:
            item = xbmcgui.ListItem(name, path = furl)
            item.setProperty('mimetype', 'video/x-msvideo')
            item.setProperty('IsPlayable', 'true')
            sPlayList.add(furl, item) #, 0) 
            if not runRes: 
                xbmcplugin.setResolvedUrl(pluginhandle, True, item)
                runRes = True
        sPlayer.play(sPlayList)
         

def NKN_ctlg(url, cook):
    dbg_log('-NKN_ctlg:' + '\n')
    dbg_log('- url:'+  url + '\n')

    catalog = [("komedii/", "Комедии"),
               ("boeviki/", "Боевики"),
               ("trillery/", "Триллеры"),
               ("detektivnye/", "Детективные"),
               ("voennye/", "Военные"),
               ("otechestvennye/", "Отечественные"),
               ("istoricheskie/", "Исторические"),
               ("semejjnye/", "Семейные"),
               ("prikljuchencheskie/", "Приключенческие"),
               ("animacionnye/", "Анимационные"),
               ("dokumentalnye/", "Документальные"),
               ("serialy/", "Сериалы"),
               ("fantasticheskie/", "Фантастические"),
               ("misticheskie/", "Мистические"),
               ("uzhasy/", "Ужасы"),
               ("fjentezi/", "Фэнтези"),
               ("dramy/", "Драмы"),
               ("melodramy/", "Мелодрамы"),
               ("kriminalnye/", "Криминальные"),
               ("jumor/", "Юмор"),
               ("oskar/", "Премия Оскар")]
               
    for ctLink, ctTitle  in catalog:
        item = xbmcgui.ListItem(ctTitle)
        uri = sys.argv[0] \
        + '?url=' + urllib.quote_plus(start_pg + ctLink) + '&cook=' + urllib.quote_plus(cook)
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  
        dbg_log('- uri:'+  uri + '\n')
        
    xbmcplugin.endOfDirectory(pluginhandle)

def uni2cp(ustr):
    raw = ''
    uni = unicode(ustr, 'utf8')
    uni_sz = len(uni)
    for i in range(uni_sz):
        raw += ('%%%02X') % ord(uni[i].encode('cp1251'))
    return raw  

def NKN_find(cook):     
    dbg_log('-NKN_find:'+ '\n')
    dbg_log('- cook:'+  cook + '\n')      
    
    kbd = xbmc.Keyboard()
    kbd.setHeading('ПОИСК')
    kbd.doModal()
    if kbd.isConfirmed():
        stxt = uni2cp(kbd.getText())
        furl = find_pg + stxt
        dbg_log('- furl:'+  furl + '\n')
        NKN_start(furl, '1', cook)

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


cook = ''
mode=''
url=''
ordr='0'
dir='0'
off='0'
gnrs=''
imag=''
name=''

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
    imag=urllib.unquote_plus(params['img'])
    dbg_log('-IMaG:'+ imag + '\n')
except: pass 
try: 
    name=urllib.unquote_plus(params['name'])
    dbg_log('-NAME:'+ name + '\n')
except: pass 
try: 
    cook=urllib.unquote_plus(params['cook'])
    dbg_log('-COOK:'+ cook + '\n')
except: pass

keyword = params['keyword'] if 'keyword' in params else None
unified = params['unified'] if 'unified' in params else None

if url=='':
    url = start_pg

if mode == '': NKN_start(url, page, cook)
elif mode == 'ctlg': NKN_ctlg(url, cook)
elif mode == 'view': NKN_view(url, imag, name, cook)
elif mode == 'play': NKN_play(url, cook, name)
elif mode == 'find': NKN_find(cook)
elif mode == 'show': NKN_view(url, imag, "Play Video", cook)
elif mode == 'search': 
    url = find_pg + uni2cp(gettranslit(keyword))
    NKN_start(url, '1', 'unis')



