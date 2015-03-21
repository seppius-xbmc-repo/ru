# -*- coding: utf-8 -*
#/*
import string, xbmc, xbmcgui, xbmcplugin, os, xbmcaddon

addon = xbmcaddon.Addon(id='plugin.video.shura.tv')
step = addon.getSetting('BigStepBackward')

myPlayer=xbmc.PLAYER_CORE_AUTO
try:
	item=xbmcgui.ListItem('', '', '', '')
	archiveName=str(xbmc.Player(myPlayer).getVideoInfoTag().getTitle())
	#xbmc.log('Name0='+archiveName)
	archiveurl=xbmc.Player(myPlayer).getPlayingFile().split('=')[0]
	#xbmc.log('url='+archiveurl)
	archivetime=xbmc.Player(myPlayer).getPlayingFile().split('=')[1]
	#xbmc.log('time1='+str(archivetime))
	playedtime=xbmc.Player(myPlayer).getTime()
	#xbmc.log('played time='+str(playedtime)+',step='+str(step*60))
	archivetime=int(archivetime)+int(playedtime)-int(step)*60
	#xbmc.log('time2='+str(archivetime))
	item.setInfo(type="Video", infoLabels={"Title": archiveName})
	url=archiveurl+'='+str(archivetime)
	#xbmc.log('url2='+url)
	xbmc.Player(myPlayer).play(url,listitem=item)
except:
	xbmc.log('[SHURA.TV] exception in OneMinBackward.py use default function for this key')
	xbmc.executebuiltin('PlayerControl(BigSkipBackward)')
#xbmc.log('[PageDownFixExceputed]')