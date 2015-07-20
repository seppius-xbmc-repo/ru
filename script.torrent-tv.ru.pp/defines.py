# Edited (c) 2015, Vorotilin D.V., E-mail: dvor85@mail.ru

import xbmcaddon
import xbmc
import sys
import urllib2
import threading
import os
from BeautifulSoup import BeautifulSoup

ADDON = xbmcaddon.Addon(id='script.torrent-tv.ru.pp')
ADDON_ICON = ADDON.getAddonInfo('icon')
ADDON_PATH = ADDON.getAddonInfo('path')
ADDON_ICON = ADDON.getAddonInfo('icon')
ADDON_ID = ADDON.getAddonInfo('id')
PTR_FILE = ADDON.getSetting('port_path')
DATA_PATH = xbmc.translatePath(os.path.join("special://profile/addon_data", ADDON_ID))
TTV_VERSION = '1.5.3'
AUTOSTART = ADDON.getSetting('startlast') == 'true'
DEBUG = ADDON.getSetting('debug') == 'true'
skin = ADDON.getSetting('skin')
SKIN_PATH = ADDON_PATH

print skin
if (skin != None) and (skin != "") and (skin != 'st.anger'):
    SKIN_PATH = DATA_PATH
    

    
def Autostart(state):
    userdata = xbmc.translatePath("special://masterprofile")
    autoexec = os.path.join(userdata, 'autoexec.py')

    if os.path.isfile(autoexec): 
        mode = 'r+' 
    elif state: 
        mode = 'w+'     
    else:
        return
        
    try:   
        found = False
        with open(autoexec, mode) as autoexec_file:            
            for line in autoexec_file:
                if ADDON_ID in line:
                    found = True
                    break
    
            if not found and state:
                autoexec_file.seek(0)
                autoexec_file.write('import xbmc\n')
                autoexec_file.write("xbmc.executebuiltin('RunAddon(%s)')\n" % ADDON_ID)
                autoexec_file.truncate()
                
        if not state and found: 
            os.unlink(autoexec)
    except:
        t, v, tb = sys.exc_info()        
        sys.stderr.write("Error while write autoexec.py: {}:{}.".format(t, v))
        del tb
        
        

class MyThread(threading.Thread):
    def __init__(self, func, params, back=True):
        threading.Thread.__init__(self)
        self.func = func
        self.params = params
        self.isCanceled = False

    def run(self):
        self.func(self.params)
        
    def stop(self):
        self.isCanceled = True
        
if (sys.platform == 'win32') or (sys.platform == 'win64'):
    ADDON_PATH = ADDON_PATH.decode('utf-8')

def showMessage(message='', heading='Torrent-TV.RU', times=6789):
    try: 
        xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, %s)' % (heading.encode('utf-8'), message.encode('utf-8'), times, ADDON_ICON))
    except Exception, e:
        try: 
            xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, %s)' % (heading, message, times, ADDON_ICON))
        except Exception, e:
            xbmc.log('showMessage: exec failed [%s]' % e, 3)

def GET(target, post=None, cookie=None):
    t = 0
    while True:
        t += 1
        try:
            print target
            req = urllib2.Request(url=target, data=post)
            req.add_header('User-Agent', 'XBMC (script.torrent-tv.ru)')
            if cookie:
                req.add_header('Cookie', 'PHPSESSID=%s' % cookie)
            resp = urllib2.urlopen(req, timeout=6)
            try:
                http = resp.read()
                return http
            finally:
                resp.close()
            
        except Exception, e:
            if t % 10 == 0:
                xbmc.log('GET EXCEPT [%s]' % (e), 4)
                xbmc.sleep(30000)       

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
