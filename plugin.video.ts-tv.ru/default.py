#!/usr/bin/python
# -*- coding: utf-8 -*-
#/*
# *  Copyright (c) 2011-2012 XBMC-Russia, HD-lab Team, E-mail: dev@hd-lab.ru
# *  Writer (c) 2011, Kostynoy S.A., E-mail: seppius2@gmail.com
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
# *  http://www.gnu.org/copyleft/gpl.html
# */
import xbmcaddon, xbmc, xbmcgui, xbmcplugin, os, urllib

handle = int(sys.argv[1])
thumb  = os.path.join( os.getcwd().replace(';', ''),'icon.png' )

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

def ShowRoot():
	def addItem(index, name, first, secon):
		listitem = xbmcgui.ListItem('%s. %s'%(index,name), iconImage = thumb, thumbnailImage = thumb)
		uri  = sys.argv[0] + '?mode=Play'
		uri += '&title=' + urllib.quote_plus(name)
		uri += '&first=' + urllib.quote_plus(first)
		uri += '&secon=' + urllib.quote_plus(secon)
		listitem.setProperty('fanart_image', thumb)
		xbmcplugin.addDirectoryItem(handle, uri, listitem)
	addItem(1, ' Концепция',      'mms://212.1.238.70/ts_tv',   'mms://85.21.245.129/ts_tv')
	addItem(2, ' Русский крест',  'mms://212.1.238.70/ts_tv2',  'mms://85.21.245.129/ts_tv2')
	addItem(3, ' Телепередачи',   'mms://212.1.238.70/ts_tv3',  'mms://85.21.245.129/ts_tv3')
	addItem(4, ' Научный',        'mms://212.1.238.70/ts_tv4',  'mms://85.21.245.129/ts_tv4')
	addItem(5, ' Здоровье',       'mms://212.1.238.70/ts_tv5',  'mms://85.21.245.129/ts_tv5')
	addItem(6, ' Документальный', 'mms://212.1.238.70/ts_tv6',  'mms://85.21.245.129/ts_tv6')
	addItem(7, ' Тематический',   'mms://212.1.238.70/ts_tv7',  'mms://85.21.245.129/ts_tv7')
	addItem(8, ' Художественный', 'mms://212.1.238.70/ts_tv8',  'mms://85.21.245.129/ts_tv8')
	addItem(9, ' Музыкальный',    'mms://212.1.238.70/ts_tv9',  'mms://85.21.245.129/ts_tv9')
	addItem(10, 'Анимационный',   'mms://212.1.238.70/ts_tv10', 'mms://85.21.245.129/ts_tv10')
	addItem(11, 'Новости',        'mms://212.1.238.70/ts_tv11', 'mms://85.21.245.129/ts_tv11')
	addItem(12, 'Анонсы',         'mms://212.1.238.70/ts_tv1',  'mms://85.21.245.129/ts_tv1')
	xbmcplugin.endOfDirectory(handle)

def Play(title, src1, src2):
	selected = xbmcgui.Dialog().select(title, ['Основной сервер','Резервный сервер'])
	if   selected == 0: xbmc.Player().play(src1)
	elif selected == 1: xbmc.Player().play(src2)
	else: return

params = get_params()
try: mode  = urllib.unquote_plus(params["mode"])
except: mode  = None
try: title  = urllib.unquote_plus(params["title"])
except: title = ''
try: first  = urllib.unquote_plus(params["first"])
except: title = ''
try: secon  = urllib.unquote_plus(params["secon"])
except: title = ''
if mode == None: ShowRoot()
elif mode == 'Play':  Play(title, first, secon)
