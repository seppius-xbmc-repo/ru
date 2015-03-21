#!/usr/bin/python
# Copyright (c) 2010-2011 ivi media. All rights reserved.
# Copyright (c) 2011 XBMC-Russia, HD-lab Team, E-mail: dev@hd-lab.ru
# Writer (c) 2011, Kostynoy S.A., E-mail: seppius2@gmail.com

import sys, xbmcaddon

_id='plugin.video.ivi.ru'
#resources directory
_resdir = "special://home/addons/" + _id + "/resources"
#add our library to python search path
sys.path.append(xbmc.translatePath( _resdir + "/lib/"))

if (__name__ == '__main__' ):
	import ivi2xbmc
	ivi2xbmc.addon_main()
