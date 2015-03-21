import urllib2, urllib, re, cookielib, sys, time

# load XML library
sys.path.append(r'g:\XBMC\resources\lib')
from ElementTree  import Element, SubElement, ElementTree

tree = ElementTree()
tree.parse(r'g:\xbmc\resources\data\test.xml')

for i in tree.getroot():             # Iterates through all found links
    print i.text
    print i.tag

for k in tree.find('text').find('buttonbox2'):
    print k.text
#tree.write("output.xhtml")