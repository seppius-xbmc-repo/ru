# Copyright (c) 2013 Torrent-TV.RU
# Writer (c) 2011, Welicobratov K.A., E-mail: 07pov23@gmail.com

import xbmc
import xbmcaddon
import cPickle
import defines
import os

import mainform 
from okdialog import OkDialog

def checkPort(params):
    if not defines.checkPort(params):
        
        dialog = OkDialog("okdialog.xml", defines.SKIN_PATH, defines.ADDON.getSetting('skin'))
        dialog.setText("Порт %s закрыт. Для стабильной работы сервиса и трансляций, настоятельно рекомендуется его открыть." % defines.ADDON.getSetting('outport'))
        dialog.doModal()

if __name__ == '__main__':
    if not defines.ADDON.getSetting('skin'):
       defines.ADDON.setSetting('skin', 'st.anger')
    if defines.ADDON.getSetting("skin") == "default":
       defines.ADDON.setSetting("skin", "st.anger")
    if not defines.ADDON.getSetting("login"):
       defines.ADDON.setSetting("login", "anonymous")
       defines.ADDON.setSetting("password", "anonymous")

    thr = defines.MyThread(checkPort, defines.ADDON.getSetting("outport"))
    thr.start()

    print defines.ADDON_PATH
    print defines.SKIN_PATH
    w = mainform.WMainForm("mainform.xml", defines.SKIN_PATH, defines.ADDON.getSetting('skin'))
    w.doModal()
    defines.showMessage('Close plugin')
    del w
    