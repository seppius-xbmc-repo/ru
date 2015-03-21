# -*- coding: utf-8 -*-

import xbmcgui, urllib
#import demjson3 as json

LIST = 146

class GenreSelectDialog(xbmcgui.WindowXMLDialog):
  def __init__(self, *args, **kwargs):
    xbmcgui.WindowXMLDialog.__init__(self)
    self.MainScreen = kwargs.get('MainScreen')

  def onInit(self):
    xbmcgui.WindowXMLDialog.onInit(self)
    genres_list = self.getControl(LIST)
    #---
    item = xbmcgui.ListItem('Все жанры')
    item.setProperty('genre_id', '')
    genres_list.addItem(item)
    #---
    for rec in self.getData():
        item = xbmcgui.ListItem(rec.capitalize())
        item.setProperty('genre_id', rec)
        genres_list.addItem(item)
    self.setFocusId(LIST)

  def onClick(self, control_id):
    genres_list = self.getControl(LIST)
    #self.close()
    self.MainScreen.genre = genres_list.getSelectedItem().getProperty('genre_id')
    self.MainScreen.getControl(121).setLabel(genres_list.getSelectedItem().getLabel())
    self.MainScreen.genre_changed = True
    self.close()

  def getData(self):
    data = self.MainScreen.Auth.Data.get_Genre(5)
    #-- parse data
    list = []
    for rec in data:
        list.append(rec[0])

    return list