

import urllib, sys, os, re, time
import xbmcaddon, xbmcplugin, xbmcgui, xbmc
from traceback import print_exc


addonname= "Virtual International Keyboard"
addonid  = "script.module.intkeyboard"
addon    = xbmcaddon.Addon(id=addonid)
language = addon.getLocalizedString
path     = xbmc.translatePath( addon.getAddonInfo('path') )
profile  = xbmc.translatePath( addon.getAddonInfo('profile') )
icondir  = os.path.join( path,'resources','icons' )
skindir  = os.path.join( path,'resources','skins' )

XBMC_SKIN  = xbmc.getSkinDir()
BASE_RESOURCE_PATH = os.path.join( path, 'resources', 'lib' )
sys.path.append (BASE_RESOURCE_PATH)
settings = addon
COMMBUTONS=['en','ru','shift','del','clear','caps','enter','space','cancel']

lines=[['ru','1','2','3','4','5','6','7','8','9','0','-','=','del'],
	['shift','q','w','e','r','t','y','u','i','o','p','[',']','clear'],
	['caps','a','s','d','f','g','h','j','k','l',';','`','_','enter'],
	['space','z','x','c','v','b','n','m',',','.','!',' ','@'],'cancel']
	
lines_ru=[['en','1','2','3','4','5','6','7','8','9','0','-','=','del'],
	['shift','й','ц','у','к','е','н','г','ш','щ','з','х','ъ','clear'],
	['caps','ф','ы','в','а','п','р','о','л','д','ж','э','\\','enter'],
	['space','я','ч','с','м','и','т','ь','б','ю','.',' ','@','cancel']]

#curr_lines=lines_ru

class GUI(xbmcgui.WindowXMLDialog):

	def __init__(self, *args, **kwargs):
		self.text=''
		self.lns=lines_ru
		pass
	
	def labelezation(self,liness):
		id=3001
		y=1
		while (y<5):
			n=1
			while (n<15):
				self.label = self.getControl(3001+(n-1)+(y-1)*14)
				self.label.setLabel(liness[y-1][n-1])
				n=n+1
				self.label.setVisible(True)
			y=y+1
	
	def onInit(self):
		#xbmc.executebuiltin('ReplaceWindow(progressdialog)')
		#xbmc.executebuiltin('Dialog.Close(progressdialog)')
		#ctr=self.getControl(10101)
		#ctr.close()
		print 'lalalalal'
		st_x=250
		st_y=250
		y=1
		while (y<5):
			n=1
			while (n<15):
				self.label = xbmcgui.ControlButton(st_x+n*50, st_y+y*50, 50, 50, self.lns[y-1][n-1])
				if n==1: 
					self.label.setWidth(100)
					self.label.setPosition(st_x, st_y+y*50)
				if n==14: 
					self.label.setWidth(100)
					self.label.setPosition(st_x+n*50, st_y+y*50)
				self.label.setVisible(False)
				self.addControl(self.label)
				#print self.label.getId()
				n=n+1
			y=y+1
			
		id=3001
		y=1
		while (y<5):
			n=1
			while (n<15):
				self.label = self.getControl(3001+(n-1)+(y-1)*14)
				if n>1: self.label.controlLeft(self.getControl(3001+(n-1)+(y-1)*14-1))
				if y>1: self.label.controlUp(self.getControl(3001+(n-1)+(y-2)*14))
				if n<14: self.label.controlRight(self.getControl(3001+(n-1)+(y-1)*14+1))
				if y<4: self.label.controlDown(self.getControl(3001+(n-1)+(y)*14))
				#print self.label.getId()
				n=n+1
				self.label.setVisible(True)
			y=y+1
		pass
		# Put your List Populating code/ and GUI startup stuff here
 
	def onAction(self, action):
		self.label.setText(self.text)
		# Same as normal python Windows.
		pass
 
	def onClick(self, controlID):
		#labl=xbmcgui.ControlLabel()
		#labl.x=500
	#	labl.y=500
		#labl.width=50
	#	labl.height=50
		#labl.label='Enter'
		if self.getControl(controlID).getLabel() not in COMMBUTONS:
			self.label = self.getControl(3000)
			self.text=self.text+self.getControl(controlID).getLabel()
			self.label.setText(self.text)
		if self.getControl(controlID).getLabel() == 'space' : #del
			self.text=self.text+' '
		
		if self.getControl(controlID).getLabel() == 'en' : #del
			self.lns=lines
			self.labelezation(lines)
		if self.getControl(controlID).getLabel() == 'ru' : #del
			self.lns=lines_ru
			self.labelezation(lines_ru)
		if self.getControl(controlID).getLabel() == 'ru' : #del
			self.text=self.text+' '
		
		if self.getControl(controlID).getLabel() == 'clear' : #del
			self.text=''
		#print self.getControl(controlID).getLabel()
		if self.getControl(controlID).getLabel() == 'del' : #del
			self.text=self.text[0:(len(self.text)-1)]
		if self.getControl(controlID).getLabel() == 'enter' : #Exit
			self.close()
		if self.getControl(controlID).getLabel() == 'cancel' : #Enter
			self.close()

		self.label.setText(self.text)
		pass
		
	def onFocus(self, controlID):
		self.label.setText(self.text)
		pass


def getRuText():
	ui = GUI("new.xml",path)
	#ui.show()
	ui.doModal()
	#print ui.text.encode('utf-8')
	try:
		out= ui.text.encode('utf-8')
	except: out= ui.text
	del ui
	return out