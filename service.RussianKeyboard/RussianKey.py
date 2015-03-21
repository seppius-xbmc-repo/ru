# -*- coding: utf-8 -*-
import os, sys, re
from traceback import print_exc

import xbmc, xbmcgui

if not xbmc.getCondVisibility('system.platform.Android'): import pyperclip
from xbmcaddon import Addon
import urllib2, urllib, httplib, time
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson

__settings__ = Addon( "service.RussianKeyboard" )
__addonDir__ = __settings__.getAddonInfo( "path" )
__language__ = __settings__.getLocalizedString
__profile__  = xbmc.translatePath( __settings__.getAddonInfo('profile') )

XBMC_SKIN  = xbmc.getSkinDir()
SKINS_PATH = os.path.join( __addonDir__, "resources", "skins" )
ADDON_SKIN = ( "default", XBMC_SKIN )[ os.path.exists( os.path.join( SKINS_PATH, XBMC_SKIN ) ) ]
MEDIA_PATH = os.path.join( SKINS_PATH, ADDON_SKIN, "media" )

ACTION_PARENT_DIR     = 9
ACTION_PREVIOUS_MENU  = (10, 92)
ACTION_CONTEXT_MENU   = 117
WORD_PER_PAGE = [9,6,5,4,3,3,3]

CTRL_ID_BACK = 8
CTRL_ID_SPACE = 32
CTRL_ID_RETN = 300
CTRL_ID_SYMBOL = 302
CTRL_ID_CLIP = 900

CTRL_ID_CAPS = 303
CTRL_ID_RU = 304
CTRL_ID_LEFT = 305
CTRL_ID_RIGHT = 306
CTRL_ID_IP = 307
CTRL_ID_TEXT = 310
CTRL_ID_HEAD = 311
CTRL_ID_CODE = 401
CTRL_ID_HZLIST = 402

class InputWindow(xbmcgui.WindowXMLDialog):
    def __init__( self, *args, **kwargs ):
        self.totalpage = 1
        self.nowpage = 0
        self.words = ''
        self.wordperpage = WORD_PER_PAGE[0]
        self.inputString = kwargs.get("default") or ""
        self.heading = kwargs.get("heading") or ""
        xbmcgui.WindowXMLDialog.__init__(self)

    def onInit(self):
        self.getControl(CTRL_ID_RU).setSelected(True)
        self.setKeyToRussian()
        self.getControl(CTRL_ID_HEAD).setLabel(self.heading)
        self.getControl(CTRL_ID_CODE).setLabel('')
        self.getControl(CTRL_ID_TEXT).setLabel(self.inputString)
        self.confirmed = False
    

    def onFocus( self, controlId ):
        self.controlId = controlId

    def onClick( self, controlID ):
        if controlID == CTRL_ID_CAPS:#big
            self.setKeyToRussian()
        elif controlID == CTRL_ID_IP:#ip
            dialog = xbmcgui.Dialog()
            value = dialog.numeric( 3, __language__(2), '' )
            self.getControl(CTRL_ID_TEXT).setLabel(self.getControl(CTRL_ID_TEXT).getLabel()+value)
        elif controlID == CTRL_ID_RU:#num
            self.setKeyToRussian()
        elif controlID == CTRL_ID_SYMBOL:#num
            self.setKeyToRussian()

        elif controlID == CTRL_ID_CLIP: #буффер обмена
 
           if not xbmc.getCondVisibility('system.platform.Android'): ou = pyperclip.paste()
           self.getControl(CTRL_ID_TEXT).setLabel(self.getControl(CTRL_ID_TEXT).getLabel()+ou)

        elif controlID == CTRL_ID_BACK:#back
                self.getControl(CTRL_ID_TEXT).setLabel(self.getControl(CTRL_ID_TEXT).getLabel().decode("utf-8")[0:-1])
        elif controlID == CTRL_ID_RETN:#enter
            newText = self.getControl(CTRL_ID_TEXT).getLabel()
            if not newText: newText = '' #return
            self.inputString = newText
            self.confirmed = True
            self.close()
        elif controlID == CTRL_ID_LEFT:#left
            if self.nowpage>0:
                self.nowpage -=1
            self.changepages()
        elif controlID == CTRL_ID_RIGHT:#right
            if self.nowpage<self.totalpage-1:
                self.nowpage +=1
            self.changepages()
        elif controlID == CTRL_ID_SPACE:#space
            self.getControl(CTRL_ID_TEXT).setLabel(self.getControl(CTRL_ID_TEXT).getLabel() + ' ')
        else:
                self.getControl(CTRL_ID_TEXT).setLabel(self.getControl(CTRL_ID_TEXT).getLabel()+self.getControl(controlID).getLabel().encode('utf-8'))

    def onAction(self,action):
       keycode = action.getButtonCode()
        # xbmc remote keyboard control handler
       if self.getControl(CTRL_ID_RU).isSelected():
              keychar = chr(keycode - 61505 + ord('a'))
              if keychar == 'q': keychar = 'й'
              elif keychar == 'Q': keychar = '1'
              elif keychar == 'R': keychar = '2'
              elif keychar == 'S': keychar = '3'
              elif keychar == 'T': keychar = '4'
              elif keychar == 'U': keychar = '5'
              elif keychar == 'V': keychar = '6'
              elif keychar == 'W': keychar = '7'
              elif keychar == 'X': keychar = '8'
              elif keychar == 'Y': keychar = '9'
              elif keychar == 'P': keychar = '0'
              elif keychar == 'w': keychar = 'ц'
              elif keychar == 'e': keychar = 'у'
              elif keychar == 'r': keychar = 'к'
              elif keychar == 't': keychar = 'е'
              elif keychar == 'y': keychar = 'н'
              elif keychar == 'u': keychar = 'г'
              elif keychar == 'i': keychar = 'ш'
              elif keychar == 'o': keychar = 'щ'
              elif keychar == 'p': keychar = 'з'
              elif keychar == '{': keychar = 'х'
              elif keychar == '}': keychar = 'ъ'
              elif keychar == 'a': keychar = 'ф'
              elif keychar == 's': keychar = 'ы'
              elif keychar == 'd': keychar = 'в'
              elif keychar == 'f': keychar = 'а'
              elif keychar == 'g': keychar = 'п'
              elif keychar == 'h': keychar = 'р'
              elif keychar == 'j': keychar = 'о'
              elif keychar == 'k': keychar = 'л'
              elif keychar == 'l': keychar = 'д'
              elif keychar == '[': keychar = 'ж'
              elif keychar == 'G': keychar = 'э'
              elif keychar == 'z': keychar = 'я'
              elif keychar == 'x': keychar = 'ч'
              elif keychar == 'c': keychar = 'с'
              elif keychar == 'v': keychar = 'м'
              elif keychar == 'b': keychar = 'и'
              elif keychar == 'n': keychar = 'т'
              elif keychar == 'm': keychar = 'ь'
              elif keychar == 'L': keychar = 'б'
              elif keychar == 'N': keychar = 'ю'
           
              self.getControl(CTRL_ID_TEXT).setLabel(self.getControl(CTRL_ID_TEXT).getLabel()+keychar)
       else:
        if keycode >= 61728 and keycode <= 61823: 
            keychar = chr(keycode - 61728 + ord(' '))
            if keychar >='0' and keychar <= '9': 
                self.onClick(ord(keychar))
            else:
                self.getControl(CTRL_ID_TEXT).setLabel(self.getControl(CTRL_ID_TEXT).getLabel()+keychar)
        elif keycode == 61706:
            self.onClick(CTRL_ID_RETN)

        # Hard keyboard handler
        elif keycode >= 61505 and keycode <= 61530: #a-z
           
                if self.getControl(CTRL_ID_CAPS).isSelected():
                    keychar = chr(keycode - 61505 + ord('A')) #A-Z
                    pass
                else:
                    keychar = chr(keycode - 61505 + ord('a'))
                    pass
                self.getControl(CTRL_ID_TEXT).setLabel(self.getControl(CTRL_ID_TEXT).getLabel()+keychar)
        elif keycode >= 61488 and keycode <= 61497: #0-9(Eden)-no overlapping code with Dharma
            self.onClick( keycode-61488+48 )
        elif keycode >= 61536 and keycode <= 61545: #0-9(Dharma)-no overlapping code with Eden
            self.onClick( keycode-61536+48 )
        elif keycode == 61500 or keycode == 192700: #Eden & Dharma scancode difference
            self.onClick( CTRL_ID_LEFT ) # <
        elif keycode == 61502 or keycode == 192702: #Eden & Dharma scancode difference
            self.onClick( CTRL_ID_RIGHT ) # >
        elif keycode == 61472:
            self.onClick( CTRL_ID_SPACE )
        elif keycode == 61448:
            self.onClick( CTRL_ID_BACK )
        elif action.getId() in ACTION_PREVIOUS_MENU:
            self.close()

    def changepages (self):
        self.getControl(CTRL_ID_HZLIST).setLabel('')
        num=0
        if self.nowpage == 0:
            hzlist = ''
        else:
            hzlist = '< '
        for i in range(self.nowpage*(self.wordperpage+1), len(self.words)):
            hzlist = hzlist+str(num)+'.'+self.words[i]+' '
            num+=1
            if num > self.wordperpage: break
        if self.nowpage < self.totalpage-1:
            hzlist = hzlist + '>'
        self.getControl(CTRL_ID_HZLIST).setLabel(hzlist)


    def setKeyToRussian (self):
        self.getControl(CTRL_ID_CODE).setLabel('')
        if self.getControl(CTRL_ID_RU).isSelected():
            if self.getControl(CTRL_ID_CAPS).isSelected():
                i = 48
                for c in u'АБВГДЕЁЖЗИ':
                    self.getControl(i).setLabel(c)
                    i+=1
                    if i > 57: break
                i = 65
                for c in u'ЙЛЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ.,-':
                    self.getControl(i).setLabel(c)
                    i+=1
                    if i > 90: break
                for j in range(i,90+1):
                    self.getControl(j).setLabel('')
            else:
                i = 48
                for c in u'абвгдеёжзи':
                    self.getControl(i).setLabel(c)

                    i+=1
                    if i > 57: break
                i = 65
                for c in u'йклмнопрстуфхцчшщъыьэюя.,-':
                    self.getControl(i).setLabel(c)
                    i+=1
                    if i > 90: break
                for j in range(i,90+1):
                    self.getControl(j).setLabel('')
        else:
            for i in range(48, 57+1):
                keychar = chr(i - 48 + ord('0'))
                self.getControl(i).setLabel(keychar)
            if self.getControl(CTRL_ID_CAPS).isSelected():
                for i in range(65, 90+1):
                    keychar = chr(i - 65 + ord('A'))
                    self.getControl(i).setLabel(keychar)
            else:
                for i in range(65, 90+1):
                    keychar = chr(i - 65 + ord('a'))
                    self.getControl(i).setLabel(keychar)
        if self.getControl(CTRL_ID_SYMBOL).isSelected():
                i = 48
                for c in '~!@#$%^&*(':
                    self.getControl(i).setLabel(c)
                    i+=1
                    if i > 57: break
                i = 65
                for c in ')_+-=[]{};:,.<>/?|        ':
                    self.getControl(i).setLabel(c)
                    i+=1
                    if i > 90: break
                for j in range(i,90+1):
                    self.getControl(j).setLabel('')
        self.getControl(400).setVisible(False)

    def isConfirmed(self):
        return self.confirmed

    def getText(self):
        return self.inputString
    
   
class Keyboard:
    def __init__( self, default='', heading='' ):
        self.confirmed = False
        self.inputString = default
        self.heading = heading

    def doModal (self):
        self.win = InputWindow("DialogKeyboardRussian.xml", __addonDir__, ADDON_SKIN, heading=self.heading, default=self.inputString )
        self.win.doModal()
        self.confirmed = self.win.isConfirmed()
        self.inputString = self.win.getText()
        del self.win

    def setHeading(self, heading):
        self.heading = heading

    def isConfirmed(self):
        return self.confirmed

    def getText(self):
        return self.inputString
