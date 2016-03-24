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

import sys,urllib, urllib2, cookielib, re,  string, xbmc #, xbmcaddon, xbmc, xbmcgui, xbmcplugin, os

def GetCookie(mail,passw):
    host = 'https://login.vk.com/'
    post = urllib.urlencode({
        'act':'login',
    'q':'1',
    'al_frame':'1',
    'expire':'',
    'captcha_sid':'',
    'captcha_key':'',
    'from_host':'vk.com',
    'email':mail,
    'pass': passw
    })

    headers = {
    'Referer': 'http://vk.com/al_index.php?act=auth_frame',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.803.0 Safari/535.1',
    'Content-Type': 'application/x-www-form-urlencoded',
              }
    conn = urllib2.Request(host, post, headers)
    data = urllib2.urlopen(conn)
    i = data.info()

    #xbmc.log(str(i))
    cookie = re.findall(r'remixsid=(.*?);', str(i))[0]
    #xbmc.log("Cookie is " + cookie)
    if not cookie or cookie == 'deleted':
        raise Exception("Wrong login!")
    #xbmc.log("koka " + cookie)
    return cookie


class VkontakteCookie:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.cookie = None

    def get_s_value(self):
        #Возвращает уникальный идентификатор, который выдается на домене login.vk.com
        host = 'http://login.vk.com/'
        post = urllib.urlencode({'email' : self.email,
                                 'expire' : '',
                                 'pass' : self.password,
                                 'q' : '1',
                                'act' :'login', 'al_frame' : '1', 'captcha_sid' : '', 'captcha_key' : '',
        'from_host':'vk.com'})

        headers = {'User-Agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; ru; rv:1.9.0.13) Gecko/2009073022 Firefox/3.0.13',
                   'Host' : 'login.vk.com',
                   'Referer' : 'http://vk.com/',
                   'Origin' : 'http://vk.com/',
                   'Connection' : 'close',
                   'Pragma' : 'no-cache',
                   'Cache-Control' : 'no-cache'
                  }

        conn = urllib2.Request(host, post, headers)
        data = urllib2.urlopen(conn)
        ssv = data.read()
        return re.findall(r"name='s' value='(.*?)'", ssv)[0]

    def get_cookie(self):
        #Возвращает remixsid из куки
        if self.cookie: return self.cookie

        host = 'http://vkontakte.ru/login.php?op=slogin'
        post = urllib.urlencode({'s' : self.get_s_value()})
        headers = {'User-Agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; ru; rv:1.9.0.13) Gecko/2009073022 Firefox/3.0.13',
                   'Host' : 'vkontakte.ru',
                   'Referer' : 'http://login.vk.com/?act=login',
                   'Connection' : 'close',
                   'Cookie' : 'remixchk=5; remixsid=nonenone',
                   'Pragma' : 'no-cache',
                   'Cache-Control' : 'no-cache'
                  }
        conn = urllib2.Request(host, post, headers)
        data = urllib2.urlopen(conn)
        cookie_src = data.info().get('Set-Cookie')
        cooke_str = re.sub(r'(expires=.*?;\s|path=\/;\s|domain=\.vkontakte\.ru(?:,\s)?)', '', cookie_src)
        self.cookie =  cooke_str.split("=")[-1].split(";")[0].strip()
        if not self.cookie:
            raise Exception('Wrong login')
        return self.cookie



