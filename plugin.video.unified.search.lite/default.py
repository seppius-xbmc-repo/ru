# -*- coding: utf-8 -*-
# Module: default
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import xbmc
import xbmcgui
import xbmcaddon
import simplejson as json

from simpleplugin import Plugin

plugin = Plugin()
_ = plugin.initialize_gettext()

_supported_addons = []

def get_categories():
    categories = [ {'action': 'search',         'label': _('New Search...')},
                   {'action': 'search_history', 'label': _('Search History')} ]

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
            'fanart': plugin.fanart
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
            progress.update(100 * i / total_addons, line2=addon['name'])
            if (progress.iscanceled()): 
                succeeded = False
                break
            
            path = []
            path.append('plugin://')
            path.append(addon['id'])
            path.append('/?unified=True&')
            path.append(addon['us_command'])
            path.append(keyword.decode('utf-8'))
            
            directory = ''.join(path)
            video_list = get_directory(directory)
            listing.extend(make_items(video_list, addon['name']))
        
        progress.close()
        
        if succeeded and len(listing) == 0:
            succeeded = False
            show_info_notification(_('Nothing found!'))
        
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

    return plugin.create_listing(listing, succeeded=succeeded, content='files', sort_methods=(1,2))

@plugin.action()
def search_results( params ):
    
    item = int(params['item'])

    with plugin.get_storage('__history__.pcl') as storage:
        history = storage.get('history', [])
    
    item_content = history[item]
    
    listing = []
    listing.append({'label': _('Search Again...'),
                    'url':   plugin.get_url(action='search', keyword=item_content['keyword'], item=item)})

    listing.extend(item_content.get('listing', []))
    return plugin.create_listing(listing, content='files', sort_methods=(1,2))

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
        listing.append({'label': item['keyword'],
                        'url': plugin.get_url(action='search_results', item=i)})

    return plugin.create_listing(listing, content='files')
    
def get_directory( directory ):
    request = {'jsonrpc': '2.0',
               'method': 'Files.GetDirectory',
               'params': {'properties': ['title', 'genre', 'year', 'rating', 'runtime', 'plot', 'file', 'art'],
                          'directory': directory,
                          'media': 'files'},
                'id': 1
               }
    response = xbmc.executeJSONRPC(json.dumps(request))

    plugin.log_error(response)
    
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
                          'properties': ['name']},
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

def load_supported_addons():
    enabled_addons = get_addons()
    for addon in enabled_addons:
        addon_object = xbmcaddon.Addon(addon['addonid'])
        if addon_object.getSetting('unified_search') == 'true':
            us_command = addon_object.getSetting('us_command')
            if not us_command:
                us_command = 'mode=search&keyword='
                
            addon_info = {'id':         addon['addonid'],
                          'name':       addon['name'],
                          'us_command': us_command}

            _supported_addons.append(addon_info)
    
if __name__ == '__main__':
    
    plugin.run()