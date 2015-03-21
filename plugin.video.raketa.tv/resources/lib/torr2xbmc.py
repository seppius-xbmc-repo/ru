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
from TSCore import TSengine as tsengine
import base64
import time
from database import DataBase
import cookielib
import webbrowser
hos = int(sys.argv[1])
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
__addon__ = xbmcaddon.Addon( id = 'plugin.video.raketa.tv' )
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
ch_color = __addon__.getSetting('ch_color')
prog_color = __addon__.getSetting("prog_color")
ch_b = __addon__.getSetting("ch_b")
prog_b = __addon__.getSetting('prog_b')
prog_str = __addon__.getSetting('prog_str')
ch_i = __addon__.getSetting("ch_i")
prog_i = __addon__.getSetting('prog_i')
playlist = __addon__.getSetting('playlist')

aceport=62062
cookie = ""
PLUGIN_DATA_PATH = xbmc.translatePath( os.path.join( "special://profile/addon_data", 'plugin.video.raketa.tv') )

if prog_str == "true": pr_str = " "
else: pr_str = chr(10)

if (sys.platform == 'win32') or (sys.platform == 'win64'):
    PLUGIN_DATA_PATH = PLUGIN_DATA_PATH.decode('utf-8')
    
PROGRAM_SOURCE_PATH = os.path.join( PLUGIN_DATA_PATH , "%s_inter-tv.zip"  % datetime.date.today().strftime("%W") )
    
if playlist == "0":
    db_name = os.path.join(PLUGIN_DATA_PATH, 'tvbase.db')
elif playlist == "1":
    db_name = os.path.join(PLUGIN_DATA_PATH, 'tvbase_a.db')
elif playlist == "2":
    db_name = os.path.join(PLUGIN_DATA_PATH, 'tvbase_vip.db')
    
cookiefile = os.path.join(PLUGIN_DATA_PATH, 'cookie.txt')
xbmcplugin.setContent(int(sys.argv[1]), 'episodes')


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
            
        resp = urllib2.urlopen(req)
        if cookie == "":
            if os.path.exists(cookiefile):
                fgetcook = open(cookiefile, 'r')
                cookie = fgetcook.read()
                del fgetcook
                try:
                    http = resp.read()
                    resp.close()
                    return http
                except:
                    cookie = UpdCookie()
            else:
                cookie = UpdCookie()
        http = resp.read()
        resp.close()
        return http
    except Exception, e:
        xbmc.log( '[%s]: GET EXCEPT [%s]' % (addon_id, e), 4 )
        showMessage('HTTP ERROR', e, 5000)
        
def showMessage(message = '', heading='Raketa-TV', times = 3000, pics = addon_icon):
    try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading.encode('utf-8'), message.encode('utf-8'), times, pics.encode('utf-8')))
    except Exception, e:
        xbmc.log( '[%s]: showMessage: Transcoding UTF-8 failed [%s]' % (addon_id, e), 2 )
        try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, pics))
        except Exception, e:
            xbmc.log( '[%s]: showMessage: exec failed [%s]' % (addon_id, e), 3 )

def GetCookie(target, post=None):
    try:
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(opener)
        resp1 = urllib2.urlopen('http://raketa-tv.com/connect')
        http1=resp1.read()
        resp1.close()
        #print http1
        beautifulSoup = BeautifulSoup(http1)
        channels=beautifulSoup.findAll('input', attrs={'type': 'hidden'})
        ct=""
        for ch in channels:
            ct=ch['value']
        post = urllib.urlencode({
            '_csrf_token' : ct,
            '_username' : login,
            '_password' : passw,
            '_remember_me' : 'on',
            '_submit' : '%D0%92%D0%BE%D0%B9%D1%82%D0%B8'
        })
        #print "target---- "+target
        req = urllib2.Request(url = target, data = post)
        req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
        resp = urllib2.urlopen(req)
        #print "ct4--- "+str(ct)
        http=resp.read()
        #req1 = urllib2.Request(url = 'http://raketa-tv.com/watch', data = post)
        #req1.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
        #resp1 = urllib2.urlopen('http://raketa-tv.com/watch')
        #print http
        if not http.find('Вход') > 1:
            showMessage('Raketa TV', 'Успешная авторизация', 10000)
            for cookie in cj:
                cookie=cookie.value
                resp.close()
                return cookie
        else: showMessage('Raketa TV', 'ОШИБКА авторизации', 10000)
    except Exception, e:
        xbmc.log( '[%s]: GET COOKIE EXCEPT [%s]' % (addon_id, e), 4 )
        showMessage('HTTP ERROR: '+str(target), e, 5000)

def UpdCookie():
    if not os.path.exists(PLUGIN_DATA_PATH):
        os.makedirs(PLUGIN_DATA_PATH)
    if os.path.exists(cookiefile):
        os.remove(cookiefile)
    out = open(cookiefile, 'w')
    co = GetCookie('https://raketa-tv.com/login_check', None)
    if co == None:
        showMessage('Raketa TV', 'Ошибка подключения')
        return None
    else:
        cookie = co
    try:
        out.write(cookie)
        out.close()
        return cookie
    except:
        showMessage('Raketa TV', 'Ошибка подключения')
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
"1+1": "620",
"1+1 Украина": "620",
"2+2 Украина": "583",
"2+2": "583",
"24 Док": "16",
"24 ДОК": "16",
"24 Техно": "710",
"24 ТЕХНО": "710",
"2x2": "323",
"365 Дней": "250",
"365 дней": "250",
"5 канал (Украина)": "586",
"5 канал Украина": "586",
"8 канал": "217",
"Amazing Life": "658",
"Animal Planet": "365",
"Animal Planet HD": "990",
"A-One": "680",
"A-ONE UA": "680",
"AXN Sci-Fi": "516",
"BBC World News": "828",
"Bridge TV": "151",
"Cartoon Network": "601",
"CBS Drama": "911",
"CBS Reality": "912",
"Zone Reality": "912",
"Comedy TV": "51",
"C Music": "319",
"Da Vinci Learning": "410",
"DIVA Universal Russia": "713",
"Diva Universal": "713",
"Dobro TV": "937",
"Discovery Channel": "325",
"Discovery Science": "409",
"Discovery World": "437",
"Investigation Discovery Europe": "19",
"ID Investigation Discovery": "19",
"Discovery HD Showcase": "111",
"Discowery HD Showcase": "111",
"Discovery Showcase HD": "111",
"Disney Channel": "150",
"English Club TV": "757",
"Enter Film": "281",
"Enter-фильм": "281",
"EuroNews": "23",
"Euronews": "23",
"Europa Plus TV": "681",
"Eurosport": "737",
"Eurosport 2": "850",
"Eurosport 2 HD": "850",
"Eurosport HD": "560",
"Extreme Sports": "288",
"Fashion TV": "661",
"Fashion TV HD": "121",
"Fashion HD": "121",
"Fashion One HD": "919",
"Fashion One": "919",
"Fox": "659",
"FOX": "659",
"FOX HD": "659",
"Fox HD": "659",
"Fox Life": "615",
"FOX Life": "615",
"FOX life HD": "464",
"France 24": "187",
"France24": "187",
"Galaxy TV": "924",
"Gulli": "810",
"HD Life": "415",
"HD Спорт": "429",
"HD Sport": "429",
"ICTV": "709",
"ICTV Украина": "709",
"JimJam": "494",
"Kids co": "598",
"Maxxi-TV": "228",
"Maxxi TV": "228",
"MCM Top": "533",
"MGM": "608",
"MGM HD": "934",
"Mezzo": "575",
"Motor TV": "531",
"Motors TV": "531",
"Motors Tv": "531",
"MTV Dance": "332",
"MTV Hits UK": "849",
"MTV Rocks": "388",
"MTV Russia": "557",
"MTV live HD": "382",
"MTV Live HD": "382",
"Music Box UA": "25",
"Music Box": "642",
"Russian Music Box": "25",
"myZen.tv HD": "141",
"Nat Geo Wild": "807",
"Nat Geo Wild HD": "807",
"National Geographic": "102",
"National Geographic HD": "389",
"News One": "247",
"NEWS ONE": "247",
"Nick Jr.": "917",
"nick jr.": "917",
"Nickelodeon": "567",
"nickelodeon": "567",
"Nickelodeon HD": "423",
"nickelodeon HD": "423",
"Ocean-TV": "55",
"O-TV": "167",
"OTV": "167",
"Outdoor HD": "322",
"Paramount Comedy": "920",
"QTV": "280",
"RTVi": "76",
"RTVі": "76",
"RU TV": "258",
"Rusong TV": "591",
"Russian Travel Guide": "648",
"SET": "311",
"SET HD": "311",
"S.E.T": "311",
"Sony Turbo": "935",
"sony turbo": "935",
"SONY Sci-Fi": "516",
"Sony Sci-Fi": "516",
"Smile of Child": "789",
"Улыбка Ребенка": "789",
"STV": "165",
"Style TV": "119",
"Style tv": "119",
"TiJi": "555",
"TLC": "425",
"Tonis": "627",
"Tonis Украина": "627",
"TVCI": "435",
"TV 1000": "127",
"TV 1000 Action East": "125",
"TV 1000 Action": "125",
"TV 1000 Русское кино": "267",
"TV 1000 Русское Кино": "267",
"TV XXI (TV21)": "309",
"XXI": "309",
"Ukrainian Fashion": "939",
"Universal Channel": "213",
"VH1": "491",
"VH 1": "491",
"VH1 Classic": "156",
"VH 1 Classic": "156",
"Viasat Explorer": "521",
"Viasat History": "277",
"Viasat Nature East": "765",
"Viasat Nature": "765",
"Viasat Sport": "455",
"World Fashion": "346",
"World Fashion Channel": "346",
"Zee TV": "626",
"Zoo TV": "273",
"Zoom": "1009",
"Авто плюс": "153",
"Авто Плюс": "153",
"Агро тв": "11",
"Амедиа": "918",
"Астро ТВ": "249",
"Астро": "249",
"Беларусь 24": "851",
"Боец": "454",
"Бойцовский клуб": "986",
"Вопросы и ответы": "333",
"Время": "669",
"Детский": "66",
"Детский мир": "747",
"Детский мир/Телеклуб": "747",
"Дождь": "384",
"Дождь HD": "384",
"Дом кино": "834",
"Дом Кино": "834",
"Домашние животные": "520",
"Домашний": "304",
"Драйв ТВ": "505",
"Еврокино": "352",
"ЕДА": "931",
"ЕДА HD": "930",
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
"Здоровое телевидение": "595",
"Зоо ТВ": "273",
"Зоопарк": "367",
"Zоопарк": "367",
"Иллюзион+": "123",
"Индия": "798",
"Индия ТВ": "798",
"Интер": "677",
"Интер Украина": "677",
"Интер+": "808",
"Интер Плюс Украина": "808",
"Интересное ТВ": "24",
"К1": "453",
"K 1 Украина": "453",
"K1 Украина": "453",
"Карусель": "740",
"Кинопоказ": "22",
"Комедия ТВ": "821",
"Кто есть кто": "769",
"Кухня ТВ": "614",
"КХЛ ТВ": "481",
"КХЛ": "481",
"КХЛ HD": "481",
"Ля-минор": "257",
"М1": "632",
"Мега": "788",
"Мир": "726",
"Мир сериала": "145",
"Много ТВ": "799",
"МногоTV": "799",
"Моя планета": "675",
"Моя Планета": "675",
"Москва 24": "334",
"Москва Доверие": "655",
"Москва доверие": "655",
"Музыка Первого": "715",
"Мужской": "82",
"Мать и дитя": "618",
"Мать и Дитя": "618",
"Мультимания": "31",
"Нано ТВ": "35",
"Наука 2.0": "723",
"Наше любимое кино": "477",
"Новый канал": "128",
"Новый канал Украина": "128",
"Ностальгия": "783",
"НСТ": "518",
"НТВ": "162",
"НТВ Мир": "422",
"НТВ+ Кино плюс": "644",
"Кино Плюс": "644",
"НТВ+ Киноклуб": "462",
"Киноклуб": "462",
"НТВ+ Кинолюкс": "8",
"НТВ Кинолюкс": "8",
"НТВ+ Киносоюз": "71",
"Кино Cоюз": "71",
"НТВ+ Кинохит": "542",
"Кинохит": "542",
"НТВ+ Наше кино": "12",
"Наше Кино": "12",
"НТВ+ Наше новое кино": "485",
"Новое Кино": "485",
"НТВ+ Премьера": "566",
"Премьера": "566",
"НТВ+ Баскетбол": "697",
"Баскетбол": "697",
"НТВ+ Наш футбол": "499",
"Наш Футбол": "499",
"НТВ+ Спорт": "134",
"НТВ+ Спорт Онлайн": "183",
"Спорт Онлайн": "183",
"НТВ+ Спорт Союз": "306",
"Спорт Союз": "306",
"НТВ+ Спорт плюс": "377",
"Спорт плюс": "377",
"НТВ+ Теннис": "358",
"Теннис": "358",
"НТВ+ Футбол": "664",
"НТВ+ Футбол 2": "563",
"Футбол 2": "563",
"НТВ+ Футбол HD": "664",
"Футбол HD": "664",
"НТВ+ Футбол 2 HD": "563",
"Футбол 2 HD": "563",
"НТН (Украина)": "140",
"НТН": "140",
"О2ТВ": "777",
"О2 ТВ": "777",
"Оружие": "376",
"Охота и рыбалка": "617",
"Охота и Рыбалка": "617",
"Охотник и рыболов": "132",
"Парк развлечений": "37",
"Парк Развлечений": "37",
"Первый автомобильный (укр)": "507",
"Первый автомобильный": "507",
"Первый деловой": "85",
"Первый канал": "146",
"Первый канал (Европа)": "391",
"Первый канал (СНГ)": "391",
"Первый канал HD": "983",
"Первый национальный (Украина)": "773",
"Первый Украина": "773",
"Первый образовательный": "774",
"Перец": "511",
"Пиксель ТВ": "940",
"Пиксель ТВ Украина": "940",
"Пиксель Украина": "940",
"Подмосковье": "161",
"Про все": "458",
"Просвещение": "685",
"Психология 21": "434",
"Пятница": "1003",
"Пятый канал": "427",
"Пятый Канал": "427",
"Раз ТВ": "363",
"РАЗ ТВ": "363",
"РБК": "743",
"РЕН ТВ": "689",
"Рен ТВ": "689",
"РЖД": "509",
"Ретро ТВ": "6",
"Рэтро ТВ": "6",
"Россия 1": "711",
"Россия": "711",
"Россия 2": "515",
"Россия 24": "291",
"Россия К": "187",
"Россия Культура": "187",
"РОССИЯ HD": "984",
"Россия HD": "984",
"РТР-Планета": "143",
"Русский иллюзион": "53",
"Русский Иллюзион": "53",
"Русский роман": "401",
"Русский экстрим": "406",
"Русский Экстрим": "406",
"Сарафан ТВ": "663",
"Сарафан": "663",
"Спас": "447",
"Спас ТВ": "447",
"СПОРТ": "154",
#"Спорт": "134",
"Спорт 1": "181",
"Спорт 1 Россия": "181",
"Спорт 1 HD": "554",
"Совершенно секретно": "275",
"Совершенно Секретно": "275",
"Союз": "349",
"СТБ": "670",
"СТБ Украина": "670",
"СТС": "79",
"Страна": "284",
"ТБН": "576",
"ТДК": "776",
"ТВ 3": "698",
"ТВ-3": "698",
"TBi": "650",
"ТВі Украина": "650",
"ТВЦ": "649",
"ТВ Центр": "649",
"ТНТ": "353",
"Тонус ТВ": "637",
"Тонус-ТВ": "637",
"Телекафе": "173",
"Телепутешествия": "794",
"Телепутешествия HD": "331",
"ТЕТ": "479",
"ТЕТ Украина": "479",
"ТРК Украина": "326",
"Украина": "326",
"ТРО Союза": "730",
"ТРО": "730",
"Успех": "547",
"Усадьба": "779",
"Феникс+ Кино": "686",
"Феникс Кино Плюс": "686",
"Футбол": "328",
"Телеканал Футбол": "328",
"Футбол (украина)": "666",
"Футбол+ (украина)": "753",
"Футбол Украина": "666",
"Футбол+ Украина": "753",
"Хокей": "702",
"Хоккей Украина": "702",
"ЧП-Инфо": "315",
"Шансон ТВ": "662",
"Ю": "898",
"ю": "898",
"Юмор ТВ": "412",
"Юмор тв": "412",
"Юмор BOX": "412",
"Эгоист ТВ": "431",
"TV 1000 Megahit HD": "816vsetv",
"TV 1000 Premium HD": "814vsetv",
"TV 1000 Comedy HD": "818vsetv",
"Малятко TV Украина": "606vsetv",
"Моя дитина": "761vsetv",
"Плюс Плюс Украина": "24vsetv",
"A-ONE UA Украина": "772vsetv",
"RU MUSIC": "388vsetv",
"Star TV Ukraine": "513vsetv",
"STAR TV Украина": "513vsetv",
"М2": "445vsetv",
"Муз ТВ": "808vsetv",
"NBA TV": "790vsetv",
"Спорт 1 Украина": "270vsetv",
"Спорт 2 Украина": "309vsetv",
"Гамма": "479vsetv",
"K 2 Украина": "20vsetv",
"КРТ": "149vsetv",
"Культура Украина": "285vsetv",
"УТР": "689vsetv",
"Унiан": "740vsetv",
"Travel Channel": "88vsetv",
"Travel Channel HD": "690vsetv",
"Travel Adventure": "832vsetv",
"TravelAdventure": "832vsetv",
"Право ТВ": "861vsetv",
"Эко-ТВ": "685vsetv",
"24 Украина": "298vsetv",
"Business": "386vsetv",
"CNN International": "47vsetv",
"Погода ТВ": "759vsetv",
"Рада Украина": "823vsetv",
"Real Estate-TV": "481vsetv",
"SHOPping-TV (Ukraine)": "810vsetv",
"Teen TV": "448vsetv",
"Ukrainian Fashion": "773vsetv",
"ВТВ": "139vsetv",
"Меню ТВ": "348vsetv",
"НЛО ТВ": "843vsetv",
"Daring TV": "696vsetv",
"Hustler TV": "666vsetv",
"Playboy TV": "663vsetv",
"Private Spice": "143vsetv",
"XXL": "664vsetv",
"Искушение": "754vsetv",
"Ночной клуб": "455vsetv",
"Русская ночь": "296vsetv",
"Глас": "294vsetv",
"100ТВ": "382vsetv",
"БСТ": "272vsetv",
"GLAS": "457vsetv",
"Израиль плюс": "532vsetv",
"ОНТ Украина": "111vsetv",
"ТРК Киев": "75vsetv",
"ab moteurs": "127vsetv",
"Look TV": "726vsetv",
"Сонце": "874vsetv",
"ТНТ Bravo Молдова": "737vsetv",
"тнт+4": "557vsetv",
"VIASAT Sport Baltic": "504vsetv",
"Гумор ТБ": "505vsetv",
"Открытый Мир": "692vsetv",
"100 ТВ": "382vsetv",
"100ТВ": "382vsetv",
"Viasat Nature HD \ History HD": "716vsetv",
"MTV Ukraina": "353vsetv",
"MTV Ukraine": "353vsetv",
}

#####################################       
def GetChannelsDB (params):
#########################
    try:
        #print "ttv импорт YaTv"
        import YaTv
        #print "ttv запрос программы"
        #d=YaTv.GetPr()
    except: pass
#########################
    db = DataBase(db_name, cookie='')
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
        li.setInfo(type = "Video", infoLabels = {"Title": ch['name'], 'year': endTime.tm_year, 'genre': genre, 'plot': prog} )
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
    del db

    
def DelChannel(params):
    db = DataBase(db_name, cookie='')
    db.DelChannel(params['id'])
    showMessage(message = 'Канал удален')
    xbmc.executebuiltin("Container.Refresh")
    del db

def FavouriteChannel(params):
    db = DataBase(db_name, cookie='')
    db.FavouriteChannel(params['id'])
    showMessage(message = 'Канал добавлен')
    xbmc.executebuiltin("Container.Refresh")
    del db
    
def DelFavouriteChannel(params):
    db = DataBase(db_name, cookie='')
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

def play_ch_db(params):
    xbmc.executebuiltin('Action(Stop)')
    url = ''
    if params['file'] == '':
        db = DataBase(db_name, cookie='')
        url = db.GetUrlsStream(params['id'])
        if url.__len__() == 0:
            showMessage('Ошибка получения ссылки')
            return
    else:
        url = params['file']
    if url != '':
        TSPlayer = tsengine()
        out = None
        if url.find('http://') == -1:
            out = TSPlayer.load_torrent(url,'PID',port=aceport)
        else:
            out = TSPlayer.load_torrent(url,'TORRENT',port=aceport)
        if out == 'Ok':
            TSPlayer.play_url_ind(0,params['title'],addon_icon,params['img'])
            db = DataBase(db_name, cookie='')
            db.IncChannel(params['id'])
            del db
            TSPlayer.end()
            xbmc.executebuiltin('Container.Refresh')
            #showMessage('Torrent', 'Stop')
            return
        #else:
            #TSPlayer.end()
            #url = ''
            #if params['file'] == '':
            #db = DataBase(db_name, cookie='')
            #showMessage('Torrent', 'Обновление торрент-ссылки')
            #url = db.UpdateUrlsStream([params['id']])
            #newlink = UpdateChannelsDB(params['id'])
            #print 'newlink---'+str(newlink)
            #pos = xbmc.getInfoLabel('Container.Position')
            #print 'pos---'+str(pos)
            #xbmc.executebuiltin('Container.Refresh')
            #return
            #xbmcgui.ListItem.
            #print 'UpdateChannelsDB----' + str(url[0]['urlstream'])
            #if url.__len__() == 0:
                #showMessage('Ошибка получения ссылки')
                #return
            #url = url[0]['urlstream']
            #print 'url---'+str(url)
                #del db
            #else:
                #url = params['file']
                #showMessage('Torrent', 'Обновление торрент-ссылки')
                #time.sleep(20)
            #if url != '':
                #TSPlayer = tsengine()
                #out = None
                #if url.find('http://') == -1:
                    #print 'TS PID---'+str(url)
                    #out = TSPlayer.load_torrent(url,'PID',port=aceport)
                    #print 'OUT PID---'+str(out)
                #else:
                    #print 'TS TORRENT'
                    #out = TSPlayer.load_torrent(url,'TORRENT',port=aceport)
                #if out == 'Ok':
                    #print 'TS OK'
                    #TSPlayer.play_url_ind(0,params['title'],addon_icon,params['img'])
                    #db = DataBase(db_name, cookie='')
                    #if __addon__.getSetting('count') == 'false':
                    #db.IncChannel(params['id'])
                    #del db
                    #TSPlayer.end()
                    #showMessage('Torrent', 'Stop')
                    #return
  

def GetParts():
    db = DataBase(db_name, cookie='')
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
    db = DataBase(db_name, cookie)
    showMessage('Raketa TV', 'Производится обновление плейлиста')
    db = DataBase(db_name, cookie='')
    db.UpdateDB()
    xbmc.executebuiltin('Container.Refresh')
    showMessage('Raketa TV', 'Обновление плейлиста выполнено')
    del db

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
    li.addContextMenuItems(commands, True)
    uri = construct_request({
        'func': 'GetChannelsDB',
        'title': 'Все каналы',
        'group': '0'
    })
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    li = xbmcgui.ListItem('[COLOR FF00FF00]Последние просмотренные[/COLOR]')
    li.addContextMenuItems(commands, True)
    uri = construct_request({
        'func': 'GetChannelsDB',
        'title': 'Последние просмотренные',
        'group': 'latest'
    })
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    li = xbmcgui.ListItem('[COLOR FF00FF00]HD Каналы[/COLOR]')
    li.addContextMenuItems(commands, True)
    uri = construct_request({
        'func': 'GetChannelsDB',
        'title': 'HD Каналы',
        'group': 'hd'
    })
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    li = xbmcgui.ListItem('[COLOR FF00FF00]Новые каналы[/COLOR]')
    li.addContextMenuItems(commands, True)
    uri = construct_request({
        'func': 'GetChannelsDB',
        'title': 'Новые каналы',
        'group': 'new'
    })
    xbmcplugin.addDirectoryItem(hos, uri, li, True)
    GetParts()
    xbmcplugin.endOfDirectory(hos)
    
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
            showMessage('Raketa TV', 'Производится обновление плейлиста')
            db = DataBase(db_name, cookie='')
            db.UpdateDB()
            showMessage('Raketa TV', 'Обновление плейлиста выполнено')
        else:
            nupd = lupd + datetime.timedelta(hours = 7)

            if nupd < datetime.datetime.now():
                showMessage('Raketa TV', 'Производится обновление плейлиста')
                db = DataBase(db_name, cookie='')
                db.UpdateDB()
                showMessage('Raketa TV', 'Обновление плейлиста выполнено')
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
