# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        script.m3u.convertor
# Purpose:     Converting m3u playlists for pvr.demo add-on
# Version:     0.0.6
# Author:      Roman_V_M
#
# Created:     11.12.2012
# Copyright:   (c) Roman_V_M, 2012
# Licence:     GPL v.3: http://www.gnu.org/copyleft/gpl.html
#-------------------------------------------------------------------------------

import xbmc, xbmcaddon, xbmcgui
import sys, codecs, os, re, urllib2
from xml.dom.minidom import Document


_ADDON_NAME =   'script.m3u.convertor'
_ADDON      =   xbmcaddon.Addon(id=_ADDON_NAME)
_ADDON_PATH =   xbmc.translatePath(_ADDON.getAddonInfo('path'))
_LANGUAGE   =   _ADDON.getLocalizedString

_PVR_CONFIG =   os.path.join(_ADDON_PATH.replace(_ADDON_NAME, 'pvr.demo'), 'PVRDemoAddonSettings.xml')
_ICONS = _ADDON.getSetting('icon_path')
_START_No = _ADDON.getSetting('start_num')
if _ADDON.getSetting('encoding') == 'UTF-8':
    _ENC = 'utf-8'
else: _ENC = 'cp1251'
if _ADDON.getSetting('useproxy') == 'true':
    _PROXY = _ADDON.getSetting('proxyip') + ':' + _ADDON.getSetting('proxyport') + '/'


def chan_rec_create(xml_config, channels, channel_info, channel_count):
    '''
    Creating a channel entry
    '''
    channel = xml_config.createElement('channel')
    channels.appendChild(channel)
    name = xml_config.createElement('name')
    channel.appendChild(name)
    name_text = xml_config.createTextNode(channel_info[0])
    name.appendChild(name_text)
    radio = xml_config.createElement('radio')
    channel.appendChild(radio)
    radio_text = xml_config.createTextNode('0')
    radio.appendChild(radio_text)
    number = xml_config.createElement('number')
    channel.appendChild(number)
    number_text = xml_config.createTextNode(str(channel_count))
    number.appendChild(number_text)
    encryption = xml_config.createElement('encryption')
    channel.appendChild(encryption)
    encryption_text = xml_config.createTextNode('0')
    encryption.appendChild(encryption_text)
    icon = xml_config.createElement('icon')
    channel.appendChild(icon)
    icon_text = xml_config.createTextNode(_ICONS + re.sub('[\\\/:*?|<>]', '-', channel_info[0]) + '.png')
    icon.appendChild(icon_text)
    stream = xml_config.createElement('stream')
    channel.appendChild(stream)
    stream_text = xml_config.createTextNode(channel_info[1])
    stream.appendChild(stream_text)


def groups_create(xml_config, demo, groups_list):
    channelgroups = xml_config.createElement('channelgroups')
    demo.appendChild(channelgroups)
    for group in groups_list.keys():
        group_entry = xml_config.createElement('group')
        channelgroups.appendChild(group_entry)
        name = xml_config.createElement('name')
        group_entry.appendChild(name)
        name_text = xml_config.createTextNode(group)
        name.appendChild(name_text)
        radio = xml_config.createElement('radio')
        group_entry.appendChild(radio)
        radio_text = xml_config.createTextNode('0')
        radio.appendChild(radio_text)
        members = xml_config.createElement('members')
        group_entry.appendChild(members)
        for channel in groups_list[group]:
            member = xml_config.createElement('member')
            members.appendChild(member)
            member_text = xml_config.createTextNode(str(channel))
            member.appendChild(member_text)


def convert_file(playlist):
    '''
    Playlist parser
    '''
    channel_count = 0
    EOL = '\n'
    header = playlist.readline()
    # Catching an exeption if the 1-st string in a *nix-formatted .m3u is empty
    try:
        if header[-2] == '\r':
            EOL = '\r' + EOL # Windows EOL convention
    except IndexError: pass
    if '#EXTM3U' in header:
        xml_config = Document()
        comment = xml_config.createComment(' This file is created by m3u2xml convertor ')
        xml_config.appendChild(comment)
        demo = xml_config.createElement('demo')
        xml_config.appendChild(demo)
        channels = xml_config.createElement('channels')
        demo.appendChild(channels)
        groups = xml_config.createElement('groups')
        demo.appendChild(groups)
        channel_info = []
        groups_list = {}
        # Extra protocols can be added if necessary
        PROTOCOLS = ['udp', 'http', 'rtmpe', 'rtp', 'rtsp']
        try:
            start_number = int(_START_No)
        except ValueError:
            start_number = 1
        for line in playlist:
            if line.split(':')[0] == '#EXTINF':
                channel_info.append(line.split(',')[-1].replace(EOL, '').decode(_ENC))
                if 'group-title=' in line and _ADDON.getSetting('groups') == 'true':
                    current_group = re.search(
                    r'group-title=".*?"', line).group().replace('group-title=', '').replace('\"', '').decode(_ENC)
                    groups_list[current_group] = []
            elif line.split(':')[0] in PROTOCOLS:
                if _ADDON.getSetting('useproxy') == 'true':
                    channel_info.append(_PROXY + line.replace(EOL, '').replace(':/', '').replace('@', ''))
                else:
                    channel_info.append(line.replace(EOL, ''))
                channel_num = start_number + channel_count
                chan_rec_create(xml_config, channels, channel_info, channel_num)
                if groups_list:
                    groups_list[current_group].append(channel_num)
                channel_count += 1
                channel_info = []
        if groups_list:
            groups_create(xml_config, demo, groups_list)
        out_xml = codecs.open(_PVR_CONFIG, encoding='utf-8', mode='w')
        xml_config.writexml(out_xml, newl='\n')
        out_xml.close()
    playlist.close()
    return channel_count

def main():
    if os.path.exists(_PVR_CONFIG):
        dialog = xbmcgui.Dialog()
        reply = dialog.yesno(
            _LANGUAGE(100612).encode('utf-8'), _LANGUAGE(100613).encode('utf-8'), _LANGUAGE(100614).encode('utf-8'))
        if reply:
            try:
                if _ADDON.getSetting('local') == 'true':
                    path = _ADDON.getSetting('path')
                    xbmc.log(_ADDON_NAME + ': Opening m3u file ' + path, xbmc.LOGNOTICE)
                    playlist = open(path, mode='r')
                else:
                    url = _ADDON.getSetting('url')
                    xbmc.log(_ADDON_NAME + ': Opening m3u url ' + url, xbmc.LOGNOTICE)
                    playlist = urllib2.urlopen(url)
            except (urllib2.URLError, ValueError, IOError):
                xbmc.log(_ADDON_NAME + ': Playlist not found', xbmc.LOGERROR)
                xbmc.executebuiltin('Notification(' +
                            _LANGUAGE(100605).encode('utf-8') + ',' + _LANGUAGE(100606).encode('utf-8') + '), 3000')
            else:
                entries_count = convert_file(playlist)
                if entries_count:
                    channels = str(entries_count)
                    xbmc.log(_ADDON_NAME + ': Successfully imported ' + channels + ' channels', xbmc.LOGNOTICE)
                    dialog.ok(  _LANGUAGE(100607).encode('utf-8'),
                                _LANGUAGE(100608).encode('utf-8') + ' ' + channels,
                                _LANGUAGE(100615).encode('utf-8'),
                                _LANGUAGE(100616).encode('utf-8'))
                else:
                    xbmc.log(_ADDON_NAME + ': Invalid playlist', xbmc.LOGERROR)
                    xbmc.executebuiltin('Notification(' +
                        _LANGUAGE(100609).encode('utf-8') + ',' + _LANGUAGE(100610).encode('utf-8') + '), 3000')
    else:
        xbmc.log(_ADDON_NAME + ': pvr.demo addon not found', xbmc.LOGERROR)
        xbmc.executebuiltin('Notification(' +
            _LANGUAGE(100609).encode('utf-8') + ',' + _LANGUAGE(100611).encode('utf-8') + '), 3000')


if __name__ == '__main__':
    main()
