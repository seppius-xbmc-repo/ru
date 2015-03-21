#!/usr/bin/python
# -*- coding: utf-8 -*-
#/*
# *   Copyright (с) 2011 XBMC-Russia, HD-lab Team, E-mail: dev@hd-lab.ru
# *   Writer (C) 03/03/2011, Kostynoy S.A., E-mail: seppius2@gmail.com
# *
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/licenses/gpl.html
# */
import urllib,urllib2,re,sys,os,time
import xbmcplugin,xbmcgui

pluginhandle = int(sys.argv[1])
fanart = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'fanart.jpg'))
xbmcplugin.setPluginFanart(pluginhandle, fanart)

def getURL(url):
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Opera/9.80 (X11; Linux i686; U; ru) Presto/2.7.62 Version/11.00')
	req.add_header('Accept', 'text/html, application/xml, application/xhtml+xml, */*')
	req.add_header('Accept-Language', 'ru,en;q=0.9')
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	return link

# begin Silhouette code (http://xbmc.ru/forum/showthread.php?p=19398#post19398)
def toLcTm(tzd, tmst):
		return time.strftime("%H:%M",time.localtime((time.mktime(tmst) - tzd*3600)))

def root(url):

	try:
		msktmht = getURL('http://time.jp-net.ru/');
		msktmls = re.compile('<h1 align=\'center\'>(.*?): (.*?)</h1>').findall(msktmht)
		msktmst = time.strptime(msktmls[0][1] + ' ' + msktmls[1][1], "%Y-%d-%m %H:%M:%S")
		#print (msktmls[0][1] + ' ' + msktmls[1][1])
		tzdf = round( (time.mktime(msktmst) - time.mktime(time.localtime())) / (3600))
	except:
		pass

	http = getURL(url)
	oneline = re.sub( '\n', ' ', http)
	chndls = re.compile('<div class="chlogo">(.*?)</div> <!-- (left|right)(up|down)part -->').findall(oneline)
	for chndel, rEL, rEU in chndls:
		chells = re.compile('<a href=(.*?)><img src="(.*?)" alt="(.*?)" title="(.*?)"></div>').findall(chndel)
		description = chells[0][3]
		title = description
		thumbnail = chells[0][1].replace('./', url)
		uri = sys.argv[0] + '?mode=BIG'
		uri += '&url='+urllib.quote_plus(url + chells[0][0])
		uri += '&name='+urllib.quote_plus(title)
		uri += '&plot='+urllib.quote_plus(description)
		uri += '&thumbnail='+urllib.quote_plus(thumbnail)
		ptls = re.compile('<div class="prtime">(.*?)</div><div class="prdesc">(.*?)</div>').findall(chndel)
		ptlsln = len(ptls)
		i = 1
		while ptlsln - i + 1:
			prtm = ptls[ptlsln - i][0]
			prds = ptls[ptlsln - i][1]
			prtmst = time.strptime(msktmls[0][1] + ' ' + prtm, "%Y-%d-%m %H:%M")
			try:
				tmdf = time.mktime(msktmst) - time.mktime(prtmst)
				if (((tmdf < 0) and (tmdf > -12*3600.0)) or (tmdf > 12*3600.0)) and (ptlsln > 1):
					i += 1
				else:
#                    if i > 1:
#                        prtm = prtm + '-' + ptls[ptlsln - i + 1][0]
					if i > 1:
						prtmst2 = time.strptime(msktmls[0][1] + ' ' + ptls[ptlsln - i + 1][0], "%Y-%d-%m %H:%M")
						prtm = toLcTm(tzdf, prtmst) + '-' + toLcTm(tzdf, prtmst2)
					else:
						prtm = toLcTm(tzdf, prtmst)
					title = prtm + " " + prds
					break
			except:
				break

		if ptlsln:
			#print title
			item=xbmcgui.ListItem(title, iconImage=thumbnail, thumbnailImage=thumbnail)
			item.setInfo( type='video', infoLabels={'title': title, 'plot': description})
			item.setProperty('IsPlayable', 'true')
			item.setProperty('fanart_image',thumbnail)
			xbmcplugin.addDirectoryItem(pluginhandle,uri,item)
	xbmcplugin.endOfDirectory(pluginhandle)
# end Silhouette code

def playVideo(url, name, thumbnail, plot):
	response    = getURL(url)
	SWFObject   = 'http://debilizator.tv/' + re.compile('new SWFObject\(\'(.*?)\'').findall(response)[0]
	flashvars   = re.compile('so.addParam\(\'flashvars\',\'(.*?)\'\);').findall(response)[0] + '&'
	flashparams = flashvars.split('&')
	param = {}
	for i in range(len(flashparams)):
		splitparams = {}
		splitparams = flashparams[i].split('=')
		if (len(splitparams)) == 2:
			param[splitparams[0]] = splitparams[1]
	rtmp_file     = param['file']
	rtmp_streamer = param['streamer']
	#rtmp_plugins  = param['plugins']
	rtmp_streamer = rtmp_streamer.replace('/load','/tv')
	furl  = ''
	furl += '%s/%s'%(rtmp_streamer,rtmp_file)
	furl += ' swfurl=%s'%SWFObject
	furl += ' pageUrl=%s'%url
	furl += ' tcUrl=%s'%rtmp_streamer
	furl += ' swfVfy=True Live=True'
	#xbmc.output('furl = %s'%furl)
	item = xbmcgui.ListItem(path = furl)
	xbmcplugin.setResolvedUrl(pluginhandle, True, item)

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

params=get_params()
url=None
name=''
plot=''
mode=None
thumbnail=fanart

try: mode=params['mode']
except: pass
try: url=urllib.unquote_plus(params['url'])
except: pass
try: name=urllib.unquote_plus(params['name'])
except: pass
try: thumbnail=urllib.unquote_plus(params['thumbnail'])
except: pass
try: plot=urllib.unquote_plus(params['plot'])
except: pass

if mode == 'BIG': playVideo(url, name, thumbnail, plot)
else: root('http://debilizator.tv/')

