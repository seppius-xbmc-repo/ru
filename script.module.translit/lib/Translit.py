#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.3
# License: GPLv3

import os, sys, json
import xbmc, xbmcaddon


class Translit():
    def __init__(self, encoding='utf-8'):
        self.version = "1.0.3"
        self.plugin = "Translit" + self.version

        self.id = 'script.module.translit'
        self.addon = xbmcaddon.Addon(self.id)
        self.icon = self.addon.getAddonInfo('icon')
        self.path = xbmc.translatePath(self.addon.getAddonInfo('path'))
        self.resource = xbmc.translatePath(os.path.join(self.path, 'lib')).decode("utf-8")
        
        self.encoding = encoding
        self.transtable = self.getTranstable()
        
        sys.path.append(self.path)


    def getTranstable(self):
        try:
            file_path = os.path.join(self.resource, "transtable.json" )
            json_tuple = open(file_path).read()

            try:
              transtable = json.loads(json_tuple)
              return transtable
            except Exception, e:
              print e
              return ()

        except IOError, e:
            print e
            return ()

    def rus(self, in_string):
        russian = unicode(in_string)
        for symb_out, symb_in in self.transtable:
          russian = russian.replace(symb_in, symb_out)
        return russian.encode(self.encoding)

    def eng(self, in_string):
        translit = unicode(in_string)
        for symb_out, symb_in in self.transtable:
          translit = translit.replace(symb_out, symb_in)
        return translit.encode(self.encoding)
