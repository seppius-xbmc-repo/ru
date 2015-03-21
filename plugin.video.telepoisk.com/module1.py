import re, os, urllib, urllib2, cookielib, time, sys, urlparse
from time import gmtime, strftime

import datetime

try:
    import json
except ImportError:
    try:
        import simplejson as json
        print( '[%s]: Error import json. Uses module simplejson' % addon_id, 2 )
    except ImportError:
        try:
            import demjson3 as json
            print( '[%s]: Error import simplejson. Uses module demjson3' % addon_id, 3 )
        except ImportError:
           print( '[%s]: Error import demjson3. Sorry.' % addon_id, 4 )


fcookies = os.path.join(os.getcwd(), r'cookies.txt')

# load XML library
sys.path.append(os.path.join(os.getcwd(), r'resources', r'lib'))
from BeautifulSoup  import BeautifulSoup

import HTMLParser
hpar = HTMLParser.HTMLParser()

#---------- get web page -------------------------------------------------------
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
           xbmc.log('We failed to reach a server.')
        elif hasattr(e, 'code'):
           xbmc.log('The server couldn\'t fulfill the request.')

    html = f.read()

    return html

#===============================================================================

url = 'http://telepoisk.com/peredacha-tv-archiv/2030722/16-11-2012'

html = get_HTML(url)

rec = re.compile("jwplayer\('mediaspace'\).setup\({(.+?)}\);", re.MULTILINE|re.DOTALL).findall(html)[0]

str =  '{'+rec.replace('\n','').replace(' ','').replace('\'','"')+'}'

j1 = json.loads(str)

v_server = j1['streamer']
v_swf    = j1['flashplayer']
v_stream = j1['file'][:-4]

video = '%s app=file swfUrl=http://tvisio.tv%s pageUrl=%s playpath=%s swfVfy=1' % (v_server, v_swf, url, v_stream)

print video
'''
rtmpdump
    -r "rtmp://94.242.214.190:1935/file"
    -a "file" -f "WIN 11,4,402,287"
    -W "http://telepoisk.com/jwplayer/player.swf"
    -p "http://telepoisk.com/peredacha-tv-archiv/2030722/16-11-2012"
    -y "Edge-1/sdb/records_2030/aoz02S10STg12eUoijfx8mynkjWg5s"
    -o aoz02S10STg12eUoijfx8mynkjWg5s.flv


<script type='text/javascript'>
                jwplayer('mediaspace').setup({
                    'flashplayer': '/jwplayer/player.swf',
                    'file': 'Edge-1/sdb/records_2030/aoz02S10STg12eUoijfx8mynkjWg5s.flv',
                    'streamer': 'rtmp://94.242.214.190:1935/file',

                    'autostart': 'true',
                    'icons': 'true',
                    'quality': 'fale',
                    'dock': 'false',
                    'controlbar': 'bottom',
                    'width': '640',
                    'height': '390'
                });
            </script>



'''