#!/usr/bin/python
# -*- coding: utf-8 -*-
#/*
# *      Copyright (C) 2011 Silen
# *
# */
import re, os, urllib, urllib2, cookielib, time, random, sys
from time import gmtime, strftime
from urlparse import urlparse

import subprocess, ConfigParser

import xbmc, xbmcgui, xbmcplugin, xbmcaddon

Addon = xbmcaddon.Addon(id='plugin.video.fepcom.net')
print Addon.getAddonInfo('path')
Addon_path = Addon.getAddonInfo('path').decode(sys.getfilesystemencoding())
print Addon_path
icon = xbmc.translatePath(os.path.join(Addon_path,'icon.png'))
fcookies = xbmc.translatePath(os.path.join(Addon_path, r'resources', r'data', r'cookies.txt'))
# load XML library
sys.path.append(os.path.join(Addon_path, r'resources', r'lib'))
#from BeautifulSoup  import BeautifulSoup
# load GUI
from Auth           import Auth

import HTMLParser
hpar = HTMLParser.HTMLParser()

#h = int(sys.argv[1])

def showMessage(heading, message, times = 3000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))


#-------------------------------------------------------------------------------
kwargs={'Addon': Addon}
au = Auth(**kwargs)
if au.Authorize() == True:
    au.showMain()
del au

