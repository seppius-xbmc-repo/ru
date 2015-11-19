#!/usr/bin/python
# -*- coding: utf-8 -*-

#  Copyright (C) 2015 KodeKarnage
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
#


'''
******************************* How To Add New Advanced Settings *******************************

Settings with unique labels can be added easily.

The commented-out sections of the settings.xml are used to create an advancedsettings.xml template, that contains all the settings
that can be set using the addon.

To add a new setting to an existing sub-group (such as network or video) simply replace "newsettingname" in this pattern and
insert it into the settings.xml in the approriate group:

	<!--newsettingname></newsettingname-->
	<setting default="false" id="newsettingnamebool" label="Activate newsettingname" type="bool"/>
	<setting default="0" enable="eq(-1,true)" id="newsettingname" label="newsettingname" subsetting="true" type="number"/>

The first boolean line determines whether the setting below it is shown AND whether it gets added to the new advancedsettings.xml.
The second setting line can be constructed any way you like. http://kodi.wiki/view/Add-on_settings

If you need to add a setting in a new sub group, then simply insert the heading and closing tags:

	<!--newgroup_HEADING-->
		<!--newsettingname></newsettingname-->
		<setting default="false" id="newsettingnamebool" label="Activate newsettingname" type="bool"/>
		<setting default="0" enable="eq(-1,true)" id="newsettingname" label="newsettingname" subsetting="true" type="number"/>
	<!--/newgroup_HEADING-->

If you need to create a sub-sub-group, then simply nest the new group within two headings:

	<!--newgroup1_HEADING-->
		<!--newgroup2_HEADING-->
			<!--newsettingname></newsettingname-->
			<setting default="false" id="newsettingnamebool" label="Activate newsettingname" type="bool"/>
			<setting default="0" enable="eq(-1,true)" id="newsettingname" label="newsettingname" subsetting="true" type="number"/>
		<!--/newgroup2_HEADING-->
	<!--/newgroup1_HEADING-->

******************************* Addon Logic *******************************

On Open of addon:
	read the current advancedsettings.xml into a dict called CAS

	extract the mysql info from the CAS and import directly to addon settings

	construct ADVS from resources/settings.xml 
		read settings.xml, remove non-commented out lines
		remove commentings, set all the values as None
		save as an xml, convert that xml to a dict called ADVS

	update ADVS with the values from CAS, ignoring the items that are in the CAS but not in ADVS (like the mysql stuff)

	cycle through ADVS (through to non-dict values)
		if value is None, then set related bool setting to false [setSetting(key+'bool',true)]
		else set the bool to True and enter the value [setSetting(key, value)]

	open addon settings, wait for them to be closed

On Close of addon settings 

	cycle through all items in ADVS,
		check keys for addon setting bool is True - [getSetting(key+'bool')]
			if true, update CAS with the relevant setting value
			if false, remove the item from CAS
		add in the MySQL info into ADVS from the addon settings (if deactivated then add blank dict with Nones for values)

	copy values from CAS that arent found in ADVS into ADVS
			
	unparse ADVS into a new the advancedsettings.xml file

	insert the header line inthe the advancedsettings.xml file
'''


# Standard Modules
import os
import xmltodict

# KODI modules
import xbmc
import xbmcaddon

__addon__        = xbmcaddon.Addon()
__addonid__      = __addon__.getAddonInfo('id')
__setting__      = __addon__.getSetting
lang             = __addon__.getLocalizedString

scriptPath       = __addon__.getAddonInfo('path')
user_data = xbmc.translatePath( "special://userdata")

def log(message, label = ''):
	logmsg       = '%s : %s - %s ' % (__addonid__, label, message)
	xbmc.log(msg = logmsg)


class Main(object):

	def __init__(self):

		# file locations
		self.existing_AS_file 			= os.path.join(user_data,'advancedsettings.xml')
		self.template_source_file		= os.path.join(scriptPath,'resources','settings.xml')

		# current advanced settings dict
		self.CAS = self.read_existing_AS_file()

		# load the MySQL information directly from the CAS into the local addon settings
		# we will leave this out of the ADVS for the moment
		# mysql uses the same keyword for the video and music database sections
		self.CAS = self.MySQL_special_handling_from_CAS(self.CAS)

		# dict of all possible settings the addon can control, values are all set to None
		self.ADVS = self.create_ADVS_dict()

		# copy the settings in the CAS over to the ADVS, ignoring any settings not found in ADVS
		self.ADVS = self.update_dicts(self.ADVS, self.CAS)

		# write the ADVS settings to local addon settings file
		self.update_addon_settings(self.ADVS)

		__addon__.openSettings()

		# clean the ADVS of deactivated settings (change the values to None), load the new settings into it
		self.ADVS = self.check_bools(self.ADVS)

		# extract the mysql information from the local addon and insert it into the ADVS
		self.ADVS = self.MySQL_special_handling_to_ADVS(self.ADVS)

		# fill out the ADVS with the items in the CAS that aren't found in ADVS
		self.ADVS = self.fill_out(self.ADVS, self.CAS)

		# remove the items from ADVS where the value is None
		self.ADVS = self.remove_Nones(self.ADVS)

		self.print_dict(self.ADVS)

		# ADVS now represents the values the user set in the Settings screen and the items in the original advancedsettings.xml
		# that are NOT found in the addons settings

		if self.ADVS:
			# write the ADVS into the existing advancedsettings.xml
			with open(self.existing_AS_file, 'w') as f:
				xmltodict.unparse(input_dict=dict(self.ADVS), output=f, pretty=True)


	def print_dict(self, dictionary):
		''' log the contents of the ADVS dictionary '''

		for k, v in dictionary.iteritems():
			if isinstance(v, dict):
				log('-->  %s' % k)
				self.print_dict(v)
			else:
				log('%s   %s' % (k, v))


	def remove_Nones(self, dictionary):
		''' Removes item pairs from the dictionary where the value is None. '''

		safe_dict = dictionary.copy()
		for k, v in safe_dict.iteritems():
			if isinstance(v, dict):
				dictionary[k] = self.remove_Nones(dictionary[k])
				if not dictionary[k]:
					del dictionary[k]
			else:
				if v is None:
					del dictionary[k]

		return dictionary


	def check_bools(self, dictionary):
		''' Check the local addons settings for whether the individual setting is active. If not, replace the value with None.
			if it is active, then extract the new value from the local settings.
		'''

		safe_dict = dictionary.copy()
		for k, v in safe_dict.iteritems():
			if isinstance(v, dict):
				dictionary[k] = self.check_bools(dictionary[k])
			else:
				if __setting__(k + 'bool') == 'false':
					dictionary[k] = None
				else:
					dictionary[k] = __setting__(k)

		return dictionary


	def update_addon_settings(self, dictonary):
		''' Extracts the settings from the dicitonary provided and loads them into the local addon settings.'''

		for k, v in dictonary.iteritems():
			if isinstance(v, dict):
				self.update_addon_settings(v)
			else:
				if v is None:
					__addon__.setSetting(k + 'bool', 'false')
				else:
					__addon__.setSetting(k + 'bool', 'true')
					__addon__.setSetting(k, v)


	def read_existing_AS_file(self):
		''' Reads the existing advancedsettings.xml and returns a dict with the values.'''

		loc = self.existing_AS_file

		null_doc = {'advancedsettings': {}}

		log('advancedsettings file exists = %s' % os.path.isfile(loc))

		if os.path.isfile(loc):

			with open(loc, 'r') as f:
				lines = f.readlines()
			
			if not lines:
				log('advancedsettings.xml file is empty')
				return null_doc

			# check for first line

			# if '<?' in lines[0]:
			# 	lines = [x.strip() for x in lines[1:]]

			# doc = ''.join(lines)

			with open(loc, 'r') as f:
				doc = xmltodict.parse(f)

			return doc

		else:
			return null_doc


	def create_ADVS_dict(self):
		''' Creates a template xml that contains all the settings that are possible to set. '''

		new_lines = []

		log('template source file exists: %s' % os.path.isfile(self.template_source_file))

		with open(self.template_source_file, 'r') as f:
			lines = f.readlines()

			for line in lines:

				if '<!--' in line:
					new_lines.append(line.replace("_HEADING",'').replace('<!--','<').replace('-->','>').strip())

		doc = ''.join(new_lines)	

		return self.set_all_values_to_None(xmltodict.parse(doc))


	def set_all_values_to_None(self, dictionary):
		''' Takes a dictionary and sets all the values to None. Looks through nested dictionaries and only changes end values.'''

		safe_dict = dictionary.copy()
		for k, v in safe_dict.iteritems():
			if isinstance(v, dict):
				dictionary[k] = self.set_all_values_to_None(dictionary[k])
			else:
				dictionary[k] = None

		return dictionary


	def update_dicts(self, dest_dict, source_dict):
		''' Takes two dictionaries and updates the first with values from the second but retains the data in the destination,
			if it is not in the source. Dicts that are values themselves are given a similar treatment, rather than being overwritten'''

		safe_dict = dest_dict.copy()
		for k, v in safe_dict.iteritems():

				if k in source_dict:
					if isinstance(v, dict):
						dest_dict[k] = self.update_dicts(v, source_dict[k])
					else:
						dest_dict[k] = source_dict[k]

		return dest_dict


	def fill_out(self, dest_dict, source_dict):
		''' Fills out the dest dictionary with the items in the source dict that aren't in the dest. Items in the dest_dict that
			aren't found in the source_dict are left in place unchanged.
		'''

		for k, v in source_dict.iteritems():
			if k in dest_dict:
				if isinstance(v, dict):
					dest_dict[k] = self.fill_out(dest_dict[k], source_dict[k])
				else:
					pass
			else:
				dest_dict[k] = source_dict[k]

		return dest_dict


	def MySQL_special_handling_from_CAS(self, dictionary):
		''' Reads the MySQL information from the CAS and loads it into the local addon '''

		video = dictionary.get('advancedsettings', {}).get('videodatabase', {})
		music = dictionary.get('advancedsettings', {}).get('musicdatabase', {})

		sql_subitems = ['name', 'type', 'host', 'port', 'user', 'pass']

		if video:
			__addon__.setSetting('vd_toggle', 'true')

			for sql_item in sql_subitems:
				if sql_item in video:
					__addon__.setSetting('vd_' + sql_item, video[sql_item])
				else:
					log('MySQL videodatabase item %s not found', sql_item)

		if music:
			__addon__.setSetting('mu_toggle', 'true')

			for sql_item in sql_subitems:
				if sql_item in music:
					__addon__.setSetting('mu_' + sql_item, music[sql_item])
				else:
					log('MySQL musicdatabase item %s not found', sql_item)

		return dictionary


	def MySQL_special_handling_to_ADVS(self, dictionary):
		''' Reads the MySQL settings from the local addon, and writes them directly into the ADVS. 
			This must be done AFTER the check for deactivated settings and BEFORE the unmatched items from CAS are brought into
			the ADVS.
		'''

		sql_subitems = ['name', 'type', 'host', 'port', 'user', 'pass']

		video = {}
		music = {}

		for sql_item in sql_subitems:
			video[sql_item] = __setting__('vd_' + sql_item) if __setting__('vd_toggle') == 'true' else None
			music[sql_item] = __setting__('mu_' + sql_item) if __setting__('mu_toggle') == 'true' else None

		sub_dict = dictionary.get('advancedsettings',{})

		sub_dict['videodatabase'] = video
		sub_dict['musicdatabase'] = music

		return {'advancedsettings': sub_dict}



if __name__ == "__main__":
	Main()


''' Example of MySQL entries in the advancedsettings.xml '''
'''
<advancedsettings>
	<videodatabase>
		<type>mysql</type>
		<host>***.***.***.***</host>
		<port>3306</port>
		<user>kodi</user>
		<pass>kodi</pass>
	</videodatabase> 
	<musicdatabase>
		<type>mysql</type>
		<host>***.***.***.***</host>
		<port>3306</port>
		<user>kodi</user>
		<pass>kodi</pass>
	</musicdatabase>
	<videolibrary>
		<importwatchedstate>true</importwatchedstate>
		<importresumepoint>true</importresumepoint>
	</videolibrary>
</advancedsettings>
'''

''' Example of an ADVS '''
Example = { 
			'advancedsettings': { 
				'edl': { 
						'commbreakautowait': None,
						'commbreakautowind': None,
						'maxcommbreakgap': None,
						'maxcommbreaklength': None,
						'mergeshortcommbreaks': None,
						'mincommbreaklength': None,
						},
				'epg': {
						'activetagcheckinterval': None,
						'displayincrementalupdatepopup': None,
						'displayupdatepopup': None,
						'lingercleanupintervaltime': None,
						'lingertime': None,
						'retryinterruptedupdateinterval': None,
						'updatecheckinterval': None,
						'updateemptytagsinterval': None,
						},
				'karaoke': { 
						'alwaysreplacegenre': None,
						'autoassignstartfrom': None,
						'nextsongpopuptime': None,
						'nocdgbackground': None,
						'storedelay': None,
						'syncdelaycdg': None,
						'syncdelaylrc': None,
						},
				'masterlock': { 
						'automastermode': None,
						'loginlock': None,
						'maxretries': None,
						'startuplock': None,
						},
				'mymovies': { 
						'categoriestogenres': None,
						},
				'network': { 
						'buffermode': None,
						'cachemembuffersize': None,
						'curlclienttimeout': None,
						'curllowspeedtime': None,
						'httpproxypassword': None,
						'httpproxyusername': None,
						'readbufferfactor': None,
						},
				'pvr': { 
						'autoscaniconsuserset': None,
						'cacheindvdplayer': None,
						'channeliconsautoscan': None,
						'infotoggleinterval': None,
						'maxvideocachelevel': None,
						'minvideocachelevel': None,
						'numericchannelswitchtimeout': None,
						'timecorrection': None,
						},
				'slideshow': { 
						'blackbarcompensation': None,
						'panamount': None,
						'zoomamount': None,
						},
				'tuxbox': { 
						'audiochannelselection': None,
						'defaultrootmenu': None,
						'defaultsubmenu': None,
						'epgrequesttime': None,
						'pictureicon': None,
						'submenuselection': None,
						'zapwaittime': None,
						},
				'video': { 
						'audiodelayrange': None,
						'blackbarcolour': None,
						'defaultplayer': None,
						'fullscreenonmoviestart': None,
						'ignorepercentatend': None,
						'ignoresecondsatstart': None,
						'percentseekbackward': None,
						'percentseekbackwardbig': None,
						'percentseekforward': None,
						'percentseekforwardbig': None,
						'playcountminimumpercent': None,
						'smallstepbackseconds': None,
						'subsdelayrange': None,
						'timeseekbackward': None,
						'timeseekbackwardbig': None,
						'timeseekforward': None,
						'timeseekforwardbig': None,
						'usetimeseeking': None,
						},
				'videolibrary': {
						'allitemsonbottom': None,
						'backgroundupdate': None,
						'cleanonupdate': None,
						'dateadded': None,
						'exportautothumbs': None,
						'hideallitems': None,
						'hideemptyseries': None,
						'hiderecentlyaddeditems': None,
						'importresumepoint': None,
						'importwatchedstate': None,
						'itemseparator': None,
						'recentlyaddeditems': None,
						},
				'videoscanner': {
						'alwaysontop': None,
						'controllerdeadzone': None,
						'enablemultimediakeys': None,
						'fanartres': None,
						'fullscreen': None,
						'ignoreerrors': None,
						'imageres': None,
						'packagefoldersize': None,
						'playlistretries': None,
						'playlisttimeout': None,
						'remotedelay': None,
						'remoterepeat': None,
						'showexitbutton': None,
						'splash': None,
						'useddsfanart': None,
						},
				'window': { 
						'height': None,
						'width': None,
						}
					}
				}
