#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) MEGOGO.NET. All rights reserved.
# Writer (c) 2013, Nevenkin.A.V, E-mail: nuismons@gmail.com
# https://docs.google.com/document/d/1KSuN3WqpzxS1wioS8N435PlIAZYU-BJdz5ZifVyNpfw/edit

import urllib
import urllib2
import hashlib
import sys
import os
import xbmcplugin
import xbmcgui
import xbmc
import xbmcaddon
import re

__addon__ = xbmcaddon.Addon( id = 'plugin.video.megogo.net' )
__language__ = __addon__.getLocalizedString

addon_icon    = __addon__.getAddonInfo('icon')
addon_fanart  = __addon__.getAddonInfo('fanart')
addon_path    = __addon__.getAddonInfo('path')
if (sys.platform == 'win32') or (sys.platform == 'win64'):
    addon_path = addon_path.decode('utf-8')
addon_type    = __addon__.getAddonInfo('type')
addon_id      = __addon__.getAddonInfo('id')
addon_author  = __addon__.getAddonInfo('author')
addon_name    = __addon__.getAddonInfo('name')
addon_version = __addon__.getAddonInfo('version')

MAX_DELAY=600
hos = int(sys.argv[1])
xbmcplugin.setContent(hos, 'movies')

UA = '%s/%s %s/%s/%s' % (addon_type, addon_id, urllib.quote_plus(addon_author), addon_version, urllib.quote_plus(addon_name))

sort=None
if __addon__.getSetting('sort_v')=='0':sortr='add'
if __addon__.getSetting('sort_v')=='1':sort='year'
if __addon__.getSetting('sort_v')=='2':sort='rate'
if __addon__.getSetting('sort_v')=='3':sort='popular'
if not sort: sort='add'
def showMessage(heading, message, times = 3000, pics = addon_icon):
    try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading.encode('utf-8'), message.encode('utf-8'), times, pics.encode('utf-8')))
    except Exception, e:
        xbmc.log( '[%s]: showMessage: Transcoding UTF-8 failed [%s]' % (addon_id, e), 2 )
        try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, pics))
        except Exception, e:
            xbmc.log( '[%s]: showMessage: exec failed [%s]' % (addon_id, e), 3 )

try:
    import simplejson as json
except ImportError:
    try:
        import simplejson as json
        xbmc.log( '[%s]: Error import json. Uses module simplejson' % addon_id, 2 )
    except ImportError:
        try:
            import demjson3 as json
            xbmc.log( '[%s]: Error import simplejson. Uses module demjson3' % addon_id, 3 )
        except ImportError:
            xbmc.log( '[%s]: Error import demjson3. Sorry.' % addon_id, 4 )

import sqlite3 as db
db_name = os.path.join( addon_path, "requests.db" )
c = db.connect(database=db_name)
cu = c.cursor()
from urllib import unquote, quote, quote_plus
import time

def add_to_db(n, item):
    err=0
    m = hashlib.md5()
    m.update(str(n))
    req=m.hexdigest()
    data=quote(item)	
    litm=str(len(data))
    try:
        old=[]
        for row in cu.execute('SELECT time FROM cache ORDER BY time'):
            tout = row[0]
            delay=int(time.time())-int(tout)
            if int(delay)>MAX_DELAY:
                old.append(tout)

        for dels in old:
            print 'запись удалена %s'%str(dels)
            cu.execute("DELETE FROM cache WHERE time = '%s'" % dels)
            c.commit()
    except: pass

    try:
        cu.execute("INSERT INTO cache VALUES ('%s','%s','%s')"%(req,data,int(time.time())))
        c.commit()
    except:
        cu.execute("CREATE TABLE cache (link, data, time int)")
        c.commit()
        cu.execute("INSERT INTO cache VALUES ('%s','%s','%s')"%(req,data,int(time.time())))
        c.commit()


def get_inf_db(n):
    m = hashlib.md5()
    m.update(str(n))
    req=m.hexdigest()
    cu.execute("SELECT time FROM cache WHERE link = '%s'" % req)
    c.commit()
    tout = cu.fetchone()[0]
    if int(tout)>0:
        delay=int(time.time())-int(tout)
        if int(delay)>MAX_DELAY:
            cu.execute("DELETE FROM cache WHERE link = '%s'" % req)
            c.commit()
            info=''
        else:
            cu.execute("SELECT data FROM cache WHERE link = '%s'" % req)
            c.commit()
            info = cu.fetchone()
            
            info= unquote(str(info))
            info=info[3:(len(info)-3)].decode()
        return info
    else: return ''
        
def GET(mCmd, mParams):
    remc=mCmd
    remp=mParams
    session=__addon__.getSetting('session')
    if mParams==[]: mParams={}
    if len(session)>1: mParams['session']=session
    
    req_p1 = []
    req_p2 = []
    if mParams:
        if len(mParams):
            for mKey in mParams:
                req_p1.append('%s=%s' % (mKey, urllib.quote_plus(mParams[mKey])))
                req_p2.append('%s=%s' % (mKey, mParams[mKey]))
    req_params = '&'.join(req_p1)
    req_hash = ''.join(req_p2)
    m = hashlib.md5()
    m.update('%s%s'%(req_hash,'acfed32a68da1d7c'))
    target = 'http://megogo.net/p/%s?%s&sign=%s' % (mCmd, req_params, '%s%s' % (m.hexdigest(), '_xbmc'))
    try:
        http=get_inf_db(target)
    except: http=""
    if len(http)<6:
        try:
            req = urllib2.Request(url = target, data = None, headers = {'User-Agent':UA})
            resp = urllib2.urlopen(req)
            http = resp.read()
            resp.close()
        except:
            __addon__.setSetting('session','')
            login()
            try:
                req = urllib2.Request(url = target, data = None, headers = {'User-Agent':UA})
                resp = urllib2.urlopen(req)
                http = resp.read()
                resp.close()
            except: pass
            print 'error'

    add_to_db(target,http)
    
    oo= get_inf_db(target)
    try:
        return json.loads(http)
    except:
        print 'error'
        return None
        

def login():
    data = GET('login', {'login': __addon__.getSetting('username'), 'pwd':__addon__.getSetting('password')})
    if data:
        urip = {'func': 'run_settings'}
        uri = '%s?%s' % (sys.argv[0], urllib.urlencode(urip))
        if data['result'] == 'ok':
            fav= data['user']['favorites']
            session = data['session']
            __addon__.setSetting('session',session)
        else:
            __addon__.setSetting('session','')
    
def logout(params):

    __addon__.setSetting('session','')
    __addon__.setSetting('username','')
    __addon__.setSetting('password','')

def run_settings(params):
    __addon__.openSettings()
    xbmc.executebuiltin('Container.Update(%s?func=mainScreen)' % sys.argv[0])
def mainScreen(params):
    session=__addon__.getSetting('session')
    
    data = GET('login', {'login': __addon__.getSetting('username'), 'pwd':__addon__.getSetting('password')})
    if data:
        urip = {'func': 'run_settings'}
        uri = '%s?%s' % (sys.argv[0], urllib.urlencode(urip))
        if data['result'] == 'ok':
            fav= data['user']['favorites']
            session = data['session']
            __addon__.setSetting('session',session)
            user = data['user']
            if len(user['nickname']):
                username = user['nickname']
            else:
                username = user['email']
            usr_avatar = 'http://megogo.net%s' % user['avatar_url']
            i = xbmcgui.ListItem('[COLOR FF0FF000]%s - MEGOGO.NET приветствует Вас![/COLOR]' % username.encode('utf-8'), iconImage = usr_avatar, thumbnailImage = usr_avatar)
    
            xbmcplugin.addDirectoryItem(hos, uri, i, True)
        else:
            i = xbmcgui.ListItem('[COLOR FF0FF000]Вы не авторизованы. Проверьте Ваши логин и пароль в настройках дополнения.[/COLOR]')
            xbmcplugin.addDirectoryItem(hos, uri, i, False)
            __addon__.setSetting('session','')
    urip = {'func':'recomendations', 'offset': 0, 'limit': 100 }
    uri = '%s?%s' % (sys.argv[0], urllib.urlencode(urip))
    title='[COLOR FFFFF000]Рекомендованное[/COLOR]'
    i = xbmcgui.ListItem(title, iconImage = addon_icon, thumbnailImage = addon_icon)
    i.setProperty('fanart_image', addon_fanart)
            #i.setInfo(type = 'video', infoLabels = {'title':title})
    xbmcplugin.addDirectoryItem(hos, uri, i, True)
    if session:
        urip = {'func':'favorites', 'mode':'lastview' }
        urip['session'] = session
        uri = '%s?%s' % (sys.argv[0], urllib.urlencode(urip))
        title='[COLOR FFFFF000]Последние просмотры[/COLOR]'
        i = xbmcgui.ListItem(title, iconImage = addon_icon, thumbnailImage = addon_icon)
        i.setProperty('fanart_image', addon_fanart)
                #i.setInfo(type = 'video', infoLabels = {'title':title})
        xbmcplugin.addDirectoryItem(hos, uri, i, True)
    data = GET('categories', [])
    if data:
        for cat in data['category_list']:
            title = '%s' % (cat['title'])
            urip = {'func':'genres', 'category': cat['id'], 'offset': 0, 'limit': 100, 'cname':title.encode('utf-8')}
            if session: urip['session'] = session
            uri = '%s?%s' % (sys.argv[0], urllib.urlencode(urip))
            i = xbmcgui.ListItem(title, iconImage = addon_icon, thumbnailImage = addon_icon)
            i.setProperty('fanart_image', addon_fanart)
            i.setInfo(type = 'video', infoLabels = {'title':title})
            if int(cat['total_num'])>0: xbmcplugin.addDirectoryItem(hos, uri, i, True)
    
    
    
    if session:
        urip = {'func':'favorites', 'offset': 0, 'limit': 100, 'mode':'favorites' }
        urip['session'] = session
        uri = '%s?%s' % (sys.argv[0], urllib.urlencode(urip))
        title='Избранное'
        i = xbmcgui.ListItem(title, iconImage = addon_icon, thumbnailImage = addon_icon)
        i.setProperty('fanart_image', addon_fanart)
                #i.setInfo(type = 'video', infoLabels = {'title':title})
        xbmcplugin.addDirectoryItem(hos, uri, i, True)
        
    li = xbmcgui.ListItem('Поиск', iconImage = addon_icon, thumbnailImage = addon_icon)
    li.setProperty('fanart_image', addon_fanart)
    urip = {'func': 'run_search'}
    uri = '%s?%s' % (sys.argv[0], urllib.urlencode(urip))
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
        
    li = xbmcgui.ListItem('Настройки', iconImage = addon_icon, thumbnailImage = addon_icon)
    li.setProperty('fanart_image', addon_fanart)
    urip = {'func': 'run_settings'}
    uri = '%s?%s' % (sys.argv[0], urllib.urlencode(urip))
    xbmcplugin.addDirectoryItem(hos, uri, li, False)
    
    xbmcplugin.endOfDirectory(hos)

def run_search(params):
    usearch = params.get('usearch', False)
    if not usearch:
        kbd = xbmc.Keyboard()
        kbd.setDefault('')
        kbd.setHeading('Поиск')
        kbd.doModal()
        out=''
        if kbd.isConfirmed():
            out = kbd.getText()
            params['text']=out
    params['offset']='0'
    params['limit']='10'
    search(params)
    
def search(params):
    session=__addon__.getSetting('session')
    data = GET('search', params)
    print data
    cnt=0
    if data:
        for video in data['video_list']:
            print video['type']
            if not(int(video['type'])==5):
                vdata=getInfo(video)
                poster = u'http://megogo.net%s' % video['image']['big']
                title=video['title'].replace('&nbsp;',' ')
                if vdata['fav']=='1': title='* '+title
                i = xbmcgui.ListItem(title, iconImage = poster , thumbnailImage = poster)
                if session:
                    if vdata['fav']=='0': i.addContextMenuItems([('В Избранное MEGOGO', 'XBMC.RunPlugin(%s?func=addFav&id=%s)' % (sys.argv[0],  video['id']),)])
                    if vdata['fav']=='1': i.addContextMenuItems([('Удалить из Избранного MEGOGO', 'XBMC.RunPlugin(%s?func=delFav&id=%s)' % (sys.argv[0],  video['id']),)])
                i.setProperty('fanart_image', addon_fanart)
                urip = {'func':'play', 'video': video['id']}
                if session: urip['session'] = session
                uri = '%s?%s' % (sys.argv[0], urllib.urlencode(urip))
                i.setProperty('IsPlayable', 'true')
                i.setInfo(type = 'video', infoLabels = {'title':title})
                i.setInfo(type='video', infoLabels = vdata['info'])
                if int(video['isSeries'])==0:
                    xbmcplugin.addDirectoryItem(hos, uri, i, False)
                if int(video['isSeries'])==1:
                    urip = {'func':'playseries', 'video': video['id'], 'poster':poster, 'sname':title.encode('utf-8').replace('&nbsp;',' ')}
                    uri = '%s?%s' % (sys.argv[0], urllib.urlencode(urip))
                    xbmcplugin.addDirectoryItem(hos, uri, i, True)
                cnt=cnt+1
        usearch = params.get('usearch', False)
        if not usearch and cnt==100:
            i = xbmcgui.ListItem('ЕЩЕ!', iconImage = addon_icon , thumbnailImage = addon_icon)
            i.setProperty('fanart_image', addon_fanart)
            
            params['func'] = 'videos'
            params['offset'] = int(params['offset']) + int(params['limit']) # TODO x3
            
            uri = '%s?%s' % (sys.argv[0], urllib.urlencode(params))

            i.setInfo(type = 'video', infoLabels = {'title':'ЕЩЕ!'})

            xbmcplugin.addDirectoryItem(hos, uri, i, True)
            
    if __addon__.getSetting('list')=='1': xbmc.executebuiltin('Container.SetViewMode(500)')
    if __addon__.getSetting('list')=='0': xbmc.executebuiltin('Container.SetViewMode(0)')
    xbmcplugin.endOfDirectory(hos)
        
    
def genres(params):
    session=__addon__.getSetting('session')
    tnames=['[COLOR FFFFF000]Новинки[/COLOR]','[COLOR FFFFF000]Последние поступления[/COLOR]','[COLOR FFFFF000]С высоким рейтингом[/COLOR]','[COLOR FFFFF000]Популярные[/COLOR]']
    tvalues=['year','add','rate','popular']
    n=0
    while n<4:
        urip = {'func':'videos', 'sort':tvalues[n],'category': params['category'], 'offset': '0', 'limit': '100', 'category_name':params['cname']}
        urip['session'] = session
        uri = '%s?%s' % (sys.argv[0], urllib.urlencode(urip))
        i = xbmcgui.ListItem(tnames[n], iconImage = addon_icon, thumbnailImage = addon_icon)
        xbmcplugin.addDirectoryItem(hos, uri, i, True)
        n=n+1
    li = xbmcgui.ListItem('[COLOR FFFFF000]Поиск[/COLOR]', iconImage = addon_icon, thumbnailImage = addon_icon)
    li.setProperty('fanart_image', addon_fanart)
    urip = {'func': 'run_search', 'cat_id':params['category']}
    uri = '%s?%s' % (sys.argv[0], urllib.urlencode(urip))
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    if session:
        data=GET('genres', {'session':session, 'category':params['category']})
    else: data=GET('genres', {'category':params['category']})
    if data:
        for genre in data['genre_list']:
            #print genre
            urip = {'func':'videos', 'genre':genre['id'],'category': params['category'], 'offset': '0', 'limit': '100', 'genre_name':(genre['title'].encode('utf-8')), 'category_name':params['cname']}
            urip['session'] = session
            uri = '%s?%s' % (sys.argv[0], urllib.urlencode(urip))
            i = xbmcgui.ListItem(genre['title'], iconImage = addon_icon, thumbnailImage = addon_icon)
            if int(genre['total_num'])>0: xbmcplugin.addDirectoryItem(hos, uri, i, True)
    xbmcplugin.endOfDirectory(hos)
    
    
def recomendations(params):
    
    i = xbmcgui.ListItem("[COLOR FF0FF000]Рекомендованное[/COLOR]", iconImage = addon_icon, thumbnailImage = addon_icon)
    i.setProperty('IsPlayable', 'false')
    xbmcplugin.addDirectoryItem(hos, '', i, False)
    session=__addon__.getSetting('session')
    data = GET('recommend', [])
    if data:
        for video in data['video_list']:
            vdata=getInfo(video)
            poster = u'http://megogo.net%s' % video['image']['big']
            title=video['title'].replace('&nbsp;',' ')
            if vdata['fav']=='1': title='* '+title
            i = xbmcgui.ListItem(title, iconImage = poster , thumbnailImage = poster)
            i.setProperty('fanart_image', addon_fanart)
            if session:
                if vdata['fav']=='0': i.addContextMenuItems([('В Избранное MEGOGO', 'XBMC.RunPlugin(%s?func=addFav&id=%s)' % (sys.argv[0],  video['id']),)])
                if vdata['fav']=='1': i.addContextMenuItems([('Удалить из Избранного MEGOGO', 'XBMC.RunPlugin(%s?func=delFav&id=%s)' % (sys.argv[0],  video['id']),)])
            urip = {'func':'play', 'video': video['id']}
            if session: urip['session'] = session
            uri = '%s?%s' % (sys.argv[0], urllib.urlencode(urip))
            i.setProperty('IsPlayable', 'true')
            i.setInfo(type = 'video', infoLabels = {'title':title})
            i.setInfo(type='video', infoLabels = vdata['info'])
            if int(video['isSeries'])==0:
                xbmcplugin.addDirectoryItem(hos, uri, i, False)
            if int(video['isSeries'])==1:
                urip = {'func':'playseries','sname':title.encode('utf-8').replace('&nbsp;',' '), 'video': video['id'], 'poster':poster}
                uri = '%s?%s' % (sys.argv[0], urllib.urlencode(urip))
                xbmcplugin.addDirectoryItem(hos, uri, i, True)
    if __addon__.getSetting('list')=='1': xbmc.executebuiltin('Container.SetViewMode(500)')
    if __addon__.getSetting('list')=='0': xbmc.executebuiltin('Container.SetViewMode(0)')
    xbmcplugin.endOfDirectory(hos)
def addFav(params):
    data = GET('addfavorite', {'video':params['id']})
def delFav(params):
    data = GET('removefavorite', {'video':params['id']})

def favorites(params):
    
    i = xbmcgui.ListItem("[COLOR FF0FF000]Избранное[/COLOR]", iconImage = addon_icon, thumbnailImage = addon_icon)
    if params['mode']=='lastview': i = xbmcgui.ListItem("[COLOR FF0FF000]Последние просмотры[/COLOR]", iconImage = addon_icon, thumbnailImage = addon_icon)
    i.setProperty('IsPlayable', 'false')
    xbmcplugin.addDirectoryItem(hos, '', i, False)
    mode=params['mode']
    del params['mode']
    session=__addon__.getSetting('session')
    if session:
        data = GET(mode, [])
        if data:
            for video in data['video_list']:
                vdata=getInfo(video)
                poster = u'http://megogo.net%s' % video['image']['big']
                title=video['title'].replace('&nbsp;',' ')
                i = xbmcgui.ListItem(title, iconImage = poster , thumbnailImage = poster)
                if vdata['fav']=='1': i.addContextMenuItems([('Удалить из Избранного MEGOGO', 'XBMC.RunPlugin(%s?func=delFav&id=%s)' % (sys.argv[0],  video['id']),)])
                i.setProperty('fanart_image', addon_fanart)
                urip = {'func':'play', 'video': video['id']}
                if session: urip['session'] = session
                uri = '%s?%s' % (sys.argv[0], urllib.urlencode(urip))
                i.setProperty('IsPlayable', 'true')
                i.setInfo(type = 'video', infoLabels = {'title':title})
                i.setInfo(type='video', infoLabels = vdata['info'])
                if int(video['isSeries'])==0:
                    xbmcplugin.addDirectoryItem(hos, uri, i, False)
                if int(video['isSeries'])==1:
                    urip = {'func':'playseries','sname':title.encode('utf-8').replace('&nbsp;',' '), 'video': video['id'], 'poster':poster}
                    uri = '%s?%s' % (sys.argv[0], urllib.urlencode(urip))
                    xbmcplugin.addDirectoryItem(hos, uri, i, True)
    if __addon__.getSetting('list')=='1': xbmc.executebuiltin('Container.SetViewMode(500)')
    if __addon__.getSetting('list')=='0': xbmc.executebuiltin('Container.SetViewMode(0)')
    xbmcplugin.endOfDirectory(hos)



def videos(params):

    session=__addon__.getSetting('session')
    try:
        if not params['sort']: params['sort']=sort
    except: params['sort']=sort
    toppage=[]
    try: toppage.append('Категория: %s'% params['category_name'])
    except: pass
    try: 
        toppage.append('Жанр: %s'% params['genre_name'])
    except: pass
    try:
        if int(params['offset'])>0:
            toppage.append('Страница: %s'% str(1+int(params['offset']) // 100))
    except: pass
    ttl='[COLOR FF0FF000]'+", ".join(toppage)+'[/COLOR]'
    i = xbmcgui.ListItem(ttl, iconImage = addon_icon, thumbnailImage = addon_icon)
    i.setProperty('IsPlayable', 'false')
    xbmcplugin.addDirectoryItem(hos, '', i, False)
    try:
        if int(params['offset'])==0:
            urip = {'func':'videos', 'category':params['category'], 'sort':'year','genre':params['genre'], 'offset': '-1', 'limit': '100', 'genre_name':params['genre_name'], 'category_name':params['category_name'],}
            uri = '%s?%s' % (sys.argv[0], urllib.urlencode(urip))
            i = xbmcgui.ListItem('[COLOR FFFFF000]Новинки[/COLOR]', iconImage = addon_icon, thumbnailImage = addon_icon)
            xbmcplugin.addDirectoryItem(hos, uri, i, True)
            
            urip = {'func':'videos', 'category':params['category'], 'sort':'add','genre':params['genre'], 'offset': '-1', 'limit': '100','genre_name':params['genre_name'], 'category_name':params['category_name']}
            uri = '%s?%s' % (sys.argv[0], urllib.urlencode(urip))
            i = xbmcgui.ListItem('[COLOR FFFFF000]Последние поступления[/COLOR]', iconImage = addon_icon, thumbnailImage = addon_icon)
            xbmcplugin.addDirectoryItem(hos, uri, i, True)
            
            urip = {'func':'videos', 'category':params['category'], 'sort':'rate','genre':params['genre'], 'offset': '-1', 'limit': '100', 'genre_name':params['genre_name'], 'category_name':params['category_name'],}
            uri = '%s?%s' % (sys.argv[0], urllib.urlencode(urip))
            i = xbmcgui.ListItem('[COLOR FFFFF000]С высоким рейтингом[/COLOR]', iconImage = addon_icon, thumbnailImage = addon_icon)
            xbmcplugin.addDirectoryItem(hos, uri, i, True)
            
            urip = {'func':'videos', 'category':params['category'], 'sort':'popular','genre':params['genre'], 'offset': '-1', 'limit': '100', 'genre_name':params['genre_name'], 'category_name':params['category_name'],}
            uri = '%s?%s' % (sys.argv[0], urllib.urlencode(urip))
            i = xbmcgui.ListItem('[COLOR FFFFF000]Популярное[/COLOR]', iconImage = addon_icon, thumbnailImage = addon_icon)
            xbmcplugin.addDirectoryItem(hos, uri, i, True)
            
            li = xbmcgui.ListItem('[COLOR FFFFF000]Поиск[/COLOR]', iconImage = addon_icon, thumbnailImage = addon_icon)
            li.setProperty('fanart_image', addon_fanart)
            urip = {'func': 'run_search', 'genre_id':params['genre']}
            uri = '%s?%s' % (sys.argv[0], urllib.urlencode(urip))
            xbmcplugin.addDirectoryItem(hos, uri, li, True)
    except: pass
    if int(params['offset'])==-1: params['offset']='0'
    data = GET('videos', params)
    cnt=0
    
    
    if data:
        for video in data['video_list']:
            vdata=getInfo(video)
            poster = u'http://megogo.net%s' % video['image']['big']
            title=video['title'].replace('&nbsp;',' ')
            if vdata['fav']=='1': title='* '+title
            i = xbmcgui.ListItem(title, iconImage = poster , thumbnailImage = poster)
            if session:
                if vdata['fav']=='0': i.addContextMenuItems([('В Избранное MEGOGO', 'XBMC.RunPlugin(%s?func=addFav&id=%s)' % (sys.argv[0],  video['id']),)])
                if vdata['fav']=='1': i.addContextMenuItems([('Удалить из Избранного MEGOGO', 'XBMC.RunPlugin(%s?func=delFav&id=%s)' % (sys.argv[0],  video['id']),)])
            i.setProperty('fanart_image', addon_fanart)
            urip = {'func':'play', 'video': video['id']}
            if session: urip['session'] = session
            uri = '%s?%s' % (sys.argv[0], urllib.urlencode(urip))
            i.setProperty('IsPlayable', 'true')
            i.setInfo(type = 'video', infoLabels = {'title':title})
            i.setInfo(type='video', infoLabels = vdata['info'])
            if int(video['isSeries'])==0:
                xbmcplugin.addDirectoryItem(hos, uri, i, False)
            if int(video['isSeries'])==1:
                urip = {'func':'playseries', 'video': video['id'], 'poster':poster, 'sname':title.encode('utf-8').replace('&nbsp;',' ')}
                uri = '%s?%s' % (sys.argv[0], urllib.urlencode(urip))
                xbmcplugin.addDirectoryItem(hos, uri, i, True)
            cnt=cnt+1
        if cnt==100:
            i = xbmcgui.ListItem('ЕЩЕ!', iconImage = addon_icon , thumbnailImage = addon_icon)
            i.setProperty('fanart_image', addon_fanart)
            
            params['func'] = 'videos'
            params['offset'] = int(params['offset']) + int(params['limit']) # TODO x3
            
            uri = '%s?%s' % (sys.argv[0], urllib.urlencode(params))

            i.setInfo(type = 'video', infoLabels = {'title':'ЕЩЕ!'})

            xbmcplugin.addDirectoryItem(hos, uri, i, True)
            
    if __addon__.getSetting('list')=='1': xbmc.executebuiltin('Container.SetViewMode(500)')
    if __addon__.getSetting('list')=='0': xbmc.executebuiltin('Container.SetViewMode(0)')
    xbmcplugin.endOfDirectory(hos)

def setmode():
    num=__addon__.getSetting('list')
    if num=='0': xbmc.executebuiltin('Container.SetViewMode(0)')
    elif num=='1': xbmc.executebuiltin('Container.SetViewMode(500)')
    
    
def getInfo(video):
    mysetInfo={}
    try: poster=video['poster']
    except: poster=None
    try: desc=video['description'].replace('<p>','').replace('\r\n\r\n','\r\n')
    except: desc=None
    try: rating=video['rating_kinopoisk']
    except: rating=None
    try: year=video['year']
    except: year=None
    try: duration=video['duration']
    except: duration=None
    try: country=video['country']
    except: country=None
    try: genres=video['genre_list']
    except: genres=None
    try: fav=str(video['isFavorite'])
    except: fav='0'
    genre=[]
    try:
        if genres:
            for gnre in genres: genre.append(gnre['title'])
        if len(genre): genre = ', '.join(genre)
    except: genre=''
    try:
        minutes = int(duration) // 60
        hours = minutes // 60
        mysetInfo['duration'] = (int(minutes))
    except: pass
    try: mysetInfo['year'] = int(year)
    except: pass
    try: mysetInfo['rating'] = float(rating)
    except: pass
    mysetInfo['plot'] = desc
    mysetInfo['plotoutline'] = desc
    mysetInfo['genre'] = genre
    
    export={'info':mysetInfo, 'fav':fav}
    return export
    
def playseries(params):
    i = xbmcgui.ListItem('[COLOR FF0FF000]%s[/COLOR]'%params['sname'], iconImage = addon_icon, thumbnailImage = addon_icon)
    i.setProperty('IsPlayable', 'false')
    xbmcplugin.addDirectoryItem(hos, '', i, False)
    poster=params['poster']
    del params['poster']
    try:    session = params['session']
    except: session = None
    data = GET('video', params)
    seasons= data['video'][0]['season_list']
    if len(seasons)>1:
        if data:
            for season in seasons:
                #poster = None
                if season['title_orig']: title='%s (%s)' % (season['title'], season['title_orig'])
                else: title=season['title']
                i = xbmcgui.ListItem(title, iconImage = poster , thumbnailImage = poster)
                urip = {'func':'playepisodes', 'video': params['video'], 'season':season['id'], 'sname':params['sname'], 'title':title.encode('utf-8')}
                if session: urip['session'] = session
                uri = '%s?%s' % (sys.argv[0], urllib.urlencode(urip))
                xbmcplugin.addDirectoryItem(hos, uri, i, True)
        xbmcplugin.endOfDirectory(hos)
    else: 
        urip = {'func':'playepisodes', 'video': params['video'], 'season':seasons[0]['id']}
        playepisodes(urip)

def playepisodes(params):
    try:
        i = xbmcgui.ListItem('[COLOR FF0FF000]%s, %s[/COLOR]'%(params['sname'],params['title']), iconImage = addon_icon, thumbnailImage = addon_icon)
        i.setProperty('IsPlayable', 'false')
        xbmcplugin.addDirectoryItem(hos, '', i, False)
    except: pass
    ses=params['season']
    del params['season']
    try:    session = params['session']
    except: session = None
    data = GET('video', params)
    seasons= data['video'][0]['season_list']
    if data:
        for season in seasons:
            poster = None
            if int(season['id'])==int(ses):
                for episodes in season['episode_list']:
                    title=episodes['title']
                    if len(episodes['title_orig'])>0: title='%s (%s)' % (episodes['title'], episodes['title_orig'])
                    poster = episodes['poster']
                    i = xbmcgui.ListItem(title, iconImage = poster , thumbnailImage = poster)
                    urip = {'func':'playepisodes', 'video': episodes['id']}
                    urip = {'func':'play', 'video': episodes['id']}
                    if session: urip['session'] = session
                    i.setProperty('IsPlayable', 'true')
                    uri = '%s?%s' % (sys.argv[0], urllib.urlencode(urip))
                    xbmcplugin.addDirectoryItem(hos, uri, i, False)
    xbmcplugin.endOfDirectory(hos)

def play(params):
    qu= __addon__.getSetting('qual_v')
    bitrate=['240','320','360','480','576','720','1080']
    if qu>0: params['bitrate']=bitrate[int(qu)-1]
    data = GET('info', params)
    i = xbmcgui.ListItem( path = data['src'] )
    xbmcplugin.setResolvedUrl(hos, True, i)

    
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
    params = get_params(sys.argv[2])
    try:
        func = params['func']
        del params['func']
    except:
        func = None
        xbmc.log( '[%s]: Primary input' % addon_id, 1 )
        mainScreen(params)
    if func != None:
        try: pfunc = globals()[func]
        except:
            pfunc = None
            xbmc.log( '[%s]: Function "%s" not found' % (addon_id, func), 4 )
            showMessage('Internal addon error', 'Function "%s" not found' % func, 2000)
        if pfunc: pfunc(params)
