#!/usr/bin/python
# -*- coding: utf-8 -*-

import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import urllib2, urllib, os, xml.dom.minidom, cookielib, base64

import socket, sys
socket.setdefaulttimeout(15)

h = int(sys.argv[1])
icon   = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'icon.jpg'))
fanart = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'fanart.jpg'))
xbmcplugin.setPluginFanart(h, fanart)


__addon__ = xbmcaddon.Addon(id = 'plugin.video.ulitka.tv')

addon_icon    = __addon__.getAddonInfo('icon')
addon_fanart  = __addon__.getAddonInfo('fanart')
addon_path    = __addon__.getAddonInfo('path')
addon_type    = __addon__.getAddonInfo('type')
addon_id      = __addon__.getAddonInfo('id')
addon_author  = __addon__.getAddonInfo('author')
addon_name    = __addon__.getAddonInfo('name')
addon_version = __addon__.getAddonInfo('version')
addon_profile = __addon__.getAddonInfo('profile')

icon   = xbmc.translatePath(addon_icon)
fanart = xbmc.translatePath(addon_fanart)
profile = xbmc.translatePath(addon_profile)

def showMessage(heading, message, times = 3000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))

def GET(tu, post=None):
    try:
        username = __addon__.getSetting('username')
        password = __addon__.getSetting('password')
        if (not len(username)) and (not len(password)):
            __addon__.openSettings()
            return None
        CJ = cookielib.CookieJar()
        urllib2.install_opener(urllib2.build_opener(urllib2.HTTPCookieProcessor(CJ)))
        if post:
            data = urllib.urlencode(post)
            req = urllib2.Request(tu, data)
        else:
            req = urllib2.Request(tu)
        req.add_header('User-Agent', '%s/%s %s/%s/%s' % (addon_type, addon_id, addon_author, addon_version, urllib.quote_plus(addon_name)))

        #if post:
            #req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        req.add_header('Authorization', 'Basic %s' % base64.b64encode('%s:%s' % (username, password)))

        cookie_path = os.path.join(profile, 'cookie')
        if not os.path.exists(cookie_path):
            os.makedirs(cookie_path)
            print '[%s]: os.makedirs(cookie_path=%s)' % (addon_id, cookie_path)

        cookie_send = {}
        for cookie_fname in os.listdir(cookie_path):
            cookie_file = os.path.join(cookie_path, cookie_fname)
            if os.path.isfile(cookie_file):
                cf = open(cookie_file, 'r')
                cookie_send[os.path.basename(cookie_file)] = cf.read()
                cf.close()
            else: print '[%s]: NOT os.path.isfile(cookie_file=%s)' % (addon_id, cookie_file)

        cookie_string = urllib.urlencode(cookie_send).replace('&','; ')
        req.add_header('Cookie', cookie_string)

        f = urllib2.urlopen(req)

        for Cook in CJ:
            cookie_file = os.path.join(cookie_path, Cook.name)
            cf = open(cookie_file, 'w')
            cf.write(Cook.value)
            cf.close()

        a = f.read()
        f.close()
        return a
    except Exception, e:
        print '[%s]: GET EXCEPTION: %s' % (addon_id, e)
        showMessage(tu, e, 5000)
        return None



def getitems(params):
    http = GET(params['url'])
    if http == None: return False
    document = xml.dom.minidom.parseString(http)
    for item in document.getElementsByTagName('item'):
        info = {'title': None}
        img  = None
        try:
            url = item.getElementsByTagName('url')[0].firstChild.data.encode('utf-8')
        except: url = None
        try: info['title'] = item.getElementsByTagName('title')[0].firstChild.data
        except:
            try: info['title'] = item.getElementsByTagName('label')[0].firstChild.data
            except: pass
        if info['title'] and url:
            IsFolder = False
            try: IsFolder = (int(item.getElementsByTagName(r'isFolder')[0].firstChild.data) == 1)
            except: pass
            try: img = item.getElementsByTagName('thumbnailImage')[0].firstChild.data
            except:
                try: img = item.getElementsByTagName('thumbnailImage')[0].firstChild.data
                except: pass
            try:    info['plot'] = item.getElementsByTagName('plot')[0].firstChild.data
            except: pass
            try:    info['plotoutline'] = item.getElementsByTagName('plotoutline')[0].firstChild.data
            except: pass
            try:    info['duration'] = item.getElementsByTagName('duration')[0].firstChild.data
            except: pass
            try:    info['tagline'] = item.getElementsByTagName('tagline')[0].firstChild.data
            except: pass
            try:    info['genre'] = item.getElementsByTagName('genre')[0].firstChild.data
            except: pass
            try:    info['tvshowtitle'] = item.getElementsByTagName('tvshowtitle')[0].firstChild.data
            except: pass
            try:    info['season'] = int(item.getElementsByTagName('season')[0].firstChild.data)
            except: pass
            try:    info['episode'] = int(item.getElementsByTagName('episode')[0].firstChild.data)
            except: pass
            try: vtype = item.getElementsByTagName('type')[0].firstChild.data
            except: vtype = 'video'
            li = xbmcgui.ListItem(info['title'], iconImage = img, thumbnailImage = img)

            if IsFolder:
                uri = '%s?func=getitems&url=%s' % (sys.argv[0], urllib.quote_plus(url))
            else:
                uri = '%s?func=play&url=%s' % (sys.argv[0], urllib.quote_plus(url))
                try: uri += '&sub=%s' % urllib.quote_plus(str(item.getElementsByTagName('sub')[0].firstChild.data.encode('utf-8')))
                except: pass
                li.setProperty('IsPlayable', 'true')
            li.setInfo(type = vtype, infoLabels = info)
            #li.setProperty('fanart_image', ifanart)
            xbmcplugin.addDirectoryItem(h, uri, li, IsFolder)

    xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_DATE)
    xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_DURATION)
    xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_GENRE)
    xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_TITLE)
    xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_VIDEO_RATING)
    xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_VIDEO_RUNTIME)
    xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_VIDEO_TITLE)
    xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
    xbmcplugin.addSortMethod(h, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(h)

def play(params):
    url = params['url']
    if not '?' in url:
        url += '?version=4.3.132&target=xbmc'
    i = xbmcgui.ListItem( path = url )
    xbmcplugin.setResolvedUrl(h, True, i)
    try:
        sub_url = params['sub']
        http = GET(sub_url)
        if http:
            suba = []
            x = 1
            document = xml.dom.minidom.parseString(http)
            for item in document.getElementsByTagName('p'):
                if item.getAttribute('begin') and item.getAttribute('end'):
                    sub_begin = item.getAttribute('begin').encode('utf-8')
                    sub_end   = item.getAttribute('end').encode('utf-8')
                    sub_data  = item.firstChild.data.encode('utf-8')
                    sub_data  = sub_data.replace('<br />', '\n')
                    suba.append(str(x))
                    suba.append('%s --> %s' % (sub_begin, sub_end))
                    suba.append(sub_data)
                    suba.append('\n')
                    x += 1
            sub_fdata = '\n'.join(suba)
            sub_url = sub_url.replace('.xml','').replace('.mp4','')
            sf = xbmc.translatePath('special://temp/%s.srt' % sub_url.split('/')[-1])
            subf = open(sf, 'w')
            subf.write(sub_fdata)
            subf.close()
            xbmc.sleep(2000)
            xbmc.Player().setSubtitles(sf)
    except: pass

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

def auth():
    cookie_path = os.path.join(profile, 'cookie')
    if os.path.exists(cookie_path):
        for cookie_fname in os.listdir(cookie_path):
            cookie_file = os.path.join(cookie_path, cookie_fname)
            try:
                os.remove(cookie_file)
            except:
                print '[%s]: GET EXCEPTION: %s' % (addon_id, e)
                showMessage(tu, e, 5000)

    token = GET('http://www.ulitka.tv/xbmc/token.php')

    #post form with auth
    username = __addon__.getSetting('username')
    password = __addon__.getSetting('password')
    post = {
        'username': username,
        'passwd': password,
        'remeber': 'yes',
        'option': 'com_user',
        'task': 'login',
        'return': 'L3hibWMvaW5kZXgueG1s',
        token: '1',
    }

    GET('http://www.ulitka.tv/component/user/', post)

def addon_main():
    auth()
    params = get_params(sys.argv[2])
    try:
        func = params['func']
    except:
        getitems({'url':'http://www.ulitka.tv/xbmc/index.xml'})
        func = None

    if func != None:
        try: pfunc = globals()[func]
        except:
            pfunc = None
            print '[%s]: Function "%s" not found' % (addon_id, func)
            showMessage('Internal addon error', 'Function "%s" not found' % func, 2000)
        if pfunc: pfunc(params)
