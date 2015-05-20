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
import urllib2

if sys.version_info >= (2,7):
    import json as _json
else:
    import simplejson as _json


class AstralRadio:
    def __init__(self, url):
        self.__url__ = url
        return

    def get_streams(self):
        streams = []
        if not self.__url__:
            return streams
        
        try:
            # Workout callsign
            callsign = self.__url__.split('//')[1].split('.')

            if len(callsign) > 0:
                # Read json config for station
                f = urllib2.urlopen(('http://provstatic1.amri.ca/ps/player_%sfm.v2.json' % callsign[0]))
                config = _json.load(f)
                f.close()

                # Create rtmp stream url
                if 'streams' in config:
                    for stream in config['streams']:
                        if 'mount' in stream and len(stream['mount']) > 0 and 'stream' in stream and len(stream['stream']) > 0:
                            rtmpurl = 'rtmp://%s/%s' % (stream['mount'], stream['stream'])
                            swfurl = config['playerBaseUrl']
                            streams.append('%s swfurl=%s/ swfvfy=true pageurl=%s/ live=true' % (rtmpurl, swfurl, swfurl))
        except:
            pass

        return streams
