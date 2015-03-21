import sys,os,time,threading,random,re
import xbmc
import xbmcgui
import xbmcplugin
import xbmcvfs
import socket
import xbmcaddon
import cookielib
import urllib2,urllib
import json,random,httplib

settings = xbmcaddon.Addon(id='script.module.torrent.ts')
language = settings.getLocalizedString
version = "0.0.1"
plugin = "torrent.ts-" + version

print plugin

Addon = xbmcaddon.Addon(id='script.module.torrent.ts')
Addon.setSetting('active','0')

pcook= Addon.getSetting('pcook')

if not pcook: 
    pcook=str(random.randint(0, 0x7fffffff))
    Addon.setSetting('pcook',pcook)
    try:
        cc=httplib.HTTPSConnection('api.parse.com')
        cc.connect()
        params={}
        params['user']=pcook
        params['action']='install'
        cc.request('POST', '/1/classes/Installations',
            json.dumps(params),
            {
            "X-Parse-Application-Id":"FSKJs49Ljj9ibnf9Lyq2tFGDdT1Z6lr1wTEiuLPB",
            "X-Parse-REST-API-Key":"AfsszHeFjXQVD642LAuso0DjDYbCJOyeM6Qj1BiQ",
            "Content-Type":"application/json"
            })
        txt=cc.getresponse().read()
        cc.close()
        print txt
    except: pass