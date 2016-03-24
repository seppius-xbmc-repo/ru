#!/usr/bin/python
# -*- coding: utf-8 -*-
# VK-XBMC add-on
# Copyright (C) 2011 Volodymyr Shcherban
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
__author__ = 'Volodymyr Shcherban'

from vk_auth import auth
import xbmcaddon
import xbmc


__settings__ = xbmcaddon.Addon(id='xbmc-vk.svoka.com')
__language__ = __settings__.getLocalizedString


APP_ID = "2054573"


from vkapicaller import ApiFromToken


class XBMCVkAppCreator:
    def __init__(self):
        self.instance = None

    def GetInstance(self):
        return self.instance or self.NewInstance()

    def NewInstance(self):
        token = __settings__.getSetting('auth_token')
        if len(token or "") < 5:
            token = self._requestToken()
        self.instance = ApiFromToken(token)
        return self.instance

    def _requestToken(self):
        token = None
        count = 5
        while not token and count > 0:
            count -= 1
            login, password = self._askLogin()
            token = auth(login, password, APP_ID, "KUPNPTTQGApLFVOVgqdx", 'friends,groups,photos,audio,video,offline')
            if token:
                __settings__.setSetting('auth_token', token)
        return token

    def _askLogin(self):
        user_keyboard = xbmc.Keyboard()
        user_keyboard.setHeading(__language__(30001))
        user_keyboard.setHiddenInput(False)
        user_keyboard.setDefault(__settings__.getSetting('username'))
        user_keyboard.doModal()
        if user_keyboard.isConfirmed():
            username = user_keyboard.getText()
            pass_keyboard = xbmc.Keyboard()
            pass_keyboard.setHeading(__language__(30002))
            pass_keyboard.setHiddenInput(True)
            pass_keyboard.doModal()
            if pass_keyboard.isConfirmed():
                return username, pass_keyboard.getText()
            else:
                raise Exception("Password input was cancelled.")
        else:
            raise Exception("Login input was cancelled.")


appManager = XBMCVkAppCreator()


def GetApi():
    return appManager.GetInstance()
