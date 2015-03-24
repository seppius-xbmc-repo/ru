#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#     Writer (c) 2011, Kostynoy S.A., E-mail: seppius2@gmail.com
#     Writer (c) 2012, Nevenkin A.V., E-mail: nuimons@gmail.com
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
import trans
import sys
import os
import xbmcplugin
import xbmcgui
import xbmc
import xbmcaddon
import time
import random
import threading

from urllib import unquote, quote, quote_plus
try:
    from hashlib import md5
except:
    from md5 import md5

GAUID='UA-31027962-2'
from pyga.requests import Tracker, Page, Session, Visitor, Event, Config

CONFIG = Config()
CONFIG.anonimize_ip_address = True

tracker = Tracker(GAUID, 'xbmc.ru', conf=CONFIG)

import pickle
def get_platform():
    platforms = {
        "Linux": "X11; Linux",
        "Windows": "Windows NT %d.%d",
        "OSX": "Macintosh; Intel Mac OS X",
        "IOS": "iPad; CPU OS 6_1 like Mac OS X",
    }
    for platform, ua_platform_name in platforms.items():
        if xbmc.getCondVisibility("System.Platform.%s" % platform):
            if platform == "Windows":
                import sys
                version = sys.getwindowsversion()
                ua_platform_name %= (version[0], version[1])
            return ua_platform_name


def get_user_agent():
    return "XBMC/%s (%s)" % (
        xbmc.getInfoLabel("System.BuildVersion").split(" ")[0],
        get_platform()
    )

    
adv_file = xbmc.translatePath('special://temp/'+ 'settings.ivi.adv')

Addon = xbmcaddon.Addon(id='plugin.video.ivi.ru')
language = Addon.getLocalizedString
addon_icon    = Addon.getAddonInfo('icon')
addon_fanart  = Addon.getAddonInfo('fanart')
addon_path    = Addon.getAddonInfo('path')
addon_type    = Addon.getAddonInfo('type')
addon_id      = Addon.getAddonInfo('id')
addon_author  = Addon.getAddonInfo('author')
addon_name    = Addon.getAddonInfo('name')
addon_version = Addon.getAddonInfo('version')

hos = int(sys.argv[1])
fhos = sys.argv[0]
try:
    import platform
    xbmcver=xbmc.getInfoLabel( "System.BuildVersion" ).replace(' ','_').replace(':','_')
    UA = 'XBMC/%s (%s; U; %s %s %s %s) %s/%s XBMC/%s'% (xbmcver,platform.system(),platform.system(),platform.release(), platform.version(), platform.machine(),addon_id,addon_version,xbmcver)
except:
    UA = 'XBMC/Unknown %s/%s/%s' % (urllib.quote_plus(addon_author), addon_version, urllib.quote_plus(addon_name))

def get_len():
    try:
        if Addon.getSetting("cnt_v") == '0': return 10
        if Addon.getSetting("cnt_v") == '1': return 25
        if Addon.getSetting("cnt_v") == '2': return 50
        if Addon.getSetting("cnt_v") == '3': return 75
        if Addon.getSetting("cnt_v") == '4': return 100
        return 50
    except: return 50
show_len=get_len()
try:
    if Addon.getSetting("adult") == 'false': 
        adult=False
    else: adult=True
except: adult=False



VERSION = '4.3as'
DOMAIN = '131896016'
GATrack='UA-30985824-1'

if not Addon.getSetting('GAcookie'):
    from random import randint
    GAcookie ="__utma%3D"+DOMAIN+"."+str(random.randint(0, 0x7fffffff))+"."+str(random.randint(0, 0x7fffffff))+"."+str(int(time.time()))+"."+str(int(time.time()))+".1%3B"
    Addon.setSetting('GAcookie', GAcookie)
if not Addon.getSetting('uniq_id'):
    from random import randint
    uniq_id=random.random()*time.time()
    Addon.setSetting('uniq_id', str(uniq_id))

GAcookie =Addon.getSetting('GAcookie')
uniq_id=Addon.getSetting('uniq_id')

ses_file = xbmc.translatePath('special://temp/'+ 'session.ag')
vis_file = xbmc.translatePath('special://temp/'+ 'visitor.ag')
try:
    with open(vis_file, 'rb') as f:
        visitor = pickle.load(f)

except: 
    visitor = Visitor()
    visitor.user_agent=get_user_agent()
    visitor.locale = xbmc.getLanguage()
    info = lambda x: xbmc.getInfoLabel("System.%s" % x)
    visitor.screen_resolution = "%sx%s" % (info("ScreenWidth"), info("ScreenHeight"))
    visitor.unique_id=random.randint(0, 0x7fffffff)

    with open(vis_file, 'wb') as f:
        pickle.dump(visitor, f)
       
try:
    with open(ses_file, 'rb') as f:
        session = pickle.load(f)

except: 
    session = Session()
    with open(ses_file, 'wb') as f:
        pickle.dump(session, f)



genres_data = []
genres_dat_file = os.path.join(addon_path, 'genres.dat')

if os.path.isfile(genres_dat_file):
    try:
        gdf = open(genres_dat_file, 'r')
        genres_data = json.loads(gdf.read())
        gdf.close()
    except: pass
    
import Cookie, cookielib	
cook_file = xbmc.translatePath('special://temp/'+ 'ivi_ga.cookies')

def send_request_to_google_analytics(utm_url, ua):
    #print utm_url
    response=None
    #try:

        #req = urllib2.Request(utm_url, None, {'User-Agent':UA} )
    #response = urllib2.urlopen(req).read()
    cookiejar = cookielib.MozillaCookieJar()
    urlOpener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
    #req = urllib2.Request(url = utm_url, data = None, headers = {'User-Agent':UA} )
    #resp = urllib2.urlopen(req)
    request = urllib2.Request(utm_url, None, {'User-Agent':ua} )
    url = urlOpener.open(request)
    http=url.read()
    #print http
    response=http
    #for cook in cookiejar:
    #    print "%s=%s"%(cook.name,cook.value)
    cookiejar.save(cook_file)
    #except:
    #	ShowMessage('ivi.ru', "GA fail: %s" % utm_url, 2000)
    return response

def track_page_view(path,nevent='', tevent='',UATRACK='UA-11561457-31'):
    try:
        track_page_view_2(path,nevent,tevent,UATRACK)
    except:
        pass
    
def track_page_view_2(path,nevent='', tevent='',UATRACK='UA-11561457-31'):
    domain = DOMAIN
    document_path = unquote(path)
    utm_gif_location = "http://www.google-analytics.com/__utm.gif"
    extra = {}
    extra['screen'] = xbmc.getInfoLabel('System.ScreenMode')

    md5String = md5(str(uniq_id)).hexdigest()
    gvid="0x" + md5String[:16]
    
    utm_url = utm_gif_location + "?" + \
        "utmwv=" + VERSION + \
        "&utmn=" + get_random_number() + \
        "&utmsr=" + quote(extra.get("screen", "")) + \
        "&utmt=" + nevent + \
        "&utme=" + tevent +\
        "&utmhn=localhost" + \
        "&utmr=" + quote('-') + \
        "&utmp=" + quote(document_path) + \
        "&utmac=" + UATRACK + \
        "&utmvid=" + gvid + \
        "&utmcc="+ GAcookie
    return send_request_to_google_analytics(utm_url, UA)


import json

def get_random_number():
    return str(random.randint(0, 0x7fffffff))

def construct_request(params):
    return '%s?%s' % (fhos, urllib.urlencode(params))

def ShowMessage(heading, message, times = 3000, pics = addon_icon):
    try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading.encode('utf-8'), message.encode('utf-8'), times, pics.encode('utf-8')))
    except Exception, e:
        print( '[%s]: ShowMessage: Transcoding UTF-8 failed [%s]' % (addon_id, e), 2 )
        try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, pics))
        except Exception, e:
            print( '[%s]: ShowMessage: exec failed [%s]' % (addon_id, e), 3 )

def GET(target, post=None):
    try:
        req = urllib2.Request(url = target, data = post, headers = {'User-Agent':UA})
        resp = urllib2.urlopen(req)
        CE = resp.headers.get('content-encoding')
        http = resp.read()
        resp.close()
        return http
    except Exception, e:
        print( '[%s]: GET EXCEPT [%s]' % (addon_id, e), 4 )
        ShowMessage('HTTP ERROR', e, 5000)

def genre2name(gid):
    gdf = open(genres_dat_file, 'r')
    genres_data = json.loads(gdf.read())
    gdf.close()
    try:
        for n in genres_data:
            if int(n.split(';')[0]) == (gid):
                reti=n.split(';')[1]
        return reti
    except: return None

def adv_send(path,post):
    try:
        req = urllib2.Request(path,post)
        req.add_header('Accept', 'text/plain')
        req.add_header('Content-Type','application/x-www-form-urlencoded')
        f = urllib2.urlopen(req)
        js = f.read()
    except: pass
    
class dig_player(xbmc.Player):

    def __init__( self, *args, **kwargs ):
        self.init()

    def init(self):
        self.mustEND=0
        self.active = None
        self.api_url = 'http://api.digitalaccess.ru/api/json/'
        self.log_url = 'http://api.digitalaccess.ru'
        self.sID='s15'
        self.vID=7029
        self.content=None
        self.ads_file=None
        self.state='pre_roll'
        self.watchid=None
        self.ads=[]
        self.midroll = []
        self.PosterImage = None
        self.main_item = None
        self.title=None
        self.lastad=0
        self.paused=None
        self.adv_file=None
        self.resume_timer=None
        self.content_start=None
        self.pre_end=None
        self.adstart_timer=None
        self.advid=None
        self.min=0
        self.ended=None
        self.send_ads=[]
        self.start_timer=None
        self.show=True
        self.playing=False
        self.strt_file=None

    def report_ads(self, curr_ads):

        json1 = self.POSTAPI({'method':'da.adv.watched', 'params':[self.vID, curr_ads['id'], {'contentid':self.vID,'site':self.sID, 'watchid':str(self.watchid),'advid':curr_ads['id'],'uid':uniq_id, "advwatchid":str(self.advwatchid)} ]})
        links= curr_ads['px_audit']
        f = open(adv_file, 'w')
        last_ad=str(int(time.time()))
        f.write(last_ad)
        f.close()
        self.lastad=last_ad
        if links:
            if len(links)<8:
                for n in links:
                    GET(n)
            else: GET(links)


    def POSTAPI(self, post):

        try:
            req = urllib2.Request(self.api_url)
            req.add_header('User-Agent', UA)
            f = urllib2.urlopen(req, json.dumps(post))
            js = json.loads(f.read())
            f.close()
            return js
        except: return None
        try:
            e_m = js['error']
            ShowMessage('ERROR %s SERVER %s' % (e_m['code'], js['server_name']), e_m['message'], times = 15000, pics = addon_icon)
            return None
        except:
            return js

    def getData    (self, vID):

        self.vID=vID
        self.watchid='%s_%s_%s'%(self.vID,uniq_id,str(int(time.time()*1000)))
        json0 = self.POSTAPI({'method':'da.content.get', 'params':[self.vID, {'contentid':self.vID,'watchid':self.watchid,'site':self.sID, 'uid':uniq_id} ]})
        try:
            vc = json0['result']
            self.content = self.find_best(vc)
        except: vc=None

        if self.content and vc:

            http = GET('http://www.ivi.ru/mobileapi/videoinfo/?subsite=15&id=%s' % self.vID)
            if http:
                data = get_video_data(json.loads(http))
                self.PosterImage = data['image']
                self.main_item = xbmcgui.ListItem(data['title'], iconImage = self.PosterImage, thumbnailImage = self.PosterImage)
                self.title=data['title']
                i = xbmcgui.ListItem(self.title, iconImage = self.PosterImage, thumbnailImage = self.PosterImage)
                iad = xbmcgui.ListItem(language(30011), iconImage = self.PosterImage, thumbnailImage = self.PosterImage)
            try:    self.content_percent_to_mark = int(vc['percent_to_mark'])
            except: self.content_percent_to_mark = 0
            try:    self.GA_id = int(vc['google_analytics_id'])
            except: self.GA_id = None
            try:    self.tns_id = int(vc['tns_id'])
            except: self.tns_id = None
            self.title=vc['title']
            try:    self.credits_begin_time = int(vc['credits_begin_time'])
            except: self.credits_begin_time = -1
            if self.credits_begin_time==0: self.credits_begin_time=-1
            try:    self.midroll = vc['midroll']
            except: self.midroll = []
            flname=self.content
            fio=i
            ind=0
            pre=self.getAds('preroll')
            #print pre
            if pre:
                self.adv_file=pre['url']
                self.advid=pre['id']
                self.state='preroll'
                self.send_ads=pre
                flname=self.adv_file
                fio=iad
            else: self.state='play'

            for na in self.midroll:
                try:
                    self.ads.append({
                        'type':'midroll',
                        'ind':ind,
                        'time':na})
                    ind=ind+1
                except: pass
            self.ads.append({
                    'type':'postroll',
                    'ind':ind,
                    'time':self.credits_begin_time
                })
            track_page_view('','event','5(Video*Videostart)')
            track_page_view('','event','5(Video*Videostart)',UATRACK=GATrack)
            tracker.track_event(Event('Video','Start',vID), session, visitor)
            self.active=True
            json1 = self.POSTAPI({'params':[self.vID, {'contentid':self.vID,'site':self.sID, 'watchid':self.watchid ,'uid':uniq_id} ],'method':'da.content.watched' })
            self.playing=False
            self.strt_file=flname

    def play_loop(self):

        self.last_ads_time=0
        added=None
        self.active=True
        self.min=0
        last=0
        self.Time = 0
        self.TotalTime = 9999
        self.percent = 0
        timeout=90
        while self.active==True:
            if self.playing:

                try:
                    self.Time = int(self.getTime())
                    self.TotalTime = self.getTotalTime()
                    self.percent = (100 * self.Time) / self.TotalTime
                except:
                    self.TotalTime = 999999
                    self.Time = 0
                    self.percent = 0
                if not self.paused and last!=self.Time:
                    last=self.Time
                    if self.state=='play' and self.content_start:
                        seconds=int(time.time()-self.content_start)
                        if seconds<=60:
                            if self.state=='play' and self.content_start:
                                self.sendstat('http://api.digitalaccess.ru/logger/content/time/',{'contentid':self.vID,'watchid':self.watchid,'fromstart':int(self.Time),'seconds':seconds})
                        if seconds>=60: self.min=self.min+1
                        if self.min>=60:
                            if self.state=='play' and self.content_start:
                                self.sendstat('http://api.digitalaccess.ru/logger/content/time/',{'contentid':self.vID,'watchid':self.watchid,'fromstart':int(self.Time),'seconds':seconds})
                                self.min=0
                    if self.state!='play' and self.adstart_timer:
                        self.sendstat('http://api.digitalaccess.ru/logger/adv/time/',{'watchid':quote(self.watchid),'advwatchid':quote(self.advwatchid),'seconds':int(time.time()-self.adstart_timer)})
                    if self.state!='play' and not self.ended:

                        if self.Time>=int(self.TotalTime-1.3) and self.Time>5 and not added:
                            if self.state=='preroll':
                                self.pre_end=time.time()
                            i = xbmcgui.ListItem(self.title, iconImage = self.PosterImage, thumbnailImage = self.PosterImage)
                            i.setProperty('StartOffset', str(self.resume_timer))
                            added=True
                            self.state='play'
                            self.playing=False
                            self.play(self.content,i)

                    else:

                        for m in self.ads:

                            if int(self.Time)==int(m['time']) and int(self.Time)!=self.last_ads_time:
                                self.resume_timer=int(m['time'])
                                try: self.ads.remove(m)
                                except: pass
                                self.last_ads_time=int(self.Time)
                                pre=self.getAds(m['type'])
                                if pre:
                                    self.state=m['type']
                                    iad = xbmcgui.ListItem(language(30011), iconImage = self.PosterImage, thumbnailImage = self.PosterImage)
                                    self.advid=pre['id']
                                    self.adv_file=pre['url']
                                    self.send_ads=pre

                                    added=None
                                    self.playing=False
                                    self.play(self.adv_file,iad)
                                else:
                                    pass

                        if self.state=='play' and self.credits_begin_time==-1 and self.Time>=int(self.TotalTime-1.3) and not self.ended:
                            pre=self.getAds('postroll')
                            if pre:
                                self.state='postroll'
                                iad = xbmcgui.ListItem(language(30011), iconImage = self.PosterImage, thumbnailImage = self.PosterImage)
                                self.advid=pre['id']
                                self.adv_file=pre['url']
                                self.send_ads=pre
                                added=None
                                self.ended=True
                                self.playing=False
                                self.play(pre['url'],iad)
            if not self.isPlaying():
                timeout=timeout-1
                if timeout==0: self.active=False
            else: timeout=90
            if self.mustEND==1:
                self.active=False
                break
            if self.TotalTime-self.Time>5:
                self.sleep(300)
            else: self.sleep(100)

    def onPlayBackEnded( self ):

        self.show=False
        self.active=False
        self.mustEND=1
        track_page_view('','event','5(Video*VideoEnded)',UATRACK=GATrack)
        tracker.track_event(Event('Video','Ended'), session, visitor)
    def onPlayBackStopped(self):

        self.active=False
        self.show=False
        self.mustEND=1
        track_page_view('','event','5(Video*VideoStopped)',UATRACK=GATrack)
        tracker.track_event(Event('Video','Stopped'), session, visitor)
    def onPlayBackPaused( self ):
        self.paused=1
        
    def onPlayBackResumed( self ):
        self.paused=False

    def onPlayBackStarted( self ):
        self.playing=True
        if self.state=='play':
            if not self.content_start:

                self.content_start=time.time()
                self.sendstat('http://api.digitalaccess.ru/logger/mediainfo/speed/',{'watchid':self.watchid,'speed':self.content_start-self.pre_end})
        else:

            try:

                self.adstart_timer=time.time()
                self.advwatchid='%s_%s'%(self.advid,str(int(self.adstart_timer*1000)))
                json1 = self.POSTAPI({'method':'da.adv.got', 'params':[self.vID, self.advid, {'contentid':self.vID,'site':self.sID, 'watchid':str(self.watchid),'advid':self.advid,'uid':uniq_id, "advwatchid":str(self.advwatchid)} ]})
                self.report_ads(self.send_ads)
            except: pass
    def getAds(self, phase):
        json1 = self.POSTAPI({'method':'da.adv.get', 'params':[self.vID, {'contentid':self.vID,'site':self.sID, 'watchid':self.watchid, 'last_adv':(int(int(time.time())-int(self.lastad))), 'uid':uniq_id},phase]} )
        #print json1
        if json1:
            try:
                ad=json1['result'][0]
                #print ad
                ad_file = self.find_best(ad)
                if ad_file:
                    adrow = {'url': ad_file, 'id': ad['id'], 'title': ad['title'].encode('utf-8'), 'px_audit': ad['px_audit'],
                    'duration': ad['duration'], 'percent_to_mark': int(ad['percent_to_mark'])-1, 'save_show': ad['save_show']}
            except:
                adrow = None
                pass
        return adrow

    def sendstat(self,path,post):
        post=urllib.urlencode(post).replace('.','%2E').replace('_','%5F')
        t = threading.Thread(target=adv_send, args=(path,post))
        t.daemon = True
        t.start()
        
    def find_best(self, data):
        #print data
        play_file = None
        if not play_file:
            for vcfl in data['files']:
                if vcfl['content_format'] == 'MP4-hi': play_file = vcfl['url']
        if not play_file:
            for vcfl in data['files']:
                if vcfl['content_format'] == 'FLV-hi': play_file = vcfl['url']
        if not play_file:
            for vcfl in data['files']:
                if vcfl['content_format'] == 'MP4-lo': play_file = vcfl['url']
        if not play_file:
            for vcfl in data['files']:
                if vcfl['content_format'] == 'FLV-lo': play_file = vcfl['url']
        #print play_file
        return play_file

    def sleep(self, s):
        xbmc.sleep(s)
    def __del__(self):
        self.active=False

def show_info():
    xbmc.executebuiltin('ActivateWindow(movieinformation)')


def playid(params, play=False):


    try:
        f = open(adv_file, 'r')
        last_ad=f.readline()

    except:
        f = open(adv_file, 'w')
        last_ad=str(int(time.time()))
        f.write(last_ad)
        f.close()
    aplay=dig_player()
    aplay.init()
    aplay.lastad=last_ad
    aplay.pre_end=time.time()
    aplay.getData(params['id'])
    print "aplay:%s"%aplay.strt_file
    if aplay.strt_file!=None:
        print "Play file:%s"%aplay.strt_file
        print 'plfile'
        item = xbmcgui.ListItem(path=aplay.strt_file)
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
        aplay.play_loop()
        aplay.stop
        aplay.active=False
    else:
        ShowMessage('ivi.ru', 'Forbidden', 2000)
        track_page_view(str(params['id']),'event','5(Video*VideoForbidden)',UATRACK=GATrack)
        tracker.track_event(Event('Video','Forbidden',str(params['id'])), session, visitor)
        aplay.stop



def main_screen(params):

    li = xbmcgui.ListItem(language(30014), iconImage = addon_icon, thumbnailImage = addon_icon)
    uri = construct_request({
        'func': 'promo',
        'url': 'http://www.ivi.ru/mobileapi/promo/v2/?subsite=15&%s'
    })
    li.setProperty('fanart_image', addon_fanart)
    xbmcplugin.addDirectoryItem(hos, uri, li, True)

    http = GET('http://www.ivi.ru/mobileapi/categories/')
    jsdata = json.loads(http)
    for categoryes in jsdata:
        li = xbmcgui.ListItem(categoryes['title'], iconImage = addon_icon, thumbnailImage = addon_icon)
        li.setProperty('fanart_image', addon_fanart)
        uri = construct_request({
            'func': 'read_category',
            'category': categoryes['id']
        })
        xbmcplugin.addDirectoryItem(hos, uri, li, True)
        for genre in categoryes['genres']:
            genres_data.append(str(genre['id'])+';'+genre['title'])
    gf = open(genres_dat_file, 'w')
    gf.write(json.dumps(genres_data))
    gf.close()

    li = xbmcgui.ListItem(language(30015), iconImage = addon_icon, thumbnailImage = addon_icon)
    li.setProperty('fanart_image', addon_fanart)
    uri = construct_request({
        'func': 'run_search'
    })
    xbmcplugin.addDirectoryItem(hos, uri, li, True)

    li = xbmcgui.ListItem(language(30030), iconImage = addon_icon, thumbnailImage = addon_icon)
    li.setProperty('fanart_image', addon_fanart)
    uri = construct_request({
        'func': 'run_settings'
    })
    xbmcplugin.addDirectoryItem(hos, uri, li, False)

    xbmcplugin.endOfDirectory(hos)

def run_settings(params):
    Addon.openSettings()

def read_category(params):
    show_len=get_len()
    categ=params['category']
    if categ=='14':
        track_page_view('movies')
        track_page_view('movies',UATRACK=GATrack)
        tracker.track_pageview(Page('/movies'), session, visitor)

    if categ=='15':
        track_page_view('series')
        track_page_view('series',UATRACK=GATrack)
        tracker.track_pageview(Page('/series'), session, visitor)
    if categ=='16':
        track_page_view('shows')
        track_page_view('shows',UATRACK=GATrack)
        tracker.track_pageview(Page('/shows'), session, visitor)
    if categ=='17':
        track_page_view('animation')
        track_page_view('animation',UATRACK=GATrack)
        tracker.track_pageview(Page('/animation'), session, visitor)
    if categ=='20':
        track_page_view('child')
        track_page_view('child',UATRACK=GATrack)
        tracker.track_pageview(Page('/child'), session, visitor)
    http = GET('http://www.ivi.ru/mobileapi/categories/')
    jsdata = json.loads(http)
    for categoryes in jsdata:
        if categoryes['id']==int(params['category']):
            li = xbmcgui.ListItem(language(30016), iconImage = addon_icon, thumbnailImage = addon_icon)
            li.setProperty('fanart_image', addon_fanart)
            uri = construct_request({
                'func': 'run_search',
                'category': categoryes['id']
            })
            xbmcplugin.addDirectoryItem(hos, uri, li, True)
            li = xbmcgui.ListItem(language(30017), iconImage = addon_icon, thumbnailImage = addon_icon)
            li.setProperty('fanart_image', addon_fanart)
            uri = construct_request({
                'func': 'read_dir',
                'category': categoryes['id'],
                'sort':'new',
                'from':0,
                'to':show_len-1

            })
            xbmcplugin.addDirectoryItem(hos, uri, li, True)
            li = xbmcgui.ListItem(language(30018), iconImage = addon_icon, thumbnailImage = addon_icon)
            li.setProperty('fanart_image', addon_fanart)
            uri = construct_request({
                'func': 'read_dir',
                'category': categoryes['id'],
                'sort':'pop',
                'from':0,
                'to':show_len-1
            })
            xbmcplugin.addDirectoryItem(hos, uri, li, True)
            for genre in categoryes['genres']:
                li = xbmcgui.ListItem(genre['title'], iconImage = addon_icon, thumbnailImage = addon_icon)
                li.setProperty('fanart_image', addon_fanart)
                uri = construct_request({
                    'func': 'read_dir',
                    'genre': genre['id'],
                    'sorted':1,
                    'from':0,
                    'to':show_len-1
                })
                if genre['id']<>169 or adult: xbmcplugin.addDirectoryItem(hos, uri, li, True)

    xbmcplugin.endOfDirectory(hos)

def read_dir(params):
    try:
        target = params['url']
        del params['url']
    except: target = 'http://www.ivi.ru/mobileapi/catalogue/v2/?subsite=15&%s'
    try:
        list = params['list']
        del params['list']
    except: list=None
    try:
        if params['sorted']:
            params['sort'] = get_sort()
            params['sorted'] =None
    except: pass
    try:
        if not params['sort']: params['sort'] = get_sort()
    except: params['sort'] = get_sort()
    http = GET(target % urllib.urlencode(params))
    if http == None:
        ShowMessage('Error', 'Cant received data', 2000)
        return False

    jsdata = json.loads(http)
    cnt=0
    v_list=''
    if list:
        for video_ind in jsdata:
            vdata=get_video_data(video_ind)
            if int(vdata['seasons_cnt'])==-1:
                v_list=v_list+str(vdata['id'])+';'
    for video_ind in jsdata:
        vdata=get_video_data(video_ind)

        vid=vdata['id']
        li = xbmcgui.ListItem(vdata['title'], iconImage = vdata['image'], thumbnailImage = vdata['image'])
        li.setProperty('fanart_image', addon_fanart)
        try: li.setInfo(type='video', infoLabels = vdata['info'])
        except: pass
        ur = {
            'func': 'read_dir',
            'id':vdata['id'],
            'url': 'http://www.ivi.ru/mobileapi/videofromcompilation/?subsite=15&%s',
            'sorted':1,
            'from':0,
            'list':'list',
            'to':show_len-1
        }
        if int(vdata['seasons_cnt'])>0: ur['func']='getser'
        if int(vdata['seasons_cnt'])==-1:
            ur['func']='playid'
            ur['playlist']=v_list
            u=sys.argv[0]+"?func=playid&playlist="+v_list+"&id="+str(vdata['id'])
        uri=construct_request(ur)
        cnt=cnt+1
        li.setProperty('fanart_image', addon_fanart)
        li.setProperty('IsPlayable', 'true')
        if vdata['adult']==0 or adult:
            if int(vdata['seasons_cnt'])==-1: xbmcplugin.addDirectoryItem(hos, url=u, listitem=li)
            else: xbmcplugin.addDirectoryItem(hos, uri, li, True)


    if cnt >= int(show_len):
        li = xbmcgui.ListItem(language(30019), iconImage = addon_icon, thumbnailImage = addon_icon)
        li.setProperty('fanart_image', addon_fanart)
        params['url']=target
        params['func'] = 'read_dir'
        params['from'] = int(params['from'])+int(show_len)
        params['to'] = int(params['from']) + int(show_len)
        uri = '%s?%s' % (sys.argv[0], urllib.urlencode(params))
        xbmcplugin.addDirectoryItem(hos, uri, li, True)
    xbmcplugin.endOfDirectory(hos)

def getser(params):
    params['to']=999
    target='http://www.ivi.ru/mobileapi/videofromcompilation/?subsite=15&%s'
    http = GET(target % urllib.urlencode(params))
    total=json.loads(http)
    v_id = int(params['id'])
    seasons=[]
    for episode in total:
        if episode['season'] not in seasons:
            seasons.append(episode['season'])
    seasons.sort()
    for ind in seasons:
        i = xbmcgui.ListItem(language(30020) % ind, iconImage = addon_icon, thumbnailImage = addon_icon)
        i.setProperty('fanart_image', addon_fanart)
        osp = {'func':'read_dir', 'id': v_id, 'url': 'http://www.ivi.ru/mobileapi/videofromcompilation/?subsite=15&%s', 'season':ind,'from':0,'to':show_len-1,'list':'list'}
        uri = '%s?%s' % (sys.argv[0], urllib.urlencode(osp))
        i.setInfo(type = 'video', infoLabels = {'season': ind})
        xbmcplugin.addDirectoryItem(hos, uri, i, True)
    xbmcplugin.endOfDirectory(hos)


def get_video_data(video):
    mysetInfo={}
    try: title=video['title']
    except: title=None
    try: duration=video['duration']
    except: duration=None
    try: id=video['id']
    except: id=None
    try: seasons_cnt = video['seasons_count']
    except: seasons_cnt = -1
    try:
        images=video['thumbnails']
    except: images=None
    try:
        images2=video['thumb_originals']
    except: images2=None

    try: season=video['season']
    except: season=None
    try: episode=video['episode']
    except: episode=None
    try: genre=video['genres']
    except: genre=None
    try: cast=video['artists']
    except: cast=None
    try:
        mysetInfo['plot'] = video['descrtiption']
        mysetInfo['plotoutline'] = video['descrtiption']
    except: pass
    try:
        mysetInfo['year'] = int(video['year'])
    except: pass
    try:
        mysetInfo['year'] = int(video['years'][0])
    except: pass
    try:
        v_ivi_rating = video['ivi_rating']
        mysetInfo['rating'] = float(v_ivi_rating*2)
    except: v_ivi_rating = None
    if not v_ivi_rating:
        try:
            v_ivi_rating = video['ivi_rating_10']
            mysetInfo['rating'] = float(v_ivi_rating)
        except: v_ivi_rating = None
    try:
        mysetInfo['duration'] = duration
    except: pass
    lth = -1
    ltw = 0
    ltu = addon_icon


    try:
        ltu=images[0]['path']
        ltu=ltu.split('.jpg')[0]+'.jpg'
        if images[0]['type']=='B2BImageFile' and images2:
            ltu=images2[0]['path']
    except:
        try: ltu=images2[0]['path']
        except: pass
    genres=None
    glist = []
    m_adult=0
    if genre:
        for gid in genre:
            if gid==169: m_adult=1
            g_name = genre2name(gid)

            if g_name:
                try: glist.index(g_name)
                except: glist.append(g_name)
        if len(glist):
            mysetInfo['genre'] = ', '.join(glist)
    if cast:
        mysetInfo['cast'] = cast
    export={'adult':m_adult, 'id':id,'title':title, 'duration':duration, 'seasons_cnt':seasons_cnt, 'image':ltu, 'info':mysetInfo}
    return export

def promo(params):                     # показ промо контента


    track_page_view('promo')
    track_page_view('promo',UATRACK=GATrack)
    tracker.track_pageview(Page('/promo'), session, visitor)
    http = GET('http://www.ivi.ru/mobileapi/promo/')
    if http == None: return False
    jsdata = json.loads(http)
    if jsdata:
        for video in jsdata:
            http=GET('http://www.ivi.ru/mobileapi/videoinfo/?id=%s'%video['content_id'])
            vdata = get_video_data(json.loads(http))
            li = xbmcgui.ListItem(vdata['title'], iconImage = vdata['image'], thumbnailImage = vdata['image'])
            li.setProperty('fanart_image', addon_fanart)

            try: li.setInfo(type='video', infoLabels = vdata['info'])
            except: pass
            uri = '%s?%s' % (sys.argv[0], urllib.urlencode({'func':'playid', 'id': video['content_id']}))
            u=sys.argv[0]+"?func=playid&id="+str(video['content_id'])
            li.setProperty('IsPlayable', 'true')
            li.setProperty('fanart_image', addon_fanart)
            li.setInfo('video',{'plot': video['text']})
            xbmcplugin.addDirectoryItem(hos, url=u, listitem= li)
        xbmcplugin.endOfDirectory(hos)

def run_search(params):                # Поиск
    track_page_view('search')
    track_page_view('search',UATRACK=GATrack)
    tracker.track_pageview(Page('/search'), session, visitor)
    kbd = xbmc.Keyboard()
    kbd.setDefault('')
    kbd.setHeading(language(30021))
    kbd.doModal()
    out=''
    if kbd.isConfirmed():
        try:
            out = trans.detranslify(kbd.getText())
            out=out.encode("utf-8")
        except:
            out = kbd.getText()

    params['from'] = 0
    params['to']= int(show_len)
    params['query'] = out
    params['url'] = 'http://www.ivi.ru/mobileapi/search/v2/?subsite=15&%s'
    
    read_dir(params)

def get_sort():

    if Addon.getSetting("sort_v") == '1': return 'pop'
    else: return 'new'

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
        print( '[%s]: Primary input' % addon_id, 1 )
        main_screen(params)
    if func != None:
        try: pfunc = globals()[func]
        except:
            pfunc = None
            print( '[%s]: Function "%s" not found' % (addon_id, func), 4 )
            ShowMessage('Internal addon error', 'Function "%s" not found' % func, 2000)
        if pfunc: pfunc(params)

with open(ses_file, 'wb') as f:
    pickle.dump(session, f)

with open(vis_file, 'wb') as f:
    pickle.dump(visitor, f)
