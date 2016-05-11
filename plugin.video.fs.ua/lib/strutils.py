from BeautifulSoup import BeautifulStoneSoup
import sys
import urllib
import re


def html_entities_decode(string):
    return BeautifulStoneSoup(string, convertEntities=BeautifulStoneSoup.HTML_ENTITIES).contents[0]


def construct_request(params):
    return '%s?%s' % (sys.argv[0], urllib.urlencode(params))


def fix_string(string):
    if isinstance(string, unicode):
        return string.encode('utf8')
    return string


def fix_broken_json(data):
    data = re.sub(r'(\w+):', r'"\1":', data)
    data = data.replace(': \'', ': "')
    data = data.replace('\',', '",')

    return data
