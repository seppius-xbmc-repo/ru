#/*
# *
# * TuneIn Radio for XBMC.
# *
# * Copyright (C) 2013 Diego Fernando Nieto
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

from random import choice as choise
import os
import sys
import urllib2
import xml.dom.minidom as minidom


class StreamTheWorld:
    ## Example XML document we are parsing follows, as the minidom code is so beautiful to follow
    # http://playerservices.streamtheworld.com/api/livestream?version=1.4&mount=CARACOL_RADIOAAC&lang=EN
    #
    #<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    #<live_stream_config version="1.4">
    #   <mountpoints>
    #          <mountpoint>
    #                       <status>
    #                               <status-code>200</status-code>
    #                               <status-message>OK</status-message>
    #                       </status>
    #
    #                       <transports>
    #                               <transport>http</transport>
    #                       </transports>
    #
    #                       <servers>
    #                               <server sid="3653">
    #                                       <ip>3653.live.streamtheworld.com</ip>
    #                                       <ports>
    #                                               <port type="http">80</port>
    #                                               <port type="http">3690</port>
    #                                               <port type="http">443</port>
    #                                       </ports>
    #                               </server>
    #
    #                               <server sid="1351">
    #                                       <ip>1351.live.streamtheworld.com</ip>
    #                                       <ports>
    #                                               <port type="http">80</port>
    #                                               <port type="http">3690</port>
    #                                               <port type="http">443</port>
    #                                       </ports>
    #                               </server>
    #                       </servers>
    #
    #                       <mount>CARACOL_RADIOAAC</mount>
    #                       <format>FLV</format>
    #                       <bitrate>32000</bitrate>
    #                       <media-format container="flv" cuepoints="andoxml">
    #                       <audio index="0" samplerate="44100" codec="heaacv2" bitrate="32000" channels="2"/>
    #                       </media-format>
    #                       <authentication>0</authentication>
    #                       <timeout>0</timeout>
    #               </mountpoint>
    #   </mountpoints>
    #</live_stream_config>

    ''' Parse streamtheworld URL to HTTP Stream
    '''
    def __init__(self, cs):
        self.__cs__ = cs
        return

    def __validate_callsign(self, cs, acc=True):
        '''
                Normal callsign format is 'WWWWAAA', where 'WWWW' is the radio station
                callsign and 'AAA' is always 'AAC'.
        '''
        if not cs or not isinstance(cs, str):
            raise ValueError('callsign \'%s\' is not a string.' % cs)
        if len(cs) < 6:
            raise ValueError('callsign \'%s\' is too short.' % cs)
        if acc and not cs.endswith('AAC'):
            cs = cs + 'AAC'
        return cs

    def __make_request(self, callsign):
        ''' Make a Call to StreamTheWorld API v1.5
        '''
        host = 'playerservices.streamtheworld.com'
        req = urllib2.Request(
            'http://%s/api/livestream?version=1.5&mount=%s&lang=en' %
            (host, callsign))

        req.add_header('User-Agent', 'Mozilla/5.0')
        return req

    def __t(self, element):
        '''get the text of a DOM element'''
        return element.firstChild.data

    def __check_status(self, ele):
        ''' should only be one status element inside a mountpoint
        '''
        status = ele.getElementsByTagName('status')[0]
        if self.__t(status.getElementsByTagName('status-code')[0]) != '200':
            msg = self.__t(status.getElementsByTagName('status-message')[0])
            raise Exception('Error locating stream: ' + msg)

    def __create_stream_urls(self, srcfile):
        ''' Return an array with all URLs
        '''
        doc = minidom.parse(srcfile)
        mp = doc.getElementsByTagName('mountpoint')[0]
        self.__check_status(mp)
        mt = self.__t(mp.getElementsByTagName('mount')[0])
        allurls = []
        for s in mp.getElementsByTagName('server'):
            # a thing of beauty, right?
            ip = self.__t(s.getElementsByTagName('ip')[0])
            ports = [self.__t(p) for p in s.getElementsByTagName('port')]
            # yes, it is always HTTP. We see ports 80, 443, and 3690 usually
            urls = ['http://%s:%s/%s' % (ip, p, mt) for p in ports]
            allurls.extend(urls)

        return allurls

    def get_stream_url(self, cs):
        ''' Get one URL from CS
        '''
        try:
            callsign = self.__validate_callsign(cs)
            req = self.__make_request(callsign)
            result = urllib2.urlopen(req)
            urls = self.__create_stream_urls(result)
        except:
            callsign = self.__validate_callsign(cs, False)
            req = self.__make_request(callsign)
            result = urllib2.urlopen(req)
            urls = self.__create_stream_urls(result)

        if len(urls) > 0:
            u = choise(urls)
            if not u.endswith('_SC'):
                u = u + '_SC'
            return u
