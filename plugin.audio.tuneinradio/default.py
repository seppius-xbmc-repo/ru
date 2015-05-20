#/*
# *
# * TuneIn Radio for XBMC.
# *
# * Copyright (C) 2013 Brian Hornsby
# *
# * This program is free software: you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation, either version 3 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program.  If not, see <http://www.gnu.org/licenses/>.
# *
# */

import xbmc
import xbmcgui
import xbmcplugin
import os
import urllib
import urllib2
import re

import resources.lib.cache as cache
import resources.lib.tunein as tunein
import resources.lib.xbmcdownload as download
import resources.lib.xbmcsettings as settings
import resources.lib.xbmcutils as utils


def get_max_preset_num(elementslist):
    maxpresetnum = 0
    for element in elementslist:
        if 'show' in element and utils.get_int(element['show'], 'preset_number') > maxpresetnum:
            maxpresetnum = utils.get_int(element['show'], 'preset_number')
        elif 'station' in element and utils.get_int(element['station'], 'preset_number') > maxpresetnum:
            maxpresetnum = utils.get_int(element['station'], 'preset_number')
        elif 'link' in element and __tunein__.is_custom_url_id(utils.get_value(element['link'], 'guide_id')) and utils.get_int(element['link'], 'preset_number') > maxpresetnum:
            maxpresetnum = utils.get_int(element['link'], 'preset_number')
    return maxpresetnum


def reorder_preset_elements(elementslist):
    log_debug('reorder_preset_elements', 2)
    newelementslist = []
    maxpresetnum = get_max_preset_num(elementslist)
    presetnum = 1
    while presetnum <= maxpresetnum:
        for element in elementslist:
            if 'show' in element and utils.get_int(element['show'], 'preset_number') == presetnum:
                newelementslist.append({'show': element['show']})
                break
            elif 'station' in element and utils.get_int(element['station'], 'preset_number') == presetnum:
                newelementslist.append({'station': element['station']})
                break
            elif 'link' in element and __tunein__.is_custom_url_id(utils.get_value(element['link'], 'guide_id')) and utils.get_int(element['link'], 'preset_number') == presetnum:
                newelementslist.append({'link': element['link']})
                break
        presetnum = presetnum + 1

    # Add any links or topics to ordered elements list.
    for element in elementslist:
        if 'link' in element and not __tunein__.is_custom_url_id(utils.get_value(element['link'], 'guide_id')):
            newelementslist.append({'link': element['link']})
        elif 'topic' in element:
            newelementslist.append({'topic': element['topic']})

    return newelementslist


def process_tunein_json(elements):
    log_debug('process_tunein_json', 2)

    elementslist = []
    for element in elements:
        if ('element' in element and element['element'] == 'outline'):
            if ('children' in element):
                for children in element['children']:
                    if ('key' in element and element['key'] == 'shows'):
                        if ('item' in children and children['item'] == 'show'):
                            elementslist.append(
                                {'show': __read_element__(children)})
                        elif ('type' in children and children['type'] == 'link'):
                            elementslist.append(
                                {'link': __read_element__(children)})
                        # else:
                            # print('Ignoring outline-children-shows: %s' %
                            # children)
                    elif ('key' in element and element['key'] == 'stations'):
                        if ('item' in children and children['item'] == 'station'):
                            elementslist.append(
                                {'station': __read_element__(children)})
                        elif ('type' in children and children['type'] == 'link'):
                            elementslist.append(
                                {'link': __read_element__(children)})
                        # else:
                            # print('Ignoring outline-children-stations: %s' %
                            # children)
                    elif('key' in element and element['key'] == 'topics'):
                        if ('item' in children and children['item'] == 'topic'):
                            elementslist.append(
                                {'topic': __read_element__(children)})
                        elif ('type' in children and children['type'] == 'link'):
                            elementslist.append(
                                {'link': __read_element__(children)})
                        # else:
                            # print('Ignoring outline-children-topics: %s' %
                            # children)
                    elif (not __featured__ and 'key' in element and element['key'] == 'featured'):
                        pass
                    elif (not __local__ and 'key' in element and element['key'] == 'local'):
                        pass
                    else:
                        if ('type' in children and children['type'] == 'audio'):
                            if 'item' in children and children['item'] == 'station':
                                elementslist.append(
                                    {'station': __read_element__(children)})
                            elif 'item' in children and children['item'] == 'show':
                                elementslist.append(
                                    {'show': __read_element__(children)})
                            elif ('guide_id' in children and children['guide_id'][0] == 's'):
                                elementslist.append(
                                    {'station': __read_element__(children)})
                            elif ('guide_id' in children and children['guide_id'][0] == 't'):
                                elementslist.append(
                                    {'topic': __read_element__(children)})
                            elif ('guide_id' in children and children['guide_id'][0] == 'p'):
                                if presets:
                                    elementslist.insert(children['preset_number'], {
                                                        'show': __read_element__(children)})
                                else:
                                    elementslist.append(
                                        {'show': __read_element__(children)})
                        elif ('type' in children and children['type'] == 'link'):
                            elementslist.append(
                                {'link': __read_element__(children)})
                        # else:
                            # print('Ignoring outline-children: %s' % children)

            elif ('type' in element and element['type'] == 'audio' and 'guide_id' in element and element['guide_id'][0] == 's'):
                elementslist.append({'station': __read_element__(element)})
            elif ('type' in element and element['type'] == 'audio' and 'guide_id' in element and element['guide_id'][0] == 't'):
                elementslist.append({'topic': __read_element__(element)})
            elif ('type' in element and element['type'] == 'audio' and 'guide_id' in element and element['guide_id'][0] == 'p'):
                elementslist.append({'show': __read_element__(element)})
            elif ('type' in element and element['type'] == 'link'):
                elementslist.append({'link': __read_element__(element)})
            elif ('item' in element and element['item'] == 'show'):
                elementslist.append({'show': __read_element__(element)})
            elif ('item' in element and element['item'] == 'station'):
                elementslist.append({'station': __read_element__(element)})
            # else:
                # print('Ignoring outline: %s' % element)
        elif ('element' in element and element['element'] == 'show'):
            elementslist.append({'show': __read_element__(element)})
        elif ('element' in element and element['element'] == 'station'):
            elementslist.append({'station': __read_element__(element)})
        elif ('element' in element and element['element'] == 'topic'):
            elementslist.append({'topic': __read_element__(element)})
        elif ('element' in element and element['element'] == 'link'):
            elementslist.append({'link': __read_element__(element)})
        # else:
            # print('Ignoring: %s' % element)

    # if presets, reorder.
    if get_max_preset_num(elementslist) > 0:
        elementslist = reorder_preset_elements(elementslist)

    for element in elementslist:
        if 'link' in element:
            add_link_outline(element['link'])
        elif 'show' in element:
            add_show_outline(element['show'])
        elif 'station' in element:
            add_station_outline(element['station'])
        elif 'topic' in element:
            add_topic_outline(element['topic'])


def __read_element__(element):
    outline = {}
    for key in element:
        outline[key] = element[key]
    return outline


def add_directory_item(name, url, label='', artist='', album='', genre='', comment='', logo=None, isfolder=True, contextmenu=None):
    log_debug('add_directory_item', 2)
    log_debug('name: %s' % name, 3)
    log_debug('url: %s' % url, 3)
    log_debug('label: %s' % label, 3)
    log_debug('artist: %s' % artist, 3)
    log_debug('album: %s' % album, 3)
    log_debug('genre: %s' % genre, 3)
    log_debug('comment: %s' % comment, 3)
    log_debug('logo: %s' % logo, 3)
    log_debug('isfolder: %s' % isfolder, 3)
    log_debug('contextmenu: %s' % contextmenu, 3)

    # If logo argument not set use default directory/stream image.
    if (logo is None or len(logo) == 0) and isfolder:
        iconImage = __settings__.get_path('%s%s%s' % (
            'resources/images/', get_logo_colour(), '/folder-32.png'))
        thumbnailImage = __settings__.get_path('%s%s%s' % (
            'resources/images/', get_logo_colour(), '/folder-256.png'))

        # Add custom logos for Browse category
        # pattern = re.compile('(.*)c=(\w+)')
        # result = pattern.match(url)
        params = utils.get_params(url.split('?')[1])
        category = utils.get_value(params, 'c')
        if (category):
            # if result.group(2) == "local":
            if category == "local":
                iconImage = __settings__.get_path('%s%s%s' % (
                    'resources/images/', get_logo_colour(), '/local-32.png'))
                thumbnailImage = __settings__.get_path('%s%s%s' % (
                    'resources/images/', get_logo_colour(), '/local-256.png'))
            elif category == "music":
                iconImage = __settings__.get_path('%s%s%s' % (
                    'resources/images/', get_logo_colour(), '/music-32.png'))
                thumbnailImage = __settings__.get_path('%s%s%s' % (
                    'resources/images/', get_logo_colour(), '/music-256.png'))
            elif category == "talk":
                iconImage = __settings__.get_path('%s%s%s' % (
                    'resources/images/', get_logo_colour(), '/talk-32.png'))
                thumbnailImage = __settings__.get_path('%s%s%s' % (
                    'resources/images/', get_logo_colour(), '/talk-256.png'))
            elif category == "sports":
                iconImage = __settings__.get_path('%s%s%s' % (
                    'resources/images/', get_logo_colour(), '/sports-32.png'))
                thumbnailImage = __settings__.get_path('%s%s%s' % (
                    'resources/images/', get_logo_colour(), '/sports-256.png'))
            elif category == "lang":
                iconImage = __settings__.get_path('%s%s%s' % (
                    'resources/images/', get_logo_colour(), '/by_language-32.png'))
                thumbnailImage = __settings__.get_path('%s%s%s' % (
                    'resources/images/', get_logo_colour(), '/by_language-256.png'))
            elif category == "podcast":
                iconImage = __settings__.get_path('%s%s%s' % (
                    'resources/images/', get_logo_colour(), '/podcasts-32.png'))
                thumbnailImage = __settings__.get_path('%s%s%s' % (
                    'resources/images/', get_logo_colour(), '/podcasts-256.png'))
            elif category == "video":
                iconImage = __settings__.get_path('%s%s%s' % (
                    'resources/images/', get_logo_colour(), '/livetv-32.png'))
                thumbnailImage = __settings__.get_path('%s%s%s' % (
                    'resources/images/', get_logo_colour(), '/livetv-256.png'))

        # Add custom logo for location
        pattern = re.compile('(.*)id=r(.*)')
        result = pattern.match(url)
        if (result):
            iconImage = __settings__.get_path('%s%s%s' % (
                'resources/images/', get_logo_colour(), '/by_location-32.png'))
            thumbnailImage = __settings__.get_path('%s%s%s' % (
                'resources/images/', get_logo_colour(), '/by_location-256.png'))

    elif (logo is None or len(logo) == 0) and not isfolder:
        iconImage = __settings__.get_path('%s%s%s' % (
            'resources/images/', get_logo_colour(), '/stream-32.png'))
        thumbnailImage = __settings__.get_path('%s%s%s' % (
            'resources/images/', get_logo_colour(), '/stream-256.png'))
    else:
        iconImage = logo
        thumbnailImage = logo

    # Add addons settings context menu.
    if contextmenu is None:
        contextmenu = [(__settings__.get_string(
            1011), 'XBMC.RunPlugin(%s?path=refresh)' % __settings__.get_argv(0))]
    else:
        contextmenu.append((__settings__.get_string(
            1011), 'XBMC.RunPlugin(%s?path=refresh)' % __settings__.get_argv(0)))

    liz = xbmcgui.ListItem(name, label, iconImage=iconImage, thumbnailImage=thumbnailImage)
    liz.addContextMenuItems(items=contextmenu, replaceItems=True)
    liz.setInfo('Music', {'Title': name, 'Artist': artist, 'Album':
                album, 'Genre': genre, 'Comment': comment})
    if not isfolder:
        liz.setProperty('IsPlayable', 'true')

    if __settings__.get('fanart') == "true":
        liz.setProperty('fanart_image', __fanart__)
    xbmcplugin.addDirectoryItem(handle=int(
        __settings__.get_argv(1)), url=url, listitem=liz, isFolder=isfolder)


def add_custom_url(link, presets=True):
    log_debug('add_custom_url', 2)
    log_debug('link: %s' % link, 3)

    if not __tunein__.is_custom_url_id(utils.get_value(link, 'guide_id')):
        return

    id = utils.get_value(link, 'guide_id')
    url = utils.get_value(link, 'URL')
    name = utils.get_value(link, 'text')
    logo = utils.get_value(link, 'image')
    path = 'custom-url'
    contextmenu = None
    if presets:
        contextmenu = [(__settings__.get_string(1017), 'XBMC.RunPlugin(%s?path=%s&id=%s)' % (
            __settings__.get_argv(0), 'remove', id, ))]
    url = utils.add_params(__settings__.get_argv(
        0), {'path': path, 'id': id, 'name': name, 'url': url, 'logo': logo})
    add_directory_item(
        name, url, logo=logo, contextmenu=contextmenu, isfolder=False)


def add_link_outline(link):
    log_debug('add_link_outline', 2)
    log_debug('link: %s' % link, 3)

    if __tunein__.is_custom_url_id(utils.get_value(link, 'guide_id')):
        add_custom_url(link)
        return

    params = utils.get_params(link['URL'].split('?')[1])
    category = utils.get_value(params, 'c')
    offset = utils.get_value(params, 'offset')
    filter = utils.get_value(params, 'filter')
    pivot = utils.get_value(params, 'pivot')
    id = utils.get_value(params, 'id')
    name = utils.get_value(link, 'text')
    logo = ''

    if 'image' in link:
        logo = utils.get_value(link, 'image')
    label = ''
    if 'subtext' in link:
        label = utils.get_value(link, 'subtext')

    path = 'browse'
    if __tunein__.is_show_id(id):
        path = 'tune-show'
        contextmenu = [(__settings__.get_string(1009), 'XBMC.RunPlugin(%s?path=%s&id=%s)' %
                    (__settings__.get_argv(0), 'add', id, ))]
    else:
        contextmenu = []

    url = utils.add_params(__settings__.get_argv(0), {
                           'path': path, 'id': id, 'c': category, 'name': name, 'filter': filter, 'offset': offset, 'pivot': pivot})

    add_directory_item(name, url, label=label, logo=logo, contextmenu=contextmenu)


def add_show(show):
    log_debug('add_show', 2)
    log_debug('show: %s' % show, 3)

    id = utils.get_value(show, 'guide_id')
    name = utils.get_value(show, 'title')
    logo = utils.get_value(show, 'logo')
    label = utils.get_value(show, 'description')
    genre = utils.get_value(show, 'genre_name')
    if len(genre) == 0:
        genre = get_genre_name(utils.get_value(show, 'genre_id'))

    if not __tunein__.is_show_id(id):
        return

    __showscache__.add(show)

    url = utils.add_params(__settings__.get_argv(
        0), {'path': 'tune-show', 'id': id, 'name': name, 'logo': logo})
    contextmenu = [(__settings__.get_string(1009), 'XBMC.RunPlugin(%s?path=%s&id=%s)' %
                    (__settings__.get_argv(0), 'add', id, ))]
    add_directory_item(name, url, label=label, genre=genre, logo=logo,
                       contextmenu=contextmenu)


def add_show_outline(show):
    log_debug('add_show_outline', 2)
    log_debug('show: %s' % show, 3)

    id = utils.get_value(show, 'guide_id')
    name = utils.get_value(show, 'text')
    logo = utils.get_value(show, 'image')
    label = utils.get_value(show, 'subtext')
    album = utils.get_value(show, 'current_track')
    is_preset = utils.get_value(show, 'is_preset')
    preset_number = utils.get_value(show, 'preset_number')

    params = utils.get_params(show['URL'].split('?')[1])
    category = utils.get_value(params, 'c')
    filter = utils.get_value(params, 'filter')

    if not __tunein__.is_show_id(id):
        return

    __showscache__.add(show)

    url = utils.add_params(__settings__.get_argv(0), {
                           'path': 'tune-show', 'id': id, 'name': name, 'logo': logo, 'c': category, 'filter': filter})

    if is_preset == 'true':
        contextmenu = [(
            __settings__.get_string(
                1012), 'XBMC.RunPlugin(%s?path=%s&id=%s&num=%s)' % (__settings__.get_argv(0), 'up', id, preset_number, )),
            (__settings__.get_string(1013), 'XBMC.RunPlugin(%s?path=%s&id=%s&num=%s)' %
             (__settings__.get_argv(0), 'down', id, preset_number,)),
            (__settings__.get_string(1010), 'XBMC.RunPlugin(%s?path=%s&id=%s)' % (__settings__.get_argv(0), 'remove', id, ))]
    else:
        contextmenu = [(__settings__.get_string(
            1009), 'XBMC.RunPlugin(%s?path=%s&id=%s)' % (__settings__.get_argv(0), 'add', id, ))]

    add_directory_item(name, url, label=label, album=album, logo=logo,
                       contextmenu=contextmenu)


def add_station(station):
    log_debug('add_station', 2)
    log_debug('station: %s' % station, 3)

    id = utils.get_value(station, 'guide_id')
    name = utils.get_value(station, 'name')
    logo = utils.get_value(station, 'logo')
    label = utils.get_value(station, 'slogan')
    genre = utils.get_value(station, 'genre_name')
    if len(genre) == 0:
        genre = get_genre_name(utils.get_value(station, 'genre_id'))

    if not __tunein__.is_station_id(id):
        return

    contextmenu = [(__settings__.get_string(1018), 'XBMC.RunPlugin(%s)' % (utils.add_params(__settings__.get_argv(0), {'path': 'xbmc-favourites', 'id': id, 'name': name, 'logo': logo})))]

    url = utils.add_params(__settings__.get_argv(
        0), {'path': 'tune', 'id': id, 'name': name, 'logo': logo})
    add_directory_item(
        name, url, label=label, genre=genre, logo=logo, isfolder=False, contextmenu=contextmenu)


def add_station_outline(station):
    log_debug('add_station_outline', 2)
    log_debug('station: %s' % station, 3)

    id = utils.get_value(station, 'guide_id')
    name = utils.get_value(station, 'text')
    logo = utils.get_value(station, 'image')
    label = utils.get_value(station, 'subtext')
    album = utils.get_value(station, 'current_track')
    is_preset = utils.get_value(station, 'is_preset')
    preset_number = utils.get_value(station, 'preset_number')
    genre = utils.get_value(station, 'genre_name')
    if len(genre) == 0:
        genre = get_genre_name(utils.get_value(station, 'genre_id'))

    if not __tunein__.is_station_id(id):
        return

    url = utils.add_params(__settings__.get_argv(
        0), {'path': 'tune', 'id': id, 'name': name, 'logo': logo})

    if is_preset == 'true':
        contextmenu = [(
            __settings__.get_string(
                1012), 'XBMC.RunPlugin(%s?path=%s&id=%s&num=%s)' % (__settings__.get_argv(0), 'up', id, preset_number, )),
            (__settings__.get_string(1013), 'XBMC.RunPlugin(%s?path=%s&id=%s&num=%s)' %
             (__settings__.get_argv(0), 'down', id, preset_number, )),
            (__settings__.get_string(1005), 'XBMC.RunPlugin(%s?path=%s&id=%s)' % (__settings__.get_argv(0), 'remove', id))]
    else:
        contextmenu = [(__settings__.get_string(
            1004), 'XBMC.RunPlugin(%s?path=%s&id=%s)' % (__settings__.get_argv(0), 'add', id))]

    contextmenu.append((__settings__.get_string(1018), 'XBMC.RunPlugin(%s)' % (utils.add_params(__settings__.get_argv(0), {'path': 'xbmc-favourites', 'id': id, 'name': name, 'logo': logo}))))
    add_directory_item(name, url, album, artist=label, album=name, genre=genre,
                       logo=logo, isfolder=False, contextmenu=contextmenu)


def add_topic(topic, file=''):
    log_debug('add_topic', 2)
    log_debug('topic: %s' % topic, 3)
    log_debug('file: %s' % file, 3)

    id = utils.get_value(topic, 'guide_id')
    name = utils.get_value(topic, 'title')
    stream_type = utils.get_value(topic, 'stream_type')

    if not __tunein__.is_topic_id(id):
        return

    if not __enabledownloads__ and stream_type == 'download':
        return

    url = utils.add_params(__settings__.get_argv(
        0), {'path': 'tune', 'id': id, 'name': name, 'file': file})

    logo = None
    contextmenu = None
    if file is not None and len(file) > 0:
        contextmenu = [(__settings__.get_string(1016), 'XBMC.RunPlugin(%s?path=%s&id=%s)' % (
            __settings__.get_argv(0), 'remove-download', id))]
    if stream_type == 'download':
        logo = __settings__.get_path('%s%s%s' % (
            'resources/images/', get_logo_colour(), '/downloads-256.png'))

    add_directory_item(
        name, url, logo=logo, isfolder=False, contextmenu=contextmenu)


def add_topic_outline(topic):
    log_debug('add_topic_outline', 2)
    log_debug('topic: %s' % topic, 3)

    id = utils.get_value(topic, 'guide_id')
    name = utils.get_value(topic, 'text')
    subtext = utils.get_value(topic, 'subtext')
    stream_type = utils.get_value(topic, 'stream_type')

    params = utils.get_params(topic['URL'].split('?')[1])
    show_id = utils.get_value(params, 'sid')

    if not __tunein__.is_topic_id(id):
        return

    if not __enabledownloads__ and stream_type == 'download':
        return

    artist = ''
    comment = ''
    genre = ''
    album = ''
    for show in __showscache__.get():
        if 'guide_id' in show and show['guide_id'] == show_id:
            artist = utils.get_value(show, 'text')
            if len(artist) == 0:
                artist = utils.get_value(show, 'hosts')
            album = utils.get_value(show, 'title')
            comment = utils.get_value(show, 'subtext')
            if len(comment) == 0:
                comment = utils.get_value(show, 'description')
            genre = get_genre_name(utils.get_value(show, 'genre_id'))
            break

    url = utils.add_params(
        __settings__.get_argv(0), {'path': 'tune', 'id': id, 'name': name})

    logo = None
    contextmenu = None
    if stream_type == 'download':
        contextmenu = [(__settings__.get_string(1014), 'XBMC.RunPlugin(%s?path=%s&id=%s)' % (
            __settings__.get_argv(0), 'download', id))]
        logo = __settings__.get_path('%s%s%s' % (
            'resources/images/', get_logo_colour(), '/downloads-256.png'))

    add_directory_item(name, url, label=subtext, artist=artist, album=album,
                       comment=comment, genre=genre, logo=logo, isfolder=False, contextmenu=contextmenu)


def add_streams(streams, name=None, logo=None):
    log_debug('add_streams', 2)
    log_debug('streams: %s' % streams, 3)
    log_debug('name: %s' % name, 3)
    log_debug('logo: %s' % logo, 3)

    pDialog = xbmcgui.DialogProgress()
    pDialog.create(__addonname__, 'Creating playlist')
    playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
    playlist.clear()
    for count, stream in enumerate(streams):
        log_debug('Adding stream %s to playlist.' % stream, 1)
        pDialog.update(50, 'Adding stream %d of %d to playlist' % (count + 1, len(streams)), stream)

        if name:
            liz = xbmcgui.ListItem(name, iconImage=logo, thumbnailImage=logo)
            liz.setInfo('music', {'Title': name})
            playlist.add(url=stream, listitem=liz)
        else:
            playlist.add(url=stream)
    pDialog.close()
    if len(playlist) > 0:
        xbmcplugin.setResolvedUrl(handle=int(__settings__.get_argv(1)), succeeded=True, listitem=playlist[0])
    else:
        xbmcplugin.setResolvedUrl(handle=int(__settings__.get_argv(1)), succeeded=False, listitem=None)


def play_streams(streams, name=None, logo=None):
    log_debug('play_streams', 2)
    log_debug('streams: %s' % streams, 3)
    log_debug('name: %s' % name, 3)
    log_debug('logo: %s' % logo, 3)
    if (__prompt__ and xbmc.Player().isPlayingAudio()):
        if (utils.yesno(__addonname__, __settings__.get_string(3005))):
            add_streams(streams, name, logo)
    else:
        add_streams(streams, name, logo)


def log_error(msg):
    print '%s: ERROR: %s' % (__addonname__, utils.normalize_unicode(msg))


def log_debug(msg, dbglvl):
    if __debuglevel__ >= int(dbglvl):
        print '%s: DEBUG: %s' % (__addonname__, utils.normalize_unicode(msg))


def get_logo_colour():
    if __iconcolour__ == 0:
        return 'white'
    elif __iconcolour__ == 1:
        return 'black'
    elif __iconcolour__ == 2:
        return 'red'
    else:
        return 'white'


def get_format(id, formats):
    if __settings__.get(('format-%s') % id) == "true":
        if len(formats) > 0:
            formats = '%s,' % (formats)
        formats = '%s%s' % (formats, id)
    return formats


def get_formats():
    formats = ''
    for format in __formatscache__.get()[0]:
        formats = get_format(format['guide_id'], formats)
    return formats


def get_genre_name(id):
    if id is None or len(id) == 0:
        return ''
    for genre in __genrescache__.get()[0]:
        if genre['guide_id'] == id:
            return genre['text']
    return ''

# Set some global values.
__xbmcrevision__ = xbmc.getInfoLabel('System.BuildVersion')
__addonid__ = 'plugin.audio.tuneinradio'
__partnerid__ = 'yvcOjvJP'
__author__ = 'Brian Hornsby'

# Initialise settings.
__settings__ = settings.Settings(__addonid__, sys.argv)

# Initialise caches.
_recentscache = cache.Cache(
    __settings__.get_datapath(), 'recents.db', __settings__.get('recents'))
__downloadscache__ = cache.Cache(__settings__.get_datapath(), 'downloads.db')
__showscache__ = cache.Cache(__settings__.get_datapath(), 'shows.db')
__genrescache__ = cache.Cache(__settings__.get_datapath(), 'genres.db')
__formatscache__ = cache.Cache(__settings__.get_datapath(), 'formats.db')

# Get addon information.
__addonname__ = __settings__.get_name()
__version__ = __settings__.get_version()

# Get addon settings values.
__username__ = __settings__.get('username')
__password__ = __settings__.get('password')
__latlon__ = __settings__.get('latlon')
__locale__ = __settings__.get('locale')
__iconcolour__ = __settings__.get('iconcolour')
__prompt__ = __settings__.get('prompt') == "true"
__featured__ = __settings__.get('featured') == "true"
__local__ = __settings__.get('local') == "true"
__debuglevel__ = __settings__.get('debuglevel')
__enabledownloads__ = __settings__.get('enabledownloads') == "true"
__onlyfavourites__ = __settings__.get('onlyfavourites') == "true"

# Initialise parameters.
__params__ = utils.get_params(__settings__.get_argv(2))
__path__ = utils.get_value(__params__, 'path')
__id__ = utils.get_value(__params__, 'id')
__fanart__ = os.path.join(__settings__.get_path(), 'fanart.jpg')
if __settings__.get('fanart') == "true" and int(__settings__.get_argv(1)) != -1:
    xbmcplugin.setPluginFanart(int(__settings__.get_argv(1)), __fanart__)

modtime = __formatscache__.lastupdate()
if modtime is None or modtime > (__settings__.get('cacheupdate') * 60 * 60) or len(__formatscache__.get()) == 0:
    __formatscache__.clear()
    __formatscache__.add(tunein.TuneIn(__partnerid__).describe_formats())
__formats__ = get_formats()

# Get mac address to be used as serial.
# Note: function seems to occasionally return 'Busy', so added workaround.
mac_address = utils.mac_address()
if mac_address == 'Busy':
    mac_address = None

# Initialise tunein.
__tunein__ = tunein.TuneIn(__partnerid__, serial=mac_address, locale=__locale__, formats=__formats__, https=(
    __settings__.get('https') == "true"), debug=(__debuglevel__ > 0))

modtime = __genrescache__.lastupdate()
if modtime is None or modtime > (__settings__.get('cacheupdate') * 60 * 60):
    __genrescache__.clear()
    __genrescache__.add(__tunein__.describe_genres())

log_debug('Addon: %s' % __addonname__, 1)
log_debug('Version: %s' % __version__, 1)
log_debug('Params: %s: %s' % (__path__, __params__), 1)

__category__ = utils.get_value(__params__, 'c')
__filter__ = utils.get_value(__params__, 'filter')
if __path__ == 'browse':
    try:
        __offset__ = utils.get_value(__params__, 'offset')
        __pivot__ = utils.get_value(__params__, 'pivot')

        # Display users presets.
        if __id__ == 'presets':
            if __username__ is None or len(__username__) == 0:
                utils.ok(__addonname__, __settings__.get_string(
                    3001), __settings__.get_string(3002))
            else:
                results = __tunein__.browse_presets(username=__username__)
                process_tunein_json(results)
                xbmcplugin.endOfDirectory(int(__settings__.get_argv(1)))

        # Browse for a station/show/topic/category.
        elif len(__id__) > 0:
            results = __tunein__.browse(
                id=__id__, filter=__filter__, offset=__offset__, pivot=__pivot__, username=__username__)
            process_tunein_json(results)
            xbmcplugin.endOfDirectory(int(__settings__.get_argv(1)))

        # Display local stations and shows.
        elif __category__ == 'local':
            results = __tunein__.browse_local(
                username=__username__, latlon=__latlon__)
            process_tunein_json(results)
            xbmcplugin.endOfDirectory(int(__settings__.get_argv(1)))

        # Display browsing channels.
        elif len(__category__) > 0:
            results = __tunein__.browse(
                channel=__category__, filter=__filter__, offset=__offset__)
            process_tunein_json(results)
            xbmcplugin.endOfDirectory(int(__settings__.get_argv(1)))

        # Display browsing channels.
        elif len(__filter__) > 0:
            results = __tunein__.browse(filter=__filter__)
            process_tunein_json(results)
            xbmcplugin.endOfDirectory(int(__settings__.get_argv(1)))

        # Display main browsing categories.
        else:
            results = __tunein__.browse()
            process_tunein_json(results)
            xbmcplugin.endOfDirectory(int(__settings__.get_argv(1)))

    except __tunein__.TuneInError as e:
        utils.ok(__addonname__, __settings__.get_string(3011),
                 __settings__.get_string(3010))
        log_error('TuneInError: %s %s' % (e.status, e.fault))
    except urllib2.URLError as e:
        utils.ok(__addonname__, __settings__.get_string(3009),
                 __settings__.get_string(3010))
        log_error('URLError: %s' % e)

# Display shows and stations downloaded by user.
elif __path__ == 'downloads':
    try:
        results = __downloadscache__.get()
        for download in results:
            topic = download[0]
            path = download[1]
            if __tunein__.is_topic_id(topic['guide_id']):
                add_topic(topic, path)
        xbmcplugin.endOfDirectory(int(__settings__.get_argv(1)))

    except __tunein__.TuneInError as e:
        utils.ok(__addonname__, __settings__.get_string(3011),
                 __settings__.get_string(3010))
        log_error('TuneInError: %s %s' % (e.status, e.fault))
    except urllib2.URLError as e:
        utils.ok(__addonname__, __settings__.get_string(3009),
                 __settings__.get_string(3010))
        log_error('URLError: %s' % e)

# Display recent shows and stations played by user.
elif __path__ == 'recents':
    try:
        results = _recentscache.get()
        for recent in results:
            if __tunein__.is_station_id(recent['guide_id']):
                add_station(recent)
            elif __tunein__.is_show_id(recent['guide_id']):
                add_show(recent)
            elif __tunein__.is_custom_url_id(recent['guide_id']):
                add_custom_url(recent, presets=False)
        xbmcplugin.endOfDirectory(int(__settings__.get_argv(1)))

    except __tunein__.TuneInError as e:
        utils.ok(__addonname__, __settings__.get_string(3011),
                 __settings__.get_string(3010))
        log_error('TuneInError: %s %s' % (e.status, e.fault))
    except urllib2.URLError as e:
        utils.ok(__addonname__, __settings__.get_string(3009),
                 __settings__.get_string(3010))
        log_error('URLError: %s' % e)

# Search for a radio station.
elif __path__ == 'search':
    try:
        searchstring = utils.keyboard(heading=__settings__.get_string(3000))
        if (searchstring and len(searchstring) > 0):
            results = __tunein__.search(searchstring, 'standard')
            process_tunein_json(results)
            xbmcplugin.endOfDirectory(int(__settings__.get_argv(1)))

    except __tunein__.TuneInError as e:
        utils.ok(__addonname__, __settings__.get_string(3011),
                 __settings__.get_string(3010))
        log_error('TuneInError: %s %s' % (e.status, e.fault))
    except urllib2.URLError as e:
        utils.ok(__addonname__, __settings__.get_string(3009),
                 __settings__.get_string(3010))
        log_error('URLError: %s' % e)

# Play custom url.
elif __path__ == 'custom-url':
    try:
        streams = []
        if __id__ and __tunein__.is_custom_url_id(__id__):
            url = utils.get_value(__params__, 'url')
        else:
            url = utils.keyboard(heading=__settings__.get_string(3006))

        if (url and len(url) > 0):
            streams.append(url)
            results = __tunein__.search_stream(url)
            name = utils.get_value(__params__, 'name')
            logo = utils.get_value(__params__, 'logo')
            known_id = None
            for station in results:
                if ('guide_id' in station and __tunein__.is_station_id(station['guide_id'])):
                    known_id = station['guide_id']
                    if (utils.yesno(__addonname__, __settings__.get_string(3007) % station['text'], __settings__.get_string(3008))):
                        result = __tunein__.preset_add(
                            __username__, __password__, id=known_id)
                        break

            if known_id is None and (__id__ is None or not __tunein__.is_custom_url_id(__id__)):
                if (utils.yesno(__addonname__, __settings__.get_string(3012), __settings__.get_string(3013))):
                    name = utils.keyboard(
                        heading=__settings__.get_string(3014))
                    result = __tunein__.preset_add(
                        __username__, __password__, url=url, name=name)

            play_streams(streams, name, logo)
            if __id__ and __tunein__.is_custom_url_id(__id__):
                _recentscache.add({'URL': url, 'guide_id': __id__, 'image': logo, 'text': utils.get_value(
                    __params__, 'name')}, 'guide_id')

    except __tunein__.TuneInError as e:
        utils.ok(__addonname__, __settings__.get_string(3011),
                 __settings__.get_string(3010))
        log_error('TuneInError: %s %s' % (e.status, e.fault))
    except urllib2.URLError as e:
        utils.ok(__addonname__, __settings__.get_string(3009),
                 __settings__.get_string(3010))
        log_error('URLError: %s' % e)

# Play station.
elif __path__ == 'tune':
    try:
        result = []
        if len(utils.get_value(__params__, 'file')) > 0:
            result = [utils.get_value(__params__, 'file')]
        elif __tunein__.is_station_id(__id__) or __tunein__.is_topic_id(__id__):
            result = __tunein__.tune(__id__)
        if len(result) > 0:
            play_streams(result, utils.get_value(
                __params__, 'name'), utils.get_value(__params__, 'logo'))
            recent = []
            if __tunein__.is_station_id(__id__):
                recent = __tunein__.describe_station(__id__)
                if recent and len(recent) > 0:
                    _recentscache.add(recent[0], 'guide_id')
            elif __tunein__.is_topic_id(__id__):
                topic = __tunein__.describe_topic(__id__)
                if topic and len(topic) > 0:
                    recent = __tunein__.describe_show(topic[0]['show_id'])
                    if recent and len(recent) > 0:
                        _recentscache.add(recent[0], 'guide_id')

    except __tunein__.TuneInError as e:
        utils.ok(__addonname__, __settings__.get_string(3011),
                 __settings__.get_string(3010))
        log_error('TuneInError: %s %s' % (e.status, e.fault))
    except urllib2.URLError as e:
        utils.ok(__addonname__, __settings__.get_string(3009),
                 __settings__.get_string(3010))
        log_error('URLError: %s' % e)

# Display shows.
elif __path__ == 'tune-show':
    try:
        if __category__ is None or len(__category__) == 0:
            __category__ = 'pbrowse'
        results = __tunein__.tune_show(
            __id__, category=__category__, filter=__filter__)
        process_tunein_json(results)
        xbmcplugin.endOfDirectory(int(__settings__.get_argv(1)))

    except __tunein__.TuneInError as e:
        utils.ok(__addonname__, __settings__.get_string(3011),
                 __settings__.get_string(3010))
        log_error('TuneInError: %s %s' % (e.status, e.fault))
    except urllib2.URLError as e:
        utils.ok(__addonname__, __settings__.get_string(3009),
                 __settings__.get_string(3010))
        log_error('URLError: %s' % e)

# Perform add or remove presets or move presets up or down.
elif __path__ == 'add' or __path__ == 'remove' or __path__ == 'up' or __path__ == 'down':
    if __username__ and len(__username__) > 0 and __password__ and len(__password__) > 0 and (__tunein__.is_station_id(__id__) or __tunein__.is_show_id(__id__) or __tunein__.is_custom_url_id(__id__)):
        try:
            __num__ = utils.get_value(__params__, 'num')
            if __num__ and len(__num__) > 0:
                __num__ = int(__num__)

            if __path__ == 'add':
                result = __tunein__.preset_add(
                    __username__, __password__, id=__id__)
            elif __path__ == 'remove':
                result = __tunein__.preset_remove(
                    __username__, __password__, id=__id__)
                xbmc.executebuiltin('Container.Refresh')
            elif __path__ == 'up' and __num__ > 1:
                result = __tunein__.preset_add(
                    __username__, __password__, id=__id__, presetnumber=(__num__ - 1))
                xbmc.executebuiltin('Container.Refresh')
            elif __path__ == 'down' and __num__ != -1:
                result = __tunein__.preset_add(
                    __username__, __password__, id=__id__, presetnumber=(__num__ + 1))
                xbmc.executebuiltin('Container.Refresh')

        except __tunein__.TuneInError as e:
            utils.ok(__addonname__, __settings__.get_string(
                3011), __settings__.get_string(3010))
            log_error('TuneInError: %s %s' % (e.status, e.fault))
        except urllib2.URLError as e:
            utils.ok(__addonname__, __settings__.get_string(
                3009), __settings__.get_string(3010))
            log_error('URLError: %s' % e)
    else:
        utils.ok(__addonname__, __settings__.get_string(3001),
                 __settings__.get_string(3002))

# Remove download file from cache.
elif __path__ == 'remove-download':
    if __tunein__.is_topic_id(__id__):
        results = __downloadscache__.get()
        removed = False
        for download in results:
            if download[0]['guide_id'] == __id__:
                __downloadscache__.remove(download)
                removed = True
        if removed:
            xbmc.executebuiltin('Container.Refresh')

# Download file.
elif __path__ == 'download':
    if len(__settings__.get('downloadpath')) > 0:
        downloadpath = __settings__.get('downloadpath')
    else:
        downloadpath = __settings__.get_datapath()
    topic = __tunein__.describe_topic(__id__)
    result = None
    if topic and len(topic) >= 1 and 'url' in topic[0] and 'stream_type' in topic[0] and topic[0]['stream_type'] == 'download':
        url = topic[0]['url']
        if len(url) == 0:
            utils.ok(__addonname__, __settings__.get_string(
                3015), __settings__.get_string(3016))
        else:
            downloadpath = os.path.join(downloadpath, topic[0]['show_title'])
            downloadpath = os.path.join(downloadpath, topic[0]['title'])
            if __settings__.get('downloadbackground') == "true":
                script = __settings__.get_path('resources/lib/xbmcdownload.py')
                dbg = 'False'
                if __debuglevel__ > 0:
                    dbg = 'True'
                command = 'XBMC.RunScript(%s, %s, %s, %s, %s, %s)' % (
                    script, url, urllib.quote_plus(downloadpath), __addonid__, True, dbg)
                log_debug('Execute builtin command: %s' % command, 3)
                xbmc.executebuiltin(command)
            else:
                result = download.download(
                    url, downloadpath, addonid=__addonid__, debug=(__debuglevel__ > 0))
                if result[0]:
                    show = __tunein__.describe_show(topic[0]['show_id'])
                    if show and len(show) > 0:
                        download = (topic[0], result[1])
                        __downloadscache__.add(download)
                else:
                    utils.ok(__addonname__, __settings__.get_string(
                        3015), __settings__.get_string(3010))

# Refresh display.
elif __path__ == 'refresh':
    xbmc.executebuiltin('Container.Refresh')

# Add station/show to XBMC favourites.
elif __path__ == 'xbmc-favourites':
    log_debug('Adding %s to XBMC favourites' % utils.get_value(__params__, 'name'), 1)
    name = utils.get_value(__params__, 'name')
    logo = utils.get_value(__params__, 'logo')
    command = 'PlayMedia(\"%s\")' % (utils.add_params(root='plugin://%s/' % (__addonid__), params={'logo': logo, 'path': 'tune', 'id': utils.get_value(__params__, 'id'), 'name': name}))
    if not utils.add_to_favourites(name, logo, command):
        utils.ok(__addonname__, __settings__.get_string(3017))

# Display main menu.
else:
    __showscache__.clear()

    if __onlyfavourites__:
        # Display users presets.
        if __username__ is None or len(__username__) == 0:
            utils.ok(__addonname__, __settings__.get_string(
                3001), __settings__.get_string(3002))
        else:
            results = __tunein__.browse_presets(username=__username__)
            process_tunein_json(results)
            xbmcplugin.endOfDirectory(int(__settings__.get_argv(1)))

    else:
        # Display main menu.
        contextmenu = [(__settings__.get_string(
            1011), 'XBMC.RunPlugin(%s?path=refresh)' % (__settings__.get_argv(0), ))]

        iconImage = __settings__.get_path(
            '%s%s%s' % ('resources/images/', get_logo_colour(), '/favourites-32.png'))
        thumbnailImage = __settings__.get_path(
            '%s%s%s' % ('resources/images/', get_logo_colour(), '/favourites-256.png'))
        liz = xbmcgui.ListItem(
            __settings__.get_string(1000), iconImage=iconImage, thumbnailImage=thumbnailImage)
        liz.addContextMenuItems(items=contextmenu, replaceItems=True)
        if __settings__.get('fanart') == "true":
            liz.setProperty('fanart_image', __fanart__)
        u = utils.add_params(root=__settings__.get_argv(
            0), params={'path': 'browse', 'id': 'presets'})
        ok = xbmcplugin.addDirectoryItem(handle=int(
            __settings__.get_argv(1)), url=u, listitem=liz, isFolder=True)

        if _recentscache.len() > 0:
            iconImage = __settings__.get_path('%s%s%s' % (
                'resources/images/', get_logo_colour(), '/recents-32.png'))
            thumbnailImage = __settings__.get_path('%s%s%s' % (
                'resources/images/', get_logo_colour(), '/recents-256.png'))
            liz = xbmcgui.ListItem(__settings__.get_string(
                1001), iconImage=iconImage, thumbnailImage=thumbnailImage)
            liz.addContextMenuItems(items=contextmenu, replaceItems=True)
            if __settings__.get('fanart') == "true":
                liz.setProperty('fanart_image', __fanart__)
            u = utils.add_params(
                root=__settings__.get_argv(0), params={'path': 'recents'})
            ok = xbmcplugin.addDirectoryItem(handle=int(
                __settings__.get_argv(1)), url=u, listitem=liz, isFolder=True)

        if __downloadscache__.len() > 0:
            iconImage = __settings__.get_path('%s%s%s' % (
                'resources/images/', get_logo_colour(), '/downloads-32.png'))
            thumbnailImage = __settings__.get_path('%s%s%s' % (
                'resources/images/', get_logo_colour(), '/downloads-256.png'))
            liz = xbmcgui.ListItem(__settings__.get_string(
                1015), iconImage=iconImage, thumbnailImage=thumbnailImage)
            liz.addContextMenuItems(items=contextmenu, replaceItems=True)
            if __settings__.get('fanart') == "true":
                liz.setProperty('fanart_image', __fanart__)
            u = utils.add_params(
                root=__settings__.get_argv(0), params={'path': 'downloads'})
            ok = xbmcplugin.addDirectoryItem(handle=int(
                __settings__.get_argv(1)), url=u, listitem=liz, isFolder=True)

        iconImage = __settings__.get_path('%s%s%s' % (
            'resources/images/', get_logo_colour(), '/browse-32.png'))
        thumbnailImage = __settings__.get_path('%s%s%s' % (
            'resources/images/', get_logo_colour(), '/browse-256.png'))
        liz = xbmcgui.ListItem(
            __settings__.get_string(1002), iconImage=iconImage, thumbnailImage=thumbnailImage)
        liz.addContextMenuItems(items=contextmenu, replaceItems=True)
        if __settings__.get('fanart') == "true":
            liz.setProperty('fanart_image', __fanart__)
        u = utils.add_params(
            root=__settings__.get_argv(0), params={'path': 'browse'})
        ok = xbmcplugin.addDirectoryItem(handle=int(
            __settings__.get_argv(1)), url=u, listitem=liz, isFolder=True)

        iconImage = __settings__.get_path('%s%s%s' % (
            'resources/images/', get_logo_colour(), '/search-32.png'))
        thumbnailImage = __settings__.get_path('%s%s%s' % (
            'resources/images/', get_logo_colour(), '/search-256.png')) 
        liz = xbmcgui.ListItem(
            __settings__.get_string(1003), iconImage=iconImage, thumbnailImage=thumbnailImage)
        liz.addContextMenuItems(items=contextmenu, replaceItems=True)
        if __settings__.get('fanart') == "true":
            liz.setProperty('fanart_image', __fanart__)
        u = utils.add_params(
            root=__settings__.get_argv(0), params={'path': 'search'})
        ok = xbmcplugin.addDirectoryItem(handle=int(
            __settings__.get_argv(1)), url=u, listitem=liz, isFolder=True)

        iconImage = __settings__.get_path('%s%s%s' % (
            'resources/images/', get_logo_colour(), '/stream-32.png'))
        thumbnailImage = __settings__.get_path('%s%s%s' % (
            'resources/images/', get_logo_colour(), '/stream-256.png')) 
        liz = xbmcgui.ListItem(
            __settings__.get_string(1006), iconImage=iconImage, thumbnailImage=thumbnailImage)
        liz.setProperty('IsPlayable', 'true')
        liz.addContextMenuItems(items=contextmenu, replaceItems=True)
        if __settings__.get('fanart') == "true":
            liz.setProperty('fanart_image', __fanart__)
        u = utils.add_params(
            root=__settings__.get_argv(0), params={'path': 'custom-url'})
        ok = xbmcplugin.addDirectoryItem(handle=int(__settings__.get_argv(1)),
                                         url=u,
                                         listitem=liz,
                                         isFolder=False)

        xbmcplugin.endOfDirectory(int(__settings__.get_argv(1)))
