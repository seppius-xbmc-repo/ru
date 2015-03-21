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

url = 'http://telik.in.ua/rossija1'
html = get_HTML(url)
soup = BeautifulSoup(html)

url = soup.find('iframe')['src']
html = get_HTML(url)
soup = BeautifulSoup(html)

url1 = soup.find('embed')['src']
html = get_HTML(url1, None, url)
print html
soup = BeautifulSoup(html)