import xbmcaddon
import xbmc
import sys
import urllib2
import urllib
import threading
import os
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup

ADDON = xbmcaddon.Addon( id = 'script.torrent-tv.ru' )
ADDON_ICON	 = ADDON.getAddonInfo('icon')
ADDON_PATH = ADDON.getAddonInfo('path')
ADDON_ICON	 = ADDON.getAddonInfo('icon')
DATA_PATH = xbmc.translatePath( os.path.join( "special://profile/addon_data", 'script.torrent-tv.ru') )
VERSION = '1.5.3'
skin = ADDON.getSetting('skin')
SKIN_PATH = ADDON_PATH
print skin
if (skin != None) and (skin != "") and (skin != 'st.anger'):
    SKIN_PATH = DATA_PATH

class MyThread(threading.Thread):
    def __init__(self, func, params, back = True):
        threading.Thread.__init__(self)
        self.func = func
        self.params = params
        #self.parent = parent

    def run(self):
        self.func(self.params)
    def stop(self):
        pass

if (sys.platform == 'win32') or (sys.platform == 'win64'):
    ADDON_PATH = ADDON_PATH.decode('utf-8')

def showMessage(message = '', heading='Torrent-TV.RU', times = 6789):
    try: 
        xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, %s)' % (heading.encode('utf-8'), message.encode('utf-8'), times, ADDON_ICON))
    except Exception, e:
        try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, %s)' % (heading, message, times, ADDON_ICON))
        except Exception, e:
            xbmc.log( 'showMessage: exec failed [%s]' % 3 )

def GET(target, post=None, cookie = None, tryies = 0):
    try:
        print target
        req = urllib2.Request(url = target, data = post)
        req.add_header('User-Agent', 'XBMC (script.torrent-tv.ru)')
        if cookie:
            req.add_header('Cookie', 'PHPSESSID=%s' % cookie)
        resp = urllib2.urlopen(req, timeout=10)
        http = resp.read()
        resp.close()
        return http
    except Exception, e:
        if tryies == 0:
            tryies = tryies + 1
            return GET(target, post, cookie, tryies)
        xbmc.log( 'GET EXCEPT [%s]' % (e), 4 )

def checkPort(params):
        data = GET("http://2ip.ru/check-port/?port=%s" % params)
        beautifulSoup = BeautifulSoup(data)
        port = beautifulSoup.find('div', attrs={'class': 'ip-entry'}).text
        if port.encode('utf-8').find("Порт закрыт") > -1:
            return False
        else:
            return True

def tryStringToInt(str_val):
    try:
        return int(str_val)
    except:
        return 0