# -*- coding: utf-8 -*-

import urllib, urllib2, re, sys, json
from bs4 import BeautifulSoup
try:
    import xbmcplugin, xbmcgui
except Exception, e:
    if len(sys.argv) < 3:
        newArgv = [sys.argv[0], 0, '/Users/sevaua/Dropbox/Documents/xbmc/plugin.video.pokerstars.tv/addon.py?title=PCA+2012+-+%2425k+High+Roller&url=http%3A%2F%2Fwww.pokerstars.tv%2Fpoker-video-16338-pca-2012-25k-high-roller.html%3Fchannel_id%3D579&mode=40']
        sys.argv = newArgv
    from test import xbmcplugin1 as xbmcplugin
    from test import xbmcgui1 as xbmcgui


def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
        params=sys.argv[2]
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
                            
    return param

def addLink(title, url):
    item = xbmcgui.ListItem(title, iconImage='DefaultVideo.png', thumbnailImage='')
    item.setInfo( type='Video', infoLabels={'Title': title} )

    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=item)


def addDir(title, url, mode):
    sys_url = sys.argv[0] + '?title=' + urllib.quote_plus(title) + '&url=' + urllib.quote_plus(url) + '&mode=' + urllib.quote_plus(str(mode))

    item = xbmcgui.ListItem(title, iconImage='DefaultFolder.png', thumbnailImage='')
    item.setInfo( type='Video', infoLabels={'Title': title} )

    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=sys_url, listitem=item, isFolder=True)

def GetHTML(url):
    headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3', 'Content-Type':'application/x-www-form-urlencoded'}
    conn = urllib2.urlopen(urllib2.Request(url, urllib.urlencode({}), headers))
    html = conn.read()
    conn.close()
    
    return html 

def getJuicerContent(url):
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    response = opener.open(url)
    content = response.read()
    return content

def getVideoURL(url):
    html = GetHTML(url)
    #presentation_id=20070&amp;autoplay=true&amp;seed_name=pokerstars" 
    presentation_id = re.compile('presentation_id=([0-9]+)').findall(html)[0]
    seed_name = re.compile('seed_name=([a-zA-Z_0-9]+)').findall(html)[0]

    informationURL = 'http://' + seed_name + '.api.videojuicer.com/presentations/' + presentation_id + '.json'
    informationJSON = json.loads(getJuicerContent(informationURL))
    videoTitle = informationJSON['title']
    #{% video %}{% id 2307 %}{% endvideo %}
    videoID = re.compile('id ([0-9]+)').findall(informationJSON["document_content"])[0]
    #http://pokerstars.api.videojuicer.com/assets/video/19854.json
    videojuicerURL = 'http://' + seed_name + '.api.videojuicer.com/assets/video/' + videoID + '.json' 

    content = getJuicerContent(videojuicerURL)
    data = json.loads(content)
    videoURL = data["url"]
    return videoURL, videoTitle

def getChanels(url):
    html = GetHTML(url)
    genre_links = re.compile('<a href="(.+?)" title="View (.+?) now" class="logo">.+?</a>').findall(html)

    for url, title in genre_links:
        yield url, title

def getSeasons(url):
    html = GetHTML(url)
    soup = BeautifulSoup(html)
    div_clm_one = soup.body.find('div', {'id':'template'}, recursive = False).find('div', {'id':'clm-one'}, recursive = False)
    div_box = div_clm_one.find('div', {'class':'box'})
    ul_nav_sub = div_box.find('ul', {'class':'nav_sub'})
    if ul_nav_sub:
        divs = ul_nav_sub.findAll('li')
        if divs:
            for div in divs:
                title = div.a.string
                url1 = div.a['href']
                try:
                    yield url1, title
                except Exception, e:
                    print str(e)

def getMovies(url):
    html = GetHTML(url)
    soup = BeautifulSoup(html)
    videoList = soup.body.find('div', {'class':'results_vidList'}, recursive = True)
    links = videoList.findAll('a', {'class':'vid_thumbSma'})
    next = videoList.find('a', {'class':'next'})
    prev = videoList.find('a', {'class':'prev'})
    if prev:
        yield prev['href'], 'Prev', True
    for link in links:
        title = link['title']
        url1 = link['href']
        yield url1, title, False
    if next:
        yield next['href'], 'Next', True

main_url = 'http://www.pokerstars.tv'

params = get_params()
url    = None
title  = None
mode   = None

try:    title = urllib.unquote_plus(params['title'])
except: pass

try:    url = urllib.unquote_plus(params['url'])
except: pass

try:    mode = int(params['mode'])
except: pass

if mode == None:
    for local_url, title in getChanels(main_url + '/poker-channels'):
        addDir(title, main_url + local_url, 20)

elif mode == 20:
    for local_url, title in getSeasons(url):
        addDir(title, main_url + local_url, 35)

elif mode == 35:
    for local_url, title, isFolder in getMovies(url):
        if isFolder:
            if title != "Prev":
                addDir(title, url + local_url, 35)
        else:
            try:
                #Watch PCA 2012 - $25k High Roller now
                title = re.compile('Watch (.+?) now').findall(title)[0]
            except Exception, e:
                pass
            addDir(title, main_url + local_url, 40)

elif mode == 40:
    local_url, title = getVideoURL(url)
    addLink(title, local_url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))