###################################################################
# Copyright (C) Alexey S.Galickiy 2015-2016 - All Rights Reserved #
###################################################################

# -*- coding: utf-8 -*-

import xbmc
import xbmcgui
import xbmcaddon
import xml.etree.ElementTree as ET
import datetime
import urllib2
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
SETUP_IPTV = u'Желаете сменить прокси?'
NO_PROXY = 'NO_PROXY'
SESION_DUR = u'Длительность сеанса (мин): '
ID_GA = 'UA-71267915-4'
USER_AGENT_GA = {'User-Agent': 'ProxyTV-Browser'}
HOST_GA = 'http://www.google-analytics.com/__utm.gif'

LINK_TVBOX = 'http://tvbox.link/'
LINK = LINK_TVBOX + 'proxytv/'
LINK_PLIST = LINK + 'plist/'
LINK_NOTV = LINK + 'notv/'
LINK_LOGO = LINK + 'logo/'
LINK_VERIFY = LINK + 'verify.php'
LINK_NOTV_FILE = LINK_NOTV + 'notv.mp4'

ADDON_NAME = 'pvr.iptvsimple'
PLUGIN_NAME = 'ProxyTV'
SERVICE_NAME = 'service.proxy.tv'
SERVICE_START = xbmcaddon.Addon(id=SERVICE_NAME);
SERVICE_PATH = xbmc.translatePath(SERVICE_START.getAddonInfo('path')).decode('utf-8')
PARAMS = HOST_GA + '?utmhn=tvbox.link&utmp=&utmac='+ID_GA+'&utmcc=__utma%3D999.999.999.999.999.1%3B'
TEXT_LIST_PROXY = u'Сервер не ответил! Настройки не изменились!'
CEPBEP_XPEH = u'ProxyTV'
KUHO_XPEH = u'Сервер не ответил. Завершение работы......................................'

bckgrnd_notv = os.path.join(SERVICE_PATH, 'img', 'notv.jpg')
pathFileM3U = os.path.join(SERVICE_PATH, 'M3U', 'epgiptv.m3u')
pathFileEPG = os.path.join(SERVICE_PATH,'EPG','epgiptv.xml')
pathLOGO = os.path.join(SERVICE_PATH,'LOGO')

TIMER = 3
TIMEOUT = 30

class notvWindow(xbmcgui.Window):

    def __init__(self):
        if SERVICE_START.getSetting('logo') == 'true':
            MANUAL = MANUAL_SEARCH_LOGO
            x1 = 420
        else:
            MANUAL = MANUAL_SEARCH
            x1 = 480
        self.addControl(xbmcgui.ControlImage(0, 0, 1280, 720, xbmc.translatePath(bckgrnd_notv)))
        self.strActionInfo = xbmcgui.ControlLabel(x1, 285, 600, 100, '', 'font13', '0xFFFFFFFF')
        self.addControl(self.strActionInfo)
        self.strActionInfo.setLabel(MANUAL)

    def closeWindow (self):
        self.close()

def downLoGo(idChannel):
    urllib.socket.setdefaulttimeout(TIMEOUT)
    try:
        nameFile = str(idChannel) + '.png'
        dwnLogo = urllib.urlopen(LINK_LOGO + nameFile)
        codeURL = dwnLogo.getcode()
        if codeURL == 200:
            pathFile = os.path.join(xbmc.translatePath(pathLOGO), nameFile)
            fileLogo = open(pathFile, 'wb')
        else:
            nameFile = 'icon.png'
            dwnLogo = urllib.urlopen(LINK_LOGO + nameFile)
            pathFile = os.path.join(xbmc.translatePath(pathLOGO), nameFile)
            fileLogo = open(pathFile, 'wb')
        fileLogo.write(dwnLogo.read())
        fileLogo.close()
    except:
        return False

def downLoadFile(pathFile, nameFile):
    urllib.socket.setdefaulttimeout(TIMEOUT)
    try:
        downLDF = urllib.urlopen(LINK_PLIST + nameFile)
        fileLDF = open(pathFile, 'wb')
        fileLDF.write(downLDF.read())
        fileLDF.close()
        return True
    except:
        return False

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
    
def createPlist(listProxy, proxyIp):
    providerDuble = ''
    if proxyIp != 'NO_PROXY':
        proxyNo = proxyIp.split('/')
        proxyPort = proxyNo[2]
    else:
        proxyPort = proxyIp
    userUTC = SERVICE_START.getSetting('timeZone')
    noListChannel = SERVICE_START.getSetting('noListChannel')
    pathFile = os.path.join(SERVICE_PATH, 'plist', 'plistGRPall')
    if noListChannel != 'true':
        downLoadFile(pathFile, 'plistGRPall')
    pathFile = os.path.join(SERVICE_PATH, 'plist', 'plistALLall')
    if noListChannel != 'true':
        downLoadFile(pathFile, 'plistALLall')
    fileM3U = open(pathFileM3U, 'w')
    fileM3U.write('#EXTM3U tvg-autor="Alexey S.Galickiy service.proxy.tv for KODI on '+LINK_TVBOX+'"\n')
    fUDP = open(pathFile,'r')
    for line in fUDP:
        channelId=line.split('|')
        if channelId[1].find('_') == -1:
            idCH = channelId[1]
            chTitle = channelId[2]
            udp = channelId[3]
            provider = channelId[5]
            serviceUTC = channelId[6]
            noProxy = int(channelId[8])
            tvgSHIFT = str(int(userUTC) - int(serviceUTC))
            if SERVICE_START.getSetting('logo') == 'true':
                downLoGo(idCH)
            group=getGroup(idCH)
            pathLg = os.path.join(xbmc.translatePath(pathLOGO), str(idCH)+'.png')
            if not os.path.exists(pathLg):
                tvgLogo = 'icon.png'
            else:
                tvgLogo = str(idCH)+'.png'
            if noProxy == 1:
                if providerDuble != provider:
                    proxy, notv = assignProxy(provider, listProxy, proxyPort)
                    providerDuble = provider
                if notv:
                    ProxyTV = proxy
                else:
                    ProxyTV = proxy+'udp/'+udp
            else:
                notv = False
                ProxyTV = udp
            fileM3U.write('#EXTINF:-1 tvg-shift="'+tvgSHIFT+'" tvg-id="'+str(idCH)+'" tvg-logo="'+tvgLogo+'" group-title="'+group+'",'+chTitle+'\n')
            fileM3U.write(ProxyTV+'\n')
    if SERVICE_START.getSetting('logo') == 'true':
        SERVICE_START.setSetting('logo','false')
    fUDP.close()
    fileM3U.close()

def searchClient(udpxy):
    urllib.socket.setdefaulttimeout(TIMEOUT)
    try:
        startTime = time.time()
        dataUdpxy = urllib.urlopen(udpxy+'status')
        endTime = time.time()
        timeProxy = str(int((endTime - startTime)*1000))
        data = dataUdpxy.read()
        table = re.findall('<td>[0-9]+', data)
        clients = table[3].replace('<td>','')
    except:
        clients = -1
        timeProxy = 0
    return clients, timeProxy

def assignProxy(provider, listProxy, proxyIP):
    for proxy in listProxy:
        if proxy[0] == provider:
            proxyPort = proxy[1]+':'+proxy[2]
            udpxy = 'http://'+proxyPort+'/'
            client, time = searchClient(udpxy)
            if int(client) == 0 or int(client) == 1 or int(client) == 2:
                notv = False
                if proxyPort != proxyIP:
                    break
            else:
                udpxy = LINK_NOTV_FILE
                notv = True
        else:
            udpxy = LINK_NOTV_FILE
            notv = True
    return udpxy, notv

def workFalse(work):
    information = xbmcgui.Dialog()
    information.notification(PLUGIN_NAME, TEXT_LIST_PROXY, xbmcgui.NOTIFICATION_INFO, 5000, work)

def getAllProxy(LIST_PROXY): 
    urllib.socket.setdefaulttimeout(TIMEOUT)
    try:
        verProxy = urllib.urlopen(LINK_VERIFY)
        for lineProxy in verProxy.readlines():
            dataProxy = lineProxy.split('|')
            provider = dataProxy[2]
            host = dataProxy[0]
            port = dataProxy[1]
            LIST_PROXY.append([provider, host, port])
            work = True
    except:
        work = False
        workFalse(work)
    return LIST_PROXY, work

def testProxy():
    lineIndex = 1
    try:
        fileM3U = open(pathFileM3U, 'r')
        for line in fileM3U:
            if lineIndex == 3:
                break
            lineIndex += 1
        fileM3U.close()
        test = line
    except:
        test = NO_PROXY
    return test

def startSetupIPTV(noProxy):
    LIST_PROXY = []
    setupIPTV = notvWindow()
    setupIPTV.show()
    xbmc.executebuiltin('XBMC.Playlist.Clear')
    listProxy, work = getAllProxy(LIST_PROXY)
    if work:
        createPlist(listProxy, noProxy)
        setupIPTV.closeWindow()
        restartPvr()
    else:
        setupIPTV.closeWindow()    
    del setupIPTV 
    urllib.socket.setdefaulttimeout(TIMEOUT)
    try:
        reqGA = urllib2.Request(PARAMS, headers = USER_AGENT_GA)
        opGA = urllib2.urlopen(reqGA)
        readGA = opGA.read()
        xbmc.log('-----> OPEN GA <-----')
    except:
        xbmc.log('-----> ERROR GA <-----')

def restartPvr():
    xbmc.sleep(TIMER * 500)
    xbmc.executebuiltin('XBMC.StartPVRManager')
    xbmc.sleep(TIMER * 500)

def createEPG():
    epgTV.createEpg()
    stopPlayer()
    restartPvr()

def start():
    if not updateSettings():
        return False
    else:
        if not updateStarTv():
            return False 
    hourEPG = int(SERVICE_START.getSetting('startEPG'))
    startTimeEPG = datetime.time(hourEPG,0,0,0)
    startEpgHour = datetime.timedelta(hours=startTimeEPG.hour).seconds
    if SERVICE_START.getSetting('timeZone') == 'NO':
        work = False
    else:
        work = True
        noPLAY = False
        yesEPG = False
        sizeBuff = createAdv()
        longUDPXY = int(SERVICE_START.getSetting('noUDPXY'))
        if sizeBuff > 0:
            setupAdvanced(sizeBuff)
        if not os.path.exists(pathFileEPG):
            timeEPG = True
        else:
            timeEPG = int((time.time() - os.stat(pathFileEPG).st_mtime) / 3600) > 21
        if SERVICE_START.getSetting('autoSetupPVR') == 'true':
            setupIPTVsimple()
            SERVICE_START.setSetting('autoSetupPVR', 'false')
        if SERVICE_START.getSetting('autoSetupTV') == 'true':
            startSetupIPTV(NO_PROXY)
        if SERVICE_START.getSetting('advanced') == 'true':
            SERVICE_START.setSetting('advanced', 'false')
    while work:
        if xbmc.abortRequested:
            break
        else:
            xbmc.sleep(TIMER * 1000)
            currentTime = datetime.datetime.now().time()
            currentHour = datetime.timedelta(hours=currentTime.hour).seconds
            startEPG = startEpgHour-currentHour
            if timeEPG:
                createEPG()
                timeEPG = False
            if startEPG > 0:
                yesEPG = True
            if startEPG < 0:
                yesEPG = False
            if startEPG == 0 and yesEPG:
                createEPG()
                yesEPG = False
            try:
                fileNAME = xbmc.Player().getPlayingFile()
                if fileNAME.find('.pvr') != -1:
                    noPLAY = True
            except:
                if noPLAY:
                    test = testProxy()
                    endTime = time.time()
                    allTime = int((endTime-startTime)/60)
                    if longUDPXY != 0:
                        if longUDPXY > allTime:
                            stopPlayer()
                            startSetupIPTV(test)
                startTime = time.time()
                noPLAY = False

def setupIPTVsimple():
    try:
        ADDON_IPTV = xbmcaddon.Addon(id=ADDON_NAME)
        ADDON_PATH = xbmc.translatePath(ADDON_IPTV.getAddonInfo('path')).decode('utf-8')
    except:
        epgTV.infoDialog(SERVICE_XPEH, ADDON_XPEH)
        sys.exit()
    else:
        transPath = xbmc.translatePath('special://home').decode('utf-8')
        pathSimple = os.path.join(transPath,'userdata','addon_data','pvr.iptvsimple')
        data = '<settings>\n<setting id="epgCache" value="false" />\n<setting id="epgPath" value="'+xbmc.translatePath(pathFileEPG)+'" />\n'
        data += '<setting id="epgPathType" value="0" />\n<setting id="epgTSOverride" value="false" />\n'
        data += '<setting id="epgTimeShift" value="0.000000" />\n<setting id="epgUrl" value="" />\n'
        data += '<setting id="logoBaseUrl" value="" />\n<setting id="logoFromEpg" value="0"/>\n'
        data += '<setting id="logoPath" value="'+xbmc.translatePath(pathLOGO)+'" />\n'
        data += '<setting id="logoPathType" value="0" />\n<setting id="m3uCache" value="false" />\n'
        data += '<setting id="m3uPath" value="'+xbmc.translatePath(pathFileM3U)+'" />\n<setting id="m3uPathType" value="0" />\n'
        data += '<setting id="m3uUrl" value="" />\n<setting id="sep1" value="" />\n<setting id="sep2" value="" />\n'
        data += '<setting id="sep3" value="" />\n<setting id="startNum" value="1" />\n</settings>'
        if not os.path.exists(pathSimple):
            os.mkdir(pathSimple)
        if os.path.exists(pathSimple):
            setSimFile = open(os.path.join(pathSimple, 'settings.xml'),'w')
            setSimFile.write(data)
            setSimFile.close()

def setupAdvanced(szBuff):
        transPath = xbmc.translatePath('special://home').decode('utf-8')
        pathAdvanced = os.path.join(transPath,'userdata','advancedsettings.xml')
        data = '<advancedsettings>\n<network>\n'
        data += '<buffermode>2</buffermode>\n'
        data += '<cachemembuffersize>252420</cachemembuffersize>\n'
        data += '<readbufferfactor>5</readbufferfactor>\n'
        data += '</network>\n<pvr>\n'
        data += '<minvideocachelevel> '+ str(szBuff) + '</minvideocachelevel>\n'
        data += '<maxvideocachelevel>100</maxvideocachelevel>\n'
        data += '</pvr>\n</advancedsettings>'
        setAdvFile = open(pathAdvanced,'w')
        setAdvFile.write(data)
        setAdvFile.close()

def createAdv():
    transPath = xbmc.translatePath('special://home').decode('utf-8')
    pathSettings = os.path.join(transPath,'userdata','addon_data','service.proxy.tv','settings.xml')
    tree = ET.parse(pathSettings)
    root = tree.getroot()
    for advanced in root:
        if advanced.get('id') == 'advanced' and advanced.get('value') == 'true':
            for buffer in root:
                if buffer.get('id') == 'minBuff':
                    val = int(buffer.get('value'))
                    return val
        else:
            val = 0
            return val

def updateStarTv():
    urllib.socket.setdefaulttimeout(TIMEOUT)
    pathFileProxy = os.path.join(SERVICE_PATH, 'starTV.py')
    try:
        upFile = urllib.urlopen(LINK + 'starTV.py')
        fileUp = open(pathFileProxy, 'wb')
        fileUp.write(upFile.read())
        fileUp.close()
        return True
    except:
        return False

def updateProxyTv():
    urllib.socket.setdefaulttimeout(TIMEOUT)
    pathFileProxy = os.path.join(SERVICE_PATH, 'proxyTV.py')
    try:
        upFile = urllib.urlopen(LINK + 'proxyTV.py')
        fileUp = open(pathFileProxy, 'wb')
        fileUp.write(upFile.read())
        fileUp.close()
        return True
    except:
        return False

def updateEpgTv():
    urllib.socket.setdefaulttimeout(TIMEOUT)
    pathFileEpg = os.path.join(SERVICE_PATH, 'epgTV.py')
    try:
        upFile = urllib.urlopen(LINK + 'epgTV.py')
        fileUp = open(pathFileEpg, 'wb')
        fileUp.write(upFile.read())
        fileUp.close()
        return True
    except:
        return False

def updateAddonTv():
    urllib.socket.setdefaulttimeout(TIMEOUT)
    pathFileXml = os.path.join(SERVICE_PATH, 'addon.xml')
    try:
        upFile = urllib.urlopen(LINK + 'addon.xml')
        fileUp = open(pathFileXml, 'wb')
        fileUp.write(upFile.read())
        fileUp.close()
        return True
    except:
        return False

def updateSettings():
    urllib.socket.setdefaulttimeout(TIMEOUT)
    pathFileXml = os.path.join(SERVICE_PATH, 'resources', 'settings.xml')
    try:
        upFile = urllib.urlopen(LINK + 'settings.xml')
        fileUp = open(pathFileXml, 'wb')
        fileUp.write(upFile.read())
        fileUp.close()
        return True
    except:
        return False

def stopPlayer():
    if xbmc.Player().isPlaying():
        xbmc.Player().stop()
