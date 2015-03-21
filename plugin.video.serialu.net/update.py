
import xbmc,xbmcgui, xbmcaddon
import urllib2, urllib, re, cookielib, sys, time, os
from urlparse import urlparse

try:
    from hashlib import md5 as md5
except:
    import md5

from datetime import date

Addon = xbmcaddon.Addon(id='plugin.video.serialu.net')

import HTMLParser
hpar = HTMLParser.HTMLParser()

import traceback
def formatExceptionInfo(maxTBlevel=5):
     cla, exc, trbk = sys.exc_info()
     excName = cla.__name__
     try:
         excArgs = exc.__dict__["args"]
     except KeyError:
         excArgs = "<no args>"
     excTb = traceback.format_tb(trbk, maxTBlevel)
     return excName+' '+excArgs+' '+excTb

# load XML library
try:
    sys.path.append(os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib'))
    from ElementTree  import Element, SubElement, ElementTree
except:
    sys.path.insert(0, os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib'))
    from ElementTree  import Element, SubElement, ElementTree

from BeautifulSoup  import BeautifulSoup

today = date.today()
path = os.path.join(Addon.getAddonInfo('path'), r'resources', r'data')

#xbmc.log('Path: '+path)

cj      = cookielib.LWPCookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllib2.install_opener(opener)

#-------------------------------------------------------------------------------
def get_HTML(url, post = None, ref = None):
    html = ''

    if ref == None:
        ref = 'http://'+urlparse(url).hostname

    request = urllib2.Request(urllib.unquote(url), post)

    request.add_header('User-Agent', 'Mozilla/4.0; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Host', urlparse(url).hostname)
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Language', 'ru-RU')
    request.add_header('Referer', ref)
    request.add_header('Cookie', 'MG_6532=1')

    ret = 502
    idx = 5

    while ret == 502 and idx > 0:
        try:
            f = urllib2.urlopen(request)
            ret = 0
        except IOError, e:
            if hasattr(e, 'reason'):
                xbmc.log('We failed to reach a server. Reason: '+ str(e.reason))
            elif hasattr(e, 'code'):
                xbmc.log('The server couldn\'t fulfill the request. Error code: '+ str(e.code))
                ret = e.code

        if ret == 502:
            time.sleep(1)
        idx = idx -1

    if ret == 0:
        html = f.read()
        f.close()

    return html

#---------- get serials info and save to XML --------------------------------------------------
def Update_Serial_XML(mode):
    #show Dialog
    dp = xbmcgui.DialogProgress()

    isUpdate = 0

    if mode == 'UPDATE':
        #load current serial list
        try:
            tree = ElementTree()
            tree.parse(os.path.join(path, r'serials.xml'))
            xml1 = tree.getroot()
            xml1.find("LAST_UPDATE").text = today.isoformat()
            xml_serials  = xml1.find('SERIALS')
            xml_types    = xml1.find('TYPES')
            xml_genres   = xml1.find('GENRES')
            dp.create("Update SERIALU.NET Info")
            isUpdate = 1
        except:
            # create XML structure
            xml1 = Element("SERIALU_NET")
            SubElement(xml1, "LAST_UPDATE").text = today.isoformat()
            xml_serials  = SubElement(xml1, "SERIALS")
            xml_types    = SubElement(xml1, "TYPES")
            xml_genres   = SubElement(xml1, "GENRES")
            dp.create("Reload SERIALU.NET Info")
    else:
        # create XML structure
        xml1 = Element("SERIALU_NET")
        SubElement(xml1, "LAST_UPDATE").text = today.isoformat()
        xml_serials  = SubElement(xml1, "SERIALS")
        xml_types    = SubElement(xml1, "TYPES")
        xml_genres   = SubElement(xml1, "GENRES")
        dp.create("Reload SERIALU.NET Info")

    # grab serial's info from site
    url='http://serialu.net/'
    #start_time = datetime.now()
    serial_found = 0

    # get max page number for update
    print Addon.getSetting('update_len')
    try:
        max_page = (10,20,50,100,1000)[int(Addon.getSetting('update_len'))]
    except:
        max_page = 10

    # get number of webpages to grab information
    page_num = Get_Page_Number(url)

    if isUpdate == 1:
        page_num = min(page_num, max_page)

    # get all serials
    for count in range(1, page_num+1):
            xbmc.log(' ***  page '+str(count))
            serial_found = Get_Film_Info(url+'/page/'+str(count)+'/', xml_serials, xml_types, xml_genres, serial_found, dp)
            percent = min(count*100/page_num, 100)
            dp.update(percent, '', 'Loaded: '+ str(count)+' of '+str(page_num)+' pages','Кол-во сериалов: '+str(serial_found))

    # order sort serials/categories/genres by names
    xml_serials[:] = sorted(xml_serials, key=getkey)
    xml_types[:]   = sorted(xml_types, key=getkey)
    xml_genres[:]  = sorted(xml_genres, key=getkey)

    dp.close()
    ElementTree(xml1).write(os.path.join(path, r'serials.xml'), encoding='utf-8')


#--- get number of pages for selected category ---------------------------------
def Get_Page_Number(url):
    link = get_HTML(url)
    ret = 1

    match=re.compile('<div class="wp-pagenavi">(.+?)</div>', re.MULTILINE|re.DOTALL).findall(link)
    page=re.compile('<a href="(.+?)/page/(.+?)</a>', re.MULTILINE|re.DOTALL).findall(match[0])

    for rec in page:
        v = re.compile('(.+?)/" title="(.+?)"', re.MULTILINE|re.DOTALL).findall(rec[1])
        if len(v) > 0:
            if ret < int(v[0][0]):
                ret = int(v[0][0])

    return ret

#--- get serial info for selected page in category ------------------------------
def Get_Film_Info(url, xml_serials, xml_types, xml_genres, serial_found, dp):
    html = get_HTML(url)
    if html=='':
        return False

    html_container = re.compile('<div class="container">(.+?)<div class="navigation">', re.MULTILINE|re.DOTALL).findall(html)

    # -- parsing web page ----------------------------------------------------------

    soup = BeautifulSoup(''.join(html_container[0].replace('<p>', '  ').replace('</p>', '')))

    serials = soup.findAll("div", { "class" : "entry" })
    for ser in serials:
        #try:
        # check if process was cancelled
        if (dp.iscanceled()): return
        # --
        i_name  = unescape(ser.find("h2").find("a").text.strip())
        i_url   = ser.find("h2").find("a")["href"]
        xbmc.log(' ***    '+i_name.encode('utf-8'))
        #-- detail info
        info = ser.find("div", { "class" : "content" })
        try:
            i_image = info.find("img")["src"]
        except:
            ser_name = ser.find("h2").find("a").text.strip() #i_name.replace(u'”', u'"').replace(u'“',u'"').replace(u'«',u'"').replace(u'»',u'"')
            search_mask = '<p><img class="m_pic" alt="'+ser_name+'" align="left" src="(.+?)" /></p>'
            img_alt = re.compile(search_mask, re.MULTILINE|re.DOTALL).findall(html)
            try:
                i_image = img_alt[0]
            except:
                search_mask = '<p><img class="m_pic" alt="'+ser_name+'"" align="left" src="(.+?)" /></p>'
                img_alt = re.compile(search_mask, re.MULTILINE|re.DOTALL).findall(html)
                try:
                    i_image = img_alt[0]
                except:
                    i_image = '-'
                    xbmc.log(i_name.encode('utf-8') + ' - image not found')


        o_name      = '-'
        i_year      = '-'
        i_country   = '-'
        i_genre     = '-'
        i_director  = '-'
        i_actors    = '-'
        i_text      = '-'

        for inf in info.findAll("strong"):
            if inf.text.encode('utf-8') == 'Оригинальное название:':
                o_name = unescape(str(inf.nextSibling).strip())
            elif inf.text.encode('utf-8') == 'Год выхода на экран:':
                i_year = unescape(str(inf.nextSibling).strip())
            elif inf.text.encode('utf-8') == 'Страна:':
                i_country = unescape(str(inf.nextSibling).strip())
            elif inf.text.encode('utf-8') == 'Сериал относится к жанру:':
                i_genre = unescape(str(inf.nextSibling).strip())
            elif inf.text.encode('utf-8') == 'Постановщик':
                i_director = unescape(str(inf.nextSibling).strip())
            elif inf.text.encode('utf-8') == 'Актеры, принявшие участие в съемках:':
                i_actors = unescape(str(inf.nextSibling).strip())
            elif inf.text.encode('utf-8') == 'Краткое описание:':
                i_text = unescape(str(inf.nextSibling))

        full_text = i_text
        if o_name != '':
            full_text = full_text+(u'\nОригинальное название: ')+o_name
        if i_actors != '':
            full_text = full_text+(u'\nАктеры: ')+i_actors

        # add info to XML
        xml_serial_hash = 'ser_'+f_md5((i_name + i_year).encode('utf-8')).hexdigest()
        #check if serial info exists
        xml_serial = xml_serials.find(xml_serial_hash)
        if xml_serial is None:   #-- create new record
            # create serial record in XML
            xml_serial = SubElement(xml_serials, xml_serial_hash)
            xml_serial.text = i_name
            SubElement(xml_serial, "name").text     = i_name
            SubElement(xml_serial, "url").text      = i_url
            SubElement(xml_serial, "year").text     = i_year
            SubElement(xml_serial, "genre").text    = i_genre
            SubElement(xml_serial, "director").text = i_director
            SubElement(xml_serial, "text").text     = full_text
            SubElement(xml_serial, "img").text      = i_image
            SubElement(xml_serial, "categories")
            SubElement(xml_serial, "genres")

        isCategory_found = 'n'
        # add serial category info
        categories = xml_serial.find("categories")
        for cat in ser.find("div", { "class" : "cat" }).findAll("a"):
            if cat.text.encode('utf-8') <> 'Сериалы':
                cur_type_hash = 'sc_'+f_md5(cat.text.strip().lower().encode('utf-8')).hexdigest()
                # check if category exists
                if xml_types.find(cur_type_hash) is None:
                    type = SubElement(xml_types, cur_type_hash)
                    SubElement(type, "name").text = unescape(cat.text.strip()).capitalize()
                if categories.find(cur_type_hash) is None:
                    SubElement(categories, cur_type_hash)
                isCategory_found = 'y'

        isMultserial = 'n'
        # add serial genre info
        genres = xml_serial.find("genres")
        for gen in i_genre.split(','):
            cur_genre_hash = 'sg_'+f_md5(gen.strip().lower().encode('utf-8')).hexdigest()
            # check if category exists
            if xml_genres.find(cur_genre_hash) is None:
                genre = SubElement(xml_genres, cur_genre_hash)
                SubElement(genre, "name").text = unescape(gen.strip()).capitalize()
            if genres.find(cur_genre_hash) is None:
                SubElement(genres, cur_genre_hash)
            # check if it's multserial
            if gen.encode('utf-8') == 'Мультсериал' and isCategory_found == 'n':
                isMultserial = 'y'

        # add multserial or foreighn serial types
        if isCategory_found == 'n':
            if isMultserial == 'y':
                # add serial category info
                categories = xml_serial.find("categories")
                cur_type_hash = 'sc_'+f_md5((u'Мультсериалы').lower().encode('utf-8')).hexdigest()
                # check if category exists
                if xml_types.find(cur_type_hash) is None:
                    type = SubElement(xml_types, cur_type_hash)
                    SubElement(type, "name").text = u'Мультсериалы'
                if categories.find(cur_type_hash) is None:
                    SubElement(categories, cur_type_hash)
            else:
                if i_country.encode('utf-8') == 'Россия':
                    # add serial category info
                    categories = xml_serial.find("categories")
                    cur_type_hash = 'sc_'+f_md5((u'Русские сериалы').lower().encode('utf-8')).hexdigest()
                    # check if category exists
                    if xml_types.find(cur_type_hash) is None:
                        type = SubElement(xml_types, cur_type_hash)
                        SubElement(type, "name").text = u'Русские сериалы'
                    if categories.find(cur_type_hash) is None:
                        SubElement(categories, cur_type_hash)
                else:
                    # add serial category info
                    categories = xml_serial.find("categories")
                    cur_type_hash = 'sc_'+f_md5((u'Зарубежные сериалы').lower().encode('utf-8')).hexdigest()
                    # check if category exists
                    if xml_types.find(cur_type_hash) is None:
                        type = SubElement(xml_types, cur_type_hash)
                        SubElement(type, "name").text = u'Зарубежные сериалы'
                    if categories.find(cur_type_hash) is None:
                        SubElement(categories, cur_type_hash)

        # update info in progress dialog
        serial_found = serial_found + 1
        #except:
            #xbmc.log(formatExceptionInfo())

    return serial_found
#-------------------------------------------------------------------------------

def unescape(text):
    try:
        text = hpar.unescape(text)
    except:
        text = hpar.unescape(text.decode('utf8'))

    try:
        text = unicode(text, 'utf-8')
    except:
        text = text

    return text

def getkey(elem):
    return elem.findtext("name")

def f_md5(str):
    try:
        rez = md5(str)
    except:
        rez = md5.md5(str)

    return rez


#-------------------------------------------------------------------------------

if len(sys.argv) > 1:
    mode = sys.argv[1]
else:
    mode = 'UPDATE'

ret = 'NO'

if mode != 'UPDATE' and mode != 'INFO':
    dialog = xbmcgui.Dialog()
    if dialog.yesno('Внимание!', 'Пересоздание списка сериалов требует','значительного времени (15-20 минут).', 'Пересоздать список?'):
        ret = 'YES'
    else:
        ret = 'NO'

if mode == 'UPDATE' or ret == 'YES':
    Update_Serial_XML(mode)
else:
    if mode == 'INFO':
        dialog = xbmcgui.Dialog()
        tree = ElementTree()
        tree.parse(os.path.join(path, r'serials.xml'))

        update_date = 'Список сериалов создан: ' + tree.getroot().find('LAST_UPDATE').text
        serial_count= 'Количество сериалов   : ' + str(len(tree.getroot().find('SERIALS')))

        dialog.ok('Информация', '', update_date, serial_count)

