#!/usr/bin/python
# -*- coding: utf-8 -*-

import xbmc, xbmcaddon, xbmcgui, xbmcplugin
import os, sys, urllib2, re, time

__addon__       = xbmcaddon.Addon(id='plugin.video.megogo')
addon_name		= __addon__.getAddonInfo('name')
addon_version	= __addon__.getAddonInfo('version')
addon_path 		= xbmc.translatePath(__addon__.getAddonInfo('path')).decode('utf-8')
language        = __addon__.getLocalizedString
source          = 'http://raw.github.com/GeekEdem/zip/master/plugin.video.megogo/addon.xml'

sys.path.append(os.path.join(addon_path, 'resources', 'lib'))
from megogo2xbmc import getconfiguration
from sqlite import DataBase
db = DataBase()

xbmc.log('[%s]: Start plugin! Version: %s' % (addon_name, addon_version))

# ##################################	  Start Splash	    ####################################### #
splash = xbmcgui.WindowXML('splash.xml', addon_path)
splash.show()
xbmc.executebuiltin("ActivateWindow(busydialog)")

# ##################################		First run		####################################### #
if __addon__.getSetting('firstrun') == '0' or __addon__.getSetting('firstrun') == '':
    __addon__.openSettings()
    __addon__.setSetting(id='firstrun', value='1')

# ##################################  SET UI LANGUAGE 'RU'	####################################### #
if __addon__.getSetting('language') == '0' or __addon__.getSetting('language') == '':
    __addon__.setSetting(id='language', value='0')

# ##################################   WRITE TO DB ACCOUNT	####################################### #
usr = __addon__.getSetting('login')
pwd = __addon__.getSetting('password')
if not db.table_exist('account'):
    db.create_login_table()
if not usr and not pwd:
    db.clear_table('account')
    db.login_data_to_db('', '', __addon__.getSetting('quality'), __addon__.getSetting('audio_language'), __addon__.getSetting('subtitle_language'))
else:
    db.login_data_to_db(usr, pwd, __addon__.getSetting('quality'), __addon__.getSetting('audio_language'), __addon__.getSetting('subtitle_language'))
db.cookie_to_db("")
xbmc.executebuiltin("Dialog.Close(busydialog)")

# ##################################    CHECK NEW VERSION   ####################################### #
# xbmc.log('[%s]: Trying to get new version...' % addon_name)
# try:
#     request = urllib2.Request(url=source, headers={'s-Agent': 'MEGOGO Addon for XBMC/Kodi'})
#     request = urllib2.urlopen(request)
#     http = request.read()
#     request.close()
#
#     p = re.compile('name="MEGOGO\WNET"\W.*?version="([^"]*?)"')
#     branch_release = re.search(p, http).group(1)
#     xbmc.log('[%s]: Branch version - %s' % (addon_name, branch_release))
#
#     if addon_version != branch_release:
#         dialog = xbmcgui.Dialog()
#         dialog.ok(language(1033), language(1034))
#         del dialog
# except Exception as e:
#     xbmc.log('[%s]: ERROR getting branch version! %s' % (addon_name, e))
#
# ##################################        START UI        ####################################### #
if getconfiguration():    # Get config from MEGOGO
    import Screens
    home = Screens.Back('back.xml', addon_path, splash=splash)
    home.doModal()
    xbmc.log('!!! RETURN TO START !!!')
    del home
else:
    dialog = xbmcgui.Dialog()
    dialog.ok(language(1025), language(1031), language(1032))
    del dialog
    splash.close()

# ##################################        CLOSE APP        ####################################### #
xbmc.log('[%s]: TRY CLOSE APP!!!' % addon_name)
dic = db.get_login_from_db()
db.close_db()
__addon__.setSetting(id='login', value=dic['login'])
__addon__.setSetting(id='password', value=dic['password'])
xbmc.log('[%s]: Close plugin. Version: %s' % (addon_name, addon_version))
