# Copyright (c) 2013 Torrent-TV.RU
# Writer (c) 2013, Welicobratov K.A., E-mail: 07pov23@gmail.com
# Edited (c) 2015, Vorotilin D.V., E-mail: dvor85@mail.ru

import xbmcgui
import time
import json

import defines

def LogToXBMC(text, type = 1):
    ttext = ''
    if type == 2:
        ttext = 'ERROR:'
 
    log = open(defines.ADDON_PATH + '/menuform.log', 'a')
    print '[MenuForm %s] %s %s\r' % (time.strftime('%X'),ttext, text)
    log.write('[MenuForm %s] %s %s\r' % (time.strftime('%X'),ttext, text))
    log.close()
    del log

class MenuForm(xbmcgui.WindowXMLDialog):
    CMD_ADD_FAVOURITE = 'favourite_add.php'
    CMD_DEL_FAVOURITE = 'favourite_delete.php'
    CMD_UP_FAVOURITE = 'favourite_up.php'
    CMD_DOWN_FAVOURITE = 'favourite_down.php'
    CMD_CLOSE_TS = 'close_ts'
    CONTROL_CMD_LIST = 301
    def __ini__(self, *args, **kwargs):
        self.li = None
        self.get_method = None
        self.session = None
        self.result = 'None'
        pass

    def onInit(self):
        self.result = 'None'
        if not self.li:
            return
        try:
            cmds = self.li.getProperty('commands').split(',')
            list = self.getControl(MenuForm.CONTROL_CMD_LIST)
            list.reset()
            for c in cmds:
                if c == MenuForm.CMD_ADD_FAVOURITE:
                    title = 'Добавить в избранное'
                elif c == MenuForm.CMD_DEL_FAVOURITE:
                    title = 'Удалить из избранного'
                elif c == MenuForm.CMD_UP_FAVOURITE:
                    title = 'Поднять вверх'
                elif c == MenuForm.CMD_DOWN_FAVOURITE:
                    title = 'Опустить вниз'
                elif c == MenuForm.CMD_CLOSE_TS:
                    title = 'Завершить TS'
                list.addItem(xbmcgui.ListItem(title, c))
            list.setHeight(cmds.__len__()*38)
            list.selectItem(0)
            self.setFocusId(MenuForm.CONTROL_CMD_LIST)
            LogToXBMC('Focus Controld %s' % self.getFocusId())
        except Exception, e: 
            LogToXBMC("В списке нет комманд %s" % e)
            pass

    def onClick(self, controlId):
        LogToXBMC('ControlID = %s' % controlId)
        if controlId == MenuForm.CONTROL_CMD_LIST:
            lt = self.getControl(MenuForm.CONTROL_CMD_LIST)
            li = lt.getSelectedItem()
            cmd = li.getLabel2()
            LogToXBMC("cmd=%s" % cmd)
    
            if cmd == MenuForm.CMD_CLOSE_TS: 
                self.CloseTS()
            else:
                self._sendCmd(cmd)
            self.close()

    def _sendCmd(self, cmd):
        channel_id = self.li.getLabel2()
        res = self.get_method('http://api.torrent-tv.ru/v3/%s?session=%s&channel_id=%s&typeresult=json' % (cmd, self.session, channel_id), cookie = self.session)
        LogToXBMC(res)
        LogToXBMC('http://api.torrent-tv.ru/v3/%s?session=%s&channel_id=%s&typeresult=json' % (cmd, self.session, channel_id))
        jdata = json.loads(res)
        if jdata['success'] == '0':
            self.result = jdata['error']
        else:
            self.result = 'OK'

    def CloseTS(self):
        LogToXBMC('Closet TS')
        self.result = 'TSCLOSE'

    def GetResult(self):
        if not self.result:
            self.result = 'None'
        res = self.result
        self.result = 'None'
        return res