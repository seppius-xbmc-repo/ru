import xbmc
import xbmcaddon

import source
import gui

ADDON = xbmcaddon.Addon(id = 'script.yandex.tvguide')

if __name__ == '__main__':
    w = gui.TVGuide( source.XMLYandex({'cache.path': xbmc.translatePath(ADDON.getAddonInfo('profile')) }) )
    w.doModal()
    del w
