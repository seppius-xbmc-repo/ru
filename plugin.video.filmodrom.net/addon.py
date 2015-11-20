# -*- coding: utf-8 -*-

import urllib, urllib2, re, sys, json
import xbmcplugin, xbmcgui

class SiteScrapper:

    def __init__(self):
        self.base_url = 'http://filmodrom.in/'
        self.encoding = 'windows-1251'
        self.preg = {
            'categories': '<li[^\>]*><a href="\/(.+?)" title=".+?">(.+?)</a>\s*</li>',
            'videos': '<h4>\s*<a href="(.+?)">(.+?)</a>',
            'videos': '<a href="(.+?)" title="(.+?)" class="short-images-link">',
            'pictures': 'class="short-images-link">\s*<img src="(http://filmodrom.net/|)(.+?)"',
            'picture': '<div class="fstory-poster">\s*<img src="(http://filmodrom.net/|)(.+?)"',
            'video': 'file=(.+?flv)',
            'serial_list': 'pl=(.+?xml)"',
            'video_title': '<meta property="og:title" content="(.+?)" />'
        }
        self.headers = {
            'Accept': '*/*',
            #'Accept-Encoding': 'gzip,deflate,sdch',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4',
            'Connection': 'keep-alive',
            #'Host': '50.7.188.178:177',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36'
            #'Content-Type': 'application/x-www-form-urlencoded'
        }
        self.params = self.getParams()
        if self.params is not None and 'url' in self.params:
            self.params['url'] = urllib2.unquote(self.params['url'])

    def isLinkUseful(self, needle):
        haystack = ['news/','movies/']
        return needle not in haystack

    def addElements(self):
        result = {}
        if self.params is None or 'url' not in self.params:
            html = self.getHTML(self.base_url)
        else:
            if self.params is None or 'page' not in self.params or self.params['mode'] == 'video':
                html = self.getHTML(self.params['url'])
            else:
                html = self.getHTML(self.params['url'] + '/page/' + self.params['page'] + '/')
        for name, preg in self.preg.iteritems():
            preg_result = re.compile(preg).findall(html)
            if preg_result is not None and preg_result != '':
                result[name] = preg_result
        #print result['videos']
        self.draw(result)

    def draw(self, params):
        if self.params is not None and 'mode' in self.params:
            if self.params['mode'] == 'cats':
                self.Categories(params)
            if self.params['mode'] == 'sub_cats':
                self.SubCategories(params)
            if self.params['mode'] == 'videos':
                self.Videos(params)
            if self.params['mode'] == 'video':
                self.Video(params)
        else:
            self.Categories(params)

    def Categories(self, params):
        for link, title in params['categories']:
            if self.isLinkUseful(link):
                try:
                    self.addDir(title, self.base_url + link, 'videos', None, '1')
                except Exception:
                    self.addDir('Ошибка', '', 'videos', None)

    def SubCategories(self, params):
        if params['sub_categories'] is None:
            return False

    def Videos(self, params):
        self.mainPage()
        #self.prevPage()
        for i in range(0, len(params['videos'])):
            try:
                if 'page' in self.params:
                    self.addDir(params['videos'][i][1], params['videos'][i][0], 'video', params['pictures'][i][1], self.params['page'])
                else:
                    self.addDir(params['videos'][i][1], params['videos'][i][0], 'video', None)
            except Exception:
                self.addDir('Ошибка', '', 'video', None)
        self.nexPage()

    def Video(self, params):
        self.mainPage()
        if len(params['video']) > 1:
            prefix = True
        else:
            prefix = False
        if len(params['video']) > 0:
            for i in range(0, len(params['video'])):
                try:
                    self.addLink(params['video_title'][i], params['video'][i], params['picture'][i][1])
                except Exception:
                    self.addLink('Ошибка', '', '')
        else:
            self.encoding = 'utf-8'
            html = self.getHTML(params['serial_list'][0])
            series = re.compile('\{"comment":"(.+?)","file":"(http://.+?.flv)"\}').findall(html)
            for title, link in series:
                try:
                    self.addLink(title, link, '')
                except Exception:
                    self.addLink('Ошибка', '', '')

    def prevPage(self):
        if 'page' in self.params and int(self.params['page']) > 1:
            page = int(self.params['page']) - 1
            self.addDir("  << Назад", self.params['url'], self.params['mode'], None, str(page))

    def mainPage(self):
        self.addDir("<<< [ На главную ]", self.base_url, 'cats', None)

    def nexPage(self):
        if 'page' in self.params:
            page = int(self.params['page']) + 1
        else:
            page = 1
        self.addDir("  Вперёд >>", self.params['url'], self.params['mode'], None, str(page))

    def getHTML(self, url):
        conn = urllib2.urlopen(urllib2.Request(url, urllib.urlencode({}), self.headers))
        self.html = conn.read()
        conn.close()
        if self.encoding != 'utf-8':
            self.html = self.html.decode(self.encoding).encode('utf-8')
        return self.html

    def getUrl(self, url):
        conn = urllib2.urlopen(urllib2.Request(url, urllib.urlencode({}), self.headers))
        result = conn.geturl()
        conn.close()
        return result

    def getParams(self):
        param = None
        if len(sys.argv) >=2 and len(sys.argv[2]) >= 2:
            params = sys.argv[2]
            cleanedparams=params.replace('?', '')
            if (params[len(params)-1] == '/'):
                params = params[0:len(params)-2]
            pairsofparams = cleanedparams.split('&')
            param = {}
            for i in range(len(pairsofparams)):
                splitparams = {}
                splitparams = pairsofparams[i].split('=')
                if (len(splitparams)) == 2:
                    param[splitparams[0]] = splitparams[1]
        return param

    def addLink(self, title, url, picture):
        item = xbmcgui.ListItem(title, iconImage='DefaultVideo.png', thumbnailImage=self.base_url + picture)
        item.setInfo(type='Video', infoLabels={'Title': title})
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=item)


    def addDir(self, title, url, mode, picture, page=None):
        sys_url = sys.argv[0] + '?title=' + urllib.quote_plus(title) + '&url=' + url + '&mode=' + urllib.quote_plus(mode)
        if picture is None:
            item = xbmcgui.ListItem(title, iconImage='DefaultFolder.png', thumbnailImage='')
        else:
            item = xbmcgui.ListItem(title, iconImage='DefaultFolder.png', thumbnailImage=self.base_url + picture)
            sys_url += '&picture=' + urllib.quote_plus(str(picture))
        if page is not None:
            sys_url += '&page=' + urllib.quote_plus(str(page))
        item.setInfo(type='Video', infoLabels={'Title': title})
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=sys_url, listitem=item, isFolder=True)

test = SiteScrapper()
test.addElements()
xbmcplugin.endOfDirectory(int(sys.argv[1]))