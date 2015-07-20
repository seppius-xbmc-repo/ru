# Copyright (c) 2014 Torrent-TV.RU
# Writer (c) 2014, Welicobratov K.A., E-mail: 07pov23@gmail.com
# Edited (c) 2015, Vorotilin D.V., E-mail: dvor85@mail.ru

import xbmcgui
import threading
import xbmc
import time
import json

import defines

from ts import TSengine as tsengine
# defines
CANCEL_DIALOG = (9, 10, 11, 92, 216, 247, 257, 275, 61467, 61448,)

def LogToXBMC(text, type=1):
    ttext = ''
    if type == 2:
        ttext = 'ERROR:'

    with open(defines.ADDON_PATH + '/player.log', 'a') as log:
        print '[MyPlayer %s] %s %s\r' % (time.strftime('%X'), ttext, text)
        log.write('[MyPlayer %s] %s %s\r' % (time.strftime('%X'), ttext, text))


class MyPlayer(xbmcgui.WindowXML):
    CONTROL_EPG_ID = 109
    CONTROL_PROGRESS_ID = 110
    CONTROL_ICON_ID = 202
    CONTROL_WINDOW_ID = 203
    CONTROL_BUTTON_PAUSE = 204
    CONTROL_BUTTON_INFOWIN = 209
    CONTROL_BUTTON_STOP = 200
    ACTION_RBC = 101
    ARROW_ACTIONS = (1, 2, 3, 4)
    DIGIT_BUTTONS = range(58, 68)
    CH_NAME_ID = 399
    DLG_SWITCH_ID = 299

    def __init__(self, *args, **kwargs):
        
        self.TSPlayer = None
        self.parent = None
        self.li = None
        self.visible = False        
        self.focusId = MyPlayer.CONTROL_WINDOW_ID
        self.nextepg_id = 1
        self.curepg = None
        
        self.select_timer = None
        self.hide_control_timer = None
        self.select_timer = None
        self.hide_swinfo_timer = None
        self.update_epg_lock = threading.RLock()
        
        self.channel_number = 0
        self.channel_number_str = ''
        self.chinfo = None
        self.swinfo = None
        self.control_window = None
        
        

    def onInit(self):
        if not self.li:
            return        
        cicon = self.getControl(MyPlayer.CONTROL_ICON_ID)
        cicon.setImage(self.li.getProperty('icon'))
        self.control_window = self.getControl(MyPlayer.CONTROL_WINDOW_ID)
        self.chinfo = self.getControl(MyPlayer.CH_NAME_ID)
        self.chinfo.setLabel(self.li.getLabel())
        self.swinfo = self.getControl(MyPlayer.DLG_SWITCH_ID)
        self.swinfo.setVisible(False)
        if not self.parent:
            return
    
        if not self.select_timer:
            self.init_channel_number()
        
        LogToXBMC("channel_number = %i" % self.channel_number)
        LogToXBMC("selitem_id = %i" % self.parent.selitem_id)    
        
        defines.MyThread(self.UpdateEpg, self.li).start()
        self.control_window.setVisible(True)
        self.hide_control_window()
        
    def init_channel_number(self):
        if self.channel_number != 0:
            self.parent.selitem_id = self.channel_number
        else:
            self.channel_number = self.parent.selitem_id

    def hide_control_window(self):
        def hide():
            self.control_window.setVisible(False)
            self.setFocusId(MyPlayer.CONTROL_WINDOW_ID)
            self.focusId = MyPlayer.CONTROL_WINDOW_ID 
            
        if self.hide_control_timer:
            self.hide_control_timer.cancel()
            self.hide_control_timer = None
        self.hide_control_timer = threading.Timer(4.9, hide)
        self.hide_control_timer.start()
        
        
    def UpdateEpg(self, li):
        with self.update_epg_lock:
            if not li:
                return
            cicon = self.getControl(MyPlayer.CONTROL_ICON_ID)
            cicon.setImage(li.getProperty('icon'))
            epg_id = li.getProperty('epg_cdn_id')
            controlEpg = self.getControl(MyPlayer.CONTROL_EPG_ID)
            controlEpg1 = self.getControl(112)
            progress = self.getControl(MyPlayer.CONTROL_PROGRESS_ID)
            if not self.parent.epg.has_key(epg_id):
                self.parent.getEpg(epg_id)
            if epg_id and self.parent.epg.has_key(epg_id) and len(self.parent.epg[epg_id]) > 0:
                ctime = time.time()
                self.curepg = filter(lambda x: (float(x['etime']) > ctime), self.parent.epg[epg_id])
                bt = float(self.curepg[0]['btime'])
                et = float(self.curepg[0]['etime'])
                sbt = time.localtime(bt)
                set = time.localtime(et)
                progress.setPercent((ctime - bt) * 100 / (et - bt))
                controlEpg.setLabel('%.2d:%.2d - %.2d:%.2d %s' % (sbt.tm_hour, sbt.tm_min, set.tm_hour, set.tm_min, self.curepg[0]['name']))
                self.setNextEpg()
                
            else:
                controlEpg.setLabel('Нет программы')
                controlEpg1.setLabel('')
                progress.setPercent(1)
        
            
    def setNextEpg(self):
        nextepg = ''
        if len(self.curepg) > 1:
            if self.nextepg_id < 1:
                self.nextepg_id = 1
                return
            elif self.nextepg_id >= len(self.curepg):
                self.nextepg_id = len(self.curepg) - 1
                return
                
            controlEpg1 = self.getControl(112)  
               
            sbt = time.localtime(self.curepg[self.nextepg_id]['btime'])
            set = time.localtime(self.curepg[self.nextepg_id]['etime'])
            nextepg = nextepg + '%.2d:%.2d - %.2d:%.2d %s\n' % (sbt.tm_hour, sbt.tm_min, set.tm_hour, set.tm_min, self.curepg[self.nextepg_id]['name'])
                
        controlEpg1.setLabel(nextepg)         
               

    def Stop(self):
        print 'CLOSE STOP'
        xbmc.executebuiltin('PlayerControl(Stop)')

    def Start(self, li):
        print "Start play "
        if not self.TSPlayer:
            LogToXBMC('InitTS')
            self.TSPlayer = tsengine(parent=self.parent)

        self.li = li
        self.channel_number = self.parent.selitem_id
        LogToXBMC('Load Torrent')
        
        self.parent.showStatus("Получение ссылки...")
        data = None
        print li.getProperty("type")
        print li.getProperty("id")
        if (li.getProperty("type") == "channel"):
            data = defines.GET("http://api.torrent-tv.ru/v3/translation_stream.php?session=%s&channel_id=%s&typeresult=json" % (self.parent.session, li.getProperty("id")))
        elif (li.getProperty("type") == "record"):
            data = defines.GET("http://api.torrent-tv.ru/v3/arc_stream.php?session=%s&record_id=%s&typeresult=json" % (self.parent.session, li.getProperty("id")))
        else:
            self.parent.showStatus("Неизвестный тип контента")
            return
        if not data:
            self.parent.showStatus("Неизвестный тип контента")
            return
        jdata = json.loads(data)
        print jdata
        if not jdata["success"]:
            self.parent.showStatus("Канал временно не доступен")
            return
        if jdata["success"] == 0:
            self.parent.showStatus(data["error"])
            return
        if not jdata["source"]:
            self.parent.showStatus("Канал временно не доступен")
            return
        url = jdata["source"]
        mode = jdata["type"].upper().replace("CONTENTID", "PID")
        self.parent.hideStatus()
        LogToXBMC('Play torrent')
        self.TSPlayer.play_url_ind(0, li.getLabel(), li.getProperty('icon'), li.getProperty('icon'), torrent=url, mode=mode)
        LogToXBMC('End playing')
        
    def hide(self):
        pass
        # xbmc.executebuiltin('Action(ParentDir)')
        # if self.TSPlayer.playing:
        #    xbmc.executebuiltin('Action(ParentDir)')
        #    print 'Главное меню'

    def EndTS(self):
        if self.TSPlayer:
            self.TSPlayer.end()
        import subprocess
        import sys

        if sys.platform == 'win32' or sys.platform == 'win64':
            LogToXBMC("Закрыть TS")
            subprocess.Popen('taskkill /F /IM ace_engine.exe /T')
            self.TSPlayer = None
            
    def run_selected_channel(self):
        self.channel_number = defines.tryStringToInt(self.channel_number_str)        
        LogToXBMC('CHANNEL NUMBER IS: %i' % self.channel_number)              
        if 0 < self.channel_number < self.parent.list.size() and self.parent.selitem_id != self.channel_number:            
            self.parent.selitem_id = self.channel_number
            self.Stop()    
        self.swinfo.setVisible(False)     
        self.channel_number = self.parent.selitem_id  
        self.chinfo.setLabel(self.parent.list.getListItem(self.parent.selitem_id).getLabel()) 
        self.channel_number_str = ''
        

    def onAction(self, action):
        LogToXBMC('Action {} | ButtonCode {}'.format(action.getId(), action.getButtonCode()))
            
        if action in CANCEL_DIALOG:
            LogToXBMC('Closes player %s %s' % (action.getId(), action.getButtonCode()))
            self.close()
        elif action.getId() == MyPlayer.ACTION_RBC:
            LogToXBMC('CLOSE PLAYER 101 %s %s' % (action.getId(), action.getButtonCode()))
            self.close()
        elif action.getId() in (3, 4): 
            ############### IF ARROW UP AND DOWN PRESSED - SWITCH CHANNEL ###############
            if action.getId() == 3:
                self.channel_number += 1
                if self.channel_number >= self.parent.list.size():
                    self.channel_number = 1
            else:
                self.channel_number -= 1
                if self.channel_number <= 0:
                    self.channel_number = self.parent.list.size() - 1
            self.channel_number_str = str(self.channel_number)
            self.swinfo.setVisible(True) 
            li = self.parent.list.getListItem(self.channel_number)                            
            self.chinfo.setLabel(li.getLabel())
            defines.MyThread(self.UpdateEpg, li).start()
            if self.select_timer: 
                self.select_timer.cancel() 
                self.select_timer = None
            self.select_timer = threading.Timer(5, self.run_selected_channel)
            self.select_timer.start()
        elif action.getId() in MyPlayer.DIGIT_BUTTONS:
            ############# IF PRESSED DIGIT KEYS - SWITCH CHANNEL #######################
            self.channel_number_str += str(action.getId() - 58)  
            self.swinfo.setVisible(True) 
            self.channel_number = defines.tryStringToInt(self.channel_number_str) 
            li = self.parent.list.getListItem(self.channel_number)                            
            self.chinfo.setLabel(li.getLabel())
            defines.MyThread(self.UpdateEpg, li).start()
            if self.select_timer: 
                self.select_timer.cancel() 
                self.select_timer = None
            self.select_timer = threading.Timer(5, self.run_selected_channel)
            self.select_timer.start()   
        elif action.getId() == 0 and action.getButtonCode() == 61530:
            xbmc.executebuiltin('Action(FullScreen)')
            xbmc.sleep(4000)
            xbmc.executebuiltin('Action(Back)')
        else:
            defines.MyThread(self.UpdateEpg, self.li).start()

        if not self.visible:            
            if self.focusId == MyPlayer.CONTROL_WINDOW_ID:
                self.setFocusId(MyPlayer.CONTROL_BUTTON_PAUSE)
            else:
                self.setFocusId(self.focusId)
            self.setFocusId(self.getFocusId())
            self.control_window.setVisible(True)
            self.hide_control_window()
            
            
    def onClick(self, controlID):
        if controlID == MyPlayer.CONTROL_BUTTON_STOP:
            self.close()
        if controlID == self.CONTROL_BUTTON_INFOWIN:
            self.parent.showInfoWindow()
