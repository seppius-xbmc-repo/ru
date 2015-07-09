# -*- coding: utf-8 -*-
##########################################################################
#
# Copyright (C) 2015 Studio-Evolution
#
# Library to work with MEGOGO.NET api for XBMC
#
#############################################################################

import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import simplejson, requests
import urllib, time, urllib2, hashlib, os, re, base64, platform, datetime
from sqlite import DataBase as DB
from Utils import get_quality, get_language, get_subtitle, get_ui_language

try:
    import requests.packages.urllib3 as urllib3
    urllib3.disable_warnings()
except:
    pass

addon 			= xbmcaddon.Addon()
language		= addon.getLocalizedString
addon_path		= addon.getAddonInfo('path').decode('utf-8')
addon_id		= addon.getAddonInfo('id')
addon_author	= addon.getAddonInfo('author')
addon_name		= addon.getAddonInfo('name')
addon_version	= addon.getAddonInfo('version')
unknown_person	= os.path.join(addon_path, 'resources', 'skins', 'Default', 'media', 'unknown_person.png')
platform_version    = xbmc.getInfoLabel('System.BuildVersion').split(" ")[0]
if int(platform_version.split(".")[0]) >= 14:
    name = 'Kodi'
else:
    name = 'Xbmc'

API_Private_Key_MEGOGO  = '63ee38849d'
API_Public_Key_MEGOGO   = '_kodi_j1'
API_URL                 = 'https://api.megogo.net/v1'
MEGOGO_URL              = 'http://megogo.net'
PAY_URL                 = 'https://megogo.net/%s/billing/payu' % get_ui_language()
PAY_VENDOR              = 'kodi-device'
try:
    UA                  = '%s/%s-%s' % (name, platform_version, platform.platform(aliased=0, terse=0)[:40])
except:
    data                = os.uname()
    UA                  = '%s/%s-%s-%s-%s' % (name, platform_version, data[0], data[2], data[-1])
    UA                  = UA[:50]

xbmc.log('[%s]: UA - %s' % (addon_name, UA))

slider_images_resolution = ['image_1920x300', 'image_1600x520', 'image_1350x510']

a = DB()

# Function to get cached JSON response from db or 
# set response from MEGOGO to db
def Get_JSON_response(url, cache_days=7):
    xbmc.log('[%s]: Trying to get %s' % (addon_name, url))
    now = time.time()
    # Language correction
    if url.find('lang=') == -1:
        if url.find('?') > 0:
            url = "%s&lang=%s" % (url, get_ui_language())
        else:
            url = "%s?lang=%s" % (url, get_ui_language())

    hashed_url = hashlib.md5(url).hexdigest()
    cache_seconds = int(cache_days * 86400)
    response = a.get_page_from_db(hashed_url, cache_seconds)
    # xbmc.log('[%s]: JSON response - %s' % (addon_name, response.encode('utf-8')))
    if not response:
        xbmc.log("[%s]: %s is not in cache, trying download data" % (addon_name, url))
        response = GET(url)
        try:
            result = simplejson.loads(response)
            xbmc.log("[%s]: %s download in %f seconds" % (addon_name, url, time.time() - now))
            a.set_page_to_db(hashed_url, int(time.time()), response)
        except Exception as e:
            xbmc.log("[%s]: Get_JSON_response ERROR! Response - %s.\n %s" % (addon_name, response, e))
            result = {'result': 'error'}
    else:
        result = simplejson.loads(response)
        xbmc.log("[%s]: %s loaded from cache in %f seconds" % (addon_name, url, time.time() - now))

    #xbmc.log('[%s]: JSON responce - %s' % (addon_name, result))
    return result


# Function for sending GET requsts to megogo.net
# req_p1 used for keeping urlencoded parameters
# req_p2 used for keeping md5-sign of parameters+API_Public_Key_MEGOGO, that send in end of each request 
def GET(url, old_url=None, login=False, post=False, post_data=None):
    try:
        dicParams = {}
        linkParams = []
        hashParams = []
        dic = a.get_login_from_db()
        if dic['cookie']:
            cookie = simplejson.loads(base64.b64decode(dic['cookie']))
        else:
            cookie = None
        usr = dic['login']
        pwd = dic['password']

        # Language correction
        if url.find('lang=') == -1 and not post and not url.startswith('auth/') and not url.startswith('search'):
            if url.find('?') > 0:
                url = "%s&lang=%s" % (url, get_ui_language())
            else:
                url = "%s?lang=%s" % (url, get_ui_language())

        page, _, params = url.partition('?')

        if params:
            params = params.split('&')
            for param in params:
                key, _, value = param.partition('=')
                dicParams[key] = value

            for keys in dicParams:
                linkParams.append('%s=%s' % (keys, urllib.quote_plus(dicParams[keys])))
                hashParams.append('%s=%s' % (keys, dicParams[keys]))

            linkParams = '&'.join(reversed(linkParams))
            hashParams = ''.join(reversed(hashParams))
        else:
            hashParams = ''
            linkParams = ''

        m = hashlib.md5()
        m.update('%s%s'%(hashParams, API_Private_Key_MEGOGO))
        if not post:
            target = '%s/%s?%s&sign=%s' % (API_URL, page, linkParams, '%s%s' % (m.hexdigest(), API_Public_Key_MEGOGO))
        else:
            target = '%s/%s?%s&sign=%s' % (PAY_URL, page, linkParams, '%s%s' % (m.hexdigest(), API_Public_Key_MEGOGO))

        xbmc.log('[%s]: GET Target:\n%s' % (addon_name, target))
        # xbmc.log('[%s]: GET\nUSR - %s\nPASS - %s\nCookie - %s\nTarget - %s' % (addon_name, usr, pwd, cookie, target))

        if cookie and not old_url and not post:
            request = requests.get(target, cookies=cookie, headers={'User-Agent': UA}, timeout=8)
            # xbmc.log('[%s]: GET cookie and not old_url, request - %s' % (addon_name, request))
            http = request.text
            # xbmc.log('[%s]: GET cookie and not old_url, http - %s' % (addon_name, http.encode('utf-8')))
            return http.encode('utf-8')

        # log in account in megogo.net
        elif usr and pwd and login and not post:
            # xbmc.log('[%s]: GET elif usr and pwd and login, url - %s' % (addon_name, url))
            if not url.startswith('auth/login?login='):
                GET('auth/login?login=%s&password=%s&remember=1' % (usr, pwd), old_url=url, login=True)
            else:
                session = requests.session()
                request = session.get(target, headers={'User-Agent': UA}, timeout=8)
                http = request.text
                if http.startswith('{"result":"ok"'):
                    cookies = requests.utils.dict_from_cookiejar(session.cookies)
                    # xbmc.log('[%s]: NEW COOKIE - %s' % (addon_name, cookies))
                    a.cookie_to_db(base64.b64encode(str(cookies).replace("'", '"')))
                    if old_url:
                        # xbmc.log('[%s]: GET elif usr and pwd, old_url - %s' % (addon_name, old_url))
                        GET(old_url)
                    else:
                        # xbmc.log('[%s]: return GET elif usr and pwd, http - %s' % (addon_name, http.encode('utf-8')))
                        return http.encode('utf-8')
                else:
                    return None

        else:
            if post_data:
                post_data = urllib.urlencode(post_data)
            request = urllib2.Request(url=target, data=post_data, headers={'User-Agent': UA})
            request = urllib2.urlopen(request)
            http = request.read()
            request.close()
            # xbmc.log('[%s]: GET else, http - %s' % (addon_name, http))
            return http

    except Exception as e:
        xbmc.log('[%s]: Cannot get data from %s.\n%s' % (addon_name, target, e))
        return None


def checkLogin(update=False):
    dic = a.get_login_from_db()
    if dic['cookie'] and not update:
        xbmc.log('[%s]: Log in success!' % (addon_name))
        return True
    else:
        if dic['login'] and dic['password']:
            answer = log_in(dic['login'], dic['password'])
            if answer:
                a.update_account_in_db('user_id', answer["user_id"])
                a.update_account_in_db('card_num', answer["credit_card"])
                a.update_account_in_db('card_type', answer["card_type"])
                return True
            else:
                return False
        else:
            xbmc.log('[%s]: Cannot log in account! login and pass EMPTY.' % addon_name)
            return False


def log_in(usr, pwd):
    xbmc.log('[%s]: Try to log in!' % addon_name)
    data = GET('auth/login?login=%s&password=%s&remember=1' % (usr, pwd), login=True)
    if data:
        result = simplejson.loads(data)
        if result['result'] == 'ok':
            return result["data"]
        else:
            return None
    else:
        xbmc.log('[%s]: Cannot log in account! Error retrieving data.' % addon_name)
        return None


# Registration new user on MEGOGO
def registerUser(usr, nick, pwd):
    xbmc.log('[%s]: Try to register new user!' % addon_name)
    data = GET('auth/register?email=%s&nickname=%s&password=%s&agree=1' % (usr, nick, pwd))
    if data:
        result = simplejson.loads(data)
        if result['result'] == 'ok':
            return {'answer': 'success'}
        elif result['result'] == 'error':
            if len(result['message']) > 0:
                errors = [result['message']]
            else:
                errors = []
            for error in result['errors']:
                errors.append('%s: %s' % (error, result['errors'][error]))
            return {'answer': 'error', 'message': errors}
        else:
            return None
    else:
        return None


# Clear user, password and session_id from addon settings
def logout():
    dic = a.get_login_from_db()
    if dic['login'] and dic['password']:
        GET('auth/logout?')
    a.clear_table('account')
    addon.setSetting('login', '')
    addon.setSetting('password', '')


def HandleMainPage(responce, types=None):
    info = []
    if types:
        array = responce[types]
    else:
        array = responce
    for item in array:
        info.append(HandleVideoResult(item))
    return info


def HandleTVPackeges(responce, types):
    arrays = []

    array = responce[types]
    for dictionary in array:
        info = []
        for channel in dictionary['channels']:
            # xbmc.log('!channel!\ntype - %s\n%s' % (type(channel), channel))
            info.append(HandleVideoResult(channel))
        arrays.append({'title': dictionary['title'], 'channels': info})
    return arrays


# Function that get information about video-file from json-answer
def HandleVideoResult(item):
    try: video = item['video']
    except: video = item

    try: title = video['title']
    except:
        try: title = item['title']
        except: title = ''

    try: vid = video['object_id']
    except: vid = video['id']

    try:
        if video["slider_type"] == "feature":
            video_type = 'collection'
        elif video["slider_type"] == "object":
            video_type = 'video'
        elif video["slider_type"] == "tv_program":
            video_type = 'TV'
    except:
        video_type = 'video'

    try: original_title = video['title_original']
    except: original_title = ''

    try:
        poster = video['image']['big']
        if poster.count(':') > 1:
            poster = ':'.join(poster.split(':')[:-1])[:-1]+'2:'+poster.split(':')[-1]
    except: poster = ''

    try: country = video['country']
    except: country = ''

    try: year = video['year']
    except: year = ''

    try: description = video['description'].replace('<p>','').replace('</p>','').replace('<i>','').replace('</i>','').replace('\r\n\r\n','\r\n').replace('&#151;','-').replace('&raquo;','"').replace('&laquo;','"').replace('<BR>','').replace('<br>','')
    except: description = ''

    try: genre = a.get_genres_from_db(video['genres'])
    except:
        try: genre = item["tv_program"]["genre"]["title"]
        except: genre = ''

    try: category = a.get_category_from_db(video['categories'])
    except:
        try: category = item["tv_program"]["category"]["title"]
        except: category = ''

    try: delivery = ', '.join(video['delivery_rules'])
    except: delivery = ''

    for resolution in slider_images_resolution:
        try: image = item[resolution]
        except: image = None
        if image and image!='':
            poster = image
            break

    try: poster = item["image"]["image_vertical"]
    except: pass

    try: rating = "%.2f" % float(item['rating_kinopoisk'])
    except: rating = ''

    try: rating_imdb = "%.2f" % float(item['rating_imdb'])
    except: rating_imdb = ''

    try: age_limit = item['age_limit']
    except: age_limit = ''

    try: like = item['like']
    except: like = ''

    try: dislike = item['dislike']
    except: dislike = ''

    try: duration = int(item['duration'] / 60)
    except: duration = ''

    try: crew = a.crew_info(item['people'])
    except: crew = ''

    try: favourite = item['is_favorite']
    except: favourite = None

    try: vote = item['vote']
    except: vote = ''

    try: quality = item['quality']
    except: quality = ''

    try: season_list = item['season_list']
    except: season_list = None

    try: available = item['is_available']
    except: available = False

    try: recommended_videos = item["recommended_videos"]
    except: recommended_videos = []

    try: exclusive = '%s' % item["is_exclusive"]
    except: exclusive = 'false'

    try: series = '%s' % item["is_series"]
    except: series = 'false'

    try: promo = item["is_promocode"]
    except: promo = False

    try: purchase = ', '.join(str(x) for x in item["tv_channel"]["purchase_info"]["svod"]["subscriptions"])
    except:
        try: purchase = ', '.join(str(x) for x in item["purchase_info"]["svod"]["subscriptions"])
        except:
            try: purchase = item["purchase_info"]
            except: purchase = None

    try:
        channel_title = item["tv_channel"]["title"]
        channel_image = item["tv_channel"]["image"]["small"]
    except:
        channel_title = None
        channel_image = None

    try:
        start_time = datetime.datetime.fromtimestamp(item['tv_program']['start_timestamp']).strftime('%H:%M, %d.%m.%Y')
    except:
        start_time = None

    # xbmc.log('PURCHASE INFO: %s' % purchase)

    locInfo = { 'title'			: title,
                'id'			: unicode(vid),
                'type'			: video_type,
                'originaltitle'	: original_title,
                'country'		: country,
                'year'			: year,
                'plot'			: description,
                'genre'			: genre,
                'categories'	: category,
                'poster'		: poster,
                'delivery_rules': delivery,
                'rating'		: rating,
                'imdb_rating'	: rating_imdb,
                'mpaa'			: age_limit,
                'like'			: unicode(like),
                'dislike'		: unicode(dislike),
                'duration'		: unicode(duration),
                'crew'			: crew,
                'favourite'		: favourite,
                'vote'			: vote,
                'quality'		: quality,
                'season_list'	: season_list,
                'available'		: available,
                'recommended'	: recommended_videos,
                'exclusive'		: exclusive,
                'series'		: series,
                'is_promocode'  : promo,
                'purchase_info' : purchase,
                'channel_title' : channel_title,
                'channel_image' : channel_image,
                'start_time'    : start_time
              }
    # xbmc.log('\n[%s]: HandleVideoResult parses data - %s' % (addon_name, locInfo))
    return locInfo


# Get configuration
def getconfiguration():
    xbmc.log('[%s]: Try to get configuration' % addon_name)
    data = GET('configuration')
    if data:
        try:
            # xbmc.log('data - %s' % data)
            data = simplejson.loads(data)
            if data['result'] == 'ok':
                a.set_genres_to_db(data['data']['genres'])
                a.set_categories_to_db(data['data']['categories'])
                a.set_member_types_to_db(data['data']['member_types'])
                a.set_support_telephone_to_db(data['data']['support_info']["phones"])
                xbmc.log('[%s]: Successful get configuration' % addon_name)
                return True
            else:
                return None
        except Exception as e:
            xbmc.log('[%s]: Getting configuration ERROR! %s' % (addon_name, e))
            return None
    else:
        return None


# Get tarifications
def gettarification():
    xbmc.log('[%s]: Try to get tarification' % addon_name)
    data = Get_JSON_response('subscription/info')
    if data['result'] == 'ok':
        xbmc.log('[%s]: Successful get tarification' % addon_name)
        return data['data']
    else:
        return None


# Get mounth price from tariff
def get_price(tarif):
    currency = None
    month_price = None
    if tarif == 'svod':
        title = 'M+'

    data = gettarification()
    if data:
        for arr in data:
            if arr['title'] == title:
                currency = arr['currency']
                month_price = arr['tariffs'][0]['price']
                break
        if currency and month_price:
            return "%s %s" % (month_price, currency)
        else:
            return None
    else:
        return None


# Get recommended materials
def main_page(force):
    if force:
        cache_days = 0
    else:
        cache_days = 0.5  # Cache main page on 12 hours
    data = Get_JSON_response('digest', cache_days)
    if data['result'] == 'ok':
        return data
    else:
        return None


# Get video data
def getvideodata(force, page, section):
    xbmc.log('[%s]: Try to get videodata' % addon_name)
    if force:
        cache = 0
    else:
        cache = 1
    if section == 'collection':
        data = Get_JSON_response('collection?id=%s' % page, cache_days=cache)
    else:
        data = Get_JSON_response('video/info?id=%s' % page, cache_days=cache)
    if data['result'] == 'ok':
        return data
    else:
        return None


# Get page
def get_page(force, page, offset=0):
    if offset != 0:
        url = '%s&offset=%d' % (page, offset)
    else:
        url = page
    if force:
        cache = 0
    else:
        cache = 1
    if page.startswith('search?'):
        data = GET(page)
        if data:
            data = simplejson.loads(data)
        else:
            return None
    else:
        data = Get_JSON_response(url, cache_days=cache)
    if data['result'] == 'ok':
        return data
    else:
        return None



# Get stream information about available bitrate, languages and subtitles
def data_from_stream(video_id):
    xbmc.log('[%s]: Try to get available configurations of stream' % addon_name)
    bitrates = []
    audios = []
    subtitles = []

    data = GET('stream?video_id=%s' % video_id)
    if data:
        # xbmc.log('DATA from stream!\n %s' % data)
        data = simplejson.loads(data)
        if data['result'] == 'ok':
            try:
                for bit in data['data']['bitrates']:
                    bitrates.append(bit['bitrate'])
            except:
                bitrates = None

            try:
                for audio in data['data']['audio_tracks']:
                    audios.append(audio['lang'])
            except:
                audios = None

            try:
                for subtitle in data['data']['subtitles']:
                    subtitles.append(subtitle['lang'])
            except:
                subtitles = None

            try:
                src = data['data']['src']
            except:
                src = None

            return {'bitrates': bitrates, 'audio': audios, 'subtitle': subtitles, 'link': src}
        else:
            return None
    else:
        return None


def get_stream(video_id):
    xbmc.log('[%s]: Try to get stream' % addon_name)
    account = a.get_login_from_db()
    preset_bitrate = get_quality(account['quality'])
    audio_lang = None
    preset_language = get_language(account['audio_language'])
    subtitle_lang = None
    preset_subtitle = get_subtitle(account['subtitle'])

    p = re.compile(ur'(\d+)')		# REGEXP TO GET VIDEO QUALITY FROM SETTINGS
    preset_bitrate = int(re.search(p, preset_bitrate).group(0))
    preset_language = preset_language[-3:-1]

    data = GET('stream?video_id=%s&bitrate=%s&lang=%s' % (video_id, preset_bitrate, preset_language))
    if data:
        result = simplejson.loads(data)
        if result['result'] == 'ok':
            if result['data']['is_wvdrm']:
                xbmc.log('[%s]: NEED TO DO DRM FOR THIS VIDEO (%s, %s)' % (addon_name, result['data']['title'], result['data']['id']))

            if not result['data']['is_tv']:
                for audio in result['data']['audio_tracks']:
                    if audio['lang'] == preset_language[-3:-1]:
                        audio_lang = audio['lang']
                        break
                    else:
                        audio_lang = None
                if not audio_lang:
                    try:
                        audio_lang = result['data']['audio_tracks'][0]['lang']
                        xbmc.log('[%s]: LANGUAGE IN MOVIE - %s' % (addon_name, audio_lang.encode('utf-8')))
                    except:
                        audio_lang = None

                xbmc.log('PRESET SUBTITLE! %s' % preset_subtitle.encode('utf-8'))
                if preset_subtitle.endswith(')'):
                    try:
                        for subtitle in result['data']['subtitles']:
                            if subtitle['lang'] == preset_subtitle[-3:-1]:
                                subtitle_lang = subtitle['url']
                                break
                            else:
                                subtitle_lang = None
                        if not subtitle_lang:
                            subtitle_lang = result['data']['subtitles'][0]['url']
                        xbmc.log('[%s]: SUBTITLE IN MOVIE - %s' % (addon_name, subtitle_lang.encode('utf-8')))
                    except:
                        subtitle_lang = None
                else:
                    subtitle_lang = None
                return {'src': result['data']['src'], 'audio': audio_lang, 'subtitle': subtitle_lang}
            else:   # IF TV
                return {'src': result['data']['src'], 'title': result['data']['title']}
        else:
            return None
    else:
        return None


# Get comments to video
def getcomments(video_id):
    data = Get_JSON_response('comment/list?video_id=%s' % video_id, cache_days=0.5)
    if data['result'] == 'ok':
        return data['data']['comments']
    else:
        return None


# Add video to favorites
def addFav(vid):
    data = Get_JSON_response('user/favorite/add?video_id=%s' % vid, cache_days=0)
    if data['result'] == 'ok':
        return True
    else:
        return False


# Delete video from favorites
def delFav(vid):
    data = Get_JSON_response('user/favorite/delete?video_id=%s' % vid, cache_days=0)
    if data['result'] == 'ok':
        return True
    else:
        return False


# Send certificate code
def send_certificate(certificate, vid, ptype, pay_id):
    if ptype == 'svod' or ptype == 'TV':
        link = 'payments/code?code=%s&video_id=%s&subscription_id=%s' % (certificate, vid, pay_id)
    elif ptype == 'tvod' or ptype == 'dto':
        link = 'payments/code?code=%s&video_id=%s&tariff_id=%s' % (certificate, vid, pay_id)
    else:
        return None

    data = Get_JSON_response(link, cache_days=0)
    # xbmc.log('CERTIFICATE RESULT! %s' % result)
    if data['result'] == 'ok':
        return {'message': data['data']['message'], 'code': data['data']['status_code']}
    else:
        return None



# PAY functions
def send_payrequest(card_data, token):
    if token:
        url = "order?pay_through_token=on"
    else:
        url = "order?pay_method=alu"

    # xbmc.log('CARD DATA %s - %s' % (type(card_data), card_data))

    xbmc.executebuiltin("ActivateWindow(busydialog)")
    data = GET(url, post=True, post_data=card_data)
    xbmc.executebuiltin("Dialog.Close(busydialog)")
    if data:
        result = simplejson.loads(data)
        if result['result'] == 'done':
            # xbmc.log('SUCCESS PAYMENT! %s' % data)
            if card_data['form[savecard]']:
                checkLogin(True)
            return {'answer': 'success', 'message': result['message']}
        elif result['result'] == 'error':
            errors = [result['message']]
            for error in result['errors']:
                errors.append(error['message'])
            return {'answer': 'error', 'message': errors}
        else:
            return None
    else:
        return None