#!/usr/bin/env python
# -*- coding: utf-8 -*-

from HTMLParser import HTMLParser
import json
import urllib


class ShowDirectoryParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.process_links = False
        self.process_data = False
        self.links_cache = []

    def handle_starttag(self, tag, attrs):
        if tag == 'section':
            for name, value in attrs:
                if name == 'class' and value == 'archive':
                    self.process_links = True

        if tag == 'a' and self.process_links:
            for name, value in attrs:
                if name == 'href' and '/shows/' in value \
                        and '/' not in value.split('/shows/')[1]\
                        and 'abrakadabra' not in value.split('/shows/')[1]:
                    self.links_cache.append({'href': value})
                    self.process_data = True
                else:
                    self.process_data = False

    def handle_data(self, data):
        if self.process_links and self.process_data and self.lasttag == 'a':
            self.links_cache[-1]['name'] = data

    def handle_endtag(self, tag):
        if self.process_links:
            if tag == 'section':
                self.process_links = False

    def get_shows_directory(self):
        return self.links_cache


class ShowItemsParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.json_link = None

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            for name, value in attrs:
                if 'data-playlist-url' in name:
                    self.json_link = 'https://www.1tv.ru' + value

    def get_show_items(self):
        json_data = urllib.urlopen(self.json_link).read()
        return json.loads(json_data)
