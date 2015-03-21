#-*- coding: utf-8 -*-
'''
    Torrenter plugin for XBMC
    Copyright (C) 2012 Vadim Skorba
    vadim.skorba@gmail.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import xbmcgui
import xbmcplugin
import sys
import Localization

class Rates(xbmcgui.Window):

    buttonWidth = 250
    buttonHeight = 250
    width = 1280
    height = 720
    rate = 0

    def __init__(self, *kargs):
        noFocus  = sys.modules[ "__main__"].__root__ + '/icons/bookmarks.png'
        focus  = sys.modules[ "__main__"].__root__ + '/icons/add_bookmark.png'
        self.addControl(xbmcgui.ControlLabel(0, self.height/4, self.width, 100, Localization.localize('Please, rate watched video:'), alignment=6))
        self.bad = xbmcgui.ControlButton(self.buttonWidth/2, self.height/2, self.buttonWidth, self.buttonHeight, Localization.localize('Bad'), alignment=6, textColor='0xFFCC3333', focusedColor='0xFFFF0000', focusTexture=focus, noFocusTexture=noFocus, shadowColor='0xFF000000')
        self.normal = xbmcgui.ControlButton(self.width/2-self.buttonWidth/2, self.height/2, self.buttonWidth, self.buttonHeight, Localization.localize('So-So'), alignment=6, textColor='0xFFCCCC33', focusedColor='0xFFFFFF00', focusTexture=focus, noFocusTexture=noFocus, shadowColor='0xFF000000')
        self.good = xbmcgui.ControlButton(self.width-self.buttonWidth*3/2, self.height/2, self.buttonWidth, self.buttonHeight, Localization.localize('Good'), alignment=6, textColor='0xFF33CC33', focusedColor='0xFF00FF00', focusTexture=focus, noFocusTexture=noFocus, shadowColor='0xFF000000')
        self.addControl(self.bad)
        self.addControl(self.normal)
        self.addControl(self.good)
        self.bad.setNavigation(self.bad, self.bad, self.bad, self.normal)
        self.normal.setNavigation(self.normal, self.normal, self.bad, self.good)
        self.good.setNavigation(self.good, self.good, self.normal, self.good)
        self.setFocus(self.normal)

    def onControl(self, control):
        if control == self.bad:
            self.rate = -1
        if control == self.normal:
            self.rate = 0
        if control == self.good:
            self.rate = 1
        self.close()
