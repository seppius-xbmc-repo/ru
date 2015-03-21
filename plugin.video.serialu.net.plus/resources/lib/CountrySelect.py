# -*- coding: utf-8 -*-

import xbmcgui, urllib
#import demjson3 as json

LIST = 146

class CountrySelectDialog(xbmcgui.WindowXMLDialog):
  def __init__(self, *args, **kwargs):
    xbmcgui.WindowXMLDialog.__init__(self)
    self.MainScreen = kwargs.get('MainScreen')

  def onInit(self):
    xbmcgui.WindowXMLDialog.onInit(self)
    country_list = self.getControl(LIST)
    #---
    item = xbmcgui.ListItem('Все страны')
    item.setProperty('country_id', '')
    country_list.addItem(item)
    #---
    for rec in self.getData():
        item = xbmcgui.ListItem(rec.capitalize())
        item.setProperty('country_id', rec)
        country_list.addItem(item)
    self.setFocusId(LIST)

  def onClick(self, control_id):
    country_list = self.getControl(LIST)
    #self.close()
    self.MainScreen.country = country_list.getSelectedItem().getProperty('country_id')
    self.MainScreen.getControl(122).setLabel(country_list.getSelectedItem().getLabel())
    self.MainScreen.country_changed = True
    self.close()

  def getData(self):
    data = self.MainScreen.Auth.Data.get_Country(1)
    #-- parse data
    list = []
    for rec in data:
        list.append(rec[0])

    return list