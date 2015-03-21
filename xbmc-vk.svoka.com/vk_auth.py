#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import urllib

try:
    import json
except ImportError:
    import simplejson as json


def auth(email, password, client_id, secret, scope):
    url = urllib.urlopen("https://oauth.vk.com/token?" + urllib.urlencode({
            "grant_type": "password",
            "client_id": client_id,
            "client_secret": secret,
            "username": email,
            "password": password,
            "scope": scope
        }))
    out = json.load(url)
    if "access_token" not in out:
        print out
    return out["access_token"]