#!/usr/bin/python
# Copyright (c) MEGOGO.NET. All rights reserved.
# Copyright (c) XBMC-Russia, HD-lab Team, E-mail: dev@hd-lab.ru
# Writer (c) 2012, Kostynoy S.A., E-mail: seppius2@gmail.com

import sys, os, xbmcaddon
__addon__=xbmcaddon.Addon(id='plugin.video.megogo.net')
_ADDON_PATH =   xbmc.translatePath(__addon__.getAddonInfo('path'))
if (sys.platform == 'win32') or (sys.platform == 'win64'):
	_ADDON_PATH = _ADDON_PATH.decode('utf-8')
sys.path.append( os.path.join( _ADDON_PATH, 'resources', 'lib') )
if (__name__ == '__main__' ):
	import megogo2xbmc
	megogo2xbmc.addon_main()
