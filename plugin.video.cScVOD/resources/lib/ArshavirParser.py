import hashlib
import re
import urllib
import urllib2

class arshavir_parsers:

    def __init__(self):
        self.quality = ''

    def get_parsed_link(self, url):
        try:
            if url.find('filmsehri') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    page = page.strip(' \t\n\r')
                    regex1 = re.findall('player.swf\\?config=(.*?)" quality="high"', page)
                    if len(regex1) > 0:
                        url2 = regex1[0]
                        request = urllib2.Request(url2, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                         'Connection': 'Close'})
                        page = urllib2.urlopen(request).read()
                        regex2 = re.findall('<file>(.*?)<\\/file>', page)
                        if len(regex2) > 0:
                            url = regex2[0]
                except Exception as ex:
                    print ex

            if url.find('watchcinema.ru') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    page = page.strip(' \t\n\r')
                    regex = re.findall('<iframe src="(.*?)"', page)
                    url = regex[0]
                    if regex[0].find('youtube') > -1:
                        url = url.replace('embed/', 'watch?v=')
                except Exception as ex:
                    print ex

            if url.find('xvideos.com') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    regex = re.findall('3GP\\|\\|(.*?)\\|\\|', page)
                    url = regex[0]
                except Exception as ex:
                    print ex

            if url.find('dailymotion.com') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    regex = re.findall('stream_h264_url":"(.*?)"', page)
                    url = regex[0].replace('\\', '')
                except Exception as ex:
                    print ex

            if url.find('vizor.tv') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    regex = re.findall('file=([^&]*)', page)
                    url = 'VIZOR' + regex[0]
                except Exception as ex:
                    print ex

            if url.find('mp333.do.am') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    regex1 = re.findall('var link1 = "(.*?)[?]lang', page)
                    regex2 = re.findall('var link1 = ".*?lang=(.*?)&', page)
                    regex3 = re.findall('var link1 = ".*?&id=(.*?)"', page)
                    url = regex1[0] + regex2[0] + '/' + regex3[0]
                except Exception as ex:
                    print ex

            if url.find('hubu.ru') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    regex = re.findall(",'(.*?)'", page)
                    url = regex[0]
                except Exception as ex:
                    print ex

            if url.find('zaycev.net') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    regex = re.findall('encodeURIComponent.*?id=(.*?)&', page)
                    regex2 = re.findall('encodeURIComponent.*?id=.*?&ass=(.*?)"', page)
                    regex3 = re.findall('encodeURIComponent.*?id=(.*?)..&', page)
                    url = 'http://dl.zaycev.net/mini/' + regex3[0] + '/' + regex[0] + '/' + regex2[0] + '.mp3'
                except Exception as ex:
                    print ex

            if url.find('loveradio.ru') > -1:
                request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'Connection': 'Close'})
                try:
                    page = urllib2.urlopen(request).read()
                    regex = re.findall("{uid: '(.*?)'", page)
                    regex2 = re.findall('icons/(.*?).png', page)
                    if regex2[0] == 'loveradio' or regex2[0] == 'top40' or regex2[0] == 'jlo':
                        regex3 = regex2[0]
                    else:
                        regex3 = 'love_' + regex2[0]
                    url = 'http://stream2.loveradio.ru:9000/' + regex3 + '_64?type=.flv&UID=' + regex[0]
                except Exception as ex:
                    print ex

            if url.find('77.91.77') > -1 and url.find('login') == -1:
                request = urllib2.Request('http://inetcom.tv/videorec/lookChannel?ch_id=13', None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'X-Requested-With': 'XMLHttpRequest',
                 'Host': 'inetcom.tv',
                 'Referer': 'http://inetcom.tv/channel/pervyi'})
                try:
                    page = urllib2.urlopen(request).read()
                    regex = re.findall('\\?sid=(.*?)\\"', page)
                    url = url + '?sid=' + regex[0]
                except Exception as ex:
                    print ex

            if url.find('mediacdn.ru') > -1:
                event = re.findall('event=(\\d+)', url)
                request = urllib2.Request('http://app.bonus-tv.ru/api/channels', None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                 'X-Requested-With': 'XMLHttpRequest',
                 'Host': 'app.bonus-tv.ru',
                 'Referer': 'http://bonus-tv.ru:90/lg/publish/',
                 'X_USERNAME': 'c3d33d76a835a59ff32bb65e77dfa45c',
                 'X_PASSWORD': 'c3d33d76a835a59ff32bb65e77dfa45c'})
                try:
                    page = urllib2.urlopen(request).read()
                    hash = re.findall('event=' + event[0] + '&hash=(.*?)"', page)
                    url = url + hash[0]
                except Exception as ex:
                    print ex

        except Exception as ex:
            print ex
            print 'html_parser ERROR'

        return url