"""
Python implementation of ga.php. 

Snatched from (based on, yep!) https://github.com/b1tr0t/Google-Analytics-for-Mobile--python-
Thank you very much, man!

Let me know if you will be in Prague, b1tr0t, I will set a beer, 
	Eugene 
"""
import re
try:
	from hashlib import md5
except:
	from md5 import md5
from random import randint
#import struct

import time
from urllib import unquote, quote


VERSION = "4.4sh"
COOKIE_NAME = "__utmmobile"
COOKIE_PATH = "/"
COOKIE_USER_PERSISTENCE = 63072000
DOMAIN = "stepashka.com"
UATRACK = "UA-31027962-1"

def get_ip(remote_address):
	# dbgMsg("remote_address: " + str(remote_address))
	if not remote_address:
		return ""
	matches = re.match('^([^.]+\.[^.]+\.[^.]+\.).*', remote_address)
	if matches:
		return matches.groups()[0] + "0"
	else:
		return ""

def get_visitor_id(guid, cookie):
	"""
	 // Generate a visitor id for this hit.
	 // If there is a visitor id in the cookie, use that, otherwise
	 // use the guid if we have one, otherwise use a random number.
	"""
	if cookie:
		return cookie
	message = ""
	# Create the visitor id using the guid.
	message = guid + UATRACK
	
	md5String = md5(message).hexdigest()
	return "0x" + md5String[:16]

def get_random_number():
	"""
	// Get a random number string.
	"""
	return str(randint(0, 0x7fffffff))

def send_request_to_google_analytics(utm_url, ua):
	"""
  // Make a tracking request to Google Analytics from this server.
  // Copies the headers from the original request to the new one.
  // If request containg utmdebug parameter, exceptions encountered
  // communicating with Google Analytics are thown.	
	"""
	import urllib2
	try:
		req = urllib2.Request(utm_url, None,
									{'User-Agent':ua}
									 )
		response = urllib2.urlopen(req).read()
	except:
		print ("GA fail: %s" % utm_url)			
	return response
	   
def track_page_view_a(visitor_id, path, ua, extra, tevent):
	#print path
	#print tevent
	"""
	// Track a page view, updates all the cookies and campaign tracker,
	// makes a server side request to Google Analytics and writes the transparent
	// gif byte data to the response.
	"""	
	domain = DOMAIN
	
	document_path = unquote(path)
	
	utm_gif_location = "http://www.google-analytics.com/__utm.gif"
	
	import urllib
	ip = urllib.urlopen('http://automation.whatismyip.com/n09230945.asp').read()
	
	# // Construct the gif hit url.
	utm_url = utm_gif_location + "?" + \
			"utmwv=" + VERSION + \
			"&utmn=" + get_random_number() + \
			"&utmhn=" + quote(domain) + \
			"&utmsr=" + quote(extra.get("screen", "")) + \
			"&utme="+ tevent + \
			"&utmr=" + quote('-') + \
			"&utmp=" + quote(document_path) + \
			"&utmac=" + UATRACK + \
			"&utmcc=__utma%3D999.999.999.999.999.1%3B" + \
			"&utmvid=" + visitor_id + \
			"&utmip=" + get_ip(ip)
	# dbgMsg("utm_url: " + utm_url)	
	print "Analitycs: %s" % utm_url
	return send_request_to_google_analytics(utm_url, ua)