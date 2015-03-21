#!/usr/bin/python
# -*- coding: utf-8 -*-
# © 2010-2011 ОАО «ВебТВ»

import sys, os

sys.path.append(os.path.join(os.getcwd().replace(';', ''), 'resources', 'lib'))

if (__name__ == "__main__" ):
	import zoomby2xbmc
	zoomby2xbmc.addon_main()
