import xbmcgui
import xbmcaddon
import defines

class ContextMenu:
    def __init__(self, *args, **kwargs):
        self.menus = {}
    
    def addItem(self, name, action):
        self.menus[name] = action;

    def show(self, item):
        mnu = MenuForm("menu.xml", defines.SKIN_PATH, "default")
        mnu.menu = self.menus
        mnu.owner = item
        mnu.doModal()

class MenuForm(xbmcgui.WindowXMLDialog):
    CONTROL_CMD_LIST = 100
    def __ini__(self, *args, **kwargs):
        self.menu = {}
        self.owner = ""

    def onInit(self):
        self.fill()

    def onClick(self, controlID):
        if controlID == MenuForm.CONTROL_CMD_LIST:
            lt = self.getControl(MenuForm.CONTROL_CMD_LIST)
            li = lt.getSelectedItem()
            cmd = li.getLabel()
            self.menu[cmd](self.owner)
            self.close()

    def onAction(self, action):
        super(MenuForm, self).onAction(action)

    def fill(self):
        list = self.getControl(MenuForm.CONTROL_CMD_LIST)
        list.reset()
        for k in self.menu:
            list.addItem(xbmcgui.ListItem(k))
        list.setHeight(self.menu.__len__()*39)
        list.selectItem(0)
        self.setFocusId(MenuForm.CONTROL_CMD_LIST)