# -*- coding: utf-8 -*-

import xbmcgui, xbmc, urllib
#import demjson3 as json

SERIAL_NAME = 100

class PlayerDialog(xbmcgui.WindowXMLDialog):
  def __init__(self, *args, **kwargs):
    #xbmcgui.WindowXMLDialog.__init__(self)
    self.playlist   = kwargs.get('playlist')
    self.name       = kwargs.get('name')
    self.Auth       = kwargs.get('Auth')

  def onInit(self):
    xbmcgui.WindowXMLDialog.onInit(self)
    #self.getControl(SERIAL_NAME).setLabel(self.name)
    #---
    self.Auth.player.play(self.playlist)
    self.close()