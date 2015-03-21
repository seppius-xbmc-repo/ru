# Copyright (c) 2013 Torrent-TV.RU
# Writer (c) 2013, Welicobratov K.A., E-mail: 07pov23@gmail.com

#imports
import xbmcgui
import xbmc
import xbmcaddon

import json
import urllib2
import time
import datetime

from ts import TSengine as tsengine
from player import MyPlayer
from adswnd import AdsForm
from menu import MenuForm
from infoform import InfoForm
from dateform import DateForm

import uuid
import os
import socket

import defines

def LogToXBMC(text, type = 1):
    ttext = ''
    if type == 2:
        ttext = 'ERROR:'

    log = open(defines.ADDON_PATH + '/mainform.log', 'a')
    print '[MainForm %s] %s %s\r' % (time.strftime('%X'),ttext, text)
    log.write('[MainForm %s] %s %s\r' % (time.strftime('%X'),ttext, text))
    log.close()
    del log

class WMainForm(xbmcgui.WindowXML):
    CANCEL_DIALOG  = ( 9, 10, 11, 92, 216, 247, 257, 275, 61467, 61448, )
    CONTEXT_MENU_IDS = (117, 101)
    ARROW_ACTIONS = (1,2,3,4)
    ACTION_MOUSE = 107
    BTN_CHANNELS_ID = 102
    BTN_TRANSLATIONS_ID = 103
    BTN_ARCHIVE_ID = 104
    BTN_VOD_ID = 113
    BTN_CLOSE = 101
    BTN_FULLSCREEN = 208
    IMG_SCREEN = 210
    CONTROL_LIST = 50
    PANEL_ADS = 105
    PROGRESS_BAR = 110
    BTN_INFO = 209
    LBL_FIRST_EPG = 300
    
    CHN_TYPE_FAVOURITE = 'Избранное'
    CHN_TYPE_TRANSLATION = 'Трансляции'
    CHN_TYPE_MODERATION = 'На модерации'
    API_ERROR_INCORRECT = 'incorrect'
    API_ERROR_NOCONNECT = 'noconnect'
    API_ERROR_ALREADY = 'already'
    API_ERROR_NOPARAM = 'noparam'
    API_ERROR_NOFAVOURITE = 'nofavourite'


    def __init__(self, *args, **kwargs):
        self.isCanceled = False
        self.translation = []
        self.category = {}
        self.seltab = 0
        self.epg = {}
        self.archive = []
        self.selitem = '0'
        self.img_progress = None
        self.txt_progress = None
        self.list = None
        self.player = MyPlayer("player.xml", defines.SKIN_PATH, defines.ADDON.getSetting('skin'))
        self.player.parent = self
        self.amalkerWnd = AdsForm("adsdialog.xml", defines.SKIN_PATH, defines.ADDON.getSetting('skin'))
        self.cur_category = WMainForm.CHN_TYPE_FAVOURITE
        self.epg = {}
        self.selitem_id = -1
        self.playditem = -1
        self.user = None
        self.infoform = None

    def initLists(self):
        self.category = {}
        self.category[WMainForm.CHN_TYPE_MODERATION] = { "name" : WMainForm.CHN_TYPE_MODERATION, "channels": []}
        self.category[WMainForm.CHN_TYPE_FAVOURITE] = { "name" : WMainForm.CHN_TYPE_FAVOURITE, "channels": []}
        self.translation = []

    def getChannels(self, param):
        data = defines.GET('http://api.torrent-tv.ru/v3/translation_list.php?session=%s&type=%s&typeresult=json' % (self.session, param), cookie = self.session)
        jdata = json.loads(data)
        if jdata['success'] == 0:
            self.showStatus(jdata['error'])
            return

        for cat in jdata["categories"]:
            if not self.category.has_key('%s' % cat["id"]):
                self.category['%s' % cat["id"]] = { "name": cat["name"], "channels": [] }

        for ch in jdata['channels']:
            if not ch["name"]:
                continue
            if not ch['logo']:
                ch['logo'] = ''
            else:
                ch['logo'] = 'http://torrent-tv.ru/uploads/' + ch['logo']
            
            chname = ch["name"]
            if ch["access_user"] == 0:
                chname = "[COLOR FF646464]%s[/COLOR]" % chname
            
            li = xbmcgui.ListItem(chname, '%s' % ch['id'], ch['logo'], ch['logo'])
            li.setProperty('epg_cdn_id', '%s' % ch['epg_id'])
            li.setProperty('icon', ch['logo'])
            li.setProperty("type", "channel")
            li.setProperty("id", '%s' % ch["id"])
            li.setProperty("access_translation", ch["access_translation"])
            li.setProperty("access_user", '%s' % ch["access_user"])
            
            if param == 'channel':
                li.setProperty('commands', "%s,%s" % (MenuForm.CMD_ADD_FAVOURITE, MenuForm.CMD_CLOSE_TS))
                self.category['%s' % ch['group']]["channels"].append(li)
            elif param == 'moderation':
                li.setProperty('commands', "%s,%s" % (MenuForm.CMD_ADD_FAVOURITE, MenuForm.CMD_CLOSE_TS))
                self.category[WMainForm.CHN_TYPE_MODERATION]["channels"].append(li)
            elif param == 'translation':
                li.setProperty('commands', "%s,%s" % (MenuForm.CMD_ADD_FAVOURITE, MenuForm.CMD_CLOSE_TS))
                self.translation.append(li)
            elif param == 'favourite':
                li.setProperty('commands', "%s,%s,%s,%s" % (MenuForm.CMD_DEL_FAVOURITE, MenuForm.CMD_UP_FAVOURITE, MenuForm.CMD_DOWN_FAVOURITE, MenuForm.CMD_CLOSE_TS))
                self.category[WMainForm.CHN_TYPE_FAVOURITE]["channels"].append(li)

    def getArcChannels(self, param):
        data = defines.GET('http://api.torrent-tv.ru/v3/arc_list.php?session=%s&typeresult=json' % self.session, cookie = self.session)
        jdata = json.loads(data)
        self.archive = []
        if jdata['success'] == 0:
            self.showStatus(jdata['error'])
            return
        
        for ch in jdata['channels']:
            if not ch["id"]:
                continue
            if not ch["logo"]:
                ch["logo"] = ""
            else:
                ch["logo"] = "http://torrent-tv.ru/uploads/" + ch["logo"]
            li = xbmcgui.ListItem(ch["name"], '%s' % ch["id"], ch["logo"], ch["logo"])
            li.setProperty("epg_cdn_id", '%s' % ch["epg_id"])
            li.setProperty("icon", ch["logo"])
            li.setProperty("type", "archive")
            self.archive.append(li)

    def getEpg(self, param):
       data = defines.GET('http://api.torrent-tv.ru/v3/translation_epg.php?session=%s&epg_id=%s&typeresult=json' % (self.session, param), cookie = self.session)
       jdata = json.loads(data)
       if jdata['success'] == 0:
          self.epg[param] = []
          self.showSimpleEpg(param)
       else:
           self.epg[param] = jdata['data']
           selitem = self.list.getSelectedItem()
           
           if selitem.getProperty('epg_cdn_id') == param:
               self.showSimpleEpg(param)
           
       self.hideStatus()

    def showScreen(self, cdn):
        if defines.tryStringToInt(cdn) < 1:
            return

        data = defines.GET('http://api.torrent-tv.ru/v3/translation_screen.php?session=%s&channel_id=%s&typeresult=json&count=1' % (self.session, cdn), cookie = self.session)
        jdata = json.loads(data)
        img = self.getControl(WMainForm.IMG_SCREEN)
        img.setImage("")
        if jdata['success'] == 0:
            LogToXBMC('showScreen: скрин не найден')
            return
        else:
            LogToXBMC('showScreen: %s' % jdata['screens'][0]['filename'])
            img.setImage(jdata['screens'][0]['filename'])

    def onInit(self):
        try:
            data = defines.GET('http://api.torrent-tv.ru/v3/version.php?application=xbmc&version=%s' % defines.VERSION)
            jdata = json.loads(data)
            if jdata['support'] == 0:
               from okdialog import OkDialog
               dialog = OkDialog("okdialog.xml", defines.SKIN_PATH, defines.ADDON.getSetting('skin'))
               dialog.setText("Текущая версия приложения (%s) не поддерживается. Последняя версия %s " % (defines.VERSION, jdata['last_version'].encode('utf-8')))
               #dialog.setText('Hello World')
               dialog.doModal()
               self.close()
            self.img_progress = self.getControl(108)
            self.txt_progress = self.getControl(107)
            self.progress = self.getControl(WMainForm.PROGRESS_BAR)
            self.showStatus("Авторизация")
            guid = defines.ADDON.getSetting("uuid")
            if guid == '':
              guid = str(uuid.uuid1())
              defines.ADDON.setSetting("uuid", guid)
            guid = guid.replace('-', '')
            print guid
            data = defines.GET('http://api.torrent-tv.ru/v3/auth.php?username=%s&password=%s&typeresult=json&application=xbmc&guid=%s' % (defines.ADDON.getSetting('login'), defines.ADDON.getSetting('password'), guid))
            jdata = json.loads(data)
            if jdata['success'] == 0:
                self.showStatus(jdata['error'])
                return

            self.user = {"login" : defines.ADDON.getSetting('login'), "balance" : jdata["balance"]}
            
            self.session = jdata['session']
            self.updateList()
            

        except Exception, e:
            LogToXBMC('OnInit: %s' % e, 2)

    def onFocus(self, ControlID):
        if ControlID == 50:
            if not self.list:
                return
            selItem = self.list.getSelectedItem()
            if selItem:
                if selItem.getLabel2() == self.selitem or selItem.getLabel() == '..':
                    return
                self.selitem = selItem.getLabel2()
                self.selitem_id = self.list.getSelectedPosition()
                LogToXBMC('Selected %s' % self.selitem_id)
                epg_id = selItem.getProperty('epg_cdn_id')
                #LogToXBMC('Icon list item = %s' % selItem.getIconImage())
                img = self.getControl(WMainForm.IMG_SCREEN)
                img.setImage("")
                
                if epg_id == '0':
                    self.showSimpleEpg()
                elif self.epg.has_key(epg_id):
                    self.showSimpleEpg(epg_id)
                else:
                    self.showStatus('Загрузка программы')
                    thr = defines.MyThread(self.getEpg, epg_id)
                    thr.start()
                
                
                thr = defines.MyThread(self.showScreen, selItem.getLabel2())
                thr.start()
                img = self.getControl(1111)
                img.setImage(selItem.getProperty('icon'))
    
    def checkButton(self, controlId):
        control = self.getControl(controlId)
        control.setLabel('>%s<' % control.getLabel())
        if self.seltab:
            btn = self.getControl(self.seltab)
            btn.setLabel(btn.getLabel().replace('<', '').replace('>',''))
        self.seltab = controlId
        LogToXBMC('Focused %s %s' % (WMainForm.CONTROL_LIST, self.selitem_id))
        if self.selitem_id > -1:
            #self.setFocusId(WMainForm.CONTROL_LIST)
            self.list.selectItem(self.selitem_id)

    def onClickChannels(self):
        LogToXBMC('onClickChannels')
        self.fillChannels()
        if self.seltab != WMainForm.BTN_CHANNELS_ID:
            self.checkButton(WMainForm.BTN_CHANNELS_ID)

    def onClickTranslations(self):
        self.fillTranslation()
        if self.seltab != WMainForm.BTN_TRANSLATIONS_ID:
            self.checkButton(WMainForm.BTN_TRANSLATIONS_ID)

    def onClickArchive(self):
        self.fillArchive()
        
        if self.seltab != WMainForm.BTN_ARCHIVE_ID:
            self.checkButton(WMainForm.BTN_ARCHIVE_ID)

    def onClick(self, controlID):
        control = self.getControl(controlID)
        LogToXBMC('onClick %s' % controlID)
        if controlID == WMainForm.BTN_CHANNELS_ID: 
            self.onClickChannels()
            LogToXBMC("playditem = %s" % self.playditem)
            if self.playditem > -1:
                self.setFocus(self.list)
                self.list.selectItem(self.playditem)
                self.playditem = -1
                
        elif controlID == WMainForm.BTN_TRANSLATIONS_ID: 
            self.onClickTranslations()
            if self.playditem > -1:
                self.setFocus(self.list)
                self.list.selectItem(self.selitem_id)
                self.playditem = -1

        elif controlID == WMainForm.BTN_ARCHIVE_ID: 
            self.onClickArchive()
            
        elif controlID == 200: 
            self.setFocusId(50)
        elif controlID == 50:
            selItem = control.getSelectedItem()
            if not selItem:
                return
            if selItem.getLabel() == '..':
                if self.seltab == WMainForm.BTN_CHANNELS_ID:
                    self.fillCategory()
                elif self.seltab == WMainForm.BTN_ARCHIVE_ID:
                    self.fillArchive()
                return

            if selItem.getProperty('type') == 'category':
                self.cur_category = selItem.getProperty("id")
                self.fillChannels()
                return

            if selItem.getProperty("type") == "rec_date":
                
                if not selItem:
                    print "SELITEM EMPTY"
                datefrm = DateForm("dateform.xml", defines.SKIN_PATH, defines.ADDON.getSetting('skin'))
                if datefrm == None:
                    print "From not created"

                stime = time.strptime(selItem.getProperty("date"), "%Y-%m-%d")
                datefrm.date = datetime.date(stime.tm_year, stime.tm_mon, stime.tm_mday)
                #datefrm.date =datetime.fromtimestamp(time.mktime(time.strptime(selItem.getProperty("date"), "%Y-%m-%d")))
                #datefrm.date = datetime.strptime(selItem.getProperty("date"), "%Y-%m-%d")
                datefrm.doModal()
                find = False
                for li in self.archive:
                    if li.getProperty("epg_cdn_id") == selItem.getProperty("epg_cdn_id"):
                        self.fillRecords(li, datefrm.date)
                        find = True
                        return
                if not find:
                    self.fillRecords(self.archive[0], datefrm.date)
                    return
            
            if selItem.getProperty("access_user") == 0:
                access = selItem.getProperty("access_translation")
                if access == "registred":
                   defines.showMessage("Трансляция доступна для зарегестрированных пользователей")
                elif access == "vip":
                   defines.showMessage("Трансляция доступна для VIP пользователей")
                else:
                   defines.showMessage("На данный момент трансляция не доступна")
                return
             
            buf = xbmcgui.ListItem(selItem.getLabel())
            buf.setProperty('epg_cdn_id', selItem.getProperty('epg_cdn_id'))
            buf.setProperty('icon', selItem.getProperty('icon'))
            buf.setProperty("type", selItem.getProperty("type"))
            buf.setProperty("id", selItem.getProperty("id"))
            if selItem.getProperty("type") == "archive":
                self.fillRecords(buf, datetime.datetime.today());
                return
            print selItem.getProperty("type")
            self.playditem = self.selitem_id
            
            self.player.Start(buf)
            if xbmc.getCondVisibility("Window.IsVisible(home)"):
                LogToXBMC("Close from HOME Window")
                self.close()
            elif xbmc.getCondVisibility("Window.IsVisible(video)"):
                self.close();
                LogToXBMC("Is Video Window")
            elif xbmc.getCondVisibility("Window.IsVisible(programs)"):
                self.close();
                LogToXBMC("Is programs Window")
            elif xbmc.getCondVisibility("Window.IsVisible(addonbrowser)"):
                self.close();
                LogToXBMC("Is addonbrowser Window")
            elif xbmc.getCondVisibility("Window.IsMedia"):
                self.close();
                LogToXBMC("Is media Window")
            elif xbmc.getCondVisibility("Window.IsVisible(12346)"):
                self.close();
                LogToXBMC("Is plugin Window")
            else:
                jrpc = json.loads(xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"GUI.GetProperties","params":{"properties":["currentwindow"]},"id":1}'))
                if jrpc["result"]["currentwindow"]["id"] == 10025:
                    LogToXBMC("Is video plugins window");
                    self.close();
                
                LogToXBMC("Is Other Window")

           
            LogToXBMC('CUR SELTAB %s' % self.seltab)
            
           # xbmc.executebuiltin('SendClick(12345,%s)' % self.seltab)
        elif controlID == WMainForm.BTN_FULLSCREEN:
            if defines.ADDON.getSetting("winmode") == "true":
                self.player.show()
            else:
                xbmc.executebuiltin("Action(FullScreen)")

        elif controlID == WMainForm.BTN_INFO:
            self.showInfoWindow()
            return

    def showInfoWindow(self):
        self.infoform = InfoForm("inform.xml", defines.SKIN_PATH, defines.ADDON.getSetting('skin'))
        self.infoform.parent = self
        self.infoform.doModal()
        self.infoform = None

    def showSimpleEpg(self, epg_id = None):
        controlEpg = self.getControl(WMainForm.LBL_FIRST_EPG)
        if epg_id and self.epg[epg_id].__len__() > 0:
            ctime = time.time()
            try:
                curepg = filter(lambda x: (float(x['etime']) > ctime), self.epg[epg_id])
            except:
                return
            bt = float(float(curepg[0]['btime']))
            et = float(float(curepg[0]['etime']))
            sbt = time.localtime(bt)
            set = time.localtime(et)
            self.progress.setPercent((ctime - bt)*100/(et - bt))
            controlEpg.setLabel('%.2d:%.2d - %.2d:%.2d %s' % (sbt.tm_hour, sbt.tm_min, set.tm_hour, set.tm_min, curepg[0]['name']))
            nextepg = ''
            for i in range(1,99):
                ce = None
                try:
                    ce = self.getControl(WMainForm.LBL_FIRST_EPG + i)
                except:
                    break
                if ce == None:
                    brea;
                if i >= curepg.__len__():
                    break
                sbt = time.localtime(float(curepg[i]['btime']))
                set = time.localtime(float(curepg[i]['etime']))
                nextepg = '%.2d:%.2d - %.2d:%.2d %s' % (sbt.tm_hour, sbt.tm_min, set.tm_hour, set.tm_min, curepg[i]['name'])
                ce.setLabel(nextepg);
            #controlEpg1.setLabel(nextepg)

        else:
            controlEpg.setLabel('Нет программы')
            for i in range(1,99):
                ce = None
                try:
                    self.getControl(WMainForm.LBL_FIRST_EPG + i).setLabel('');
                except:
                    break
            self.progress.setPercent(1)

    def onAction(self, action):
        if not action:
            super(WMainForm, self).onAction(action)
            return
        if action.getButtonCode() == 61513:
            return;
        if action in WMainForm.CANCEL_DIALOG:
            LogToXBMC('CLOSE FORM')
            self.isCanceled = True
            #xbmc.executebuiltin('Action(PreviousMenu)')
            if self.player.TSPlayer:
               self.player.TSPlayer.closed = True
               self.player.Stop()
            self.close()
        elif action.getId() in WMainForm.ARROW_ACTIONS:
            LogToXBMC("ARROW_ACTION %s" % self.seltab )
            self.onFocus(self.getFocusId())
        elif action.getId() in WMainForm.CONTEXT_MENU_IDS and self.getFocusId() == WMainForm.CONTROL_LIST:
            if action.getId() == 101:
                return
            mnu = MenuForm("menu.xml", defines.SKIN_PATH, defines.ADDON.getSetting('skin'))
            mnu.li = self.getFocus().getSelectedItem()
            print "mnu.li = %s" % mnu.li.getProperty("commands")
            mnu.get_method = defines.GET
            mnu.session = self.session
            LogToXBMC('Выполнить комманду')
            mnu.doModal()
            LogToXBMC('Комманда выполнена')
            res = mnu.GetResult()
            LogToXBMC('Результат комманды %s' % res)
            if res == 'OK':
                self.updateList()
            elif res == WMainForm.API_ERROR_INCORRECT:
                self.showStatus('Пользователь не опознан по сессии')
            elif res == WMainForm.API_ERROR_NOCONNECT:
                self.showStatus('Ошибка соединения с БД')
            elif res == WMainForm.API_ERROR_ALREADY:
                self.showStatus('Канал уже был добавлен в избранное ранее')
            elif res == WMainForm.API_ERROR_NOPARAM:
                self.showStatus('Ошибка входных параметров')
            elif res == WMainForm.API_ERROR_NOFAVOURITE:
                self.showStatus('Канал не найден в избранном')
            elif res == 'TSCLOSE':
                LogToXBMC("Закрыть TS");
                self.player.EndTS();
        elif action.getId() == WMainForm.ACTION_MOUSE:
            if (self.getFocusId() == WMainForm.CONTROL_LIST):
                self.onFocus(WMainForm.CONTROL_LIST)
        else:
            super(WMainForm, self).onAction(action)

    def updateList(self):
        self.showStatus("Получение списка каналов")
        self.list = self.getControl(50)
        self.initLists()
        thr = defines.MyThread(self.getChannels, 'channel', not (self.cur_category in (WMainForm.CHN_TYPE_TRANSLATION, WMainForm.CHN_TYPE_MODERATION, WMainForm.CHN_TYPE_FAVOURITE)))
        thr.daemon = False
        thr.start()
        thr1 = defines.MyThread(self.getChannels, 'translation', self.cur_category == WMainForm.CHN_TYPE_TRANSLATION)
        thr1.daemon = False
        thr1.start()
        thr2 = defines.MyThread(self.getChannels, 'moderation', self.cur_category == WMainForm.CHN_TYPE_MODERATION)
        thr2.daemon = False
        thr2.start()
        thr3 = defines.MyThread(self.getChannels, 'favourite', self.cur_category == WMainForm.CHN_TYPE_FAVOURITE)
        thr3.start()
        thr4 = defines.MyThread(self.getArcChannels, "", False)
        thr4.start()
        LogToXBMC('Ожидание результата')
        if self.cur_category == WMainForm.CHN_TYPE_FAVOURITE:
            thr3.join(10)
        elif self.cur_category == WMainForm.CHN_TYPE_MODERATION:
            thr2.join(10)
        elif self.cur_category == WMainForm.CHN_TYPE_TRANSLATION:
            thr1.join(10)
        else:
            thr.join(10)
        self.list.reset()
        self.setFocus(self.getControl(WMainForm.BTN_CHANNELS_ID))
        self.img_progress.setVisible(False)
        self.hideStatus()
        LogToXBMC(self.selitem_id)
        

    def showStatus(self, str):
        if self.img_progress: self.img_progress.setVisible(True)
        if self.txt_progress: self.txt_progress.setLabel(str)
        if self.infoform: self.infoform.printASStatus(str)

    def showInfoStatus(self, str):
        if self.infoform: self.infoform.printASStatus(str)

    def hideStatus(self):
        if self.img_progress: self.img_progress.setVisible(False)
        if self.txt_progress: self.txt_progress.setLabel("")

    def fillChannels(self):
        self.showStatus("Заполнение списка")
        if not self.list:
            self.showStatus("Список не инициализирован")
            return
        self.list.reset()
        if len(self.category[self.cur_category]["channels"]) == 0:
            self.fillCategory()
            self.hideStatus()
        else:
            li = xbmcgui.ListItem('..')
            self.list.addItem(li)
            for ch in self.category[self.cur_category]["channels"]:
                self.list.addItem(ch)
            self.hideStatus()

    def fillTranslation(self):
        if not self.list:
            self.showStatus("Список не инициализирован")
            return
        self.showStatus("Заполнение списка")
        self.list.reset()
        for ch in self.translation:
            self.list.addItem(ch)
        self.hideStatus()

    def fillArchive(self):
        if not self.list:
            self.showStatus("Список не инициализирован")
            return
        self.list.reset()
        for ch in self.archive:
            self.list.addItem(ch)
        LogToXBMC("fillArchive");

    def fillCategory(self):
        if not self.list:
            self.showStatus("Список не инициализирован")
            return
        self.list.reset()
        for gr in self.category:
            li = xbmcgui.ListItem(self.category[gr]["name"])
            li.setProperty('type', 'category')
            li.setProperty('id', '%s' % gr)
            self.list.addItem(li)

    def fillRecords(self, li, date = time.localtime()):
        self.showStatus("Загрузка архива")
        LogToXBMC("Show records")
        self.list.reset()
        const_li = xbmcgui.ListItem("..")
        self.list.addItem(const_li)
        const_li = xbmcgui.ListItem("[COLOR FF0080FF]%s-%s-%s[/COLOR]" % (date.day, date.month, date.year))
        const_li.setProperty("type", "rec_date")
        const_li.setProperty("epg_cdn_id", li.getProperty("epg_cdn_id"))
        const_li.setProperty("date", "%s-%s-%s" % (date.year, date.month, date.day))
        self.list.addItem(const_li)
        data = defines.GET("http://api.torrent-tv.ru/v3/arc_records.php?session=%s&date=%d-%d-%s&epg_id=%s&typeresult=json" % (self.session, date.day, date.month, date.year, li.getProperty("epg_cdn_id")), cookie = self.session)
        jdata = json.loads(data)
        if jdata["success"] == 0:
            self.showStatus(jdata["error"])
            return
        
        

        for rec in jdata["records"]:
            rec_date = time.localtime(float(rec["time"]))
            rec_li = xbmcgui.ListItem("[COLOR FFC0C0C0]%.2d:%.2d[/COLOR] %s" % (rec_date.tm_hour, rec_date.tm_min, rec["name"]), rec["name"], li.getProperty("icon"), li.getProperty("icon"))
            rec_li.setProperty("type", "record")
            rec_li.setProperty("id", '%s' % rec["record_id"])
            rec_li.setProperty("epg_cdn_id", '%s' % rec["epg_id"])
            rec_li.setProperty("icon", li.getProperty("icon"))
            self.list.addItem(rec_li)

        self.hideStatus()

    def IsCanceled(self):
        return self.isCanceled