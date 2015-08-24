#!/usr/bin/python
# -*- coding: utf-8 -*-

import httplib
import urllib
import urllib2

import re

import sys
import os

import xbmcplugin
import xbmcgui
import xbmc
import xbmcaddon
import time
import random
from urllib import unquote, quote
import json

__addon__ = xbmcaddon.Addon( id = 'plugin.video.twitch.tv' )
__language__ = __addon__.getLocalizedString
addon_icon    = xbmc.translatePath(os.path.join(__addon__.getAddonInfo('path'),'icon.png'))
addon_fanart  = __addon__.getAddonInfo('fanart')
addon_path    = __addon__.getAddonInfo('path')
addon_type    = __addon__.getAddonInfo('type')
addon_id      = __addon__.getAddonInfo('id')
addon_author  = __addon__.getAddonInfo('author')
addon_name    = __addon__.getAddonInfo('name')
addon_version = __addon__.getAddonInfo('version')
hos = int(sys.argv[1])
lang = __addon__.getLocalizedString
UA = '%s/%s %s/%s/%s' % (addon_type, addon_id, urllib.quote_plus(addon_author), addon_version, urllib.quote_plus(addon_name))




conf_file = os.path.join(xbmc.translatePath('special://temp/'), 'settings.twitchtv.dat')
xbmcplugin.setContent(int(sys.argv[1]), 'movies')
csort = __addon__.getSetting('csort')
gsort = __addon__.getSetting('gsort')
pcook= __addon__.getSetting('pcook')
if not pcook: 
    pcook=str(random.randint(0, 0x7fffffff))
    __addon__.setSetting('pcook',pcook)

def showMessage(heading, message, times = 3000, pics = addon_icon):
    try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading.encode('utf-8'), message.encode('utf-8'), times, pics.encode('utf-8')))
    except Exception, e:
        xbmc.log( '[%s]: showMessage: Transcoding UTF-8 failed [%s]' % (addon_id, e), 2 )
        try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, pics))
        except Exception, e:
            xbmc.log( '[%s]: showMessage: exec failed [%s]' % (addon_id, e), 3 )

def construct_request(params):
    return '%s?%s' % (sys.argv[0], urllib.urlencode(params))
    
def GET(target, post=None):
    print target
    try:
        req = urllib2.Request(url = target, data = post, headers = {'User-Agent':UA})
        resp = urllib2.urlopen(req)
        CE = resp.headers.get('content-encoding')
        http = resp.read()
        resp.close()
        return http
    except Exception, e:
        xbmc.log( '[%s]: GET EXCEPT [%s]' % (addon_id, e), 4 )
        showMessage('HTTP ERROR', e, 5000)

try: 
    list=__addon__.getSetting('black')
    bl=list.split(',')
except: 
    list=''
    bl=[]
try: 
    glist=__addon__.getSetting('Gblack')
    gbl=glist.split(',')
except: 
    glist=''
    gbl=[]

def main_menu(params):
    toParse('AppOpened',{})
    li = xbmcgui.ListItem((lang(30010)), addon_fanart, addon_icon)
    li.setProperty('IsPlayable', 'false')
    uri = construct_request({
        'func': 'get_favorites'
    })
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    
    li = xbmcgui.ListItem((lang(30012)), addon_fanart, addon_icon)
    li.setProperty('IsPlayable', 'false')
    uri = construct_request({
        'func': 'get_featured'
    })
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    
    li = xbmcgui.ListItem((lang(30013)), addon_fanart, addon_icon)
    li.setProperty('IsPlayable', 'false')
    uri = construct_request({
        'func': 'get_games'
    })
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    
    if len(bl)>1 or len(gbl)>1:
        li = xbmcgui.ListItem('Black List', addon_fanart, addon_icon)
        li.setProperty('IsPlayable', 'false')
        uri = construct_request({
            'func': 'get_black'
        })
        xbmcplugin.addDirectoryItem(hos, uri, li, True)
    
    xbmcplugin.endOfDirectory(hos)


  
def toParse(what,params):
    #try:

        #poid=__addon__.getSetting('poid')
        
        cc=httplib.HTTPSConnection('api.parse.com',443)
        cc.connect()
        params['user']=pcook
        print json.dumps({"dimensions": params})
        print '/1/events/%s'%what
        cc.request('POST', '/1/events/%s'%what,
        json.dumps({"dimensions": params}),
        {
        "X-Parse-Application-Id":"UFH35vkZwVtgheIFTegWhPgHQqgdIARN5xCUkkrW",
        "X-Parse-REST-API-Key":"FOb2PCacJb4nu34RLp6qH4yvotMZrxM123lo8fjc",
        "Content-Type":"application/json"
        })
        txt=cc.getresponse().read()
        cc.close()
        #poid= json.loads(txt)['objectId']
        #__addon__.setSetting('poid',poid)

        
            
        print txt
        
    #except: pass

 
    
def get_black(params):	#print games
    for n in bl[1::]:
        li = xbmcgui.ListItem('Показывать пользователя [COLOR=FF00FF00]%s[/COLOR]'%n, addon_fanart, addon_icon)
        li.setProperty('IsPlayable', 'false')
        uri = construct_request({
            'mode':'n',
            'name':n,
            'func': 'remove_black'
        })
        xbmcplugin.addDirectoryItem(hos, uri, li, True)
    for n in gbl[1::]:
        li = xbmcgui.ListItem('Показывать игру [COLOR=FFFF0000]%s[/COLOR]'%n, addon_fanart, addon_icon)
        li.setProperty('IsPlayable', 'false')
        uri = construct_request({
            'mode':'g',
            'name':n,
            'func': 'remove_black'
        })
        xbmcplugin.addDirectoryItem(hos, uri, li, True)
    xbmcplugin.endOfDirectory(hos)
    
def remove_black(params):
    
    if params['mode']=='g': 
        toParse('remove_BLG',{"nm":params['name']})
        gbl.remove(params['name'])
        print gbl
        __addon__.setSetting('Gblack',','.join(gbl))
    if params['mode']=='n': 
        toParse('remove_BLU',{"ch":params['name']})
        bl.remove(params['name'])
        print bl
        __addon__.setSetting('black',','.join(bl))
def get_games(params):

    http = GET('https://api.twitch.tv/kraken/games/top?limit=100')
    json1=json.loads(http)
    for entries in json1['top']:
        title= entries['game']['name'].encode('utf-8')
        pic= entries['game']['box']['large']
        chls=entries['channels']
        viewers=entries['viewers']
        li = xbmcgui.ListItem('%s [COLOR=88888888](v:%s ch:%s)[/COLOR]'%(title,viewers,chls), addon_fanart, pic)
        li.addContextMenuItems([('%s в черный список'%title, 'XBMC.RunPlugin(%s?func=addGBlack&id=%s&pl=gam)' % (sys.argv[0],  title),),])
        li.setProperty('IsPlayable', 'false')
        uri = construct_request({
            'game': title.replace(' ','+'),
            'func': 'get_stream_list'
        })
        if title not in gbl: xbmcplugin.addDirectoryItem(hos, uri, li, True)
    if gsort=='0': xbmcplugin.addSortMethod(hos,xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(hos)
#https://api.twitch.tv/kraken/streams/featured
def get_featured(params):
    http = GET('https://api.twitch.tv/kraken/streams/featured?limit=100')
    json1=json.loads(http)
#	print json1
    for entries in json1['featured']:
        #print entries
        try:
            title=entries['stream']['channel']['status']
        except:
            title='untitled'
        name=entries['stream']['channel']['name']
        game=entries['stream']['channel']['game']
        
        pic=entries['stream']['preview']['large']
        ico=entries['stream']['channel']['logo']
        if not ico: ico=pic
        viewers=entries['stream']['viewers']
        li = xbmcgui.ListItem('[COLOR=FFFF0000](%s)[/COLOR] %s [COLOR=FF00FF00](%s)[/COLOR]'%(name.encode('utf-8'),title,viewers), pic, ico)
        li.setProperty('IsPlayable', 'true')
        if game: li.addContextMenuItems([('%s в черный список'%name.encode('utf-8'), 'XBMC.RunPlugin(%s?func=addBlack&id=%s&pl=fea)' % (sys.argv[0],  name)),('%s в черный список'%game.encode('utf-8'), 'XBMC.RunPlugin(%s?func=addGBlack&id=%s&pl=fea)' % (sys.argv[0],  game),),])
        else: li.addContextMenuItems([('%s в черный список'%name.encode('utf-8'), 'XBMC.RunPlugin(%s?func=addBlack&id=%s&pl=fea)' % (sys.argv[0],  name)),])
        uri = construct_request({
            'name': name,
            'game': game,
            'func': 'get_stream'
        })
        if name not in bl and game not in gbl: xbmcplugin.addDirectoryItem(hos, uri, li)

    if csort=='0': xbmcplugin.addSortMethod(hos,xbmcplugin.SORT_METHOD_LABEL)
    xbmc.executebuiltin('Container.SetViewMode(500)')
    toParse('GetFeatured',{})
    xbmcplugin.endOfDirectory(hos)
    
def addBlack(params):
    toParse('add_BLG',{"nm":params['id']})
    try: list=__addon__.getSetting('black')
    except: list=''
    list="%s,%s"%(list,params['id'])
    __addon__.setSetting('black',list)
    if params['pl']=='str': xbmc.executebuiltin('Container.Refresh(%s?func=get_stream_list&game=%s)' % (sys.argv[0],params['game'].replace(' ','%2b')))
    if params['pl']=='fea': xbmc.executebuiltin('Container.Refresh(%s?func=get_featured)' % sys.argv[0])
def addGBlack(params):
    toParse('add_BLU',{"ch":params['id']})
    try: list=__addon__.getSetting('Gblack')
    except: list=''
    list="%s,%s"%(list,params['id'])
    __addon__.setSetting('Gblack',list)
    if params['pl']=='gam': xbmc.executebuiltin('Container.Refresh(%s?func=get_games)' % sys.argv[0])
    if params['pl']=='fea': xbmc.executebuiltin('Container.Refresh(%s?func=get_featured)' % sys.argv[0])
    
def get_favorites(params):
    
    subs=__addon__.getSetting('subs')
    
    link='https://api.twitch.tv/kraken/users/%s/follows/channels'%subs
    http = GET(link)
    json1=json.loads(http)
    #try:
    cnt= len(json1['follows'])
    ggg=""
    for entries in json1['follows']:
        name=entries['channel']['name']
        #https://api.twitch.tv/kraken/streams?channel=zisss,voyboy
        ggg=ggg+name+","
        
        #    xbmcplugin.addDirectoryItem(hos, uri, li)
        #else: cnt=cnt-1
    strm= GET("https://api.twitch.tv/kraken/streams?channel="+ ggg)
    json1=json.loads(strm)
    
    for entries in json1['streams']:
        print entries
        try:
            title=entries['channel']['status']
        except:
            title='untitled'
        name=entries['channel']['name']
        pic=entries['preview']['large']
        ico=entries['channel']['logo']
        if not ico: ico=pic
        viewers=entries['viewers']
        li = xbmcgui.ListItem('[COLOR=FFFF0000](%s)[/COLOR] %s [COLOR=FF00FF00](%s)[/COLOR]'%(name.encode('utf-8'),title,viewers), pic, ico)
        #li.addContextMenuItems([('%s в черный список'%name.encode('utf-8'), 'XBMC.RunPlugin(%s?func=addBlack&id=%s&pl=str&game=%s)' % (sys.argv[0],  name, params['game'])),])
        li.setProperty('IsPlayable', 'true')
        uri = construct_request({
            'name': name,
            'func': 'get_stream'
        })
        xbmcplugin.addDirectoryItem(hos, uri, li)
    if csort=='0': xbmcplugin.addSortMethod(hos,xbmcplugin.SORT_METHOD_LABEL)
    xbmc.executebuiltin('Container.SetViewMode(500)')
    #except: pass
    xbmcplugin.endOfDirectory(hos)
    
def get_stream_list(params):
    toParse('ShowStreams',{"Game":params['game']})
    http = GET('https://api.twitch.tv/kraken/streams?game=%s&limit=50'%params['game'])
    json1=json.loads(http)
    #print http
    for entries in json1['streams']:
        #print entries['channel']
        try:
            title=entries['channel']['status']
        except:
            title='untitled'
        name=entries['channel']['name']
        pic=entries['preview']['large']
        ico=entries['channel']['logo']
        if not ico: ico=pic
        viewers=entries['viewers']
        li = xbmcgui.ListItem('[COLOR=FFFF0000](%s)[/COLOR] %s [COLOR=FF00FF00](%s)[/COLOR]'%(name.encode('utf-8'),title,viewers), pic, ico)
        li.addContextMenuItems([('%s в черный список'%name.encode('utf-8'), 'XBMC.RunPlugin(%s?func=addBlack&id=%s&pl=str&game=%s)' % (sys.argv[0],  name, params['game'])),])
        li.setProperty('IsPlayable', 'true')
        uri = construct_request({
            'name': name,
            'game': params['game'],
            'func': 'get_stream'
        })
        if name not in bl: xbmcplugin.addDirectoryItem(hos, uri, li)

    if csort=='0': xbmcplugin.addSortMethod(hos,xbmcplugin.SORT_METHOD_LABEL)
    xbmc.executebuiltin('Container.SetViewMode(500)')
    xbmcplugin.endOfDirectory(hos)
    
def get_stream(params):	
    try: game=params['game'].replace('+',' ')
    except: game=''
    toParse('Play',{"game":game,"channel":params['name']})
    playLive(params['name'],True)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
def playLive(name, play=False):
        name=name.replace('live_user_','')
        headers = {'User-agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0',
            'Referer' : 'http://www.justin.tv/'+name}
        url1 = 'http://usher.justin.tv/find/'+name+'.json?type=live'
        
        url='http://api.twitch.tv/api/channels/%s/access_token'%name
        data = json.loads(GET(url))

        token= data['token']
        sig=data['sig']

        url2='http://usher.twitch.tv/api/channel/hls/%s.m3u8?sig=%s&token=%s&allow_source=true'%(name,sig,token)

        data=GET(url2)

        qual='226,360,480,720,1080'
        quals=qual.split(',')
        qua = int(__addon__.getSetting('video'))

        modev=quals[qua]

        streamurls = data.split('\n')
        pllst=None
        zz=None
        for line in reversed(streamurls):
            print line
            if "http" in line: zz=line
            if modev in line:
                pllst= zz
        if not pllst: pllst=zz
   
        if pllst:
            li = xbmcgui.ListItem(path=pllst)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True,li)	
        else:
            showMessage('Twitch.TV','Стрим не найден')
            return
def getSwfUrl(channel_name):
        """Helper method to grab the swf url, resolving HTTP 301/302 along the way"""
        base_url = 'http://www.justin.tv/widgets/live_embed_player.swf?channel=%s' % channel_name
        headers = {'User-agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0',
                   'Referer' : 'http://www.justin.tv/'+channel_name}
        req = urllib2.Request(base_url, None, headers)
        response = urllib2.urlopen(req)
        return response.geturl()	
    
def get_params(paramstring):
    param=[]
    if len(paramstring)>=2:
        params=paramstring
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=splitparams[1]
    if len(param) > 0:
        for cur in param:
            param[cur] = urllib.unquote_plus(param[cur])
    return param
    
def addon_main():
    print sys.argv[2]
    params = get_params(sys.argv[2])
    try:
        func = params['func']
        del params['func']
    except:
        func = None
        xbmc.log( '[%s]: Primary input' % addon_id, 1 )
        main_menu(params)
    if func != None:
        try: pfunc = globals()[func]
        except:
            pfunc = None
            xbmc.log( '[%s]: Function "%s" not found' % (addon_id, func), 4 )
            showMessage('Internal addon error', 'Function "%s" not found' % func, 2000)
        if pfunc: pfunc(params)
