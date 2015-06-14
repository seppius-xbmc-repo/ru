#!/usr/bin/python
# -*- coding: utf-8 -*-

import string, xbmc, xbmcgui, xbmcplugin, xbmcaddon, os, sys, urllib, urllib2, cookielib, time, codecs, datetime, re
import socket
import sqlite3 as db
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
import calendar

socket.setdefaulttimeout(35000)

PLUGIN_NAME   = 'YaTv'
siteUrl = 'm.tv.yandex.ru'
httpSiteUrl = 'http://' + siteUrl
sid_file = os.path.join(xbmc.translatePath('special://temp/'), 'script.module.YaTv.cookies.sid')

addon = xbmcaddon.Addon(id='script.module.YaTv')
handle = addon.getAddonInfo('id')
__settings__ = xbmcaddon.Addon(id='script.module.YaTv')
thumb = os.path.join( addon.getAddonInfo('path'), "icon.png" )
fanart = os.path.join( addon.getAddonInfo('path'), "fanart.jpg" )
icon = os.path.join( addon.getAddonInfo('path'), 'icon.png')
db_name = os.path.join( addon.getAddonInfo('path'), "move_info.db" )
c = db.connect(database=db_name, check_same_thread=False)
cu = c.cursor()

def ru(x):return unicode(x,'utf8', 'ignore')
def xt(x):return xbmc.translatePath(x)

def showMessage(heading, message, times = 3000):
	xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")'%(heading, message, times, icon))


def GET(target, referer, post=None,cookie=None):
	try:
		req = urllib2.Request(url = target, data = post)
		req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
		try:req.add_header('Cookie', cookie)
		except Exception, e:
			pass
		resp = urllib2.urlopen(req, timeout=50000)
		http1 = resp.read()
		try:http=http1.replace('<br />',' ').replace('<br>',' ').replace('&nbsp;','')
		except Exception, e:
			pass
		return http
	except Exception, e:
		print 'HTTP ERROR '+ target
		
def GetCookie(target, post=None):
    try:
        req = urllib2.Request(url = target, data = post)
        req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
        resp = urllib2.urlopen(req)
        #print resp.read()
        cookie = resp.headers['Set-Cookie'].split(";")[0]
        return cookie
    except Exception, e:
        print e
        
tzd = {"0":"2", "-1":"3", "-2":"1", "-3":"6", "-4":"9", "-5":"10", "-6":"12", "-7":"16", "-8":"17", "-9":"18", "-10":"19", "-11":"20", "-12":"21"}

def GetCh():
    zone = str(time.timezone / 3600)
    try:
        tz = tzd[zone]
        tdelta = 0
        #print "YATV timezone="+str(time.timezone)
        #print "YATV tz="+str(tz)
    except:
        tz = "9"
        tdelta = (4*3600 + time.altzone)
        #print "YATV Except: timezone="+str(time.timezone)
        #print "YATV Except: tz="+str(tz)
    channels = ["997","998","994","996","993","734","758","328","853","314","21","916","1016","688","328","1013","140","1016","949","950","951","947","899","934","991","767","557","558","539","906","752","863","1003","900","1000","1005","970","550","548","571","926","543","547","546","509","405","564","862","730","909","542","645","924","556","863","538","625","74","809","240","901","549","965","529","967","702","942","943","751","98","917","788","339","598","392","670","904","763","887","842","536","796","910","797","911","889","845","572","402","695","748","777","145","727","761","513","790","759","481","448","773","139","348","843","696","666","663","143","664","754","455","296","382","272","457","532","111","726","737","557","504","505","692","799","353","716"]
    data = urllib.urlencode({'timezone' : tz})
    cookie = GetCookie('http://www.vsetv.com/rewrite_url.php', data)
    for ch in channels:
        dt=datetime.datetime.strftime(datetime.datetime.now() ,"%Y-%m-%d")
        s_time = ""
        f_time = ""
        title_pr = ""
        timezone = urllib.urlencode({
            'timezone' : tz,
            'submit.x' : '13',
            'submit.y' : '9',
            'selected_channel' : 'channel_'+ch+'',
            'selected_date' : 'day_'+dt+''
        })
        Url = 'http://www.vsetv.com/rewrite_url.php'
        http = GET(Url, Url, timezone, cookie)
        beautifulSoup = BeautifulSoup(http)
        el = beautifulSoup.findAll('div', attrs={'id': 'schedule_container'})
        d=[]
        prog=[]
        i=0
        if tdelta == 0:
            for gr in el:
                for g in gr:
                    if not g['class'].find('pasttime')>-1 and not g['class'].find('pastprname2')>-1 and not g['class'].find('pastdesc')>-1:
                        if g['class'].find('time')>-1 or g['class'].find('onair')>-1:
                            i+=1
                            if i==1: k=g.string.encode('utf-8')
                            f_time = g.string.encode('utf-8')
                            try:
                                if not s_time == "" and not title_pr == "":
                                    if datetime.datetime(*(time.strptime(s_time, "%H:%M")[0:6])).timetuple().tm_hour < datetime.datetime(*(time.strptime(k, "%H:%M")[0:6])).timetuple().tm_hour:
                                        start_t_d = datetime.datetime.date(datetime.datetime.today())+ datetime.timedelta(days=1)
                                    elif datetime.datetime(*(time.strptime(s_time, "%H:%M")[0:6])).timetuple().tm_hour >= datetime.datetime(*(time.strptime(k, "%H:%M")[0:6])).timetuple().tm_hour and datetime.datetime(*(time.strptime(k, "%H:%M")[0:6])).timetuple().tm_hour<5:
                                        start_t_d = datetime.datetime.date(datetime.datetime.today())+ datetime.timedelta(days=1)
                                    else:
                                        start_t_d = datetime.datetime.date(datetime.datetime.today())
                                    start_t_t = datetime.datetime.time((datetime.datetime(*(time.strptime(s_time, "%H:%M")[0:6]))))
                                    start_t1 = datetime.datetime.combine(start_t_d, start_t_t)
                                    start_t = time.mktime(start_t1.timetuple())
                                    if datetime.datetime(*(time.strptime(f_time, "%H:%M")[0:6])).timetuple().tm_hour < datetime.datetime(*(time.strptime(k, "%H:%M")[0:6])).timetuple().tm_hour:
                                        finish_t_d = datetime.datetime.date(datetime.datetime.today())+ datetime.timedelta(days=1)
                                    elif datetime.datetime(*(time.strptime(f_time, "%H:%M")[0:6])).timetuple().tm_hour >= datetime.datetime(*(time.strptime(k, "%H:%M")[0:6])).timetuple().tm_hour and datetime.datetime(*(time.strptime(k, "%H:%M")[0:6])).timetuple().tm_hour<5:
                                        finish_t_d = datetime.datetime.date(datetime.datetime.today())+ datetime.timedelta(days=1)
                                    else:
                                        finish_t_d = datetime.datetime.date(datetime.datetime.today())
                                    finish_t_t = datetime.datetime.time((datetime.datetime(*(time.strptime(f_time, "%H:%M")[0:6]))))
                                    finish_t1 = datetime.datetime.combine(finish_t_d, finish_t_t)
                                    finish_t = time.mktime(finish_t1.timetuple())
                                    prog.append({"start":start_t, "finish":finish_t, "program":{"title":title_pr.replace("\\/","//"), "description": description.replace("\\/","//")}})
                            except Exception, e:
                                print e
                            s_time = g.string.encode('utf-8')
                        elif g['class'].find('prname2')>-1:
                            try:
                                try:
                                    try:
                                        title_pr = g.string.encode('utf-8')
                                        description = ""
                                    except:
                                        title_pr = g.contents[0].encode('utf-8')
                                        description = ""
                                except Exception, e:
                                    title_pr = g.contents[1].encode('utf-8')
                                    description = ""
                            except:
                                try:
                                    m=g.findAll('a')
                                    for p in m:
                                        title_pr = p.string.encode('utf-8')
                                        desc = p['href']
                                        Url = 'http://www.vsetv.com/'+str(desc)
                                        http = GET(Url, Url)
                                        beautifulSoup = BeautifulSoup(http)
                                        el = beautifulSoup.findAll('span', attrs={'class': 'big'})
                                        description = ""
                                        for e in el:
                                            description = description + e.string.encode('utf-8')
                                except Exception, e:
                                    description = ""
                                    print 'ERROR description: '+str(title_pr)+' '+str(ch)+'---'+str(e)
        else:
            for gr in el:
                for g in gr:
                    if not g['class'].find('pastdesc')>-1:
                        if g['class'].find('time')>-1 or g['class'].find('onair')>-1 or g['class'].find('pasttime')>-1:
                            i+=1
                            if i==1: k=g.string.encode('utf-8')
                            f_time = g.string.encode('utf-8')
                            try:
                                if not s_time == "" and not title_pr == "":
                                    #print s_time
                                    #print f_time
                                    #print title_pr
                                    if datetime.datetime(*(time.strptime(s_time, "%H:%M")[0:6])).timetuple().tm_hour < datetime.datetime(*(time.strptime(k, "%H:%M")[0:6])).timetuple().tm_hour:
                                        start_t_d = datetime.datetime.date(datetime.datetime.today())+ datetime.timedelta(days=1)
                                    elif datetime.datetime(*(time.strptime(s_time, "%H:%M")[0:6])).timetuple().tm_hour >= datetime.datetime(*(time.strptime(k, "%H:%M")[0:6])).timetuple().tm_hour and datetime.datetime(*(time.strptime(k, "%H:%M")[0:6])).timetuple().tm_hour<5:
                                        start_t_d = datetime.datetime.date(datetime.datetime.today())+ datetime.timedelta(days=1)
                                    else:
                                        start_t_d = datetime.datetime.date(datetime.datetime.today())
                                    start_t_t = datetime.datetime.time((datetime.datetime(*(time.strptime(s_time, "%H:%M")[0:6]))))
                                    start_t1 = datetime.datetime.combine(start_t_d, start_t_t)
                                    start_t = time.mktime(start_t1.timetuple())-tdelta
                                    if datetime.datetime(*(time.strptime(f_time, "%H:%M")[0:6])).timetuple().tm_hour < datetime.datetime(*(time.strptime(k, "%H:%M")[0:6])).timetuple().tm_hour:
                                        finish_t_d = datetime.datetime.date(datetime.datetime.today())+ datetime.timedelta(days=1)
                                    elif datetime.datetime(*(time.strptime(f_time, "%H:%M")[0:6])).timetuple().tm_hour >= datetime.datetime(*(time.strptime(k, "%H:%M")[0:6])).timetuple().tm_hour and datetime.datetime(*(time.strptime(k, "%H:%M")[0:6])).timetuple().tm_hour<5:
                                        finish_t_d = datetime.datetime.date(datetime.datetime.today())+ datetime.timedelta(days=1)
                                    else:
                                        finish_t_d = datetime.datetime.date(datetime.datetime.today())
                                    finish_t_t = datetime.datetime.time((datetime.datetime(*(time.strptime(f_time, "%H:%M")[0:6]))))
                                    finish_t1 = datetime.datetime.combine(finish_t_d, finish_t_t)
                                    finish_t = time.mktime(finish_t1.timetuple())-tdelta
                                    prog.append({"start":start_t, "finish":finish_t, "program":{"title":title_pr.replace("\\/","//")}})
                            except Exception, e:
                                print e
                            s_time = g.string.encode('utf-8')
                        elif g['class'].find('prname2')>-1 or g['class'].find('pastprname2')>-1:
                            try:
                                try:
                                    try:
                                        title_pr = g.string.encode('utf-8')
                                    except:
                                        title_pr = g.contents[0].encode('utf-8')
                                except Exception, e:
                                    title_pr = g.contents[1].encode('utf-8')
                            except:
                                m=g.findAll('a')
                                for p in m:
                                    title_pr = p.string.encode('utf-8')
            dt=datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=1) ,"%Y-%m-%d")
            timezone = urllib.urlencode({
            'timezone' : tz,
            'submit.x' : '13',
            'submit.y' : '9',
            'selected_channel' : 'channel_'+ch+'',
            'selected_date' : 'day_'+dt+''
            })
            Url = 'http://www.vsetv.com/rewrite_url.php'
            http = GET(Url, Url, timezone, cookie)
            beautifulSoup = BeautifulSoup(http)
            el = beautifulSoup.findAll('div', attrs={'id': 'schedule_container'})
            #d=[]
            #prog=[]
            i=0
            for gr in el:
                for g in gr:
                    if not g['class'].find('pastdesc')>-1:
                        if g['class'].find('time')>-1 or g['class'].find('onair')>-1 or g['class'].find('pasttime')>-1:
                            i+=1
                            if i==1: k=g.string.encode('utf-8')
                            f_time = g.string.encode('utf-8')
                            try:
                                if not s_time == "" and not title_pr == "":
                                    if datetime.datetime(*(time.strptime(s_time, "%H:%M")[0:6])).timetuple().tm_hour < datetime.datetime(*(time.strptime(k, "%H:%M")[0:6])).timetuple().tm_hour and i!=1:
                                        start_t_d = datetime.datetime.date(datetime.datetime.today())+ datetime.timedelta(days=2)
                                    elif datetime.datetime(*(time.strptime(s_time, "%H:%M")[0:6])).timetuple().tm_hour >= datetime.datetime(*(time.strptime(k, "%H:%M")[0:6])).timetuple().tm_hour and datetime.datetime(*(time.strptime(k, "%H:%M")[0:6])).timetuple().tm_hour<5 and i!=1:
                                        start_t_d = datetime.datetime.date(datetime.datetime.today())+ datetime.timedelta(days=2)
                                    else:
                                        start_t_d = datetime.datetime.date(datetime.datetime.today())+ datetime.timedelta(days=1)
                                    start_t_t = datetime.datetime.time((datetime.datetime(*(time.strptime(s_time, "%H:%M")[0:6]))))
                                    start_t1 = datetime.datetime.combine(start_t_d, start_t_t)
                                    start_t = time.mktime(start_t1.timetuple())-tdelta
                                    if datetime.datetime(*(time.strptime(f_time, "%H:%M")[0:6])).timetuple().tm_hour < datetime.datetime(*(time.strptime(k, "%H:%M")[0:6])).timetuple().tm_hour and i!=1:
                                        finish_t_d = datetime.datetime.date(datetime.datetime.today())+ datetime.timedelta(days=2)
                                    elif datetime.datetime(*(time.strptime(f_time, "%H:%M")[0:6])).timetuple().tm_hour >= datetime.datetime(*(time.strptime(k, "%H:%M")[0:6])).timetuple().tm_hour and datetime.datetime(*(time.strptime(k, "%H:%M")[0:6])).timetuple().tm_hour<5 and i!=1:
                                        finish_t_d = datetime.datetime.date(datetime.datetime.today())+ datetime.timedelta(days=2)
                                    else:
                                        finish_t_d = datetime.datetime.date(datetime.datetime.today())+ datetime.timedelta(days=1)
                                    finish_t_t = datetime.datetime.time((datetime.datetime(*(time.strptime(f_time, "%H:%M")[0:6]))))
                                    finish_t1 = datetime.datetime.combine(finish_t_d, finish_t_t)
                                    finish_t = time.mktime(finish_t1.timetuple())-tdelta
                                    prog.append({"start":start_t, "finish":finish_t, "program":{"title":title_pr.replace("\\/","//")}})
                            except Exception, e:
                                print e
                            s_time = g.string.encode('utf-8')
                        elif g['class'].find('prname2')>-1 or g['class'].find('pastprname2')>-1:
                            try:
                                try:
                                    try:
                                        title_pr = g.string.encode('utf-8')
                                    except:
                                        title_pr = g.contents[0].encode('utf-8')
                                except Exception, e:
                                    title_pr = g.contents[1].encode('utf-8')
                            except:
                                m=g.findAll('a')
                                for p in m:
                                    title_pr = p.string.encode('utf-8')
        d.append({"events":prog})
        add_to_db_New(str(ch)+"vsetv", d[0])

def GetChCache():
    zone = str(time.timezone / 3600)
    try:
        tz = tzd[zone]
        tdelta = 0
        #print "YATV timezone="+str(time.timezone)
        #print "YATV tz="+str(tz)
    except:
        tz = "9"
        tdelta = (4*3600 + time.altzone)
        #print "YATV Except: timezone="+str(time.timezone)
        #print "YATV Except: tz="+str(tz)
    channels = ["997","998","994","996","993","734","758","328","853","314","21","916","1016","688","328","1013","140","1016","949","950","951","947","899","934","991","767","557","558","539","906","752","863","1003","900","1000","1005","970","550","548","571","926","543","547","546","509","405","564","862","730","909","542","645","924","556","863","538","625","74","809","240","901","549","965","529","967","702","942","943","751","98","917","788","339","598","392","670","904","763","887","842","536","796","910","797","911","889","845","572","402","695","748","777","145","727","761","513","790","759","481","448","773","139","348","843","696","666","663","143","664","754","455","296","382","272","457","532","111","726","737","557","504","505","692","799","353","716"]
    data = urllib.urlencode({'timezone' : tz})
    cookie = GetCookie('http://www.vsetv.com/rewrite_url.php', data)
    for ch in channels:
        dt=datetime.datetime.strftime(datetime.datetime.now() ,"%Y-%m-%d")
        s_time = ""
        f_time = ""
        title_pr = ""
        timezone = urllib.urlencode({
            'timezone' : tz,
            'submit.x' : '13',
            'submit.y' : '9',
            'selected_channel' : 'channel_'+ch+'',
            'selected_date' : 'day_'+dt+''
        })
        Url = 'http://www.vsetv.com/rewrite_url.php'
        http = GET(Url, Url, timezone, cookie)
        #if ch == "1016":
            #print http
        beautifulSoup = BeautifulSoup(http)
        el = beautifulSoup.findAll('div', attrs={'id': 'schedule_container'})
        #beautifulSoup = BeautifulSoup(http)
        tzsite = beautifulSoup.findAll('select', attrs={'name': 'timezone'})
        print "tzsite= "+str(tzsite)
        d=[]
        prog=[]
        i=0
        if tdelta == 0:
            for gr in el:
                for g in gr:
                    if not g['class'].find('pasttime')>-1 and not g['class'].find('pastprname2')>-1 and not g['class'].find('pastdesc')>-1:
                        if g['class'].find('time')>-1 or g['class'].find('onair')>-1:
                            i+=1
                            if i==1: k=g.string.encode('utf-8')
                            f_time = g.string.encode('utf-8')
                            try:
                                if not s_time == "" and not title_pr == "":
                                    #if ch == "818": 
                                        #print s_time 
                                        #print f_time
                                        #print title_pr
                                    if datetime.datetime(*(time.strptime(s_time, "%H:%M")[0:6])).timetuple().tm_hour < datetime.datetime(*(time.strptime(k, "%H:%M")[0:6])).timetuple().tm_hour:
                                        start_t_d = datetime.datetime.date(datetime.datetime.today())+ datetime.timedelta(days=1)
                                    elif datetime.datetime(*(time.strptime(s_time, "%H:%M")[0:6])).timetuple().tm_hour >= datetime.datetime(*(time.strptime(k, "%H:%M")[0:6])).timetuple().tm_hour and datetime.datetime(*(time.strptime(k, "%H:%M")[0:6])).timetuple().tm_hour<5:
                                        start_t_d = datetime.datetime.date(datetime.datetime.today())+ datetime.timedelta(days=1)
                                    else:
                                        start_t_d = datetime.datetime.date(datetime.datetime.today())
                                    start_t_t = datetime.datetime.time((datetime.datetime(*(time.strptime(s_time, "%H:%M")[0:6]))))
                                    start_t1 = datetime.datetime.combine(start_t_d, start_t_t)
                                    start_t = time.mktime(start_t1.timetuple())
                                    if datetime.datetime(*(time.strptime(f_time, "%H:%M")[0:6])).timetuple().tm_hour < datetime.datetime(*(time.strptime(k, "%H:%M")[0:6])).timetuple().tm_hour:
                                        finish_t_d = datetime.datetime.date(datetime.datetime.today())+ datetime.timedelta(days=1)
                                    elif datetime.datetime(*(time.strptime(f_time, "%H:%M")[0:6])).timetuple().tm_hour >= datetime.datetime(*(time.strptime(k, "%H:%M")[0:6])).timetuple().tm_hour and datetime.datetime(*(time.strptime(k, "%H:%M")[0:6])).timetuple().tm_hour<5:
                                        finish_t_d = datetime.datetime.date(datetime.datetime.today())+ datetime.timedelta(days=1)
                                    else:
                                        finish_t_d = datetime.datetime.date(datetime.datetime.today())
                                    finish_t_t = datetime.datetime.time((datetime.datetime(*(time.strptime(f_time, "%H:%M")[0:6]))))
                                    finish_t1 = datetime.datetime.combine(finish_t_d, finish_t_t)
                                    finish_t = time.mktime(finish_t1.timetuple())
                                    prog.append({"start":start_t, "finish":finish_t, "program":{"title":title_pr.replace("\\/","//")}})
                            except Exception, e:
                                print e
                            s_time = g.string.encode('utf-8')
                        elif g['class'].find('prname2')>-1:
                            try:
                                try:
                                    try:
                                        title_pr = g.string.encode('utf-8')
                                    except:
                                        title_pr = g.contents[0].encode('utf-8')
                                except Exception, e:
                                    title_pr = g.contents[1].encode('utf-8')
                            except:
                                m=g.findAll('a')
                                for p in m:
                                    title_pr = p.string.encode('utf-8')
        else:
            for gr in el:
                for g in gr:
                    if not g['class'].find('pastdesc')>-1:
                        if g['class'].find('time')>-1 or g['class'].find('onair')>-1 or g['class'].find('pasttime')>-1:
                            i+=1
                            if i==1: k=g.string.encode('utf-8')
                            f_time = g.string.encode('utf-8')
                            try:
                                if not s_time == "" and not title_pr == "":
                                    if datetime.datetime(*(time.strptime(s_time, "%H:%M")[0:6])).timetuple().tm_hour < datetime.datetime(*(time.strptime(k, "%H:%M")[0:6])).timetuple().tm_hour:
                                        start_t_d = datetime.datetime.date(datetime.datetime.today())+ datetime.timedelta(days=1)
                                    elif datetime.datetime(*(time.strptime(s_time, "%H:%M")[0:6])).timetuple().tm_hour >= datetime.datetime(*(time.strptime(k, "%H:%M")[0:6])).timetuple().tm_hour and datetime.datetime(*(time.strptime(k, "%H:%M")[0:6])).timetuple().tm_hour<5:
                                        start_t_d = datetime.datetime.date(datetime.datetime.today())+ datetime.timedelta(days=1)
                                    else:
                                        start_t_d = datetime.datetime.date(datetime.datetime.today())
                                    start_t_t = datetime.datetime.time((datetime.datetime(*(time.strptime(s_time, "%H:%M")[0:6]))))
                                    start_t1 = datetime.datetime.combine(start_t_d, start_t_t)
                                    start_t = time.mktime(start_t1.timetuple())-tdelta
                                    if datetime.datetime(*(time.strptime(f_time, "%H:%M")[0:6])).timetuple().tm_hour < datetime.datetime(*(time.strptime(k, "%H:%M")[0:6])).timetuple().tm_hour:
                                        finish_t_d = datetime.datetime.date(datetime.datetime.today())+ datetime.timedelta(days=1)
                                    elif datetime.datetime(*(time.strptime(f_time, "%H:%M")[0:6])).timetuple().tm_hour >= datetime.datetime(*(time.strptime(k, "%H:%M")[0:6])).timetuple().tm_hour and datetime.datetime(*(time.strptime(k, "%H:%M")[0:6])).timetuple().tm_hour<5:
                                        finish_t_d = datetime.datetime.date(datetime.datetime.today())+ datetime.timedelta(days=1)
                                    else:
                                        finish_t_d = datetime.datetime.date(datetime.datetime.today())
                                    finish_t_t = datetime.datetime.time((datetime.datetime(*(time.strptime(f_time, "%H:%M")[0:6]))))
                                    finish_t1 = datetime.datetime.combine(finish_t_d, finish_t_t)
                                    finish_t = time.mktime(finish_t1.timetuple())-tdelta
                                    #if ch == "1016":
                                        #print "title= "+str(title_pr)
                                        #print "f_time= "+str(f_time)
                                        #print "finish_t= "+str(finish_t)
                                        #print "timetuple= "+str(finish_t1.timetuple())
                                        #print "time.mktime= "+str(time.mktime(finish_t1.timetuple()))
                                    prog.append({"start":start_t, "finish":finish_t, "program":{"title":title_pr.replace("\\/","//")}})
                            except Exception, e:
                                print e
                            s_time = g.string.encode('utf-8')
                        elif g['class'].find('prname2')>-1 or g['class'].find('pastprname2')>-1:
                            try:
                                try:
                                    try:
                                        title_pr = g.string.encode('utf-8')
                                    except:
                                        title_pr = g.contents[0].encode('utf-8')
                                except Exception, e:
                                    title_pr = g.contents[1].encode('utf-8')
                            except:
                                m=g.findAll('a')
                                for p in m:
                                    title_pr = p.string.encode('utf-8')
            dt=datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=1) ,"%Y-%m-%d")
            timezone = urllib.urlencode({
            'timezone' : tz,
            'submit.x' : '13',
            'submit.y' : '9',
            'selected_channel' : 'channel_'+ch+'',
            'selected_date' : 'day_'+dt+''
            })
            Url = 'http://www.vsetv.com/rewrite_url.php'
            http = GET(Url, Url, timezone, cookie)
            beautifulSoup = BeautifulSoup(http)
            el = beautifulSoup.findAll('div', attrs={'id': 'schedule_container'})
            #d=[]
            #prog=[]
            i=0
            for gr in el:
                for g in gr:
                    if not g['class'].find('pastdesc')>-1:
                        if g['class'].find('time')>-1 or g['class'].find('onair')>-1 or g['class'].find('pasttime')>-1:
                            i+=1
                            if i==1: k=g.string.encode('utf-8')
                            f_time = g.string.encode('utf-8')
                            try:
                                if not s_time == "" and not title_pr == "":
                                    if datetime.datetime(*(time.strptime(s_time, "%H:%M")[0:6])).timetuple().tm_hour < datetime.datetime(*(time.strptime(k, "%H:%M")[0:6])).timetuple().tm_hour and i!=1:
                                        start_t_d = datetime.datetime.date(datetime.datetime.today())+ datetime.timedelta(days=2)
                                    elif datetime.datetime(*(time.strptime(s_time, "%H:%M")[0:6])).timetuple().tm_hour >= datetime.datetime(*(time.strptime(k, "%H:%M")[0:6])).timetuple().tm_hour and datetime.datetime(*(time.strptime(k, "%H:%M")[0:6])).timetuple().tm_hour<5 and i!=1:
                                        start_t_d = datetime.datetime.date(datetime.datetime.today())+ datetime.timedelta(days=2)
                                    else:
                                        start_t_d = datetime.datetime.date(datetime.datetime.today())+ datetime.timedelta(days=1)
                                    start_t_t = datetime.datetime.time((datetime.datetime(*(time.strptime(s_time, "%H:%M")[0:6]))))
                                    start_t1 = datetime.datetime.combine(start_t_d, start_t_t)
                                    start_t = time.mktime(start_t1.timetuple())-tdelta
                                    if datetime.datetime(*(time.strptime(f_time, "%H:%M")[0:6])).timetuple().tm_hour < datetime.datetime(*(time.strptime(k, "%H:%M")[0:6])).timetuple().tm_hour and i!=1:
                                        finish_t_d = datetime.datetime.date(datetime.datetime.today())+ datetime.timedelta(days=2)
                                    elif datetime.datetime(*(time.strptime(f_time, "%H:%M")[0:6])).timetuple().tm_hour >= datetime.datetime(*(time.strptime(k, "%H:%M")[0:6])).timetuple().tm_hour and datetime.datetime(*(time.strptime(k, "%H:%M")[0:6])).timetuple().tm_hour<5 and i!=1:
                                        finish_t_d = datetime.datetime.date(datetime.datetime.today())+ datetime.timedelta(days=2)
                                    else:
                                        finish_t_d = datetime.datetime.date(datetime.datetime.today())+ datetime.timedelta(days=1)
                                    finish_t_t = datetime.datetime.time((datetime.datetime(*(time.strptime(f_time, "%H:%M")[0:6]))))
                                    finish_t1 = datetime.datetime.combine(finish_t_d, finish_t_t)
                                    finish_t = time.mktime(finish_t1.timetuple())-tdelta
                                    prog.append({"start":start_t, "finish":finish_t, "program":{"title":title_pr.replace("\\/","//")}})
                            except Exception, e:
                                print e
                            s_time = g.string.encode('utf-8')
                        elif g['class'].find('prname2')>-1 or g['class'].find('pastprname2')>-1:
                            try:
                                try:
                                    try:
                                        title_pr = g.string.encode('utf-8')
                                    except:
                                        title_pr = g.contents[0].encode('utf-8')
                                except Exception, e:
                                    title_pr = g.contents[1].encode('utf-8')
                            except:
                                m=g.findAll('a')
                                for p in m:
                                    title_pr = p.string.encode('utf-8')

        d.append({"events":prog})
        save_cache(d[0], str(ch)+"vsetv")

def GetChannels(Url):
	http = GET(Url, Url)
	ht={}
	if http == None:
		showMessage('YaTV:', 'Сервер не отвечает', 1000)
		http = GET(Url, Url)
		if http == None:
			http = GET(Url, Url)
			if http == None:
				return None
			else:
				http = http.replace(':false',':0').replace(':true',':1')
				http=eval(http)
				for channel in http["schedules"]:
					if xbmc.abortRequested:
						break
					else:
						save_cache(channel, channel["channel"]["id"])
		else:
			http = http.replace(':false',':0').replace(':true',':1')
			http=eval(http)
			for channel in http["schedules"]:
				if xbmc.abortRequested:
					break
				else:
					save_cache(channel, channel["channel"]["id"])
	else:
		http = http.replace(':false',':0').replace(':true',':1')
		http=eval(http)
		for channel in http["schedules"]:
			if xbmc.abortRequested:
				break
			else:
				save_cache(channel, channel["channel"]["id"])

def UpdCache():
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[146,711,649,162,187,515,353,304,18,79],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[427,405,511,698,291,740,323,557,898,150],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[421,655,335,161,334,916,917,918,919,921],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[922,924,925,926,927,928,929,932,933,934],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[935,710,579,658,365,516,463,601,495,325],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[409,437,60,23,850,288,661,429,575,608],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[102,567,55,127,267,309,589,213,521,277],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[346,454,669,66,923,834,273,123,798,462],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[22,71,542,618,675,518,12,485,783,617],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[566,638,743,53,406,663,447,181,173,163],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[794,716,180,779,686,61,16,502,410,659],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[615,810,520,352,19,494,598,646,51,138],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[741,15,801,145,82,765,223,328,31,644],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[37,434,384,648,313,119,125,789,547,156],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[455,333,604,376,769,705,21,626,637,477],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[1008,918,852,1039,1033,1436],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[275,776,555,308,332,849,388,897,425,774],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[258,389,680,723,154,367,505,595,6,737],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[481,726,423,113,713,111,662,201,681,322],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[377,499,134,664,183,697,358,563,311,217],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[24,799,821,614,153,415,250,8,401,306],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[557,1003,1021,747,987,988,1035,1032,1329],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[214,851,923,920,931,930,911,912,983,984],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[990,989,986,987,988,756,828,355,312,715],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[777,284,278,797,319,831,757,393,461,631],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[59,315,442,804,533,25,642,141,552,247],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[132,39,591,331,731,491,91,554,531,473],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[412,430,431,11,121,807,363,685,509,464],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[151,730,560,178,35,382,576,349,270,237],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[852,165,257,249,777,984,412,382,178,655],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[119,994,1037,1377,916,161,579,1371,1372,463],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[929,495,355,1330,393,1394,1026,801,921,1359],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[716,589,1012,1013,1011,613,124,996,1036,1392],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[1331,897,1332,1000,638,1322,933,789,922],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[1396,1562,59,925],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[620,583,586,680,937,281,709,228,430,167],"duration":43200,"lang":"ru"}&userRegion=187&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[280,76,627,939,677,808,453,632,788,128],"duration":43200,"lang":"ru"}&userRegion=187&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[422,140,507,85,773,940,143,181,670,650],"duration":43200,"lang":"ru"}&userRegion=187&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[479,326,90,666,753,702,315,649,18,391],"duration":43200,"lang":"ru"}&userRegion=187&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[458,1009,1555,1478,1525,1487,1492,1557,1488,1528],"duration":43200,"lang":"ru"}&userRegion=187&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[1511,1500,1537,1499,1477,1508,1552,1466,1464,1476],"duration":43200,"lang":"ru"}&userRegion=187&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[1548,1495,1550,1507,1534,1538,1470,1533,1530,1535],"duration":43200,"lang":"ru"}&userRegion=187&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[1473,1481,1522,1521,1513,1483,1512,1510,1553,1547],"duration":43200,"lang":"ru"}&userRegion=187&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[1503,1516,1480,1468,1502,1489,1514,1465,1515,1505],"duration":43200,"lang":"ru"}&userRegion=187&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[1506,1469,1462,1485,1498,1484,1559,1493,1467,1471],"duration":43200,"lang":"ru"}&userRegion=187&resource=schedule'
    GetChannels(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[1526,1456,1505,1463,1472,1531],"duration":43200,"lang":"ru"}&userRegion=187&resource=schedule'
    GetChannels(Url)
    GetChCache()

def GetChannelsFull(Url):
	http = GET(Url, Url)
	if http == None:
		showMessage('YaTV:', 'Сервер не отвечает', 1000)
		http = GET(Url, Url)
		if http == None:
			http = GET(Url, Url)
			if http == None:
				return None
			else:
				http = http.replace(':false',':0').replace(':true',':1')
				http = eval(http.replace("\\/","//"))
				for channel in http["schedules"]:
					if xbmc.abortRequested:
						break
					else:
						add_to_db_New(channel["channel"]["id"], channel)
						xbmc.sleep(250)
		else:
			http = http.replace(':false',':0').replace(':true',':1')
			http = eval(http.replace("\\/","//"))
			for channel in http["schedules"]:
				if xbmc.abortRequested:
					break
				else:
					add_to_db_New(channel["channel"]["id"], channel)
					xbmc.sleep(250)
	else:
		http = http.replace(':false',':0').replace(':true',':1')
		http = eval(http.replace("\\/","//"))
		for channel in http["schedules"]:
			if xbmc.abortRequested:
				break
			else:
				add_to_db_New(channel["channel"]["id"], channel)
				xbmc.sleep(250)
			
def UpdFull():
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[146,711,649,162,187,515,353,304,18,79],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[427,405,511,698,291,740,323,557,898,150],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[421,655,335,161,334,916,917,918,919,921],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[922,924,925,926,927,928,929,932,933,934],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[935,710,579,658,365,516,463,601,495,325],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[409,437,60,23,850,288,661,429,575,608],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[102,567,55,127,267,309,589,213,521,277],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[346,454,669,66,923,834,273,123,798,462],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[22,71,542,618,675,518,12,485,783,617],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[566,638,743,53,406,663,447,181,173,163],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[794,716,180,779,686,61,16,502,410,659],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[615,810,520,352,19,494,598,646,51,138],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[741,15,801,145,82,765,223,328,31,644],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[37,434,384,648,313,119,125,789,547,156],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[455,333,604,376,769,705,21,626,637,477],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[1008,918,852,1039,1033,1436],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[275,776,555,308,332,849,388,897,425,774],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[258,389,680,723,154,367,505,595,6,737],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[481,726,423,113,713,111,662,201,681,322],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[377,499,134,664,183,697,358,563,311,217],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[24,799,821,614,153,415,250,8,401,306],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[557,1003,1021,747,987,988,1035,1032,1329],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[214,851,923,920,931,930,911,912,983,984],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[990,989,986,987,988,756,828,355,312,715],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[777,284,278,797,319,831,757,393,461,631],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[59,315,442,804,533,25,642,141,552,247],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[132,39,591,331,731,491,91,554,531,473],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[412,430,431,11,121,807,363,685,509,464],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[151,730,560,178,35,382,576,349,270,237],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[852,165,257,249,777,984,412,382,178,655],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[119,994,1037,1377,916,161,579,1371,1372,463],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[929,495,355,1330,393,1394,1026,801,921,1359],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[716,589,1012,1013,1011,613,124,996,1036,1392],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[1331,897,1332,1000,638,1322,933,789,922],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[1396,1562,59,925],"duration":43200,"lang":"ru"}&userRegion=213&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[620,583,586,680,937,281,709,228,430,167],"duration":43200,"lang":"ru"}&userRegion=187&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[280,76,627,939,677,808,453,632,788,128],"duration":43200,"lang":"ru"}&userRegion=187&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[422,140,507,85,773,940,143,181,670,650],"duration":43200,"lang":"ru"}&userRegion=187&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[479,326,90,666,753,702,315,649,18,391],"duration":43200,"lang":"ru"}&userRegion=187&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[458,1009,1555,1478,1525,1487,1492,1557,1488,1528],"duration":43200,"lang":"ru"}&userRegion=187&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[1511,1500,1537,1499,1477,1508,1552,1466,1464,1476],"duration":43200,"lang":"ru"}&userRegion=187&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[1548,1495,1550,1507,1534,1538,1470,1533,1530,1535],"duration":43200,"lang":"ru"}&userRegion=187&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[1473,1481,1522,1521,1513,1483,1512,1510,1553,1547],"duration":43200,"lang":"ru"}&userRegion=187&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[1503,1516,1480,1468,1502,1489,1514,1465,1515,1505],"duration":43200,"lang":"ru"}&userRegion=187&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[1506,1469,1462,1485,1498,1484,1559,1493,1467,1471],"duration":43200,"lang":"ru"}&userRegion=187&resource=schedule'
    GetChannelsFull(Url)
    Url = 'http://tv.yandex.ru/ajax/i-tv-region/get?params={"channelIds":[1526,1456,1505,1463,1472,1531],"duration":43200,"lang":"ru"}&userRegion=187&resource=schedule'
    GetChannelsFull(Url)
    GetCh()

def GetPr(id2,format=None):
        #print "запрос"
        try:
            #print id2
            #GetChCache()
            try:import torr2xbmc
            except:pass
            try: d=eval(get_inf_db_New(id2)[0][0].replace("#z","\\").replace("#y",'"'))
            except Exception, e:
                #print e
                try: d=get_cache(id2)
                except Exception, e:
                    #print "ERROR CACHE " + str(e)
                    return {}
        except Exception, e:
            print e
            return {}
        rez={}
        #title      = d["channel"]["title"]
        #print d
        #idch       = d["channel"]["id"]
        try:logo   = d["channel"]["logo"]["src"]
        except:logo=""
        prlist= d["events"]
        #print prlist
        plot = []
        k=0
        plt=""
        prog1=[]
        p_list=[]
        type1=""
        img=""
        st=""
        year=""
        age=""
        plt_time=""
        plt_prog=""
        tdlocal = (datetime.datetime.now().timetuple().tm_hour - datetime.datetime.utcnow().timetuple().tm_hour)*3600
        for j in prlist:
            #print j["program"]["title"]
            try:
                td=datetime.timedelta(hours=int(j["finish"][-4]))
                start_t = time.mktime((datetime.datetime(*(time.strptime(j["start"][:j["start"].count(j["start"])-7], "%Y-%m-%dT%H:%M:%S")[0:6]))-td).timetuple())+tdlocal#-time.timezone + time.localtime().tm_isdst*3600
                finish_t = time.mktime((datetime.datetime(*(time.strptime(j["finish"][:j["finish"].count(j["finish"])-7], "%Y-%m-%dT%H:%M:%S")[0:6]))-td).timetuple())+tdlocal#-time.timezone + time.localtime().tm_isdst*3600
            except Exception, e:
                #print e
                try:
                    start_t = j["start"]
                    finish_t = j["finish"]
                except Exception, e:
                    print e
            #print 'finish_t'+str(finish_t)
            if finish_t > time.time():
                #print 'finish_t'+str(finish_t)
                try:
                    start   = time.localtime(float(start_t))
                    finish  = time.localtime(float(finish_t))
                    if finish.tm_min<10: f_time_m = ":0"+str(finish.tm_min)
                    else:                f_time_m = ":"+str(finish.tm_min)
                    if finish.tm_hour<10: f_time_h = "0"+str(finish.tm_hour)
                    else:                f_time_h = str(finish.tm_hour)
                    if start.tm_min<10: s_time_m = ":0"+str(start.tm_min)
                    else:                s_time_m = ":"+str(start.tm_min)
                    if start.tm_hour<10: s_time_h = "0"+str(start.tm_hour)
                    else:                s_time_h = str(start.tm_hour)
                    f_time=f_time_h+f_time_m
                    s_time=s_time_h+s_time_m
                except Exception, e:
                    print 'ERROR TIME '+str(e)
                try:
                    title_pr = j["program"]["title"]
                    #print title_pr
                except Exception, e:
                    print e
                try:type2= j["program"]["type"]
                except: type2=""
                try:age = j["program"]["age"]
                except: age="0"
                k+=1
                if k==1:
                    st = start_t
                    year = finish.tm_year
                    try:type1=j["program"]["type"]["name"]
                    except: type1=""
                    try:
                        img=j["program"]["images"][0]["sizes"]["200"]["src"].replace("normal","orig").replace("//","http://")
                    except:img=""
                    try:
                        if torr2xbmc.__addon__.getSetting('description') == 'false':
                            try:
                                if j["program"]["description"] == "":description = ""
                                else:description = j["program"]["description"] + chr(10)
                            except:description = ""
                        else:description = ""
                    except:description = ""
                    plt = plt +"[B][COLOR FF0084FF]"+ s_time+"[/COLOR] [COLOR FFFFFFFF]"+"[B][COLOR FF0084FF]"+"-"+"[/COLOR] [COLOR FFFFFFFF]"+"[B][COLOR FF0084FF]"+ f_time+"[/COLOR][/B][COLOR FF111111] [B][COLOR FFFFFFFF]"+title_pr+"[/COLOR][/B][COLOR FF999999]"+chr(10)+description+"[/COLOR]"
                    try:
                        prog_color = torr2xbmc.__addon__.getSetting('prog_color')
                        prog_b = torr2xbmc.__addon__.getSetting('prog_b')
                        time_color = torr2xbmc.__addon__.getSetting('time_color')
                        prog_i = torr2xbmc.__addon__.getSetting('prog_i')
                        if prog_b == "true":
                            if prog_i == "true":
                                plt_time = "[I][B][COLOR FF"+time_color+"]" + s_time+"-" + f_time+"[/COLOR]"
                                plt_prog = "[I][B][COLOR FF"+prog_color+"]"+title_pr+"[/COLOR][/B][/I]"
                            else:
                                plt_time = "[B][COLOR FF"+time_color+"]" + s_time+"-" + f_time+"[/COLOR]"
                                plt_prog = "[B][COLOR FF"+prog_color+"]"+title_pr+"[/COLOR][/B]"
                        else:
                            if prog_i == "true":
                                plt_time = "[I][COLOR FF"+time_color+"]" + s_time+"-" + f_time+"[/COLOR]"
                                plt_prog = "[I][COLOR FF"+prog_color+"]"+title_pr+"[/COLOR][/I]"
                            else:
                                plt_time = "[COLOR FF"+time_color+"]" + s_time+"-" + f_time+"[/COLOR]"
                                plt_prog = "[COLOR FF"+prog_color+"]"+title_pr+"[/COLOR]"
                    except:
                        plt_time = "[B][COLOR FF0084FF]" + s_time+"-" + f_time+"[/COLOR]"
                        plt_prog = "[B][COLOR FFFFFFFF]"+title_pr+"[/COLOR][/B]"
                elif k<=4:
                    #print k
                    prog1.append({"time":"[B][COLOR FF0084FF]"+ s_time+"[/COLOR] [COLOR FFFFFFFF]"+"[B][COLOR FF0084FF]"+"-"+"[/COLOR] [COLOR FFFFFFFF]"+"[B][COLOR FF0084FF]"+ f_time+"[/COLOR][/B]", "title":"[B][COLOR FFFFFFFF]"+ title_pr +"[/COLOR][/B]"})
                    plt = plt +"[B][COLOR FF0084FF]"+ s_time+"[/COLOR] [COLOR FFFFFFFF]"+"[B][COLOR FF0084FF]"+"-"+"[/COLOR] [COLOR FFFFFFFF]"+"[B][COLOR FF0084FF]"+ f_time+"[/COLOR] [COLOR FFFFFFFF]"+ title_pr +"[/COLOR][/B]"+chr(10)
                    #print 'prog1---'+str(prog1)
                else:
                    #print k
                    plt = plt +"[B][COLOR FF0084FF]"+ s_time+"[/COLOR] [COLOR FFFFFFFF]"+"[B][COLOR FF0084FF]"+"-"+"[/COLOR] [COLOR FFFFFFFF]"+"[B][COLOR FF0084FF]"+ f_time+"[/COLOR] [COLOR FFFFFFFF]"+ title_pr +"[/COLOR][/B]"+chr(10)
                p_list.append({"start": start_t, "finish": finish_t, "s_time": s_time, "f_time": f_time, "title_pr": title_pr, "type":type2, "age":age})
                #print "plt---"+str(plt)
            try:
                rez={"plot":plt, "img":img, "ico":logo, "genre": type1, "year":year, "mpaa":str(age)+"+", "strt":st, "p_list": p_list, "prog1":prog1, "plttime":plt_time, "pltprog":plt_prog}
            except Exception, e:
                print e
                pass
        #print 'rez'+str(rez)
        return rez
    

def GetLastUpdate():
    c = db.connect(database=db_name)
    cu = c.cursor()
    cu.execute("CREATE TABLE IF NOT EXISTS settings (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, lastupdate  datetime, success integer, dbver INTEGER NOT NULL DEFAULT '0');")
    c.commit()
    cu.execute('SELECT lastupdate FROM settings WHERE id = 1')
    res = cu.fetchone()
    if res == None:
        c.close()
        return None
    else:
        try:
            dt = datetime.datetime.fromtimestamp(time.mktime(time.strptime(res[0], '%Y-%m-%d %H:%M:%S.%f')))
            c.close()
            return dt
        except Exception, e:
            print e
            dt = datetime.datetime.now() - datetime.timedelta(hours = 23)
            c.close()
            return dt
    return None


def GetUpdateProg():
	try:
		throwaway = datetime.datetime.strptime('20110101','%Y%m%d')
	except:
		time.sleep(250)
		throwaway = datetime.datetime.strptime('20110101','%Y%m%d')
	lupd = GetLastUpdate()
	global c
	global cu
	if lupd == None:
		try:
			cu.execute('INSERT INTO settings (id, lastupdate, dbver) VALUES (1, "%s", 1);' % datetime.datetime.now())
			c.commit()
			UpdCache()
			UpdFull()
			cu.execute('UPDATE settings SET success = 1 WHERE id = 1;')
			c.commit()
			c.close()
		except Exception, e:
			print e
	else:
		nupd = lupd + datetime.timedelta(hours = 12)
		ver = ""
		try:
			c = db.connect(database=db_name, check_same_thread=False)
			cu = c.cursor()
			cu.execute('SELECT dbver FROM settings WHERE id = 1')
			ver = cu.fetchone()[0]
		except Exception, e:
			ver=0
		if nupd < datetime.datetime.now() or ver <> 1:
			print 'remove db'
			try:
				try:
					c.close()
					os.remove(db_name)
				except:
					try:
						c.close()
						xbmc.sleep(250)
						os.remove(db_name)
					except Exception, e:
						print 'Не удалось удалить старую БД программы: '+ str(e)
						return
				c = db.connect(database=db_name)
				cu = c.cursor()
				cu.execute("CREATE TABLE IF NOT EXISTS settings (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, lastupdate  datetime, success integer, dbver INTEGER NOT NULL DEFAULT '0');")
				c.commit()
				cu.execute('INSERT INTO settings (id, lastupdate, dbver) VALUES (1, "%s", 1);' % datetime.datetime.now())
				c.commit()
				UpdCache()
				UpdFull()
				cu.execute('UPDATE settings SET success = 1 WHERE id = 1;')
				c.commit()
				c.close()
			except Exception, e:
				print 'Ошибка: ' + str(e)
				return
		elif nupd > datetime.datetime.now():
			cu.execute('SELECT success FROM settings WHERE id = 1;')
			sc = cu.fetchone()
			if not sc[0]==1:
				UpdCache()
				UpdFull()
				cu.execute('UPDATE settings SET success = 1 WHERE id = 1;')
				c.commit()
				c.close()
			else:
				if lupd.timetuple().tm_mday != datetime.datetime.now().timetuple().tm_mday:
					GetCh()



def save_cache(item, id):
	s="YAcache="+str(item)
	path=ru(os.path.join(addon.getAddonInfo('path'),"lib"))
	fl = open(os.path.join( path ,"cache"+str(id)+".py"), "w")
	fl.write("# -*- coding: utf-8 -*-"+chr(10))
	fl.write(s)
	fl.close()


def get_cache(id):
    cache =  __import__ ("cache"+str(id))
    YAcache = getattr(cache, "YAcache")
    return YAcache


def add_to_db_New(id, item):
        err=0
        item=str(item)
        try:
            cu.execute('CREATE TABLE "%s" (db_item VARCHAR(255));' %id)
            c.commit()
        except Exception, e:
            err=1
        if err==0:
            cu.execute('INSERT INTO "%s" (db_item) VALUES ("%s");' %(id, item.replace("\\","#z").replace('"',"#y")))
            c.commit()
        elif err==1:
            cu.execute('UPDATE "%s" SET db_item = "%s";' %(id, item.replace("\\","#z").replace('"',"#y")))
            c.commit()
        
def get_inf_db_New(id):
		#tor_id="n"+n
		cu.execute(str('SELECT db_item FROM "%s";' %id))
		c.commit()
		info = cu.fetchall()
		#c.close()
		return info