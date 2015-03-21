import re, os, urllib, urllib2, cookielib, time, sys
from time import gmtime, strftime
import urlparse
import demjson3

# load XML library
sys.path.append(os.path.join(os.getcwd(), r'resources', r'lib'))
from BeautifulSoup  import BeautifulSoup

fcookies = os.path.join(os.getcwd(), r'cookies.txt')

import HTMLParser
hpar = HTMLParser.HTMLParser()


def unescape(text):
    try:
        text = hpar.unescape(text)
    except:
        text = hpar.unescape(text.decode('utf8'))

    try:
        text = unicode(text, 'utf-8')
    except:
        text = text

    return text

#---------- get web page -------------------------------------------------------
def get_HTML(url, post = None, ref = None):
    print url
    request = urllib2.Request(url, post)

    host = urlparse.urlsplit(url).hostname
    if ref==None:
        try:
           ref='http://'+host
        except:
            ref='localhost'

    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host',   host)
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Language', 'ru-RU')
    request.add_header('Referer',             ref)
    request.add_header('X-Requested-With','XMLHttpRequest')
    request.add_header('Content-Type','application/x-www-form-urlencoded')

    try:
        f = urllib2.urlopen(request)
    except IOError, e:
        if hasattr(e, 'reason'):
           print('We failed to reach a server.')
        elif hasattr(e, 'code'):
           print('The server couldn\'t fulfill the request.')

    html = f.read()

    return html

#-------------------------------------------------------------------------------
def Decode(param):
    #-- define variables
    loc_3 = [0,0,0,0]
    loc_4 = [0,0,0]
    loc_2 = ''
    #-- define hash parameters for decoding
    dec = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='
    hash1 = ["Z", "v", "6", "W", "m", "y", "g", "X", "b", "o", "V", "d", "k", "t", "M", "Q", "u", "5", "D", "e", "J", "s", "z", "f", "L", "="];
    hash2 = ["a", "G", "9", "w", "1", "N", "l", "T", "I", "R", "7", "2", "n", "B", "4", "H", "3", "U", "0", "p", "Y", "c", "i", "x", "8", "q"];

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
            if loc_3[j + 1] == 64:
                break
            try:
                loc_2 += unichr(loc_4[j])
            except:
                pass
            j = j + 1

        i = i + 4;

    return loc_2

#-------------------------------------------------------------------------------

# get cookies from last session
cj = cookielib.FileCookieJar(fcookies)
hr  = urllib2.HTTPCookieProcessor(cj)
opener = urllib2.build_opener(hr)
urllib2.install_opener(opener)

#-- get movie detail
url  = 'http://docu.im/movie/play/381' #339
html = get_HTML(url).replace("<span class='heading'>", "|<span class='heading'>").replace('<p>', '|Text:<p>')
soup = BeautifulSoup(html, fromEncoding="utf-8")

movie_id = soup.find('div', {'class':'player-wrapper'}).find('div', {'id':'player'})['movie-id']
video_id = soup.find('div', {'class':'player-wrapper'}).find('div', {'id':'player'})['video-id']

try:
    if len(soup.find('div', {'id':'season-switch-items'})) > 0:
        is_Serial = True
    else:
        is_Serial = False
except:
    is_Serial = False

if is_Serial == True:
    for rec in soup.find('div', {'id':'season-switch-items'}).findAll('div', {'class':'switch-item'}):
        season_name = rec.find('a').text
        season_id = rec.find('a').text.replace(u'сезон', '').replace(u'Сезон', '').replace(u' ', '')

        url  = 'http://docu.im/movie/player/%s/playlist.txt?season=%s'%(movie_id, season_id)
        html = get_HTML(url)

        info = Decode(html)

        rec = demjson3.loads(info)

        try:
            rec = demjson3.loads(rec['pl'])
        except:
            pass

        for t in rec['playlist']:
            print season_name+'  '+t['comment']
            print t['file']
            print ' '
else:
    url  = 'http://docu.im/movie/player/%s/style.txt'%(movie_id)
    html = get_HTML(url)

    info = Decode(html)

    rec = demjson3.loads(info)
    rec = demjson3.loads(rec['pl'])

    for t in rec['playlist']:
        print t['comment']
        print t['file']
        print ' '

'''

mp4:DRWIBma6yreJrYl4QJSuZH8XAO7iNz5qq?audioIndex=0&wmsAuthSign=c2VydmVyX3RpbWU9MTEvMjkvMjAxMiAzOjIwOjAyIEFNJmhhc2hfdmFsdWU9c05zUTNObVdsSnlSKys1OXV2OHd0dz09JnZhbGlkbWludXRlcz0zMA==
mp4:DRWIBma6yreJrYl4QJSuZH8XAO7iNz5qq,j4Eoa6Kqrubh9b1KCBSnPDgPDYSH0IYsL]?audioIndex={0;1}&wmsAuthSign=c2VydmVyX3RpbWU9MTEvMjkvMjAxMiAzOjUwOjA5IEFNJmhhc2hfdmFsdWU9Zk9WS2pSYzV2MGVOMnRvVE5xWFM3UT09JnZhbGlkbWludXRlcz0zMA==\",\"id\":\"2590\",\"sub\":\"/


rtmp://video.docu.im:1935/docu app=docu swfUrl=http://docu.im/player/uppod.swf pageUrl=http://docu.im/movie/play/428 playpath=mp4:SOCwzw8Y7guC7UFoukCGk6gmGgchlSmeH?audioIndex=0&wmsAuthSign=c2VydmVyX3RpbWU9MTEvMjkvMjAxMiA5OjUxOjM3IFBNJmhhc2hfdmFsdWU9ZmNaczdNQ3pRSCs2d2NYR2NabkUrUT09JnZhbGlkbWludXRlcz0zMA==


rtmpdump    -r "rtmp://video.docu.im:1935/docu"    -a "docu"    -f "WIN 11,4,402,287"    -W "http://docu.im/player/uppod.swf"    -p "http://docu.im/movie/play/428"    -y "mp4:SOCwzw8Y7guC7UFoukCGk6gmGgchlSmeH?audioIndex=0&wmsAuthSign=c2VydmVyX3RpbWU9MTEvMjkvMjAxMiA5OjUxOjM3IFBNJmhhc2hfdmFsdWU9ZmNaczdNQ3pRSCs2d2NYR2NabkUrUT09JnZhbGlkbWludXRlcz0zMA=="    -o mp4_test.flv

'''