#encoding: utf-8
import urllib,urllib2,re,os
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
import xbmcplugin,xbmcaddon,xbmcgui

__version__ = "1.0.0"
__plugin__ = "KinoGovno " + __version__
__author__ = "x86demon"
__url__ = "www.xbmc.com"
__settings__ = xbmcaddon.Addon(id='plugin.video.kinogovno')
__language__ = __settings__.getLocalizedString

THUMBNAIL_PATH = os.path.join(os.getcwd().replace( ";", "" ), 'resources', 'media')
movielogo = os.path.join(THUMBNAIL_PATH, 'movies.png')
gamelogo = os.path.join(THUMBNAIL_PATH, 'games.png')
animelogo = os.path.join(THUMBNAIL_PATH, 'anime.png')
tvlogo = os.path.join(THUMBNAIL_PATH, 'tv.png')
nextIcon = os.path.join(THUMBNAIL_PATH, 'next.png')

def MAIN():
	addDir('Movie Trailers', 'http://kino-govno.com/news/trailers', 'trailers', movielogo)
	addDir('Game Trailers', 'http://kino-govno.com/news/games', 'games', gamelogo)
	addDir('Anime Trailers', 'http://kino-govno.com/news/anime', 'anime', animelogo)
	addDir('Tv-show Trailers', 'http://kino-govno.com/news/tv', 'tv', tvlogo)

									   
def getURL(url):
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
	opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')]
	urllib2.install_opener(opener)
	response = opener.open(url);link=response.read();response.close()
	return link
	

def htmlEntitiesDecode(string):
	return string.replace('&laquo;', '"').replace('&raquo;', '"').replace('&minus;', ' - ')

def INDEX(url, feedType):
	link=getURL(url.replace( " ", "%20" ))
	
	beautifulSoup = BeautifulSoup(link)
	news_titles = beautifulSoup.findAll('a', 'news_head')
	news = beautifulSoup.findAll('div', 'news_text')
	
	titleSearch = re.compile('trailers#\d+?">([^<]+)',re.IGNORECASE + re.DOTALL + re.MULTILINE)
	
	thumbnailsSearch = re.compile(r'flashvars="image=([\w\d:/\.%-]+)',re.IGNORECASE + re.DOTALL + re.MULTILINE)
	filesSearch = re.compile(r'&amp;file=([\w\d:/\.%-]+)',re.IGNORECASE + re.DOTALL + re.MULTILINE)
	qualityLinksSearch = re.compile(r'<a href="([^"]+)" class="link_11" title="([^"]+)"',re.IGNORECASE + re.DOTALL + re.MULTILINE)

	c = 0
	for news_text in news:
		try:
			
			movieTags = news_text.findAll(id=re.compile("video\d+"))
			for movieContainer in movieTags:
				tagStr = str(movieContainer)
				
				postTitle = ''
				try:
					postTitle = news_titles[c].find('span').contents[0].encode('utf8')
				except:
					pass

				title = ''
				try:
					annotation = movieContainer.previousSibling
					titles = titleSearch.findall(str(annotation))
					title = re.sub('(^\s+|\s+$)', '', titles[0])
					if len(title) != len(postTitle):
						title = postTitle + ": " + title
				except:
					title = postTitle
					pass

				thumb = thumbnailsSearch.findall(tagStr)
				file = filesSearch.findall(tagStr)

				if __settings__.getSetting("Quality select") == "true":
					try:
						qualityLinksData = qualityLinksSearch.findall(tagStr)
						if len(qualityLinksData) > 0:
							qualityLinksData.insert(0, [file[0], 'Play'])
							reqUrl = ''
							for row in qualityLinksData:
								reqUrl = reqUrl + '|||' + row[0] + '||' + row[1]

							addDir('[MQ] ' + htmlEntitiesDecode(title), reqUrl.lstrip('|'), 5, thumb[0])
						else:
							addDir('[SQ] ' + htmlEntitiesDecode(title), file[0], 5, thumb[0])
					except:
						pass
				else:
					addDir(htmlEntitiesDecode(title), file[0], 5, thumb[0])
				   
			c = c + 1
		except:
			pass
 
	try:
		nextRegexp = re.compile('(\d+)')
		nextPageNumber = int(nextRegexp.findall(url)[0]) + 15
	except:
		nextPageNumber = 15

	addDir('[Older entries]', 'http://www.kino-govno.com/news/%s/%d' % (feedType, nextPageNumber), feedType, nextIcon)


def VIDEO(name,url):
	if url.find('||') != -1:
		data = url.split('|||')
		qualitiesData = []
		for dataRow in data:
			qualitiesData.append(dataRow.split('||'))
		
		listVariables = []
		for url, qName in qualitiesData:
			listVariables.append(qName)
		
		dia = xbmcgui.Dialog()
		selected = dia.select('Choose quality', listVariables)
		url = qualitiesData[selected][0]
	
	if url.find('http://www.kino-govno.com/kgfix.php') != -1:
		url = re.sub(re.compile(r'http://www.kino-govno.com/kgfix.php%3Fnum%3D\d+%26url%3D',re.IGNORECASE + re.DOTALL + re.MULTILINE), '', url)
		url = re.sub(re.compile(r'http://www.kino-govno.com/kgfix.php?num=\d+&amp;url=',re.IGNORECASE + re.DOTALL + re.MULTILINE), '', url)

	url = urllib.unquote(url)
	url = url.replace('&amp;', '&')
	
	addLink(name,url)
		
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


def addLink(name,url):
	#TODO: Download need fixing
	def Download(url,dest):
			dp = xbmcgui.DialogProgress()
			dp.create("KinoGovno Download","Downloading File",url)
			urllib.urlretrieve(url,dest,lambda nb, bs, fs, url=url: _pbhook(nb,bs,fs,url,dp))
	def _pbhook(numblocks, blocksize, filesize, url=None,dp=None):
			try:
					percent = min((numblocks*blocksize*100)/filesize, 100)
					print percent
					dp.update(percent)
			except:
					percent = 100
					dp.update(percent)
			if dp.iscanceled():
					dp.close()
	if __settings__.getSetting("Download Flv") == "true":
			dialog = xbmcgui.Dialog()
			path = dialog.browse(3, 'Choose Download Directory', 'files', '', False, False, '')
			filename = xbmc.makeLegalFilename(path+name+'.flv')
			Download(url,filename)
	thumbnail = xbmc.getInfoImage("ListItem.Thumb")
	liz=xbmcgui.ListItem(name,iconImage="DefaultVideo.png", thumbnailImage=thumbnail)
	liz.setInfo( type="Video", infoLabels={ "Title": name } )
	try:
		if __settings__.getSetting("dvdplayer") == "true":
			xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(url, liz)
		else:
			xbmc.Player().play(url, liz)
	except:
		dialog = xbmcgui.Dialog()
		dialog.ok('Script failed', 'Failed to play stram ' + name)
		

def addDir(name,url,mode,iconimage):
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
	ok=True
	liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
	liz.setInfo( type="Video", infoLabels={ "Title": name } )
	if __settings__.getSetting("Show fanart") == "true" and mode == 5:
		liz.setProperty('fanart_image',iconimage)
	xbmcplugin.setContent( handle=int( sys.argv[ 1 ] ), content="movies" )
	if mode==5:
		ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
	else: ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
	return ok

params=get_params()
url=None
name=None
mode=None

try:
	url=urllib.unquote_plus(params["url"])
except:
	pass
try:
	name=urllib.unquote_plus(params["name"])
except:
	pass
try:
	mode=params["mode"]
except:
	pass

if mode==None or url==None or len(url)<1:
	MAIN()
elif mode != "5":
	INDEX(url, mode)
else:
	VIDEO(name,url)

xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
xbmcplugin.endOfDirectory(int(sys.argv[1]))
