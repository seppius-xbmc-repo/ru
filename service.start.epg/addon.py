############################################################
# Copyright (C) Alex S.Galickiy 2015 - All Rights Reserved #
############################################################

# -*- coding: utf-8 -*-
import os, xbmc, xbmcaddon, urllib, time

SCRIPT_NAME = 'script.epg.iptv'
SCRIPT_EPG = xbmcaddon.Addon(id=SCRIPT_NAME);
SCRIPT_PATH = xbmc.translatePath(SCRIPT_EPG.getAddonInfo('path')).decode('utf-8')
SERVICE_NAME = 'service.start.epg'
SERVICE_START = xbmcaddon.Addon(id=SERVICE_NAME);
TIMER = int(SERVICE_START.getSetting('startScript'))

def getFolder(catalog=None,file=None):
    PATHfolder=os.path.join(SCRIPT_PATH,catalog,file);
    return PATHfolder

def lifeProxy():
    host = ''
    port = ''
    udpTV = ''
    try:
        playList=open(getFolder('M3U','epgiptv.m3u'),'r')
    except:
        return False, host, port, udpTV
    for line in playList:
        proxyHost = line.find('udp')
        if proxyHost!=-1:
            proxyM3U = line.split('/')
            break
    playList.close()
    hostPort = proxyM3U[2].split(':')
    host = hostPort[0]
    udpTV = proxyM3U[4].replace('\n','')
    if host.find('@')==-1:
        port = hostPort[1]
        try:
            data=urllib.urlopen('http://'+host+':'+port+'/status')
            if data.code==200:
                return True, host, port, udpTV
        except: 
            return False, host, port, udpTV
    else:  
        return False, host, port, udpTV

def stopPlayer():
    if xbmc.Player().isPlaying():
        xbmc.log('-----> Stop the Player <-----')
        xbmc.Player().stop()

def searchProxy():
    boolean, host, port, udpTV = lifeProxy()
    if boolean:
        try:
            openUDP = urllib.urlopen('http://'+host+':'+port+'/udp/'+udpTV)
            if openUDP.read(8):
                searchEPG()
            else:
                stopPlayer()
                xbmc.executebuiltin('XBMC.RunAddon('+SCRIPT_NAME+')')
        except:
            stopPlayer()
            xbmc.executebuiltin('XBMC.RunAddon('+SCRIPT_NAME+')')
    else:
        stopPlayer()
        xbmc.executebuiltin('XBMC.RunAddon('+SCRIPT_NAME+')')

def searchEPG():
    fileEPG = getFolder('EPG','epgiptv.xml')
    if int((time.time() - os.stat(fileEPG).st_mtime)/3600)>22:
        stopPlayer()
        xbmc.executebuiltin('XBMC.RunAddon('+SCRIPT_NAME+')')

def startService():
    waitAbort = xbmc.Monitor()
    while True:
        xbmc.log('-----> Verification PROXY&EPG <-----')
        searchProxy()
        if xbmc.abortRequested or waitAbort.waitForAbort(TIMER):
            break

xbmc.log('-----> START service for script.epg.iptv <-----')
startService()
xbmc.log('-----> FINISH service for script.epg.iptv <-----')