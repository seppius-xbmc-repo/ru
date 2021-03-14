#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import urllib
from HTMLParser import HTMLParser


class DocDirectoryParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.process_links = False
        self.links_cache = []

    def handle_starttag(self, tag, attrs):
        if tag == 'header':
            for name, value in attrs:
                if name == 'id' and value == 'page-title':
                    self.process_links = True

        if tag == 'a' and self.process_links:
            for name, value in attrs:
                if name == 'href' and '/doc/' in value:
                    self.links_cache.append({'href': value})

    def handle_data(self, data):
        if self.process_links and self.lasttag == 'span':
            self.links_cache[-1]['name'] = data

    def handle_endtag(self, tag):
        if self.process_links:
            if tag == 'header':
                self.process_links = False

    def get_doc_directory(self):
        del self.links_cache[-1]  # del all-video element
        return self.links_cache


class DocItemsParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.json_link = None

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for name, value in attrs:
                if 'collection_id' in value:
                    collection_id = value.split('collection_id=', 1)[1]
                    self.json_link = 'https://www.1tv.ru/video_materials.json?collection_id=' + \
                                     collection_id + '&sort=none'

    def get_doc_items(self):
        json_data = urllib.urlopen(self.json_link).read()
        return json.loads(json_data)
