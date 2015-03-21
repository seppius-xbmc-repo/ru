#!/usr/bin/python
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
import urllib2, re, xbmcaddon, string, xbmc, xbmcgui, xbmcplugin

__settings__ = xbmcaddon.Addon(id='plugin.video.cnews.tv')
__language__ = __settings__.getLocalizedString

HEADER  = "Opera/10.60 (X11; openSUSE 11.3/Linux i686; U; ru) Presto/2.6.30 Version/10.60"
handle  = int(sys.argv[1])
target  = 'http://tv.cnews.ru/bottom_init.php'
referer = 'http://tv.cnews.ru/'

def clean(name):
	remove=[('<span>',' '),('</span>',' '),('&amp;','&'),('&quot;','"'),('&#39;','\''),('&nbsp;',' '),('&laquo;','"'),('&raquo;', '"'),('&#151;','-'),('<nobr>',''),('</nobr>',''),('<P>',''),('</P>','')]
	for trash, crap in remove:
		name=name.replace(trash, crap)
	return name

def get_list():
	dialog = xbmcgui.Dialog()
	try:
		req = urllib2.Request(target)
		req.add_header('User-Agent', HEADER)
		req.add_header('Referer', referer)
		f = urllib2.urlopen(req)
		a = f.read()
		f.close()
	except:
		dialog.ok('ERROR on GET', 'Cannot GET URL %s' % target)
		return
	stage1 = re.compile('<plaha mov_id="(.+?)" img="(.+?)" head="(.+?)" desc="(.+?)" prog="(.+?)" prog_id="(.+?)" is_iss="(.+?)" iss_head="(.+?)" iss_mov="(.*?)" size_low="(.+?)" size_med="(.+?)" size_high="(.+?)" size_wmv="(.+?)" video_low="(.+?)" video_med="(.+?)" video_high="(.*?)" prog_descr="(.+?)" img_big="(.*?)" iss_id="(.+?)" qview="(.+?)" soit="(.+?)" sub="(.+?)" is_last="(.+?)" descr_med="(.+?)" descr_full="(.*?)" wmv_path="(.*?)" add_date="(.+?)" />', re.DOTALL).findall(a)
	if len(stage1) == 0:
		dialog.ok('ERROR in DATA', 'stage1 not corrected!')
		return
	use_wmv = bool(__settings__.getSetting('use_wmv'))
	quality = int(__settings__.getSetting('quality'))
	for (mov_id, img, head, desc, prog, prog_id, is_iss, iss_head, iss_mov, size_low, size_med, size_high, size_wmv,
	video_low, video_med, video_high, prog_descr, img_big, iss_id, qview, soit, sub, is_last, descr_med,
	descr_full, wmv_path, add_date) in stage1:
		size_low  = int(size_low)
		size_med  = int(size_med)
		size_high = int(size_high)
		size_wmv  = int(size_wmv)
		head = clean(head)
		desc = clean(desc)
		prog = clean(prog)
		iss_head   = clean(iss_head)
		prog_descr = clean(prog_descr)
		descr_med  = clean(descr_med)
		descr_full = clean(descr_full)
		if (use_wmv == True) and (len(wmv_path) > 0):
			play_file = wmv_path
			play_size = size_wmv
		else:
			if quality == 0:
				if (size_low > 0) and (len(video_low) > 0):
					play_size = size_low
					play_file = video_low
				elif (size_med > 0) and (len(video_med) > 0):
					play_size = size_med
					play_file = video_med
				elif (size_high > 0) and (len(video_high) > 0):
					play_size = size_high
					play_file = video_high
				else:
					dialog.ok('ERROR in quality INDEX 0', 'play_size and play_file not corrected!')
					return
			elif quality == 1:
				if (size_med > 0) and (len(video_med) > 0):
					play_size = size_med
					play_file = video_med
				elif (size_high > 0) and (len(video_high) > 0):
					play_size = size_high
					play_file = video_high
				elif (size_low > 0) and (len(video_low) > 0):
					play_size = size_low
					play_file = video_low
				else:
					dialog.ok('ERROR in quality INDEX 1', 'play_size and play_file not corrected!')
					return
			elif quality == 2:
				if (size_high > 0) and (len(video_high) > 0):
					play_size = size_high
					play_file = video_high
				elif (size_med > 0) and (len(video_med) > 0):
					play_size = size_med
					play_file = video_med
				elif (size_low > 0) and (len(video_low) > 0):
					play_size = size_low
					play_file = video_low
				else:
					dialog.ok('ERROR in quality INDEX 2', 'play_size and play_file not corrected!')
					return
			else:
				dialog.ok('ERROR in quality INDEX', 'Unknown quality INDEX %s' % quality)
				return
		post_year  = '1970'
		post_month = '01'
		post_day   = '01'
		ddata = re.compile('([0-9][0-9][0-9][0-9])([0-9][0-9])([0-9][0-9])').findall(add_date)[0]
		if len(ddata) == 3:
			(post_year, post_month, post_day) = ddata
		premiered_aired = post_year + '-' + post_month + '-' + post_day
		track_date = post_day + '.' + post_month + '.' + post_year
		subdata = re.compile('\|(.*?)\|(.*)').findall(sub)[0]
		if len(subdata) == 2:
			(str_data, duration) = subdata
		duration = clean(duration)
		str_data = clean(str_data)
		xbmc.output(head)
		listitem=xbmcgui.ListItem(head, iconImage = img, thumbnailImage = img)
		listitem.setInfo(type = "video", infoLabels = {
			"title":	desc,
			"date":		track_date,
			"studio":	'TV.CNEWS ('+clean(str_data)+')',
			"year":		int(post_year),
			"premiered":	premiered_aired,
			"aired":	premiered_aired,
			"plot":		descr_full,
			"plotoutline":	descr_med,
			"duration":     duration,
			"genre":	prog } )
	        xbmcplugin.addDirectoryItem(handle, play_file, listitem, False)

get_list()

xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_DATE)
xbmcplugin.endOfDirectory(handle)

