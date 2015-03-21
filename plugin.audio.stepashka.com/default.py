#!/usr/bin/python


import sys, os, xbmcaddon

__addon__ = xbmcaddon.Addon( id = 'plugin.audio.stepashka.com' )
sys.path.append( os.path.join( __addon__.getAddonInfo( 'path' ), 'resources', 'lib') )

if (__name__ == '__main__' ):
	import ivi2fstep
	ivi2fstep.addon_main()
