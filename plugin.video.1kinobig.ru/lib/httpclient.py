import cookielib
import os
import urllib2

import xbmcvfs

from lib import utils

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    "Accept-Encoding": "windows-1251,utf-8;q=0.7,*;q=0.7",
    'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8,uk;q=0.7',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 '
                  'Safari/537.36 '
}


class HTTPClient:
    def __init__(self, site_url=None, cookie_path=None):
        self.site_url = site_url

        cookie_path = os.path.join(cookie_path, 'plugin.video.1kinobig.ru.cookies')
        if isinstance(cookie_path, unicode):
            cookie_path = cookie_path.encode('utf8')
        self.cookie_path = cookie_path

    def drop_cookie(self):
        xbmcvfs.delete(self.cookie_path)

    def get_full_url(self, url):
        if not url.startswith("http"):
            url = self.site_url + url
        return url

    def get_html(self, url, referer, post_params=None, post_headers=None):
        headers['Referer'] = referer
        url = self.get_full_url(url)

        if post_params is not None:
            post_params = utils.encode_url(post_params)
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
        elif 'Content-Type' in headers:
            del headers['Content-Type']

        if post_headers is not None:
            for post_header_key in post_headers.keys():
                headers[post_header_key] = post_headers.get(post_header_key)

        jar = cookielib.LWPCookieJar(self.cookie_path)
        if xbmcvfs.exists(self.cookie_path):
            jar.load()

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))
        urllib2.install_opener(opener)
        request = urllib2.Request(url, post_params, headers)

        response = opener.open(request)
        the_page = response.read()
        response.close()

        jar.save()

        return the_page
