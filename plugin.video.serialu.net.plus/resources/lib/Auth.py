import xbmc, xbmcgui, xbmcaddon, xbmcplugin
import urllib, urllib2, json, sys, os, cookielib
import urlparse

import gzip, StringIO, zlib

from BeautifulSoup  import BeautifulSoup
from PlayerSelect   import PlayerDialog
from Main           import MainScreen
from Data           import Data

class Auth(object):
  def __init__(self, *args, **kwargs):
    self.Addon = kwargs.get('Addon')
    #--- paths ------------------------------
    self.Addon_path = self.Addon.getAddonInfo('path').decode(sys.getfilesystemencoding())
    self.Data_path  = xbmc.translatePath(os.path.join(self.Addon_path, r'resources', r'data'))
    #---
    self.fcookies = xbmc.translatePath(os.path.join(self.Addon_path, r'cookies.txt'))
    self.HTML_retry = 0
    self.player = xbmc.Player()
    #---
    kwargs={'Auth': self}
    self.Data = Data(**kwargs)
    #-------
    # get cookies from last session
    self.cj = cookielib.MozillaCookieJar(self.fcookies)
    try:
        self.cj.load(self.fcookies, True, True)
    except:
        pass
    hr  = urllib2.HTTPCookieProcessor(self.cj)
    opener = urllib2.build_opener(hr)
    urllib2.install_opener(opener)

  def _del_(self):
    self.cj.save(elf.fcookies, True, True)
    del self.Player

  #-----------------------------------------------------------------------------
  def Authorize(self):
    return True

  #---------------------- HTML request -----------------------------------------
  def get_HTML(self, url, post = None, ref = None, get_url = False):
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
           xbmc.executebuiltin('Notification(SEASONVAR.ru,%s,5000,%s)'%(e.reason.capitalize(), os.path.join(self.Addon.getAddonInfo('path'), 'warning.jpg')))
           #---
           if self.HTML_retry < 3:
               xbmc.sleep(2000)
               self.HTML_retry = self.HTML_retry+1
               return self.get_HTML(url, post, ref, get_url)

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

    self.HTML_retry = 0

    return html

  #---------------------------------------------------------------------------
  def Player(self, **kwargs):
      kwargs['Auth'] = self
      aw = PlayerDialog('tvp_playerDialog.xml', self.Addon.getAddonInfo('path'), **kwargs)
      aw.doModal()
      del aw

  #---------------------------------------------------------------------------
  def showMain(self):
    kwargs={'Auth': self}
    aw = MainScreen('tvp_main.xml', self.Addon.getAddonInfo('path'), **kwargs)
    aw.doModal()
    del aw