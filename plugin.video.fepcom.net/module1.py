import urllib, urllib2, json, sys, os, cookielib, re
import urlparse

import gzip, StringIO, zlib

try:
    from hashlib import md5 as md5
except:
    import md5

sys.path.append(os.path.join(os.getcwd(), r'resources', r'lib'))
from BeautifulSoup  import BeautifulSoup
from Data import Data

import HTMLParser
hpar = HTMLParser.HTMLParser()

#-- system functions -----------------------------------------------------------
def unescape(text):
    try:
        text = hpar.unescape(text)
    except:
        text = hpar.unescape(text.decode('utf8'))

    try:
        text = unicode(text, 'utf-8')
    except:
        text = text

    return text.strip()

def f_md5(str):
    try:
        rez = md5(str)
    except:
        rez = md5.md5(str)
    return rez

#---------------------- HTML request -----------------------------------------
def get_HTML(url, post = None, ref = None, get_url = False):
    request = urllib2.Request(url, post)
    host = urlparse.urlsplit(url).hostname
    if ref==None:
        ref='http://'+host

    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host',   host)
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Language', 'ru-RU')
    request.add_header('Accept-Encoding', 'gzip')
    request.add_header('Referer',             ref)

    is_OK = False
    try:
        f = urllib2.urlopen(request, timeout=240)
        is_OK = True
    except IOError, e:
        is_OK = False
        if hasattr(e, 'reason'):
           print e.reason #'ERROR: '+e.reason
           xbmc.executebuiltin('Notification(SEASONVAR.ru,%s,5000,%s)'%(e.reason.capitalize(), os.path.join(Addon.getAddonInfo('path'), 'warning.jpg')))
           #---
           if HTML_retry < 3:
               xbmc.sleep(2000)
               HTML_retry = HTML_retry+1
               return get_HTML(url, post, ref, get_url)

        elif hasattr(e, 'code'):
           print 'The server couldn\'t fulfill the request.'

    if is_OK == True:
        if get_url == True:
            html = f.geturl()
        else:
            html = f.read()
            #--
            if f.headers.get('content-encoding', '') == 'gzip':
                html = StringIO.StringIO(html)
                gzipper = gzip.GzipFile(fileobj=html)
                html = gzipper.read()
            elif f.headers.getheader("Content-Encoding") == 'deflate':
                html = zlib.decompress(html)



    return html

#------ get movie detail info --------------------------------------------------
def Load_Page(url, i_rubric, data):

    #-- get movie info
    html = get_HTML(url)
    #-- parsing web page
    soup = BeautifulSoup(html, fromEncoding="windows-1251")
    #-- check if page have video
    if len(soup.findAll('object', {'type':'application/x-shockwave-flash'})) < 1:
        return

    #-- get movie info
    rec = soup.find('div', {'class' : 'post'})

    #-- get image
    try:
        i_image = rec.find('div', {'class' : 'post_content'}).find('img')['src']
    except:
        try:
            i_image = re.compile('src="(.+?)"', re.MULTILINE|re.DOTALL).findall(str(rec.find('div', {'class' : 'post_content'}).find('img')))
        except:
            print '**** IMG!!'
            return empty
    if i_image.find('http://') == -1:
        i_image = 'http://fepcom.net'+i_image

    #-- get name
    i_name = unescape(rec.find('h1').text)
    #-- get url
    i_url = url

    #-- get movie info
    info = rec.find('div', {'class' : 'post_content'})

    o_name      = '-'
    i_year      = '-'
    i_country   = '-'
    i_genre     = '-'
    i_director  = '-'
    i_actors    = '-'
    i_text      = '-'

    for inf in info.findAll("strong"):
        header = inf.text.replace(':', '').encode('utf-8')
        if header == 'Оригинальное название':
            o_name = unescape(str(inf.nextSibling).strip())
        elif header == 'Год выхода на экран':
            i_year = unescape(str(inf.nextSibling).strip())
        elif header == 'Страна':
            i_country = unescape(str(inf.nextSibling).strip())
        elif header == 'Фильм относится к жанру':
            i_genre = unescape(str(inf.nextSibling).strip())
        elif header == 'Постановщик':
            i_director = unescape(str(inf.nextSibling).strip())
        elif header == 'Актеры, принявшие участие в съемках':
            i_actors = unescape(str(inf.nextSibling).strip())
        elif header == 'Краткое описание':
            i_text = unescape(str(inf.nextSibling))

    if i_name == o_name:
        o_name = ''

    full_text = i_text
    if o_name != '':
        full_text = full_text+(u'\nОригинальное название: ')+o_name
    if i_actors != '':
        full_text = full_text+(u'\nАктеры: ')+i_actors

    movie_id = f_md5((i_name + i_year).encode('utf-8')).hexdigest()
    movie = (movie_id, i_name, o_name, i_url, i_year, i_director, i_actors, i_country.title(), i_text, i_image, i_genre.title(), i_rubric)

    if data.is_Serial_exist(movie_id) == False:
        data.add_Serial(movie)

        for c in i_country.replace('-',',').replace('/',',').replace('.',',').title().split(','):
            data.add_Country(c.strip())

        for g in i_genre.title().split(','):
            data.add_Genre(g.strip())

        print i_name


#------ process page -----------------------------------------------------------
def Update(url, i_rubric, data):

    print '============   '+i_rubric+'   ============================'

    max_page = get_Number_of_Pages(url)

    for page in range(1, max_page+1):
        print 'PAGE '+str(page)+' ----------------------------'
        page_url = url+'/page/'+str(page)+'/'
        html = get_HTML(page_url)
        # -- parsing web page --------------------------------------------------
        soup = BeautifulSoup(html, fromEncoding="windows-1251")

        for rec in soup.findAll('div', {'class':'short_post_link'}):
            try:
                Load_Page(rec.find('a')['href'], i_rubric, data)
            except:
                pass

#------ get number of pages ----------------------------------------------------
def get_Number_of_Pages(url):
    html = get_HTML(url)
    # -- parsing web page --------------------------------------------------
    soup = BeautifulSoup(html, fromEncoding="windows-1251")

    page = 1

    for rec in soup.find('div', {'class':'navigation'}).findAll('a'):
        try:
            if int(rec.text) > page:
                page = int(rec.text)
        except:
            pass

    return page

#-------------------------------------------------------------------------------

db_file = os.path.join(os.getcwd(), r'resources', r'data', r'fepcom_net.db3')
kwargs={'DB': db_file}
x_data = Data(**kwargs)

url = 'http://fepcom.net/filmy-onlajn/'
rubric_ = u'Фильмы'
Update(url, rubric_, x_data)

url = 'http://fepcom.net/dokumentalnoe-kino/'
rubric_ = u'Документальное кино'
Update(url, rubric_, x_data)

url = 'http://fepcom.net/retro-onlajn/'
rubric_ = u'Ретро кино'
Update(url, rubric_, x_data)

url = 'http://fepcom.net/yumor/'
rubric_ = u'Юмор'
Update(url, rubric_, x_data)



