# Copyright (c) 2014 Torrent-TV.RU
# Writer (c) 2014, Welicobratov K.A., E-mail: 07pov23@gmail.com

import xbmcgui
import threading
import xbmcaddon    
import xbmc
import time
import json

import defines

from ts import TSengine as tsengine
#defines
CANCEL_DIALOG  = ( 9, 10, 11, 92, 216, 247, 257, 275, 61467, 61448, )

def LogToXBMC(text, type = 1):
    ttext = ''
    if type == 2:
        ttext = 'ERROR:'

    log = open(defines.ADDON_PATH + '/player.log', 'a')
    print '[MyPlayer %s] %s %s\r' % (time.strftime('%X'),ttext, text)
    log.write('[MyPlayer %s] %s %s\r' % (time.strftime('%X'),ttext, text))
    log.close()
    del log

class MyPlayer(xbmcgui.WindowXML):
    CONTROL_EPG_ID = 109
    CONTROL_PROGRESS_ID = 110
    CONTROL_ICON_ID = 202
    CONTROL_WINDOW_ID = 203
    CONTROL_BUTTON_PAUSE = 204
    CONTROL_BUTTON_INFOWIN = 209
    CONTROL_BUTTON_STOP = 200
    ACTION_RBC = 101

    def __init__(self, *args, **kwargs):
        self.played = False
        self.thr = None
        self.TSPlayer = None
        self.parent = None
        self.li = None
        self.visible = False
        self.t = None
        self.focusId = 203

    def onInit(self):
        if not self.li:
            return
        
        cicon = self.getControl(MyPlayer.CONTROL_ICON_ID)
        cicon.setImage(self.li.getProperty('icon'))
        if not self.parent:
            return
        self.UpdateEpg()
        self.getControl(MyPlayer.CONTROL_WINDOW_ID).setVisible(False)
        self.setFocusId(MyPlayer.CONTROL_EPG_ID)

    def UpdateEpg(self):
        if not self.li:
            return
        epg_id = self.li.getProperty('epg_cdn_id')
        controlEpg = self.getControl(MyPlayer.CONTROL_EPG_ID)
        controlEpg1 = self.getControl(112)
        progress = self.getControl(MyPlayer.CONTROL_PROGRESS_ID)
        if epg_id and self.parent.epg.has_key(epg_id) and self.parent.epg[epg_id].__len__() > 0:
            ctime = time.time()
            curepg = filter(lambda x: (float(x['etime']) > ctime), self.parent.epg[epg_id])
            bt = float(curepg[0]['btime'])
            et = float(curepg[0]['etime'])
            sbt = time.localtime(bt)
            set = time.localtime(et)
            progress.setPercent((ctime - bt)*100/(et - bt))
            controlEpg.setLabel('%.2d:%.2d - %.2d:%.2d %s' % (sbt.tm_hour, sbt.tm_min, set.tm_hour, set.tm_min, curepg[0]['name']))
            #nextepg = ''
            #for i in (1,2,3):
            #    if i >= curepg.__len__():
            #        break
            #    sbt = time.localtime(curepg[i]['btime'])
            #    set = time.localtime(curepg[i]['etime'])
            #    nextepg = nextepg + '%.2d:%.2d - %.2d:%.2d %s\n' % (sbt.tm_hour, sbt.tm_min, set.tm_hour, set.tm_min, curepg[i]['name'])
            #controlEpg1.setLabel(nextepg)
        else:
            controlEpg.setLabel('Нет программы')
            #controlEpg1.setLabel('')
            progress.setPercent(1)

    def Stop(self):
        print 'CLOSE STOP'
        #self.TSPlayer.thr.error = Exception('Stop player')
        xbmc.executebuiltin('PlayerControl(Stop)')

    def Start(self, li):
        pass
        print "Start play "
        if not self.TSPlayer :
            LogToXBMC('InitTS')
            self.TSPlayer = tsengine(parent = self.parent)

        self.li = li
        LogToXBMC('Load Torrent')
        
        self.parent.showStatus("Получение ссылки...")
        data = None
        print li.getProperty("type")
        print li.getProperty("id")
        if (li.getProperty("type") == "channel"):
            data = defines.GET("http://api.torrent-tv.ru/v3/translation_stream.php?session=%s&channel_id=%s&typeresult=json" % (self.parent.session, li.getProperty("id")));
        elif (li.getProperty("type") == "record"):
            data = defines.GET("http://api.torrent-tv.ru/v3/arc_stream.php?session=%s&record_id=%s&typeresult=json" % (self.parent.session, li.getProperty("id")));
        else:
            self.parent.showStatus("Неизвестный тип контента")
            return
        if not data:
            self.parent.showStatus("Ошибка Torrent-TV.RU")
            return
        jdata = json.loads(data);
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
        mode = jdata["type"].upper().replace("CONTENTID","PID")
        self.parent.hideStatus()
        LogToXBMC('Play torrent')
        self.TSPlayer.play_url_ind(0,li.getLabel(), li.getProperty('icon'), li.getProperty('icon'), torrent = url, mode = mode)
        
    def hide(self):
        pass
        #xbmc.executebuiltin('Action(ParentDir)')
        #if self.TSPlayer.playing:
        #    xbmc.executebuiltin('Action(ParentDir)')
        #    print 'Главное меню'

    def getPlayed(self):
        return self.played

    def hideControl(self):
        self.getControl(MyPlayer.CONTROL_WINDOW_ID).setVisible(False)
        self.setFocusId(MyPlayer.CONTROL_WINDOW_ID)
        self.focusId = MyPlayer.CONTROL_WINDOW_ID
        
    def EndTS(self):
        if self.TSPlayer:
            self.TSPlayer.end()
        import subprocess
        import sys

        if sys.platform == 'win32' or sys.platform == 'win64':
            LogToXBMC("Закрыть TS");
            subprocess.Popen('taskkill /F /IM ace_engine.exe /T')
            self.TSPlayer = None

    def onAction(self, action):
        if action in CANCEL_DIALOG:
            LogToXBMC('Closes player %s %s' % (action.getId(), action.getButtonCode()))
            self.close()
        elif action.getId() == MyPlayer.ACTION_RBC:
            LogToXBMC('CLOSE PLAYER 101 %s %s' % (action.getId(), action.getButtonCode()))
            self.close()
        elif action.getId() == 0 and action.getButtonCode() == 61530:
            xbmc.executebuiltin('Action(FullScreen)')
            xbmc.sleep(4000)
            xbmc.executebuiltin('Action(Back)')

        wnd = self.getControl(MyPlayer.CONTROL_WINDOW_ID)
        if not self.visible:
            self.UpdateEpg()
            wnd.setVisible(True)
            if self.focusId == MyPlayer.CONTROL_WINDOW_ID:
                self.setFocusId(MyPlayer.CONTROL_BUTTON_PAUSE)
            else:
                self.setFocusId(self.focusId)
            self.setFocusId(self.getFocusId())
            if self.t:
                self.t.cancel()
                self.t = None
            self.t = threading.Timer(4, self.hideControl)
            self.t.start()

    def onClick(self, controlID):
        if controlID == MyPlayer.CONTROL_BUTTON_STOP:
            self.close()
        if controlID == self.CONTROL_BUTTON_INFOWIN:
            self.parent.showInfoWindow()
