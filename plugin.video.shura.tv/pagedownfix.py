# -*- coding: utf-8 -*
#/*
import string, xbmc, xbmcgui, xbmcplugin, os, xbmcaddon

myPlayer=xbmc.PLAYER_CORE_AUTO
if 'tvshka' in xbmc.Player(myPlayer).getPlayingFile():
	xbmc.Player(myPlayer).playprevious()
	xbmc.log('[PageDownFixExceputed] in SHURA.TV')
else:
	xbmc.executebuiltin('PlayerControl(Previous)')
	xbmc.log('[PageDownFixExceputed] not in SHURA.TV')
#xbmc.log('[PageDownFixExceputed]')