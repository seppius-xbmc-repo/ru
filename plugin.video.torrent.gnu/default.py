#!/usr/bin/python
# Copyright (c) 2010-2011 ivi media. All rights reserved.
# Copyright (c) 2011 XBMC-Russia, HD-lab Team, E-mail: dev@hd-lab.ru
# Writer (c) 2011, Kostynoy S.A., E-mail: seppius2@gmail.com

import sys, os, xbmcaddon

__addon__ = xbmcaddon.Addon( id = 'plugin.video.torrent.gnu' )
sys.path.append( os.path.join( __addon__.getAddonInfo( 'path' ), 'resources', 'lib') )

if (__name__ == '__main__' ):
	import torr2xbmc
	torr2xbmc.addon_main()
