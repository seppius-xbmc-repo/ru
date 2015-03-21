#!/usr/bin/python
import sys,urllib2,urllib,re,xbmcplugin,xbmcgui
def get_params(paramstring):
    param=[]
    if len(paramstring)>=2:
        params=paramstring
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
#------------------------------------------------------------------------------------------
def showMessage(heading, message, times = 20000):
    xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)'%(heading, message, times))
#------------------------------------------------------------------------------------------
def getPage(url,ref=None):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    req.add_header('Accept', '*/*')
    req.add_header('Accept-Language', 'ru-RU')
    req.add_header('Referer',             ref)
    try:
        response = urllib2.urlopen(req)
        html=response.read()
        response.close()
        return html
    except Exception, e:
        showMessage('HTTP Error','Error getting page '+url)
        return ''
#------------------------------------------------------------------------------------------
def unescape(s):
    s = s.replace("&lt;", "<")
    s = s.replace("&gt;", ">")
    s = s.replace("&quot;", '"')
    s = s.replace("&hellip;", '...')
    # this has to be last:
    s = s.replace("&amp;", "&")
    return s
#------------------------------------------------------------------------------------------
def Search(reg,s):
    m=re.search(reg,s)
    if m==None:
        return '';
    else:
        return m.group(1)
#------------------------------------------------------------------------------------------
def ListChannels():
    i=0
    for k in kanals:
        listItem = xbmcgui.ListItem(k[0],iconImage=k[2],thumbnailImage=k[2])
        url = myname + '?mode=sub&site='+str(i)
        xbmcplugin.addDirectoryItem(thisPlugin,url,listItem,True)
        i=i+1
    xbmcplugin.endOfDirectory(thisPlugin)
#------------------------------------------------------------------------------------------
def ListSub(site):
    i=int(site)
    for sub in kanals[i][3]:
        name=sub.split(':')[0]
        menu_id=sub.split(':')[1]
        url = myname + '?mode=page&site='+site+'&page='+menu_id+'&sort=0'
        listItem = xbmcgui.ListItem(name)
        xbmcplugin.addDirectoryItem(thisPlugin,url,listItem,True)
    xbmcplugin.endOfDirectory(thisPlugin)
#------------------------------------------------------------------------------------------
def ListPage(site,page,sort):
    if sort=='0':
        listItem = xbmcgui.ListItem('ПОПУЛЯРНЫЕ')
        url = myname + '?mode=page&site='+site+'&page='+page+'&sort=1'
        xbmcplugin.addDirectoryItem(thisPlugin,url,listItem,True)
        listItem = xbmcgui.ListItem('СПИСОК')
        url = myname + '?mode=page&site='+site+'&page='+page+'&sort=2'
        xbmcplugin.addDirectoryItem(thisPlugin,url,listItem,True)
    
    k=kanals[int(site)]
    url=k[1]+'index/'
    if not page=='0':
        url=url+'menu_id/'+page+'/'
    url=url+'sort_by/'+sort
    html=getPage(url)
    if sort=='2':
        match=re.compile('<li class="item ">([.\s\S]*?)</li>').findall(html)
    else:
        match=re.compile('<li class="item">([.\s\S]*?)</li>').findall(html)
    for item in match:
        if '${url}' not in item:
            ListItem(site,item)
    xbmcplugin.endOfDirectory(thisPlugin)
#------------------------------------------------------------------------------------------
def ListItem(site,item):
    prog=unescape(Search('<span class="overlay"><span>(.+?)</span>',item))
    title=unescape(Search('<a class="title".+?>(.+?)</a>',item))
    duration=Search('<span class="duration">(.+?)</span>',item)
    if prog=='':
        name=title
    else:
        name=prog+'. '+title
    thumb=Search('<img src="(.+?)"',item)
    link=Search('<a class="title" href="(.+?)"',item)+'/'
    brand=Search('/brand_id/(.*?)/',link)
    cid=Search('/video_cid/(.*?)/',link)
    if not cid=='':
        return
    iD=Search('/video_id/(.*?)/',link)
    #if iD=='':
    #    return
    url=myname+'?mode=serial&site='+site+'&page='+ brand+'&sort='+iD
    listItem = xbmcgui.ListItem(name,thumbnailImage=thumb)
    xbmcplugin.addDirectoryItem(thisPlugin,url,listItem,True)
#------------------------------------------------------------------------------------------
def ListSerial(site,brand,iD):
    url=kanals[int(site)][1]+'show/brand_id/'+brand
    if not iD=='':
        url=url+'/video_id/'+iD
    html=getPage(url)
    if not html.find('Смотрите также')==-1:
        listItem = xbmcgui.ListItem('СМОТРИТЕ ТАКЖЕ')
        link=myname+'?mode=more&site='+site+'&page='+ brand+'&sort='+iD
        xbmcplugin.addDirectoryItem(thisPlugin,link,listItem,True) 
        
    name=unescape(Search('<meta property="og:title" content="(.+?)"',html))
    img=Search('<meta property="og:image" content="(.+?)"',html)
    url=myname+'?mode=play&site='+site+'&page='+ brand+'&sort='+iD
    listItem = xbmcgui.ListItem(name,thumbnailImage=img)
    listItem.setInfo( type="Video", infoLabels={ "Title": name} )
    listItem.setProperty('IsPlayable', 'true')
    listItem.select(True)
    xbmcplugin.addDirectoryItem(thisPlugin,url,listItem)
    if html.find('Другие ')==-1:
        xbmcplugin.endOfDirectory(thisPlugin)
        return
    div=Search('<div id="viewtype_picture"([.\s\S]*)',html)
    match=re.compile('(<li class="item .*?">[.\s\S]*?</li>)').findall(div)
    for item in match:
        cls=Search('class="(item .*?)"',item)
        if cls=='item item_active':
            continue
        cid=Search('/video_cid/(.*?)/',item)
        if not cid=='':
            continue        
        name=Search('<a class="name".+?>(.+?)</a>',item)
        img=Search('data-original="(.+?)"',item)
        brand=Search('brand_id/(.+?)/',item)
        iD=Search('video_id/(.+?)/',item)
        url=myname+'?mode=play&site='+site+'&page='+ brand+'&sort='+iD
        listItem = xbmcgui.ListItem(name,thumbnailImage=img)
        listItem.setInfo( type="Video", infoLabels={ "Title": name} )
        listItem.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(thisPlugin,url,listItem) 
    xbmcplugin.endOfDirectory(thisPlugin)    
#------------------------------------------------------------------------------------------
def Play(site,brand,iD):
    url=kanals[int(site)][1]+'show/brand_id/'+brand+'/video_id/'+iD
    #print url
    html=getPage(url)
    #desc=unescape(Search('<meta property="og:description" content="(.+?)"',html))
    name=unescape(Search('<meta property="og:title" content="(.+?)"',html))
    thumb=Search('<meta property="og:image" content="(.+?)"',html)
    link=Search('<iframe src="(.+?)"',html)
    vlink=getVLink(link,url)
    if vlink=='':
        vlink=getVLink2(link)
        if vlink=='':
            showMessage('Video not found',url,15000)
            return
    i = xbmcgui.ListItem(path = vlink,thumbnailImage=thumb)
    i.setInfo( type="Video", infoLabels={ "Title": name} )
    i.setProperty('IsPlayable', 'true')
    xbmcplugin.setResolvedUrl(thisPlugin, True, i)
    #xbmc.Player().play(link, i)
#------------------------------------------------------------------------------------------
def getVLink2(link):
    vid=Search('video_id/(\d+?)/',link)
    print 'vid: '+vid
    if vid=='':
        return ''
    newlink='http://cdn1.vesti.ru/_cdn_auth/secure/v/vh/mp4/high/'+vid[0:3]+'/'+vid[3:6]+'.mp4?auth=vh&vid='+vid
    if touch(newlink):
        return newlink
    else:
        return newlink.replace('high','medium')
#------------------------------------------------------------------------------------------
def getVLink(link,ref):
    html=getPage(link,ref)
    vLink=Search('"video":"(http:.*?)"',html)
    if vLink=='':
        return ''
    vLink=vLink.replace('\/','/')
    hlink=vLink.replace('medium','high')
    if touch(hlink):
        return hlink
    else:
        return vLink
#------------------------------------------------------------------------------------------
def touch(url):
    req = urllib2.Request(url)
    try:
        res=urllib2.urlopen(req)
        res.close()
        return True
    except:
        return False
#------------------------------------------------------------------------------------------
def ListMore(site,brand,iD):
    url=kanals[int(site)][1]+'show/brand_id/'+brand
    if not iD=='':
        url=url+'/video_id/'+iD
    html=getPage(url)
    match=re.compile('<li class="item">([.\s\S]*?)</li>').findall(html)
    print len(match)
    for item in match:
        name=unescape(Search('<a class="name".+?>(.+?)</a>',item))
        thumb=Search('<img src="(.+?)"',item)
        link=Search('<a href="(.+?)"',item)+'/'
        brand=Search('/brand_id/(.*?)/',link)
        iD=Search('/video_id/(.*?)/',link)
        url=myname+'?mode=serial&site='+site+'&page='+ brand+'&sort='+iD
        listItem = xbmcgui.ListItem(name,thumbnailImage=thumb)
        xbmcplugin.addDirectoryItem(thisPlugin,url,listItem,True)
    xbmcplugin.endOfDirectory(thisPlugin)
    
#------------------------------------------------------------------------------------------    
kanals=[
    ['Россия 1','http://russia.tv/video/','http://russia.tv/i/logo/standart-russia1.png',['Все:0','Сериалы:265','Документалистика:266','Художественные:267','Передачи:268','Музыка и юмор:269','Новости:282']],
    ['Россия 2','http://russia2.tv/video/','http://russia2.tv/i/logo/standart-russia2.png',['Все:0','Кино:462','Наука:302','Путешествия:303','Спорт:304','Документалистика:306','Вести-Спорт:422','Передачи:305']],
    ['Культура','http://tvkultura.ru/video/','http://tvkultura.ru/i/logo/standart-russiak.png',['Все:0','Документалистика:522','Портреты:523','Передачи:524','Новости:525','Интервью:526','Образование:527']]
    ]

mode=''
site=''
page=''
sort=''

myname=sys.argv[0]
thisPlugin = int(sys.argv[1])
params = get_params(sys.argv[2])


try:
    mode  = urllib.unquote_plus(params["mode"])
    site  = urllib.unquote_plus(params["site"])
    page  = urllib.unquote_plus(params["page"])
    sort = urllib.unquote_plus(params["sort"])
except:
    pass



if mode == '':
    ListChannels()
elif mode == 'sub':
    ListSub(site)
elif mode == 'page':
    ListPage(site,page,sort)
elif mode == 'serial':
    ListSerial(site,page,sort)
elif mode == 'more':
    ListMore(site,page,sort)    
elif mode == 'play':
    Play(site,page,sort)
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        

