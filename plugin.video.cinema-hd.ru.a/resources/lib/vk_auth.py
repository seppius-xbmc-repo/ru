#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib, urllib2
import re

class vk_auth:
	def __init__(self, email, password):
		self.email = email
		self.password = password
	
	def get_remixsid_cookie(self):
		headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:15.0) Gecko/20100101 Firefox/15.0'}
		post_values = {'act': 'login', 'email': self.email, 'pass': self.password, 'role': 'al_frame'}
		post = urllib.urlencode(post_values)
		#print post
		req = urllib2.Request('https://login.vk.com/?act=login', post, headers)
		response = urllib2.urlopen(req)
		#print response.info()
		self.remixsid = re.findall(r"(remixsid[6]?=[a-z 0-9]*);", response.headers['Set-Cookie'])
		if self.remixsid: return self.remixsid[0]
		else: return False