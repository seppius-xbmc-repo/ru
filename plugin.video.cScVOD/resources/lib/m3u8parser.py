# -*- coding: utf-8 -*-
import urllib2, urllib
import os, re
import hashlib

def parse_megogo(url):
    try:
        video_id = url.split('/')[-1:][0].split('-')[0]
        mCmd = 'info'
        Params = {'video': video_id}
        req_p1 = []
        req_p2 = []
        for mKey in Params:
            req_p1.append('%s=%s' % (mKey, urllib.quote_plus(Params[mKey])))
            req_p2.append('%s=%s' % (mKey, Params[mKey]))
        req_params = '&'.join(req_p1)
        req_hash = ''.join(req_p2)
        m = hashlib.md5()
        m.update('%s%s'%(req_hash,'acfed32a68da1d7c'))
        target = 'http://megogo.net/p/%s?%s&sign=%s' % ('info', req_params, '%s%s' % (m.hexdigest(), '_xbmc'))
        UA = '%s/%s %s/%s/%s' % ('xbmc.python.pluginsource', 'plugin.video.megogo.net', urllib.quote_plus('MEGOGO.NET'), '1.0.1', urllib.quote_plus('MEGOGO.NET'))
        req = urllib2.Request(url = target, data = None, headers = {'User-Agent':UA})
        resp = urllib2.urlopen(req)
        page_target = resp.read()
        url = re.findall('{"src":"(.*)","alternateSrc"', page_target)[0].replace('\/','/')
       # print 'parsed url = ', url
    except Exception as ex:
        print ex
        
    if url.find('m3u8') > -1:
        best_m3u8(url)
	
	return(url)
	
def best_m3u8(url):
    video_tulpe = []
    video_tulpe_tmp = []
    url_main = ''
    film_quality = None
    try:
        url_split = url.split('/')[:-1]
        for url_frag in url_split:
            url_main = url_main + (url_frag + '/')	
        req = urllib2.Request(url = url, data = None, headers = {'User-agent': 'QuickTime/7.6.2 (qtver=7.6.2;os=Windows NT 5.1 Service Pack 3)'})
        resp = urllib2.urlopen(req)
        page = resp.read()
        film_quality = re.findall('BANDWIDTH=(.*)', page)
        video_tulpe_tmp = re.findall('BANDWIDTH=.*\s(.*)', page)
        if video_tulpe_tmp[0].find('http') < 0:
            for tulpe in video_tulpe_tmp:
                video_tulpe.append(url_main + tulpe)
        else:
            video_tulpe = video_tulpe_tmp
        url = video_tulpe[0]
        #print '***** best url ***** = ', url
    except Exception as ex:
        print ex
	
	return(url)

