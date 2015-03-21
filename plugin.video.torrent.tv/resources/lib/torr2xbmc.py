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
        cookie = resp.headers['Set-Cookie'].split(";")[0]
        http=resp.read()
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
    if GetCookie('http://torrent-tv.ru/auth.php', data) == None:
        if GetCookie('http://1ttv.org/auth.php', data) == None:
            return None
        else:
            cookie = GetCookie('http://1ttv.org/auth.php', data)
    else:
        cookie = GetCookie('http://torrent-tv.ru/auth.php', data)
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
"1+1": "620",
"112 Украина": "921vsetv",
"112": "921vsetv",
"100 ТВ": "382vsetv",
"2+2": "583",
"24 Док": "16",
"24 Техно": "710",
"24 Украина": "298vsetv",
"2x2": "323",
"2х2 (+2)": "809vsetv",
"365 Дней": "250",
"360 градусов": "653vsetv",
"5 канал (Украина)": "586",
"5 канал Украина": "586",
"8 канал": "217",
"9 ТВ Орбита": "782vsetv",
"ab moteurs": "127vsetv",
"Al Jazeera English": "240vsetv",
"Amedia 1": "895vsetv",
"Amedia Premium": "896vsetv",
"Amedia Premium HD": "896vsetv",
"Amazing Life": "658",
"Amedia 2": "918",
"Animal Planet": "365",
"Animal Planet HD": "990",
"ATR": "763vsetv",
"A-One": "680",
"A-ONE UA": "772vsetv",
"A-One UA": "772vsetv",
"AXN Sci-Fi": "516",
"SONY Sci-Fi": "516",
"Sony Sci-Fi": "516",
"BBC World News": "828",
"Bridge TV": "151",
"Bloomberg": "90vsetv",
"Business": "386vsetv",
"Cartoon Network": "601",
"CCTV 4": "904vsetv",
"CCTV Русский": "598vsetv",
"CBS Drama": "911",
"CBS Reality": "912",
"CNN International": "47vsetv",
"CNL": "392vsetv",
"Comedy TV": "51",
"C Music": "319",
"Da Vinci Learning": "410",
"DIVA Universal Russia": "713",
"Dobro TV": "937",
"Deutsche Welle": "84vsetv",
"Discovery Channel": "325",
"Discovery Science": "409",
"Discovery Science HD": "409",
"Discovery World": "437",
"Investigation Discovery Europe": "19",
"Investigation Discovery": "19",
"ID Xtra": "943vsetv",
"Daring TV": "696vsetv",
"Discovery HD Showcase": "111",
"Discowery HD Showcase": "111",
"Discovery Showcase HD": "111",
"Discovery Channel HD": "938vsetv",
"Disney Channel": "150",
"Disney Channel(+2)": "645vsetv",
"E Entertainment": "713",
"Е! Entertainment": "713",
"Е Entertainment": "713",
"English Club TV": "757",
"Enter Film": "281",
"EuroNews": "23",
"EuroNews UA": "23",
"Europa Plus TV": "681",
"Eurosport": "737",
"Eurosport Int. (Eng)": "737",
"Eurosport 2": "850",
"Eurosport 2 Int. (Eng)": "850",
"Eurosport 2 HD": "850",
"Eurosport HD": "560",
"Extreme Sports": "288",
"Fashion TV": "661",
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
"Galaxy TV": "924",
"GALAXY": "924",
"Gulli": "810",
"GLAS": "457vsetv",
"HD Life": "415",
"HD Спорт": "429",
"HD СПОРТ": "429",
"HD Кино": "987",
"HD Кино 2": "988",
"History Channel": "902vsetv",
"History Channel HD": "905vsetv",
"Hustler TV": "666vsetv",
"ICTV": "709",
"iConcerts TV HD": "797vsetv",
"JimJam": "494",
"Jewish News One": "796vsetv",
"JN1": "796vsetv",
"Kids co": "598",
"KidsCo": "598",
"Lale": "911vsetv",
"Life News": "1032",
"Look TV": "726vsetv",
"Luxe TV HD": "536vsetv",
"Luxury World": "946vsetv",
"Maxxi-TV": "228",
"MCM Top": "533",
"MGM": "608",
"MGM HD": "934",
"Mezzo": "575",
"Mezzo Live HD": "672vsetv",
"Motor TV": "531",
"Motors TV": "531",
"Motors Tv": "531",
"MTV Russia": "1021",
"MTV Россия": "1021",
"MTV Ukraina": "353vsetv",
"MTV Dance": "332",
"MTV Hits UK": "849",
"MTV Rocks": "388",
"MTV Music": "430",
"MTV live HD": "382",
"MTV Live HD": "382",
"Music Box UA": "417vsetv",
"Music Box": "642",
"Russian Music Box": "25",
"myZen.tv HD": "141",
"MyZen TV HD": "141",
"NBA TV": "790vsetv",
"Nat Geo Wild": "807",
"Nat Geo Wild HD": "807",
"National Geographic": "102",
"National Geographic HD": "389",
"News One": "247",
"NHK World TV": "789vsetv",
"Nick Jr.": "917",
"Nickelodeon": "567",
"Nickelodeon HD": "423",
"Ocean-TV": "55",
"O-TV": "167",
"Outdoor HD": "322",
"Outdoor Channel": "322",
"Paramount Comedy": "920",
"Paramount Channel": "935vsetv",
"Playboy TV": "663vsetv",
"Private Spice": "143vsetv",
"Brazzers TV Europe": "143vsetv",
"QTV": "280",
"Real Estate-TV": "481vsetv",
"RTVi": "76",
"RU TV": "258",
"Ru Music": "388vsetv",
"Rusong TV": "591",
"Russian Travel Guide": "648",
"Russia Today Documentary": "788vsetv",
"Russia Today": "313",
"Russia Today HD": "313",
"SHOPping-TV (Ukraine)": "810vsetv",
"SET": "311",
"SET HD": "311",
"S.E.T": "311",
"Sony Turbo": "935",
"Smile of Child": "789",
"Star TV Ukraine": "513vsetv",
"STV": "165",
"Style TV": "119",
"Style tv": "119",
"Teen TV": "448vsetv",
"TiJi": "555",
"TLC": "425",
"TLC Europe": "777vsetv",
"TLC HD": "901vsetv",
"Tonis": "627",
"Tonis HD": "627",
"TVCI": "435",
"TV Rus": "799vsetv",
"TV5 Monde": "74vsetv",
"TV 1000": "127",
"TV1000": "127",
"TV 1000 Action East": "125",
"TV 1000 Action": "125",
"TV 1000 Русское кино": "267",
"TV1000 Action East": "125",
"TV1000 Action": "125",
"TV1000 Русское кино": "267",
"TV1000 Megahit HD": "816vsetv",
"TV1000 Premium HD": "814vsetv",
"TV1000 Comedy HD": "818vsetv",
"TV 1000 Megahit HD": "816vsetv",
"TV 1000 Premium HD": "814vsetv",
"TV 1000 Comedy HD": "818vsetv",
"Travel Channel": "88vsetv",
"Travel Channel HD": "690vsetv",
"Travel+ adventure": "832vsetv",
"Travel + adventure": "832vsetv",
"Travel + adventure HD": "1035",
"TV XXI (TV21)": "309",
#"Ukrainian Fashion": "939",
"Universal Channel": "213",
"Ukrainian Fashion": "773vsetv",
"VH1": "491",
"VH1 Classic": "156",
"Viasat Explorer": "521",
"Viasat Explorer CEE": "521",
"Viasat History": "277",
"Viasat Nature East": "765",
"Viasat Sport": "455",
"Viasat Sport HD": "455",
"VIASAT Sport Baltic": "504vsetv",
"Viasat Sport Baltic": "504vsetv",
"Sport Baltic": "504vsetv",
"Viasat Nature-History HD": "716vsetv",
"Viasat Nature/History HD": "716vsetv",
"World Fashion": "346",
"XSPORT": "748vsetv",
"Xsport": "748vsetv",
"XXL": "664vsetv",
"Zee TV": "626",
"Zoom": "1009",
"Авто плюс": "153",
"Авто 24": "924vsetv",
"Агро тв": "11",
"Амедиа": "918",
"Астро ТВ": "249",
"Астро": "249",
"Беларусь 24": "851",
"Бигуди": "481vsetv",
"Боец": "454",
"Бойцовский клуб": "986",
"БТБ": "877vsetv",
"БСТ": "272vsetv",
"Вопросы и ответы": "333",
"Вместе РФ": "967vsetv",
"Время": "669",
"ВТВ": "139vsetv",
"Гамма": "479vsetv",
"Глас": "294vsetv",
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
"Драйв ТВ": "505",
"Еврокино": "352",
"ЕДА": "931",
"Еда": "931",
"Еда ТВ": "931",
"ЕДА HD": "930",
"Еда HD": "930",
"Живи": "113",
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
"Интер": "677",
"Интер+": "808",
"Интересное ТВ": "24",
"Израиль плюс": "532vsetv",
"История": "879vsetv",
"К1": "453",
"К2": "20vsetv",
"Карусель": "740",
"Кинопоказ": "22",
"Комедия ТВ": "821",
"комедия тв": "821",
"Комсомольская правда": "852",
"Кто есть кто": "769",
"Кто Есть Кто": "769",
"КРТ": "149vsetv",
"Киевская Русь": "149vsetv",
"Кухня ТВ": "614",
"Культура Украина": "285vsetv",
"КХЛ ТВ": "481",
"КХЛ HD": "481",
"Ля-минор": "257",
"Львов ТВ": "920vsetv",
"Lviv TV": "920vsetv",
"М1": "632",
"М2": "445vsetv",
"Мега": "788",
"Меню ТВ": "348vsetv",
"Мир": "726",
"Мир HD": "965vsetv",
"Мир (+3)": "529vsetv",
"Меню ТВ": "348vsetv",
"Мир 24": "838vsetv",
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
"Малятко ТВ": "606vsetv",
"Моя дитина": "761vsetv",
"Мать и дитя": "618",
"Мать и Дитя": "618",
"Мультимания": "31",
"Муз ТВ": "808vsetv",
"Мульт": "962vsetv",
"Надия": "871vsetv",
"Надiя": "871vsetv",
"Нано ТВ": "35",
"Наука 2.0": "723",
"Наше любимое кино": "477",
"НЛО ТВ": "843vsetv",
"Новый канал": "128",
"Ностальгия": "783",
"Ночной клуб": "455vsetv",
"НСТ": "518",
"НТВ": "162",
"НТВ Мир": "422",
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
"НТВ+ Наш футбол HD": "889vsetv",
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
"НТВ+ Футбол 2": "563",
"НТВ+ Футбол HD": "664",
"НТВ+ Футбол 2 HD": "563",
"НТВ+ 3D": "702vsetv",
"НТН (Украина)": "140",
"НТС Севастополь": "884vsetv",
"О2ТВ": "777",
"О2 ТВ": "777",
"Оружие": "376",
"ОСТ": "926",
"ОТР": "880vsetv",
"ОНТ Украина": "111vsetv",
"Открытый Мир": "692vsetv",
"Охота и рыбалка": "617",
"Охотник и рыболов": "132",
"Охотник и рыболов HD": "842vsetv",
"Парк развлечений": "37",
"Первый автомобильный (укр)": "507",
"Первый автомобильный (Украина)": "507",
"Первый деловой": "85",
"Первый канал": "146",
"Первый канал (+4)": "542vsetv",
"Первый канал (Европа)": "391",
"Первый канал (Украина)": "339vsetv",
"Первый канал Украина": "339vsetv",
"Первый канал (СНГ)": "391",
"Первый канал HD": "983",
"ПЕРВЫЙ HD": "983",
"Первый муниципальный (Донецк)": "670vsetv",
"Первый национальный (Украина)": "773",
"Первый образовательный": "774",
"Перец": "511",
"Пиксель ТВ": "940",
"ПлюсПлюс": "24vsetv",
"Погода ТВ": "759vsetv",
"Подмосковье": "161",
"Про все": "458",
"Pro Все": "458",
"Про Все": "458",
"Право ТВ": "861vsetv",
"Просвещение": "685",
"Психология 21": "434",
"Пятый канал": "427",
"Пятница": "1003",
"Пятница (+2)": "625vsetv",
"Рада Украина": "823vsetv",
"Радость Моя": "693vsetv",
"Радость моя": "693vsetv",
"Раз ТВ": "363",
"РАЗ ТВ": "363",
"РБК": "743",
"РЕН ТВ": "689",
"РЕН ТВ  (+7)": "572vsetv",
"РЖД": "509",
"Ретро ТВ": "6",
"Россия 1": "711",
"Россия 1 (+4)": "549vsetv",
"Россия 2": "515",
"Россия 24": "291",
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
"Сонце": "874vsetv",
"Спас": "447",
"Спас ТВ": "447",
"Спорт 1": "181",
"Спорт 1 HD": "554",
"Спорт 1 (Украина)": "270vsetv",
"Спорт 2 (Украина)": "309vsetv",
"Совершенно секретно": "275",
"Союз": "349",
"СТБ": "670",
"СТС": "79",
"СТС (+2)": "538vsetv",
"СТС Love": "952vsetv",
"Стиль и мода": "863vsetv",
"Страна": "284",
"ТБН": "576",
"Тбн": "576",
#"ТБН": "694vsetv",
"ТНВ-Планета": "781vsetv",
"ТНВ-Татарстан": "145vsetv",
"ТНВ-ТАТАРСТАН": "145vsetv",
"ТВ-Центр-Международное": "435",
"ТВ Центр Международный": "435",
"ТДК": "776",
"ТВ 3": "698",
"ТВ 3 (+3)": "845vsetv",
"ТВі": "650",
"TBi": "650",
"ТВi": "650",
"ТВЦ": "649",
"ТВ Центр": "649",
"Телеканал 100": "887vsetv",
"ТНТ": "353",
"ТНТ (+2)": "556vsetv",
"ТНТ Bravo Молдова": "737vsetv",
"тнт+4": "557vsetv",
"Тонус ТВ": "637",
"Тонус-ТВ": "637",
"Телекафе": "173",
"Телепутешествия": "794",
"Телепутешествия HD": "331",
"ТЕТ": "479",
"ТРК Украина": "326",
"ТРК Киев": "75vsetv",
"Ukraine": "326",
"ТРО Союза": "730",
"ТРО": "730",
"Успех": "547",
"Улыбка ребенка": "531vsetv",
"Усадьба": "779",
"Унiан": "740vsetv",
"УТР": "689vsetv",
"Феникс+ Кино": "686",
"Футбол": "328",
"Футбол (украина)": "666",
"Футбол+ (украина)": "753",
"Футбол 1 Украина": "666",
"Футбол 2 Украина": "753",
"Футбол 1 (Украина)": "666",
"Футбол 2 (Украина)": "753",
"Хокей": "702",
"ЧП-Инфо": "315",
"Черноморская телекомпания": "751vsetv",
"Центральный канал": "317vsetv",
"Шансон ТВ": "662",
"Ю": "898",
"Юмор ТВ": "412",
"Юмор тв": "412",
"Юмор BOX": "412",
"Юмор Box": "412",
"Эко-ТВ": "685vsetv",
"Эгоист ТВ": "431",
"1+1 (резерв)": "620",
"112 Украина (резерв)": "921vsetv",
"112 (резерв)": "921vsetv",
"100 ТВ (резерв)": "382vsetv",
"2+2 (резерв)": "583",
"24 Док (резерв)": "16",
"24 Техно (резерв)": "710",
"24 Украина (резерв)": "298vsetv",
"2x2 (резерв)": "323",
"365 Дней (резерв)": "250",
"5 канал (Украина) (резерв)": "586",
"5 канал Украина (резерв)": "586",
"8 канал (резерв)": "217",
"9 ТВ Орбита (резерв)": "782vsetv",
"ab moteurs (резерв)": "127vsetv",
"Amedia 1 (резерв)": "895vsetv",
"Amedia Premium (резерв)": "896vsetv",
"Amazing Life (резерв)": "658",
"Amedia 2 (резерв)": "918",
"Animal Planet (резерв)": "365",
"Animal Planet HD (резерв)": "990",
"ATR (резерв)": "763vsetv",
"A-One (резерв)": "680",
"A-ONE UA (резерв)": "772vsetv",
"AXN Sci-Fi (резерв)": "516",
"SONY Sci-Fi (резерв)": "516",
"Sony Sci-Fi (резерв)": "516",
"BBC World News (резерв)": "828",
"Bridge TV (резерв)": "151",
"Business (резерв)": "386vsetv",
"Cartoon Network (резерв)": "601",
"CCTV 4 (резерв)": "904vsetv",
"CCTV Русский (резерв)": "598vsetv",
"CBS Drama (резерв)": "911",
"CBS Reality (резерв)": "912",
"CNN International (резерв)": "47vsetv",
"CNL (резерв)": "392vsetv",
"Comedy TV (резерв)": "51",
"C Music (резерв)": "319",
"Da Vinci Learning (резерв)": "410",
"DIVA Universal Russia (резерв)": "713",
"Dobro TV (резерв)": "937",
"Discovery Channel (резерв)": "325",
"Discovery Science (резерв)": "409",
"Discovery World (резерв)": "437",
"Investigation Discovery Europe (резерв)": "19",
"Investigation Discovery (резерв)": "19",
"Daring TV (резерв)": "696vsetv",
"Discovery HD Showcase (резерв)": "111",
"Discowery HD Showcase (резерв)": "111",
"Discovery Showcase HD (резерв)": "111",
"Disney Channel (резерв)": "150",
"English Club TV (резерв)": "757",
"Enter Film (резерв)": "281",
"EuroNews (резерв)": "23",
"EuroNews UA (резерв)": "23",
"Europa Plus TV (резерв)": "681",
"Eurosport (резерв)": "737",
"Eurosport Int. (Eng) (резерв)": "737",
"Eurosport 2 (резерв)": "850",
"EuroSport 2 (резерв)": "850",
"Eurosport 2 Int. (Eng) (резерв)": "850",
"Eurosport 2 HD (резерв)": "850",
"Eurosport HD (резерв)": "560",
"Extreme Sports (резерв)": "288",
"Fashion TV (резерв)": "661",
"Fashion TV HD (резерв)": "121",
"Fashion HD (резерв)": "121",
"Fashion One HD (резерв)": "919",
"Fashion One (резерв)": "919",
"Fox (резерв)": "659",
"FOX HD (резерв)": "659",
"Fox HD (резерв)": "659",
"Fox Life (резерв)": "615",
"FOX life HD (резерв)": "464",
"FOX Life HD (резерв)": "464",
"Fox Life HD (резерв)": "464",
"France 24 (резерв)": "187",
"France24 (резерв)": "187",
"Galaxy TV (резерв)": "924",
"GALAXY (резерв)": "924",
"Gulli (резерв)": "810",
"GLAS (резерв)": "457vsetv",
"HD Life (резерв)": "415",
"HD Спорт (резерв)": "429",
"HD СПОРТ (резерв)": "429",
"History Channel (резерв)": "902vsetv",
"Hustler TV (резерв)": "666vsetv",
"ICTV (резерв)": "709",
"iConcerts TV HD (резерв)": "797vsetv",
"JimJam (резерв)": "494",
"Jewish News One (резерв)": "796vsetv",
"JN1 (резерв)": "796vsetv",
"Kids co (резерв)": "598",
"KidsCo (резерв)": "598",
"Lale (резерв)": "911vsetv",
"Look TV (резерв)": "726vsetv",
"Luxe TV HD (резерв)": "536vsetv",
"Maxxi-TV (резерв)": "228",
"MCM Top (резерв)": "533",
"MGM (резерв)": "608",
"MGM HD (резерв)": "934",
"Mezzo (резерв)": "575",
"Motor TV (резерв)": "531",
"Motors TV (резерв)": "531",
"Motors Tv (резерв)": "531",
"MTV Russia (резерв)": "1021",
"MTV Россия (резерв)": "1021",
"MTV Ukraina (резерв)": "353vsetv",
"MTV Dance (резерв)": "332",
"MTV Hits UK (резерв)": "849",
"MTV Rocks (резерв)": "388",
"MTV Music (резерв)": "430",
"MTV live HD (резерв)": "382",
"MTV Live HD (резерв)": "382",
"Music Box UA (резерв)": "417vsetv",
"Music Box (резерв)": "642",
"Russian Music Box (резерв)": "25",
"myZen.tv HD (резерв)": "141",
"MyZen TV HD (резерв)": "141",
"NBA TV (резерв)": "790vsetv",
"Nat Geo Wild (резерв)": "807",
"Nat Geo Wild HD (резерв)": "807",
"National Geographic (резерв)": "102",
"National Geographic HD (резерв)": "389",
"News One (резерв)": "247",
"Nick Jr. (резерв)": "917",
"Nickelodeon (резерв)": "567",
"Nickelodeon HD (резерв)": "423",
"Ocean-TV (резерв)": "55",
"O-TV (резерв)": "167",
"Outdoor HD (резерв)": "322",
"Outdoor Channel (резерв)": "322",
"Paramount Comedy (резерв)": "920",
"Playboy TV (резерв)": "663vsetv",
"Private Spice (резерв)": "143vsetv",
"Brazzers TV Europe (резерв)": "143vsetv",
"QTV (резерв)": "280",
"Real Estate-TV (резерв)": "481vsetv",
"RTVi (резерв)": "76",
"RU TV (резерв)": "258",
"Ru Music (резерв)": "388vsetv",
"Rusong TV (резерв)": "591",
"Russian Travel Guide (резерв)": "648",
"Russia Today Documentary (резерв)": "788vsetv",
"Russia Today Documentary HD (резерв)": "788vsetv",
"SHOPping-TV (Ukraine) (резерв)": "810vsetv",
"SET (резерв)": "311",
"SET HD (резерв)": "311",
"S.E.T (резерв)": "311",
"Sony Turbo (резерв)": "935",
"Smile of Child (резерв)": "789",
"Star TV Ukraine (резерв)": "513vsetv",
"STV (резерв)": "165",
"Style TV (резерв)": "119",
"Style tv (резерв)": "119",
"Teen TV (резерв)": "448vsetv",
"TiJi (резерв)": "555",
"TLC (резерв)": "425",
"TLC Europe (резерв)": "777vsetv",
"Tonis (резерв)": "627",
"Tonis HD (резерв)": "627",
"TVCI (резерв)": "435",
"TV Rus (резерв)": "799vsetv",
"TV 1000 (резерв)": "127",
"TV1000 (резерв)": "127",
"TV 1000 Action East (резерв)": "125",
"TV 1000 Action (резерв)": "125",
"TV 1000 Русское кино (резерв)": "267",
"TV1000 Action East (резерв)": "125",
"TV1000 Action (резерв)": "125",
"TV1000 Русское кино (резерв)": "267",
"TV1000 Megahit HD (резерв)": "816vsetv",
"TV1000 Premium HD (резерв)": "814vsetv",
"TV1000 Comedy HD (резерв)": "818vsetv",
"TV 1000 Megahit HD (резерв)": "816vsetv",
"TV 1000 Premium HD (резерв)": "814vsetv",
"TV 1000 Comedy HD (резерв)": "818vsetv",
"Travel Channel (резерв)": "88vsetv",
"Travel Channel HD (резерв)": "690vsetv",
"Travel+ adventure (резерв)": "832vsetv",
"TV XXI (TV21) (резерв)": "309",
#"Ukrainian Fashion (резерв)": "939",
"Universal Channel (резерв)": "213",
"Ukrainian Fashion (резерв)": "773vsetv",
"VH1 (резерв)": "491",
"VH1 Classic (резерв)": "156",
"Viasat Explorer (резерв)": "521",
"Viasat Explorer CEE (резерв)": "521",
"Viasat History (резерв)": "277",
"Viasat Nature East (резерв)": "765",
"Viasat Sport (резерв)": "455",
"Viasat Sport HD (резерв)": "455",
"VIASAT Sport Baltic (резерв)": "504vsetv",
"Viasat Sport Baltic (резерв)": "504vsetv",
"Sport Baltic (резерв)": "504vsetv",
"Viasat Nature-History HD (резерв)": "716vsetv",
"Viasat Nature/History HD (резерв)": "716vsetv",
"World Fashion (резерв)": "346",
"XSPORT (резерв)": "748vsetv",
"Xsport (резерв)": "748vsetv",
"XXL (резерв)": "664vsetv",
"Zee TV (резерв)": "626",
"Zoom (резерв)": "1009",
"Авто плюс (резерв)": "153",
"Агро тв (резерв)": "11",
"Амедиа (резерв)": "918",
"Астро ТВ (резерв)": "249",
"Астро (резерв)": "249",
"Беларусь 24 (резерв)": "851",
"Бигуди (резерв)": "481vsetv",
"Боец (резерв)": "454",
"Бойцовский клуб (резерв)": "986",
"БТБ (резерв)": "877vsetv",
"БСТ (резерв)": "272vsetv",
"Вопросы и ответы (резерв)": "333",
"Время (резерв)": "669",
"ВТВ (резерв)": "139vsetv",
"Гамма (резерв)": "479vsetv",
"Глас (резерв)": "294vsetv",
"Гумор ТБ (резерв)": "505vsetv",
"Детский (резерв)": "66",
"Детский мир (резерв)": "747",
"Дождь (резерв)": "384",
"Дождь HD (резерв)": "384",
"Дом кино (резерв)": "834",
"Домашние животные (резерв)": "520",
"Домашние Животные (резерв)": "520",
"Домашний (резерв)": "304",
"Домашний магазин (резерв)": "695vsetv",
"Драйв ТВ (резерв)": "505",
"Еврокино (резерв)": "352",
"ЕДА (резерв)": "931",
"Еда (резерв)": "931",
"Еда ТВ (резерв)": "931",
"ЕДА HD (резерв)": "930",
"Живи (резерв)": "113",
"Звезда (резерв)": "405",
"Закон ТВ (резерв)": "178",
"Закон тв (резерв)": "178",
"Закон-тв (резерв)": "178",
"Закон ТВ (резерв)": "178",
"Загородный (резерв)": "705",
"Загородная жизнь (резерв)": "21",
"Знание (резерв)": "201",
"Здоровое ТВ (резерв)": "595",
"Зоо ТВ (резерв)": "273",
"Зоопарк (резерв)": "367",
"Иллюзион+ (резерв)": "123",
"Искушение (резерв)": "754vsetv",
"Индия (резерв)": "798",
"Интер (резерв)": "677",
"Интер+ (резерв)": "808",
"Интересное ТВ (резерв)": "24",
"Израиль плюс (резерв)": "532vsetv",
"История (резерв)": "879vsetv",
"К1 (резерв)": "453",
"К2 (резерв)": "20vsetv",
"Карусель (резерв)": "740",
"Кинопоказ (резерв)": "22",
"Комедия ТВ (резерв)": "821",
"Комсомольская правда (резерв)": "852",
"Кто есть кто (резерв)": "769",
"Кто Есть Кто (резерв)": "769",
"КРТ (резерв)": "149vsetv",
"Киевская Русь (резерв)": "149vsetv",
"Кухня ТВ (резерв)": "614",
"Культура Украина (резерв)": "285vsetv",
"КХЛ ТВ (резерв)": "481",
"КХЛ HD (резерв)": "481",
"Ля-минор (резерв)": "257",
"Львов ТВ (резерв)": "920vsetv",
"М1 (резерв)": "632",
"М2 (резерв)": "445vsetv",
"Мега (резерв)": "788",
"Меню ТВ (резерв)": "348vsetv",
"Мир (резерв)": "726",
"Мир сериала (резерв)": "145",
"Мир Сериала (резерв)": "145",
"Много ТВ (резерв)": "799",
"Моя планета (резерв)": "675",
"Москва 24 (резерв)": "334",
"Москва Доверие (резерв)": "655",
"Москва доверие (резерв)": "655",
"Музыка Первого (резерв)": "715",
"Мужской (резерв)": "82",
"Малятко ТВ (резерв)": "606vsetv",
"Моя дитина (резерв)": "761vsetv",
"Мать и дитя (резерв)": "618",
"Мать и Дитя (резерв)": "618",
"Мультимания (резерв)": "31",
"Муз ТВ (резерв)": "808vsetv",
"Надия (резерв)": "871vsetv",
"Надiя (резерв)": "871vsetv",
"Нано ТВ (резерв)": "35",
"Наука 2.0 (резерв)": "723",
"Наше любимое кино (резерв)": "477",
"НЛО ТВ (резерв)": "843vsetv",
"Новый канал (резерв)": "128",
"Ностальгия (резерв)": "783",
"Ночной клуб (резерв)": "455vsetv",
"НСТ (резерв)": "518",
"НТВ (резерв)": "162",
"НТВ Мир (резерв)": "422",
"НТВ+ Кино плюс (резерв)": "644",
"НТВ+ Киноклуб (резерв)": "462",
"НТВ+ Кинолюкс (резерв)": "8",
"НТВ+ Киносоюз (резерв)": "71",
"НТВ+ Кино Cоюз (резерв)": "71",
"НТВ+ Кинохит (резерв)": "542",
"НТВ+ Наше кино (резерв)": "12",
"НТВ+ Наше новое кино (резерв)": "485",
"НТВ+ Премьера (резерв)": "566",
"НТВ+ Баскетбол (резерв)": "697",
"НТВ+ Наш футбол (резерв)": "499",
"НТВ+ Наш футбол HD (резерв)": "889vsetv",
"НТВ+ Спорт (резерв)": "134",
"НТВ+СПОРТ (резерв)": "134",
"НТВ+ Спорт Онлайн (резерв)": "183",
"НТВ+ Спорт онлайн (резерв)": "183",
"НТВ+ Спорт Союз (резерв)": "306",
"НТВ+ Спорт плюс (резерв)": "377",
"НТВ+ СпортХит (резерв)": "910vsetv",
"НТВ+ Спорт Хит (резерв)": "910vsetv",
"НТВ+ Спортхит (резерв)": "910vsetv",
"НТВ+ Теннис (резерв)": "358",
"НТВ+ Футбол (резерв)": "664",
"НТВ+ Футбол 2 (резерв)": "563",
"НТВ+ Футбол HD (резерв)": "664",
"НТВ+ Футбол 2 HD (резерв)": "563",
"НТН (Украина) (резерв)": "140",
"НТС Севастополь (резерв)": "884vsetv",
"О2ТВ (резерв)": "777",
"О2 ТВ (резерв)": "777",
"Оружие (резерв)": "376",
"ОСТ (резерв)": "926",
"ОТР (резерв)": "880vsetv",
"ОНТ Украина (резерв)": "111vsetv",
"Открытый Мир (резерв)": "692vsetv",
"Охота и рыбалка (резерв)": "617",
"Охотник и рыболов (резерв)": "132",
"Охотник и рыболов HD (резерв)": "842vsetv",
"Парк развлечений (резерв)": "37",
"Первый автомобильный (укр) (резерв)": "507",
"Первый деловой (резерв)": "85",
"Первый канал (резерв)": "146",
"Первый канал (Европа) (резерв)": "391",
"Первый канал (Украина) (резерв)": "339vsetv",
"Первый канал (СНГ) (резерв)": "391",
"Первый канал HD (резерв)": "983",
"ПЕРВЫЙ HD (резерв)": "983",
"Первый муниципальный (Донецк) (резерв)": "670vsetv",
"Первый национальный (Украина) (резерв)": "773",
"Первый образовательный (резерв)": "774",
"Перец (резерв)": "511",
"Пиксель ТВ (резерв)": "940",
"ПлюсПлюс (резерв)": "24vsetv",
"Погода ТВ (резерв)": "759vsetv",
"Подмосковье (резерв)": "161",
"Про все (резерв)": "458",
"Pro Все (резерв)": "458",
"Про Все (резерв)": "458",
"Право ТВ (резерв)": "861vsetv",
"Просвещение (резерв)": "685",
"Психология 21 (резерв)": "434",
"Пятый канал (резерв)": "427",
"Пятница (резерв)": "1003",
"Рада Украина (резерв)": "823vsetv",
"Раз ТВ (резерв)": "363",
"РАЗ ТВ (резерв)": "363",
"РБК (резерв)": "743",
"РЕН ТВ (резерв)": "689",
"РЕН ТВ (+7) (резерв)": "572vsetv",
"РЖД (резерв)": "509",
"Ретро ТВ (резерв)": "6",
"Россия 1 (резерв)": "711",
"Россия 2 (резерв)": "515",
"Россия 24 (резерв)": "291",
"Россия К (резерв)": "187",
"РОССИЯ HD (резерв)": "984",
"Россия HD (резерв)": "984",
"РТР-Планета (резерв)": "143",
"РТР Планета (резерв)": "143",
"Русский Бестселлер (резерв)": "994",
"Русский иллюзион (резерв)": "53",
"Русский роман (резерв)": "401",
"Русский экстрим (резерв)": "406",
"Русская ночь (резерв)": "296vsetv",
"Сарафан ТВ (резерв)": "663",
"Сарафан (резерв)": "663",
"Сонце (резерв)": "874vsetv",
"Спас (резерв)": "447",
"Спас ТВ (резерв)": "447",
"Спорт 1 (резерв)": "181",
"Спорт 1 HD (резерв)": "554",
"Спорт 1 (Украина) (резерв)": "270vsetv",
"Спорт 2 (Украина) (резерв)": "309vsetv",
"Совершенно секретно (резерв)": "275",
"Союз (резерв)": "349",
"СТБ (резерв)": "670",
"СТС (резерв)": "79",
"Страна (резерв)": "284",
"ТБН (резерв)": "576",
"Тбн (резерв)": "576",
#"ТБН (резерв)": "694vsetv",
"ТНВ-Татарстан (резерв)": "145vsetv",
"ТНВ-ТАТАРСТАН (резерв)": "145vsetv",
"ТВ-Центр-Международное (резерв)": "435",
"ТВ Центр Международный (резерв)": "435",
"ТДК (резерв)": "776",
"ТВ 3 (резерв)": "698",
"ТВ 3 (+3) (резерв)": "845vsetv",
"ТВі (резерв)": "650",
"TBi (резерв)": "650",
"ТВi (резерв)": "650",
"ТВЦ (резерв)": "649",
"ТВ Центр (резерв)": "649",
"Телеканал 100 (резерв)": "887vsetv",
"ТНТ (резерв)": "353",
"ТНТ Bravo Молдова (резерв)": "737vsetv",
"тнт+4 (резерв)": "557vsetv",
"Тонус ТВ (резерв)": "637",
"Тонус-ТВ (резерв)": "637",
"Телекафе (резерв)": "173",
"Телепутешествия (резерв)": "794",
"Телепутешествия HD (резерв)": "331",
"ТЕТ (резерв)": "479",
"ТРК Украина (резерв)": "326",
"ТРК Киев (резерв)": "75vsetv",
"Ukraine (резерв)": "326",
"ТРО Союза (резерв)": "730",
"ТРО (резерв)": "730",
"Успех (резерв)": "547",
"Усадьба (резерв)": "779",
"Унiан (резерв)": "740vsetv",
"УТР (резерв)": "689vsetv",
"Феникс+ Кино (резерв)": "686",
"Футбол (резерв)": "328",
"Футбол (украина) (резерв)": "666",
"Футбол+ (украина) (резерв)": "753",
"Футбол 1 Украина (резерв)": "666",
"Футбол 2 Украина (резерв)": "753",
"Хокей (резерв)": "702",
"ЧП-Инфо (резерв)": "315",
"Шансон ТВ (резерв)": "662",
"Ю (резерв)": "898",
"Юмор ТВ (резерв)": "412",
"Юмор тв (резерв)": "412",
"Юмор BOX (резерв)": "412",
"Эко-ТВ (резерв)": "685vsetv",
"Эгоист ТВ (резерв)": "431",
"1+1(резерв)": "620",
"112 Украина(резерв)": "921vsetv",
"112(резерв)": "921vsetv",
"100 ТВ(резерв)": "382vsetv",
"2+2(резерв)": "583",
"24 Док(резерв)": "16",
"24 Техно(резерв)": "710",
"24 Украина(резерв)": "298vsetv",
"2x2(резерв)": "323",
"365 Дней(резерв)": "250",
"5 канал (Украина)(резерв)": "586",
"5 канал Украина(резерв)": "586",
"8 канал(резерв)": "217",
"9 ТВ Орбита(резерв)": "782vsetv",
"ab moteurs(резерв)": "127vsetv",
"Amedia 1(резерв)": "895vsetv",
"Amedia Premium(резерв)": "896vsetv",
"Amazing Life(резерв)": "658",
"Amedia 2(резерв)": "918",
"Animal Planet(резерв)": "365",
"Animal Planet HD(резерв)": "990",
"ATR(резерв)": "763vsetv",
"A-One(резерв)": "680",
"A-ONE UA(резерв)": "772vsetv",
"AXN Sci-Fi(резерв)": "516",
"SONY Sci-Fi(резерв)": "516",
"Sony Sci-Fi(резерв)": "516",
"BBC World News(резерв)": "828",
"Bridge TV(резерв)": "151",
"Business(резерв)": "386vsetv",
"Cartoon Network(резерв)": "601",
"CCTV 4(резерв)": "904vsetv",
"CCTV Русский(резерв)": "598vsetv",
"CBS Drama(резерв)": "911",
"CBS Reality(резерв)": "912",
"CNN International(резерв)": "47vsetv",
"CNL(резерв)": "392vsetv",
"Comedy TV(резерв)": "51",
"C Music(резерв)": "319",
"Da Vinci Learning(резерв)": "410",
"DIVA Universal Russia(резерв)": "713",
"Dobro TV(резерв)": "937",
"Discovery Channel(резерв)": "325",
"Discovery Science(резерв)": "409",
"Discovery World(резерв)": "437",
"Investigation Discovery Europe(резерв)": "19",
"Investigation Discovery(резерв)": "19",
"Daring TV(резерв)": "696vsetv",
"Discovery HD Showcase(резерв)": "111",
"Discowery HD Showcase(резерв)": "111",
"Discovery Showcase HD(резерв)": "111",
"Disney Channel(резерв)": "150",
"English Club TV(резерв)": "757",
"Enter Film(резерв)": "281",
"EuroNews(резерв)": "23",
"EuroNews UA(резерв)": "23",
"Europa Plus TV(резерв)": "681",
"Eurosport(резерв)": "737",
"Eurosport Int. (Eng)(резерв)": "737",
"Eurosport 2(резерв)": "850",
"EuroSport 2(резерв)": "850",
"Eurosport 2 Int. (Eng)(резерв)": "850",
"Eurosport 2 HD(резерв)": "850",
"Eurosport HD(резерв)": "560",
"Extreme Sports(резерв)": "288",
"Fashion TV(резерв)": "661",
"Fashion TV HD(резерв)": "121",
"Fashion HD(резерв)": "121",
"Fashion One HD(резерв)": "919",
"Fashion One(резерв)": "919",
"Fox(резерв)": "659",
"FOX HD(резерв)": "659",
"Fox HD(резерв)": "659",
"Fox Life(резерв)": "615",
"FOX life HD(резерв)": "464",
"FOX Life HD(резерв)": "464",
"Fox Life HD(резерв)": "464",
"France 24(резерв)": "187",
"France24(резерв)": "187",
"Galaxy TV(резерв)": "924",
"GALAXY(резерв)": "924",
"Gulli(резерв)": "810",
"GLAS(резерв)": "457vsetv",
"HD Life(резерв)": "415",
"HD Спорт(резерв)": "429",
"HD СПОРТ(резерв)": "429",
"History Channel(резерв)": "902vsetv",
"Hustler TV(резерв)": "666vsetv",
"ICTV(резерв)": "709",
"iConcerts TV HD(резерв)": "797vsetv",
"JimJam(резерв)": "494",
"Jewish News One(резерв)": "796vsetv",
"JN1(резерв)": "796vsetv",
"Kids co(резерв)": "598",
"KidsCo(резерв)": "598",
"Lale(резерв)": "911vsetv",
"Look TV(резерв)": "726vsetv",
"Luxe TV HD(резерв)": "536vsetv",
"Maxxi-TV(резерв)": "228",
"MCM Top(резерв)": "533",
"MGM(резерв)": "608",
"MGM HD(резерв)": "934",
"Mezzo(резерв)": "575",
"Motor TV(резерв)": "531",
"Motors TV(резерв)": "531",
"Motors Tv(резерв)": "531",
"MTV Russia(резерв)": "1021",
"MTV Россия(резерв)": "1021",
"MTV Ukraina(резерв)": "353vsetv",
"MTV Dance(резерв)": "332",
"MTV Hits UK(резерв)": "849",
"MTV Rocks(резерв)": "388",
"MTV Music(резерв)": "430",
"MTV live HD(резерв)": "382",
"MTV Live HD(резерв)": "382",
"Music Box UA(резерв)": "417vsetv",
"Music Box(резерв)": "642",
"Russian Music Box(резерв)": "25",
"myZen.tv HD(резерв)": "141",
"MyZen TV HD(резерв)": "141",
"NBA TV(резерв)": "790vsetv",
"Nat Geo Wild(резерв)": "807",
"Nat Geo Wild HD(резерв)": "807",
"National Geographic(резерв)": "102",
"National Geographic HD(резерв)": "389",
"News One(резерв)": "247",
"Nick Jr.(резерв)": "917",
"Nickelodeon(резерв)": "567",
"Nickelodeon HD(резерв)": "423",
"Ocean-TV(резерв)": "55",
"O-TV(резерв)": "167",
"Outdoor HD(резерв)": "322",
"Outdoor Channel(резерв)": "322",
"Paramount Comedy(резерв)": "920",
"Playboy TV(резерв)": "663vsetv",
"Private Spice(резерв)": "143vsetv",
"Brazzers TV Europe(резерв)": "143vsetv",
"QTV(резерв)": "280",
"Real Estate-TV(резерв)": "481vsetv",
"RTVi(резерв)": "76",
"RU TV(резерв)": "258",
"Ru Music(резерв)": "388vsetv",
"Rusong TV(резерв)": "591",
"Russian Travel Guide(резерв)": "648",
"Russia Today Documentary(резерв)": "788vsetv",
"Russia Today Documentary HD(резерв)": "788vsetv",
"SHOPping-TV (Ukraine)(резерв)": "810vsetv",
"SET(резерв)": "311",
"SET HD(резерв)": "311",
"S.E.T(резерв)": "311",
"Sony Turbo(резерв)": "935",
"Smile of Child(резерв)": "789",
"Star TV Ukraine(резерв)": "513vsetv",
"STV(резерв)": "165",
"Style TV(резерв)": "119",
"Style tv(резерв)": "119",
"Teen TV(резерв)": "448vsetv",
"TiJi(резерв)": "555",
"TLC(резерв)": "425",
"TLC Europe(резерв)": "777vsetv",
"Tonis(резерв)": "627",
"Tonis HD(резерв)": "627",
"TVCI(резерв)": "435",
"TV Rus(резерв)": "799vsetv",
"TV 1000(резерв)": "127",
"TV1000(резерв)": "127",
"TV 1000 Action East(резерв)": "125",
"TV 1000 Action(резерв)": "125",
"TV 1000 Русское кино(резерв)": "267",
"TV1000 Action East(резерв)": "125",
"TV1000 Action(резерв)": "125",
"TV1000 Русское кино(резерв)": "267",
"TV1000 Megahit HD(резерв)": "816vsetv",
"TV1000 Premium HD(резерв)": "814vsetv",
"TV1000 Comedy HD(резерв)": "818vsetv",
"TV 1000 Megahit HD(резерв)": "816vsetv",
"TV 1000 Premium HD(резерв)": "814vsetv",
"TV 1000 Comedy HD(резерв)": "818vsetv",
"Travel Channel(резерв)": "88vsetv",
"Travel Channel HD(резерв)": "690vsetv",
"Travel+ adventure(резерв)": "832vsetv",
"TV XXI (TV21)(резерв)": "309",
#"Ukrainian Fashion(резерв)": "939",
"Universal Channel(резерв)": "213",
"Ukrainian Fashion(резерв)": "773vsetv",
"VH1(резерв)": "491",
"VH1 Classic(резерв)": "156",
"Viasat Explorer(резерв)": "521",
"Viasat Explorer CEE(резерв)": "521",
"Viasat History(резерв)": "277",
"Viasat Nature East(резерв)": "765",
"Viasat Sport(резерв)": "455",
"Viasat Sport HD(резерв)": "455",
"VIASAT Sport Baltic(резерв)": "504vsetv",
"Viasat Sport Baltic(резерв)": "504vsetv",
"Sport Baltic(резерв)": "504vsetv",
"Viasat Nature-History HD(резерв)": "716vsetv",
"Viasat Nature/History HD(резерв)": "716vsetv",
"World Fashion(резерв)": "346",
"XSPORT(резерв)": "748vsetv",
"Xsport(резерв)": "748vsetv",
"XXL(резерв)": "664vsetv",
"Zee TV(резерв)": "626",
"Zoom(резерв)": "1009",
"Авто плюс(резерв)": "153",
"Агро тв(резерв)": "11",
"Амедиа(резерв)": "918",
"Астро ТВ(резерв)": "249",
"Астро(резерв)": "249",
"Беларусь 24(резерв)": "851",
"Бигуди(резерв)": "481vsetv",
"Боец(резерв)": "454",
"Бойцовский клуб(резерв)": "986",
"БТБ(резерв)": "877vsetv",
"БСТ(резерв)": "272vsetv",
"Вопросы и ответы(резерв)": "333",
"Время(резерв)": "669",
"ВТВ(резерв)": "139vsetv",
"Гамма(резерв)": "479vsetv",
"Глас(резерв)": "294vsetv",
"Гумор ТБ(резерв)": "505vsetv",
"Детский(резерв)": "66",
"Детский мир(резерв)": "747",
"Дождь(резерв)": "384",
"Дождь HD(резерв)": "384",
"Дом кино(резерв)": "834",
"Домашние животные(резерв)": "520",
"Домашние Животные(резерв)": "520",
"Домашний(резерв)": "304",
"Домашний магазин(резерв)": "695vsetv",
"Драйв ТВ(резерв)": "505",
"Еврокино(резерв)": "352",
"ЕДА(резерв)": "931",
"Еда(резерв)": "931",
"Еда ТВ(резерв)": "931",
"ЕДА HD(резерв)": "930",
"Живи(резерв)": "113",
"Звезда(резерв)": "405",
"Закон ТВ(резерв)": "178",
"Закон тв(резерв)": "178",
"Закон-тв(резерв)": "178",
"Закон ТВ(резерв)": "178",
"Загородный(резерв)": "705",
"Загородная жизнь(резерв)": "21",
"Знание(резерв)": "201",
"Здоровое ТВ(резерв)": "595",
"Зоо ТВ(резерв)": "273",
"Зоопарк(резерв)": "367",
"Иллюзион+(резерв)": "123",
"Искушение(резерв)": "754vsetv",
"Индия(резерв)": "798",
"Интер(резерв)": "677",
"Интер+(резерв)": "808",
"Интересное ТВ(резерв)": "24",
"Израиль плюс(резерв)": "532vsetv",
"История(резерв)": "879vsetv",
"К1(резерв)": "453",
"К2(резерв)": "20vsetv",
"Карусель(резерв)": "740",
"Кинопоказ(резерв)": "22",
"Комедия ТВ(резерв)": "821",
"Комсомольская правда(резерв)": "852",
"Кто есть кто(резерв)": "769",
"Кто Есть Кто(резерв)": "769",
"КРТ(резерв)": "149vsetv",
"Киевская Русь(резерв)": "149vsetv",
"Кухня ТВ(резерв)": "614",
"Культура Украина(резерв)": "285vsetv",
"КХЛ ТВ(резерв)": "481",
"КХЛ HD(резерв)": "481",
"Ля-минор(резерв)": "257",
"Львов ТВ(резерв)": "920vsetv",
"М1(резерв)": "632",
"М2(резерв)": "445vsetv",
"Мега(резерв)": "788",
"Меню ТВ(резерв)": "348vsetv",
"Мир(резерв)": "726",
"Мир сериала(резерв)": "145",
"Мир Сериала(резерв)": "145",
"Много ТВ(резерв)": "799",
"Моя планета(резерв)": "675",
"Москва 24(резерв)": "334",
"Москва Доверие(резерв)": "655",
"Москва доверие(резерв)": "655",
"Музыка Первого(резерв)": "715",
"Мужской(резерв)": "82",
"Малятко ТВ(резерв)": "606vsetv",
"Моя дитина(резерв)": "761vsetv",
"Мать и дитя(резерв)": "618",
"Мать и Дитя(резерв)": "618",
"Мультимания(резерв)": "31",
"Муз ТВ(резерв)": "808vsetv",
"Надия(резерв)": "871vsetv",
"Надiя(резерв)": "871vsetv",
"Нано ТВ(резерв)": "35",
"Наука 2.0(резерв)": "723",
"Наше любимое кино(резерв)": "477",
"НЛО ТВ(резерв)": "843vsetv",
"Новый канал(резерв)": "128",
"Ностальгия(резерв)": "783",
"Ночной клуб(резерв)": "455vsetv",
"НСТ(резерв)": "518",
"НТВ(резерв)": "162",
"НТВ Мир(резерв)": "422",
"НТВ+ Кино плюс(резерв)": "644",
"НТВ+ Киноклуб(резерв)": "462",
"НТВ+ Кинолюкс(резерв)": "8",
"НТВ+ Киносоюз(резерв)": "71",
"НТВ+ Кино Cоюз(резерв)": "71",
"НТВ+ Кинохит(резерв)": "542",
"НТВ+ Наше кино(резерв)": "12",
"НТВ+ Наше новое кино(резерв)": "485",
"НТВ+ Премьера(резерв)": "566",
"НТВ+ Баскетбол(резерв)": "697",
"НТВ+ Наш футбол(резерв)": "499",
"НТВ+ Наш футбол HD(резерв)": "889vsetv",
"НТВ+ Спорт(резерв)": "134",
"НТВ+СПОРТ(резерв)": "134",
"НТВ+ Спорт Онлайн(резерв)": "183",
"НТВ+ Спорт онлайн(резерв)": "183",
"НТВ+ Спорт Союз(резерв)": "306",
"НТВ+ Спорт плюс(резерв)": "377",
"НТВ+ СпортХит(резерв)": "910vsetv",
"НТВ+ Спорт Хит(резерв)": "910vsetv",
"НТВ+ Спортхит(резерв)": "910vsetv",
"НТВ+ Теннис(резерв)": "358",
"НТВ+ Футбол(резерв)": "664",
"НТВ+ Футбол 2(резерв)": "563",
"НТВ+ Футбол HD(резерв)": "664",
"НТВ+ Футбол 2 HD(резерв)": "563",
"НТН (Украина)(резерв)": "140",
"НТС Севастополь(резерв)": "884vsetv",
"О2ТВ(резерв)": "777",
"О2 ТВ(резерв)": "777",
"Оружие(резерв)": "376",
"ОСТ(резерв)": "926",
"ОТР(резерв)": "880vsetv",
"ОНТ Украина(резерв)": "111vsetv",
"Открытый Мир(резерв)": "692vsetv",
"Охота и рыбалка(резерв)": "617",
"Охотник и рыболов(резерв)": "132",
"Охотник и рыболов HD(резерв)": "842vsetv",
"Парк развлечений(резерв)": "37",
"Первый автомобильный (укр)(резерв)": "507",
"Первый деловой(резерв)": "85",
"Первый канал(резерв)": "146",
"Первый канал (Европа)(резерв)": "391",
"Первый канал (Украина)(резерв)": "339vsetv",
"Первый канал (СНГ)(резерв)": "391",
"Первый канал HD(резерв)": "983",
"ПЕРВЫЙ HD(резерв)": "983",
"Первый муниципальный (Донецк)(резерв)": "670vsetv",
"Первый национальный (Украина)(резерв)": "773",
"Первый образовательный(резерв)": "774",
"Перец(резерв)": "511",
"Пиксель ТВ(резерв)": "940",
"ПлюсПлюс(резерв)": "24vsetv",
"Погода ТВ(резерв)": "759vsetv",
"Подмосковье(резерв)": "161",
"Про все(резерв)": "458",
"Pro Все(резерв)": "458",
"Про Все(резерв)": "458",
"Право ТВ(резерв)": "861vsetv",
"Просвещение(резерв)": "685",
"Психология 21(резерв)": "434",
"Пятый канал(резерв)": "427",
"Пятница(резерв)": "1003",
"Рада Украина(резерв)": "823vsetv",
"Раз ТВ(резерв)": "363",
"РАЗ ТВ(резерв)": "363",
"РБК(резерв)": "743",
"РЕН ТВ(резерв)": "689",
"РЕН ТВ (+7)(резерв)": "572vsetv",
"РЖД(резерв)": "509",
"Ретро ТВ(резерв)": "6",
"Россия 1(резерв)": "711",
"Россия 2(резерв)": "515",
"Россия 24(резерв)": "291",
"Россия К(резерв)": "187",
"РОССИЯ HD(резерв)": "984",
"Россия HD(резерв)": "984",
"РТР-Планета(резерв)": "143",
"РТР Планета(резерв)": "143",
"Русский Бестселлер(резерв)": "994",
"Русский иллюзион(резерв)": "53",
"Русский роман(резерв)": "401",
"Русский экстрим(резерв)": "406",
"Русская ночь(резерв)": "296vsetv",
"Сарафан ТВ(резерв)": "663",
"Сарафан(резерв)": "663",
"Сонце(резерв)": "874vsetv",
"Спас(резерв)": "447",
"Спас ТВ(резерв)": "447",
"Спорт 1(резерв)": "181",
"Спорт 1 HD(резерв)": "554",
"Спорт 1 (Украина)(резерв)": "270vsetv",
"Спорт 2 (Украина)(резерв)": "309vsetv",
"Совершенно секретно(резерв)": "275",
"Союз(резерв)": "349",
"СТБ(резерв)": "670",
"СТС(резерв)": "79",
"Страна(резерв)": "284",
"ТБН(резерв)": "576",
"Тбн(резерв)": "576",
#"ТБН(резерв)": "694vsetv",
"ТНВ-Татарстан(резерв)": "145vsetv",
"ТНВ-ТАТАРСТАН(резерв)": "145vsetv",
"ТВ-Центр-Международное(резерв)": "435",
"ТВ Центр Международный(резерв)": "435",
"ТДК(резерв)": "776",
"ТВ 3(резерв)": "698",
"ТВ 3 (+3)(резерв)": "845vsetv",
"ТВі(резерв)": "650",
"TBi(резерв)": "650",
"ТВi(резерв)": "650",
"ТВЦ(резерв)": "649",
"ТВ Центр(резерв)": "649",
"Телеканал 100(резерв)": "887vsetv",
"ТНТ(резерв)": "353",
"ТНТ Bravo Молдова(резерв)": "737vsetv",
"тнт+4(резерв)": "557vsetv",
"Тонус ТВ(резерв)": "637",
"Тонус-ТВ(резерв)": "637",
"Телекафе(резерв)": "173",
"Телепутешествия(резерв)": "794",
"Телепутешествия HD(резерв)": "331",
"ТЕТ(резерв)": "479",
"ТРК Украина(резерв)": "326",
"ТРК Киев(резерв)": "75vsetv",
"Ukraine(резерв)": "326",
"ТРО Союза(резерв)": "730",
"ТРО(резерв)": "730",
"Успех(резерв)": "547",
"Усадьба(резерв)": "779",
"Унiан(резерв)": "740vsetv",
"УТР(резерв)": "689vsetv",
"Феникс+ Кино(резерв)": "686",
"Футбол(резерв)": "328",
"Футбол (украина)(резерв)": "666",
"Футбол+ (украина)(резерв)": "753",
"Футбол 1 Украина(резерв)": "666",
"Футбол 2 Украина(резерв)": "753",
"Хокей(резерв)": "702",
"ЧП-Инфо(резерв)": "315",
"Шансон ТВ(резерв)": "662",
"Ю(резерв)": "898",
"Юмор ТВ(резерв)": "412",
"Юмор тв(резерв)": "412",
"Юмор BOX(резерв)": "412",
"Эко-ТВ(резерв)": "685vsetv",
"Эгоист ТВ(резерв)": "431",
"1+1(Резерв)": "620",
"112 Украина(Резерв)": "921vsetv",
"112(Резерв)": "921vsetv",
"100 ТВ(Резерв)": "382vsetv",
"2+2(Резерв)": "583",
"24 Док(Резерв)": "16",
"24 Техно(Резерв)": "710",
"24 Украина(Резерв)": "298vsetv",
"2x2(Резерв)": "323",
"365 Дней(Резерв)": "250",
"5 канал (Украина)(Резерв)": "586",
"5 канал Украина(Резерв)": "586",
"8 канал(Резерв)": "217",
"9 ТВ Орбита(Резерв)": "782vsetv",
"ab moteurs(Резерв)": "127vsetv",
"Amedia 1(Резерв)": "895vsetv",
"Amedia Premium(Резерв)": "896vsetv",
"Amazing Life(Резерв)": "658",
"Amedia 2(Резерв)": "918",
"Animal Planet(Резерв)": "365",
"Animal Planet HD(Резерв)": "990",
"ATR(Резерв)": "763vsetv",
"A-One(Резерв)": "680",
"A-ONE UA(Резерв)": "772vsetv",
"AXN Sci-Fi(Резерв)": "516",
"SONY Sci-Fi(Резерв)": "516",
"Sony Sci-Fi(Резерв)": "516",
"BBC World News(Резерв)": "828",
"Bridge TV(Резерв)": "151",
"Business(Резерв)": "386vsetv",
"Cartoon Network(Резерв)": "601",
"CCTV 4(Резерв)": "904vsetv",
"CCTV Русский(Резерв)": "598vsetv",
"CBS Drama(Резерв)": "911",
"CBS Reality(Резерв)": "912",
"CNN International(Резерв)": "47vsetv",
"CNL(Резерв)": "392vsetv",
"Comedy TV(Резерв)": "51",
"C Music(Резерв)": "319",
"Da Vinci Learning(Резерв)": "410",
"DIVA Universal Russia(Резерв)": "713",
"Dobro TV(Резерв)": "937",
"Discovery Channel(Резерв)": "325",
"Discovery Science(Резерв)": "409",
"Discovery World(Резерв)": "437",
"Investigation Discovery Europe(Резерв)": "19",
"Investigation Discovery(Резерв)": "19",
"Daring TV(Резерв)": "696vsetv",
"Discovery HD Showcase(Резерв)": "111",
"Discowery HD Showcase(Резерв)": "111",
"Discovery Showcase HD(Резерв)": "111",
"Disney Channel(Резерв)": "150",
"English Club TV(Резерв)": "757",
"Enter Film(Резерв)": "281",
"EuroNews(Резерв)": "23",
"EuroNews UA(Резерв)": "23",
"Europa Plus TV(Резерв)": "681",
"Eurosport(Резерв)": "737",
"Eurosport Int. (Eng)(Резерв)": "737",
"Eurosport 2(Резерв)": "850",
"Eurosport 2 Int. (Eng)(Резерв)": "850",
"Eurosport 2 HD(Резерв)": "850",
"Eurosport HD(Резерв)": "560",
"Extreme Sports(Резерв)": "288",
"Fashion TV(Резерв)": "661",
"Fashion TV HD(Резерв)": "121",
"Fashion HD(Резерв)": "121",
"Fashion One HD(Резерв)": "919",
"Fashion One(Резерв)": "919",
"Fox(Резерв)": "659",
"FOX HD(Резерв)": "659",
"Fox HD(Резерв)": "659",
"Fox Life(Резерв)": "615",
"FOX life HD(Резерв)": "464",
"FOX Life HD(Резерв)": "464",
"Fox Life HD(Резерв)": "464",
"France 24(Резерв)": "187",
"France24(Резерв)": "187",
"Galaxy TV(Резерв)": "924",
"GALAXY(Резерв)": "924",
"Gulli(Резерв)": "810",
"GLAS(Резерв)": "457vsetv",
"HD Life(Резерв)": "415",
"HD Спорт(Резерв)": "429",
"HD СПОРТ(Резерв)": "429",
"History Channel(Резерв)": "902vsetv",
"Hustler TV(Резерв)": "666vsetv",
"ICTV(Резерв)": "709",
"iConcerts TV HD(Резерв)": "797vsetv",
"JimJam(Резерв)": "494",
"Jewish News One(Резерв)": "796vsetv",
"JN1(Резерв)": "796vsetv",
"Kids co(Резерв)": "598",
"KidsCo(Резерв)": "598",
"Lale(Резерв)": "911vsetv",
"Look TV(Резерв)": "726vsetv",
"Luxe TV HD(Резерв)": "536vsetv",
"Maxxi-TV(Резерв)": "228",
"MCM Top(Резерв)": "533",
"MGM(Резерв)": "608",
"MGM HD(Резерв)": "934",
"Mezzo(Резерв)": "575",
"Motor TV(Резерв)": "531",
"Motors TV(Резерв)": "531",
"Motors Tv(Резерв)": "531",
"MTV Russia(Резерв)": "1021",
"MTV Россия(Резерв)": "1021",
"MTV Ukraina(Резерв)": "353vsetv",
"MTV Dance(Резерв)": "332",
"MTV Hits UK(Резерв)": "849",
"MTV Rocks(Резерв)": "388",
"MTV Music(Резерв)": "430",
"MTV live HD(Резерв)": "382",
"MTV Live HD(Резерв)": "382",
"Music Box UA(Резерв)": "417vsetv",
"Music Box(Резерв)": "642",
"Russian Music Box(Резерв)": "25",
"myZen.tv HD(Резерв)": "141",
"MyZen TV HD(Резерв)": "141",
"NBA TV(Резерв)": "790vsetv",
"Nat Geo Wild(Резерв)": "807",
"Nat Geo Wild HD(Резерв)": "807",
"National Geographic(Резерв)": "102",
"National Geographic HD(Резерв)": "389",
"News One(Резерв)": "247",
"Nick Jr.(Резерв)": "917",
"Nickelodeon(Резерв)": "567",
"Nickelodeon HD(Резерв)": "423",
"Ocean-TV(Резерв)": "55",
"O-TV(Резерв)": "167",
"Outdoor HD(Резерв)": "322",
"Outdoor Channel(Резерв)": "322",
"Paramount Comedy(Резерв)": "920",
"Playboy TV(Резерв)": "663vsetv",
"Private Spice(Резерв)": "143vsetv",
"Brazzers TV Europe(Резерв)": "143vsetv",
"QTV(Резерв)": "280",
"Real Estate-TV(Резерв)": "481vsetv",
"RTVi(Резерв)": "76",
"RU TV(Резерв)": "258",
"Ru Music(Резерв)": "388vsetv",
"Rusong TV(Резерв)": "591",
"Russian Travel Guide(Резерв)": "648",
"Russia Today Documentary(Резерв)": "788vsetv",
"SHOPping-TV (Ukraine)(Резерв)": "810vsetv",
"SET(Резерв)": "311",
"SET HD(Резерв)": "311",
"S.E.T(Резерв)": "311",
"Sony Turbo(Резерв)": "935",
"Smile of Child(Резерв)": "789",
"Star TV Ukraine(Резерв)": "513vsetv",
"STV(Резерв)": "165",
"Style TV(Резерв)": "119",
"Style tv(Резерв)": "119",
"Teen TV(Резерв)": "448vsetv",
"TiJi(Резерв)": "555",
"TLC(Резерв)": "425",
"TLC Europe(Резерв)": "777vsetv",
"Tonis(Резерв)": "627",
"Tonis HD(Резерв)": "627",
"TVCI(Резерв)": "435",
"TV Rus(Резерв)": "799vsetv",
"TV 1000(Резерв)": "127",
"TV1000(Резерв)": "127",
"TV 1000 Action East(Резерв)": "125",
"TV 1000 Action(Резерв)": "125",
"TV 1000 Русское кино(Резерв)": "267",
"TV1000 Action East(Резерв)": "125",
"TV1000 Action(Резерв)": "125",
"TV1000 Русское кино(Резерв)": "267",
"TV1000 Megahit HD(Резерв)": "816vsetv",
"TV1000 Premium HD(Резерв)": "814vsetv",
"TV1000 Comedy HD(Резерв)": "818vsetv",
"TV 1000 Megahit HD(Резерв)": "816vsetv",
"TV 1000 Premium HD(Резерв)": "814vsetv",
"TV 1000 Comedy HD(Резерв)": "818vsetv",
"Travel Channel(Резерв)": "88vsetv",
"Travel Channel HD(Резерв)": "690vsetv",
"Travel+ adventure(Резерв)": "832vsetv",
"TV XXI (TV21)(Резерв)": "309",
#"Ukrainian Fashion(Резерв)": "939",
"Universal Channel(Резерв)": "213",
"Ukrainian Fashion(Резерв)": "773vsetv",
"VH1(Резерв)": "491",
"VH1 Classic(Резерв)": "156",
"Viasat Explorer(Резерв)": "521",
"Viasat Explorer CEE(Резерв)": "521",
"Viasat History(Резерв)": "277",
"Viasat Nature East(Резерв)": "765",
"Viasat Sport(Резерв)": "455",
"Viasat Sport HD(Резерв)": "455",
"VIASAT Sport Baltic(Резерв)": "504vsetv",
"Viasat Sport Baltic(Резерв)": "504vsetv",
"Sport Baltic(Резерв)": "504vsetv",
"Viasat Nature-History HD(Резерв)": "716vsetv",
"Viasat Nature/History HD(Резерв)": "716vsetv",
"World Fashion(Резерв)": "346",
"XSPORT(Резерв)": "748vsetv",
"Xsport(Резерв)": "748vsetv",
"XXL(Резерв)": "664vsetv",
"Zee TV(Резерв)": "626",
"Zoom(Резерв)": "1009",
"Авто плюс(Резерв)": "153",
"Агро тв(Резерв)": "11",
"Амедиа(Резерв)": "918",
"Астро ТВ(Резерв)": "249",
"Астро(Резерв)": "249",
"Беларусь 24(Резерв)": "851",
"Бигуди(Резерв)": "481vsetv",
"Боец(Резерв)": "454",
"Бойцовский клуб(Резерв)": "986",
"БТБ(Резерв)": "877vsetv",
"БСТ(Резерв)": "272vsetv",
"Вопросы и ответы(Резерв)": "333",
"Время(Резерв)": "669",
"ВТВ(Резерв)": "139vsetv",
"Гамма(Резерв)": "479vsetv",
"Глас(Резерв)": "294vsetv",
"Гумор ТБ(Резерв)": "505vsetv",
"Детский(Резерв)": "66",
"Детский мир(Резерв)": "747",
"Дождь(Резерв)": "384",
"Дождь HD(Резерв)": "384",
"Дом кино(Резерв)": "834",
"Домашние животные(Резерв)": "520",
"Домашние Животные(Резерв)": "520",
"Домашний(Резерв)": "304",
"Домашний магазин(Резерв)": "695vsetv",
"Драйв ТВ(Резерв)": "505",
"Еврокино(Резерв)": "352",
"ЕДА(Резерв)": "931",
"Еда(Резерв)": "931",
"Еда ТВ(Резерв)": "931",
"ЕДА HD(Резерв)": "930",
"Живи(Резерв)": "113",
"Звезда(Резерв)": "405",
"Закон ТВ(Резерв)": "178",
"Закон тв(Резерв)": "178",
"Закон-тв(Резерв)": "178",
"Закон ТВ(Резерв)": "178",
"Загородный(Резерв)": "705",
"Загородная жизнь(Резерв)": "21",
"Знание(Резерв)": "201",
"Здоровое ТВ(Резерв)": "595",
"Зоо ТВ(Резерв)": "273",
"Зоопарк(Резерв)": "367",
"Иллюзион+(Резерв)": "123",
"Искушение(Резерв)": "754vsetv",
"Индия(Резерв)": "798",
"Интер(Резерв)": "677",
"Интер+(Резерв)": "808",
"Интересное ТВ(Резерв)": "24",
"Израиль плюс(Резерв)": "532vsetv",
"История(Резерв)": "879vsetv",
"К1(Резерв)": "453",
"К2(Резерв)": "20vsetv",
"Карусель(Резерв)": "740",
"Кинопоказ(Резерв)": "22",
"Комедия ТВ(Резерв)": "821",
"Комсомольская правда(Резерв)": "852",
"Кто есть кто(Резерв)": "769",
"Кто Есть Кто(Резерв)": "769",
"КРТ(Резерв)": "149vsetv",
"Киевская Русь(Резерв)": "149vsetv",
"Кухня ТВ(Резерв)": "614",
"Культура Украина(Резерв)": "285vsetv",
"КХЛ ТВ(Резерв)": "481",
"КХЛ HD(Резерв)": "481",
"Ля-минор(Резерв)": "257",
"Львов ТВ(Резерв)": "920vsetv",
"М1(Резерв)": "632",
"М2(Резерв)": "445vsetv",
"Мега(Резерв)": "788",
"Меню ТВ(Резерв)": "348vsetv",
"Мир(Резерв)": "726",
"Мир сериала(Резерв)": "145",
"Мир Сериала(Резерв)": "145",
"Много ТВ(Резерв)": "799",
"Моя планета(Резерв)": "675",
"Москва 24(Резерв)": "334",
"Москва Доверие(Резерв)": "655",
"Москва доверие(Резерв)": "655",
"Музыка Первого(Резерв)": "715",
"Мужской(Резерв)": "82",
"Малятко ТВ(Резерв)": "606vsetv",
"Моя дитина(Резерв)": "761vsetv",
"Мать и дитя(Резерв)": "618",
"Мать и Дитя(Резерв)": "618",
"Мультимания(Резерв)": "31",
"Муз ТВ(Резерв)": "808vsetv",
"Надия(Резерв)": "871vsetv",
"Надiя(Резерв)": "871vsetv",
"Нано ТВ(Резерв)": "35",
"Наука 2.0(Резерв)": "723",
"Наше любимое кино(Резерв)": "477",
"НЛО ТВ(Резерв)": "843vsetv",
"Новый канал(Резерв)": "128",
"Ностальгия(Резерв)": "783",
"Ночной клуб(Резерв)": "455vsetv",
"НСТ(Резерв)": "518",
"НТВ(Резерв)": "162",
"НТВ Мир(Резерв)": "422",
"НТВ+ Кино плюс(Резерв)": "644",
"НТВ+ Киноклуб(Резерв)": "462",
"НТВ+ Кинолюкс(Резерв)": "8",
"НТВ+ Киносоюз(Резерв)": "71",
"НТВ+ Кино Cоюз(Резерв)": "71",
"НТВ+ Кинохит(Резерв)": "542",
"НТВ+ Наше кино(Резерв)": "12",
"НТВ+ Наше новое кино(Резерв)": "485",
"НТВ+ Премьера(Резерв)": "566",
"НТВ+ Баскетбол(Резерв)": "697",
"НТВ+ Наш футбол(Резерв)": "499",
"НТВ+ Наш футбол HD(Резерв)": "889vsetv",
"НТВ+ Спорт(Резерв)": "134",
"НТВ+СПОРТ(Резерв)": "134",
"НТВ+ Спорт Онлайн(Резерв)": "183",
"НТВ+ Спорт онлайн(Резерв)": "183",
"НТВ+ Спорт Союз(Резерв)": "306",
"НТВ+ Спорт плюс(Резерв)": "377",
"НТВ+ СпортХит(Резерв)": "910vsetv",
"НТВ+ Спорт Хит(Резерв)": "910vsetv",
"НТВ+ Спортхит(Резерв)": "910vsetv",
"НТВ+ Теннис(Резерв)": "358",
"НТВ+ Футбол(Резерв)": "664",
"НТВ+ Футбол 2(Резерв)": "563",
"НТВ+ Футбол HD(Резерв)": "664",
"НТВ+ Футбол 2 HD(Резерв)": "563",
"НТН (Украина)(Резерв)": "140",
"НТС Севастополь(Резерв)": "884vsetv",
"О2ТВ(Резерв)": "777",
"О2 ТВ(Резерв)": "777",
"Оружие(Резерв)": "376",
"ОСТ(Резерв)": "926",
"ОТР(Резерв)": "880vsetv",
"ОНТ Украина(Резерв)": "111vsetv",
"Открытый Мир(Резерв)": "692vsetv",
"Охота и рыбалка(Резерв)": "617",
"Охотник и рыболов(Резерв)": "132",
"Охотник и рыболов HD(Резерв)": "842vsetv",
"Парк развлечений(Резерв)": "37",
"Первый автомобильный (укр)(Резерв)": "507",
"Первый деловой(Резерв)": "85",
"Первый канал(Резерв)": "146",
"Первый канал (Европа)(Резерв)": "391",
"Первый канал (Украина)(Резерв)": "339vsetv",
"Первый канал (СНГ)(Резерв)": "391",
"Первый канал HD(Резерв)": "983",
"ПЕРВЫЙ HD(Резерв)": "983",
"Первый муниципальный (Донецк)(Резерв)": "670vsetv",
"Первый национальный (Украина)(Резерв)": "773",
"Первый образовательный(Резерв)": "774",
"Перец(Резерв)": "511",
"Пиксель ТВ(Резерв)": "940",
"ПлюсПлюс(Резерв)": "24vsetv",
"Погода ТВ(Резерв)": "759vsetv",
"Подмосковье(Резерв)": "161",
"Про все(Резерв)": "458",
"Pro Все(Резерв)": "458",
"Про Все(Резерв)": "458",
"Право ТВ(Резерв)": "861vsetv",
"Просвещение(Резерв)": "685",
"Психология 21(Резерв)": "434",
"Пятый канал(Резерв)": "427",
"Пятница(Резерв)": "1003",
"Рада Украина(Резерв)": "823vsetv",
"Раз ТВ(Резерв)": "363",
"РАЗ ТВ(Резерв)": "363",
"РБК(Резерв)": "743",
"РЕН ТВ(Резерв)": "689",
"РЕН ТВ (+7)(Резерв)": "572vsetv",
"РЖД(Резерв)": "509",
"Ретро ТВ(Резерв)": "6",
"Россия 1(Резерв)": "711",
"Россия 2(Резерв)": "515",
"Россия 24(Резерв)": "291",
"Россия К(Резерв)": "187",
"РОССИЯ HD(Резерв)": "984",
"Россия HD(Резерв)": "984",
"РТР-Планета(Резерв)": "143",
"РТР Планета(Резерв)": "143",
"Русский Бестселлер(Резерв)": "994",
"Русский иллюзион(Резерв)": "53",
"Русский роман(Резерв)": "401",
"Русский экстрим(Резерв)": "406",
"Русская ночь(Резерв)": "296vsetv",
"Сарафан ТВ(Резерв)": "663",
"Сарафан(Резерв)": "663",
"Сонце(Резерв)": "874vsetv",
"Спас(Резерв)": "447",
"Спас ТВ(Резерв)": "447",
"Спорт 1(Резерв)": "181",
"Спорт 1 HD(Резерв)": "554",
"Спорт 1 (Украина)(Резерв)": "270vsetv",
"Спорт 2 (Украина)(Резерв)": "309vsetv",
"Совершенно секретно(Резерв)": "275",
"Союз(Резерв)": "349",
"СТБ(Резерв)": "670",
"СТС(Резерв)": "79",
"Страна(Резерв)": "284",
"ТБН(Резерв)": "576",
"Тбн(Резерв)": "576",
#"ТБН(Резерв)": "694vsetv",
"ТНВ-Татарстан(Резерв)": "145vsetv",
"ТНВ-ТАТАРСТАН(Резерв)": "145vsetv",
"ТВ-Центр-Международное(Резерв)": "435",
"ТВ Центр Международный(Резерв)": "435",
"ТДК(Резерв)": "776",
"ТВ 3(Резерв)": "698",
"ТВ 3 (+3)(Резерв)": "845vsetv",
"ТВі(Резерв)": "650",
"TBi(Резерв)": "650",
"ТВi(Резерв)": "650",
"ТВЦ(Резерв)": "649",
"ТВ Центр(Резерв)": "649",
"Телеканал 100(Резерв)": "887vsetv",
"ТНТ(Резерв)": "353",
"ТНТ Bravo Молдова(Резерв)": "737vsetv",
"тнт+4(Резерв)": "557vsetv",
"Тонус ТВ(Резерв)": "637",
"Тонус-ТВ(Резерв)": "637",
"Телекафе(Резерв)": "173",
"Телепутешествия(Резерв)": "794",
"Телепутешествия HD(Резерв)": "331",
"ТЕТ(Резерв)": "479",
"ТРК Украина(Резерв)": "326",
"ТРК Киев(Резерв)": "75vsetv",
"Ukraine(Резерв)": "326",
"ТРО Союза(Резерв)": "730",
"ТРО(Резерв)": "730",
"Успех(Резерв)": "547",
"Усадьба(Резерв)": "779",
"Унiан(Резерв)": "740vsetv",
"УТР(Резерв)": "689vsetv",
"Феникс+ Кино(Резерв)": "686",
"Футбол(Резерв)": "328",
"Футбол (украина)(Резерв)": "666",
"Футбол+ (украина)(Резерв)": "753",
"Футбол 1 Украина(Резерв)": "666",
"Футбол 2 Украина(Резерв)": "753",
"Хокей(Резерв)": "702",
"ЧП-Инфо(Резерв)": "315",
"Шансон ТВ(Резерв)": "662",
"Ю(Резерв)": "898",
"Юмор ТВ(Резерв)": "412",
"Юмор тв(Резерв)": "412",
"Юмор BOX(Резерв)": "412",
"Эко-ТВ(Резерв)": "685vsetv",
"Эгоист ТВ(Резерв)": "431",
"1+1 (Резерв)": "620",
"112 Украина (Резерв)": "921vsetv",
"112 (Резерв)": "921vsetv",
"100 ТВ (Резерв)": "382vsetv",
"2+2 (Резерв)": "583",
"24 Док (Резерв)": "16",
"24 Техно (Резерв)": "710",
"24 Украина (Резерв)": "298vsetv",
"2x2 (Резерв)": "323",
"365 Дней (Резерв)": "250",
"5 канал (Украина) (Резерв)": "586",
"5 канал Украина (Резерв)": "586",
"8 канал (Резерв)": "217",
"9 ТВ Орбита (Резерв)": "782vsetv",
"ab moteurs (Резерв)": "127vsetv",
"Amedia 1 (Резерв)": "895vsetv",
"Amedia Premium (Резерв)": "896vsetv",
"Amazing Life (Резерв)": "658",
"Amedia 2 (Резерв)": "918",
"Animal Planet (Резерв)": "365",
"Animal Planet HD (Резерв)": "990",
"ATR (Резерв)": "763vsetv",
"A-One (Резерв)": "680",
"A-ONE UA (Резерв)": "772vsetv",
"AXN Sci-Fi (Резерв)": "516",
"SONY Sci-Fi (Резерв)": "516",
"Sony Sci-Fi (Резерв)": "516",
"BBC World News (Резерв)": "828",
"Bridge TV (Резерв)": "151",
"Business (Резерв)": "386vsetv",
"Cartoon Network (Резерв)": "601",
"CCTV 4 (Резерв)": "904vsetv",
"CCTV Русский (Резерв)": "598vsetv",
"CBS Drama (Резерв)": "911",
"CBS Reality (Резерв)": "912",
"CNN International (Резерв)": "47vsetv",
"CNL (Резерв)": "392vsetv",
"Comedy TV (Резерв)": "51",
"C Music (Резерв)": "319",
"Da Vinci Learning (Резерв)": "410",
"DIVA Universal Russia (Резерв)": "713",
"Dobro TV (Резерв)": "937",
"Discovery Channel (Резерв)": "325",
"Discovery Science (Резерв)": "409",
"Discovery World (Резерв)": "437",
"Investigation Discovery Europe (Резерв)": "19",
"Investigation Discovery (Резерв)": "19",
"Daring TV (Резерв)": "696vsetv",
"Discovery HD Showcase (Резерв)": "111",
"Discowery HD Showcase (Резерв)": "111",
"Discovery Showcase HD (Резерв)": "111",
"Disney Channel (Резерв)": "150",
"English Club TV (Резерв)": "757",
"Enter Film (Резерв)": "281",
"EuroNews (Резерв)": "23",
"EuroNews UA (Резерв)": "23",
"Europa Plus TV (Резерв)": "681",
"Eurosport (Резерв)": "737",
"Eurosport Int. (Eng) (Резерв)": "737",
"Eurosport 2 (Резерв)": "850",
"Eurosport 2 Int. (Eng) (Резерв)": "850",
"Eurosport 2 HD (Резерв)": "850",
"Eurosport HD (Резерв)": "560",
"Extreme Sports (Резерв)": "288",
"Fashion TV (Резерв)": "661",
"Fashion TV HD (Резерв)": "121",
"Fashion HD (Резерв)": "121",
"Fashion One HD (Резерв)": "919",
"Fashion One (Резерв)": "919",
"Fox (Резерв)": "659",
"FOX HD (Резерв)": "659",
"Fox HD (Резерв)": "659",
"Fox Life (Резерв)": "615",
"FOX life HD (Резерв)": "464",
"FOX Life HD (Резерв)": "464",
"Fox Life HD (Резерв)": "464",
"France 24 (Резерв)": "187",
"France24 (Резерв)": "187",
"Galaxy TV (Резерв)": "924",
"GALAXY (Резерв)": "924",
"Gulli (Резерв)": "810",
"GLAS (Резерв)": "457vsetv",
"HD Life (Резерв)": "415",
"HD Спорт (Резерв)": "429",
"HD СПОРТ (Резерв)": "429",
"History Channel (Резерв)": "902vsetv",
"Hustler TV (Резерв)": "666vsetv",
"ICTV (Резерв)": "709",
"iConcerts TV HD (Резерв)": "797vsetv",
"JimJam (Резерв)": "494",
"Jewish News One (Резерв)": "796vsetv",
"JN1 (Резерв)": "796vsetv",
"Kids co (Резерв)": "598",
"KidsCo (Резерв)": "598",
"Lale (Резерв)": "911vsetv",
"Look TV (Резерв)": "726vsetv",
"Luxe TV HD (Резерв)": "536vsetv",
"Maxxi-TV (Резерв)": "228",
"MCM Top (Резерв)": "533",
"MGM (Резерв)": "608",
"MGM HD (Резерв)": "934",
"Mezzo (Резерв)": "575",
"Motor TV (Резерв)": "531",
"Motors TV (Резерв)": "531",
"Motors Tv (Резерв)": "531",
"MTV Russia (Резерв)": "1021",
"MTV Россия (Резерв)": "1021",
"MTV Ukraina (Резерв)": "353vsetv",
"MTV Dance (Резерв)": "332",
"MTV Hits UK (Резерв)": "849",
"MTV Rocks (Резерв)": "388",
"MTV Music (Резерв)": "430",
"MTV live HD (Резерв)": "382",
"MTV Live HD (Резерв)": "382",
"Music Box UA (Резерв)": "417vsetv",
"Music Box (Резерв)": "642",
"Russian Music Box (Резерв)": "25",
"myZen.tv HD (Резерв)": "141",
"MyZen TV HD (Резерв)": "141",
"NBA TV (Резерв)": "790vsetv",
"Nat Geo Wild (Резерв)": "807",
"Nat Geo Wild HD (Резерв)": "807",
"National Geographic (Резерв)": "102",
"National Geographic HD (Резерв)": "389",
"News One (Резерв)": "247",
"Nick Jr. (Резерв)": "917",
"Nickelodeon (Резерв)": "567",
"Nickelodeon HD (Резерв)": "423",
"Ocean-TV (Резерв)": "55",
"O-TV (Резерв)": "167",
"Outdoor HD (Резерв)": "322",
"Outdoor Channel (Резерв)": "322",
"Paramount Comedy (Резерв)": "920",
"Playboy TV (Резерв)": "663vsetv",
"Private Spice (Резерв)": "143vsetv",
"Brazzers TV Europe (Резерв)": "143vsetv",
"QTV (Резерв)": "280",
"Real Estate-TV (Резерв)": "481vsetv",
"RTVi (Резерв)": "76",
"RU TV (Резерв)": "258",
"Ru Music (Резерв)": "388vsetv",
"Rusong TV (Резерв)": "591",
"Russian Travel Guide (Резерв)": "648",
"Russia Today Documentary (Резерв)": "788vsetv",
"SHOPping-TV (Ukraine) (Резерв)": "810vsetv",
"SET (Резерв)": "311",
"SET HD (Резерв)": "311",
"S.E.T (Резерв)": "311",
"Sony Turbo (Резерв)": "935",
"Smile of Child (Резерв)": "789",
"Star TV Ukraine (Резерв)": "513vsetv",
"STV (Резерв)": "165",
"Style TV (Резерв)": "119",
"Style tv (Резерв)": "119",
"Teen TV (Резерв)": "448vsetv",
"TiJi (Резерв)": "555",
"TLC (Резерв)": "425",
"TLC Europe (Резерв)": "777vsetv",
"Tonis (Резерв)": "627",
"Tonis HD (Резерв)": "627",
"TVCI (Резерв)": "435",
"TV Rus (Резерв)": "799vsetv",
"TV 1000 (Резерв)": "127",
"TV1000 (Резерв)": "127",
"TV 1000 Action East (Резерв)": "125",
"TV 1000 Action (Резерв)": "125",
"TV 1000 Русское кино (Резерв)": "267",
"TV1000 Action East (Резерв)": "125",
"TV1000 Action (Резерв)": "125",
"TV1000 Русское кино (Резерв)": "267",
"TV1000 Megahit HD (Резерв)": "816vsetv",
"TV1000 Premium HD (Резерв)": "814vsetv",
"TV1000 Comedy HD (Резерв)": "818vsetv",
"TV 1000 Megahit HD (Резерв)": "816vsetv",
"TV 1000 Premium HD (Резерв)": "814vsetv",
"TV 1000 Comedy HD (Резерв)": "818vsetv",
"Travel Channel (Резерв)": "88vsetv",
"Travel Channel HD (Резерв)": "690vsetv",
"Travel+ adventure (Резерв)": "832vsetv",
"TV XXI (TV21) (Резерв)": "309",
#"Ukrainian Fashion (Резерв)": "939",
"Universal Channel (Резерв)": "213",
"Ukrainian Fashion (Резерв)": "773vsetv",
"VH1 (Резерв)": "491",
"VH1 Classic (Резерв)": "156",
"Viasat Explorer (Резерв)": "521",
"Viasat Explorer CEE (Резерв)": "521",
"Viasat History (Резерв)": "277",
"Viasat Nature East (Резерв)": "765",
"Viasat Sport (Резерв)": "455",
"Viasat Sport HD (Резерв)": "455",
"VIASAT Sport Baltic (Резерв)": "504vsetv",
"Viasat Sport Baltic (Резерв)": "504vsetv",
"Sport Baltic (Резерв)": "504vsetv",
"Viasat Nature-History HD (Резерв)": "716vsetv",
"Viasat Nature/History HD (Резерв)": "716vsetv",
"World Fashion (Резерв)": "346",
"XSPORT (Резерв)": "748vsetv",
"Xsport (Резерв)": "748vsetv",
"XXL (Резерв)": "664vsetv",
"Zee TV (Резерв)": "626",
"Zoom (Резерв)": "1009",
"Авто плюс (Резерв)": "153",
"Агро тв (Резерв)": "11",
"Амедиа (Резерв)": "918",
"Астро ТВ (Резерв)": "249",
"Астро (Резерв)": "249",
"Беларусь 24 (Резерв)": "851",
"Бигуди (Резерв)": "481vsetv",
"Боец (Резерв)": "454",
"Бойцовский клуб (Резерв)": "986",
"БТБ (Резерв)": "877vsetv",
"БСТ (Резерв)": "272vsetv",
"Вопросы и ответы (Резерв)": "333",
"Время (Резерв)": "669",
"ВТВ (Резерв)": "139vsetv",
"Гамма (Резерв)": "479vsetv",
"Глас (Резерв)": "294vsetv",
"Гумор ТБ (Резерв)": "505vsetv",
"Детский (Резерв)": "66",
"Детский мир (Резерв)": "747",
"Дождь (Резерв)": "384",
"Дождь HD (Резерв)": "384",
"Дом кино (Резерв)": "834",
"Домашние животные (Резерв)": "520",
"Домашние Животные (Резерв)": "520",
"Домашний (Резерв)": "304",
"Домашний магазин (Резерв)": "695vsetv",
"Драйв ТВ (Резерв)": "505",
"Еврокино (Резерв)": "352",
"ЕДА (Резерв)": "931",
"Еда (Резерв)": "931",
"Еда ТВ (Резерв)": "931",
"ЕДА HD (Резерв)": "930",
"Живи (Резерв)": "113",
"Звезда (Резерв)": "405",
"Закон ТВ (Резерв)": "178",
"Закон тв (Резерв)": "178",
"Закон-тв (Резерв)": "178",
"Закон ТВ (Резерв)": "178",
"Загородный (Резерв)": "705",
"Загородная жизнь (Резерв)": "21",
"Знание (Резерв)": "201",
"Здоровое ТВ (Резерв)": "595",
"Зоо ТВ (Резерв)": "273",
"Зоопарк (Резерв)": "367",
"Иллюзион+ (Резерв)": "123",
"Искушение (Резерв)": "754vsetv",
"Индия (Резерв)": "798",
"Интер (Резерв)": "677",
"Интер+ (Резерв)": "808",
"Интересное ТВ (Резерв)": "24",
"Израиль плюс (Резерв)": "532vsetv",
"История (Резерв)": "879vsetv",
"К1 (Резерв)": "453",
"К2 (Резерв)": "20vsetv",
"Карусель (Резерв)": "740",
"Кинопоказ (Резерв)": "22",
"Комедия ТВ (Резерв)": "821",
"Комсомольская правда (Резерв)": "852",
"Кто есть кто (Резерв)": "769",
"Кто Есть Кто (Резерв)": "769",
"КРТ (Резерв)": "149vsetv",
"Киевская Русь (Резерв)": "149vsetv",
"Кухня ТВ (Резерв)": "614",
"Культура Украина (Резерв)": "285vsetv",
"КХЛ ТВ (Резерв)": "481",
"КХЛ HD (Резерв)": "481",
"Ля-минор (Резерв)": "257",
"Львов ТВ (Резерв)": "920vsetv",
"М1 (Резерв)": "632",
"М2 (Резерв)": "445vsetv",
"Мега (Резерв)": "788",
"Меню ТВ (Резерв)": "348vsetv",
"Мир (Резерв)": "726",
"Мир сериала (Резерв)": "145",
"Мир Сериала (Резерв)": "145",
"Много ТВ (Резерв)": "799",
"Моя планета (Резерв)": "675",
"Москва 24 (Резерв)": "334",
"Москва Доверие (Резерв)": "655",
"Москва доверие (Резерв)": "655",
"Музыка Первого (Резерв)": "715",
"Мужской (Резерв)": "82",
"Малятко ТВ (Резерв)": "606vsetv",
"Моя дитина (Резерв)": "761vsetv",
"Мать и дитя (Резерв)": "618",
"Мать и Дитя (Резерв)": "618",
"Мультимания (Резерв)": "31",
"Муз ТВ (Резерв)": "808vsetv",
"Надия (Резерв)": "871vsetv",
"Надiя (Резерв)": "871vsetv",
"Нано ТВ (Резерв)": "35",
"Наука 2.0 (Резерв)": "723",
"Наше любимое кино (Резерв)": "477",
"НЛО ТВ (Резерв)": "843vsetv",
"Новый канал (Резерв)": "128",
"Ностальгия (Резерв)": "783",
"Ночной клуб (Резерв)": "455vsetv",
"НСТ (Резерв)": "518",
"НТВ (Резерв)": "162",
"НТВ Мир (Резерв)": "422",
"НТВ+ Кино плюс (Резерв)": "644",
"НТВ+ Киноклуб (Резерв)": "462",
"НТВ+ Кинолюкс (Резерв)": "8",
"НТВ+ Киносоюз (Резерв)": "71",
"НТВ+ Кино Cоюз (Резерв)": "71",
"НТВ+ Кинохит (Резерв)": "542",
"НТВ+ Наше кино (Резерв)": "12",
"НТВ+ Наше новое кино (Резерв)": "485",
"НТВ+ Премьера (Резерв)": "566",
"НТВ+ Баскетбол (Резерв)": "697",
"НТВ+ Наш футбол (Резерв)": "499",
"НТВ+ Наш футбол HD (Резерв)": "889vsetv",
"НТВ+ Спорт (Резерв)": "134",
"НТВ+СПОРТ (Резерв)": "134",
"НТВ+ Спорт Онлайн (Резерв)": "183",
"НТВ+ Спорт онлайн (Резерв)": "183",
"НТВ+ Спорт Союз (Резерв)": "306",
"НТВ+ Спорт плюс (Резерв)": "377",
"НТВ+ СпортХит (Резерв)": "910vsetv",
"НТВ+ Спорт Хит (Резерв)": "910vsetv",
"НТВ+ Спортхит (Резерв)": "910vsetv",
"НТВ+ Теннис (Резерв)": "358",
"НТВ+ Футбол (Резерв)": "664",
"НТВ+ Футбол 2 (Резерв)": "563",
"НТВ+ Футбол HD (Резерв)": "664",
"НТВ+ Футбол 2 HD (Резерв)": "563",
"НТН (Украина) (Резерв)": "140",
"НТС Севастополь (Резерв)": "884vsetv",
"О2ТВ (Резерв)": "777",
"О2 ТВ (Резерв)": "777",
"Оружие (Резерв)": "376",
"ОСТ (Резерв)": "926",
"ОТР (Резерв)": "880vsetv",
"ОНТ Украина (Резерв)": "111vsetv",
"Открытый Мир (Резерв)": "692vsetv",
"Охота и рыбалка (Резерв)": "617",
"Охотник и рыболов (Резерв)": "132",
"Охотник и рыболов HD (Резерв)": "842vsetv",
"Парк развлечений (Резерв)": "37",
"Первый автомобильный (укр) (Резерв)": "507",
"Первый деловой (Резерв)": "85",
"Первый канал (Резерв)": "146",
"Первый канал (Европа) (Резерв)": "391",
"Первый канал (Украина) (Резерв)": "339vsetv",
"Первый канал (СНГ) (Резерв)": "391",
"Первый канал HD (Резерв)": "983",
"ПЕРВЫЙ HD (Резерв)": "983",
"Первый муниципальный (Донецк) (Резерв)": "670vsetv",
"Первый национальный (Украина) (Резерв)": "773",
"Первый образовательный (Резерв)": "774",
"Перец (Резерв)": "511",
"Пиксель ТВ (Резерв)": "940",
"ПлюсПлюс (Резерв)": "24vsetv",
"Погода ТВ (Резерв)": "759vsetv",
"Подмосковье (Резерв)": "161",
"Про все (Резерв)": "458",
"Pro Все (Резерв)": "458",
"Про Все (Резерв)": "458",
"Право ТВ (Резерв)": "861vsetv",
"Просвещение (Резерв)": "685",
"Психология 21 (Резерв)": "434",
"Пятый канал (Резерв)": "427",
"Пятница (Резерв)": "1003",
"Рада Украина (Резерв)": "823vsetv",
"Раз ТВ (Резерв)": "363",
"РАЗ ТВ (Резерв)": "363",
"РБК (Резерв)": "743",
"РЕН ТВ (Резерв)": "689",
"РЕН ТВ (+7) (Резерв)": "572vsetv",
"РЖД (Резерв)": "509",
"Ретро ТВ (Резерв)": "6",
"Россия 1 (Резерв)": "711",
"Россия 2 (Резерв)": "515",
"Россия 24 (Резерв)": "291",
"Россия К (Резерв)": "187",
"РОССИЯ HD (Резерв)": "984",
"Россия HD (Резерв)": "984",
"РТР-Планета (Резерв)": "143",
"РТР Планета (Резерв)": "143",
"Русский Бестселлер (Резерв)": "994",
"Русский иллюзион (Резерв)": "53",
"Русский роман (Резерв)": "401",
"Русский экстрим (Резерв)": "406",
"Русская ночь (Резерв)": "296vsetv",
"Сарафан ТВ (Резерв)": "663",
"Сарафан (Резерв)": "663",
"Сонце (Резерв)": "874vsetv",
"Спас (Резерв)": "447",
"Спас ТВ (Резерв)": "447",
"Спорт 1 (Резерв)": "181",
"Спорт 1 HD (Резерв)": "554",
"Спорт 1 (Украина) (Резерв)": "270vsetv",
"Спорт 2 (Украина) (Резерв)": "309vsetv",
"Совершенно секретно (Резерв)": "275",
"Союз (Резерв)": "349",
"СТБ (Резерв)": "670",
"СТС (Резерв)": "79",
"Страна (Резерв)": "284",
"ТБН (Резерв)": "576",
"Тбн (Резерв)": "576",
#"ТБН (Резерв)": "694vsetv",
"ТНВ-Татарстан (Резерв)": "145vsetv",
"ТНВ-ТАТАРСТАН (Резерв)": "145vsetv",
"ТВ-Центр-Международное (Резерв)": "435",
"ТВ Центр Международный (Резерв)": "435",
"ТДК (Резерв)": "776",
"ТВ 3 (Резерв)": "698",
"ТВ 3 (+3) (Резерв)": "845vsetv",
"ТВі (Резерв)": "650",
"TBi (Резерв)": "650",
"ТВi (Резерв)": "650",
"ТВЦ (Резерв)": "649",
"ТВ Центр (Резерв)": "649",
"Телеканал 100 (Резерв)": "887vsetv",
"ТНТ (Резерв)": "353",
"ТНТ Bravo Молдова (Резерв)": "737vsetv",
"тнт+4 (Резерв)": "557vsetv",
"Тонус ТВ (Резерв)": "637",
"Тонус-ТВ (Резерв)": "637",
"Телекафе (Резерв)": "173",
"Телепутешествия (Резерв)": "794",
"Телепутешествия HD (Резерв)": "331",
"ТЕТ (Резерв)": "479",
"ТРК Украина (Резерв)": "326",
"ТРК Киев (Резерв)": "75vsetv",
"Ukraine (Резерв)": "326",
"ТРО Союза (Резерв)": "730",
"ТРО (Резерв)": "730",
"Успех (Резерв)": "547",
"Усадьба (Резерв)": "779",
"Унiан (Резерв)": "740vsetv",
"УТР (Резерв)": "689vsetv",
"Феникс+ Кино (Резерв)": "686",
"Футбол (Резерв)": "328",
"Футбол (украина) (Резерв)": "666",
"Футбол+ (украина) (Резерв)": "753",
"Футбол 1 Украина (Резерв)": "666",
"Футбол 2 Украина (Резерв)": "753",
"Хокей (Резерв)": "702",
"ЧП-Инфо (Резерв)": "315",
"Шансон ТВ (Резерв)": "662",
"Ю (Резерв)": "898",
"Юмор ТВ (Резерв)": "412",
"Юмор тв (Резерв)": "412",
"Юмор BOX (Резерв)": "412",
"Эко-ТВ (Резерв)": "685vsetv",
"Эгоист ТВ (Резерв)": "431",
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
            ni=dx[ch['name']]
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
    http = GET('http://torrent-tv.ru/' + params['file'])
    if http == None:
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
 ###################################
        try:
            d=[]
            ni=dx[title.strip()]
            d=YaTv.GetPr(id2=ni)
        except:ni=title.strip()
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
    http = GET('http://torrent-tv.ru/films.php')
    if http == None:
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
    http = GET('http://torrent-tv.ru' + params['file']+'&page=1')
    if http == None:
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
    http = GET('http://torrent-tv.ru' + params['file']+page)
    if http == None:
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
    http = GET('http://torrent-tv.ru/' + params['file'])
    if http == None:
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
    http = GET('http://torrent-tv.ru/' + params['file'])#+'?data='+title)
    if http == None:
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
    http = GET('http://torrent-tv.ru/' + params['file'].replace(title,params['date']))
    if http == None:
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
        page = GET('http://torrent-tv.ru/torrent-online.php?translation=' + str(params['id']), data)
        if page == None:
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
    http = GET('http://torrent-tv.ru/' + params['file'])
    if http == None:
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
            showMessage('Torrent TV', 'Обновление плейлиста выполнено')
        else:
            nupd = lupd + datetime.timedelta(hours = 7)

            if nupd < datetime.datetime.now():
                showMessage('Torrent TV', 'Производится обновление плейлиста')
                cookie = UpdCookie()
                db = DataBase(db_name, cookie)
                db.UpdateDB()
                showMessage('Torrent TV', 'Обновление плейлиста выполнено')
        del db
        
        func = None
        xbmc.log( '[%s]: Primary input' % addon_id, 1 )

        mainScreen(params)
    if func != None:
        try:
            pfunc = globals()[func]
        except:
            pfunc = None
            xbmc.log( '[%s]: Function "%s" not found' % (addon_id, func), 4 )
            showMessage('Internal addon error', 'Function "%s" not found' % func, 2000)
        if pfunc:
            pfunc(params)
