############################################################
# Copyright (C) Alex S.Galickiy 2015 - All Rights Reserved #
############################################################

# -*- coding: utf-8 -*-

import xbmc
import xbmcgui
import xbmcaddon
import urllib
import epgTV
import time
import sys
import re
import os

MANUAL_SEARCH = u'Автонастройка каналов. Ждите...'
MANUAL_SEARCH_LOGO = u'Автонастройка. Загрузка логотипов. Ждите...'
SERVICE_XPEH = u'Ошибка ProxyTV!'
ADDON_XPEH = u'Включите дополнение PVR IPTV Simple Client!\nПерезагрузите KODI!'
SERVICE_EPG = u'Сообщение'
CREATE_EPG = u'Требуется обновление программы.\nЖелаете обновить EPG?'

LINK_TVBOX = 'http://tvbox.link/'
LINK = LINK_TVBOX + 'proxytv/'
LINK_PLIST = LINK + 'plist/'
LINK_NOTV = LINK + 'notv/'
LINK_LOGO = LINK + 'logo/'
LINK_VERIFY = LINK + 'verify.php'
LINK_NOTV_FILE = LINK_NOTV + 'notv.mp4'

SERVICE_NAME = 'service.proxy.tv'
SERVICE_START = xbmcaddon.Addon(id=SERVICE_NAME);
SERVICE_PATH = xbmc.translatePath(SERVICE_START.getAddonInfo('path')).decode('utf-8')

ADDON_NAME = 'pvr.iptvsimple'

bckgrnd_notv = os.path.join(SERVICE_PATH, 'img', 'notv.jpg')
pathFileM3U = os.path.join(SERVICE_PATH, 'M3U', 'epgiptv.m3u')
pathFileEPG = os.path.join(SERVICE_PATH,'EPG','epgiptv.xml')
pathLOGO = os.path.join(SERVICE_PATH,'LOGO')

TIMER = 3
TIMEOUT = 10
LIST_PROXY = []

urllib.socket.setdefaulttimeout(TIMEOUT)

class notvWindow(xbmcgui.Window):

    def __init__(self):
        if SERVICE_START.getSetting('logo') == 'true':
            MANUAL = MANUAL_SEARCH_LOGO
            x1 = 420
        else:
            MANUAL = MANUAL_SEARCH
            x1 = 480
        self.addControl(xbmcgui.ControlImage(0, 0, 1280, 720, bckgrnd_notv))
        self.strActionInfo = xbmcgui.ControlLabel(x1, 285, 600, 100, '', 'font13', '0xFFFFFFFF')
        self.addControl(self.strActionInfo)
        self.strActionInfo.setLabel(MANUAL) 

    def closeWindow (self):
        self.close()
   
def downLoadFile(pathFile, nameFile):
    work = True
    while work:
        try:
            downLDF = urllib.urlopen(LINK_PLIST + nameFile)
            fileLDF = open(pathFile, 'wb')
            fileLDF.write(downLDF.read())
            fileLDF.close()
            work = False
        except:
            work = True

def getGroup(id):
    group = 'РАЗНОЕ'
    pathFile = os.path.join(SERVICE_PATH, 'plist', 'plistGRPall')
    fGroup = open(pathFile,'r')
    for line in fGroup:
        lineGroup = line.split('|')
        if lineGroup[2].find(id)>-1:
            lineChannel = lineGroup[2].split(',')
            for channel in lineChannel:
                if channel == id:
                    group = lineGroup[1]
                    break
    fGroup.close()
    return group
    
def createPlist():
    userUTC = SERVICE_START.getSetting('timeZone')
    pathFile = os.path.join(SERVICE_PATH, 'plist', 'plistGRPall')
    downLoadFile(pathFile, 'plistGRPall')
    pathFile = os.path.join(SERVICE_PATH, 'plist', 'plistALLall')
    downLoadFile(pathFile, 'plistALLall')
    fileM3U = open(pathFileM3U, 'w')
    fileM3U.write('#EXTM3U tvg-autor="Alex S.Galickiy service.proxy.tv for KODI on '+LINK_TVBOX+'"\n')
    fUDP = open(pathFile,'r')
    for line in fUDP:
        channelId=line.split('|')
        if channelId[1].find('_') == -1:
            idCH = channelId[1]
            chTitle = channelId[2]
            udp = channelId[3]
            provider = channelId[5]
            serviceUTC = channelId[6]
            tvgSHIFT = str(int(userUTC) - int(serviceUTC))
            if SERVICE_START.getSetting('logo') == 'true':
                downLoGo(idCH)
            group=getGroup(idCH)
            proxy, notv = assignProxy(provider)
            fileM3U.write('#EXTINF:-1 tvg-shift="'+tvgSHIFT+'" tvg-id="'+str(idCH)+'" tvg-logo="'+str(idCH)+'.png" group-title="'+group+'",'+chTitle+'\n')
            if notv:
                fileM3U.write(proxy+'\n')
            else:
                fileM3U.write(proxy+'udp/'+udp+'\n')
    if SERVICE_START.getSetting('logo') == 'true':
        SERVICE_START.setSetting('logo','false')
    fUDP.close()
    fileM3U.close()

def downLoGo(idChannel):
    nameFile = str(idChannel) + '.png';
    pathFile = os.path.join(SERVICE_PATH, 'LOGO', nameFile)
    try:
        dwnLogo = urllib.urlopen(LINK_LOGO + nameFile)
        fileLogo = open(pathFile, 'wb')
        fileLogo.write(dwnLogo.read())
        fileLogo.close()
    except:
        return False
    else:
        return True

def assignProxy(provider):
    for proxy in LIST_PROXY:
        if proxy[0] == provider:
            udpxy = 'http://'+proxy[1]+':'+proxy[2]+'/'
            notv = False
            break
        else:
            udpxy = LINK_NOTV_FILE
            notv = True
    return udpxy, notv

def getAllProxy():
    work = True
    while work:
        try:
            verProxy = urllib.urlopen(LINK_VERIFY)
            for lineProxy in verProxy.readlines():
                dataProxy = lineProxy.split('|')
                provider = dataProxy[2]
                host = dataProxy[0]
                port = dataProxy[1]
                LIST_PROXY.append([provider, host, port])
            work = False
        except:
            work = True
    return LIST_PROXY

def testProxy(index):
    lineIndex = 1
    try:
        fileM3U = open(pathFileM3U, 'r')
        for line in fileM3U:
            if lineIndex == int(index) * 2 + 3:
                break
            lineIndex += 1
        fileM3U.close()
        try:
            openUDP = urllib.urlopen(line)
            if openUDP.read(65536):
                test = True
            else:
                test = False
        except:
            test = False
    except:
        test = False
    return test

def startSetupIPTV():
    setupIPTV = notvWindow()
    setupIPTV.show()
    LIST_PROXY = []
    LIST_PROXY = getAllProxy()
    createPlist()
    setupIPTV.closeWindow()
    restartPvr()
    del setupIPTV

def restartPvr():
    xbmc.sleep(TIMER * 500)
    xbmc.executebuiltin('XBMC.StartPVRManager')
    xbmc.sleep(TIMER * 500)

def start():
    if SERVICE_START.getSetting('timeZone') == 'NO':
        work = False
    else:
        isFILE = ''
        work = True
        noPLAY = False
        epgYes = True
        waitAbort = xbmc.Monitor()
        if SERVICE_START.getSetting('autoSetupPVR') == 'true':
            setupIPTVsimple()
            SERVICE_START.setSetting('autoSetupPVR', 'false')
        if SERVICE_START.getSetting('autoSetupTV') == 'true':
            startSetupIPTV()
    while work:
        if xbmc.abortRequested or waitAbort.waitForAbort(TIMER):
            break
        else:
            if not os.path.exists(pathFileEPG):
                timeEpg = True
            else:
                timeEpg = int((time.time() - os.stat(pathFileEPG).st_mtime) / 3600) > 21
            if timeEpg:
                if epgYes:
                    dialogYES_NO = xbmcgui.Dialog()
                    if dialogYES_NO.yesno(SERVICE_EPG, CREATE_EPG):
                        epgTV.createEpg()
                        stopPlayer()
                        restartPvr()
                    else:
                        epgYes = False
            try:
                fileNAME = xbmc.Player().getPlayingFile()
                if fileNAME.find('.pvr') != -1:
                    if isFILE != fileNAME:
                        isFILE = fileNAME
                        noPLAY = True
                elif noPLAY:
                    noPLAY = False
            except:
                if noPLAY:
                    strIndex = re.findall('[0-9]+', isFILE)
                    if not testProxy(strIndex[0]):
                        startSetupIPTV()
                        noPLAY = False
                        epgYes = True
                        isFILE = ''
                    else:
                        noPLAY = False

def setupIPTVsimple():
    try:
        ADDON_IPTV = xbmcaddon.Addon(id=ADDON_NAME)
        ADDON_PATH = xbmc.translatePath(ADDON_IPTV.getAddonInfo('path')).decode('utf-8')
    except:
        infoDialog(SERVICE_XPEH, ADDON_XPEH)
        sys.exit()
    else:
        transPath = xbmc.translatePath('special://home').decode('utf-8')
        pathSimple = os.path.join(transPath,'userdata','addon_data','pvr.iptvsimple')
        data = '<settings>\n<setting id="epgCache" value="false" />\n<setting id="epgPath" value="'+xbmc.translatePath(pathFileEPG)+'" />\n'
        data += '<setting id="epgPathType" value="0" />\n<setting id="epgTSOverride" value="false" />\n';
        data += '<setting id="epgTimeShift" value="0.000000" />\n<setting id="epgUrl" value="" />\n';
        data += '<setting id="logoBaseUrl" value="" />\n<setting id="logoPath" value="'+xbmc.translatePath(pathLOGO)+'" />\n';
        data += '<setting id="logoPathType" value="0" />\n<setting id="m3uCache" value="false" />\n'
        data += '<setting id="m3uPath" value="'+xbmc.translatePath(pathFileM3U)+'" />\n<setting id="m3uPathType" value="0" />\n';
        data += '<setting id="m3uUrl" value="" />\n<setting id="sep1" value="" />\n<setting id="sep2" value="" />\n';
        data += '<setting id="sep3" value="" />\n<setting id="startNum" value="1" />\n</settings>'
        if not os.path.exists(pathSimple):
            os.mkdir(pathSimple)
        if os.path.exists(pathSimple):
            setSimFile = open(os.path.join(pathSimple, 'settings.xml'),'w')
            setSimFile.write(data)
            setSimFile.close()

def updateProxyTv():
    work = True
    pathFileProxy = os.path.join(SERVICE_PATH, 'proxyTV.py')
    while work:
        try:
            upFile = urllib.urlopen(LINK + 'proxyTV.py')
            fileUp = open(pathFileProxy, 'wb')
            fileUp.write(upFile.read())
            fileUp.close()
            work = False
        except:
            work = True

def updateEpgTv():
    work = True
    pathFileEpg = os.path.join(SERVICE_PATH, 'epgTV.py')
    while work:
        try:
            upFile = urllib.urlopen(LINK + 'epgTV.py')
            fileUp = open(pathFileEpg, 'wb')
            fileUp.write(upFile.read())
            fileUp.close()
            work = False
        except:
            work = True

def updateAddonTv():
    work = True
    pathFileXml = os.path.join(SERVICE_PATH, 'addon.xml')
    while work:
        try:
            upFile = urllib.urlopen(LINK + 'addon.xml')
            fileUp = open(pathFileXml, 'wb')
            fileUp.write(upFile.read())
            fileUp.close()
            work = False
        except:
            work = True

def stopPlayer():
    if xbmc.Player().isPlaying():
        xbmc.Player().stop()

def infoDialog(title, msg):
    Dialog = xbmcgui.Dialog()
    return Dialog.ok(title, msg)