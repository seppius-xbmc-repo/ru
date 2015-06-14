#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import xbmc
import xbmcgui
import xbmcplugin
import xbmcvfs
import socket
import xbmcaddon
import cookielib
import urllib2
import urllib
import datetime
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup

settings = xbmcaddon.Addon(id='script.module.YaTv')
language = settings.getLocalizedString
version = "0.0.1"
plugin = "YaTv" + version

import os
_ADDON_PATH_ =   xbmc.translatePath(settings.getAddonInfo('path'))
if (sys.platform == 'win32'):
	_ADDON_PATH_ = _ADDON_PATH_.decode('utf-8')

sys.path.append( os.path.join( _ADDON_PATH_, 'lib') )

import YaTv

br = 0
while 1==1:
    if br == 1: break
    else:
        for i in range (0,43200):
            if i == 0:
                YaTv.GetUpdateProg()
            if xbmc.abortRequested:
                br = 1
                break
            else: xbmc.sleep(1000) 
