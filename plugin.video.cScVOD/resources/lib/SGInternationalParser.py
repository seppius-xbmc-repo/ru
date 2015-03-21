# Embedded file name: /usr/lib/enigma2/python/Plugins/Extensions/cScVOD/parsers/SGInternationalParser.py
import sys
import urllib2
import urllib
import os
import re
import json
import xbmc,xbmcaddon
import datetime
from time import time
from time import sleep
from net import Net
import jsunpack
net = Net()

addon = xbmcaddon.Addon(id='plugin.video.cScVOD')
datapath = xbmc.translatePath(addon.getAddonInfo('profile'))
cookie_path = os.path.join(datapath, 'cookies')
if os.path.exists(cookie_path) == False:
        os.makedirs(cookie_path)
cookie_jar = os.path.join(cookie_path, "cookie.lwp")

def regex_get_all(text, start_with, end_with):
    r = re.findall("(?i)(" + start_with + "[\S\s]+?" + end_with + ")", text)
    return r

def open_url(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent','Mozilla/5.0 (Linux; <Android Version>; <Build Tag etc.>) AppleWebKit/<WebKit Rev>(KHTML, like Gecko) Chrome/<Chrome Rev> Safari/<WebKit Rev>')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    return link

def regex_from_to(text, from_string, to_string, excluding=True):
    if excluding:
        r = re.search("(?i)" + from_string + "([\S\s]+?)" + to_string, text).group(1)
    else:
        r = re.search("(?i)(" + from_string + "[\S\s]+?" + to_string + ")", text).group(1)
    return r
	
def filmon_play(url):
    sp = url.split('@')
    url = sp[0]
    description = sp[1]	
    streamerlink = net.http_GET(url).content.encode("utf-8").rstrip()
    net.save_cookies(cookie_jar)
    swfplay = 'http://www.filmon.com' + regex_from_to(streamerlink, '"streamer":"', '",').replace("\/", "/")
    slink = open_url('http://www.filmon.com/api/init/')
    smatch= re.compile('"session_key":"(.+?)"').findall(slink)
    session_id=smatch[0]
    utc_now = datetime.datetime.now()
    net.set_cookies(cookie_jar)
    url='http://www.filmon.com/api/channel/%s?session_key=%s' % (description,session_id)
    link = net.http_GET(url).content
    link = json.loads(link)
    link = str(link)
    streams = regex_from_to(link, "streams'", "u'tvguide")
    hl_streams = regex_get_all(streams, '{', '}')
    url = regex_from_to(hl_streams[1], "url': u'", "',")
    name = regex_from_to(hl_streams[1], "name': u'", "',")
    try:
        timeout = regex_from_to(hl_streams[1], "watch-timeout': u'", "',")
    except:
        timeout = '86500'
    #name = name.replace('low', 'high')
    if name.endswith('m4v'):
        app = 'vodlast'
    else:
        appfind = url[7:].split('/')
        app = 'live/' + appfind[2]
		
    if url.endswith('/'):
        STurl = str(url) + ' playpath=' + name + ' swfUrl=' + swfplay + ' tcUrl='+ str(url) + ' pageUrl=http://www.filmon.com/' + ' live=1 timeout=45 swfVfy=1'
        STurl2 = str(url)  + name + ' playpath=' + name + ' swfUrl=' + swfplay + ' tcUrl='+ str(url) + ' pageUrl=http://www.filmon.com/' + ' live=1 timeout=45 swfVfy=1'
    else:
        STurl = str(url) + ' playpath=' + name + ' app=' + app + ' swfUrl=' + swfplay + ' tcUrl='+ str(url) + ' pageUrl=http://www.filmon.com/' + ' live=1 timeout=45 swfVfy=1'
        STurl2 = str(url) + '/' + name + ' playpath=' + name + ' app=' + app + ' swfUrl=' + swfplay + ' tcUrl='+ str(url) + ' pageUrl=http://www.filmon.com/' + ' live=1 timeout=45 swfVfy=1'
    return STurl2

class Base36:

    def __init__(self, ls = False):
        self.ls = False
        if ls:
            self.ls = ls

    def base36encode(self, number, alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
        """Converts an integer to a base36 string."""
        if not isinstance(number, (int, long)):
            raise TypeError('number must be an integer')
        base36 = ''
        sign = ''
        if number < 0:
            sign = '-'
            number = -number
        if 0 <= number < len(alphabet):
            return sign + alphabet[number]
        while number != 0:
            number, i = divmod(number, len(alphabet))
            base36 = alphabet[i] + base36

        return sign + base36

    def base36decode(self, number):
        return int(number, 36)

    def param36decode(self, match_object):
        if self.ls:
            param = int(match_object.group(0), 36)
            return str(self.ls[param])
        else:
            return False


def unpack_js(p, k):
    """emulate js unpacking code"""
    k = k.split('|')
    for x in range(len(k) - 1, -1, -1):
        if k[x]:
            p = re.sub('\\b%s\\b' % Base36().base36encode(x), k[x], p)

    return p


def exec_javascript(lsParam):
    return re.sub('[a-zA-Z0-9]+', Base36(lsParam[3]).param36decode, str(lsParam[0]))


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


class europe_parsers:

    def __init__(self):
        self.quality = ''
        self.net = Net()

    def get_parsed_link(self, url):
        try:
            if url.find('embed.divxstage') > -1 or url.find('embed.movshare') > -1 or url.find('embed.nowvideo') > -1 or url.find('embed.novamov') > -1 or url.find('embed.youwatch') > -1 or url.find('embed.vodlocker') > -1 or url.find('embed.sharevid') > -1 or url.find('embed.sharerepo') > -1 or url.find('embed.played') > -1:
                url = url.replace('http://embed.','http://www.')	
                url = url.replace('embed.php?v=','video/')				
            if url.find('nowvideo.sx') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    key = re.compile('flashvars.filekey=(.+?);').findall(page)
                    ip_key = key[0]
                    pattern = 'var %s="(.+?)".+?flashvars.file="(.+?)"' % str(ip_key)
                    r = re.search(pattern, page, re.DOTALL)
                    if r:
                        filekey, filename = r.groups()
                    else:
                        print 'errrrroor nowvideo'
                    api = 'http://www.nowvideo.sx/api/player.api.php?key=%s&file=%s' % (filekey, filename)
                    request2 = urllib2.Request(api, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                     'Connection': 'Close'})
                    try:
                        html = urllib2.urlopen(request2).read()
                        code = re.findall('url=(.*?)&title', html)
                        code = code[0]
                        if len(code) > 0:
                            url = code
                    except:
                        print 'nowvideo api error'

                except Exception as ex:
                    print ex

            if url.find('movshare.net') > -1:
                page = mod_request(url)
                r = re.search('<param name="src" value="(.+?)"', page)
                if not r:
                    key = re.compile('flashvars.filekey=".*?-(.+?)";').findall(page)
                    filekey = key[0]
                    key2 = re.compile('flashvars.file="(.*?)";').findall(page)
                    media_id = key2[0]
                    api = 'http://www.movshare.net/api/player.api.php?key=%s&file=%s' % (filekey, media_id)
                    try:
                        html = mod_request(api)
                        r = re.search('url=(.+?)&title', html)
                    except:
                        print 'movshare errorrrrrrrrr'

                if r:
                    stream_url = r.group(1)
                url = stream_url
            if url.find('videoweed.es') > -1:
                url = url.find('video','file')
                page = mod_request(url)
                key = re.compile('flashvars.filekey=".*?-(.+?)";').findall(page)
                filekey = key[0]
                key2 = re.compile('flashvars.file="(.*?)";').findall(page)
                media_id = key2[0]
                api_call = ('http://www.videoweed.es/api/player.api.php?user=undefined&codes=1&file=%s' + '&pass=undefined&key=%s') % (media_id, filekey)
                try:
                    html = mod_request(api_call)
                    r = re.search('url=(.+?)&title', html)
                except:
                    print 'videoweed errorrrrrrrrr'

                if r:
                    stream_url = r.group(1)
                url = stream_url
            if url.find('novamov.com') > -1:
                page = mod_request(url)
                key = re.compile('flashvars.filekey=".*?-(.+?)";').findall(page)
                filekey = key[0]
                key2 = re.compile('flashvars.file="(.*?)";').findall(page)
                media_id = key2[0]
                api = 'http://www.novamov.com/api/player.api.php?key=%s&file=%s' % (filekey, media_id)
                try:
                    html = mod_request(api)
                    r = re.search('url=(.+?)&title', html)
                except:
                    print 'novamov errorrrrrrrrr'

                if r:
                    stream_url = r.group(1)
                url = stream_url
            if url.find('divxstage.to') > -1:
                page = mod_request(url)
                key = re.compile('flashvars.filekey=".*?-(.+?)";').findall(page)
                filekey = key[0]
                key2 = re.compile('flashvars.file="(.*?)";').findall(page)
                media_id = key2[0]
                api = 'http://www.divxstage.eu/api/player.api.php?user=undefined&key=' + filekey + '&pass=undefined&codes=1&file=' + media_id
                try:
                    html = mod_request(api)
                    r = re.search('url=(.+?)&title', html)
                except:
                    print 'divxstage errorrrrrrrrr'

                if r:
                    stream_url = r.group(1)
                url = stream_url
            if url.find('youwatch.org') > -1:
                #url = url.replace('.org/', '.org/embed-')
                url = url
                soup = mod_request(url)
                html = soup.decode('utf-8')
                jscript = re.findall('function\\(p,a,c,k,e,d\\).*return p\\}(.*)\\)', html)
                if jscript:
                    lsParam = eval(jscript[0].encode('utf-8'))
                    flashvars = exec_javascript(lsParam)
                    r = re.findall('file:"(.*)",provider', flashvars)
                    if r:
                        stream_url = r[0].encode('utf-8')
                url = stream_url
            if url.find('vodlocker.com') > -1:
                url = url.find('embed\-','')
                url = url.find('\-640x360.html','')
                post_url = url
                resp = self.net.http_GET(url)
                html = resp.content
                data = {}
                r = re.findall('type="hidden" name="(.+?)"\\s* value="?(.+?)">', html)
                data['usr_login'] = ''
                for name, value in r:
                    data[name] = value

                data['imhuman'] = 'Proceed to video'
                data['btn_download'] = 'Proceed to video'
                sleep(20)
                html = self.net.http_POST(post_url, data).content
                r = re.search('file\\s*:\\s*"(http://.+?)"', html)
                if r:
                    stream_url = str(r.group(1))
                url = stream_url
            if url.find('vidto.me') > -1:
                url = url.find('embed\-','')
                url = url.find('\-640x360.html','')
                print '39'
                print url
                html = self.net.http_GET(url).content
                sleep(6)
                data = {}
                r = re.findall('type="(?:hidden|submit)?" name="(.+?)"\\s* value="?(.+?)">', html)
                for name, value in r:
                    data[name] = value

                html = self.net.http_POST(url, data).content
                r = re.search('<a id="lnk_download" href="(.+?)"', html)
                if r:
                    r = re.sub(' ', '%20', r.group(1))
                    url2 = r
                url = url2
            if url.find('sharevid.org') > -1:
                html = self.net.http_GET(url).content
                data = {}
                r = re.findall('type="hidden" name="(.+?)"\\s* value="?(.+?)">', html)
                for name, value in r:
                    data[name] = value

                html = self.net.http_POST(url, data).content
                r = re.search("file\\s*:\\s*'(.+?)'", html)
                if r:
                    url2 = r.group(1)
                url = url2
            if url.find('sharerepo.com') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code = re.findall("var lnk1 = '(.*?)';", page)
                    if len(code) > 0:
                        md5hash = code[0]
                        url = md5hash
                except Exception as ex:
                    print ex

            if url.find('allmyvideos.net') > -1:
                html = self.net.http_GET(url).content
                data = {}
                r = re.findall('type="hidden" name="(.+?)"\\s* value="?(.+?)">', html)
                for name, value in r:
                    data[name] = value

                html = self.net.http_POST(url, data).content
                r = re.search('"sources"\\s*:\\s*.\n*\\s*.\n*\\s*"file"\\s*:\\s*"(.+?)"', html)
                if r:
                    url = r.group(1)
            if url.find('played.to') > -1:
                web_url = url
                html = self.net.http_GET(web_url, {'host': 'played.to'}).content
                id = re.compile('<input type="hidden" name="id" value="(.+?)">').findall(html)[0]
                fname = re.compile('<input type="hidden" name="fname" value="(.+?)">').findall(html)[0]
                hash = re.compile('<input type="hidden" name="hash" value="(.+?)">').findall(html)[0]
                data = {'op': 'download1',
                 'usr_login': '',
                 'id': id,
                 'fname': fname,
                 'referer': '',
                 'hash': hash,
                 'imhuman': 'Continue+to+Video'}
                html = self.net.http_POST(web_url, data).content
                played = re.compile('file: "(.+?)"').findall(html)
                url = played[0]
            if url.find('gorillavid.in') > -1:
                web_url = url
                resp = self.net.http_GET(web_url)
                html = resp.content
                r = re.findall('<title>404 - Not Found</title>', html)
                if r:
                    print 'File Not Found or removed'
                form_values = {}
                for i in re.finditer('<input type="hidden" name="(.+?)" value="(.+?)">', html):
                    form_values[i.group(1)] = i.group(2)

                html = self.net.http_POST(web_url, form_data=form_values).content
                r = re.search('file: "(.+?)"', html)
                if r:
                    url = r.group(1)
         
            if url.find('ecostream.tv') > -1:
                #c = '/tmp/ecostream_cookie'
                r = re.search('\\/stream\\/(.*?)\.ht',url)
                media_id = r.group(1)
                web_url = url
                html = Net().http_GET(web_url).content
                if re.search('>File not found!<',html):
                    msg = 'File Not Found or removed'
                    print msg
                Net().save_cookies(cookie_jar)
                web_url = 'http://www.ecostream.tv/js/ecoss.js'
                js = Net().http_GET(web_url).content
                r = re.search("\$\.post\('([^']+)'[^;]+'#auth'\).html\(''\)", js)
                if not r:
                    print 'Posturl not found'
                post_url = r.group(1)
                r = re.search('data\("tpm",([^\)]+)\);', js)
                if not r:
                    print 'Postparameterparts not found'
                post_param_parts = r.group(1).split('+')
                found_parts = []
                for part in post_param_parts:
                    pattern = "%s='([^']+)'" % part.strip()
                    r = re.search(pattern, html)
                    if not r:
                        print 'Formvaluepart not found'            
                    found_parts.append(r.group(1))
                tpm = ''.join(found_parts)            
                # emulate click on button "Start Stream"
                postHeader = ({'Referer':web_url, 'X-Requested-With':'XMLHttpRequest'})
                web_url = 'http://www.ecostream.tv' + post_url
                Net().set_cookies(cookie_jar)
                html = Net().http_POST(web_url,{'id':media_id, 'tpm':tpm}, headers = postHeader).content
                sPattern = '"url":"([^"]+)"'
                r = re.search(sPattern, html)
                if not r:
                    print 'Unable to resolve Ecostream link. Filelink not found.'
                sLinkToFile = urllib2.quote(r.group(1))
                url = 'http://cscvod.ru/ecostream.php?url=' + sLinkToFile
            
            if url.find('filmon.com') > -1:
                url = filmon_play(url)
			
        except Exception as ex:
            print ex
            print 'sgparsed_international_link'

        return url