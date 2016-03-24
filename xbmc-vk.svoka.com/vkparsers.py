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

import urllib, urllib2, re, cookielib, base64
import vkapp

try:
    import json
except ImportError:
    import simplejson as json

def GetVideoFilesAPI(codedFiles):
    files = json.loads(base64.decodestring(codedFiles))
    external_url = files.get("external")
    if external_url:
        if "youtube" in external_url:
            start = external_url.find("v=") + len('v=')
            end = external_url.find('&', start)
            if start <= len('embed/'):
                return [external_url]
            if end < 0:
                end = None
            return ["plugin://plugin.video.youtube/?action=play_video&videoid="+external_url[start:end]]
        return [external_url]
    ret = []
    for v in files:
        ret.append(files[v])
    return ret


def GetVideoFiles(url):
    app = vkapp.appManager
    # TODO make this a generic function in appManager
    proc = urllib2.HTTPCookieProcessor()
    proc.cookiejar.set_cookie(cookielib.Cookie(0, 'remixsid', app.GetCookie(),
                                   '80', False, 'vk.com', True, False, '/',
                                   True, False, None, False, None, None, None))
    opener = urllib2.build_opener(urllib2.HTTPHandler(), proc)
    html = opener.open(url).read()    

    player = re.findall(r"\\nvar vars =(.*?});", html)
    if not player:
        yt = re.findall(r"www\.youtube\.com\\/embed\\/(.*?)\?autoplay",html)
        if not yt:
            return ["/unable to play " + url]
        return ["plugin://plugin.video.youtube/?action=play_video&videoid="+str(yt[0])]
    tmp = ""
    for a in player[0]:
        if ord(a)< 128:
            tmp += a
        else:
            tmp += urllib.quote(a)
    player[0] = filter(lambda x: x != "\\", tmp)

    jsonStr = player[0]
    prs = json.loads(jsonStr)

    urlStart = "http://cs" + str(prs["host"]) + ".vk.com/u" + str(prs["uid"]) + "/videos/" + str(prs["vtag"])

    resolutions = ["240", "360", "480", "720", "1080"]
    videoURLs = []
    if prs["no_flv"]!=1:
        if str(prs["uid"])=="0": #strange behaviour on old videos
            urlStart = "http://" + prs["host"] + "/assets/videos/" + str(prs["vtag"]) + str(prs["vkid"]) + ".vk"
        videoURLs.append(urlStart + ".flv")
    
    if prs["hd"]>0 or prs["no_flv"]==1:
        for i in range(int(prs["hd"])+1):
            videoURLs.append(urlStart + "." + resolutions[i] + ".mp4")
    
    videoURLs.reverse()
    return videoURLs

if __name__== '__main__':
    import sys
    if len(sys.argv) > 1:
        try:
            url = "http://vk.com/" + re.findall(r"(video[-0-9]+[-_][0-9]+)", sys.argv[1])[0]
            print url
            for s in GetVideoFiles(url):
                print s
        except Exception, e:
            sys.stderr.writelines(["error: " + str(e) + "\n", "usage: vkparsers.py http://vk.com/video111_222\n"])
    else:
        print("usage: vkparsers.py http://vk.com/video111_222")
