#!/usr/bin/python
# Copyright (c) 2011 Muzunga.TV, http://muzunga.tv/
# Writer (c) 2011, Muzunga.TV

import sys, os

sys.path.append(os.path.join(os.getcwd().replace(';', ''), 'resources', 'lib'))

if (__name__ == "__main__" ):
	import addon
	addon.addon_main()
