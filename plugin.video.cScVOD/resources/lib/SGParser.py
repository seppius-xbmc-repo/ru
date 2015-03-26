# -*- coding: utf-8 -*-
import sys, urllib2, urllib, os, re, base64, jsunpack, cookielib
try:
    import json
except:
    import simplejson as json
import datetime
from time import time
from time import sleep
from net import Net
from SGInternationalParser import europe_parsers

def debug(obj, text = ''):
    print datetime.fromtimestamp(time()).strftime('[%H:%M:%S]')
    print '%s' % text + ' %s\n' % obj


def mod_request(url, param = None):
    try:
        debug(url, 'MODUL REQUEST URL')
        req = urllib2.Request(url, param, {'User-agent': 'QuickTime/7.6.2 (qtver=7.6.2;os=Windows NT 5.1 Service Pack 3)'})
        html = urllib2.urlopen(req).read()
    except Exception as ex:
        print ex
        print 'REQUEST Exception'

    return html


def hdrezka_film(url):
    parts = url.split('@')
    url = parts[1]
    request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
     'Connection': 'Close'})
    try:
        page = urllib2.urlopen(request).read()
        code = re.findall('name="post_id" id="post_id" value="(.*)" />', page)
        if len(code) > 0:
            url2 = 'http://hdrezka.tv/engine/ajax/getvideo.php'
            headers = {'Accept': 'text/plain, */*; q=0.01',
             'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
             'Host': 'hdrezka.tv',
             'Referer': url,
             'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:27.0) Gecko/20100101 Firefox/27.0',
             'X-Requested-With': 'XMLHttpRequest'}
            data = urllib.urlencode({'id': code[0]})
            plist = []
            plist2 = []
            request = urllib2.Request(url2, data, headers)
            response = urllib2.urlopen(request).read()
            page = json.loads(response)
            url2 = json.loads(page['link'])
            if url2['mp4'] > 0:
                code_url = 'http://185.25.119.98/php/rezka.php?url=' + url2['mp4']
                request2 = urllib2.Request(code_url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                hash = urllib2.urlopen(request2).read()
                url = hash
                print url
            url = url
            print url
        url = url
        print url
    except Exception as ex:
        print ex

    return url


def hdrezka_serial(url):
    parts = url.split('@')
    url = parts[1]
    season = parts[3]
    episode = parts[2]
    request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
     'Connection': 'Close'})
    try:
        page = urllib2.urlopen(request).read()
        code = re.findall('class="b-content__inline_item" data-id="(.*)"', page)
        if len(code) > 0:
            print 'get video'
            url2 = 'http://hdrezka.tv/engine/ajax/getvideo.php'
            headers = {'Accept': 'text/plain, */*; q=0.01',
             'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
             'Host': 'hdrezka.tv',
             'Referer': url,
             'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:27.0) Gecko/20100101 Firefox/27.0',
             'X-Requested-With': 'XMLHttpRequest'}
            data = urllib.urlencode({'id': code[0],
             'season': season,
             'episode': episode})
            plist = []
            request = urllib2.Request(url2, data, headers)
            response = urllib2.urlopen(request).read()
            page = json.loads(response)
            url2 = json.loads(page['link'])
            if url2['mp4'] > 0:
                code_url = 'http://185.25.119.98/php/rezka.php?url=' + url2['mp4']
                request2 = urllib2.Request(code_url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                hash = urllib2.urlopen(request2).read()
                url = hash
                print 'hdrezka serial: ' + url
            url = url
            print url
        url = url
        print url
    except Exception as ex:
        print ex

    return url


def hdrezka_gid(url):
    parts = url.split('@')
    url = parts[1]
    request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
     'Connection': 'Close'})
    try:
        page = urllib2.urlopen(request).read()
        code_list = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', page)
        for urls in code_list:
            if urls.find('720.mp4/manifest') > 0:
                url = urls
            elif urls.find('480.mp4/manifest') > 0:
                url = urls

        url = url
        url = url.replace("',", '')
        url = url.replace('/manifest.f4m', '')
        print 'gggggg' + url
    except Exception as ex:
        print ex

    return url

##################################################################################################################################

def MYOBFUSCATECOM_OIO(data, _0lllOI="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=", enc=''):
    i = 0;
    while i < len(data):
        h1 = _0lllOI.find(data[i]);
        h2 = _0lllOI.find(data[i+1]);
        h3 = _0lllOI.find(data[i+2]);
        h4 = _0lllOI.find(data[i+3]);
        i += 4;
        bits = h1 << 18 | h2 << 12 | h3 << 6 | h4;
        o1 = bits >> 16 & 0xff;
        o2 = bits >> 8 & 0xff;
        o3 = bits & 0xff;
        if h3 == 64:
            enc += chr(o1);
        else:
            if h4 == 64:
                enc += chr(o1) + chr(o2);
            else:
                enc += chr(o1) + chr(o2) + chr(o3);
    return enc

def MYOBFUSCATECOM_0ll(string, baseRet=''):
    ret = baseRet
    i = len(string) - 1
    while i >= 0:
        ret += string[i]
        i -= 1
    return ret

def getDataBeetwenMarkers(data, marker1, marker2, withMarkers=True, caseSensitive=True):
    if caseSensitive:
        idx1 = data.find(marker1)
    else:
        idx1 = data.lower().find(marker1.lower())
    if -1 == idx1: return False, ''
    if caseSensitive:
        idx2 = data.find(marker2, idx1 + len(marker1))
    else:
        idx2 = data.lower().find(marker2.lower(), idx1 + len(marker1))
    if -1 == idx2: return False, ''
    
    if withMarkers:
        idx2 = idx2 + len(marker2)
    else:
        idx1 = idx1 + len(marker1)

    return True, data[idx1:idx2]

def parseHQQstream(url):
    print("parse NETUTV,HQQ url[%s]\n" % url)
    match = re.search("=([0-9A-Z]+?)[^0-9^A-Z]", url + '|' )
    vid = match.group(1)
    playerUrl = "http://hqq.tv/sec/player/embed_player.php?vid=%s&autoplay=no" % vid    
    HTTP_HEADER= { 'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36',
                   'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' }
    HTTP_HEADER['Referer'] = url
    req = urllib2.Request(playerUrl, headers=HTTP_HEADER)
    data = urllib2.urlopen(req).read()
    data = base64.b64decode(re.search('base64\,([^"]+?)"', data).group(1))
    l01 = re.search("='([^']+?)'", data).group(1)
    _0x84de = re.search("var _0x84de=\[([^]]+?)\]", data).group(1)
    _0x84de = re.compile('"([^"]*?)"').findall(_0x84de)    
    data = MYOBFUSCATECOM_OIO( MYOBFUSCATECOM_0ll(l01, _0x84de[1]), _0x84de[0], _0x84de[1])
    data = re.search("='([^']+?)'", data).group(1).replace('%', '\\').decode('unicode-escape').encode('UTF-8')
    data = re.compile('<input name="([^"]+?)" [^>]+? value="([^"]+?)">').findall(data)
    post_data = {}
    for idx in range(len(data)):
        post_data[ data[idx][0] ] = data[idx][1]   
    secPlayerUrl = "http://hqq.tv/sec/player/embed_player.php?vid=%s&at=%s&autoplayed=%s&referer=on&http_referer=%s&pass=" % (vid, post_data.get('at', ''),  post_data.get('autoplayed', ''), urllib.quote(playerUrl))
    HTTP_HEADER['Referer'] = playerUrl
    req = urllib2.Request(secPlayerUrl, headers=HTTP_HEADER)
    data = urllib2.urlopen(req).read()
    try:
        file_vars = getDataBeetwenMarkers(data, 'unescape(', ')', False)[1]
        file_name = getDataBeetwenMarkers(data, 'file:', ',', False)[1].strip()
        file_vars = file_vars.replace('%', '%u00')
        file_vars = re.search('"(.*?)"', file_vars).group(1).replace('%', '\\').decode('unicode-escape').encode('UTF-8')
        file_vars = getDataBeetwenMarkers(file_vars, file_name + ' = ', ';', False)[1].strip()
        file_vars = file_vars.split('+')
    except:
        file_vars = None
    file_url = ''
    if file_vars != None:
        try:
            for file_var in file_vars:
                file_var = file_var.strip()
                if 0 < len(file_var):
                    match = re.search('''["']([^"]*?)["']''', file_var)
                    if match:
                        file_url += match.group(1)
                    else:
                        file_url += re.search('''var[ ]+%s[ ]*=[ ]*["']([^"]*?)["']''' % file_var, data).group(1)
        except:
            file_url = None
    if file_url.startswith('#') and 3 < len(file_url):
        file_url = getUtf8Str(file_url[1:])
    
    if file_url.startswith('http'):
        return file_url
    return None

def getUtf8Str(st):
    idx = 0
    st2 = ''
    while idx < len(st):
        st2 += '\\u0' + st[idx:idx + 3]
        idx += 3
    return st2.decode('unicode-escape').encode('UTF-8')	

########################################################################################################################

class common:
    HOST   = 'Mozilla/5.0 (Windows NT 6.1; rv:17.0) Gecko/20100101 Firefox/17.0'
    HEADER = None

    def __init__(self, proxyURL= '', useProxy = False):
        self.proxyURL = proxyURL
        self.useProxy = useProxy  
    
    def getPage(self, url, addParams = {}, post_data = None):
        try:
            addParams['url'] = url
            if 'return_data' not in addParams:
                addParams['return_data'] = True
            response = self.getURLRequestData(addParams, post_data)
            status = True
        except:
            response = None
            status = False
        return (status, response)
            
    def getURLRequestData(self, params = {}, post_data = None):
        
        def urlOpen(req, customOpeners):
            if len(customOpeners) > 0:
                opener = urllib2.build_opener( *customOpeners )
                response = opener.open(req)
            else:
                response = urllib2.urlopen(req)
            return response
        
        cj = cookielib.LWPCookieJar()

        response = None
        req      = None
        out_data = None
        opener   = None
        
        if 'host' in params:
            host = params['host']
        else:
            host = self.HOST

        if 'header' in params:
            headers = params['header']
        elif None != self.HEADER:
            headers = self.HEADER
        else:
            headers = { 'User-Agent' : host }

        customOpeners = []

        if 'use_cookie' not in params and 'cookiefile' in params and ('load_cookie' in params or 'save_cookie' in params):
            params['use_cookie'] = True 
        
        if params.get('use_cookie', False):
            if params.get('load_cookie', False):
                try:
                    cj.load(params['cookiefile'], ignore_discard = True)
                except:
                    printExc()
            try:
                for cookieKey in params.get('cookie_items', {}).keys():
                    printDBG("cookie_item[%s=%s]" % (cookieKey, params['cookie_items'][cookieKey]))
                    cookieItem = cookielib.Cookie(version=0, name=cookieKey, value=params['cookie_items'][cookieKey], port=None, port_specified=False, domain='', domain_specified=False, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=None, discard=True, comment=None, comment_url=None, rest={'HttpOnly': None}, rfc2109=False)
                    cj.set_cookie(cookieItem)
            except:
                print 'cocie error'
            customOpeners.append( urllib2.HTTPCookieProcessor(cj) )

        if self.useProxy:
            http_proxy = self.proxyURL
        else:
            http_proxy = ''

        if 'http_proxy' in params:
            http_proxy = params['http_proxy']
        if '' != http_proxy:
            customOpeners.append( urllib2.ProxyHandler({"http":http_proxy}) )
            customOpeners.append( urllib2.ProxyHandler({"https":http_proxy}) )

        if None != post_data:
            if params.get('raw_post_data', False):
                dataPost = post_data
            else:
                dataPost = urllib.urlencode(post_data)
            req = urllib2.Request(params['url'], dataPost, headers)
        else:
            req = urllib2.Request(params['url'], None, headers)

        if not params.get('return_data', False):
            out_data = urlOpen(req, customOpeners)
        else:
            gzip_encoding = False
            try:
                response = urlOpen(req, customOpeners)
                if response.info().get('Content-Encoding') == 'gzip':
                    gzip_encoding = True
                data = response.read()
                response.close()
            except urllib2.HTTPError, e:
                if e.code == 404:
                    if e.fp.info().get('Content-Encoding', '') == 'gzip':
                        gzip_encoding = True
                    data = e.fp.read()
                else:
                    if e.code in [300, 302, 303, 307] and params.get('use_cookie', False) and params.get('save_cookie', False):
                        new_cookie = e.fp.info().get('Set-Cookie', '')
                    raise e
            try:
                if gzip_encoding:
                    buf = StringIO(data)
                    f = gzip.GzipFile(fileobj=buf)
                    out_data = f.read()
                else:
                    out_data = data
            except:
                out_data = data
 
        if params.get('use_cookie', False) and params.get('save_cookie', False):
            cj.save(params['cookiefile'], ignore_discard = True)

        return out_data 

def getSearchGroups(data, pattern, grupsNum=1):
    tab = []
    match = re.search(pattern, data)
    
    for idx in range(grupsNum):
        try:    value = match.group(idx + 1)
        except: value = ''
        tab.append(value)
    return tab
        
def parserMYVIRU(linkUrl):
    COOKIE_FILE = '/tmp/myvicocie'
    params  = {'cookiefile':COOKIE_FILE, 'use_cookie': True, 'save_cookie':True}
    HTTP_HEADER= { 'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36',
                   'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' }
    if linkUrl.startswith("http://myvi.ru/player/flash/"):
        videoId = linkUrl.split('/')[-1]
        sts, response = common().getPage(linkUrl, {'return_data':False})
        preloaderUrl = response.geturl()
        response.close()
        flashApiUrl = "http://myvi.ru/player/api/video/getFlash/%s?ap=1&referer&sig&url=%s" % (videoId, urllib.quote(preloaderUrl))
        sts, data = common().getPage(flashApiUrl)
        data = data.replace('\\', '')
        data = re.search('"videoUrl":"(.*?)"', data).group(1).replace('\/', '/')
        linkUrl = "http:" + data
    if linkUrl.startswith("http://myvi.tv/embed/html/"): 
        sts, data = common().getPage(linkUrl)
        data = getSearchGroups(data, """dataUrl[^'^"]*?:[^'^"]*?['"]([^'^"]+?)['"]""")[0]
        sts, data = common().getPage("http:" + data, params)
        data = json.loads(data)
        for item in data['sprutoData']['playlist']:
            url = item['video'][0]['url'].encode('utf-8')
    return url

##########################################################################################################################################
	
class sg_parsers:

    def __init__(self):
        self.quality = ''

    def get_parsed_link(self, url):
        try:
            if url.find('vidics.ch') > -1:
                req = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                res = urllib2.urlopen(req)
                url = res.geturl()
            if url.find('movie25.cm') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code = re.findall('<IFRAME SRC="(.*)" FRAME', page)
                    if len(code) > 0:
                        md5hash = code[0]
                        url = md5hash
                except Exception as ex:
                    print ex
					
            if url.find('solarmovie.is') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code = re.findall('src="(.*?)"', page)
                    if len(code) > 0:
                        md5hash = code[0]
                        url = md5hash
                except Exception as ex:
                    print ex

            url = europe_parsers().get_parsed_link(url)
            if url.find('.lovekino.tv/video/md5hash') > -1:
                url1 = 'http://s2.lovekino.tv/player/play.php?name=films/klyatva.na.krovi.2010.xvid.iptvrip.filesx.flv'
                request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code = re.findall('video/(.*?)/', page)
                    if len(code) > 0:
                        md5hash = code[0]
                        url = url.replace('md5hash', md5hash)
                except Exception as ex:
                    print ex

            if url.find('.kinoylei.ru') > -1:
                url1 = 'http://server1.kinoylei.ru/get2/3074'
                request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code = re.findall('film/(.*?)/', page)
                    if len(code) > 0:
                        md5hash = code[0]
                        url = url.replace('md5hash', md5hash)
                except Exception as ex:
                    print ex

            if url.find('.kinoluvr.ru') > -1:
                url1 = 'http://server1.kinoluvr.ru/get2/5792'
                request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code = re.findall('film/(.*?)/', page)
                    if len(code) > 0:
                        md5hash = code[0]
                        url = url.replace('md5hash', md5hash)
                except Exception as ex:
                    print ex

            if url.find('stepashka.com/video/') > -1:
                url1 = 'http://online.stepashka.com/filmy/trillery/26171-oblivion-oblivion-2013.html'
                request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 (Windows NT 6.0; rv:12.0) Gecko/20100101 Firefox/12.0',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code_list = re.findall('"st=http://online.stepashka.com\\/player\\/26171\\/.*\\/(.*)\\/1"', page)
                    if len(code_list) > 0:
                        md5 = code_list[0]
                        url = url.replace('md5hash', md5)
                        print 'stepashka'
                        print url
                except Exception as ex:
                    print ex

            if url.find('kaban.tv/') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code_list = re.findall(',"file":"(.*)","f', page)
                    if len(code_list) > 0:
                        code = code_list[0]
                        code_url = 'http://185.25.119.98/php/kaban/kaban.php?code=' + code
                        request2 = urllib2.Request(code_url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                         'Connection': 'Close'})
                        try:
                            hash = urllib2.urlopen(request2).read()
                            code_list2 = re.findall('or (.*)', hash)
                            if len(code_list2) > 0:
                                url = code_list2[0]
                                print 'kabantv'
                                print url
                            else:
                                url = hash
                        except Exception as ex:
                            print ex

                except Exception as ex:
                    print ex

            if url.find('poiuytrew.pw/') > -1:
                url1 = 'http://filmix.net/dramy/82725-vnutri-lyuina-devisa-inside-llewyn-davis-2013.html'
                request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code_list = re.findall("cleanArray\(\['(.*?)','.*?\','','',''\]", page)
                    if len(code_list) > 0:
                        code = code_list[0]
                        print 'ffffffffffff ' + code
                        code_url = 'http://185.25.119.98/php/filmix_c.php?code=' + code
                        request2 = urllib2.Request(code_url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                         'Connection': 'Close'})
                        hash = urllib2.urlopen(request2).read()
                        print 'hhhhhhhhh ' + hash
                        url = url.replace('md5hash', hash)
                        if url.find('[720,480,360]') > -1:
                            url = url.replace('[720,480,360]', '720')
                        elif url.find('[,480,360]') > -1:
                            url = url.replace('[,480,360]', '480')
                        else:
                            url = url
                        print 'filmix'
                        print url
                except Exception as ex:
                    print ex

            if url.find('pirateplayer.com/') > -1:
                url1 = 'http://online.stepashka.com/filmy/detektiv/29140-falshivaya-kukla-hamis-a-baba-1991.html'
                request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code_list = re.findall('st=http:\\/\\/online.stepashka.com\\/player\\/.*\\/.*\\/(.*)\\/"', page)
                    if len(code_list) > 0:
                        code = code_list[0]
                        url = url.replace('md5hash', code)
                        print 'stepashka'
                        print url
                except Exception as ex:
                    print ex

            if url.find('.videokub.com/embed/') > -1 or url.find('.videokub.me/embed/') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code_list = re.findall('file:"(.*?)/",', page)
                    if len(code_list) > 0:
                        url = code_list[0]
                        print 'videokub'
                        print url
                except Exception as ex:
                    print ex

            if url.find('hotcloud.org/') > -1:
                url1 = 'https://my-hit.org/film/558/playlist.txt'
                request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code = re.findall('id=(.*?)"}]}', page)
                    if len(code) > 0:
                        md5hash = code[0]
                        url = url.replace('md5hash', md5hash)
                except Exception as ex:
                    print ex

            if url.find('moviestape.com/') > -1:
                url1 = 'http://fs0.moviestape.com/show.php?name=films/Captain.Phillips.mp4'
                request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code = re.findall("file : 'http:\\/\\/.*\\/video\\/(.*)\\/.*\\/.*mp4'};", page)
                    if len(code) > 0:
                        md5hash = code[0]
                        url = url.replace('md5hash', md5hash)
                except Exception as ex:
                    print ex

            if url.find('aburmu4.tv') > -1:
                url1 = 'http://s1.aburmu4.tv/player/play.php?s=1&name=vsfw/antboy_2013.flv'
                request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code = re.findall("file : 'http:\\/\\/.*\\/v\\/(.*)\\/.*\\/.*flv'};", page)
                    if len(code) > 0:
                        md5hash = code[0]
                        url = url.replace('md5hash', md5hash)
                        url = url.replace('aburmu4.tv@', '')
                except Exception as ex:
                    print ex

            if url.find('serverfilm.net') > -1:
                url1 = 'http://srv10.serverfilm.net/php/video.php?name=film/gorod.grehov.2.flv'
                request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code = re.findall("file.*:.*'http:\\/\\/.*\\/video\\/(.*)\\/.*\\/.*flv'};", page)
                    if len(code) > 0:
                        md5hash = code[0]
                        url = url.replace('md5hash', md5hash)
                        url = url.replace('aburmu4.tv@', '')
                except Exception as ex:
                    print ex

            if url.find('dolgoe.net') > -1:
                url1 = 'http://srv10.dolgoe.net/php/video.php?name=film/tammy.2014.flv'
                request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code = re.findall("file.*:.*'http:\\/\\/.*\\/video\\/(.*)\\/.*\\/.*flv'};", page)
                    if len(code) > 0:
                        md5hash = code[0]
                        url = url.replace('md5hash', md5hash)
                        url = url.replace('aburmu4.tv@', '')
                except Exception as ex:
                    print ex

            if url.find('korolek.tv') > -1:
                url1 = 'http://s1.korolek.tv/player/play.php?name=vsfw/golodni.igry.2014.camrip.flv'
                request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code = re.findall("file.*:.*'http:\\/\\/.*\\/v\\/(.*)\\/.*\\/.*flv'};", page)
                    if len(code) > 0:
                        md5hash = code[0]
                        url = url.replace('md5hash', md5hash)
                        url = url.replace('aburmu4.tv@', '')
                except Exception as ex:
                    print ex

            if url.find('serialo.ru/video') > -1:
                url5 = 'http://latino-serialo.ru/italianskie_seriali_online/2638-polny-ocharovaniya-cheias-de-charme-seriya-10.html'
                request = urllib2.Request(url5, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    hash_list = re.findall(';pl=(.*?)"', page)
                    if len(hash_list) > 0:
                        hash = hash_list[0]
                        print 'hash ' + hash
                        request2 = urllib2.Request(hash, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                         'Connection': 'Close'})
                        page = urllib2.urlopen(request2).read()
                        page = page.replace('\n', '')
                        tmp = re.findall('file":"(.*?)"', page)
                        tmp = tmp[0]
                        print 'tmp ' + tmp
                        md5hash = re.findall('\\/video\\/(.*?)\\/', tmp)
                        md5hash = md5hash[0]
                        tmp2 = tmp.replace(md5hash, 'md5hash')
                        md4hash = re.findall('\\/md5hash\\/(.*?)\\/', tmp2)
                        md4hash = md4hash[0]
                        print 'md5hash ' + md5hash
                        print 'md4hash ' + md4hash
                        url2 = url.replace('md5hash', md5hash)
                        url = url2.replace('md4hash', md4hash)
                        print 'PLAY URL' + url
                except Exception as ex:
                    print ex

            if url.find('divan.tv/') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code = re.findall('file: "(.*?)",', page)
                    if len(code) > 0:
                        url = code[0]
                except Exception as ex:
                    print ex

            if url.find('baskino.com/films') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code_list = re.findall('file:"(.*?)"', page)
                    if len(code_list) > 0:
                        url = code_list[0]
                        print 'baskino'
                        print url
                except Exception as ex:
                    print ex

            if url.find('hdrezka.tv/films') > -1:
                url = hdrezka_film(url)
                url = url
            if url.find('hdrezka.tv/series') > -1:
                url = hdrezka_serial(url)
                url = url
            if url.find('hdcdn.nl') > -1:
                url = url.replace('hdcdn.nl', 'moonwalk.cc')
            if url.find('gidtv.cc/s') > -1:
                url = hdrezka_gid(url)
                url = url
            if url.find('kinobar.net/player') > -1 or url.find('kinomig.tv') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code_list = re.findall('src="(.*)" type=', page)
                    if len(code_list) > 0:
                        url = code_list[0]
                        print 'kinobar'
                        print url
                except Exception as ex:
                    print ex

            if url.find('serials.tv/') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code_list = re.findall("src: '(.*?)',", page)
                    if len(code_list) > 0:
                        url = code_list[0]
                        print 'kinobar'
                        print url
                except Exception as ex:
                    print ex

            if url.find('.jampo.tv/play') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code_list = re.findall('<video width=".*?" height=".*?" src="(.*?)" controls />', page)
                    if len(code_list) > 0:
                        url = code_list[0]
                        print 'jampo'
                        print url
                except Exception as ex:
                    print ex

            if url.find('lidertvvv') > -1:
                url = url.replace('lidertvvv', '')
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code = re.findall('file: "(.*?)",', page)
                    if len(code) > 0:
                        url = code[0]
                except Exception as ex:
                    print ex

            if url.find('moonwalk.cc/serial') > -1:
                url1 = url
                request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code = re.findall("video_token: '(.*)',", page)
                    if len(code) > 0:
                        url = 'http://moonwalk.cc/video/' + code[0] + '/iframe'
                except Exception as ex:
                    print ex

            if url.find('moonwalk.cc/video') > -1:
                # url1 = 'http://185.25.119.98/tes/tes.php?url=' + url
                # request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 # 'Connection': 'Close'})
                # try:
                    # page = urllib2.urlopen(request).read()
                    # url = page
                # except Exception as ex:
                    # print ex
				url = url.replace('iframe','index.m3u8')

            if url.find('serialon.com/') > -1:
                url1 = 'http://www.serialon.com/serial/10601-agent-osobogo-naznacheniya-4-15-seriya.html'
                request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code = re.findall("file':'http:\\/\\/www.serialon.com\\/.*\\/(.*)\\/.*\\/.*\\/.*.flv", page)
                    if len(code) > 0:
                        md5hash = code[0]
                        url = url.replace('md5hash', md5hash)
                except Exception as ex:
                    print ex

            if url.find('serialsonline.net/clip') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code = re.findall('file:"(.*)"', page)
                    if len(code) > 0:
                        url = code[0]
                except Exception as ex:
                    print ex

            if url.find('watch-online-hd.ru/') > -1 or url.find('hdgo.cc') > -1:
                print 'hhhhhdddddddggggggooooooo'
                url1 = 'http://watch-online-hd.ru/embed/54/'
                request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code = re.findall('http://v4.watch-online-hd.ru\\/flv\\/(.*)\\/54-sdelka-s-dyavolom.mp4', page)
                    if len(code) > 0:
                        md5hash = code[0]
                        url = url.replace('md5hash', md5hash)
                except Exception as ex:
                    print ex

            if url.find('onlyclips.net/artist') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code = re.findall('<iframe.*src=".*youtube.com\\/embed\\/(.*)" fr', page)
                    if len(code) > 0:
                        url = 'http://www.youtube.com/watch?v=' + code[0]
                except Exception as ex:
                    print ex

            if url.find('vk.com') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code = re.findall('iframe.*?src="(.*?)"', page)
                    if len(code) > 0:
                        md5hash = code[0]
                        url = md5hash.replace('http:', '')
                        url = 'http:' + url
                except Exception as ex:
                    print ex

            if url.find('rutube.ru') > -1:
                url2 = 'http://185.25.119.98/rutube.php?url=' + url
                request = urllib2.Request(url2, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code = page.replace('amp;', '')
                    url = code
                except Exception as ex:
                    print ex

            if url.find('videoapi.my.mail.ru') > -1:
                url = url.replace('embed/', '')
                url = url.replace('html', 'json')
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code = re.findall('sd":"(.*?)"', page)
                    hd = re.findall('"key":"720p","url":"(.*?)"', page)
                    sd = re.findall('"key":"480p","url":"(.*?)"', page)
                    ld = re.findall('"key":"360p","url":"(.*?)"', page)
                    if len(hd) > 0:
                        url = hd[0]
                    elif len(sd) > 0:
                        url = sd[0]
                    elif len(ld) > 0:
                        url = ld[0]
                    elif len(code) > 0:
                        url = code[0]
                except Exception as ex:
                    print ex

            if url.find('online-cinema.biz') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code = re.findall('&file=(.*?)"', page)
                    code = code[0]
                    if len(code) > 0:
                        url = code
                except Exception as ex:
                    print ex

            if url.find('50.7.168.250/s/md5') > -1 or url.find('video-fokus.org/s/md5') > -1 or url.find('50.7.132.82/s/md5') > -1 or url.find('37.48.85.202/s/md5') > -1:
                url1 = 'http://kino-live.org/hq/715505-slova.html'
                request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    page = page.replace('\n', '')
                    hash_list = re.findall('\\/s\\/(.*?)\\/', page)
                    if len(hash_list) > 0:
                        hash = hash_list[0]
                        url = url.replace('md5hash', hash)
                except Exception as ex:
                    print ex

            if url.find('188.227.185.66/s/md5') > -1 or url.find('176.58.40.180/s/md5') > -1 or url.find('212.113.33.98/s/md5') > -1:
                url1 = 'http://kino-live.org/hq/715505-slova.html'
                request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    page = page.replace('\n', '')
                    hash_list = re.findall('\\/s\\/(.*?)\\/', page)
                    if len(hash_list) > 0:
                        hash = hash_list[0]
                        url = url.replace('md5hash', hash)
                except Exception as ex:
                    print ex

            if url.find('911.to/get_cv/md5/') > -1:
                end = url.split('md5')[1]
                request = urllib2.Request('http://911.to/ajax/get_player/482', None, {'Host': '911.to',
                 'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; ru; rv:1.9.2.13) Gecko/20101203 Firefox/3.6.13',
                 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                 'Accept-Language': 'ru-ru,ru;q=0.8,en-us;q=0.5,en;q=0.3',
                 'Accept-Charset': 'windows-1251,utf-8;q=0.7,*;q=0.7',
                 'Keep-Alive': '115',
                 'Connection': 'keep-alive',
                 'Cache-Control': 'max-age=0',
                 'Referer': 'http%3A%2F%2F911.to%2Fajax%2Fget_player%2F482'})
                try:
                    page = urllib2.urlopen(request).read()
                    if len(page) > 0:
                        md5 = re.findall('http://911.to/get_cv/(.*?)/482', page)[0]
                        url = url.replace('md5', md5)
                except Exception as ex:
                    print ex
					
	        if url.find('hqq.tv/') > -1 or url.find('netu.tv/') > -1:
		        url = parseHQQstream(url)

            if url.find('myvi.ru/') > -1:
                url = parserMYVIRU(url)

            if url.find('filehoot.com/') > -1:
                HTTP_HEADER= { 'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36',
                   'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' }
                req = urllib2.Request(url, headers=HTTP_HEADER)
                data = urllib2.urlopen(req).read()
                file_url = ''
                try:
                    file_url = getDataBeetwenMarkers(data, "file:'", "',", False)[1].strip()
                except:
                    file_url = None
                
                if file_url.startswith('http'):
                    url = file_url
                else:
                    url = None
					
            if url.find('fserver.pw/') > -1:
                #end = url.split('md5')[1]
                request = urllib2.Request('http://sv1.fserver.pw/file_test-K2.1.php?filename=bezvozvratnuy.put.flv&userid=&filmid=1379&filmname=%D0%91%D0%B5%D0%B7%D0%B2%D0%BE%D0%B7%D0%B2%D1%80%D0%B0%D1%82%D0%BD%D1%8B%D0%B9%20%D0%BF%D1%83%D1%82%D1%8C%20%D1%81%D0%BC%D0%BE%D1%82%D1%80%D0%B5%D1%82%D1%8C%20%D0%BE%D0%BD%D0%BB%D0%B0%D0%B9%D0%BD&filmurl=http://onlainfilm.ucoz.ua/load/bezvozvratnyj_put_smotret_onlajn/3-1-0-1379', None, {
                 'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; ru; rv:1.9.2.13) Gecko/20101203 Firefox/3.6.13',
                 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                 'Accept-Language': 'ru-ru,ru;q=0.8,en-us;q=0.5,en;q=0.3',
                 'Accept-Charset': 'windows-1251,utf-8;q=0.7,*;q=0.7',
                 'Keep-Alive': '115',
                 'Connection': 'keep-alive',
                 'Cache-Control': 'max-age=0',
                 'Referer': 'http://onlainfilm.ucoz.ua/load/soprotivlenie_smotret_onlajn/3-1-0-1673'})
                try:
                    page = urllib2.urlopen(request).read()
                    md5 = re.findall('video\\/(.*?)\\/', page)
                    if len(md5) > 0:
                        md5 = md5[0]
                        url = url.replace('md5hash', md5)
                except Exception as ex:
                    print ex

        except Exception as ex:
            print ex
            print 'sgparsed_link'

        return url
