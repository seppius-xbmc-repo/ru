# Copyright (c) 2010-2011 Torrent-TV.RU
# Writer (c) 2011, Welicobratov K.A., E-mail: 07pov23@gmail.com
import xbmcgui
import xbmc
import xbmcgui

class OkDialog(xbmcgui.WindowXMLDialog):
    LABEL_USER_LOGIN = 101
    LABEL_USER_BALANCE = 102
    LABEL_AS_STATUS = 103
    LABEL_AS_PORT = 104
    LABEL_ADDR = 105

    TEXT_NOPORT = "Закрыт"
    TEXT_YESPORT = "Открыт"

    def __init__(self, *args, **kwargs):
        self.text = ""
        pass

    def onInit(self):
        self.getControl(1).setText(self.text)

    def setText(self, text):
        self.text = text
