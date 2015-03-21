# declare file encoding
# -*- coding: utf-8 -*-

#  Copyright (C) 2014 Lamkin666
#
#  This Program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This Program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with XBMC; see the file COPYING.  If not, write to
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#  http://www.gnu.org/copyleft/gpl.html

import sys
import xbmc
import RussianKey
import xbmcgui
import xbmcaddon



_addon_ = xbmcaddon.Addon("service.RussianKeyboard")	
if sys.version_info >=  (2, 7):
	import json
else:
	import simplejson as json

def json_query(query):
	xbmc_request = json.dumps(query)
	result = xbmc.executeJSONRPC(xbmc_request)
	result = unicode(result, 'utf-8', errors='ignore')
	return json.loads(result)

class keyboard_monitor:

	def __init__(self):
		self._daemon()

	def push_string(self, count, line_num):
			        self.string1 = self.process_file()
				self.ac = True
				self.req = json.dumps({"id": "0", "jsonrpc":"2.0", "method":"Input.SendText", "params":{"text":self.string1, "done":self.ac}})
				xbmc.executeJSONRPC(self.req)

	def process_file(self):
                                keyboard = RussianKey.Keyboard('', '')
	                        keyboard.doModal()
	                        output = keyboard.getText()	
		                return output

	def _daemon(self):
		#this will run constantly
		while (not xbmc.abortRequested):
			xbmc.sleep(500)
			self.count = 0
			self.line_num = 0
			if xbmc.getCondVisibility('Window.IsActive(virtualkeyboard)'):            
                                
				self.push_string(self.count, self.line_num)

if (__name__ == "__main__"):
	kbm = keyboard_monitor()




