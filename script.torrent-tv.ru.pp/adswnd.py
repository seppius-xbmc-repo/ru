# Copyright (c) 2010-2011 Torrent-TV.RU
# Writer (c) 2011, Welicobratov K.A., E-mail: 07pov23@gmail.com
import xbmcgui

class AdsForm(xbmcgui.WindowXMLDialog):
    def __init__(self, *args, **kwargs):
        self.playing = False
