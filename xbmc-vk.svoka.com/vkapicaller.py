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

import urllib
try:
    import json
except ImportError:
    import simplejson as json

try:
    from hashlib import md5
except ImportError:
    from md5 import md5


def ApiFromToken(token):
    return VkApp(token)


class VkApp:
    def __init__(self, access_token):
        #param is API call parameters
        if not access_token:
            raise Exception("Trying to create API without token")
        self.param = {'access_token': access_token}

    def call(self, api, **call_params):
        v = dict()
        v.update(self.param)
        v.update(call_params)

        request = "&".join(["%s=%s" % (str(key), urllib.quote(str(v[key]))) for key in v.keys()])
        request_url = "https://api.vk.com/method/" + api + "?" + request

        reply = urllib.urlopen(request_url)
        resp = json.load(reply)
        if "error" in resp:
            raise Exception("Error, error! DATA: " + str(resp))
        else:
            return resp["response"]
