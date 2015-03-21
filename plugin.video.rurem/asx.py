import httplib, urllib, urllib2, re
import xml.parsers.expat
import config1

class Parser:
    streams = []
    url = None
    
    def parseUrl(self, url):
        asx = urllib2.urlopen(url)
        data = asx.read()
        return self.parseString(data)
    
    def parseString(self, data):
        p = xml.parsers.expat.ParserCreate()
        p.StartElementHandler = self.start_element
        p.EndElementHandler = self.end_element

        p.Parse(str(data))
        return self.streams
        
    def start_element(self, name, attrs):
        if name == 'Ref' or name == 'REF':
            href = None
            if 'HREF' in attrs:
                href = attrs['HREF']
            if 'href' in attrs:
                href = attrs['href']
            if href != None and (href.startswith('mms://') or href.startswith('rtsp://')):
                self.url = href
    
    def end_element(self, name):
        if name == 'Ref' or name == 'REF':
            if self.url != None:
                self.streams.append(self.url)
            
