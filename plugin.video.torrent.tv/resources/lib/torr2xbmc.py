#!/usr/bin/python
# -*- coding: utf-8 -*-

import httplib
import urllib
import urllib2
import re
import sys
import os
import socket
import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmc
import xbmcaddon
import datetime
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
from ASCore import TSengine,_TSPlayer
import base64
import time
from database import DataBase
from urllib import unquote, quote


hos = int(sys.argv[1])
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
__addon__ = xbmcaddon.Addon( id = 'plugin.video.torrent.tv' )
__language__ = __addon__.getLocalizedString
addon_icon     = __addon__.getAddonInfo('icon')
addon_fanart  = __addon__.getAddonInfo('fanart')
addon_path     = __addon__.getAddonInfo('path')
addon_type     = __addon__.getAddonInfo('type')
addon_id        = __addon__.getAddonInfo('id')
addon_author  = __addon__.getAddonInfo('author')
addon_name     = __addon__.getAddonInfo('name')
addon_version = __addon__.getAddonInfo('version')
prt_file=__addon__.getSetting('port_path')
adult = __addon__.getSetting('adult')
login = __addon__.getSetting("login")
passw = __addon__.getSetting("password")
autostart = __addon__.getSetting('autostart')
ch_color = __addon__.getSetting('ch_color')
prog_color = __addon__.getSetting("prog_color")
ch_b = __addon__.getSetting("ch_b")
prog_b = __addon__.getSetting('prog_b')
prog_str = __addon__.getSetting('prog_str')
ch_i = __addon__.getSetting("ch_i")
prog_i = __addon__.getSetting('prog_i')
archive = __addon__.getSetting('archive')
view = __addon__.getSetting('view')
aceport=62062
cookie = ""
PLUGIN_DATA_PATH = xbmc.translatePath( os.path.join( "special://profile/addon_data", 'plugin.video.torrent.tv') )
view_mode = ""
if view == str(0):view_mode = 50
elif view == str(1): view_mode = 51
elif view == str(2): view_mode = 500
elif view == str(3): view_mode = 501
elif view == str(4): view_mode = 508
elif view == str(5): view_mode = 504
elif view == str(6): view_mode = 503
elif view == str(7): view_mode = 515

if (sys.platform == 'win32') or (sys.platform == 'win64'):
    PLUGIN_DATA_PATH = PLUGIN_DATA_PATH.decode('utf-8')

if prog_str == "true": pr_str = " "
else: pr_str = chr(10)
    
PROGRAM_SOURCE_PATH = os.path.join( PLUGIN_DATA_PATH , "%s_inter-tv.zip"  % datetime.date.today().strftime("%W") )

settingsTV = xbmcaddon.Addon(id = 'script.module.YaTv')
_ADDON_PATH_TV_ =   xbmc.translatePath(settingsTV.getAddonInfo('path'))
if (sys.platform == 'win32'):
	_ADDON_PATH_TV_ = _ADDON_PATH_TV_.decode('utf-8')

sys.path.append( os.path.join( _ADDON_PATH_TV_, 'lib') )

    
db_name = os.path.join(PLUGIN_DATA_PATH, 'tvbase.db')
cookiefile = os.path.join(PLUGIN_DATA_PATH, 'cookie.txt')
xbmcplugin.setContent(int(sys.argv[1]), 'episodes')

data = urllib.urlencode({
    'email' : login,
    'password' : passw,
    'remember' : 1,
    'enter' : 'enter'
})

############################
if __addon__.getSetting('fanart') == 'false':xbmcplugin.setContent(int(sys.argv[1]), 'movies')
if __addon__.getSetting('fanart') == 'true':xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
############################

try:
    if prt_file:  
        gf = open(prt_file, 'r')
        aceport=int(gf.read())
        gf.close()
except: prt_file=None
if not prt_file:
    try:
        fpath= os.path.expanduser("~")
        pfile= os.path.join(fpath,'AppData\Roaming\TorrentStream\engine' ,'acestream.port')
        gf = open(pfile, 'r')
        aceport=int(gf.read())
        gf.close()
        __addon__.setSetting('port_path',pfile)
        print aceport
    except: aceport=62062

def construct_request(params):
    return '%s?%s' % (sys.argv[0], urllib.urlencode(params))
 
def GET(target, post=None):
    try:
        req = urllib2.Request(url = target, data = post)
        req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
        global cookie
        if cookie != "":
            req.add_header('Cookie', cookie)
            
        if cookie == "":
            if os.path.exists(cookiefile):
                fgetcook = open(cookiefile, 'r')
                cookie = fgetcook.read()
                del fgetcook
                try:
                    req.add_header('Cookie', cookie)
                    resp = urllib2.urlopen(req)
                    http = resp.read()
                    if not http.find('Вход') > 1:
                        return http
                    else:
                        cookie = UpdCookie()
                        req.add_header('Cookie', cookie)
                        resp = urllib2.urlopen(req)
                        http = resp.read()
                        if not http.find('Вход') > 1:
                            return http
                        else:
                            showMessage('Torrent TV', 'ОШИБКА авторизации', 3000)
                            return http
                    resp.close()
                except:
                    cookie = UpdCookie()
                    req.add_header('Cookie', cookie)
            else:
                cookie = UpdCookie()
                req.add_header('Cookie', cookie)
        resp = urllib2.urlopen(req)
        http = resp.read()
        resp.close()
        return http
    except Exception, e:
        xbmc.log( '[%s]: GET EXCEPT [%s]' % (addon_id, e), 4 )
        showMessage('HTTP ERROR', e, 5000)
        
def showMessage(message = '', heading='TorrentTV', times = 3000, pics = addon_icon):
    try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading.encode('utf-8'), message.encode('utf-8'), times, pics.encode('utf-8')))
    except Exception, e:
        #xbmc.log( '[%s]: showMessage: Transcoding UTF-8 failed [%s]' % (addon_id, e), 2 )
        try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, pics))
        except Exception, e:
            xbmc.log( '[%s]: showMessage: exec failed [%s]' % (addon_id, e), 3 )

def GetCookie(target, post=None):
    try:
        req = urllib2.Request(url = target, data = post)
        req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
        resp = urllib2.urlopen(req)
        #print resp.headers['Set-Cookie']
        #for i in resp.headers:
            #print i
        cookie = resp.headers['Set-Cookie'].split(";")[0]
        http=resp.read()
        resp.close()
        if not http.find('Вход') > 1:
            showMessage('Torrent TV', 'Успешная авторизация', 3000)
            return cookie
        else: showMessage('Torrent TV', 'ОШИБКА авторизации', 3000)
    except Exception, e:
        xbmc.log( '[%s]: GET COOKIE EXCEPT [%s]' % (addon_id, e), 4 )
        showMessage('HTTP ERROR: '+str(target), e, 5000)

def UpdCookie():
    if not os.path.exists(PLUGIN_DATA_PATH):
        os.makedirs(PLUGIN_DATA_PATH)
    if os.path.exists(cookiefile):
        os.remove(cookiefile)
    out = open(cookiefile, 'w')
    cookie = ''
    #if GetCookie('http://torrent-tv.ru/auth.php', data) == None:
    if GetCookie('http://1ttv.org/auth.php', data) == None:
        return None
    else:
        cookie = GetCookie('http://1ttv.org/auth.php', data)
    #else:
        #cookie = GetCookie('http://torrent-tv.ru/auth.php', data)
    try:
        out.write(cookie)
        out.close()
        return cookie
    except:
        showMessage('Torrent TV', 'Ошибка подключения')
        return None        

def GetScript(params):
    import time
    xbmc.executebuiltin( "ActivateWindow(%d)" % ( 10147 ) )
    window = xbmcgui.Window( 10147 )


########################
    try:
        import YaTv
        ncl=dx[params['title']]
        #print ncl
        txtProgram=YaTv.GetPrDay(ncl)
        print txtProgram
    except:
        txtProgram='Нет программы'
#########################
        
        xbmc.sleep(13)
        window.getControl(1).setLabel(ch['name'])
        window.getControl(5).setText(txtProgram)
    
#####################################

dx={
"1 HD": "1329",
"1+1": "1480",
#"112 Украина": "921vsetv",
#"112 Украина HD": "921vsetv",
#"112": "921vsetv",
"112 Украина": "1555",
"112 Украина HD": "1555",
"112": "1555",
"100 ТВ": "382vsetv",
"2+2": "1468",
"24 Док": "16",
"24 Техно": "1436",
"Техно 24": "1436",
#"24 Украина": "298vsetv",
"24 Украина": "1478",
"2x2": "323",
"2х2 (+2)": "809vsetv",
"2x2 (+5)": "734vsetv",
"365 Дней": "250",
#"360 градусов": "653vsetv",
#"360 градусов HD": "653vsetv",
"360 градусов": "161",
"360 градусов HD": "161",
"5 канал (Украина)": "1462",
"5 канал Украина": "1462",
"8 канал": "217",
"9 ТВ Орбита": "782vsetv",
"9 волна": "909vsetv",
"9 Волна": "909vsetv",
#"ab moteurs": "127vsetv",
"ab moteurs": "579",
"Al Jazeera English": "240vsetv",
#"Amedia 1": "895vsetv",
"Amedia 1": "1371",
#"Amedia Premium": "896vsetv",
#"Amedia Premium HD": "896vsetv",
#"Amedia Premium HD (SD)": "896vsetv",
"Amedia Premium": "1372",
"Amedia Premium HD": "1372",
"Amedia Premium HD (SD)": "1372",
"Amedia Hit HD": "1016vsetv",
"Amazing Life": "658",
"Amedia 2": "918",
"Animal Planet": "365",
"Animal Planet HD": "990",
"ATR": "763vsetv",
"A-One": "680",
#"A-ONE UA": "772vsetv",
#"A-One UA": "772vsetv",
"A-ONE UA": "1525",
"A-One UA": "1525",
"AXN Sci-Fi": "516",
"SONY Sci-Fi": "516",
"Sony Sci-Fi": "516",
"BBC World News": "828",
"Bridge TV": "151",
#"Bloomberg": "90vsetv",
#"Boomerang": "404vsetv",
"Bloomberg": "463",
"Boomerang": "929",
#"Business": "386vsetv",
"Business": "929",
"Cartoon Network": "601",
"CCTV 4": "904vsetv",
"CCTV Русский": "598vsetv",
"CBS Drama": "911",
"CBS Reality": "912",
#"CNN International": "47vsetv",
"CNN International": "495",
"CNL": "392vsetv",
"Comedy TV": "51",
"C Music": "319",
"Dange TV": "862vsetv",
"Da Vinci Learning": "410",
"DIVA Universal Russia": "713",
"Dobro TV": "937",
"Docu Box HD": "993vsetv",
#"Deutsche Welle": "84vsetv",
"Deutsche Welle": "355",
"Discovery Channel": "325",
"Discovery Science": "409",
"Discovery Science HD": "409",
"Discovery World": "437",
"Investigation Discovery Europe": "19",
"Investigation Discovery": "19",
"ID Xtra": "943vsetv",
"ID Xtra Europe": "1000vsetv",
#"IQ HD RU": "944vsetv",
#"IQ HD": "944vsetv",
"IQ HD RU": "1330",
"IQ HD": "1330",
"Daring TV": "696vsetv",
"Discovery HD Showcase": "111",
"Discowery HD Showcase": "111",
"Discovery Showcase HD": "111",
#"Discovery Channel HD": "938vsetv",
"Discovery Channel HD": "325",
"Disney Channel": "150",
"Disney Channel(+2)": "645vsetv",
"E Entertainment": "713",
"Е! Entertainment": "713",
"Е Entertainment": "713",
"English Club TV": "757",
"Enter Film": "1547",
"EuroNews": "23",
"EuroNews UA": "23",
"Europa Plus TV": "681",
"Eurosport": "737",
"Eurosport Int. (Eng)": "737",
"Eurosport 2": "850",
"Eurosport 2 Int. (Eng)": "850",
"Eurosport 2 HD": "850",
"Eurosport HD": "560",
"Eureka HD": "970vsetv",
"Extreme Sports": "288",
"Fast and Fun Box HD": "994vsetv",
"Fashion TV": "661",
"Fashion Box HD": "996vsetv",
"Fashion TV HD": "121",
"Fashion HD": "121",
"Fashion One HD": "919",
"Fashion One": "919",
"Fox": "659",
"FOX HD": "659",
"Fox HD": "659",
"Fox Life": "615",
"FOX life HD": "464",
"FOX Life HD": "464",
"Fox Life HD": "464",
"France 24": "187",
"France24": "187",
#"Fine Living": "406vsetv",
"Fine Living": "393",
"Film Box": "998vsetv",
"Filmbox ArtHouse": "997vsetv",
"Food Network": "1005vsetv",
"Galaxy TV": "924",
"GALAXY": "924",
"Gulli": "810",
"GLAS": "457vsetv",
"HD Life": "415",
"HD Life (SD)": "415",
"HD Спорт": "429",
"HD СПОРТ": "429",
"HD Кино": "987",
"HD Кино 2": "988",
#"History Channel": "902vsetv",
#"History Channel HD": "905vsetv",
"History Channel": "1394",
"History Channel HD": "1394",
"Hustler TV": "666vsetv",
"ICTV": "1502",
"iConcerts TV HD": "927",
"iConcerts HD": "927",
"JimJam": "494",
"Jewish News One": "796vsetv",
"JN1": "796vsetv",
"Kids co": "598",
"KidsCo": "598",
"Lale": "911vsetv",
"Life News": "1032",
"LifeNews": "1032",
"Life News HD": "1032",
"Look TV": "726vsetv",
"Luxe TV HD": "536vsetv",
#"Luxury World": "946vsetv",
"Luxury World": "1026",
"Maxxi-TV": "1485",
"MCM Top": "533",
#"MGM": "608",
"AMC": "608",
"MGM HD": "934",
"Mezzo": "575",
#"Mezzo Live HD": "672vsetv",
"Mezzo Live HD": "801",
"Motor TV": "531",
"Motors TV": "531",
"Motors Tv": "531",
"MTV Russia": "1021",
"MTV Россия": "1021",
"MTV Ukraina": "353vsetv",
"MTV Dance": "332",
"MTV Hits UK": "849",
"MTV Hits": "849",
"MTV Rocks": "388",
"MTV Music": "430",
"MTV live HD": "382",
"MTV Live HD": "382",
#"Music Box UA": "417vsetv",
"Music Box UA": "1492",
"Music Box": "642",
"Music Box TV": "642",
"Russian Music Box": "25",
"Music Box RU": "25",
"myZen.tv HD": "141",
"MyZen TV HD": "141",
"NBA TV": "790vsetv",
"Nat Geo Wild": "807",
"Nat Geo Wild HD": "807",
"National Geographic": "102",
"National Geographic HD": "389",
"Nautical Channel": "934vsetv",
"News One": "247",
#"NHK World TV": "789vsetv",
"NHK World TV": "921",
"Nick Jr.": "917",
"Nickelodeon": "567",
"Nickelodeon HD": "423",
"Ocean-TV": "55",
"O-TV": "1510",
#"OE": "982vsetv",
"OE": "1557",
"Outdoor HD": "1033",
"Outdoor Channel": "322",
"Outdoor Channel HD": "1033",
"Paramount Comedy": "920",
#"Paramount Channel": "935vsetv",
"Paramount Channel": "1359",
"Playboy TV": "663vsetv",
"Private Spice": "143vsetv",
"Brazzers TV Europe": "143vsetv",
"QTV": "1498",
"Real Estate-TV": "481vsetv",
"RTVi": "76",
"R1": "405vsetv",
"RU TV": "258",
#"Ru Music": "388vsetv",
"Ru Music": "1488",
"Rusong TV": "591",
"Russian Travel Guide": "648",
"Russia Today Documentary": "788vsetv",
"Russia Today": "313",
"Russia Today HD": "313",
"Russian Travel Guide HD": "900vsetv",
"RTG HD": "900vsetv",
#"SHOPping-TV (Ukraine)": "810vsetv",
"SHOPping-TV (Ukraine)": "1528",
"Shop 24": "863vsetv",
"Shopping Live": "752vsetv",
"SET": "311",
"SET HD": "311",
"S.E.T": "311",
"Sony Turbo": "935",
"Smile of Child": "789",
"Star TV Ukraine": "513vsetv",
"STV": "165",
"Style TV": "119",
"Style tv": "119",
#"Teen TV": "448vsetv",
"Teen TV": "716",
"Teletravel HD": "331",
"TiJi": "555",
"TLC": "425",
"TLC Europe": "777vsetv",
"TLC HD": "901vsetv",
"Tonis": "1471",
"Tonis HD": "1526",
#"Top Shop": "1003vsetv",
"Topsong TV": "1003vsetv",
"TVCI": "435",
"TV Rus": "799vsetv",
"TV5 Monde": "74vsetv",
"TV5 Monde": "589",
"TV 1000": "127",
"TV1000": "127",
"TV 1000 Action East": "125",
"TV 1000 Action": "125",
"TV 1000 Русское кино": "267",
"TV1000 Action East": "125",
"TV1000 Action": "125",
"TV1000 Русское кино": "267",
#"TV1000 Megahit HD": "816vsetv",
#"TV1000 Premium HD": "814vsetv",
#"TV1000 Comedy HD": "818vsetv",
#"TV 1000 Megahit HD": "816vsetv",
#"TV 1000 Premium HD": "814vsetv",
#"TV 1000 Comedy HD": "818vsetv",
#"TV1000 Comedy": "817vsetv",
"TV1000 Megahit HD": "1012",
"TV1000 Premium HD": "1013",
"TV1000 Comedy HD": "1011",
"TV 1000 Megahit HD": "1012",
"TV 1000 Premium HD": "1013",
"TV 1000 Comedy HD": "1011",
"TV1000 Comedy": "1011",
#"Travel Channel": "88vsetv",
#"Travel Channel HD": "690vsetv",
"Travel Channel": "613",
"Travel Channel HD": "124",
#"Travel+ adventure": "832vsetv",
#"Travel + adventure": "832vsetv",
"Travel+ adventure": "996",
"Travel + adventure": "996",
"Travel + adventure HD": "1035",
"Travel+ adventure HD": "1035",
"TV XXI (TV21)": "309",
#"Ukrainian Fashion": "939",
"Universal Channel": "213",
"Ukrainian Fashion": "773vsetv",
"VH1": "491",
"VH1 Classic": "156",
"Viasat Explorer": "521",
"Viasat Explore": "521",
"Viasat Explorer CEE": "521",
"Viasat Explore CEE": "521",
"Viasat History": "277",
"Viasat Nature East": "765",
"Viasat Sport": "455",
"Viasat Sport HD": "455",
"VIASAT Sport Baltic": "504vsetv",
"Viasat Sport Baltic": "504vsetv",
"Viasat Golf": "906vsetv",
"Viasat Golf HD": "916vsetv",
"Sport Baltic": "504vsetv",
"Viasat Nature-History HD": "716vsetv",
"Viasat Nature/History HD": "716vsetv",
"World Fashion": "346",
"XSPORT": "748vsetv",
"Xsport": "748vsetv",
"XXL": "664vsetv",
"Zee TV": "626",
"Zoom": "1484",
#"Zik": "684vsetv",
"Zik": "1511",
"Авто плюс": "153",
"Авто 24": "924vsetv",
"Агро тв": "11",
"Амедиа": "918",
"Астро ТВ": "249",
"Астро": "249",
"Беларусь 24": "851",
#"Бигуди": "481vsetv",
"Бигуди": "1500",
"Боец": "454",
"Бойцовский клуб": "986",
#"БТБ": "877vsetv",
"БТБ": "1537",
"БСТ": "272vsetv",
"Вопросы и ответы": "333",
"Вместе РФ": "967vsetv",
"Время": "669",
"ВТВ": "139vsetv",
#"Гамма": "479vsetv",
"Гамма": "1499",
#"Глас": "294vsetv",
#"Глас ТВ": "294vsetv",
"Глас": "1477",
"Глас ТВ": "1477",
"Гумор ТБ": "505vsetv",
"Детский": "66",
"Детский мир": "747",
"Дождь": "384",
"Дождь HD": "384",
"Дом кино": "834",
"Домашние животные": "520",
"Домашние Животные": "520",
"Домашний": "304",
"Домашний магазин": "695vsetv",
#"Донбасс": "617vsetv",
"Донбасс": "1508",
"Драйв ТВ": "505",
"Еврокино": "352",
"ЕДА": "931",
"Еда": "931",
"Еда ТВ": "931",
"ЕДА HD": "930",
"Еда HD": "930",
#"Еспресо ТВ": "936vsetv",
"Еспресо ТВ": "1552",
"Живи": "113",
"Живая Планета": "1562",
"Звезда": "405",
"Закон ТВ": "178",
"Закон тв": "178",
"Закон-тв": "178",
"Закон ТВ": "178",
"Загородный": "705",
"Загородная жизнь": "21",
"Знание": "201",
"Здоровое ТВ": "595",
"Зоо ТВ": "273",
"Зоопарк": "367",
"Иллюзион+": "123",
"Искушение": "754vsetv",
"Индия": "798",
"Интер": "1489",
"Интер+": "1514",
"Индиго TV": "1456",
"Интересное ТВ": "24",
"Израиль плюс": "532vsetv",
#"История": "879vsetv",
"История": "1036",
"К1": "1465",
#"К2": "20vsetv",
"К2": "1466",
"Карусель": "740",
"Карусель International": "688vsetv",
"Карусель (+3)": "730vsetv",
"Кинопоказ": "22",
"Кинопоказ 1 HD": "138",
"Кинопоказ 2 HD": "741",
"Кинопремиум HD": "947vsetv",
"Кино ТВ": "1037",
"КиноТВ": "1037",
"Комедия ТВ": "821",
"комедия тв": "821",
"Комсомольская правда": "852",
"Кто есть кто": "769",
"Кто Есть Кто": "769",
#"КРТ": "149vsetv",
"КРТ": "1464",
#"Киевская Русь": "149vsetv",
"Киевская Русь": "1464",
"Кухня ТВ": "614",
#"Культура Украина": "285vsetv",
"Культура Украина": "1476",
"КХЛ ТВ": "481",
"КХЛ HD": "481",
#"Кубань 24 Орбита": "782vsetv",
"Кубань 24 Орбита": "1392",
"Ля-минор": "257",
#"Львов ТВ": "920vsetv",
#"Lviv TV": "920vsetv",
"Львов ТВ": "1548",
"Lviv TV": "1548",
"М1": "1553",
#"М2": "445vsetv",
"М2": "1495",
#"Марс TV": "928vsetv",
"Марс TV": "1550",
"Мега": "1469",
"Меню ТВ": "348vsetv",
"Мир": "726",
"Мир HD": "965vsetv",
"Мир (+3)": "529vsetv",
"Меню ТВ": "348vsetv",
#"Мир 24": "838vsetv",
"Мир 24": "1331",
"Мир сериала": "145",
"Мир Сериала": "145",
"Много ТВ": "799",
"Многосерийное ТВ": "799",
"Моя планета": "675",
"Москва 24": "334",
"Москва Доверие": "655",
"Москва доверие": "655",
"Музыка Первого": "715",
"Мужской": "82",
#"Малятко ТВ": "606vsetv",
"Малятко ТВ": "1507",
"Моя дитина": "761vsetv",
"Мать и дитя": "618",
"Мать и Дитя": "618",
"Мама": "618",
"Мультимания": "31",
#"Муз ТВ": "808vsetv",
"Муз ТВ": "897",
#"Мульт": "962vsetv",
#"Надия": "871vsetv",
#"Надiя": "871vsetv",
"Мульт": "1332",
"Надия": "1534",
"Надiя": "1534",
"Нано ТВ": "35",
"Наука 2.0": "723",
"Наше любимое кино": "477",
"НЛО ТВ": "843vsetv",
"Новый канал": "1515",
"Ностальгия": "783",
"Ночной клуб": "455vsetv",
"НСТ": "518",
"НТВ": "162",
"НТВ (+3)": "509vsetv",
"НТВ (+4)": "546vsetv",
"НТВ (+7)": "547vsetv",
"НТВ Мир": "422",
"НТВ МИР": "422",
"НТВ+ Кино плюс": "644",
"НТВ+ Киноклуб": "462",
"НТВ+ Кинолюкс": "8",
"НТВ+ Киносоюз": "71",
"НТВ+ Кино Cоюз": "71",
"НТВ+ Кино Союз": "71",
"НТВ+ Кинохит": "542",
"НТВ+ Наше кино": "12",
"НТВ+ Наше новое кино": "485",
"НТВ+ Премьера": "566",
"НТВ+ Баскетбол": "697",
"НТВ+ Наш футбол": "499",
"НТВ+ Наш футбол HD": "499",
"НТВ+ Спорт": "134",
"НТВ+СПОРТ": "134",
"НТВ+ Спорт Онлайн": "183",
"НТВ+ Спорт онлайн": "183",
"НТВ+ Спорт Союз": "306",
"НТВ+ Спорт плюс": "377",
"НТВ+ СпортХит": "910vsetv",
"НТВ+ Спорт Хит": "910vsetv",
"НТВ+ Спорт Хит HD": "917vsetv",
"НТВ+ СпортХит HD": "917vsetv",
"НТВ+ Спортхит": "910vsetv",
"НТВ+ Теннис": "358",
"НТВ+ Футбол": "664",
"НТВ+ Футбол 1": "664",
"НТВ+ Футбол 2": "563",
"НТВ+ Футбол 3": "1039",
"НТВ+ Футбол HD": "664",
"НТВ+ Футбол 1 HD": "664",
"НТВ+ Футбол 2 HD": "563",
"НТВ+ Футбол 3 HD": "1039",
"НТВ+ 3D": "702vsetv",
"НТН (Украина)": "1467",
#"НТС Севастополь": "884vsetv",
"НТС Севастополь": "1538",
"О2ТВ": "777",
"О2 ТВ": "777",
"Оружие": "376",
"ОСТ": "926",
#"ОТР": "880vsetv",
"ОТР": "1000",
"ОТС": "899vsetv",
"ОНТ Украина": "111vsetv",
"Открытый Мир": "692vsetv",
"Остросюжетное HD": "951vsetv",
"Охота и рыбалка": "617",
"Охотник и рыболов": "132",
"Охотник и рыболов HD": "842vsetv",
"Парк развлечений": "37",
"Первый автомобильный (укр)": "1493",
"Первый автомобильный (Украина)": "1493",
"Первый деловой": "85",
"Первый канал": "146",
"Первый канал (+4)": "542vsetv",
"Первый канал (+6)": "543vsetv",
"Первый канал (Европа)": "21vsetv",
"Первый канал (Украина)": "339vsetv",
"Первый канал Украина": "339vsetv",
"Первый канал (СНГ)": "314vsetv",
"Первый канал HD": "983",
"Первый канал HD (+4)": "926vsetv",
"ПЕРВЫЙ HD": "983",
"ПИК HD": "922",
"Первый муниципальный (Донецк)": "670vsetv",
"Первый национальный (Украина)": "1505",
"ПЕРШИЙ UKRAINE": "1531",
"Первый Метео": "59",
"Первый образовательный": "774",
"Перец": "511",
"Пиксель ТВ": "1472",
#"ПлюсПлюс": "24vsetv",
"ПлюсПлюс": "1470",
"Погода ТВ": "759vsetv",
"Подмосковье": "161",
"Про все": "458",
"Pro Все": "458",
"Про Все": "458",
#"Право ТВ": "861vsetv",
"Право ТВ": "1533",
"Просвещение": "685",
"Психология 21": "434",
"Пятый канал": "427",
"Пятница": "1003",
"Пятница (+2)": "625vsetv",
#"Рада Украина": "823vsetv",
"Рада Украина": "1530",
#"Радость Моя": "693vsetv",
#"Радость моя": "693vsetv",
"Радость Моя": "638",
"Радость моя": "638",
"Раз ТВ": "363",
"РАЗ ТВ": "363",
"РБК": "743",
"РЕН ТВ": "689",
"РЕН ТВ  (+7)": "572vsetv",
"РЕН ТВ (+4)": "571vsetv",
"РЖД": "509",
"РЖД ТВ": "509",
"Ретро ТВ": "6",
"Россия 1": "711",
"Россия 1 (+4)": "549vsetv",
"Россия 1 (+2)": "548vsetv",
"Россия 1 (+6)": "550vsetv",
"Россия 2": "515",
"Россия 24": "328vsetv",
"Россия К": "187",
"РОССИЯ HD": "984",
"Россия HD": "984",
"РТР-Планета": "143",
"РТР Планета": "143",
"РТР Россия": "98vsetv",
"Русский Бестселлер": "994",
"Русский бестселлер": "994",
"Русский иллюзион": "53",
"Русский роман": "401",
"Русский экстрим": "406",
"Русский детектив": "942vsetv",
"Русский Детектив": "942vsetv",
"Русская ночь": "296vsetv",
"Сарафан ТВ": "663",
"Сарафан": "663",
#"Сонце": "874vsetv",
"Сонце": "1535",
"Спас": "447",
"Спас ТВ": "447",
"Спорт 1": "181",
"Спорт": "154",
"Спорт 1 HD": "554",
#"Спорт 1 (Украина)": "270vsetv",
#"Спорт 2 (Украина)": "309vsetv",
"Спорт 1 (Украина)": "1473",
"Спорт 2 (Украина)": "1481",
"Совершенно секретно": "275",
"Союз": "349",
"СТБ": "1506",
"СТС": "79",
"СТС (+2)": "538vsetv",
"СТС (+4)": "539vsetv",
"СТС International": "758vsetv",
#"СТС Love": "952vsetv",
"СТС Love": "1322",
"Стиль и мода": "863vsetv",
"Страна": "284",
"Страшное HD": "1377",
"Семейное HD": "949vsetv",
"Сериал HD": "950vsetv",
"ТБН": "576",
"Тбн": "576",
#"ТБН": "694vsetv",
#"ТНВ-Планета": "781vsetv",
"ТНВ-Планета": "933",
"ТНВ-Татарстан": "145vsetv",
"ТНВ-ТАТАРСТАН": "145vsetv",
"ТВ-Центр-Международное": "435",
"ТВ Центр Международный": "435",
"ТДК": "776",
"ТВ 3": "698",
"ТВ 3 (+3)": "845vsetv",
"ТВ 3 (+2)": "564vsetv",
"ТВі": "650",
"TBi": "650",
"ТВi": "650",
"ТВЦ": "649",
"ТВ Центр": "649",
"Театр": "925",
"Телеканал 100": "887vsetv",
"ТНТ": "353",
"ТНТ (+2)": "556vsetv",
"ТНТ (+3)": "767vsetv",
"ТНТ (+4)": "557vsetv",
"ТНТ (+7)": "558vsetv",
"ТНТ Comedy": "51",
"ТНТ Comedy (Европа)": "991vsetv",
"ТНТ Bravo Молдова": "737vsetv",
"тнт+4": "557vsetv",
"Тонус ТВ": "637",
"Тонус-ТВ": "637",
"Телекафе": "173",
"Теледом HD": "853vsetv",
"Телепутешествия": "794",
"Телепутешествия HD": "331",
"ТЕТ": "1559",
"ТРК Украина": "1463",
#"ТРК Киев": "75vsetv",
"ТРК Киев": "1522",
"Точка ТВ": "1396",
"Ukraine": "326",
"ТРО Союза": "730",
"ТРО": "730",
"Успех": "547",
#"Улыбка ребенка": "531vsetv",
"Улыбка ребенка": "789",
"Усадьба": "779",
#"Унiан": "740vsetv",
#"УТР": "689vsetv",
"Унiан": "1521",
"УТР": "1513",
"Феникс+ Кино": "686",
"Футбол": "328",
"Футбол (украина)": "666",
"Футбол+ (украина)": "753",
"Футбол 1 Украина": "1503",
"Футбол 2 Украина": "1516",
"Футбол 1 (Украина)": "1503",
"Футбол 2 (Украина)": "1516",
"Футбол 1 HD (Украина)": "1503",
"Футбол 2 HD (Украина)": "1516",
"Хокей": "702",
"ЧП-Инфо": "315",
"Черноморская телекомпания": "751vsetv",
#"Центральный канал": "317vsetv",
"Центральный канал": "1483",
"Шансон ТВ": "662",
"Ю": "898",
"Юмор ТВ": "412",
"Юмор тв": "412",
"Юмор BOX": "412",
"Юмор Box": "412",
#"Эко-ТВ": "685vsetv",
"Эко-ТВ": "1512",
"Эгоист ТВ": "431",
}
#####################################       
def GetChannelsDB (params):
#########################
    try:
        import YaTv
    except: pass
#########################
    db = DataBase(db_name, cookie)
    channels = None
    if not params.has_key('group'):
        return
    elif params['group'] == '0':
        channels = db.GetChannels(adult = adult)
    elif params['group'] == 'hd':
        channels = db.GetChannelsHD(adult = adult)
    elif params['group'] == 'latest':
        channels = db.GetLatestChannels(adult = adult)
    elif params['group'] == 'new':
        channels = db.GetNewChannels(adult = adult)
    elif params['group'] == 'favourite':
        channels = db.GetFavouriteChannels(adult = adult)
    else:
        channels = db.GetChannels(params['group'], adult = adult)
    import time
    for ch in channels:
        img = ch['imgurl']
        if __addon__.getSetting('logopack') == 'true':
            logo_path = os.path.join(PLUGIN_DATA_PATH, 'logo')
            logo_src = os.path.join(logo_path, ch['name'].decode('utf-8') + '.png')
            if os.path.exists(logo_src):
                img = logo_src
        title = ch['name']
        if params['group'] == '0' or params['group'] == 'hd' or params['group'] == 'latest' or params['group'] == 'new':
            title = '[COLOR FF7092BE]%s:[/COLOR] %s' % (ch['group_name'], title)
 ###################################
        try:
            d=[]
            ni=dx[ch['name'].replace(" (резерв)","").replace(" (Резерв)","").replace("(резерв)","").replace("(Резерв)","")]
            d=YaTv.GetPr(id2=ni)
        except:ni=ch['name']
        try:prog = d["plot"]
        except:prog =""
        try:
            tbn=d["img"]
            if tbn == '': tbn = img
        except:tbn = img
        try:
            genre = d["genre"]
            if genre == "": genre = ch['group_name']
        except:genre = ch['group_name']
        if ch_b == "true":
            if ch_i == "true": title = "[I][B][COLOR FF"+ch_color+"]" + title + "[/COLOR][/B][/I]"
            else: title = "[B][COLOR FF"+ch_color+"]" + title + "[/COLOR][/B]"
        else:
            if ch_i == "true": title = "[I][COLOR FF"+ch_color+"]" + title + "[/COLOR][/I]"
            else: title = "[COLOR FF"+ch_color+"]" + title + "[/COLOR]"
        try:
            if d["strt"] > time.time(): title = title
            else: title =title +pr_str+d["plttime"]+" "+d["pltprog"]
            prog =chr(10)+prog
            #if d["strt"] > time.time(): prog1 = ""
            #else:
                #try:prog1 = d["prog1"]
                #except:prog1 = ""
        except:
            try:title =title +pr_str+d["plttime"]+" "+d["pltprog"]
            except:title =title
            prog =chr(10)+prog
            #try:prog1 = d["prog1"]
            #except:prog1 = ""
        #if prog1 == "":
            #prog1 = title
        try:title1 = (d["plttime"]+" "+d["pltprog"]).strip()
        except:title1 = title
        if __addon__.getSetting('fanart') == 'false':
            if __addon__.getSetting('disable') == 'false':
                li = xbmcgui.ListItem(title, title, img, img)
                li.setProperty('fanart_image', tbn.encode('utf-8'))
            else:
                li = xbmcgui.ListItem(title, title, img, img)
                li.setProperty('fanart_image', img)
        else:
            if __addon__.getSetting('disable') == 'false':
                li = xbmcgui.ListItem(title, title, img, tbn.encode('utf-8'))
            else:
                li = xbmcgui.ListItem(title, title, img, img)
        startTime = time.localtime()#float(item['start'])
        endTime = time.localtime()#item['end']
        li.setProperty('IsPlayable', 'true')
        li.setInfo(type = "Video", infoLabels = {"Title": ch['name'], 'year': endTime.tm_year, 'genre': genre, 'plot': prog})
 ###################################           
        uri = construct_request({
            'func': 'play_ch_db',
            'img': img.encode('utf-8'),
            'title': title1,
            'file': ch['urlstream'],
            'id': ch['id']
        })
        deluri = construct_request({
            'func': 'DelChannel',
            'id': ch['id']
        })
        favouriteuri = construct_request({
            'func': 'FavouriteChannel',
            'id': ch['id']
        })
        delfavouriteuri = construct_request({
            'func': 'DelFavouriteChannel',
            'id': ch['id']
        })
        deldb = construct_request({
            'func': 'DelDB',
        })
        commands = []
        if params['group'] != 'favourite':
            commands.append(('[COLOR FF669933]Добавить[/COLOR][COLOR FFB77D00] в "ИЗБРАННЫЕ"[/COLOR]', 'XBMC.RunPlugin(%s)' % (favouriteuri),))
        commands.append(('[COLOR FFCC3333]Удалить[/COLOR][COLOR FFB77D00] из "ИЗБРАННЫЕ"[/COLOR]', 'XBMC.RunPlugin(%s)' % (delfavouriteuri),))
        commands.append(('Удалить канал', 'XBMC.RunPlugin(%s)' % (deluri),))
        commands.append(('Удалить БД каналов', 'XBMC.RunPlugin(%s)' % (deldb),))
        li.addContextMenuItems(commands)
        xbmcplugin.addDirectoryItem(hos, uri, li)
    xbmcplugin.endOfDirectory(hos)
    #xbmc.executebuiltin('Container.SetViewMode(%s)' % view_mode)
    del db
    
def DelChannel(params):
    db = DataBase(db_name, cookie)
    db.DelChannel(params['id'])
    showMessage(message = 'Канал удален')
    xbmc.executebuiltin("Container.Refresh")
    del db

def FavouriteChannel(params):
    db = DataBase(db_name, cookie)
    db.FavouriteChannel(params['id'])
    showMessage(message = 'Канал добавлен')
    xbmc.executebuiltin("Container.Refresh")
    del db
    
def DelFavouriteChannel(params):
    db = DataBase(db_name, cookie)
    db.DelFavouriteChannel(params['id'])
    showMessage(message = 'Канал удален')
    xbmc.executebuiltin("Container.Refresh")
    del db

def DelDB(params):
    db = DataBase(db_name, cookie)
    #db.RemoveDB()
    rem = db.RemoveDB()
    if rem == 0:
        xbmc.executebuiltin("Container.Refresh")
        showMessage(message = 'База каналов удалена')
    elif rem == 1:
        showMessage(message = 'Не удалось удалить базу каналов')
    else:
        showMessage(message = 'База каналов уже удалена')    
    del db
    
def GetChannelsWeb(params):
#########################
    try:
        import YaTv
    except: pass
#########################
    #http = GET('http://torrent-tv.ru/' + params['file'])
    #if http == None:
    http = GET('http://1ttv.org/' + params['file'])
    if http == None:
        showMessage('Torrent TV', 'Сайты не отвечают')
        return
    #print http
    beautifulSoup = BeautifulSoup(http)
    channels=beautifulSoup.findAll('div', attrs={'class': 'best-channels-content'})
    for ch in channels:
        link =ch.find('a')['href']
        title= ch.find('strong').string.encode('utf-8').replace('\n', '').strip()
        img='http://torrent-tv.ru/'+ch.find('img')['src']
        if __addon__.getSetting('logopack') == "true":
            logo_path = os.path.join(PLUGIN_DATA_PATH, 'logo')
            logo_src = os.path.join(logo_path, ch.find('strong').string.replace('\n', '').replace('  ', '') + '.png')
            if os.path.exists(logo_src):
                img = logo_src
 ###################################
        try:
            d=[]
            ni=dx[title.strip().replace(" (резерв)","").replace("( Резерв)","").replace("(резерв)","").replace("(Резерв)","")]
            d=YaTv.GetPr(id2=ni)
        except:ni=title.strip()
        #except:ni=title.strip()
        try:prog = d["plot"]
        except:prog =""
        try:
            tbn=d["img"]
            if tbn == '': tbn = img
        except:tbn = img
        try:genre = d["genre"]
        except:genre = ''
        if ch_b == "true":
            if ch_i == "true": title = "[I][B][COLOR FF"+ch_color+"]" + title + "[/COLOR][/B][/I]"
            else: title = "[B][COLOR FF"+ch_color+"]" + title + "[/COLOR][/B]"
        else:
            if ch_i == "true": title = "[I][COLOR FF"+ch_color+"]" + title + "[/COLOR][/I]"
            else: title = "[COLOR FF"+ch_color+"]" + title + "[/COLOR]"
        try:
            if d["strt"] > time.time(): title = title
            else: title =title +pr_str+d["plttime"]+" "+d["pltprog"]
            prog =chr(10)+prog
            #if d["strt"] > time.time(): prog1 = ""
            #else:
                #try:prog1 = d["prog1"]
                #except:prog1 = ""
        except:
            try:title =title +pr_str+d["plttime"]+" "+d["pltprog"]
            except:title =title
            prog =chr(10)+prog
            #try:prog1 = d["prog1"]
            #except:prog1 = ""
        #if prog1 == "":
            #prog1 = title
        try:title1 = (d["plttime"]+" "+d["pltprog"]).strip()
        except:title1 = title
        if __addon__.getSetting('fanart') == 'false':
            if __addon__.getSetting('disable') == 'false':
                li = xbmcgui.ListItem(title, title, img, img)
                li.setProperty('fanart_image', tbn.encode('utf-8'))
            else:
                li = xbmcgui.ListItem(title, title, img, img)
                li.setProperty('fanart_image', img)
        else:
            if __addon__.getSetting('disable') == 'false':
                li = xbmcgui.ListItem(title, title, img, tbn.encode('utf-8'))
            else:
                li = xbmcgui.ListItem(title, title, img, img)


        startTime = time.localtime()#float(item['start'])
        endTime = time.localtime()#item['end']
        li.setProperty('IsPlayable', 'true')
        li.setInfo(type = "Video", infoLabels = {"Title": title, 'year': endTime.tm_year, 'genre': genre, 'plot': prog} )
 ###################################           

                
        uri = construct_request({
                'func': 'play_ch_web',
                'img':img.encode('utf-8'),
                'title':title1,
                'file':link
        })
        commands = []
        li.addContextMenuItems(commands)
        xbmcplugin.addDirectoryItem(hos, uri, li)
    xbmcplugin.endOfDirectory(hos)
    #xbmc.executebuiltin('Container.SetViewMode(%s)' % view_mode)

def GetFilms(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    li = xbmcgui.ListItem('Новинки')
    uri = construct_request({
        'func': 'getPages',
        'file': '/film_selector.php?new',
        'page': '1',
    })
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    li = xbmcgui.ListItem('Сериалы')
    uri = construct_request({
        'func': 'getPages',
        'file': '/film_selector.php?serials',
        'page': '1',
    })
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    li = xbmcgui.ListItem('Последние фильмы')
    uri = construct_request({
        'func': 'getPages',
        'file': '/film_selector.php?last_added',
        'page': '1',
    })
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    li = xbmcgui.ListItem('HD-фильмы')
    uri = construct_request({
        'func': 'getPages',
        'file': '/film_selector.php?specific=hd',
        'page': '1',
    })
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    li = xbmcgui.ListItem('Фильмы HD 1080')
    uri = construct_request({
        'func': 'getPages',
        'file': '/film_selector.php?specific=1080',
        'page': '1',
    })
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    li = xbmcgui.ListItem('Фильмы HD 4k')
    uri = construct_request({
        'func': 'getPages',
        'file': '/film_selector.php?specific=4k',
        'page': '1',
    })
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    li = xbmcgui.ListItem('Фильмы в 3D')
    uri = construct_request({
        'func': 'getPages',
        'file': '/film_selector.php?specific=3d',
        'page': '1',
    })
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    li = xbmcgui.ListItem('Русские')
    uri = construct_request({
        'func': 'getPages',
        'file': '/film_selector.php?specific=rus',
        'page': '1',
    })
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    li = xbmcgui.ListItem('Зарубежные')
    uri = construct_request({
        'func': 'getPages',
        'file': '/film_selector.php?specific=foreign',
        'page': '1',
    })
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    li = xbmcgui.ListItem('Популярное за неделю')
    uri = construct_request({
        'func': 'getPages',
        'file': '/film_selector.php?specific=weektop',
        'page': '1',
    })
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    li = xbmcgui.ListItem('Каталог фильмов')
    uri = construct_request({
        'func': 'getABC',
    })
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    li = xbmcgui.ListItem('Категории')
    uri = construct_request({
        'func': 'getCat',
    })
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    li = xbmcgui.ListItem('[COLOR FFFF6347]<< ПОИСК ФИЛЬМОВ >>[/COLOR]')
    uri = construct_request({
        'func': 'get_querry',
    })
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    xbmcplugin.endOfDirectory(hos)

def get_querry(params):
    skbd = xbmc.Keyboard()
    skbd.setHeading('Поиск:')
    skbd.doModal()
    if skbd.isConfirmed():
        SearchStr = skbd.getText()
        if SearchStr:
            getPages({'file':'/film_selector.php?search='+SearchStr,
                        'page': '1',
                      })
        else: return

def getCat(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    #http = GET('http://torrent-tv.ru/films.php')
    #if http == None:
    http = GET('http://1ttv.org/films.php')
    if http == None:
        showMessage('Torrent TV', 'Сайты не отвечают')
        return
    beautifulSoup = BeautifulSoup(http)
    next=beautifulSoup.findAll('a', attrs={'class': 'genre_cat_link'})
    title = ''
    file = ''
    for n in next:
        title = n.string.encode('utf-8').strip()
        file = n['href']
        li = xbmcgui.ListItem(title)
        uri = construct_request({
            'func': 'getPages',
            'file': file,
            'page': '1',
        })
        xbmcplugin.addDirectoryItem(hos, uri, li, True)
    xbmcplugin.endOfDirectory(hos)
    
def getABC(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    abc = ['A','B','C','D','E','F','G','H','I','J','K','L','M','O','P','Q','R','S','T','U','V','W','X','Y','Z','А','Б','В','Г','Д','Е','Ж','З','И','К','Л','М','Н','О','П','Р','С','Т','У','Ф','Х','Ц','Ч','Ш','Щ','Ы','Э','Ю','Я']
    li = xbmcgui.ListItem('0-9')
    uri = construct_request({
        'func': 'getPages',
        'file': '/film_selector.php?letter=0',
        'page': '1',
    })
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    for a in abc:
        li = xbmcgui.ListItem(a)
        uri = construct_request({
            'func': 'getPages',
            'file': '/film_selector.php?letter='+a,
            'page': '1',
        })
        xbmcplugin.addDirectoryItem(hos, uri, li, True)
    xbmcplugin.endOfDirectory(hos)


def getPages(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    #http = GET('http://torrent-tv.ru' + params['file']+'&page=1')
    #if http == None:
    http = GET('http://1ttv.org' + params['file']+'&page=1')
    if http == None:
        showMessage('Torrent TV', 'Сайты не отвечают')
        return
    beautifulSoup = BeautifulSoup(http)
    next=beautifulSoup.findAll('div', attrs={'class': 'best-channels'})[1].findAll('a')
    count_ch = 0
    if next:
        count_ch = 1
    for n in next:
        res = re.compile('&page=.*')
        res.findall(str(n['href']))
        se_res = res.findall(str(n['href']))
        if se_res:
            if count_ch < int(se_res[0][6:]):
                count_ch = int(se_res[0][6:])
    if count_ch == 1:
        getFilms({'file': params['file'],
                    'file': params['file'],
                    'page': str(count_ch),
                })
    else:
        for i in range(1,count_ch+1):
            li = xbmcgui.ListItem('[COLOR FF6495ED]Страница '+str(i)+'[/COLOR]')
            uri = construct_request({
                'func': 'getFilms',
                'file': params['file'],
                'page': str(i),
            })
            xbmcplugin.addDirectoryItem(hos, uri, li, True, totalItems=count_ch)
        xbmcplugin.endOfDirectory(hos)

def getFilms(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    page = '&page='+params['page']
    #http = GET('http://torrent-tv.ru' + params['file']+page)
    #if http == None:
    http = GET('http://1ttv.org' + params['file']+page)
    if http == None:
        showMessage('Torrent TV', 'Сайты не отвечают')
        return
    beautifulSoup = BeautifulSoup(http)
    channels=beautifulSoup.findAll('div', attrs={'class': 'best-channels-content'})
    des = beautifulSoup.find(text=re.compile('var descrs = {.*'))
    for ch in channels:
        link =ch.find('a')['href']
        if link.find('person')>-1: continue
        title= ch.find('strong').string.encode('utf-8').replace('\n', '').replace('&nbsp;', '-').replace('&laquo;', '<<').replace('&raquo;', '>>').strip()
        img=ch.find('img')['src']
        res = re.compile("[0-9].*")
        num=res.search(str(link))
        if num:
            numb = num.group()
        else:
            print "Not find"
        numst = '%s_%s:.*' % ('new',str(numb))
        res = re.compile(numst)
        descr = ''
        if des:
            num=res.search(str(des))
            if num:
                descr = num.group().replace('new_'+str(numb)+": '",'').replace("',",'')
            else:
                try:
                    descr= beautifulSoup.findAll('div', attrs={'id': 'descr_new_'+numb})[0].getText().encode('utf-8')
                except: pass
        gen=ch.findAll('a', attrs={'href': re.compile('/film_selector\.php\?genre.*')})
        genre = ''
        if len(gen)>1:
            for g in gen:
                if genre:
                    genre = genre+', '+g.string.encode('utf-8')
                else:
                    genre = g.string.encode('utf-8')
        elif len(gen)==1:
            genre = gen[0].string.encode('utf-8')
        yr = ch.find('p')
        y=str(yr)
        mm=re.compile(': [0-9][0-9][0-9][0-9]')
        m = mm.search(y)
        if m:
            year=m.group(0).split('"')[0].replace(': ','')
        else:year = ''
        if ch_b == "true":
            if ch_i == "true": title = "[I][B][COLOR FF"+ch_color+"]" + title + "[/COLOR][/B][/I]"
            else: title = "[B][COLOR FF"+ch_color+"]" + title + "[/COLOR][/B]"
        else:
            if ch_i == "true": title = "[I][COLOR FF"+ch_color+"]" + title + "[/COLOR][/I]"
            else: title = "[COLOR FF"+ch_color+"]" + title + "[/COLOR]"
        #if __addon__.getSetting('fanart') == 'false':
        li = xbmcgui.ListItem(title, title, img, img)
        li.setProperty('fanart_image', img)
        #else:
            #li = xbmcgui.ListItem(title, title, img, img)
        #li = xbmcgui.ListItem(title, title, img, img)
        #print 'descr: ' +str(descr)
        li.setInfo(type = "Video", infoLabels = {"Title": title, "year": year, 'plot': descr, 'genre': genre})
        uri = construct_request({
                'func': 'GetFilmsWeb',
                'img':img,
                'title':title,
                'file':link,
                'descr':descr,
                'year':year,
                'genre':genre,
        })
        xbmcplugin.addDirectoryItem(hos, uri, li, True)
    xbmcplugin.endOfDirectory(hos)
    xbmc.executebuiltin('Container.SetViewMode(%s)' % view_mode)

def GetFilmsWeb(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    #http = GET('http://torrent-tv.ru/' + params['file'])
    #if http == None:
    http = GET('http://1ttv.org/' + params['file'])
    if http == None:
        showMessage('Torrent TV', 'Сайты не отвечают')
        return
    beautifulSoup = BeautifulSoup(http)
    try:
        if not params.has_key("descr") or params["descr"].find('...')>-1:
            descr = beautifulSoup.findAll('div', attrs={'class': 'channel-description'})[0].string.encode('utf-8')
            #print 'descr : '+str(descr)
        else: descr = params['descr']
    except: descr = ' '
    try:
        if not params.has_key('img'):
            img=beautifulSoup.findAll('div', attrs={'id': 'ctp'})[0].find('img')['src']
            #print 'img :'+str(img)
        else: img = params['img']
    except: img = ' '
    try:
        if not params.has_key('year'):
            year=beautifulSoup.findAll('a', attrs={'href': re.compile('/film_selector\.php\?year.*')})[0].string.encode('utf-8')
            #print 'year :'+str(year)
        else: year = params['year']
    except: year = ' '
    try:
        if not params.has_key('genre'):
            genre=beautifulSoup.findAll('a', attrs={'href': re.compile('/film_selector\.php\?genre.*')})[0].string.encode('utf-8')
            #print 'genre :'+str(genre)
        else: genre = params['genre']
    except: genre = ' '
    rating=''
    #try:
    rat = beautifulSoup.find('div', attrs={'id': 'ratings'})
    if rat:
        rat = rat.getText().encode('utf-8')
        mm=re.compile('IMDb.*')
        m = mm.search(rat)
        if m:
            rating=m.group(0).replace('IMDb&nbsp;','')[:3]
            if rating.find(str(0.00))>-1:
                mm=re.compile('КП.*')
                m = mm.search(rat)
                if m:
                    rating=m.group(0).replace('КП&nbsp;','')[:3]
                    if rating.find(str(0.00))>-1:
                        rating=beautifulSoup.findAll('span', attrs={'id': re.compile('ttv_rating.*')})[0].string.encode('utf-8')[:3]
                else:
                    rating=beautifulSoup.findAll('span', attrs={'id': re.compile('ttv_rating.*')})[0].string.encode('utf-8')[:3]
        else:
            rating=beautifulSoup.findAll('span', attrs={'id': re.compile('ttv_rating.*')})[0].string.encode('utf-8')[:3]
    else: rating=' '
        #print 'rating :'+rating
    #except: pass
    #print 'rating :'+str(rating)
    director=''
    writer=''
    direct=beautifulSoup.find(text=("режиссер").decode('utf-8')).findNext('div')
    #print 'direct :'+str(direct)
    if direct:
        try:
            director = direct.getText().encode('utf-8')
            #print 'director :'+str(director)
        except:
            l = direct('a')
            if len(l)>1:
                for g in l:
                    if director and g:
                        director = director+', '+g.string.encode('utf-8')
                    elif g:
                        director = g.string.encode('utf-8')
            elif len(l)==1 and l:
                director= l[0].string.encode('utf-8')
    else: director = ' '
    writ=beautifulSoup.find(text=("сценарий").decode('utf-8')).findNext('div')
    if writ:
        try:
           writer = writ.getText().encode('utf-8')
        except:
            l = writ('a')
            if len(l)>1:
                for g in l:
                    if writer and g:
                        writer = writer+', '+g.string.encode('utf-8')
                    elif g:
                        writer = g.string.encode('utf-8')
            elif len(l)==1 and l:
                writer= l[0].string.encode('utf-8')
    else: writer = ' '
    films = beautifulSoup.findAll('tr')
    for film in films:
        gb = ''
        tt = ''
        leaches = ''
        seeds = ''
        stat = ''
        ftype = ''
        hdtype = ''
        ddd = ''
        p1 = film.findAll('td', attrs={'id':re.compile('trnt_cntnr_.*_1')})
        if p1:
            if len(films)>2:
                link = p1[0].find('img')['onclick']
                res = re.compile("'.*'")
                res.findall(str(link))
                link = res.findall(str(link))[0].replace("'", '')
                p4 = film.findAll('td', attrs={'id':re.compile('trnt_cntnr_.*_4')})
                tt = p4[0].find('span').string.encode('utf-8').strip().replace('&nbsp;', '').replace('&ndash;', '').replace('&nbsp;', '').replace('amp;', '').replace('gt;', '>').replace('&laquo;', '«').replace('&raquo;', '»')
            #print tt
            else:
                tget= beautifulSoup.find('div', attrs={'class':'tv-player'})
                m=re.search('http:(.+)"', str(tget))
                if m:
                    link= m.group(0).split('"')[0]
                else:
                    m = re.search('load.*', str(tget))
                    link = m.group(0).split('"')[1]
                p4 = film.findAll('td', attrs={'id':re.compile('trnt_cntnr_.*_4')})
                tt = p4[0].string.encode('utf-8').strip().replace('&nbsp;', '').replace('&ndash;', '').replace('&nbsp;', '').replace('amp;', '').replace('gt;', '>').replace('&laquo;', '«').replace('&raquo;', '»')
            try:
                p2 = film.findAll('td', attrs={'id':re.compile('trnt_cntnr_.*_2')})
                ftype = p2[0].findAll('span')
                for f in ftype:
                    hdtype = "[COLOR FFff7f24]"+hdtype +'('+f.getText().encode('utf-8').replace('&nbsp;&nbsp;','')+')'+"[/COLOR]"
                #print hdtype
            except:pass
            try:
                d=film.findAll('img', attrs={'title': str('Фильм в 3D').decode('utf-8')})
                if d:
                    ddd = "[COLOR FFff7f24](3D)[/COLOR]"
                    #print ddd
            except: pass
            try:
                p3 = film.findAll('td', attrs={'id':re.compile('trnt_cntnr_.*_3')})
                gb = "[COLOR FF6495ED]["+p3[0].find('strong').string.encode('utf-8')+"][/COLOR]"
                #print gb
            except: pass
            try:
                p5 = film.findAll('td', attrs={'id':re.compile('trnt_cntnr_.*_5')})
                seeds = p5[0].find('strong').string.encode('utf-8')
                #print seeds
            except: pass
            try:
                p6 = film.findAll('td', attrs={'id':re.compile('trnt_cntnr_.*_6')})
                leaches = p6[0].find('strong').string.encode('utf-8')
                #print leaches
            except: pass
        else: continue
        if seeds and leaches:
            stat= "[COLOR FF00ff7f]("+seeds+ ",[/COLOR][COLOR FFFF0000]"+leaches+")[/COLOR]"
        elif seeds:
            stat = "[COLOR FF00ff7f]("+seeds+ ")[/COLOR]"
        elif leaches:
            stat = "[COLOR COLOR FFFF0000]("+leaches+ ")[/COLOR]"
        title = (gb+hdtype+ddd+stat+tt).replace('&nbsp;', '').replace('&ndash;', '').replace('&nbsp;', '').replace('amp;', '').replace('gt;', '>').replace('&laquo;', '«').replace('&raquo;', '»')
        li = xbmcgui.ListItem(title, title, img, img)
        li.setProperty('fanart_image', img)
        #li.setProperty('IsPlayable', 'true')
        li.setInfo(type = "Video", infoLabels = {"Title": title, 'year': year, 'genre': genre, 'plot': descr, 'director': director, 'writer': writer, 'rating': rating} )
        uri = construct_request({
                'func': 'start_torr',
                'img':img.encode('utf-8'),
                'title':title,
                'title1':tt,
                'file':link,
                'year':year,
                'genre':genre,
                'descr':descr,
                'director':director,
                'writer':writer,
                'rating':rating
        })
        commands = []
        li.addContextMenuItems(commands)
        xbmcplugin.addDirectoryItem(hos, uri, li, True)
    xbmcplugin.endOfDirectory(hos)
    xbmc.executebuiltin('Container.SetViewMode(%s)' % view_mode)

def start_torr(params):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    TSplayer=TSengine()
    out=TSplayer.load_torrent(params['file'],'TORRENT')
    if out=='Ok':
        for k,v in TSplayer.files.iteritems():
            if TSplayer.files.__len__() == 1:
               p=urllib.unquote_plus(params['title1'])
            else: p=urllib.unquote_plus(k)
            li = xbmcgui.ListItem(urllib.unquote(k), urllib.unquote(k), params['img'], params['img'])
            #if __addon__.getSetting('fanart') == 'false':
            li.setProperty('fanart_image', params['img'])
            li.setInfo(type = "Video", infoLabels = {'year': params['year'], 'genre': params['genre'], 'plot': params['descr'], 'director': params['director'], 'writer': params['writer'], 'rating': params['rating']})
            #li = xbmcgui.ListItem(urllib.unquote(k))
            li.setProperty('IsPlayable', 'true')
            #li.addContextMenuItems([('Добавить в плейлист', 'XBMC.RunPlugin(%s)' % uri),])
            uri = construct_request({
                'torr_url': urllib.quote(params['file']),
                'title': k,
                'title1': p,
                'ind':v,
                'img':params['img'],
                'func': 'play_url2'
            })
            #li.addContextMenuItems([('Добавить в плейлист', 'XBMC.RunPlugin(%s?func=addplist&torr_url=%s&title=%s&ind=%s&img=%s&func=play_url2)' % (sys.argv[0],urllib.quote(torr_link),k,v,img  )),])
            xbmcplugin.addDirectoryItem(hos, uri, li)
    xbmcplugin.addSortMethod(hos, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(hos)
    xbmc.executebuiltin('Container.SetViewMode(%s)' % view_mode)
    TSplayer.end()

def play_url2(params):
    torr_link=urllib.unquote(params["torr_url"])
    img=urllib.unquote_plus(params["img"])
    title=urllib.unquote_plus(params["title"])
    TSplayer=TSengine()
    out=TSplayer.load_torrent(torr_link,'TORRENT')
    if out=='Ok':
        lnk=TSplayer.get_link(int(params['ind']),title, img, img)
        if lnk:
            item = xbmcgui.ListItem(path=lnk)
            item.setInfo(type="Video",infoLabels={"Title": params['title1']})
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
            while not xbmc.Player().isPlaying:
                xbmc.sleep(300)
            while TSplayer.player.active and not TSplayer.local: 
                TSplayer.loop()
                xbmc.sleep(300)
                if xbmc.abortRequested:
                    TSplayer.log.out("XBMC is shutting down")
                    break
            if TSplayer.local and xbmc.Player().isPlaying: 
                try: time1=TSplayer.player.getTime()
                except: time1=0
                i = xbmcgui.ListItem("***%s"%title)
                i.setProperty('StartOffset', str(time1))
                xbmc.Player().play(TSplayer.filename.decode('utf-8'),i)

        else:
            item = xbmcgui.ListItem(path='')
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), False, item) 
    TSplayer.end()
    xbmc.Player().stop
    xbmc.executebuiltin('Container.Refresh')

def GetArchive(params):
    #date = datetime.datetime.now().timetuple()
    #title = str(date.tm_mday) + '-' + str(date.tm_mon) + '-'  + str(date.tm_year)
    #http = GET('http://torrent-tv.ru/' + params['file'])#+'?data='+title)
    #if http == None:
    http = GET('http://1ttv.org/' + params['file'])
    if http == None:
        showMessage('Torrent TV', 'Сайты не отвечают')
        return
    beautifulSoup = BeautifulSoup(http)
    channels=beautifulSoup.findAll('div', attrs={'class': 'best-channels-content'})
    for ch in channels:
        link =ch.find('a')['href']
        title= ch.find('strong').string.encode('utf-8').replace('\n', '').strip()
        img='http://torrent-tv.ru/'+ch.find('img')['src']
        if __addon__.getSetting('logopack') == "true":
            logo_path = os.path.join(PLUGIN_DATA_PATH, 'logo')
            logo_src = os.path.join(logo_path, ch.find('strong').string.replace('\n', '').replace('  ', '') + '.png')
            if os.path.exists(logo_src):
                img = logo_src
        if ch_b == "true":
            if ch_i == "true": title = "[I][B][COLOR FF"+ch_color+"]" + title + "[/COLOR][/B][/I]"
            else: title = "[B][COLOR FF"+ch_color+"]" + title + "[/COLOR][/B]"
        else:
            if ch_i == "true": title = "[I][COLOR FF"+ch_color+"]" + title + "[/COLOR][/I]"
            else: title = "[COLOR FF"+ch_color+"]" + title + "[/COLOR]"
        li = xbmcgui.ListItem(title, title, img, img)
        startTime = time.localtime()
        endTime = time.localtime()
        li.setInfo(type = "Video", infoLabels = {"Title": title, 'year': endTime.tm_year})
        uri = construct_request({
                'func': 'getArchiveCalendar',
                'img':img.encode('utf-8'),
                'title':title,
                'file':link
        })
        xbmcplugin.addDirectoryItem(hos, uri, li, True)
    xbmcplugin.endOfDirectory(hos)
    
def getArchiveCalendar(params):
    res = re.compile('&data=.*')
    res.findall(params['file'])
    if res:
        date_site = res.findall(params['file'])[0].replace('&data=', '')
        #print date_site
        dt = datetime.datetime.fromtimestamp(time.mktime(time.strptime(date_site, '%d-%m-%Y')))
        #print dt
    for i in range(int(archive)):
        #date = datetime.datetime.now() - datetime.timedelta(days=i)
        date = dt - datetime.timedelta(days=i)
        date = date.timetuple()
        title = str(date.tm_mday) + '-' + str(date.tm_mon) + '-'  + str(date.tm_year)
        li = xbmcgui.ListItem(title)
        uri = construct_request({
            'func': 'getArchiveDate',
            'date': title,
            'file': params['file'],
            'img': params['img'],
        })
        xbmcplugin.addDirectoryItem(hos, uri, li, True)
    xbmcplugin.endOfDirectory(hos)
    
def getArchiveDate(params):
    date = datetime.datetime.now().timetuple()
    title = str(date.tm_mday) + '-' + str(date.tm_mon) + '-'  + str(date.tm_year)
    #http = GET('http://torrent-tv.ru/' + params['file'].replace(title,params['date']))
    #if http == None:
    http = GET('http://1ttv.org/' + params['file'].replace(title,params['date']))
    if http == None:
        showMessage('Torrent TV', 'Сайты не отвечают')
        return
    beautifulSoup = BeautifulSoup(http)
    channels=beautifulSoup.findAll('div', attrs={'class': 'best-channels'})
    search = channels[0].findAll('p')
    for ch in search:
        if not ch.find('strong'): continue
        link =str(ch.find('a')['href']).replace('\n', '').strip()
        title= str(ch.find('a').string.encode('utf-8').replace('\n', '')).strip()
        time_title = str(ch.find('strong')).replace('&ndash;', '').replace('\n', '').replace('<strong>', '').replace('</strong>', '').strip()
        img = params['img']
        if prog_b == "true":
            if prog_i == "true": title = "[I][B][COLOR FF"+prog_color+"]" + time_title + ' - ' + title + "[/COLOR][/B][/I]"
            else: title = "[B][COLOR FF"+prog_color+"]" + time_title + ' - ' + title + "[/COLOR][/B]"
        else:
            if prog_i == "true": title = "[I][COLOR FF"+prog_color+"]" + time_title + ' - ' + title + "[/COLOR][/I]"
            else: title = "[COLOR FF"+prog_color+"]" + time_title + ' - ' + title + "[/COLOR]"
        li = xbmcgui.ListItem(title, title, img, img)
        startTime = time.localtime()
        endTime = time.localtime()
        li.setProperty('IsPlayable', 'true')
        li.setInfo(type = "Video", infoLabels = {"Title": title, 'year': endTime.tm_year})
        uri = construct_request({
                'func': 'play_ch_web',
                'img':img,
                'title':title,
                'file':link
        })
        xbmcplugin.addDirectoryItem(hos, uri, li, False)
    xbmcplugin.endOfDirectory(hos)

    
def play_ch_db(params):
    showMessage(message = 'Запуск...', heading='Torrent TV', times = 2000)
    xbmc.executebuiltin('Action(Stop)')
    try:
        #page = GET('http://torrent-tv.ru/torrent-online.php?translation=' + str(params['id']), data)
        #if page == None:
        page = GET('http://1ttv.org/torrent-online.php?translation=' + str(params['id']), data)
        if page == None:
            showMessage('Torrent TV', 'Сайты не отвечают')
            return
        res = re.compile('DateTime = ".*"')
        res.findall(page)
        if res:
            DateTime = res.findall(page)[0].replace('DateTime = ', '').replace('"', '')
            php = GET('http://www.torrent-tv.ru/calendar.php?date=' + str(int(time.time()))+'453&datetime='+str(DateTime), data)
        else:
            print "ERROR getting DateTime"
    except Exception, e:
        print 'play_ch_db ERROR: %s' % e
    url = ''
    if params['file'] == '':
        cookie = ''
        if os.path.exists(cookiefile):
            fgetcook = open(cookiefile, 'r')
            cookie = fgetcook.read()
            del fgetcook
        if not cookie:
            cookie = ''
        db = DataBase(db_name, cookie)
        url = db.GetUrlsStream(params['id'])            
        if url.__len__() == 0:
            showMessage('Ошибка получения ссылки')
            return
    else:
        url = params['file']
    TSplayer=TSengine()
    out = None
    if url.find('http://') == -1:
        out = TSplayer.load_torrent(url,'PID',port=aceport)
    else:
        out = TSplayer.load_torrent(url,'TORRENT',port=aceport)
    if out == 'Ok':
        lnk=TSplayer.get_link()
        if lnk:
            item = xbmcgui.ListItem(path=lnk)
            item.setInfo(type="Video",infoLabels={"Title": params['title']})
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)  
            while not xbmc.Player().isPlaying:
                xbmc.sleep(300)
            while TSplayer.player.active and not TSplayer.local: 
                TSplayer.loop()
                xbmc.sleep(300)
                if xbmc.abortRequested:
                    TSplayer.log.out("XBMC is shutting down")
                    break

        else:
            item = xbmcgui.ListItem(path='')
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), False, item)
    TSplayer.end()
    xbmc.Player().stop
    xbmc.sleep(1)
    xbmc.executebuiltin('Container.Refresh')


def play_ch_web(params):
    showMessage(message = 'Запуск...', heading='Torrent TV', times = 2000)
    xbmc.executebuiltin('Action(Stop)') 
    #http = GET('http://torrent-tv.ru/' + params['file'])
    #if http == None:
    http = GET('http://1ttv.org/' + params['file'])
    if http == None:
        showMessage('Torrent TV', 'Сайты не отвечают')
        return
    beautifulSoup = BeautifulSoup(http)
    tget= beautifulSoup.find('div', attrs={'class':'tv-player'})
    mode = ''
    url = ''
    m=re.search('http:(.+)"', str(tget))
    if m:
        mode = 'TORRENT'
        url = m.group(0).split('"')[0]
        m=re.search('http://[0-9]+.[0-9]+.[0-9]+.[0-9]+:[0-9]+', url)
    else:
        mode = 'PID'
        m = re.search('load.*', str(tget))
        url = m.group(0).split('"')[1]
    TSplayer=TSengine()
    out = None
    out = TSplayer.load_torrent(url,mode,port=aceport)
    if out == 'Ok':
        lnk=TSplayer.get_link(0,params['title'], params['img'], params['img'])
        if lnk:
            item = xbmcgui.ListItem(path=lnk)
            item.setInfo(type="Video",infoLabels={"Title": params['title']})
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)  
            while not xbmc.Player().isPlaying:
                xbmc.sleep(300)
            while TSplayer.player.active and not TSplayer.local: 
                TSplayer.loop()
                xbmc.sleep(300)
                if xbmc.abortRequested:
                    TSplayer.log.out("XBMC is shutting down")
                    break

        else:
            item = xbmcgui.ListItem(path='')
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), False, item)
    TSplayer.end()
    xbmc.Player().stop
    xbmc.sleep(1)
    xbmc.executebuiltin('Container.Refresh')

def GetParts():
    db = DataBase(db_name, cookie)
    parts = db.GetParts(adult = adult)
    refreshuri = construct_request({
        'func': 'Refreshuri'
    })
    deldb = construct_request({
        'func': 'DelDB',
    })
    commands = []
    commands.append(('Обновить список каналов', 'XBMC.RunPlugin(%s)' % (refreshuri),))
    commands.append(('Удалить БД каналов', 'XBMC.RunPlugin(%s)' % (deldb),))
    for part in parts:
        li = xbmcgui.ListItem(part['name'])
        li.addContextMenuItems(commands)
        uri = construct_request({
            'func': 'GetChannelsDB',
            'group': part['id'],
        })
        xbmcplugin.addDirectoryItem(hos, uri, li, True)

def Refreshuri(params):
    cookie = UpdCookie()
    db = DataBase(db_name, cookie)
    showMessage('Torrent TV', 'Производится обновление плейлиста')
    db.UpdateDB()
    xbmc.executebuiltin('Container.Refresh')
    showMessage('Torrent TV', 'Обновление плейлиста завершено')

def mainScreen(params):
    refreshuri = construct_request({
        'func': 'Refreshuri'
    })
    deldb = construct_request({
        'func': 'DelDB',
    })
    commands = []
    commands.append(('Обновить список каналов', 'XBMC.RunPlugin(%s)' % (refreshuri),))
    commands.append(('Удалить БД каналов', 'XBMC.RunPlugin(%s)' % (deldb),))
    li = xbmcgui.ListItem('[COLOR FFB77D00]ИЗБРАННЫЕ[/COLOR]')
    li.addContextMenuItems(commands)
    uri = construct_request({
        'func': 'GetChannelsDB',
        'title': 'ИЗБРАННЫЕ',
        'group': 'favourite'
    })
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    li = xbmcgui.ListItem('[COLOR FF00FF00]Все каналы[/COLOR]')
    li.addContextMenuItems(commands)
    uri = construct_request({
        'func': 'GetChannelsDB',
        'title': 'Все каналы',
        'group': '0'
    })
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    li = xbmcgui.ListItem('[COLOR FF00FF00]Последние просмотренные[/COLOR]')
    li.addContextMenuItems(commands)
    uri = construct_request({
        'func': 'GetChannelsDB',
        'title': 'Последние просмотренные',
        'group': 'latest'
    })
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    li = xbmcgui.ListItem('[COLOR FF00FF00]HD Каналы[/COLOR]')
    li.addContextMenuItems(commands)
    uri = construct_request({
        'func': 'GetChannelsDB',
        'title': 'HD Каналы',
        'group': 'hd'
    })
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    li = xbmcgui.ListItem('[COLOR FF00FF00]Новые каналы[/COLOR]')
    li.addContextMenuItems(commands)
    uri = construct_request({
        'func': 'GetChannelsDB',
        'title': 'Новые каналы',
        'group': 'new'
    })
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    li = xbmcgui.ListItem('[COLOR FF0099FF]На модерации[/COLOR]')
    li.addContextMenuItems(commands)
    uri = construct_request({
        'func': 'GetChannelsWeb',
        'title': 'На модерации',
        'file': 'on_moderation.php'
    })
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    li = xbmcgui.ListItem('[COLOR FF0099FF]Трансляции[/COLOR]')
    li.addContextMenuItems(commands)
    uri = construct_request({
        'func': 'GetChannelsWeb',
        'title': 'Трансляции',
        'file': 'translations.php'
    })
    li.addContextMenuItems(commands)
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    li = xbmcgui.ListItem('[COLOR FF6495ED]Архив[/COLOR]')
    li.addContextMenuItems(commands)
    uri = construct_request({
        'func': 'GetArchive',
        'title': 'Архив',
        'file': 'tv-archive.php'
    })
    li.addContextMenuItems(commands)
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    li = xbmcgui.ListItem('[COLOR FFFFff7f24]Фильмы Online[/COLOR]')
    li.addContextMenuItems(commands)
    uri = construct_request({
        'func': 'GetFilms',
    })
    li.addContextMenuItems(commands)
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    GetParts()
    xbmcplugin.endOfDirectory(hos)
    #xbmc.executebuiltin('Container.Update(plugin://plugin.video.torrent.tv/?func=GetFilms)')
    #xbmc.executebuiltin('Container.SetViewMode(%s)' % view_mode)
        
from urllib import unquote, quote, quote_plus

def get_params(paramstring):
    param=[]
    if len(paramstring)>=2:
        params=paramstring
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=splitparams[1]
    if len(param) > 0:
        for cur in param:
            param[cur] = urllib.unquote_plus(param[cur])
    return param

def addon_main():
    import datetime
    params = get_params(sys.argv[2])
    try:
        func = params['func']
        del params['func']
    except:
        db = DataBase(db_name, cookie='')        
        dbver = db.GetDBVer()
        if db.GetDBVer() <> 6:
            del db
            os.remove(db_name)

        db = DataBase(db_name, cookie='')
        lupd = db.GetLastUpdate()
        if lupd == None:
            showMessage('Torrent TV', 'Производится обновление плейлиста')
            cookie = UpdCookie()
            db = DataBase(db_name, cookie)
            db.UpdateDB()
            if db.last_error == 0:
                showMessage('Torrent TV', 'Обновление плейлиста выполнено')
            else:
                showMessage('Torrent TV', 'Ошибка!')
        else:
            nupd = lupd + datetime.timedelta(hours = 7)

            if nupd < datetime.datetime.now():
                showMessage('Torrent TV', 'Производится обновление плейлиста')
                cookie = UpdCookie()
                db = DataBase(db_name, cookie)
                db.UpdateDB()
                if db.last_error == 0:
                    showMessage('Torrent TV', 'Обновление плейлиста выполнено')
                else:
                    showMessage('Torrent TV', 'Ошибка!')
                    
        del db
        
        func = None
        xbmc.log( '[%s]: Primary input' % addon_id, 1 )

        mainScreen(params)
        print 'mainScreen'
    if func != None:
        try:
            pfunc = globals()[func]
        except:
            pfunc = None
            xbmc.log( '[%s]: Function "%s" not found' % (addon_id, func), 4 )
            showMessage('Internal addon error', 'Function "%s" not found' % func, 2000)
        if pfunc:
            pfunc(params)
