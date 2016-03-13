###################################################################
# Copyright (C) Alexey S.Galickiy 2015-2016 - All Rights Reserved #
###################################################################

# -*- coding: utf-8 -*-

import xbmc
import epgTV
import xbmcgui
import proxyTV

if __name__ == '__main__':
    xbmc.log('-----> START service.proxy.tv ' + epgTV.VERSION + ' <-----')
    if proxyTV.updateAddonTv():
        if proxyTV.updateProxyTv():
            if proxyTV.updateEpgTv():
                start = True
            else: start = False
        else: start = False
    else: start = False
    if start:
        proxyTV.start()
    else:
        information = xbmcgui.Dialog()
        information.notification(proxyTV.CEPBEP_XPEH, proxyTV.KUHO_XPEH, xbmcgui.NOTIFICATION_INFO, 8000, False)
    xbmc.log('-----> FINISH service.proxy.tv ' + epgTV.VERSION + ' <-----')    
