# -*- coding: utf-8 -*-

import urllib2
import antizapret

urllib2.install_opener(urllib2.build_opener(antizapret.AntizapretProxyHandler()))

req = urllib2.Request("http://blockedsite.ru")
response = urllib2.urlopen(req)
data = response.read()
