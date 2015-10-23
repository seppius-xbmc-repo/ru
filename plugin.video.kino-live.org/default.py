#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#   Writer (c) 23/06/2011, Khrysev D.A., E-mail: x86demon@gmail.com
#
#   This Program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2, or (at your option)
#   any later version.
#
#   This Program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; see the file COPYING.  If not, write to
#   the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#   http://www.gnu.org/licenses/gpl.html

import urllib
import urllib2
import re
import sys
import os
import cookielib

import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmc

from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
import socket

socket.setdefaulttimeout(50)

icon = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''), 'icon.png'))
siteUrl = 'kino-live2.org'
httpSiteUrl = 'http://' + siteUrl

__settings__ = xbmcaddon.Addon(id='plugin.video.kino-live.org')
__addondir__ = xbmc.translatePath(__settings__.getAddonInfo('profile'))
if os.path.exists(__addondir__) == False:
    os.mkdir(__addondir__)
cookiepath = os.path.join(__addondir__, 'plugin.video.kino-live.org.lwp')

h = int(sys.argv[1])

def construct_request(params):
    return '%s?%s' % (sys.argv[0], urllib.urlencode(params))


def htmlEntitiesDecode(string):
    return BeautifulStoneSoup(string, convertEntities=BeautifulStoneSoup.HTML_ENTITIES).contents[0]


def showMessage(heading, message, times=3000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, icon))

headers = {
'User-Agent': 'Opera/9.80 (X11; Linux i686; U; ru) Presto/2.7.62 Version/11.00',
'Accept': ' text/html, application/xml, application/xhtml+xml, image/png, image/jpeg, image/gif, image/x-xbitmap, */*',
'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
'Accept-Charset': 'utf-8, utf-16, *;q=0.1',
'Accept-Encoding': 'identity, *;q=0'
}

def GET(url, referer, post_params=None):
    headers['Referer'] = referer

    if post_params != None:
        post_params = urllib.urlencode(post_params)
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
    elif headers.has_key('Content-Type'):
        del headers['Content-Type']

    jar = cookielib.LWPCookieJar(cookiepath)
    if os.path.isfile(cookiepath):
        jar.load()

    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))
    urllib2.install_opener(opener)
    req = urllib2.Request(url, post_params, headers)

    response = opener.open(req)
    the_page = response.read()
    response.close()

    jar.save()

    return the_page


def logout(params):
    GET(httpSiteUrl + '/index.php?action=logout', httpSiteUrl)
    __settings__.setSetting("Login", "");
    __settings__.setSetting("Password", "")


def check_login():
    login = __settings__.getSetting("Login")
    password = __settings__.getSetting("Password")

    if len(login) > 0:
        http = GET(httpSiteUrl, httpSiteUrl)
        if http == None: return None

        beautifulSoup = BeautifulSoup(http)
        userPanel = beautifulSoup.find('a', {"id": "loginlink"})

        if userPanel == None:
            os.remove(cookiepath)

            loginResponse = GET(httpSiteUrl, httpSiteUrl, {
            'login': 'submit',
            'login_name': login,
            'login_password': password,
            'submit': 'Вход'
            })

            loginSoup = BeautifulSoup(loginResponse)
            userPanel = loginSoup.find('a', {"id": "loginlink"})
            if userPanel == None:
                showMessage('Login', 'Check login and password', 3000)
            else:
                return userPanel.text.encode('utf-8', 'cp1251')
        else:
            return userPanel.text.encode('utf-8', 'cp1251')
    return None


def mainScreen(params):
    login = check_login()
    if login != None:
        li = xbmcgui.ListItem('[Закладки %s]' % login.replace('Привет, ', ''))
        uri = construct_request({
        'href': httpSiteUrl + '/favorites/',
        'mode': 'readCategory'
        })
        xbmcplugin.addDirectoryItem(h, uri, li, True)

    li = xbmcgui.ListItem('[Категории]')
    uri = construct_request({
    'href': httpSiteUrl,
    'mode': 'getCategories'
    })
    xbmcplugin.addDirectoryItem(h, uri, li, True)

    li = xbmcgui.ListItem('[По годам]')
    uri = construct_request({
    'mode': 'getTags'
    })
    xbmcplugin.addDirectoryItem(h, uri, li, True)

    li = xbmcgui.ListItem('[Поиск]')
    uri = construct_request({
    'mode': 'runSearch'
    })
    xbmcplugin.addDirectoryItem(h, uri, li, True)

    readCategory({
    'href': httpSiteUrl + '/lastnews/'
    });


def readCategory(params, postParams=None):
    categoryUrl = urllib.unquote_plus(params['href'])
    http = GET(categoryUrl, httpSiteUrl, postParams)
    if http == None: return False

    beautifulSoup = BeautifulSoup(http)
    content = beautifulSoup.find('div', attrs={'id': 'dle-content'})
    dataRows = content.findAll('div', 'tezt')

    if len(dataRows) == 0:
        showMessage('ОШИБКА', 'Неверная страница', 3000)
        return False
    else:
        for data in dataRows:
            img = data.find('img')
            cover = None
            if img != None:
                cover = img['src']
                if cover.find("://") < 0:
                    cover = httpSiteUrl + cover
            titleContainer = data.findPrevious('div', 'ah1')
            if titleContainer == None:
                titleContainer = data.findPrevious('h1')
            href = titleContainer.find('a')
            if href is None:
                titleText = titleContainer.text
                href = data.findNextSibling('div', 'more').find('a')
            else:
                titleText = href.text
            titleText = titleText.encode('utf-8', 'cp1251')

            link = data.findNextSibling('div', 'more').find('a')
            href = link['href']
            plotEl = data.find('div', id=re.compile('news-id-\d+'))
            itemInfo = []
            for plotItemRow in plotEl.contents:
                try:
                    itemInfo.append(plotItemRow.encode('utf-8', 'cp1251'))
                except:
                    pass
            plot = "\n".join(itemInfo[2:])
            li = xbmcgui.ListItem(titleText, iconImage=cover, thumbnailImage=cover)
            li.setProperty('IsPlayable', 'false')
            li.setInfo(type='video', infoLabels={'title': titleText, 'plot': plot})
            uri = construct_request({
            'mode': 'getFiles',
            'cover': cover,
            'title': titleText,
            'href': href
            })
            xbmcplugin.addDirectoryItem(h, uri, li, True)

    #TODO: Find a way to use pager in search results
    if postParams == None:
        try:
            pager = content.find('div', 'pages')
            pages = pager.findAll('a')
            nextPageLink = pages[len(pages) - 1]
            if nextPageLink != None:
                li = xbmcgui.ListItem('[NEXT PAGE >]')
                li.setProperty('IsPlayable', 'false')
                uri = construct_request({
                'href': nextPageLink['href'],
                'mode': 'readCategory'
                })
                xbmcplugin.addDirectoryItem(h, uri, li, True)
        except:
            pass

    xbmcplugin.endOfDirectory(h)


def getCategories(params):
    categoryUrl = urllib.unquote_plus(params['href'])
    http = GET(categoryUrl, httpSiteUrl)
    if http == None: return False

    beautifulSoup = BeautifulSoup(http)
    categoryContainer = beautifulSoup.find('ul', 'cats')
    categories = categoryContainer.findAll('a')
    if len(categories) == 0:
        showMessage('ОШИБКА', 'Неверная страница', 3000)
        return False
    else:
        for link in categories:
            if link != None:
                title = link.string
                if title == None:
                    title = link.find("h2").string
                href = link['href']
                if href.find("://") < 0:
                    href = httpSiteUrl + href
                li = xbmcgui.ListItem('[%s]' % title)
                li.setProperty('IsPlayable', 'false')
                uri = construct_request({
                'href': href,
                'mode': 'readCategory'
                })
                xbmcplugin.addDirectoryItem(h, uri, li, True)

    xbmcplugin.endOfDirectory(h)


def getTags(params):
    http = GET(httpSiteUrl + '/tags/', httpSiteUrl)
    if http == None: return False

    beautifulSoup = BeautifulSoup(http)
    tagsContainer = beautifulSoup.find('td', 'news')
    tags = tagsContainer.findAll('a')
    if len(tags) == 0:
        showMessage('ОШИБКА', 'Неверная страница', 3000)
        return False
    else:
        tags.reverse()
        for link in tags:
            if link != None:
                title = link.string
                href = link['href']
                if href.find("://") < 0:
                    href = httpSiteUrl + href
                li = xbmcgui.ListItem('[%s]' % title)
                li.setProperty('IsPlayable', 'false')
                uri = construct_request({
                'href': href,
                'mode': 'readCategory'
                })
                xbmcplugin.addDirectoryItem(h, uri, li, True)

    xbmcplugin.endOfDirectory(h)


def getFiles(params):
    folderUrl = urllib.unquote_plus(params['href'])
    cover = urllib.unquote_plus(params['cover'])
    itemName = urllib.unquote_plus(params['title'])

    http = GET(folderUrl, httpSiteUrl)
    if http == None: return False

    playListRegexp = re.compile('pl=([^"]+)', re.IGNORECASE + re.DOTALL + re.MULTILINE)
    playlist = playListRegexp.findall(http)

    if len(playlist) > 0:
        commentRegexp = re.compile('"comment":"\s*([^"]+)', re.IGNORECASE + re.DOTALL + re.MULTILINE)
        fileRegexp = re.compile('"file":"\s*([^"]+)', re.IGNORECASE + re.DOTALL + re.MULTILINE)
        playlistJson = GET(httpSiteUrl + playlist[0], folderUrl)
        comments = commentRegexp.findall(playlistJson)
        files = fileRegexp.findall(playlistJson)
        i = 0
        for comment in comments:
            li = xbmcgui.ListItem(comment, iconImage=cover, thumbnailImage=cover)
            li.setProperty('IsPlayable', 'true')
            li.setInfo(type='video', infoLabels={'title': itemName + ' - ' + comment})
            uri = construct_request({
            'mode': 'play',
            'file': files[i],
            'referer': folderUrl
            })
            xbmcplugin.addDirectoryItem(h, uri, li)
            i = i + 1
        xbmcplugin.endOfDirectory(h)
    else:
        fileRegexp = re.compile('file=([^"]+)', re.IGNORECASE + re.DOTALL + re.MULTILINE)
        files = fileRegexp.findall(http)

        li = xbmcgui.ListItem(itemName, iconImage=cover, thumbnailImage=cover)
        li.setProperty('IsPlayable', 'true')
        li.setInfo(type='video', infoLabels={'title': itemName})
        xbmc.Player().play(getFile(files[0]), li)


def runSearch(params):
    skbd = xbmc.Keyboard()
    skbd.setHeading('Что ищем?')
    skbd.doModal()
    if skbd.isConfirmed():
        SearchStr = skbd.getText()
        params = {
        'href': httpSiteUrl
        }
        postParams = {
        'do': 'search',
        'subaction': 'search',
        'story': SearchStr.decode('utf-8').encode('cp1251')
        }
        return readCategory(params, postParams)

def play(params):
    referer = urllib.unquote_plus(params['referer'])
    file = urllib.unquote_plus(params['file'])
    headers['Referer'] = referer

    i = xbmcgui.ListItem(path=getFile(file))
    xbmcplugin.setResolvedUrl(h, True, i)


def getFile(files):
    files = files.split(' or ')
    file = files[0]
    if len(files) == 2:
        fileTest = urllib.urlopen(files[1])
        fileUrl = fileTest.geturl()
        if fileUrl:
            file = fileUrl
    return file

def get_params(paramstring):
    param = []
    if len(paramstring) >= 2:
        params = paramstring
        cleanedparams = params.replace('?', '')
        if (params[len(params) - 1] == '/'):
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]
    return param

params = get_params(sys.argv[2])

mode = None
func = None

try:
    mode = urllib.unquote_plus(params['mode'])
except:
    mainScreen(params)

if (mode != None):
    try:
        func = globals()[mode]
    except:
        pass
    if func: func(params)
