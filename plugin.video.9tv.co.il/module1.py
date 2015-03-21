import re, os, urllib, urllib2, cookielib, time, random, sys
from time import gmtime, strftime
import urlparse

fcookies = 'cookies.txt'

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

url = 'http://9tv.co.il/video/2014/02/17/46538.html'
html = get_HTML(url)
soup = BeautifulSoup(html, fromEncoding="windows-1251")

for rec in soup.findAll("div", {"class":"blockV"}):
    print rec
    print rec.find('a')['href']
    for t in rec.findAll('a'):
        print '---'
        print t.text
    print rec.find('img')['src']
    print rec.find('span', {'class':'date'}).text
    print ' '

'''
for rec in soup.findAll('param', {'name':'flashvars'}):
    print rec
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

    print oid
    print vid

for rec in soup.findAll('iframe', {'src' : re.compile('video_ext.php\?')}):
    print rec['src']

for rec in soup.findAll('param', {'name':'flashvars'}):
   for s in rec['value'].split('&'):
    if s.split('=',1)[0] == 'file':
        print s.split('=',1)[1]

'''