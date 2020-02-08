import xbmcgui
import defines
from contextmenu import ContextMenu
import subprocess

import os

class WMainForm(xbmcgui.WindowXML):
    CANCEL_DIALOG  = ( 9, 10, 11, 92, 216, 247, 257, 275, 61467, 61448, )
    CONTEXT_MENU_IDS = (117, 101)
    CONTROL_LIST = 10
    CONTROL_LABEL_PATH = 12
    CONTROL_LABEL_PATH_INFO = 11
    PAGE_SIZE = 52
    def __init__(self, *args, **kwargs):
        self.mnu = ContextMenu()
        self.mnu.addItem("Удалить", self.onMenuDelete)
        self.mnu.addItem("Получить описание", self.onMenuUpdateInfo)
        self.mnu.addItem("Описание", self.onMenuShowInfo)
        self.mnu.addItem("Обновить", self.onMenuUpdate)
        self.mnu.addItem("Запуск", self.onMenuRun)

    def onInit(self):
        self.list = self.getControl(10);
        self.updateList()
        
    def onFocus(self, ControlID):
        super(WMainForm, self).onFocus(ControlID)

    def onClick(self, controlID):
        if controlID == WMainForm.CONTROL_LIST:
            self.onMenuRun(self.list.getSelectedItem())

    def onAction(self, action):
        if not action:
            super(WMainForm, self).onAction(action)
        elif action in WMainForm.CANCEL_DIALOG:
            self.close()
        elif action.getId() in WMainForm.CONTEXT_MENU_IDS and self.getFocusId() == WMainForm.CONTROL_LIST:
            if action.getId() == 101:
                return
            self.mnu.show(self.getFocus().getSelectedItem())
        else:
            super(WMainForm, self).onAction(action)
    
    def onMenuDelete(self, item):
        file = item.getProperty("filename")
        os.remove(file)
        self.updateList()

    def onMenuUpdateInfo(self, item):
        pass

    def onMenuShowInfo(self, item):
        pass

    def onMenuUpdate(self, item):
        pass

    def onMenuRun(self, item):
        file = item.getProperty("filename")
        if not os.path.exists(file):
            return
        fname, ext = os.path.splitext(file)
        command = defines.ADDON.getSetting("emu%s.command" % (ext))
        command = command.replace("%ROM%", file).split(" ", 1)
        subprocess.Popen(command)

    def updateList(self):
        self.list.reset()
        const_li = xbmcgui.ListItem("..")
        self.list.addItem(const_li)
        files = os.listdir(self._getSearchPath())
        self.getControl(WMainForm.CONTROL_LABEL_PATH).setLabel(self._getSearchPath())
        page = files[:WMainForm.PAGE_SIZE]
        for fn in page:
            name = os.path.basename(fn)
            li = xbmcgui.ListItem(name)
            li.setProperty("filename", os.path.join(self._getSearchPath(),name))
            self.list.addItem(li)
        self.list.addItem(xbmcgui.ListItem("next"))
        label = self.getControl(WMainForm.CONTROL_LABEL_PATH_INFO)
        label.setLabel("страница №%s всего игр %s" % (1, len(files)))

    def _getSearchPath(self):
        return defines.ADDON.getSetting("game.folder").replace("smb:", "")