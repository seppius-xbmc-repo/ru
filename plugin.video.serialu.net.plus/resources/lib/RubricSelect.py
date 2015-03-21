# -*- coding: utf-8 -*-

import xbmcgui, urllib

LIST = 146

class RubricSelectDialog(xbmcgui.WindowXMLDialog):
  def __init__(self, *args, **kwargs):
    xbmcgui.WindowXMLDialog.__init__(self)
    self.MainScreen = kwargs.get('MainScreen')

  def onInit(self):
    xbmcgui.WindowXMLDialog.onInit(self)
    rubrics_list = self.getControl(LIST)
    #---
    item = xbmcgui.ListItem('Все рубрики')
    item.setProperty('rubric_id', '')
    rubrics_list.addItem(item)
    #---
    for rec in self.getData():
        item = xbmcgui.ListItem(rec.capitalize())
        item.setProperty('rubric_id', rec)
        rubrics_list.addItem(item)
    self.setFocusId(LIST)

  def onClick(self, control_id):
    rubrics_list = self.getControl(LIST)
    #self.close()
    self.MainScreen.rubric = rubrics_list.getSelectedItem().getProperty('rubric_id')
    self.MainScreen.getControl(123).setLabel(rubrics_list.getSelectedItem().getLabel())
    self.MainScreen.rubric_changed = True
    self.close()

  def getData(self):
    data = self.MainScreen.Auth.Data.get_Rubric()
    #-- parse data
    list = []
    for rec in data:
        list.append(rec[0])

    return list