# -*- coding: utf-8 -*-
# Module: default
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import xbmc
import xbmcgui
import xbmcaddon
import urllib
import simplejson as json

from simpleplugin import Plugin

plugin = Plugin()
_ = plugin.initialize_gettext()

_supported_addons = []

def get_categories():
    categories = [ {'action': 'search',           'label': _('New Search'), 'is_folder': False},
                   {'action': 'search_results',   'label': _('Last Search')},
                   {'action': 'search_history',   'label': _('Search History')},
                   {'action': 'supported_addons', 'label': _('Supported Add-ons')} ]

    return categories

def show_info_notification(text):
    xbmcgui.Dialog().notification(plugin.addon.getAddonInfo('name'), text)

def make_items( video_list, addon_name ):
    listing = []

    for video_item in video_list:
        item_info = {'label': '%s [%s]' % (video_item['label'], addon_name),
                     'info':  { 'video': {#'year':      video_item.get('year', 0),
                                          #'title':     video.get('title'),
                                          'genre':     video_item.get('genres', ''),
                                          'rating':    video_item.get('rating', 0),
                                          'duration':  video_item.get('runtime', ''),
                                          'plot':      video_item.get('plot', '')} },
                     'url':         video_item.get('file'),
                     'is_playable': (video_item['filetype'] == 'file'),
                     'is_folder':   (video_item['filetype'] == 'directory'),
                     'art':         { 'poster': video_item['art'].get('poster') },
                     'fanart':      video_item['art'].get('fanart'),
                     'thumb':       video_item['art'].get('thumb')}
        listing.append(item_info)

    return listing

@plugin.action()
def root( params ):

    listing = []

    categories = get_categories()
    for category in categories:
        url = plugin.get_url(action=category['action'])

        listing.append({
            'label': category['label'],
            'url': url,
            'icon': plugin.icon,
            'fanart': plugin.fanart,
            'is_folder': category.get('is_folder', True)
        })

    return plugin.create_listing(listing, content='files')

@plugin.action()
def search( params ):

    keyword = params.get('keyword','')
    item = params.get('item')

    succeeded = False

    if keyword == '':
        kbd = xbmc.Keyboard()
        kbd.setDefault('')
        kbd.setHeading(_('Search'))
        kbd.doModal()
        if kbd.isConfirmed():
            keyword = kbd.getText()


    listing = []
    if keyword != '':
        succeeded = True

        load_supported_addons()

        progress = xbmcgui.DialogProgress()
        progress.create(_('Search'), _('Please wait. Searching...'))

        total_addons = len(_supported_addons)
        for i, addon in enumerate(_supported_addons):
            result_string = '%s: %d' % (_('Search results'), len(listing))
            progress.update(100 * i / total_addons, line2=addon['name'], line3=result_string)
            if (progress.iscanceled()):
                succeeded = False
                break

            path = []
            path.append('plugin://')
            path.append(addon['id'])
            path.append('/?usearch=True&')
            path.append(addon['us_command'])
            #path.append(keyword.decode('utf-8'))
            path.append(urllib.quote(keyword))

            directory = ''.join(path)
            
            video_list = get_directory(directory)
            listing.extend(make_items(video_list, addon['name']))

        progress.close()

        if succeeded:
            with plugin.get_storage('__history__.pcl') as storage:
                history = storage.get('history', [])

                item_content = {'keyword': keyword, 'listing': listing}
                if item:
                    history[int(item)] = item_content
                else:
                    history.insert(0, item_content)

                if len(history) > plugin.history_length:
                    history.pop(-1)
                storage['history'] = history

        if succeeded and len(listing) == 0:
            succeeded = False
            show_info_notification(_('Nothing found!'))
    if succeeded:
        execute_addon( 'action=search_results&update=true' )

@plugin.action()
def search_results( params ):

    item = int(params.get('item', '0'))
    update_listing = (params.get('update') == 'true')

    listing = []

    with plugin.get_storage('__history__.pcl') as storage:
        history = storage.get('history', [])

    if len(history) >= (item + 1):
        item_content = history[item]

        #listing.append({'label': _('Search Again...'),
        #                'url':   plugin.get_url(action='search', keyword=item_content['keyword'], item=item)})

        listing.extend(item_content.get('listing', []))

    return plugin.create_listing(listing, content='files', sort_methods=(1,2), update_listing=update_listing)

@plugin.action()
def search_history( params ):
    history_length = plugin.history_length

    with plugin.get_storage('__history__.pcl') as storage:
        history = storage.get('history', [])

        if len(history) > history_length:
            history[history_length - len(history):] = []
            storage['history'] = history

    listing = []
    for i, item in enumerate(history):
        listing.append({'label': '%s [%d]' % (item['keyword'], len(item['listing'])),
                        'url': plugin.get_url(action='search_results', item=i),
                        'icon': plugin.icon,
                        'fanart': plugin.fanart})

    return plugin.create_listing(listing, content='files')

@plugin.action()
def supported_addons( params ):
    load_supported_addons(True)

    update_listing = (params.get('update') == 'true')

    listing = []
    for addon in _supported_addons:
        status = '[V]' if addon['united_search'] else '[X]'
        label = '[B]%s[/B] %s' % (status, addon['name'])
        change_status_title = _('Disable') if addon['united_search'] else _('Enable')

        context_menu = [(_('Settings'), 'RunPlugin(%s)' % plugin.get_url(action='addon_open_settings', id=addon['id'])),
                        (change_status_title, 'RunPlugin(%s)' % plugin.get_url(action='addon_change_status', id=addon['id']))]
        item_info = {'label':       label,
                     'sorttitle':   addon['name'],
                     'info':        { 'video': {'plot': addon['description']} },
                     'url':         'plugin://%s/' % (addon['id']),
                     'context_menu': context_menu,
                     'replaceItems': True,
                     'fanart':       addon['fanart'],
                     'thumb':        addon['thumbnail']}
        listing.append(item_info)

    return plugin.create_listing(listing, content='files', sort_methods=(26,27), update_listing=update_listing)

@plugin.action()
def addon_open_settings( params ):
    addon_object = xbmcaddon.Addon(params['id'])
    addon_object.openSettings()

@plugin.action()
def addon_change_status( params ):
    addon_object = xbmcaddon.Addon(params['id'])
    united_search = addon_object.getSetting('united_search')
    addon_object.setSetting('united_search', 'false' if united_search == 'true' else 'true')

    execute_addon( 'action=supported_addons&update=true' )

def execute_addon( params ):
    request = {'jsonrpc': '2.0',
               'method': 'Addons.ExecuteAddon',
               'params': {'addonid': plugin.id,
                          'params': params,
                          'wait': False},
                'id': 1
               }
    response = xbmc.executeJSONRPC(json.dumps(request))

def get_directory( directory ):
    request = {'jsonrpc': '2.0',
               'method': 'Files.GetDirectory',
               'params': {'properties': ['title', 'genre', 'year', 'rating', 'runtime', 'plot', 'file', 'art'],
                          'directory': directory,
                          'media': 'files'},
                'id': 1
               }
    response = xbmc.executeJSONRPC(json.dumps(request))

    j = json.loads(response)
    result = j.get('result')
    if result:
        files = result.get('files', [])
    else:
        files = []

    return files

def get_addons():
    request = {'jsonrpc': '2.0',
               'method': 'Addons.GetAddons',
               'params': {'type': 'xbmc.addon.video',
                          'content': 'video',
                          'enabled': True,
                          'properties': ['name', 'fanart', 'thumbnail', 'description']},
                'id': 1
               }
    response = xbmc.executeJSONRPC(json.dumps(request))

    j = json.loads(response)
    result = j.get('result')
    if result:
        addons = result.get('addons', [])
    else:
        addons = []

    return addons

def load_supported_addons( all_supported=False ):
    enabled_addons = get_addons()
    for addon in enabled_addons:
        addon_object = xbmcaddon.Addon(addon['addonid'])
        united_search = addon_object.getSetting('united_search')
        if united_search == 'true' or all_supported and united_search == 'false':
            us_command = addon_object.getSetting('us_command')
            if not us_command:
                us_command = 'mode=search&keyword='

            addon_info = {'id':             addon['addonid'],
                          'name':           addon['name'],
                          'us_command':     us_command,
                          'united_search': (united_search == 'true'),
                          'description':    addon['description'],
                          'thumbnail':      addon['thumbnail'],
                          'fanart':         addon['fanart']}

            _supported_addons.append(addon_info)

if __name__ == '__main__':

    plugin.run()