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

import sys
import os

import urllib
import urllib2
import re

import ConfigParser
import xml.dom.minidom as minidom

if sys.version_info >= (2, 7):
    import json as _json
else:
    import simplejson as _json

from . import astralradio as astralradio
from . import streamtheworld as streamtheworld

BASE_URL = 'opml.radiotime.com/'


class TuneIn:

    class TuneInError(Exception):

        ''' Exception raised when an error or invalid response is received.
        '''
        def __init__(self, status, fault, faultcode=''):
            self.status = status
            self.fault = fault
            self.faultcode = faultcode

        def __str__(self):
            return repr(self.status)
            return repr(self.fault)
            return repr(self.faultcode)

    def log_debug(self, msg):
        if self._debug is True:
            print 'TuneIn Library: DEBUG: %s' % msg

    def __init__(self, partnerid, serial=None, locale="en-GB", formats=None, https=True, debug=False):
        if https is False:
            self._protocol = 'http://'
        else:
            self._protocol = 'https://'
        self._global_params = []
        self._global_params.append({'param': 'partnerId', 'value': partnerid})
        if serial is not None:
            self._global_params.append({'param': 'serial', 'value': serial})
        self._global_params.append({'param': 'render', 'value': 'json'})
        self._global_params.append({'param': 'locale', 'value': locale})
        if (formats is not None):
            self._global_params.append({'param': 'formats', 'value': formats})
        self._debug = debug
        self.log_debug('Protocol: %s' % self._protocol)
        self.log_debug('Global Params: %s' % self._global_params)

    def __add_params_to_url(self, method, fnparams=None, addrender=True, addserial=True):
        params = {}

        for param in self._global_params:
            if (param['param'] == 'render' and addrender is False):
                pass
            elif (param['param'] == 'serial' and addserial is False):
                pass
            elif (param['value']):
                params[param['param']] = param['value']

        for param in fnparams:
            if (param['value']):
                params[param['param']] = param['value']

        url = '%s%s%s?%s' % (
            self._protocol, BASE_URL, method, urllib.urlencode(params))
        self.log_debug('URL: %s' % url)
        return url

    def __call_tunein(self, method, params=None):
        url = self.__add_params_to_url(method, params)
        req = urllib2.Request(url)
        f = urllib2.urlopen(req)
        result = _json.load(f)
        f.close()
        return result

    def __parse_asf(self, url):
        self.log_debug('__parse_asf')
        self.log_debug('url: %s' % url)
        streams = []
        req = urllib2.Request(url)
        f = urllib2.urlopen(req)
        config = ConfigParser.RawConfigParser()
        config.readfp(f)
        references = config.items('Reference')
        for ref in references:
            streams.append(ref[1])
        f.close()
        return streams

    def __parse_asx(self, url):
        self.log_debug('__parse_asx')
        self.log_debug('url: %s' % url)
        streams = []
        req = urllib2.Request(url)
        f = urllib2.urlopen(req)
        xmlstr = f.read().decode('ascii', 'ignore')
        dom = minidom.parseString(xmlstr)
        asx = dom.childNodes[0]
        for node in asx.childNodes:
            if (str(node.localName).lower() == 'entryref' and node.hasAttribute('href')):
                streams.append(node.getAttribute('href'))
            elif (str(node.localName).lower() == 'entryref' and node.hasAttribute('HREF')):
                streams.append(node.getAttribute('HREF'))
            elif (str(node.localName).lower() == 'entry'):
                for subnode in node.childNodes:
                    if (str(subnode.localName).lower() == 'ref' and subnode.hasAttribute('href') and not subnode.getAttribute('href') in streams):
                        streams.append(subnode.getAttribute('href'))
                    elif (str(subnode.localName).lower() == 'ref' and subnode.hasAttribute('HREF') and not subnode.getAttribute('HREF') in streams):
                        streams.append(subnode.getAttribute('HREF'))
        f.close()
        return streams

    def __parse_m3u(self, url):
        self.log_debug('__parse_m3u')
        self.log_debug('url: %s' % url)
        streams = []
        req = urllib2.Request(url)
        f = urllib2.urlopen(req)
        for line in f:
            if len(line.strip()) > 0 and not line.strip().startswith('#'):
                streams.append(line.strip())
        f.close()
        return streams

    def __parse_pls(self, url):
        self.log_debug('__parse_pls')
        self.log_debug('url: %s' % url)
        streams = []
        req = urllib2.Request(url)
        f = urllib2.urlopen(req)
        config = ConfigParser.RawConfigParser()
        config.readfp(f)
        numentries = config.getint('playlist', 'NumberOfEntries')
        while (numentries > 0):
            streams.append(
                config.get('playlist', 'File' + str(numentries)))
            numentries -= 1
        f.close()
        return streams

    def __result_ok(self, result):
        return result['head']['status'] != '200'

    def __result_status(self, result):
        return int(result['head']['status'])

    def __result_fault(self, result):
        if ('fault' in result['head']):
            return result['head']['fault']
        else:
            return ''

    def __result_fault_code(self, result):
        if ('fault_code' in result['head']):
            return result['head']['fault_code']
        else:
            return ''

    def is_category_id(self, id):
        ''' Returns True if argument is a TuneIn category id.
        '''
        if (not id or len(id) == 0 or id[0] != 'c' or not id[1:].isdigit()):
            return False
        return True

    def is_folder_id(self, id):
        ''' Returns True if argument is a TuneIn folder id.
        '''
        if (not id or len(id) == 0 or id[0] != 'f' or not id[1:].isdigit()):
            return False
        return True

    def is_genre_id(self, id):
        ''' Returns True if argument is a TuneIn genre id.
        '''
        if (not id or len(id) == 0 or id[0] != 'g' or not id[1:].isdigit()):
            return False
        return True

    def is_artist_id(self, id):
        ''' Returns True if argument is a TuneIn artist id.
        '''
        if (not id or len(id) == 0 or id[0] != 'm' or not id[1:].isdigit()):
            return False
        return True

    def is_region_id(self, id):
        ''' Returns True if argument is a TuneIn region id.
        '''
        if (not id or len(id) == 0 or id[0] != 'r' or not id[1:].isdigit()):
            return False
        return True

    def is_show_id(self, id):
        ''' Returns True if argument is a TuneIn show id.
        '''
        if (not id or len(id) == 0 or id[0] != 'p' or not id[1:].isdigit()):
            return False
        return True

    def is_station_id(self, id):
        ''' Returns True if argument is a TuneIn station id.
        '''
        if (not id or len(id) == 0 or id[0] != 's' or not id[1:].isdigit()):
            return False
        return True

    def is_topic_id(self, id):
        ''' Returns True if argument is a TuneIn topic id.
        '''
        if (not id or len(id) == 0 or id[0] != 't' or not id[1:].isdigit()):
            return False
        return True

    def is_custom_url_id(self, id):
        ''' Returns True if argument is a TuneIn custom url id.
        '''
        if (not id or len(id) == 0 or id[0] != 'u' or not id[1:].isdigit()):
            return False
        return True

    def account_auth(self, username, password):
        '''Verifies credentials associated with a TuneIn account.
        '''
        params = [{'param': 'c', 'value': 'auth'}, {'param': 'username',
                                                    'value': username}, {'param': 'password', 'value': password}]
        result = self.__call_tunein('Account.ashx', params)
        if (self.__result_ok(result)):
            raise TuneIn.TuneInError(self.__result_status(
                result), 'Account authentication failed.')
        else:
            return result['body']

    def account_create(self, username, password, email, postalcode=None, city=None, countryid=None):
        '''Creates a new TuneIn named account, optionally associating with a device if the serial parameter is not provided.
        '''
        params = [{'param': 'c', 'value': 'join'}, {'param': 'username', 'value': username}, {'param': 'password', 'value': password}, {
            'param': 'email', 'value': email}, {'param': 'postalCode', 'value': postalcode}, {'param': 'city', 'value': city}, {'param': 'countryId', 'value': countryid}]
        result = self.__call_tunein('Account.ashx', params)
        if (self.__result_ok(result)):
            raise TuneIn.TuneInError(self.__result_status(
                result), self.__result_fault(result), self.__result_fault_code(result))
        else:
            return result['body']

    def account_join(self, username, password):
        '''Associates a named TuneIn account with an existing device.

                If the user has created presets under an anonymous account, they will be merged with the named account.
        '''
        params = [{'param': 'c', 'value': 'join'}, {'param': 'username',
                                                    'value': username}, {'param': 'password', 'value': password}]
        result = self.__call_tunein('Account.ashx', params)
        if (self.__result_ok(result)):
            raise TuneIn.TuneInError(self.__result_status(
                result), self.__result_fault(result), self.__result_fault_code(result))
        else:
            return result['body']

    def account_drop(self, username, password):
        '''Removes a device from a named account. This will reset any presets associated with the device.
        '''
        params = [{'param': 'c', 'value': 'drop'}, {'param': 'username',
                                                    'value': username}, {'param': 'password', 'value': password}]
        result = self.__call_tunein('Account.ashx', params)
        if (self.__result_ok(result)):
            raise TuneIn.TuneInError(self.__result_status(
                result), self.__result_fault(result), self.__result_fault_code(result))
        else:
            return result['body']

    def account_query(self):
        '''Shows a TuneIn account name associated with a given serial value.
           Useful to determine if a particular account is already joined.
        '''
        params = [{'param': 'c', 'value': 'query'}]
        result = self.__call_tunein('Account.ashx', params)
        if (self.__result_ok(result)):
            raise TuneIn.TuneInError(self.__result_status(
                result), self.__result_fault(result), self.__result_fault_code(result))
        else:
            return result['body']

    def account_remind(self, email):
        '''Sends an account reminder to a registered email address.
        '''
        params = [{'param': 'c', 'value': 'remind'}, {'param':
                                                      'email', 'value': email}]
        result = self.__call_tunein('Account.ashx', params)
        if (self.__result_ok(result)):
            raise TuneIn.TuneInError(self.__result_status(
                result), self.__result_fault(result), self.__result_fault_code(result))
        else:
            return result['body']

    def account_reset(self, username=None, email=None):
        '''Provides an opportunity for a user to reset their account password.
        '''
        params = [{'param': 'c', 'value': 'reset'}, {'param': 'username',
                                                     'value': username}, {'param': 'email', 'value': email}]
        result = self.__call_tunein('Account.ashx', params)
        if (self.__result_ok(result)):
            raise TuneIn.TuneInError(self.__result_status(
                result), self.__result_fault(result), self.__result_fault_code(result))
        else:
            return result['body']

    def account_claim(self):
        '''Generates a simple keyphrase that a user can enter on the TuneIn.com/mydevice page to associate a device with an annoymous account.
        '''
        params = [{'param': 'c', 'value': 'claim'}]
        result = self.__call_tunein('Account.ashx', params)
        if (self.__result_ok(result)):
            raise TuneIn.TuneInError(self.__result_status(
                result), self.__result_fault(result), self.__result_fault_code(result))
        else:
            return result['body']

    def browse_local(self, username=None, latlon=None, formats=None):
        '''Creates a list of radio stations local to the caller, typically using IP geo-location.
        '''
        params = [{'param': 'c', 'value': 'local'}, {'param': 'username', 'value': username}, {
            'param': 'latlon', 'value': latlon}, {'param': 'formats', 'value': formats}]
        result = self.__call_tunein('Browse.ashx', params)
        if (self.__result_ok(result)):
            raise TuneIn.TuneInError(self.__result_status(
                result), self.__result_fault(result), self.__result_fault_code(result))
        else:
            return result['body']

    def browse_presets(self, username=None, formats=None):
        '''Shows either a list of items (if there is a single preset folder), or a list of folders for username.
        '''
        params = [{'param': 'c', 'value': 'presets'}, {'param': 'username',
                                                       'value': username}, {'param': 'formats', 'value': formats}]
        result = self.__call_tunein('Browse.ashx', params)
        if (self.__result_ok(result)):
            raise TuneIn.TuneInError(self.__result_status(
                result), self.__result_fault(result), self.__result_fault_code(result))
        else:
            return result['body']

    def browse(self, channel=None, id=None, filter=None, offset=None, pivot=None, username=None):
        '''Shows a list of the available navigation structures.
        '''
        params = [{'param': 'c', 'value': channel}, {'param': 'id', 'value': id}, {'param': 'filter', 'value': filter}, {
            'param': 'offset', 'value': offset}, {'param': 'pivot', 'value': pivot}, {'param': 'username', 'value': username}]
        result = self.__call_tunein('Browse.ashx', params)
        if (self.__result_ok(result)):
            raise TuneIn.TuneInError(self.__result_status(
                result), self.__result_fault(result), self.__result_fault_code(result))
        else:
            return result['body']

    def browse_lang(self, filter=None):
        '''Shows a list of stations based on language.
        '''
        params = [{'param': 'c', 'value': 'lang'}, {'param':
                                                    'filter', 'value': filter}]
        result = self.__call_tunein('Browse.ashx', params)
        if (self.__result_ok(result)):
            raise TuneIn.TuneInError(self.__result_status(
                result), self.__result_fault(result), self.__result_fault_code(result))
        else:
            return result['body']

    def browse_station(self, id, detail=None):
        '''Shows a list of recommendations for specified stations.
        '''
        if (not self.is_station_id(id)):
            raise TuneIn.TuneInError(-1, 'Id is not of the correct type.')
        params = [{'param': 'id', 'value': id}, {'param': 'detail',
                                                 'value': detail}]
        result = self.__call_tunein('Browse.ashx', params)
        if (self.__result_ok(result)):
            raise TuneIn.TuneInError(self.__result_status(
                result), self.__result_fault(result), self.__result_fault_code(result))
        else:
            return result['body']

    def browse_schedule(self, id, username=None, start=None, stop=None, forward=None, live=None, offset=None, autodetect=None):
        '''Shows a complete list for the current day or a specified date range.
        '''
        if (not self.is_station_id(id)):
            raise TuneIn.TuneInError(-1, 'Id is not of the correct type.')
        params = [{'param': 'c', 'value': 'schedule'}, {'param': 'id', 'value': id}, {'param': 'username', 'value': username}, {'param': 'start', 'value': start}, {'param': 'stop', 'value': stop}, {
            'param': 'forward', 'value': forward}, {'param': 'live', 'value': live}, {'param': 'offset', 'value': offset}, {'param': 'autodetect', 'value': autodetect}]
        result = self.__call_tunein('Browse.ashx', params)
        if (self.__result_ok(result)):
            raise TuneIn.TuneInError(self.__result_status(
                result), self.__result_fault(result), self.__result_fault_code(result))
        else:
            return result['body']

    def browse_playlist(self, id, username=None, start=None, stop=None):
        '''Shows a list of songs played for the current day or a specified date range.
        '''
        if (not self.is_station_id(id)):
            raise TuneIn.TuneInError(-1, 'Id is not of the correct type.')
        params = [{'param': 'c', 'value': 'playlist'}, {'param': 'id', 'value': id}, {
            'param': 'username', 'value': username}, {'param': 'start', 'value': start}, {'param': 'stop', 'value': stop}]
        result = self.__call_tunein('Browse.ashx', params)
        if (self.__result_ok(result)):
            raise TuneIn.TuneInError(self.__result_status(
                result), self.__result_fault(result), self.__result_fault_code(result))
        else:
            return result['body']

    def browse_show(self, id):
        '''Shows affiliate networks and genres for a given radio show.
        '''
        if (not self.is_show_id(id)):
            raise TuneIn.TuneInError(-1, 'Id is not of the correct type.')
        params = [{'param': 'id', 'value': id}]
        result = self.__call_tunein('Browse.ashx', params)
        if (self.__result_ok(result)):
            raise TuneIn.TuneInError(self.__result_status(
                result), self.__result_fault(result), self.__result_fault_code(result))
        else:
            return result['body']

    def config_time(self):
        '''Retrieves the current server time and details of the client detected timezone.
        '''
        params = [{'param': 'c', 'value': 'time'}]
        result = self.__call_tunein('Config.ashx', params)
        if (self.__result_ok(result)):
            raise TuneIn.TuneInError(self.__result_status(
                result), self.__result_fault(result), self.__result_fault_code(result))
        else:
            return result['body']

    def config_localizedstrings(self):
        '''Retrieve text resources in a particular locale.
        '''
        params = [{'param': 'c', 'value': 'contentQuery'}]
        result = self.__call_tunein('Config.ashx', params)
        if (self.__result_ok(result)):
            raise TuneIn.TuneInError(self.__result_status(
                result), self.__result_fault(result), self.__result_fault_code(result))
        else:
            return result['body']

    def config_streamsample(self):
        '''Retrieves a list of streams using the various protocols, playlists and codecs for player development and testing.
        '''
        params = [{'param': 'c', 'value': 'streamSampleQuery'}]
        result = self.__call_tunein('Config.ashx', params)
        if (self.__result_ok(result)):
            raise TuneIn.TuneInError(self.__result_status(
                result), self.__result_fault(result), self.__result_fault_code(result))
        else:
            return result['body']

    def describe_nowplaying(self, id):
        '''Describe the content currently broadcast on a station or stream.
        '''
        if (not self.is_station_id(id) and not self.is_show_id(id)):
            raise TuneIn.TuneInError(-1, 'Id is not of the correct type.')
        params = [{'param': 'c', 'value': 'nowplaying'}, {'param':
                                                          'id', 'value': id}]
        result = self.__call_tunein('Describe.ashx', params)
        if (self.__result_ok(result)):
            raise TuneIn.TuneInError(self.__result_status(
                result), self.__result_fault(result), self.__result_fault_code(result))
        else:
            return result['body']

    def describe_station(self, id, detail=None):
        '''Describe a station.
        '''
        if (not self.is_station_id(id)):
            raise TuneIn.TuneInError(-1, 'Id is not of the correct type.')
        params = [{'param': 'id', 'value': id}, {'param': 'detail',
                                                 'value': detail}]
        result = self.__call_tunein('Describe.ashx', params)
        if (self.__result_ok(result)):
            raise TuneIn.TuneInError(self.__result_status(
                result), self.__result_fault(result), self.__result_fault_code(result))
        else:
            return result['body']

    def describe_show(self, id, detail=None):
        '''Describe a show.
        '''
        if (not self.is_show_id(id)):
            raise TuneIn.TuneInError(-1, 'Id is not of the correct type.')
        params = [{'param': 'id', 'value': id}, {'param': 'detail',
                                                 'value': detail}]
        result = self.__call_tunein('Describe.ashx', params)
        if (self.__result_ok(result)):
            raise TuneIn.TuneInError(self.__result_status(
                result), self.__result_fault(result), self.__result_fault_code(result))
        else:
            return result['body']

    def describe_topic(self, id):
        '''Retrieves metadata for a singe radio show topic.
        '''
        if (not self.is_topic_id(id)):
            raise TuneIn.TuneInError(-1, 'Id is not of the correct type.')
        params = [{'param': 'id', 'value': id}]
        result = self.__call_tunein('Describe.ashx', params)
        if (self.__result_ok(result)):
            raise TuneIn.TuneInError(self.__result_status(
                result), self.__result_fault(result), self.__result_fault_code(result))
        else:
            return result['body']

    def describe_custom_url(self, id):
        '''Retrieves metadata for a singe custom url topic.
        '''
        if (not self.is_custom_url_id(id)):
            raise TuneIn.TuneInError(-1, 'Id is not of the correct type.')
        params = [{'param': 'id', 'value': id}]
        result = self.__call_tunein('Describe.ashx', params)
        if (self.__result_ok(result)):
            raise TuneIn.TuneInError(self.__result_status(
                result), self.__result_fault(result), self.__result_fault_code(result))
        else:
            return result['body']

    def describe_countries(self):
        '''Retrieves a list of all countries known to the TuneIn directory.
        '''
        params = [{'param': 'c', 'value': 'countries'}]
        result = self.__call_tunein('Describe.ashx', params)
        if (self.__result_ok(result)):
            raise TuneIn.TuneInError(self.__result_status(
                result), self.__result_fault(result), self.__result_fault_code(result))
        else:
            return result['body']

    def describe_languages(self):
        '''Retrieves a list of all languages broadcast by stations in the TuneIn directory.
        '''
        params = [{'param': 'c', 'value': 'languages'}]
        result = self.__call_tunein('Describe.ashx', params)
        if (self.__result_ok(result)):
            raise TuneIn.TuneInError(self.__result_status(
                result), self.__result_fault(result), self.__result_fault_code(result))
        else:
            return result['body']

    def describe_locales(self):
        '''Retrieves a list of all locales supported by API.
        '''
        params = [{'param': 'c', 'value': 'locales'}]
        result = self.__call_tunein('Describe.ashx', params)
        if (self.__result_ok(result)):
            raise TuneIn.TuneInError(self.__result_status(
                result), self.__result_fault(result), self.__result_fault_code(result))
        else:
            return result['body']

    def describe_formats(self):
        '''Retrieves a list of the media formats recognized by the API.
        '''
        params = [{'param': 'c', 'value': 'formats'}]
        result = self.__call_tunein('Describe.ashx', params)
        if (self.__result_ok(result)):
            raise TuneIn.TuneInError(self.__result_status(
                result), self.__result_fault(result), self.__result_fault_code(result))
        else:
            return result['body']

    def describe_genres(self):
        '''Retrieves a list of all genres tagged in the TuneIn directory.
        '''
        params = [{'param': 'c', 'value': 'genres'}]
        result = self.__call_tunein('Describe.ashx', params)
        if (self.__result_ok(result)):
            raise TuneIn.TuneInError(self.__result_status(
                result), self.__result_fault(result), self.__result_fault_code(result))
        else:
            return result['body']

    def options(self, id):
        '''
        '''
        params = [{'param': 'id', 'value': 'id'}]
        result = self.__call_tunein('Options.ashx', params)
        if (self.__result_ok(result)):
            raise TuneIn.TuneInError(self.__result_status(
                result), self.__result_fault(result), self.__result_fault_code(result))
        else:
            return result['body']

    def preset_add(self, username=None, password=None, folderid=None, id=None, url=None, presetnumber=None, name=None):
        '''Adds a preset to a named or anonymous TuneIn account.
        '''
        params = [{'param': 'c', 'value': 'add'}, {'param': 'username', 'value': username}, {'param': 'password', 'value': password}, {'param': 'folderId', 'value': folderid}, {
            'param': 'id', 'value': id}, {'param': 'url', 'value': url}, {'param': 'presetNumber', 'value': presetnumber}, {'param': 'name', 'value': name}]
        result = self.__call_tunein('Preset.ashx', params)
        if (self.__result_ok(result)):
            raise TuneIn.TuneInError(self.__result_status(
                result), self.__result_fault(result), self.__result_fault_code(result))
        else:
            return result['body']

    def preset_remove(self, username=None, password=None, folderid=None, id=None, url=None, presetnumber=None):
        '''Removes a preset from a named or anonymous TuneIn account.
        '''
        params = [{'param': 'c', 'value': 'remove'}, {'param': 'username', 'value': username}, {'param': 'password', 'value': password}, {
            'param': 'folderId', 'value': folderid}, {'param': 'id', 'value': id}, {'param': 'url', 'value': url}, {'param': 'presetNumber', 'value': presetnumber}]
        result = self.__call_tunein('Preset.ashx', params)
        if (self.__result_ok(result)):
            raise TuneIn.TuneInError(self.__result_status(
                result), self.__result_fault(result), self.__result_fault_code(result))
        else:
            return result['body']

    def preset_addfolder(self, username=None, password=None, name=None):
        '''Adds a folder to a named or anonymous TuneIn account.
        '''
        params = [{'param': 'c', 'value': 'addFolder'}, {'param': 'username', 'value': username}, {
            'param': 'password', 'value': password}, {'param': 'name', 'value': name}]
        result = self.__call_tunein('Preset.ashx', params)
        if (self.__result_ok(result)):
            raise TuneIn.TuneInError(self.__result_status(
                result), self.__result_fault(result), self.__result_fault_code(result))
        else:
            return result['body']

    def preset_removefolder(self, username=None, password=None, folderid=None, name=None):
        '''Removes a folder from a named or anonymous TuneIn account.
        '''
        params = [{'param': 'c', 'value': 'removeFolder'}, {'param': 'username', 'value': username}, {
            'param': 'password', 'value': password}, {'param': 'folderId', 'value': folderid}]
        result = self.__call_tunein('Preset.ashx', params)
        if (self.__result_ok(result)):
            raise TuneIn.TuneInError(self.__result_status(
                result), self.__result_fault(result), self.__result_fault_code(result))
        else:
            return result['body']

    def preset_renamefolder(self, username=None, password=None, folderid=None, name=None):
        '''Renames a folder for a named or anonymous TuneIn account.
        '''
        params = [{'param': 'c', 'value': 'renameFolder'}, {'param': 'username', 'value': username}, {
            'param': 'password', 'value': password}, {'param': 'folderId', 'value': folderid}, {'param': 'name', 'value': name}]
        result = self.__call_tunein('Preset.ashx', params)
        if (self.__result_ok(result)):
            raise TuneIn.TuneInError(self.__result_status(
                result), self.__result_fault(result), self.__result_fault_code(result))
        else:
            return result['body']

    def preset_listfolders(self, username=None, password=None):
        '''Renames a folder for a named or anonymous TuneIn account.
        '''
        params = [{'param': 'c', 'value': 'listFolders'}, {'param': 'username',
                                                           'value': username}, {'param': 'password', 'value': password}]
        result = self.__call_tunein('Preset.ashx', params)
        if (self.__result_ok(result)):
            raise TuneIn.TuneInError(self.__result_status(
                result), self.__result_fault(result), self.__result_fault_code(result))
        else:
            return result['body']

    def recommend(self, artists, ratings=None):
        '''
        '''
        return []

    def report_wizard(self, id, email=None):
        '''
        '''
        return []

    def report_feedback(self, id, text, email=None):
        '''
        '''
        return []

    def report_stream(self, id, streamurl, error, message):
        '''
        '''
        return []

    def search(self, query, filter=None, types=None, call=None, name=None, freq=None):
        '''Free-text searching for stations, shows, topics, songs, artists and stream urls.
        '''
        params = [{'param': 'query', 'value': query}, {'param': 'filter', 'value': filter}, {'param': 'types', 'value': types}, {
            'param': 'call', 'value': call}, {'param': 'name', 'value': name}, {'param': 'freq', 'value': freq}]
        result = self.__call_tunein('Search.ashx', params)
        if (self.__result_ok(result)):
            raise TuneIn.TuneInError(self.__result_status(
                result), self.__result_fault(result), self.__result_fault_code(result))
        else:
            return result['body']

    def search_artist(self, query):
        '''Search for station broadcasting a specific artist.
        '''
        params = [{'param': 'c', 'value': 'artist'}, {'param':
                                                      'query', 'value': query}]
        result = self.__call_tunein('Search.ashx', params)
        if (self.__result_ok(result)):
            raise TuneIn.TuneInError(self.__result_status(
                result), self.__result_fault(result), self.__result_fault_code(result))
        else:
            return result['body']

    def search_song(self, query):
        '''Search for station broadcasting a specific song.
        '''
        params = [{'param': 'c', 'value': 'song'}, {'param':
                                                    'query', 'value': query}]
        result = self.__call_tunein('Search.ashx', params)
        if (self.__result_ok(result)):
            raise TuneIn.TuneInError(self.__result_status(
                result), self.__result_fault(result), self.__result_fault_code(result))
        else:
            return result['body']

    def search_song_artist(self, query):
        '''Search for station broadcasting a specific song and artist.
        '''
        params = [{'param': 'c', 'value': 'song,artist'}, {'param':
                                                           'query', 'value': query}]
        result = self.__call_tunein('Search.ashx', params)
        if (self.__result_ok(result)):
            raise TuneIn.TuneInError(self.__result_status(
                result), self.__result_fault(result), self.__result_fault_code(result))
        else:
            return result['body']

    def search_stream(self, query):
        '''Search for a station broadcasting on a specific stream.
        '''
        params = [{'param': 'c', 'value': 'stream'}, {'param':
                                                      'query', 'value': query}]
        result = self.__call_tunein('Search.ashx', params)
        if (self.__result_ok(result)):
            raise TuneIn.TuneInError(self.__result_status(
                result), self.__result_fault(result), self.__result_fault_code(result))
        else:
            return result['body']

    def tune(self, id):
        '''Returns a list of streams associated with the station.
        '''
        self.log_debug('tune')
        self.log_debug('id: %s' % id)
        if (not self.is_station_id(id) and not self.is_topic_id(id)):
            raise TuneIn.TuneInError(-1, 'Id is not of the correct type.')
        params = [{'param': 'id', 'value': id}]
        req = urllib2.Request(
            self.__add_params_to_url('Tune.ashx', params, addrender=False))
        f = urllib2.urlopen(req)

        self.log_debug('First pass of streams.')

        streams = []
        for stream in f:
            stream = stream.rsplit()[0]
            self.log_debug('stream: %s' % stream)
            (filepath, filename) = os.path.split(stream)
            (shortname, extension) = os.path.splitext(filename)
            filepath = filepath.lower()
            filename = filename.lower()
            shortname = shortname.lower()
            extension = extension.lower()
            self.log_debug('filepath: %s' % filepath)
            self.log_debug('filename: %s' % filename)
            self.log_debug('shortname: %s' % shortname)
            self.log_debug('extension: %s' % extension)
            if (extension == '.pls'):
                self.log_debug('PLS Playlist')
                for stream in self.__parse_pls(stream):
                    streams.append(stream)
            elif (extension == '.asx'):
                self.log_debug('ASX Playlist')
                for stream in self.__parse_asx(stream):
                    streams.append(stream)
            elif (extension == '.m3u'):
                self.log_debug('M3U Playlist')
                for stream in self.__parse_m3u(stream):
                    streams.append(stream)
            elif (re.search('streamtheworld.com', filepath)):
                ''' StreamTheWorld Support
                '''
                self.log_debug('StreamTheWorld stream')
                pattern = re.compile('(.*)callsign\=(.*)$')
                result = pattern.match(filename)
                if (result):
                    stw = streamtheworld.StreamTheWorld(result.group(2))
                    stw_url = stw.get_stream_url(result.group(2))
                    streams.append(stw_url)
            elif (stream.find('player.amri.ca') != -1):
                ''' Astral Radio Support
                '''
                self.log_debug('Astral Radio stream')
                astral = astralradio.AstralRadio(stream)
                for stream in astral.get_streams():
                    streams.append(stream)
            else:
                self.log_debug('Unknown stream')
                try:
                    request = urllib2.Request(stream)
                    opener = urllib2.build_opener()
                    f = opener.open(request)
                    if f.url != stream:
                        stream = f.url
                        streams.append(stream)
                    elif f.info().gettype() == 'video/x-ms-asf':
                        try:
                            for stream in self.__parse_asf(stream):
                                streams.append(stream)
                        except:
                            try:
                                for stream in self.__parse_asx(stream):
                                    streams.append(stream)
                            except:
                                pass
                    else:
                        streams.append(stream)
                except urllib2.URLError as e:
                    self.log_debug('Ignoring URLError: %s' % e)
                    streams.append(stream)

        self.log_debug('Second pass of streams.')

        tmpstreams = streams
        streams = []
        for stream in tmpstreams:
            stream = stream.rsplit()[0]
            self.log_debug('stream: %s' % stream)
            (filepath, filename) = os.path.split(stream)
            (shortname, extension) = os.path.splitext(filename)
            filepath = filepath.lower()
            filename = filename.lower()
            shortname = shortname.lower()
            extension = extension.lower()
            self.log_debug('filepath: %s' % filepath)
            self.log_debug('filename: %s' % filename)
            self.log_debug('shortname: %s' % shortname)
            self.log_debug('extension: %s' % extension)
            if (extension == '.pls'):
                self.log_debug('PLS Playlist')
                for stream in self.__parse_pls(stream):
                    streams.append(stream)
            elif (extension == '.asx'):
                self.log_debug('ASX Playlist')
                for stream in self.__parse_asx(stream):
                    streams.append(stream)
            elif (extension == '.m3u'):
                self.log_debug('M3U Playlist')
                for stream in self.__parse_m3u(stream):
                    streams.append(stream)
            else:
                self.log_debug('Unknown stream')
                streams.append(stream)

        return streams

    def tune_ebrowse(self, id):
        '''Returns individual links for streams associated with the station.
        '''
        if (not self.is_station_id(id)):
            raise TuneIn.TuneInError(-1, 'Id is not of the correct type.')
        params = [{'param': 'id', 'value': id}, {'param': 'c',
                                                 'value': 'ebrowse'}]
        return []

    def tune_show(self, id, flatten=None, category='pbrowse', filter=''):
        '''Provides links to all available downloads for station.
        '''
        if (not self.is_show_id(id)):
            raise TuneIn.TuneInError(-1, 'Id is not of the correct type.')
        params = [{'param': 'id', 'value': id}, {'param': 'c', 'value': category}, {
            'param': 'flatten', 'value': flatten}, {'param': 'filter', 'value': filter}]
        result = self.__call_tunein('Tune.ashx', params)
        if (self.__result_ok(result)):
            raise TuneIn.TuneInError(self.__result_status(
                result), self.__result_fault(result), self.__result_fault_code(result))
        return result['body']
