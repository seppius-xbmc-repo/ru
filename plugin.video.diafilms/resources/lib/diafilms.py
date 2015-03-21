import re, os, urllib, urllib2, cookielib, time, sys

import xbmcgui
import xbmcaddon
import xbmc

Addon = xbmcaddon.Addon(id='plugin.video.diafilms')

try:
    sys.path.append(os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib'))
    from BeautifulSoup  import BeautifulSoup
except:
    try:
        sys.path.insert(0, os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib'))
        from BeautifulSoup  import BeautifulSoup
    except:
        sys.path.append(os.path.join(os.getcwd(), r'resources', r'lib'))
        from BeautifulSoup  import BeautifulSoup
        icon = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'icon.png'))


import HTMLParser
hpar = HTMLParser.HTMLParser()

class Diafilm(xbmcgui.WindowXML):
    # Controls
    CONTROL_MAIN_IMAGE = 100
    # Actions
    ACTION_CONTEXT_MENU = [117]
    ACTION_MENU = [122]
    ACTION_PREVIOUS_MENU = [9]
    ACTION_SHOW_INFO = [11]
    ACTION_EXIT_SCRIPT = [10, 13]
    ACTION_DOWN = [4]
    ACTION_UP = [3]
    ACTION_0 = [58]

    def __init__(self, xmlFilename, scriptPath, defaultSkin, defaultRes):
        pass

    def Set_URL(self, url):
        self.Diafilm_URL= url

    def onInit(self):
        self.Clean_List()

        # -- fill up the image list
        # get diafilm list
        post = None
        request = urllib2.Request(self.Diafilm_URL, post)

        request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
        request.add_header('Host',	'diafilmy.su')
        request.add_header('Accept', '*/*')
        request.add_header('Accept-Language', 'ru-RU')
        request.add_header('Referer',	'http://google.com')

        try:
            f = urllib2.urlopen(request)
        except IOError, e:
            if hasattr(e, 'reason'):
                xbmc.log('We failed to reach a server. Reason: '+ e.reason)
            elif hasattr(e, 'code'):
                xbmc.log('The server couldn\'t fulfill the request. Error code: '+ e.code)

        html = f.read()

        # -- parsing web page ------------------------------------------------------
        soup = BeautifulSoup(html, fromEncoding="windows-1251")

        df_nav = soup.find("div", { "class" : "maincont" })
        for df in df_nav.findAll('img'):
            self.Add_to_List('http://www.diafilmy.su'+df['src'], df['title'])

        self.setFocus(self.getControl(self.CONTROL_MAIN_IMAGE))

    def onFocus(self, controlId):
        pass

    def onAction(self, action):
        if action in self.ACTION_EXIT_SCRIPT:
            self.close()

    def onClick(self, controlId):
        pass

    def Clean_List(self):
        self.getControl(self.CONTROL_MAIN_IMAGE).reset()

    def Add_to_List(self, url, title):


        li = xbmcgui.ListItem(label=title,
                              iconImage=url,
                              path = url)
        li.setProperty('show_info', 'true')
        li.setProperty('show_info', 'photo')
        li.setProperty('title', title)
        li.setProperty('aspectratio', 'keep')
        self.getControl(self.CONTROL_MAIN_IMAGE).addItem(li)




