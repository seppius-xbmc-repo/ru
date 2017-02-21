# -*- coding: utf-8 -*
#/*
import string, xbmc, xbmcgui, xbmcplugin, os, xbmcaddon

if 'tvshka' in xbmc.Player().getPlayingFile():
	xbmc.Player().playprevious()
	xbmc.log('[PageDownFixExceputed] in SHURA.TV')
else:
	xbmc.executebuiltin('PlayerControl(Previous)')
	xbmc.log('[PageDownFixExceputed] not in SHURA.TV')
#xbmc.log('[PageDownFixExceputed]')