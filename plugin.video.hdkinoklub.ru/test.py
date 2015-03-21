
import re, os, urllib, urllib2, cookielib, time, sys
from time import gmtime, strftime
from subprocess import Popen, PIPE, STDOUT
import urlparse, json

fcookies = 'cookies.txt'

sys.path.append(os.path.join(os.getcwd(), r'resources', r'lib'))
from BeautifulSoup  import BeautifulSoup

import HTMLParser
hpar = HTMLParser.HTMLParser()

# get cookies from last session
cj = cookielib.MozillaCookieJar(fcookies)
hr  = urllib2.HTTPCookieProcessor(cj)
opener = urllib2.build_opener(hr)
urllib2.install_opener(opener)


#---------- get web page -------------------------------------------------------
def get_HTML(url, post = None, ref = None, l = None):
    request = urllib2.Request(url, post)

    host = urlparse.urlsplit(url).hostname
    if ref==None:
        ref='http://'+host

    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host',   host)
    request.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
    request.add_header('Accept-Language', 'ru-RU')
    request.add_header('Referer',             ref)

    request.add_header('Accept-Encoding', 'gzip,deflate,sdch')

    request.add_header('Cache-Control', 'max-age=0')
    request.add_header('Connection', 'keep-alive')
    #print len(post)
    #s = len(post)
    #request.add_header('Content-Length', s)
    request.add_header('Content-Type', 'application/x-www-form-urlencoded')

    try:
        f = urllib2.urlopen(request)
    except IOError, e:
        if hasattr(e, 'reason'):
           print 'We failed to reach a server.'
        elif hasattr(e, 'code'):
           print 'The server couldn\'t fulfill the request.'

    if l == None:
        html = f.read()
    else:
        html = f.read(l)

    return html


#-------------------------------------------------------------------------------
##js_code = """eval(function(p,a,c,k,e,d){e=function(c){return(c<a?'':e(parseInt(c/a)))+((c=c%a)>35?String.fromCharCode(c+29):c.toString(36))};if(!''.replace(/^/,String)){while(c--){d[e(c)]=k[c]||e(c)}k=[function(e){return d[e]}];e=function(){return'\\w+'};c=1};while(c--){if(k[c]){p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c])}}return p}('1 h="-o";1 w="z";1 s="r";1 q="p-t.y";1 x="6";1 5=\'<7 v="9://2.3/a/m/i/6" b="j" d="n" k="0" l></7>\';1 u=\'\';1 S=\'2.3\';1 O=\'9://2.3\';1 g;A M(c,4){P(\'Q\').U({T:4,R:{8:5,L:\'K a 8\'},E:"D",C:"B",F:e,G:e,J:\'I\',H:c,b:\'f%\',d:"f%"});g=N}',57,57,'|var|kodik|biz|files|videoCode|720p|iframe|code|http|video|width|posters|height|false|100|player_ready|s1|69a2883bb5d200b9fb4ae47948586417|607|frameborder|AllowFullScreen|3082|360|77446475|video153|player|d834549405a0d3a3|s3|1453|clickUnder|src|s2|quality|txt|170403208|function|flash|primary|start|startparam|fallback|stagevideo|image|glow|skin|Get|heading|createPlayer|true|url|jwplayer|videoplayer|sharing|domain|sources|setup'.split('|'),0,{})); console.log("http://api.vk.com/method/video.getEmbed?oid=" + s1 + "&video_id=" + s2 + "&embed_hash=" + s3 + "&callback=responseWork");"""

f1 = open(os.path.join(os.getcwd(),'code.txt'), 'r')
js_code = f1.read()
f1.close()

js_code = js_code + ';"http://api.vk.com/method/video.getEmbed?oid=" + s1 + "&video_id=" + s2 +"&embed_hash=" + s3 +"&callback=responseWork";'

node_js = os.path.join(os.getcwd(), r'node.exe')

p = Popen([node_js, '-p'], stdout=PIPE, stdin=PIPE, stderr=PIPE)
rez = p.communicate(input = js_code)

print rez

'''
url = 'http://hdkinoklub.ru'
html = get_HTML(url)

url = 'http://hdkinoklub.ru/index.php?do=search'
str = ('earth').encode('windows-1251')
values = {
        'do'	        : 'search',
        'subaction'	    : 'search',
        'search_start'	: 1,
        'full_search'	: 1,
        'result_from'	: 1,
        'story'         : 'earth',
        'titleonly'	    : 3,
        'searchuser'    : '',
        'replyless'	    : 0,
        'replylimit'	: 0,
        'searchdate'	: 0,
        'beforeafter'	: 'after',
        'sortby'	    : 'title',
        'resorder'	    : 'asc',
        'showposts'	    : 0,
        'catlist[]'	    : 0
    }

post = urllib.urlencode(values)
html = get_HTML(url, post, url)
print html
'''