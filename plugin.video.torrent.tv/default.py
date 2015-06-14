#!/usr/bin/python
# Copyright (c) 2010-2011 ivi media. All rights reserved.
# Copyright (c) 2011 XBMC-Russia, HD-lab Team, E-mail: dev@hd-lab.ru
# Writer (c) 2011, Welicobratov K.A., E-mail: powerdeth@narod.ru
import sys, os, xbmcaddon

__addon__ = xbmcaddon.Addon( id = 'plugin.video.torrent.tv' )
_ADDON_PATH =   xbmc.translatePath(__addon__.getAddonInfo('path'))
if (sys.platform == 'win32'):
	_ADDON_PATH = _ADDON_PATH.decode('utf-8')
sys.path.append( os.path.join( _ADDON_PATH, 'resources', 'lib') )

if (__name__ == '__main__' ):
	import torr2xbmc
	torr2xbmc.addon_main()