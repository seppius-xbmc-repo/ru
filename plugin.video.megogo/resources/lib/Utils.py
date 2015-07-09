# -*- coding: utf-8 -*-
#############################################################################
#
# Copyright (C) 2015 Studio-Evolution
#
# Utilites for MEGOGO.NET on XBMC
#
#############################################################################

import xbmc, xbmcgui, xbmcaddon, xbmcvfs
import urllib2, os
import megogo2xbmc

addon			= xbmcaddon.Addon()
addon_id		= addon.getAddonInfo('id')
addon_name		= addon.getAddonInfo('name')
addon_icon		= addon.getAddonInfo('icon')
addon_fanart	= addon.getAddonInfo('fanart')
addon_path		= addon.getAddonInfo('path').decode("utf-8")
addon_version	= addon.getAddonInfo('version')
language		= addon.getLocalizedString
unknown_person	= os.path.join(addon_path, 'resources', 'skins', 'Default', 'media', 'unknown_person.png')


global windowstack
windowstack = []

global ids
ids = []


# Open file
def FileDoOpen(path):
    if os.path.isfile(path): 		## File found.
        fil = open(path, 'r')
        contents = fil.read()
        fil.close()
        return contents
    else: return '' 			    ## File not found.


# Save data to file
def FileDoSave(path, data):
    fil = open(path, 'w')
    fil.write(data)
    fil.close()


# Parse arguments
# def parse_argv(paramstring):
#    params={}
#    if len(paramstring)>=2:
#        if paramstring.endswith('/'):
#            paramstring = params[:-2]
#        if paramstring.startswith('plugin://%s/' % addon_id):
#            paramstring = paramstring.replace('plugin://%s/' % addon_id, '')
#            clas, _, func = paramstring.partition('/')
#            return clas, func
#        elif paramstring.startswith('?'):
#            paramstring = paramstring[1:]
#            pairsofparams = paramstring.split('&')
#            for pair in pairsofparams:
#                key, value = pair.split('=')
#                params[key] = value
#            return params


def CreateListItems(data=None):
    #Int_InfoLabels		= ["duration", "vote", "like", "dislike"]
    #Float_InfoLabels	= ["rating", "imdb_rating"]
    #String_InfoLabels	= ["id", "type", "originaltitle", "country", "plot", "genre", "categories", "year", "delivery_rules", "mpaa", "crew", "favourite", "screenshots", "quality", "season_list", "available", "audio_list"]
    itemlist = []

    if data is not None:
        image_requests = []
        for (count, result) in enumerate(data):
            listitem = xbmcgui.ListItem('%s' % (str(count)))
            # itempath = ""
            # counter = 1
            for (key, value) in result.iteritems():
                if not value:
                    continue

                #try: xbmc.log('[%s]: value.encode in CreateListItems - %s' % (addon_name, value.encode('utf-8')))
                #except: xbmc.log('[%s]: value in CreateListItems - %s' % (addon_name, value))

                if key.lower() in ['poster', 'screenshots', 'channel_image']:
                    if type(value) == list:
                        for picture in value:
                            if picture.startswith("http://") and (picture.endswith(".jpg") or picture.endswith(".png")):
                                if not picture.decode('utf-8') in image_requests:
                                    if Get_File(picture):
                                        # xbmc.log('1 Get_File(%s)' % picture)
                                        image_requests.append(picture.decode('utf-8'))
                                    else:
                                        # xbmc.log('2 Get_File(%s)' % picture)
                                        new_pic = picture.replace("2:", "5:")
                                        # xbmc.log('3 Get_File(%s)' % new_pic)
                                        Get_File(new_pic)
                                        image_requests.append(new_pic.decode('utf-8'))
                    elif type(value) == str:
                        if value.startswith("http://") and (value.endswith(".jpg") or value.endswith(".png")):
                            if not value.decode('utf-8') in image_requests:
                                if Get_File(value):
                                    image_requests.append(value.decode('utf-8'))
                                else:
                                    new_pic = picture.replace("2:", "5:")
                                    Get_File(new_pic)
                                    image_requests.append(new_pic.decode('utf-8'))
                    if key.lower() in ["poster"]:
                        listitem.setThumbnailImage(value)
                if key.lower() in ["title"]:
                    listitem.setLabel(value)
                if key.lower() in ["exclusive"]:
                    if value in ["True", "true"]:
                        listitem.setInfo('video', {key.lower(): value})
                        continue
                if key.lower() in ["delivery_rules"]:
                    if value.find('tvod') >= 0:
                        listitem.setProperty('Buy', 'True')
                    if value.find('dto') >= 0:
                        listitem.setProperty('Buy_Forever', 'True')
                    if value.find('svod') >= 0:
                        listitem.setProperty('Subscribe', 'True')
                listitem.setProperty('%s' % key, value)

            itemlist.append(listitem)

    return itemlist


def CreateActorListItems(data):
    itemlist = []
    if data is not None:
        image_requests = []
        for (count, result) in enumerate(data):
            listitem = xbmcgui.ListItem('%s' % (str(count)))
            counter = 1
            for (key, value) in result.iteritems():
                if not value:
                    continue
                if key.lower() in ["name"]:
                    listitem.setLabel(value)
                if key.lower() in ["thumb"]:
                    if value.startswith("http://") and (value.endswith(".jpg") or value.endswith(".png")):
                        if not value.decode('utf-8') in image_requests:
                            Get_File(value)
                            image_requests.append(value.decode('utf-8'))
                    listitem.setThumbnailImage(value)
                if key.lower() in ['id']:
                    listitem.setProperty('%s' % key.lower(), unicode(value))
                if key.lower() in ['name_original', 'type']:
                    listitem.setProperty('%s' % key.lower(), value.encode('utf-8'))

            listitem.setProperty("index", str(counter))
            itemlist.append(listitem)
            counter += 1

    return itemlist


def CreateCommentList(video_id, data=None):
    if not data:
        data = megogo2xbmc.getcomments(video_id)
        if not data:
            return []

    itemlist = []
    image_requests = []
    for (count, result) in enumerate(data):
        listitem = xbmcgui.ListItem('%s' % (str(count)))
        counter = 1
        for (key, value) in result.iteritems():
            if not value:
                continue
            if key.lower() in ["user_name"]:
                listitem.setLabel(value)
            if key.lower() in ["user_avatar"]:
                if value.startswith("http://") and (value.endswith(".jpg") or value.endswith(".png")):
                    if not value.decode('utf-8') in image_requests:
                        try:
                            Get_File(value)
                        except:
                            image_requests.append(value.decode('utf-8'))
                listitem.setThumbnailImage(value)
            if key.lower() in ['text']:
                listitem.setProperty('%s' % key.lower(), value.encode('utf-8'))
            if key.lower() in ['date']:
                data, _, time = value.partition('T')
                listitem.setProperty('%s' % key.lower(), "%s %s" % (data, time[:-1]))

        listitem.setProperty("index", str(counter))
        itemlist.append(listitem)
        counter += 1

    return itemlist


def CreateTiriffList(data, currency):
    if not data:
        return []
    Int_InfoLabels		= ["tariff_id", "period"]
    Float_InfoLabels	= ["price"]
    String_InfoLabels	= ["description", "title"]

    itemlist = []
    for (count, result) in enumerate(data):
        listitem = xbmcgui.ListItem('%s' % (str(count)))
        listitem.setProperty('currency', unicode(currency))
        for (key, value) in result.iteritems():
            if not value:
                continue
            if key.lower() in Int_InfoLabels:
                listitem.setProperty('%s' % key.lower(), unicode(value))
            if key.lower() in String_InfoLabels:
                listitem.setProperty('%s' % key.lower(), value.encode('utf-8'))
            if key.lower() in Float_InfoLabels:
                try:
                    listitem.setProperty('%s' % key.lower(), "%1.1f" % float(value))
                except:
                    pass
        itemlist.append(listitem)
    return itemlist


def update_content(force=False, page=False, section=False, offset=0):
    listitems = fetch_data(force, page, section, offset)
    if listitems and page != 'tv?limit=200':
        return CreateListItems(listitems)
    elif listitems and page == 'tv?limit=200':
        for item in listitems:
            item['channels'] = CreateListItems(item['channels'])
        return listitems
    else:
        return []


def fetch_data(force=False, page=False, section=False, offset=0):
    if page == 'configuration':
        return megogo2xbmc.getconfiguration()
    elif page == 'tarification':
        return megogo2xbmc.gettarification()
    elif page == 'Main':
        response = megogo2xbmc.main_page(force)
    elif page and section:
        response = megogo2xbmc.getvideodata(force, page, section)
    else:
        response = megogo2xbmc.get_page(force, page, offset)

    if not response:
        return []
    try:
        if len(response['data']['video_list']) == 0:
            return []
    except:
        pass
    if page == 'Main' and section == 'recommended':
        return megogo2xbmc.HandleMainPage(response['data'], 'recommended')
    elif page == 'Main' and section == 'slider':
        return megogo2xbmc.HandleMainPage(response['data'], 'sliders')
    elif page.startswith('subscription') or page.startswith('premieres') or page.startswith('video?category_id=') or page.startswith('user/') or page.startswith('video/collection') or page.startswith('search'):
        return megogo2xbmc.HandleMainPage(response['data'], 'video_list')
    elif page.startswith('collections'):
        return megogo2xbmc.HandleMainPage(response['data'], 'collections')
    elif page.startswith('tv/channels'):
        return megogo2xbmc.HandleMainPage(response['data'], 'channels')
    elif page == 'tv?limit=200':
        return megogo2xbmc.HandleTVPackeges(response['data'], 'packages')
    elif page.startswith('video/episodes'):
        return response['data']
    else:
        return megogo2xbmc.HandleVideoResult(response['data'])


def get_title(page):
    response = megogo2xbmc.get_page(False, page)
    if len(response) == 0 or response['result'] != 'ok':
        return False
    else:
        return response['data']['title']


def Get_File(url):
    clean_url = xbmc.translatePath(url).replace("image://", "")
    if clean_url.endswith("/"):
        clean_url = clean_url[:-1]
    cachedthumb = str(xbmc.getCacheThumbName(clean_url)).decode('utf-8')
    xbmc.log('[%s]: image link %s -> cache %s' % (addon_name, url, cachedthumb))
    xbmc_vid_cache_file = os.path.join('special://profile/Thumbnails/Video', cachedthumb[0], cachedthumb)
    xbmc_cache_file_jpg = os.path.join("special://profile/Thumbnails/", cachedthumb[0], cachedthumb[:-4] + ".jpg").replace("\\", "/")
    xbmc_cache_file_png = xbmc_cache_file_jpg[:-4] + ".png"
    if xbmcvfs.exists(xbmc_cache_file_jpg):
        xbmc.log("[%s]: xbmc_cache_file_jpg - %s" % (addon_name, xbmc_cache_file_jpg))
        return xbmc.translatePath(xbmc_cache_file_jpg)
    elif xbmcvfs.exists(xbmc_cache_file_png):
        xbmc.log("[%s]: xbmc_cache_file_png - %s" % (addon_name, xbmc_cache_file_png))
        return xbmc_cache_file_png
    elif xbmcvfs.exists(xbmc_vid_cache_file):
        xbmc.log("[%s]: xbmc_vid_cache_file - %s" % (addon_name, xbmc_vid_cache_file))
        return xbmc_vid_cache_file
    else:
        try:
            #xbmc.log("[%s]: Download: %s" % (addon_name, url))
            request = urllib2.Request(url)
            request.add_header('Accept-encoding', 'gzip')
            response = urllib2.urlopen(request)
            data = response.read()
            response.close()
        except:
            xbmc.log("[%s]: image download failed: %s" % (addon_name, url))
            return None
        if data != '':
            try:
                if url.endswith(".png"):
                    image = xbmc_cache_file_png
                else:
                    image = xbmc_cache_file_jpg
                tmpfile = open(xbmc.translatePath(image), 'wb')
                tmpfile.write(data)
                tmpfile.close()
                xbmc.log("[%s]: image %s downloaded: %s" % (addon_name, image, url))
                return xbmc.translatePath(image)
            except:
                xbmc.log("[%s]: failed to save image %s" % (addon_name, url))
                return None
        else:
            return None


def get_subscribe_tariffs(title):
    if title == 'svod':
        product = 'main'
    elif title == 'TV':
        product = 'tv'

    tariffs = []

    data = megogo2xbmc.gettarification()
    if data:
        for arr in data:
            if arr['product'] == product:
                tariffs.append(arr)
        return tariffs
    else:
        return None


def get_quality(value):
    return language(int(value)+201)


def get_language(value):
    return language(int(value)+300)


def get_subtitle(value):
    if int(value) == 0:
        return language(400)
    else:
        return language((int(value)-1)+300)


def get_ui_language():
    index = get_language(addon.getSetting('language'))[-3:-1]
    return index


def AddToWindowStack(window, controlID):
    windowstack.append({'window': window, 'id': controlID})


def DelWindowStack():
    global windowstack
    for window in windowstack:
        window['window'].close()
    windowstack = []


def PopWindowStack(active):
    if windowstack:
        array = windowstack.pop()
        dialog = array['window']
        ids.append(array['id'])
        dialog.doModal()
    else:
        active.close()


def DelFromWindowStack(amount):
    if amount:
        inc = 0
        while inc < amount:
            if len(windowstack) > 0:
                del windowstack[-1]
                inc += 1
            else:
                break


def CountWindowStack():
    global windowstack
    return len(windowstack)


def getids():
    if ids:
        return ids.pop()
    else:
        return None


class VideoPlayer(xbmc.Player):
    def __init__(self, *args, **kwargs):
        xbmc.Player.__init__(self)
        self.size = None
        self.counter = 0
        self.stopped = False
        self.popstack = kwargs.get("popstack", True)

    def onPlayBackEnded(self):
        if self.size:
            self.counter += 1
            if self.counter <= self.size:
                self.stopped = False
                xbmc.sleep(1500)
                if not self.isPlaying():
                    self.stopped = True
            else:
                self.stopped = True
        else:
            self.stopped = True

    def onPlayBackStopped(self):
        self.stopped = True

    def onPlayBackStarted(self):
        self.stopped = False

    def play_item(self, stream_url, listitem, subtitle=None, popstack=True):
        if subtitle:
            try:
                listitem.setSubtitles([subtitle])
            except Exception as e:
                xbmc.log('[%s]: NOT KODI. SUBTITLE EXCEPTION: %s' % (addon_name, e))
            xbmc.log('SUBTITILE - %s' % subtitle)
        xbmc.executebuiltin("Dialog.Close(all, true)")
        self.play(stream_url, listitem)

    def play_playlist(self, playlist, size, popstack=True):
        self.size = size
        xbmc.executebuiltin("Dialog.Close(all, true)")
        self.play(playlist)

    def WaitForVideoEnd(self):
        while not self.stopped:
            xbmc.sleep(200)
        self.stopped = False