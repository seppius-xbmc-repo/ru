# -*- coding: utf-8 -*-
import os
import sys
import gc

import json
import xbmc, xbmcgui, xbmcplugin
import urllib
from simpleplugin import RoutedPlugin
from simpleplugin import MemStorage

try:
    import urllib2
except:
    import urllib.request as urllib2

plugin = RoutedPlugin()
storage = MemStorage('legends')

@plugin.route('/')
def root():
    listing = get_releases_list()
    return plugin.create_listing(listing, content='movies', sort_methods=(xbmcplugin.SORT_METHOD_DATEADDED, xbmcplugin.SORT_METHOD_VIDEO_RATING), cache_to_disk=True)


@plugin.route('/film')
def film():
    allmovies = storage['movies']

    use_torrserver = plugin.get_setting('use_engine', True)
    id = int(plugin.params.id)
    major_version = int(xbmc.getInfoLabel('System.BuildVersion')[:2])

    info = []
    for release in allmovies:    
        if int(release['filmID']) == id:
            info = release['torrents']
            break
    plugin.log_error(info)
    list_torrent = []
    list = []
    auto_play = plugin.get_setting('auto_play', True)
    for i in info:
        list_torrent.append(i['magnet'])
        date = i['date'].split('-')
        date = date[2]+"."+date[1]+"."+date[0]

        label = i['type']

        lowSeeders = ""
        if i.get('lowSeeders', False):
            lowSeeders = " [COLOR=red]Очень мало сидеров[/COLOR]"

        if major_version > 16:
            if ("HDR" in label):
                thumb = os.path.join(plugin.path, 'resources', 'images', '2160pHDR.png')
            elif (("UHD" in label) or ("2160p" in label)):
                thumb = os.path.join(plugin.path, 'resources', 'images', '2160pSDR.png')
            else:
                thumb = os.path.join(plugin.path, 'resources', 'images', '1080p.png')

            label2 = "{0}{1}".format(date, lowSeeders)

            li = plugin.create_list_item({"label": label, "label2": label2, "thumb": thumb})
            list.append(li)
        else:
            list.append(label)

    if (len(list_torrent) > 0):
        if not auto_play:
            if major_version > 16:
                dialog = xbmcgui.Dialog()
                ret = dialog.select('Список торрентов', list=list, useDetails=True)
            else:
                dialog = xbmcgui.Dialog()
                ret = dialog.select('Список торрентов', list=list)
        else:
            ret = len(list_torrent) - 1
        if ret > -1:
            t_url = list_torrent[ret]
            if use_torrserver:
                ip = plugin.get_setting('ts-host', True)
                port = plugin.get_setting('ts-port', True)
                path = "http://{0}:{1}/torrent/play?link={2}&preload=0&file=0&save=false".format(ip, port, t_url)
            else:
                path = "plugin://plugin.video.elementum/play?uri={0}".format(t_url)
            return plugin.resolve_url(path, succeeded=True)
    else:
        xbmcgui.Dialog().ok("Нет подходящих торрентов", "Нет подходящих под фильтр торрентов")
        return plugin.resolve_url(succeeded=False)


def get_json():
    if plugin.get_setting('mode', True) == 0:
        page = urllib2.urlopen('https://ndr.neocities.org/ndr_kodi.json').read()
    else:
        page = urllib2.urlopen('https://ndr.neocities.org/legends_kodi.json').read()

    releases = json.loads(page)
    releases = releases['movies']
    return releases


def get_releases_list():
    releases = get_json()
    storage['movies'] = releases
    major_version = int(xbmc.getInfoLabel('System.BuildVersion')[:2])
    listing = []
    num = 0
    for release in releases:
        timestr = release['filmLength']
        ftr = [3600,60]
        duration = sum([a*b for a,b in zip(ftr, map(int,timestr.split(':')))])
        s=num
        hour = s / 3600
        min = (s - hour * 3600) / 60
        sec = s - hour * 3600 - min * 60
        fake_time = '%02d:%02d:%02d' % (hour, min, 59 - sec)
        cm = []
        playcount = get_playcount(release['filmID'])
        if (playcount > 0):
            cm.append(('Не просмотренно', 'RunPlugin(%s)' % plugin.url_for('mark_unwatched', id=release['filmID'])))
        else:
            cm.append(('Просмотренно', 'RunPlugin(%s)' % plugin.url_for('mark_watched', id=release['filmID'])))
        if major_version < 17:
            cm.append(('Сведения', 'Action(Info)'))

        listing.append({
            'label': release['nameRU'],
            'art': {
                'thumb': release['posterURL'],
                'poster': release['bigPosterURL'],
                'fanart': release['bigPosterURL'],
                'icon': release['posterURL']
            },
            'info': {
                'video': {
                    'count': num,
                    'cast': release['actors'].split(','),
                    'dateadded': release['torrentsDate'] + " "+fake_time,
                    'director': release['directors'].split(','),
                    'genre': release['genre'].split(','),
                    'country': release['country'],
                    'year': int(release['year']),
                    'rating': float(release['ratingFloat']),
                    'plot': release['description'],
                    'plotoutline': release['description'],
                    'title': release['nameRU'],
                    'sorttitle': release['nameRU'],
                    'duration': duration,
                    'originaltitle': release['nameOriginal'],
                    'premiered': release['premierDate'],
                    'trailer': release['trailerURL'],
                    'mediatype': 'movie',
                    'mpaa': release['ratingMPAA'] if release['ratingAgeLimits'] == "" else release['ratingAgeLimits'],
                    'playcount': playcount,
                }
            },
            'is_folder': False,
            'is_playable': True,
            'url': plugin.url_for('film', id=release['filmID']),
            'context_menu': cm
            })
        num += 1
    return listing

@plugin.route('/mark_watched')
def mark_watched():
    id = plugin.params.id
    with plugin.get_storage("watched") as storage:
        storage[id] = 1
    return xbmc.executebuiltin("Container.Refresh")


@plugin.route('/mark_unwatched')
def mark_unwatched():
    id = plugin.params.id
    with plugin.get_storage("watched") as storage:
        storage[id] = 0
    return xbmc.executebuiltin("Container.Refresh")

def get_playcount(id):
    count = 0
    with plugin.get_storage("watched") as storage:
        count = storage.get(str(id), 0) 
    return count

if __name__ == '__main__':
    plugin.run()

gc.collect()