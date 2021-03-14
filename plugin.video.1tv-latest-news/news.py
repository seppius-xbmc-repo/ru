#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import urllib
from HTMLParser import HTMLParser


class NewsItemsParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.json_link = None

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            for name, value in attrs:
                if name == 'data-playlist-url':
                    self.json_link = 'https://www.1tv.ru' + value

    def get_news_items(self):
        json_data = urllib.urlopen(self.json_link).read()
        return json.loads(json_data)
