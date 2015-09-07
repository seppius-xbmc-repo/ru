############################################################
# Copyright (C) Alex S.Galickiy 2015 - All Rights Reserved #
############################################################

# -*- coding: utf-8 -*-

import xbmc
import xbmcgui
import xbmcaddon
import os
import sys
import json
import time
import xmlETR
import urllib
import urllib2 as tvya
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

CATEGORY_XPEH = u'БЕЗ КАТЕГОРИИ'
DISCRIPT_XPEH = u'ОПИСАНИЕ ОТСУТСТВУЕТ'
START_CREATE_EPG = u'Обновление EPG...'

VERSION = '2.0.0'
SERVICE_NAME = 'service.proxy.tv'
SERVICE_START = xbmcaddon.Addon(id=SERVICE_NAME);
SERVICE_PATH = xbmc.translatePath(SERVICE_START.getAddonInfo('path')).decode('utf-8')

LINK_TVBOX = 'http://tvbox.link/'
TV_Ya = 'https://tv.yandex.ru/ajax/i-tv-region/get?params='
USER_AGENT = {'User-Agent': SERVICE_NAME+'/'+VERSION}
FIELDS = 'channel, id, schedules, events, program, type, name, title, description, start, finish'

pathFilePlist = os.path.join(SERVICE_PATH, 'plist', 'plistALLall')

class paramsGET(object):
    pass

def getDATE(serviceUTC):
    userUTC = int(SERVICE_START.getSetting('timeZone'))
    date = datetime.now() + timedelta(hours = serviceUTC - userUTC)
    return date.strftime('%Y-%m-%dT%H:%M:%S') + getUTC(serviceUTC)

def getUTC(serviceUTC):
    UTC = int(serviceUTC)
    if UTC > 0:
        hours='%2B'+'%02.f'%UTC+':00'
    else:
        UTC = -1 * UTC
        hours = '%2D'+'%02.f'%UTC+':00'
    return hours

def encodeDate(ecd):
    date = ecd.replace(':','')
    date = date.replace('-','')
    date = date.replace('T','')
    return date

def countPlist():
    count = 0
    fCount = open(pathFilePlist,'r')
    for line in fCount:
        chCount = line.split('|')
        if chCount[1].find('_') == -1:
            count += 1
    return count

def createEpg():
    lineCount = 0
    channelCount = countPlist()
    progressEPG = xbmcgui.DialogProgressBG()
    progressEPG.create(START_CREATE_EPG, '')
    root = ET.Element('tv')
    root.set('generator-info-name','Alex S.Galickiy service.proxy.tv for KODI on ' + LINK_TVBOX)
    fUDP = open(pathFilePlist,'r')
    for line in fUDP:
        channelId = line.split('|')
        if channelId[1].find('_') == -1:
            lineCount += 1
            idCH = channelId[1]
            titleCh = channelId[2]
            region = channelId[4]
            serviceUTC = int(channelId[6])
            programme = int(channelId[7])
            if programme == 1:
                i = 0
                jEpg = tvGuide(idCH, region, serviceUTC)
                epg = json.loads(jEpg)
                print titleCh
                print getDATE(serviceUTC)
                tvChannelTitle = epg['schedules'][i]['channel']['title']
                if tvChannelTitle.isdigit():
                    tvChannelTitle = 'TV ' + str(tvChannelTitle)
                tvChannelId = epg['schedules'][i]['channel']['id']
                tvChannelId = str(tvChannelId)
                channel = ET.SubElement(root, 'channel')
                channel.set("id",tvChannelId)
                displayName = ET.SubElement(channel, 'display-name')
                displayName.set('lang', 'ru')
                displayName.text = tvChannelTitle.upper()
                totalEvents = len(epg['schedules'][i]['events'])
                for j in range(totalEvents):
                    tvProgramTitle = epg['schedules'][i]['events'][j]['program']['title']
                    try:
                        tvProgramDescription = epg['schedules'][i]['events'][j]['program']['description']
                    except:
                        tvProgramDescription = DISCRIPT_XPEH
                    try:
                        tvProgramCategory = epg['schedules'][i]['events'][j]['program']['type']['name']
                    except:
                        tvProgramCategory = CATEGORY_XPEH
                    tvProgramStart = encodeDate(epg['schedules'][i]['events'][j]['start'])
                    tvProgramFinish = encodeDate(epg['schedules'][i]['events'][j]['finish'])
                    programme = ET.SubElement(root, 'programme')
                    programme.set('start', tvProgramStart)
                    programme.set('stop', tvProgramFinish)
                    programme.set('channel', tvChannelId)
                    title = ET.SubElement(programme, 'title')
                    title.set('lang', 'ru')
                    title.text = tvProgramTitle
                    description = ET.SubElement(programme, 'desc')
                    description.set('lang', 'ru')
                    description.text = tvProgramDescription
                    category = ET.SubElement(programme, 'category')
                    category.set('lang', 'ru')
                    category.text = tvProgramCategory.upper()
                persent = lineCount * 100 / channelCount
                progressEPG.update(persent, START_CREATE_EPG, tvChannelTitle.upper())
                xmlTV = xmlETR.ETR(root)
    xmlTV.write(os.path.join(SERVICE_PATH, 'EPG', 'epgiptv.xml'))
    progressEPG.close()

def tvGuide(idCH, region, serviceUTC):
    work = True
    paramGet = paramsGET
    paramGet.params = {}
    paramGet.params['channelLimit'] = 1
    paramGet.params['channelIds'] = idCH
    paramGet.params['start'] = getDATE(serviceUTC)
    paramGet.params['channelProgramsLimit'] = ''
    paramGet.params['fields'] = FIELDS
    user = urllib.urlencode([('userRegion', region), ('resource', 'schedule')])
    params = json.dumps(paramGet.params) + '&' + user
    urlParams = TV_Ya + params.replace(' ', '')
    uReg = tvya.Request(urlParams, headers = USER_AGENT)
    while work:
        try:
            chEpg = tvya.urlopen(uReg).read()
            work = False
        except:
            work = True
    return chEpg