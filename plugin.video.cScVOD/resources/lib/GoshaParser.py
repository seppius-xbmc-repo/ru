# Embedded file name: /usr/lib/enigma2/python/Plugins/Extensions/nStreamVOD/nStreamGoshaParser.py
import re
import urllib2
import urllib

class gosha_parsers:

    def __init__(self):
        self.quality = ''

    def get_parsed_link(self, url):
        try:
            if url.find('//kino-v-online.tv/kino/md5') > -1 or url.find('//kino-v-online.tv/serial/md5') > -1 or url.find('?st=1') > -1:
                url1 = 'http://kino-v-online.tv/2796-materik-online-film.html'
                request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    hash_list = re.findall('/kino/(.*?)/', page)
                    if len(hash_list) > 0:
                        hash = hash_list[0]
                        url = url.replace('md5hash', hash)
                except Exception as ex:
                    print ex

            if url.find('kinoprosmotr.net/') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    page = page.replace('\n', '')
                    hash_list = re.findall(';file=(.*?)\\&', page)
                    if len(hash_list) > 0:
                        url = hash_list[0]
                except Exception as ex:
                    print ex

            if url.find('kinoprosmotr.org/video/') > -1:
                url1 = 'http://kinoprosmotr.net/serial/1839-ne-ver-su-iz-kvartiry-23.html'
                request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    page = page.replace('\n', '')
                    hash_list = re.findall('serial.php%3Fip%3D(.*?)%26fi', page)
                    if len(hash_list) > 0:
                        hash = hash_list[0]
                        url = url.replace('md5hash', hash)
                except Exception as ex:
                    print ex

            if url.find('film-center.info/') > -1:
                url1 = 'http://srv1.film-center.info/player/play.php?name=flv/full/zavtrak.na.trave.1979.dvdrip.flv'
                request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    page = page.replace('\n', '')
                    hash_list = re.findall('\\/video\\/(.*?)\\/', page)
                    if len(hash_list) > 0:
                        hash = hash_list[0]
                        url = url.replace('md5hash', hash)
                except Exception as ex:
                    print ex

            if url.find('onlinefilmx.ru/video') > -1 or url.find('onlinefilmx.tv/video') > -1:
                url1 = 'http://s2.onlinefilmx.tv/player/play.php?id=882'
                request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    page = page.replace('\n', '')
                    hash_list = re.findall('\\/video\\/(.*?)\\/', page)
                    if len(hash_list) > 0:
                        hash = hash_list[0]
                        url = url.replace('md5hash', hash)
                except Exception as ex:
                    print ex

            if url.find('minizal.net/') > -1:
                url1 = 'http://s2.minizal.net/php/playlist.php?pl=/syn_otca_narodov.txt'
                request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    page = page.replace('\n', '')
                    hash_list = re.findall('\\/video\\/(.*?)\\/', page)
                    if len(hash_list) > 0:
                        hash = hash_list[0]
                        url = url.replace('md5hash', hash)
                except Exception as ex:
                    print ex

            if url.find('porntube.com') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    page = page.replace('\n', '')
                    q = re.findall('\\?\\?(.*?)\\&\\&', url)
                    q = q[0]
                    print 'aaaaaaaaaaaaaaaaaaaa q:' + q
                    pos = page.find('<stream label="' + q)
                    tmp = page[page.find('<stream label="' + q):page.find('</stream>', pos)]
                    print 'bbbbbbbbbbbbbbbbbbbb tmp:' + tmp
                    film = re.findall('<file>(.*?)<', tmp)
                    if len(film) > 0:
                        film = film[0]
                        url = film.replace('&amp;', '&')
                except Exception as ex:
                    print ex

            if url.find('fileplaneta.com') > -1:
                string = re.findall('\\&dd=(.*?)\\&\\&', url)
                string = string[0]
                print 'aaaaaaaaaaaaaaaaaaaa q:' + string
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    str = page.find(string)
                    tmp = page[page.find('http://', str):page.find('</file>', str)]
                    print 'bbbbbbbbbbbbbbbbbbbb tmp:' + tmp
                    url = tmp
                except Exception as ex:
                    print ex

            if url.find('latino-serialo.ru') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    page = page.replace('\n', '')
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
                        print 'rrrrrrrrrrrrrrrrrrrrrrrrrr tmp ' + tmp
                        md5hash = re.findall('\\/video\\/(.*?)\\/', tmp)
                        md5hash = md5hash[0]
                        tmp2 = tmp.replace(md5hash, 'md5hash')
                        md4hash = re.findall('\\/md5hash\\/(.*?)\\/', tmp2)
                        md4hash = md4hash[0]
                        print 'aaaaaaaaaaaaaaaaaaaaaaaa md5hash ' + md5hash
                        print 'bbbbbbbbbbbbbbbbbbbbbbbbbbb md4hash ' + md4hash
                        string = re.findall('\\?\\?(.*?)\\&\\&', url)
                        string = string[0]
                        print 'bbbbbbbbbbbbbbbbbbbbbbbbbbb string ' + string
                        url2 = string.replace('md5hash', md5hash)
                        url = url2.replace('md4hash', md4hash)
                except Exception as ex:
                    print ex

            if url.find('allserials.tv/s/md5') > -1:
                url1 = 'http://allserials.tv/get.php?action=playlist&pl=Osennie.cvety.2009'
                request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    page = page.replace('\n', '')
                    if len(page) > 0:
                        code_url = 'http://gegen-abzocke.com/xml/nstrim/allserials/code.php?code_url=' + page
                        request2 = urllib2.Request(code_url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                         'Connection': 'Close'})
                        hash = urllib2.urlopen(request2).read()
                        url = url.replace('md5hash', hash)
                        print 'filmix'
                        print url
                except Exception as ex:
                    print ex

            if url.find('kinopod.org/get/md5') > -1 or url.find('flvstorage.com/get/md5') > -1:
                url1 = 'http://kinopod.tv/serials/episode/38967.html'
                request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    page = page.replace('\n', '')
                    hash_list = re.findall('\\/get\\/(.*?)\\/', page)
                    if len(hash_list) > 0:
                        hash = hash_list[0]
                        url = url.replace('md5hash', hash)
                except Exception as ex:
                    print ex

            if url.find('kino-live.org/s/md5') > -1:
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

            if url.find('kinobanda.net/') > -1:
                url1 = 'http://kinobanda.net/get.php?pl=23298/1/0/'
                request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    page = page.replace('\n', '')
                    if len(page) > 0:
                        hash = page[0]
                        url = url.replace('md5hash', hash)
                except Exception as ex:
                    print ex

            if url.find('kino-dom.tv/s/md5') > -1:
                url1 = 'http://kino-dom.tv/drama/1110-taynyy-krug-the-sesret-sirsle-1-sezon-1-seriya-eng-onlayn.html'
                request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    page = page.replace('\n', '')
                    hash_list = re.findall('pl:"http:\\/\\/kino-dom\\.tv\\/(.*?)\\/play\\/', page)
                    if len(hash_list) > 0:
                        hash = hash_list[0]
                        url = url.replace('md5hash', hash)
                except Exception as ex:
                    print ex

            if url.find('new-kino.net') > -1:
                url1 = 'http://new-kino.net/komedii/5631-igrushka-1982.html'
                request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    page = page.replace('\n', '')
                    hash_list = re.findall('\\/dd11\\/(.*?)\\/', page)
                    if len(hash_list) > 0:
                        hash = hash_list[0]
                        url = url.replace('md5hash', hash)
                except Exception as ex:
                    print ex

            if url.find('linecinema.org/s/md5') > -1:
                url1 = 'http://www.linecinema.org/newsz/boevyk-online/508954-bliznecy-drakony-twin-dragons-1992-dvdrip-onlayn.html'
                request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    page = page.replace('\n', '')
                    hash_list = re.findall('linecinema\\.org\\/s\\/(.*?)\\/', page)
                    if len(hash_list) > 0:
                        hash = hash_list[0]
                        url = url.replace('md5hash', hash)
                except Exception as ex:
                    print ex

            if url.find('//figvam.ru/') > -1:
                url = url.replace('figvam.ru', 'go2load.com')
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    page = page.replace('\n', '')
                    hash_list = re.findall('ftp\\:\\/\\/(.*?)"', page)
                    if len(hash_list) > 0:
                        hash = hash_list[0]
                        url = 'ftp://' + hash
                    print url
                except Exception as ex:
                    print ex

            if url.find('allinspace.com/') > -1:
                url_row = re.findall('&(.*?)&&', url)
                url_row = url_row[0]
                request = urllib2.Request(url_row, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    url1 = re.findall('ttp://(.*?)&', url)
                    url1 = url1[0]
                    url = 'http://' + url1
                except Exception as ex:
                    print ex

            if url.find('.igru-film.net/') > -1:
                url_row = re.findall('xyss(.*?)xys', url)
                url_row = url_row[0]
                url_film = 'http://fepcom.net/' + url_row
                film = re.findall('ssa(.*?)xyss', url)
                film = film[0]
                request = urllib2.Request(url_film, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    film_row = re.findall(';file=([^&]*)', page)
                    if len(film_row) > 0:
                        film_row = film_row[0]
                        code_url = 'http://gegen-abzocke.com/xml/nstrim/fepcom/code.php?code_url=' + film_row
                        request = urllib2.Request(code_url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                         'Connection': 'Close'})
                        code = urllib2.urlopen(request).read()
                        url = film.replace('md5hash', code)
                except Exception as ex:
                    print ex

            if url.find('kinoylei.ru/') > -1:
                url1 = 'http://server1.kinoluvr.ru/get/2902-3142'
                request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code = re.findall('--(.*?)&', page)
                    if len(code) > 0:
                        md5hash = code[0]
                        url = url.replace('md5hash', md5hash)
                except Exception as ex:
                    print ex

            if url.find('//77.120.114') > -1 or url.find('nowfilms.ru/') > -1:
                url_row = re.findall('xyss(.*?)xys', url)
                url_row = url_row[0]
                url_film = 'http://' + url_row
                film = re.findall('ssa(.*?)xyss', url)
                film = film[0]
                film_end = re.findall('/md5hash/(.*?)xys', url)
                film_end = film_end[0]
                request = urllib2.Request(url_film, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    link = urllib2.urlopen(request).read()
                    film_row = re.findall(';pl=([^"]*)', link)
                    if len(film_row) > 0:
                        film_row = film_row[0]
                        if film_row.find('/tmp/') > 0:
                            request2 = urllib2.Request(film_row, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                             'Connection': 'Close'})
                            link = urllib2.urlopen(request2).read()
                            indexer = link.find(film_end)
                        if indexer > 0:
                            md5hash = link[indexer - 23:indexer - 1]
                            url = film.replace('md5hash', md5hash)
                    else:
                        url = re.findall(';file=([^"]*)', link)
                        url = url[0]
                except Exception as ex:
                    print ex

            if url.find('mightyupload') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    link1 = urllib2.urlopen(request).read()
                    if link1.find("file: '") > -1:
                        url2 = re.findall("file: '(.*?)'", link1)
                        url = url2[0]
                except Exception as ex:
                    print ex

            if url.find('baskino.com') > -1:
                string = re.findall('\\?\\?(.*?)\\&\\&', url)
                string = string[0]
                print string + 'string'
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    indexer = page.find(string)
                    link2 = page[indexer - 150:indexer]
                    link2 = link2.replace('\\', '')
                    link2 = link2 + string + '"'
                    url1 = re.findall('file:"(.*?)"', link2)
                    url = url1[0]
                except Exception as ex:
                    print ex

            if url.find('kset.kz') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code = re.findall('ImZpbGUi(.*?)=', page)
                    code = code[0]
                    if len(code) > 0:
                        code_url = 'http://gegen-abzocke.com/xml/nstrim/kset/code.php?code_url=' + code
                        request3 = urllib2.Request(code_url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                         'Connection': 'Close'})
                        url = urllib2.urlopen(request3).read()
                except Exception as ex:
                    print ex

            if url.find('//kinostok.tv/video/') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code = re.findall('file: "(.*?)"', page)
                    code = code[0]
                    code = code.replace('#', '')
                    if len(code) > 0:
                        code_url = 'http://gegen-abzocke.com/xml/nstrim/kinostok/code.php?code_url=' + code
                        request3 = urllib2.Request(code_url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                         'Connection': 'Close'})
                        url = urllib2.urlopen(request3).read()
                except Exception as ex:
                    print ex

            if url.find('enter.az') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code = re.findall('file=(.*?)&', page)
                    code = code[0]
                    if len(code) > 0:
                        code_url = 'http://gegen-abzocke.com/xml/nstrim/enter/code.php?code_url=' + code
                        request3 = urllib2.Request(code_url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                         'Connection': 'Close'})
                        url = urllib2.urlopen(request3).read()
                except Exception as ex:
                    print ex

            if url.find('//kinostok.tv/player/') > -1 or url.find('//kinostok.tv/embed') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    if len(page) > 0:
                        code_url = 'http://gegen-abzocke.com/xml/nstrim/kinostok/code.php?code_url=' + page
                        request3 = urllib2.Request(code_url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                         'Connection': 'Close'})
                        tmp = urllib2.urlopen(request3).read()
                        url1 = re.findall('file":"(.*?)"', tmp)
                        url = url1[0]
                except Exception as ex:
                    print ex

            if url.find('online-life.ru') > -1:
                url1 = re.findall('\\?\\?(.*?)\\&\\&', url)
                url1 = url1[0]
                print url1 + 'url1'
                if url.find('txt') > -1:
                    request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                     'Connection': 'Close'})
                    page = urllib2.urlopen(request).read()
                    url1 = re.findall('pl:"(.*?)"', page)
                    url1 = url1[0]
                request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                page = urllib2.urlopen(request).read()
                hash = re.findall('/video/(.*?)/tync', page)
                hash = hash[0]
                url = url.replace('md5hash', hash)
                print ex
            if url.find('.kinoxa-x.ru') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code = re.findall('"http://srv(.*?)"', page)
                    code = code[0]
                    if len(code) > 0:
                        url = 'http://srv' + code
                except Exception as ex:
                    print ex

            if url.find('kinohd.org') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code = re.findall("file : '(.*?)'", page)
                    code = code[0]
                    if len(code) > 0:
                        url = code
                except Exception as ex:
                    print ex

            if url.find('imovies.ge/') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code = re.findall('file>(.*?)<', page)
                    code = code[0]
                    if len(code) > 0:
                        url = code
                except Exception as ex:
                    print ex

            if url.find('veterok.tv/v/') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code = re.findall('http://cdn(.*?)"', page)
                    code = code[0]
                    if len(code) > 0:
                        url = 'http://cdn' + code
                except Exception as ex:
                    print ex

            if url.find('.tushkan.net/php') > -1 or url.find('rugailo.net/php') > -1 or url.find('videose.org/') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code = re.findall("file:'(.*?)'", page)
                    code = code[0]
                    if len(code) > 0:
                        url = code
                except Exception as ex:
                    print ex

            if url.find('.tushkan.net/video') > -1:
                url1 = 'http://srv3.tushkan.net/php/tushkan.php?name=film/Slova.2012.flv'
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

            if url.find('hdrezka.tv') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code = re.findall('"mp4":"(.*?)"', page)
                    if len(code) > 0:
                        code = code[0]
                        url = code.replace('\\', '')
                except Exception as ex:
                    print ex

            if url.find('jampo.com.ua') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code = re.findall("flashvars.File = '(.*?)'", page)
                    code = code[0]
                    if len(code) > 0:
                        url = code
                except Exception as ex:
                    print ex

            if url.find('api.video.mail.ru/') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code = re.findall('sd":"(.*?)"', page)
                    code = code[0]
                    if len(code) > 0:
                        url = code
                except Exception as ex:
                    print ex

            if url.find('/streaming.video.') > -1:
                try:
                    id_list = re.findall('get-location/(.*)/m', url)
                    id = id_list[0]
                    url1 = 'http://static.video.yandex.ru/get-token/' + id + '?nc=0.50940609164536'
                    request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                     'Connection': 'Close'})
                    page = urllib2.urlopen(request).read()
                    hash_list = re.findall('token>(.*)</token>', page)
                    hash = hash_list[0]
                    link1 = url.replace('md5hash', hash)
                    request2 = urllib2.Request(link1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                     'Connection': 'Close'})
                    page2 = urllib2.urlopen(request2).read()
                    film_list = re.findall('video-location>(.*)</video-location>', page2)
                    film = film_list[0]
                    url = film.replace('&amp;', '&')
                except Exception as ex:
                    print ex

            if url.find('embed.nowvideo.eu/') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    film1 = re.findall('flashvars.file="(.*)";', page)
                    film = film1[0]
                    filekey1 = re.findall('flashvars.filekey="(.*)";', page)
                    filekey = filekey1[0]
                    xml_url = 'http://www.nowvideo.eu/api/player.api.php?user=undefined&codes=1&key=' + filekey + '&pass=undefined&file=' + film
                    request = urllib2.Request(xml_url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                     'Connection': 'Close'})
                    page = urllib2.urlopen(request).read()
                    url2 = re.findall('http(.*)&title', page)
                    url1 = url2[0]
                    url = 'http' + url1
                except Exception as ex:
                    print ex

            if url.find('novamov.com/embed') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    film1 = re.findall('flashvars.file="(.*)";', page)
                    film = film1[0]
                    filekey1 = re.findall('flashvars.filekey="(.*)";', page)
                    filekey = filekey1[0]
                    xml_url = 'http://www.novamov.com/api/player.api.php?user=undefined&codes=1&key=' + filekey + '&pass=undefined&file=' + film
                    request = urllib2.Request(xml_url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                     'Connection': 'Close'})
                    page = urllib2.urlopen(request).read()
                    url2 = re.findall('http(.*)&title', page)
                    url1 = url2[0]
                    url = 'http' + url1
                except Exception as ex:
                    print ex

            if url.find('videoweed.es/file/') > -1 or url.find('videoweed.es/embed') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    film1 = re.findall('flashvars.file="(.*)";', page)
                    film = film1[0]
                    filekey1 = re.findall('flashvars.filekey="(.*)";', page)
                    filekey = filekey1[0]
                    xml_url = 'http://www.videoweed.es/api/player.api.php?user=undefined&codes=1&key=' + filekey + '&pass=undefined&file=' + film
                    request = urllib2.Request(xml_url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                     'Connection': 'Close'})
                    page = urllib2.urlopen(request).read()
                    url2 = re.findall('http(.*)&title', page)
                    url1 = url2[0]
                    url = 'http' + url1
                except Exception as ex:
                    print ex

            if url.find('/video.sibnet.ru') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    page = page.replace('&amp;', '&')
                    url_list = re.findall('<file>(.*?)<\\/file>', page)
                    if len(url_list) > 0:
                        url = url_list[0]
                        print 'sibnet'
                        print url
                except Exception as ex:
                    print ex

            if url.find('namba.net/') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    id = re.findall('video\\/(.*?)\\/', url)
                    id = id[0]
                    page = urllib2.urlopen(request).read()
                    url_list = re.findall("CSRF_TOKEN='(.*?)'", page)
                    print url_list
                    if len(url_list) > 0:
                        token = url_list[0]
                        url1 = 'http://namba.net/api/?service=video&action=video&token=' + token + '&id=' + id
                        request2 = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                         'Connection': 'Close'})
                        page = urllib2.urlopen(request2).read()
                        url_list2 = re.findall('flv":"(.*?)"', page)
                        film2 = url_list2[0]
                        url = film2.replace('\\', '')
                        print 'namba'
                        print url
                except Exception as ex:
                    print ex

            if url.find('filmix.net/s/md5hash') > -1 or url.find('filevideosvc.org/s/md5hash') > -1:
                url1 = 'http://filmix.net/semejnyj/36974-tor-legenda-vikingov-legends-of-valhalla-thor-2011.html'
                request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code_list = re.findall("cleanArray\\(\\['(.*?)'", page)
                    if len(code_list) > 0:
                        code = code_list[0]
                        code_url = 'http://gegen-abzocke.com/xml/nstrim/filmix/code.php?code_url=' + code
                        request2 = urllib2.Request(code_url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                         'Connection': 'Close'})
                        hash = urllib2.urlopen(request2).read()
                        url = url.replace('md5hash', hash)
                        print 'filmix'
                        print url
                except Exception as ex:
                    print ex

            if url.find('.tfilm.tv/') > -1:
                url1 = 'http://filmin.ru/28234-buket.html'
                request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code_list = re.findall(';file=(.*?)&', page)
                    if len(code_list) > 0:
                        code = code_list[0]
                        code_url = 'http://gegen-abzocke.com/xml/nstrim/filmin/code.php?code_url=' + code
                        request2 = urllib2.Request(code_url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                         'Connection': 'Close'})
                        hash = urllib2.urlopen(request2).read()
                        url = url.replace('md5hash', hash)
                        print 'filmin'
                        print url
                except Exception as ex:
                    print ex

            if url.find('bigcinema.tv') > -1:
                url1 = 'http://bigcinema.tv/movie/prometey---prometheus.html'
                request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    str = page.find('(loadPlayer')
                    tmp = page[page.find('file:', str):page.find('};', str)]
                    code_list = re.findall("'(.*?)'", tmp)
                    if len(code_list) > 0:
                        code = code_list[0]
                        code_url = 'http://gegen-abzocke.com/xml/nstrim/bigcinema/code.php?code_url=' + code
                        request2 = urllib2.Request(code_url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                         'Connection': 'Close'})
                        hash = urllib2.urlopen(request2).read()
                        url = url.replace('md5hash', hash)
                        print 'filmix'
                        print url
                except Exception as ex:
                    print ex

            if url.find('tree.tv') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    page = page.replace('\\', '')
                    q = re.findall('dd=(.*?)\\&\\&', url)
                    q = q[0]
                    str2 = page.find(q)
                    str = page.find('http://balancer', str2)
                    url2 = page[page.find(q, str) - 150:page.find(q, str) + 150]
                    print 'rrrrrrrrrrrrrrrrrrrrrrrrrr url2 ' + url2
                    url3 = re.findall('http://(.*?).mp4', url2)
                    url3 = url3[0]
                    url = 'http://' + url3 + '.mp4'
                    print 'rrrrrrrrrrrrrrrrrrrrrrrrrr url ' + url
                    print 'filmix'
                    print url
                except Exception as ex:
                    print ex

            if url.find('ofx.xyz') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    page = page.replace('\\', '')
                    q = re.findall('dd=(.*?)\\&\\&', url)
                    q = q[0]
                    str2 = page.find(q)
                    str = page.find('/vid/', str2)
                    url2 = page[page.find(q, str) - 50:page.find(q, str) + 50]
                    print 'rrrrrrrrrrrrrrrrrrrrrrrrrr url2 ' + url2
                    url3 = re.findall('/vid/(.*?).flv', url2)
                    url3 = url3[0]
                    url = 'http://ofx.xyz/vid/' + url3 + '.flv'
                    print 'rrrrrrrrrrrrrrrrrrrrrrrrrr url ' + url
                    print 'filmix'
                    print url
                except Exception as ex:
                    print ex

            if url.find('911.to') > -1:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; rv:33.0) Gecko/20100101 Firefox/33.0',
                 'Origin': 'http://911.to',
                 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                 'X-Requested-With': 'XMLHttpRequest',
                 'Accept-Language': 'de,en-US;q=0.7,en;q=0.3',
                 'Connection': 'keep-alive'}
                request = urllib2.Request(url, None, headers)
                try:
                    page = urllib2.urlopen(request).read()
                    page = page.replace('\\', '')
                    q = re.findall('dd=(.*?)\\&\\&', url)
                    q = q[0]
                    str2 = page.find(q)
                    str = page.find('/get_cv/', str2)
                    url2 = page[page.find(q, str) - 50:page.find(q, str) + 50]
                    print 'rrrrrrrrrrrrrrrrrrrrrrrrrr url2 ' + url2
                    url3 = re.findall('/get_cv/(.*?).mp4', url2)
                    url3 = url3[0]
                    url = 'http://911.to/get_cv/' + url3 + '.mp4'
                    print 'rrrrrrrrrrrrrrrrrrrrrrrrrr url ' + url
                    print 'filmix'
                    print url
                except Exception as ex:
                    print ex

            if url.find('liveparser=1') > -1:
                string = re.findall('dd=(.*?)\\&\\&', url)
                string = string[0]
                url1 = 'http://31.131.16.114/liveparser.php?str=' + string
                request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    url2 = re.findall('<url>(.*?)<', page)
                    url2 = url2[0]
                    start = re.findall('<start>(.*?)<', page)
                    start = start[0]
                    end = re.findall('<end>(.*?)<', page)
                    end = end[0]
                    if url2.find('ttp://') > -1:
                        url = url2
                    request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                     'Connection': 'Close'})
                    page = urllib2.urlopen(request).read()
                    print 'aaaaaaaaaaaaaaaaaaaaaaaaaa start ' + start
                    print 'ssssssssssssssssssssssssss end ' + end
                    str2 = page.find(start)
                    url2 = page[page.find(start):page.find(end, str2 + len(start) + 2)]
                    url = url2.replace(start, '')
                    print 'url' + url
                    print url
                except Exception as ex:
                    print ex

            if url.find('liveparser=2') > -1:
                string = re.findall('dd=(.*?)\\&', url)
                string = string[0]
                url2 = re.findall('url2=(.*?)\\&\\&', url)
                url2 = url2[0]
                url1 = 'http://31.131.16.114/liveparser.php?str=' + string
                request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    start = re.findall('<start>(.*?)<', page)
                    start = start[0]
                    end = re.findall('<end>(.*?)<', page)
                    end = end[0]
                    request = urllib2.Request('http://' + url2, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                     'Connection': 'Close'})
                    page = urllib2.urlopen(request).read()
                    print 'aaaaaaaaaaaaaaaaaaaaaaaaaa start ' + start
                    print 'ssssssssssssssssssssssssss end ' + end
                    str2 = page.find(start)
                    url2 = page[page.find(start):page.find(end, str2 + len(start) + 2)]
                    print 'url2' + url2
                    hash = url2.replace(start, '')
                    url = url.replace('md5hash', hash)
                    print 'url' + url
                    print url
                except Exception as ex:
                    print ex

            if url.find('.datalock.ru/') > -1:
                url1 = 'http://newseriya.ru/serial-3151-Kak_ya_vstretil_vashu_mamu-7-season.html'
                request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code_list = re.findall('"pl":"(.*?)"', page)
                    if len(code_list) > 0:
                        code = code_list[0]
                        code_url = 'http://gegen-abzocke.com/xml/nstrim/seasonvar/code.php?code_url=' + code
                        request2 = urllib2.Request(code_url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                         'Connection': 'Close'})
                        hash = urllib2.urlopen(request2).read()
                        url = url.replace('md5hash', hash)
                        print 'seasonvar'
                        print url
                except Exception as ex:
                    print ex

            if url.find('stepashka.com/video/') > -1:
                url1 = 'http://online.stepashka.com/filmy/dramy/32265-kinoproba-audition-odison-1999.html'
                request = urllib2.Request(url1, None, {'User-agent': 'Mozilla/5.0 (Windows NT 6.0; rv:12.0) Gecko/20100101 Firefox/12.0',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code_list = re.findall('"st=(.*?)"', page)
                    if len(code_list) > 0:
                        link1 = code_list[0]
                        tmp = link1.replace('http://online.stepashka.com/player/', '')
                        myarr = tmp.split('/')
                        md5 = myarr[2]
                        url = url.replace('md5hash', md5)
                        print 'stepashka'
                        print url
                except Exception as ex:
                    print ex

            if url.find('//77.120.119') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code_list = re.findall('file":"(.*?)"', page)
                    if len(code_list) > 0:
                        code = code_list[0]
                        code_url = 'http://gegen-abzocke.com/xml/nstrim/liveonline/code.php?code_url=' + code
                        request2 = urllib2.Request(code_url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                         'Connection': 'Close'})
                        url = urllib2.urlopen(request2).read()
                        print 'filmix'
                        print url
                except Exception as ex:
                    print ex

            if url.find('uletfilm.net/') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code_list = re.findall('file":"(.*?)"', page)
                    if len(code_list) > 0:
                        code = code_list[0]
                        code_url = 'http://gegen-abzocke.com/xml/nstrim/uletno/code.php?code_url=' + code
                        request2 = urllib2.Request(code_url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                         'Connection': 'Close'})
                        url = urllib2.urlopen(request2).read()
                        print 'filmix'
                        print url
                except Exception as ex:
                    print ex

            if url.find('//vtraxe.com/') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code_list = re.findall('3Fv=(.*?)&', page)
                    if len(code_list) > 0:
                        code = code_list[0]
                        code_url = 'http://gegen-abzocke.com/xml/nstrim/uletno/code.php?code_url=' + code
                        request2 = urllib2.Request(code_url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                         'Connection': 'Close'})
                        url = urllib2.urlopen(request2).read()
                        print 'filmix'
                        print url
                except Exception as ex:
                    print ex

            if url.find('uakino') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    code_list = re.findall('file":"(.*?)"', page)
                    if len(code_list) > 0:
                        url2 = code_list[0]
                        url2 = url2.replace('%2F', '/')
                        url = url2.replace('%3A', ':')
                        print 'uakino'
                        print url
                except Exception as ex:
                    print ex

        except Exception as ex:
            print ex
            print 'goshparsed_link'

        return url