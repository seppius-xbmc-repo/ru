import urllib2, urllib, re, cookielib, sys, time

# load XML library
sys.path.append(r'g:\XBMC\resources\lib')
from ElementTree  import Element, SubElement, ElementTree

window = Element("window")

title = SubElement(window, "title", font="large")
title.text = ("Проверка АБВГД..").decode('utf-8')

text = SubElement(window, "text", wrap="word")

box = SubElement(text, "buttonbox1")
SubElement(box, "button").text = ("OK").decode('utf-8')
SubElement(box, "button").text = ("Проба записи").decode('utf-8')

box = SubElement(text, "buttonbox2")
SubElement(box, "button").text = ("Error").decode('utf-8')
SubElement(box, "button").text = ("Але! Гараж").decode('utf-8')

ElementTree(window).write(r'g:\xbmc\resources\data\test.xml', encoding='utf-8')



