import xbmcaddon
import xbmc

ADDON = xbmcaddon.Addon( id = 'script.game.center' )
ADDON_PATH = ADDON.getAddonInfo('path')
ADDON_ICON	 = ADDON.getAddonInfo('icon')
SKIN_PATH = ADDON_PATH
GAMES_FOLDER = ADDON.getSetting("game.folder")

def showMessage(message = '', heading='Game Center', times = 6789):
    try: 
        xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, %s)' % (heading.encode('utf-8'), message.encode('utf-8'), times, ADDON_ICON))
    except Exception, e:
        try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, %s)' % (heading, message, times, ADDON_ICON))
        except Exception, e:
            xbmc.log( 'showMessage: exec failed [%s]' % e )