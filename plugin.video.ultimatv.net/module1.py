import re, os, urllib, urllib2, cookielib, time, random, sys
from time import gmtime, strftime
import urlparse

fcookies = 'cookies.txt'

import demjson3 as json

# load XML library

sys.path.append(os.path.join(os.getcwd(), r'resources', r'lib'))
from BeautifulSoup  import BeautifulSoup

# get cookies from last session
cj = cookielib.MozillaCookieJar(fcookies)
hr  = urllib2.HTTPCookieProcessor(cj)
opener = urllib2.build_opener(hr)
urllib2.install_opener(opener)

def get_HTML(url, post = None, ref = None):
    request = urllib2.Request(url, post)

    host = urlparse.urlsplit(url).hostname
    if ref==None:
        ref='http://'+host

    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host',   host)
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Language', 'ru-RU')
    request.add_header('Referer',             ref)

    try:
        f = urllib2.urlopen(request)
    except IOError, e:
        if hasattr(e, 'reason'):
           print 'We failed to reach a server.'
        elif hasattr(e, 'code'):
           print 'The server couldn\'t fulfill the request.'

    html = f.read()

    return html

#-------------------------------------------------------------------------------
post = None
url = 'http://www.cn.ru/tv/xml/1/channels/?' # 'http://www.cn.ru/tv/xml/1/schedule/?channel=19343529'
html = get_HTML(url, post)

print html

'''
soup = BeautifulSoup(html, fromEncoding="utf-8")

url = soup.find('iframe')['src']


html = get_HTML(url, post)
#print html
soup = BeautifulSoup(html, fromEncoding="utf-8")

f_str = soup.find('param',{'name':'flashVars'})['value']
for rec in f_str.split('&'):
    if rec.split('=')[0] == 'videoid':
        varsideoid = rec.split('=')[1]
    if rec.split('=')[0] == 'sessid':
        sessid = rec.split('=')[1]

url = 'http://clients.cdnet.tv/flashplayer/instruction.php?' + soup.find('object').find('param',{'name':'flashVars'})['value'].replace('videotype=','type=')
html = get_HTML(url, post)
#print html
soup = BeautifulSoup(html, fromEncoding="utf-8")
stream_sd = soup.find('root')['stream_hd']
chanel_sd = soup.find('root')['chanel_hd']

video = 'rtmpdump -r "'+stream_sd+'/'+chanel_sd+'" -p http://clients.cdnet.tv/flashbroadcast.php?channel='+varsideoid+' -W http://clients.cdnet.tv/flashplayer/player.swf -f "WIN 11,4,402,287" -T "Ys#QBn%3O0@l1" -o TesT.flv'

print video


#-- userid=0&              videoid=1042&         videotype=stream&   sessid=ae570789943d61a78413c78bde9dd6a3

#-- ?userid=" + param1 + "&videoid=" + param2 + "&type=" + param3 + "&sessid=" + param4

-a app: 42
-f flahVer: WIN 11,4,402,287
-s swfUrl: http://clients.cdnet.tv/flashplayer/player.swf
-t tcUrl: rtmpe://94.242.221.71/42
-p pageUrl: http://clients.cdnet.tv/flashbroadcast.php?channel=1042&session=...
-y Playpath: channel_42.stream


rtmpdump -r "rtmp://94.242.221.71/42" -a "42" -f "11,4,402,287" -W "http://clients.cdnet.tv/flashplayer/player.swf" -p "http://clients.cdnet.tv/flashbroadcast.php?channel=1042&session=6c2c533332f2b4b00401377952e78afc" -y "channel_42.stream" -o -TesT.flv


rtmpdump -r "rtmpe://94.242.221.71/42/channel_42.stream" -p http://clients.cdnet.tv/flashbroadcast.php?channel=1042 -W http://clients.cdnet.tv/flashplayer/player.swf -f "WIN 11,4,402,287" -T "Ys#QBn%3O0@l1" -o TesT.flv

'''



















