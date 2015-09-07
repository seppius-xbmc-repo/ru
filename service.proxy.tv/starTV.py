############################################################
# Copyright (C) Alex S.Galickiy 2015 - All Rights Reserved #
############################################################

# -*- coding: utf-8 -*-

import xbmc
import proxyTV
import epgTV

if __name__ == '__main__':
    xbmc.log('-----> START service.proxy.tv ' + epgTV.VERSION + ' <-----')
    proxyTV.updateAddonTv()
    proxyTV.updateProxyTv()
    proxyTV.updateEpgTv()
    proxyTV.start()
    xbmc.log('-----> FINISH service.proxy.tv ' + epgTV.VERSION + ' <-----')    
    