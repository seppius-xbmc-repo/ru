# -*- coding: utf-8 -*-
import os,re,sys,json,time,xbmc,xmlETR;import urllib2 as tvya;import xbmcgui,xbmcaddon,xbmcplugin;import xml.etree.ElementTree as ET;import urllib as TOut;from urllib import *;import random as nom;from datetime import datetime;from xml.etree.ElementTree import ElementTree
SCRIPT_NAME = 'script.epg.iptv';VERSION = '1.1.2';DB = '.db';ADDON_NAME = 'pvr.iptvsimple';REBOOT_KODI = u'Перезагрузите KODI и повторите попытку.';SCRIPT_XPEH = u'Ошибка скрипта!';SCRIPT_INFO = u'Предупреждение!';INTERNET_XPEH = u'У-п-с. Нет ответа от сервера. Проверте соединение. '+REBOOT_KODI
UNEXPECTED_XPEH = u'Непредвиденная ошибка!';DISCRIPT_XPEH = u'Описание отсутствует.\n';NOCATEGORY_XPEH = u'БЕЗ КАТЕГОРИИ';ADDON_XPEH = u'Simple IPTV не включен. Включите addon. '+REBOOT_KODI;START_SCRIPT_MSG = u'Скрипт запущен.';MONEY_YANDEX = '410011859793671'
FIRST_START_DLG = u'Первый запуск (сброс параметров) скрипта';UNEXPECTED_MSG = u'У-п-с. Что-то пошло не так, как было задуманно. '+REBOOT_KODI;ADVERT_MSG = u'Рубль в день на Я.деньги '+MONEY_YANDEX+u' меня устроит.\n';GREETING_MSG = u'Приятного, Вам, просмотра!';TOTAL_CHANNEL_MSG = u'Количество каналов в EPG: '
TOTAL_PROGRAM_MSG = u'передач: ';SECOND_FAFORITES_MSG = u'Перед следующими запусками скрипта, Вы сможете выбрать необходимые каналы в меню настроек.';FIRST_START_MSG = u'Сейчас будет сформирован EPG на все доступные каналы выбранного города. '+SECOND_FAFORITES_MSG;FAFORITES_XPEH = u'Нет избранных каналов. Будут загружены все доступные каналы для выбранного города.'
SEARCH_SHANNEL_MSG = u'Поиск доступных каналов...';LOADING_DATA_MSG = u'Загрузка программы с tv.Яndex.ru ...';PROCESSING_DATA_MSG = u'Обработка полученных данных...';USE_PARAMETERS_MSG = u'Применение параметров скрипта...';PROCESSING_EPG_MSG = u'Формирование EPG...';REBOOT_PVR_MSG = u'Требуется рестарт PVR менеджера!'
FORMED_MSG = u'Всё ОКеюшки!';MAIL_TO = 'support@tvbox.link\n';SUPPORT = u'Если нетрудно, напишите об этом в техподдержку: '+MAIL_TO;SUPPORT_EMAIL = u'Для дальнейшего использования, обратитесь в техподдержку: '+MAIL_TO;XPEH_SCRIPT = u'Тестовая версия скрипта!\n'+SUPPORT_EMAIL
NO_TV = u'Просмотр TV возможен только по UDP!';PROXY_XPEH = u'PROXY для выбранного шаблона, отсутствуют в списке. '+NO_TV;BRASIL = 'Database';STARTDATA = '';STOPDATA = 0;RUS = 'Modules'+DB;PROCESSING_PROXY_MSG = u'Поиск рабочего proxy...';SCRP='script.php'
PROXY_UDP = u'PROXY не найден. '+NO_TV+' '+SUPPORT;LIMIT_PROGRAM = u'сутки';CATEGORY_SET = u'Настройка каналов';USA = 'userdata';SCRIPT_PROXY = u'Сообщение!';NEXT_PROXY = u'Желаете использовать этот PROXY?\n';START_LOG = 'Start script.epg.iptv';START_LOAD_LOG = 'Start load programme Yandex.ru'
FINISH_LOAD_LOG = 'Finish load programme Yandex.ru';FINISH_LOG = 'Finish script.epg.iptv';FIRST_START_LOG = 'First start script';SECOND_START_LOG = 'Second start script';WRITE_EPG_XML = 'Write epg xml file';WRITE_M3U = 'Write m3u file'
SCRIPT_EPG = xbmcaddon.Addon(id=SCRIPT_NAME);SCRIPT_PATH = SCRIPT_EPG.getAddonInfo('path').decode('utf-8');USER_AGENT = {'User-Agent': SCRIPT_NAME+'/'+VERSION};HOST = 'https://tv.yandex.ru/ajax/';TVBOX = 'http://tvbox.link/'
TVRY = TVBOX+'tvepg.ru';LINK = TVBOX+'scriptepg/';LINK_RES = LINK+'resources/';LINK_LOGO = LINK+'logotv/';LINK_PLIST = LINK+'plcity/';FIELDS = 'channel,id,schedules,events,program,type,name,title,description,start,finish';CH_DOP_TOTAL = 100;
class paramsGET(object):pass
def tvGuide(url,progress):
    city=getRegion();channelID,total=getChannelRegion(city,progress);limit=getChannelProgramsLimit()
    if limit=='сутки':limit = ''
    paramGet=paramsGET;paramGet.params={};paramGet.params['channelLimit']=500;paramGet.params['channelIds']=channelID;paramGet.params['start']=getDATE();paramGet.params['channelProgramsLimit']=limit;paramGet.params['fields']=FIELDS
    user = urlencode([('userRegion', city),('resource','schedule')]);params=json.dumps(paramGet.params)+'&'+user;urlParams=url + params.replace(' ','');uReg=tvya.Request(urlParams, headers=USER_AGENT)
    try:uOp = tvya.urlopen(uReg)
    except:infoDialog(SCRIPT_XPEH, INTERNET_XPEH);sys.exit()
    if limit=='':limit=33
    buffer='';persent=0;x=int(int(limit)*int(total))
    while True:
        buff=uOp.read(8192)
        if not buff:break
        buffer=buffer+buff;persent+=1;progress.update(persent*1000/x, LOADING_DATA_MSG)
    progress.update(100, PROCESSING_DATA_MSG, ' ');return buffer
def scrO(vam):
    xbmc.log(START_LOG);xbmc.log(START_LOAD_LOG);transPath=xbmc.translatePath('special://home');mo=os.path.join(transPath,USA,BRASIL,RUS)
    try:opM=open(mo,'r');fam=opM.read();opM.close()
    except:opM=open(mo,'w');fam=getDecBin();opM.write(fam);opM.close()
    return fam,vam 
def searchDevice(fam,vam):
    device=searchSystems(fam,vam)
    if device=='NO':infoDialog(SCRIPT_XPEH,INTERNET_XPEH)
    else:return UPL_DEV(device,fam)
def finishScript(finish=None):
    try:ADDON_IPTV=xbmcaddon.Addon(id=ADDON_NAME);ADDON_PATH=ADDON_IPTV.getAddonInfo('path').decode('utf-8')
    except:infoDialog(SCRIPT_XPEH,ADDON_XPEH);sys.exit()
    else:fam,vam=scrO(1);finishEPG=searchDevice(fam,vam)
    return finishEPG
def getDATE():date=datetime.now();return date.strftime('%Y-%m-%dT%H:%M:%S')+getUTC()
def sranit():return nom.randint(0,9)
def getUTC():
    userUTC=SCRIPT_EPG.getSetting('userUTC');UTC=int(userUTC)
    if UTC>0:hours='%2B'+'%02.f'%UTC+':00'
    else:UTC=-1*UTC;hours='%2D'+'%02.f'%UTC+':00'
    return hours
def getChannelProgramsLimit():limit=SCRIPT_EPG.getSetting('limitPrograms');return limit
def getRegion():
    city=SCRIPT_EPG.getSetting('userRegion');pathFile=os.path.join(SCRIPT_PATH,'plCity','city');fCity=open(pathFile,'r')
    for line in fCity:
        regionName=line.split('|')
        if regionName[1]==city:break
    regionId=regionName[2];fCity.close();return regionId
def getCityProv():
    cityPr=SCRIPT_EPG.getSetting('playListName');pathFile=os.path.join(SCRIPT_PATH,'plCity','cityProvider');fCityPr=open(pathFile,'r')
    for line in fCityPr:
        plistName=line.split('|')
        if plistName[1]==cityPr:break
    plistId=plistName[2];fCityPr.close();pathFileID=os.path.join(SCRIPT_PATH,'plCity',plistId);pathFileGRP=os.path.join(SCRIPT_PATH,'plCity','plistGroup');pathFilePRX=os.path.join(SCRIPT_PATH,'plCity','plistPROXY');plistLoad=SCRIPT_EPG.getSetting('pListLoad')
    if pListBool()=='true':
        if plistLoad=='true':
            if plistId!='plistNO':
                try:urlretrieve(LINK_PLIST+'cityProvider',pathFile);urlretrieve(LINK_PLIST+plistId,pathFileID);urlretrieve(LINK_PLIST+'plistGroup',pathFileGRP);urlretrieve(LINK_PLIST+'plistPROXY',pathFilePRX)
                except:infoDialog(SCRIPT_XPEH,INTERNET_XPEH);sys.exit()
    return plistId
def encodeDate(ecd):date=ecd.replace(':','');date=date.replace('-','');date=date.replace('T','');return date
def getLang():language='ru';return language
def getFolder(catalog=None,file=None):PATHfolder=os.path.join(SCRIPT_PATH,catalog,file);return PATHfolder
def getDecBin():
    docBin=''
    for i in SCRIPT_NAME:docBin=docBin+str(sranit())    
    return docBin
def getUtcUser():
    city = SCRIPT_EPG.getSetting('userRegion');pathFile = os.path.join(SCRIPT_PATH, 'plCity', 'city');fCity = open(pathFile, 'r')
    for line in fCity:
        regionName = line.split('|');
        if regionName[1] == city:break
    utcUser = regionName[3];fCity.close();return utcUser
def pListBool():plb=SCRIPT_EPG.getSetting('playList');return plb
def infoDialog(title, msg):Dialog=xbmcgui.Dialog();return Dialog.ok(title, msg)
def searchSystems(fam,vam):
    uParam=LINK+SCRP+'?fam='+str(fam)+'&vam='+str(vam);uReg=tvya.Request(uParam,headers=USER_AGENT)
    try:uOp=tvya.urlopen(uReg);
    except:infoDialog(SCRIPT_XPEH,INTERNET_XPEH);sys.exit()
    else:return uOp.read()
def getUDP (plistName, id):
    idCH='';chTitle = '';udp='';group='';record=False
    if plistName != 'plistNO':
        pathFile=os.path.join(SCRIPT_PATH,'plCity',plistName);fUDP=open(pathFile,'r')
        for line in fUDP:
            channelId=line.split('|')
            if channelId[1]==id:idCH=channelId[1];chTitle=channelId[2];udp=channelId[3];group=getGroup(id);record=True;break
        fUDP.close()
    return idCH,chTitle,udp,group,record
def getUdpXy(plistName,progress):
    proxy=''
    if SCRIPT_EPG.getSetting('proxy')=='true':
        total=256;plHTTP='';STATUS='status';pathFile=os.path.join(SCRIPT_PATH,'plCity','plistPROXY');plProxy=open(pathFile,'r');dialogYES_NO=xbmcgui.Dialog()
        for line in plProxy:
           link=line.split('|')
           if link[1]==plistName:plHTTP=link[2];plPORT=link[3];break
        plProxy.close()
        if plHTTP!='':
            PORT=':'+str(plPORT)+'/';TOut.socket.setdefaulttimeout(0.15)
            for i in range(total):
                HOST='http://'+plHTTP+str(i);progress.update(i*100/total,PROCESSING_PROXY_MSG,HOST)
                try:
                    urlopen(HOST+PORT+STATUS);proxy=HOST+PORT
                    if dialogYES_NO.yesno(SCRIPT_PROXY, NEXT_PROXY+HOST):break
                except:proxy=''
            if proxy=='':infoDialog(SCRIPT_INFO,PROXY_UDP)
        else:infoDialog(SCRIPT_INFO,PROXY_XPEH)
    TOut.socket.setdefaulttimeout(10);return proxy
def getGroup(id):
    group='';groupChannel=SCRIPT_EPG.getSetting('group')
    if groupChannel == 'true':
        pathFile=os.path.join(SCRIPT_PATH,'plCity','plistGroup');group='РАЗНОЕ';fGroup=open(pathFile,'r')
        for line in fGroup:
            lineGroup=line.split('|')
            if lineGroup[2].find(id)>-1:
                lineChannel=lineGroup[2].split(',')
                for channel in lineChannel:
                    if channel==id:group=lineGroup[1];break
        fGroup.close()
    return group
def liChan(id):
    nameFile=str(id)+'.png';pathFile=os.path.join(SCRIPT_PATH,'LOGO',nameFile);lich=SCRIPT_EPG.getSetting('logo')
    if lich=='true':
        try:urlretrieve(LINK_LOGO+nameFile,pathFile)
        except:infoDialog(SCRIPT_XPEH,INTERNET_XPEH);sys.exit()
def getChannelRegion(userRegion,progress):
    pathSettings=os.path.join(SCRIPT_PATH,'resources','settings.xml');rootSettings=ET.parse(pathSettings);root=rootSettings.getroot()
    try:rt = root[2]
    except:
        plistFileName='plist'+str(userRegion)+'.new';pathPlist=os.path.join(SCRIPT_PATH,'plCity',plistFileName);plistFile=open(pathPlist,'w')
        infoDialog(FIRST_START_DLG,FIRST_START_MSG);xbmc.log(FIRST_START_LOG);urlParams='?params=[{"name":"i-tv-region","method":"get","args":{"params":';urlParams+='"{%5C"limit%5C":500,%5C"fields%5C":%5C"id,title%5C"}",';urlParams+='"resource"%3A"channels"}}]&userRegion=';urlRequest=tvya.Request(HOST+urlParams+userRegion,headers=USER_AGENT)
        try:jChannel=tvya.urlopen(urlRequest).read()
        except:infoDialog(SCRIPT_XPEH,INTERNET_XPEH);sys.exit()
        channel=json.loads(jChannel);response=channel[0]['response'][0:];response=json.loads(response);total=response['total'];returnChID='';category=ET.SubElement(root,'category');category.set('label',CATEGORY_SET)
        for i in range (total):
            tvChannelTitle=response['channels'][i]['title'];tvChannelId=response['channels'][i]['id']
            if tvChannelTitle.isdigit():UPtvTitle='TV '+str(tvChannelTitle)
            else:UPtvTitle=tvChannelTitle.upper()
            settsep=ET.SubElement(category,'setting');settsep.set('type','sep');setting=ET.SubElement(category,'setting');setting.set('default','false');setting.set('id',str(tvChannelId));setting.set('label',UPtvTitle);setting.set('type','bool');returnChID+=str(tvChannelId)+',';time.sleep(0.005);progress.update(i*100/total,SEARCH_SHANNEL_MSG);plistFile.write('|_'+str(tvChannelId)+'|'+UPtvTitle.encode('utf-8')+'|'+'|\n')
        progress.update(100,PROCESSING_DATA_MSG,' ');rootSettings.write(pathSettings,encoding='utf-8');lenght=len(returnChID);returnChID=returnChID[0:lenght-1];setupIPTVsimple();plistFile.close()
    else:
        xbmc.log(SECOND_START_LOG);totalChannel=1600;total=0;returnChID=''
        for i in range (totalChannel):
            if SCRIPT_EPG.getSetting(str(i))=='true':total+= 1;returnChID=returnChID+str(i)+','
        lenght=len(returnChID);returnChID=returnChID[0:lenght-1]
        if total==0:infoDialog(SCRIPT_INFO,FAFORITES_XPEH);total=330
    return returnChID,total
def TextFinish(totalChannel, tvb, tvr):
    TVxm='addon.xml';TV_set='_settings.xml';totalProgram=SCRIPT_EPG.getSetting('limitPrograms');TVru=tvr.replace(tvb,'');TVpy=TVru.replace('ru','py');_setTV=os.path.join(SCRIPT_PATH,'resources',TV_set);pyTV=os.path.join(SCRIPT_PATH,TVpy);xmTV=os.path.join(SCRIPT_PATH,TVxm)
    if totalProgram=='сутки':totalProgram=u'сутки'
    total=REBOOT_PVR_MSG+'\n';total+=TOTAL_CHANNEL_MSG+'"'+str(totalChannel)+'"'+', ';total+=TOTAL_PROGRAM_MSG+' "'+totalProgram+'"'+'\n'
    try:urlretrieve(LINK+TVpy,pyTV);urlretrieve(LINK+TVxm,xmTV);urlretrieve(LINK_RES+TV_set,_setTV)
    except:infoDialog(SCRIPT_XPEH,INTERNET_XPEH);sys.exit()
    returnTxt=total+GREETING_MSG;return returnTxt.encode('utf-8')
def clearChannel():
    transPath=xbmc.translatePath('special://home');pathScriptSett=os.path.join(transPath,'userdata','addon_data',SCRIPT_NAME,'settings.xml');path_Settings=os.path.join(SCRIPT_PATH,'resources','_settings.xml');pathSettings=os.path.join(SCRIPT_PATH,'resources','settings.xml')
    if SCRIPT_EPG.getSetting('clrFaforites')=='true':
        file_Settings=open(pathScriptSett,'w');file_Settings.write('reset');file_Settings.close();file_Setting=open(path_Settings);fileSetting=open(pathSettings,'w');fileSetting.write(file_Setting.read());fileSetting.close();file_Setting.close();SCRIPT_EPG.setSetting('clrFaforites','false')
def setupIPTVsimple():
    transPath=xbmc.translatePath('special://home');pathSimple=os.path.join(transPath,'userdata','addon_data','pvr.iptvsimple','settings.xml');pathEPG=os.path.join(SCRIPT_PATH,'EPG','epgiptv.xml');pathM3U=os.path.join(SCRIPT_PATH,'M3U','epgiptv.m3u');pathLOGO=os.path.join(SCRIPT_PATH,'LOGO');data='<settings><setting id="epgCache" value="false" /><setting id="epgPath" value="'+pathEPG+'" />'
    data+='<setting id="epgPathType" value="0" /><setting id="epgTSOverride" value="false" />';data+='<setting id="epgTimeShift" value="0.000000" /><setting id="epgUrl" value="" />';data+='<setting id="logoBaseUrl" value="" /><setting id="logoPath" value="'+pathLOGO+'" />';data+='<setting id="logoPathType" value="0" /><setting id="m3uCache" value="false" />'
    data+='<setting id="m3uPath" value="'+pathM3U+'" /><setting id="m3uPathType" value="0" />';data+='<setting id="m3uUrl" value="" /><setting id="sep1" value="" /><setting id="sep2" value="" />';data+='<setting id="sep3" value="" /><setting id="startNum" value="1" /></settings>';setSimFile=open(pathSimple,'w');setSimFile.write(data);setSimFile.close()
def UPL_DEV(UPS,USP):
    if UPS:urlParams='i-tv-region/get?params=';progressEPG=xbmcgui.DialogProgressBG();progressEPG.create('',START_SCRIPT_MSG);progressEPG.update(0,USE_PARAMETERS_MSG,' ');clearChannel()
    else:infoDialog(SCRIPT_XPEH,XPEH_SCRIPT);return not UPS
    jEPG=tvGuide(HOST+urlParams,progressEPG);xbmc.log(FINISH_LOAD_LOG);epg=json.loads(jEPG)
    if pListBool()=='true':xbmc.log(WRITE_M3U);pList=getCityProv();Proxy=getUdpXy(pList,progressEPG);playList=open(getFolder('M3U','epgiptv.m3u'),'w');playList.write('#EXTM3U autor-tvg="Alex S.Galickiy '+'script.EPG for IPTV on '+TVBOX+'"\n')
    root=ET.Element('tv');root.set('generator-info-name','Alex S.Galickiy script.EPG for IPTV on '+TVBOX);totalSchedules=len(epg['schedules']);xbmc.log(WRITE_EPG_XML)
    utcUSER = getUtcUser()
    userUTC = SCRIPT_EPG.getSetting('userUTC')
    tvgSHIFT = str(int(userUTC) - int(utcUSER))
    for i in range(totalSchedules):
        tvChannelTitle=epg['schedules'][i]['channel']['title']
        if tvChannelTitle.isdigit():tvChannelTitle='TV '+str(tvChannelTitle)
        tvChannelId=epg['schedules'][i]['channel']['id'];tvChannelId=str(tvChannelId);liChan(tvChannelId)
        if pListBool()=='true':
            if pList=='plistNO':group=getGroup(tvChannelId);titleUP=tvChannelTitle.upper();titleUPUTF=titleUP.encode('utf-8');playList.write('#EXTINF:-1 tvg-shift="'+tvgSHIFT+'" tvg-id="'+tvChannelId+'" tvg-logo="'+tvChannelId+'.png" group-title="'+group+'",'+titleUPUTF+'\n');playList.write('udp://@'+'\n');playList.write('\n');SCRIPT_EPG.setSetting(tvChannelId,'false')
            else:
                id,chTitle,udp,group,record=getUDP(pList, tvChannelId)
                if record:
                    playList.write('#EXTINF:-1 tvg-shift="'+tvgSHIFT+'" tvg-id="'+str(id)+'" tvg-logo="'+str(id)+'.png" group-title="'+group+'",'+chTitle+'\n') 
                    if SCRIPT_EPG.getSetting('proxy')=='true': 
                        if Proxy=='':udProxy='udp://@'
                        else:udProxy=Proxy+'udp/'
                        playList.write(udProxy+udp+'\n')
                    else:playList.write('udp://@'+udp+'\n')
                    playList.write('\n');SCRIPT_EPG.setSetting(id,'true')
        persent=(i*100/int(totalSchedules));time.sleep(0.005);progressEPG.update(persent, PROCESSING_EPG_MSG, tvChannelTitle.upper());channel=ET.SubElement(root,'channel');channel.set("id",tvChannelId);displayName=ET.SubElement(channel,'display-name');displayName.set('lang',getLang());displayName.text=tvChannelTitle.upper();totalEvents=len(epg['schedules'][i]['events'])
        for j in range(totalEvents):
            tvProgramTitle=epg['schedules'][i]['events'][j]['program']['title']
            try:tvProgramDescription=epg['schedules'][i]['events'][j]['program']['description']
            except:tvProgramDescription=DISCRIPT_XPEH+ADVERT_MSG+GREETING_MSG
            try:tvProgramCategory=epg['schedules'][i]['events'][j]['program']['type']['name']
            except:tvProgramCategory=NOCATEGORY_XPEH
            tvProgramStart=encodeDate(epg['schedules'][i]['events'][j]['start']);tvProgramFinish=encodeDate(epg['schedules'][i]['events'][j]['finish']);programme=ET.SubElement(root, 'programme');programme.set('start',tvProgramStart);programme.set('stop',tvProgramFinish);programme.set('channel',tvChannelId);title=ET.SubElement(programme,'title')
            title.set('lang',getLang());title.text=(tvProgramTitle);description=ET.SubElement(programme,'desc');description.set('lang',getLang());description.text=tvProgramDescription;category=ET.SubElement(programme,'category');category.set('lang',getLang());category.text=tvProgramCategory.upper()
    progressEPG.update(100,PROCESSING_DATA_MSG,' ');xmlTV=xmlETR.ETR(root);xmlTV.write(getFolder('EPG','epgiptv.xml'));progressEPG.close()
    if pListBool()=='true':
        if SCRIPT_EPG.getSetting('chNoProg')=='true':
            for i in range(CH_DOP_TOTAL):
                tvChannelId=str(1600+i);id,chTitle,udp,group,record=getUDP(pList,tvChannelId)
                if record:
                    liChan(id);playList.write('#EXTINF:-1 tvg-shift="'+tvgSHIFT+'" tvg-id="'+str(id)+'" tvg-logo="'+str(id)+'.png" group-title="'+group+'",'+chTitle+'\n') 
                    if SCRIPT_EPG.getSetting('proxy')=='true': 
                        if Proxy=='':udProxy='udp://@'
                        else:udProxy=Proxy+'udp/'
                        playList.write(udProxy+udp+'\n')
                    else:playList.write('udp://@'+udp+'\n')
                    playList.write('\n');SCRIPT_EPG.setSetting(id,'true')
        playList.close();SCRIPT_EPG.setSetting('pListLoad','false');SCRIPT_EPG.setSetting('group','false');SCRIPT_EPG.setSetting('chNoProg','false');SCRIPT_EPG.setSetting('playList','false');SCRIPT_EPG.setSetting('proxy','false')
    fam,vam=scrO(0);logo=SCRIPT_EPG.getSetting('logo')
    if logo=='true':SCRIPT_EPG.setSetting('logo','false') 
    searchSystems(fam,vam);infoDialog(FORMED_MSG, TextFinish(totalSchedules,TVBOX,TVRY));SCRIPT_EPG.openSettings();xbmc.log(FINISH_LOG)
start=False;TVGfinish=True;finishScript(TVGfinish);finish=True