class xbmcplugin1(object):
	@staticmethod
	def addDirectoryItem(handle, url, listitem, isFolder=False):
		print listitem.infoLabels
		print listitem.title + ' - ' + url

	@staticmethod
	def endOfDirectory(bla):
		pass
		
class xbmcgui1(object):
	@staticmethod
	def ListItem(title, iconImage='DefaultVideo.png', thumbnailImage=''):
		obj = xbmcgui1()
		obj.title = title
		return obj

	def setInfo(self, type='Video', infoLabels={} ):
		self.infoLabels = infoLabels