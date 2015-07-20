# Copyright (c) 2010-2011 Torrent-TV.RU
# Writer (c) 2011, Welicobratov K.A., E-mail: 07pov23@gmail.com
import xbmcgui
from BeautifulSoup import BeautifulSoup

import defines

class InfoForm(xbmcgui.WindowXMLDialog):
    LABEL_USER_LOGIN = 101
    LABEL_USER_BALANCE = 102
    LABEL_AS_STATUS = 103
    LABEL_AS_PORT = 104
    LABEL_ADDR = 105

    TEXT_NOPORT = "Закрыт"
    TEXT_YESPORT = "Открыт"

    def __init__(self, *args, **kwargs):
        self.parent = None
        self.portLabel = None
        self.ASLabel = None
        print 'init infoform'
        pass

    def onInit(self):
        userLabel = self.getControl(self.LABEL_USER_LOGIN)
        ballanceLabel = self.getControl(self.LABEL_USER_BALANCE)
        self.portLabel = self.getControl(self.LABEL_AS_PORT)
        self.addrLabel = self.getControl(self.LABEL_ADDR)
        self.outport = defines.ADDON.getSetting("outport")
        self.ASLabel = self.getControl(self.LABEL_AS_STATUS)

        print 'OnInit infoform %s' % self.parent
        if self.parent and self.parent.user:
            userLabel.setLabel(self.parent.user["login"])
            if float(self.parent.user["ballance"]) > 7:
                ballanceLabel.setLabel("[COLOR=blue]%sp.[/COLOR]" % self.parent.user["ballance"])
            else:
                ballanceLabel.setLabel("[COLOR=red]%sp.[/COLOR]" % self.parent.user["ballance"])
        
        self.portLabel.setLabel("%s (Проверяется)" % self.outport, "Проверка")

        thraddr = defines.MyThread(self.getAddr, None)
        thraddr.start()
        
        thrport = defines.MyThread(self.checkPort, self.outport)
        thrport.start()

    def printASStatus(self, text):
        if self.ASLabel:
            self.ASLabel.setLabel(text)

    def getAddr(self, params):
        data = defines.GET("http://2ip.ru/")
        beautifulSoup = BeautifulSoup(data)
        addr = beautifulSoup.find('big', attrs={'id': 'd_clip_button'})
        addr = addr.string
        self.addrLabel.setLabel(addr)
        
        print "InfoForm адрес получен"
        

    def checkPort(self, params):
        if not defines.checkPort(params):
            self.printCheckPort(params, False)
            return False
        else:
            self.printCheckPort(params, True)
            return True

    def printCheckPort(self, params, res=False):
        if self.portLabel:
            if res:
                self.portLabel.setLabel("%s ([COLOR=green]%s[/COLOR])" % (params, self.TEXT_YESPORT))
            else:
                self.portLabel.setLabel("%s ([COLOR=red]%s[/COLOR])" % (params, self.TEXT_NOPORT))
