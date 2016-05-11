import urllib
import urllib2
import cookielib
import os

import xbmcvfs

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:25.0) Gecko/20100101 Firefox/25.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
    'Accept-Charset': 'utf-8, utf-16, *;q=0.1',
    'Accept-Encoding': 'identity, *;q=0'
}


class HttpClient:
    def __init__(self, http_site_url = None, cookie_path = None):
        self.http_site_url = http_site_url

        cookie_path = os.path.join(cookie_path, 'plugin.video.fs.ua.cookies.lwp')
        if isinstance(cookie_path, unicode):
            cookie_path = cookie_path.encode('utf8')
        self.cookie_path = cookie_path

    def remove_cookie(self):
        xbmcvfs.delete(self.cookie_path)

    def get_full_url(self, url):
        if url.startswith('//'):
            url = 'http:' + url
        if not '://' in url:
            url = self.http_site_url + url
        return url

    def GET(self, url, referer, post_params=None):
        headers['Referer'] = referer
        url = self.get_full_url(url)

        if post_params is not None:
            post_params = urllib.urlencode(post_params)
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
        elif headers.has_key('Content-Type'):
            del headers['Content-Type']

        jar = cookielib.LWPCookieJar(self.cookie_path)
        if xbmcvfs.exists(self.cookie_path):
            jar.load()

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))
        urllib2.install_opener(opener)
        req = urllib2.Request(url, post_params, headers)

        response = opener.open(req)
        the_page = response.read()
        response.close()

        jar.save()

        return the_page

