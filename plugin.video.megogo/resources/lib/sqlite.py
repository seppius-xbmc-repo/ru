# -*- coding: utf-8 -*-
##########################################################################
#
# Copyright (C) 2015 Studio-Evolution
#
# Library to work with MEGOGO.NET api for XBMC
#
#############################################################################

import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import time, os, base64
import sqlite3 as db

addon 			= xbmcaddon.Addon()
addon_name		= addon.getAddonInfo('name')
language		= addon.getLocalizedString
addon_path		= addon.getAddonInfo('path').decode('utf-8')
addon_id		= addon.getAddonInfo('id')
db_name = os.path.join(addon_path, "resources", "requests.db")
unknown_person	= os.path.join(addon_path, 'resources', 'skins', 'Default', 'media', 'unknown_person.png')

MAX_DELAY = 2592000  # 30 days


class DataBase:

    def __init__(self):
        self.c = db.connect(database=db_name)
        self.cu = self.c.cursor()

    def close_db(self):
        self.c.close()

    # Check existing of table in db
    def table_exist(self, name):
        self.cu.execute("PRAGMA table_info(%s)" % name)
        if len(self.cu.fetchall()) > 0:
            return True
        else:
            return False

    # Clear table in db
    def clear_table(self, name):
        self.cu.execute("DELETE FROM %s" % name)
        self.cu.execute("VACUUM")
        self.c.commit()
        xbmc.log('[%s]: "%s" table was cleared' % (addon_name, name))

    # Function that get cached requests from DB when time is < cache_time
    def get_page_from_db(self, url, cache_seconds):
        xbmc.log('[%s]: trying get %s from db' % (addon_name, url))
        if self.table_exist('cache'):
            self.cu.execute("SELECT time FROM cache WHERE link = '%s'" % url)
            self.c.commit()
        else:
            self.cu.execute("CREATE TABLE cache (link, time int, data)")
            self.c.commit()

        try:
            time_in_db = self.cu.fetchone()[0]
        except:
            xbmc.log('[%s]: No records in db with link %s, return empty line' % (addon_name, url))
            return ''

        now = time.time()
        difference = int(now-time_in_db)
        xbmc.log('[%s]: time_in_db - %d; time now - %d; difference - %d' % (addon_name, time_in_db, now, difference))
        if difference > cache_seconds:
            self.cu.execute("DELETE FROM cache WHERE link = '%s'" % url)
            self.cu.execute("VACUUM")
            self.c.commit()
            xbmc.log('[%s]: Cached object in db is too old, deleting it. Return empty string.' % addon_name)
            return ''
        else:
            self.cu.execute("SELECT data FROM cache WHERE link = '%s'" % url)
            self.c.commit()
            info = self.cu.fetchone()[0]
            return info

    # Function that cached all requests to DB and delete all that older MAX_DELAY
    def set_page_to_db(self, url, timestamp, result):
        try:
            xbmc.log('[%s]: Try to delete old records' % addon_name)
            old_response = []
            for row in self.cu.execute('SELECT time FROM cache ORDER BY time'):
                time_in_db = row[0]
                delay = int(time.time()) - time_in_db
                if int(delay) > MAX_DELAY:
                    old_response.append(time_in_db)
            for dels in old_response:
                self.cu.execute("DELETE FROM cache WHERE time = '%s'" % dels)
                self.c.commit()
            if len(old_response) > 0:
                xbmc.log('[%s]: %d record(s) was deleted from db' % (addon_name, len(old_response)))
            else:
                xbmc.log('[%s]: No old records. Nothing to delete.' % addon_name)
        except:
            pass
        xbmc.log('[%s]: trying write %s to db' % (addon_name, url))
        if not self.table_exist('cache'):
            self.cu.execute("CREATE TABLE cache (link, time int, data)")
            self.c.commit()
            xbmc.log('[%s]: table "CACHE" was created' % addon_name)
        #try:
        self.cu.execute("INSERT INTO cache(link, time, data) VALUES (?, ?, ?)", (url, timestamp, unicode(result.decode('utf-8'))))
        self.c.commit()
        xbmc.log('[%s]: %s was writen to db' % (addon_name, url))
        #except:
        #    xbmc.log('[%s]: Cannot write data from %s to db' % (addon_name, url))

    # Write to db list of genres
    def set_genres_to_db(self, genres):
        if self.table_exist('genres'):
            self.clear_table('genres')
        else:
            self.cu.execute("CREATE TABLE genres (id int, title)")
            self.c.commit()
            xbmc.log('[%s]: table "GENRES" was created' % addon_name)

        if len(genres) != 0:
            for genre in genres:
                gId = genre['id']
                gName = genre['title']
                self.cu.execute("INSERT INTO genres(id, title) VALUES (?, ?)", (gId, gName))
            self.c.commit()
            xbmc.log('[%s]: %d new genres was writen to db' % (addon_name, len(genres)))

    # Get from db list of genres
    def get_genres_from_db(self, genre_list):
        genres = []
        for genre in genre_list:
            self.cu.execute("SELECT title FROM genres WHERE id = %d" % genre)
            try:
                var = self.cu.fetchone()[0]
            except:
                var = None
            if var:
                genres.append(var)
        return ', '.join(genres)

    # Write to db all categories
    def set_categories_to_db(self, categories):
        if self.table_exist('categories'):
            self.clear_table('categories')
        else:
            self.cu.execute("CREATE TABLE categories (id int, title, genres)")
            self.c.commit()
            xbmc.log('[%s]: table "CATEGORIES" was created' % addon_name)

        if len(categories) != 0:
            for category in categories:
                cId = category['id']
                cName = category['title']
                cGenres = ', '.join(str(x) for x in category['genres'])
                self.cu.execute("INSERT INTO categories(id, title, genres) VALUES (?, ?, ?)", (cId, cName, cGenres))
            self.c.commit()
            xbmc.log('[%s]: %d new categories was writen to db' % (addon_name, len(categories)))

    # Get from db list of categories
    def get_category_from_db(self, categories):
        categoris = []
        for category in categories:
            self.cu.execute("SELECT title FROM categories WHERE id = %d" % category)
            try:
                var = self.cu.fetchone()[0]
            except:
                var = None
            if var:
                categoris.append(var)
        return ', '.join(categoris)

    # Get from db id of category by name
    def get_category_from_db_by_name(self, name):
        self.cu.execute("SELECT id FROM categories WHERE title = %s" % name)
        try:
            var = self.cu.fetchone()[0]
        except:
            var = None
        return var

    # Write to db all MemberTypes
    def set_member_types_to_db(self, types):
        if self.table_exist('MemberTypes'):
            self.clear_table('MemberTypes')
        else:
            self.cu.execute("CREATE TABLE MemberTypes (type, title)")
            self.c.commit()
            xbmc.log('[%s]: table "MemberTypes" was created' % addon_name)

        if len(types) != 0:
            for memberType in types:
                mType = memberType['type']
                mName = memberType['title']
                self.cu.execute("INSERT INTO MemberTypes(type, title) VALUES (?, ?)", (mType, mName))
            self.c.commit()
            xbmc.log('[%s]: %d new MemberTypes was writen to db' % (addon_name, len(types)))

    # Get from db MemberType
    def get_member_types_from_db(self, typ):
        self.cu.execute("SELECT title FROM MemberTypes WHERE type = '%s'" % typ)
        try:
            var = self.cu.fetchone()[0]
        except:
            var = None
        if var:
            return var
        else:
            return ''

    # Write to db support telephones
    def set_support_telephone_to_db(self, phones):
        if self.table_exist('support'):
            self.clear_table('support')
        else:
            self.cu.execute("CREATE TABLE support (number)")
            self.c.commit()
            xbmc.log('[%s]: table "SUPPORT" was created' % addon_name)

        phone = ', '.join(phones)
        self.cu.execute("INSERT INTO support (number) VALUES (?)", (phone,))
        self.c.commit()
        xbmc.log('[%s]: %d new phones was writen to db' % (addon_name, len(phones)))

    # Get from db support telephones
    def get_support_telephone_from_db(self):
        self.cu.execute("SELECT number FROM support")
        try:
            var = self.cu.fetchone()[0]
            return var
        except:
            return None

    # Get crew information
    def crew_info(self, peoples):
        info = []
        for man in peoples:
            crew_id = man['id']
            crew_type = self.get_member_types_from_db(man['type'])
            try:
                crew_name = man['name']
            except:
                crew_name = None
            try:
                crew_origin_name = man['name_original']
            except:
                crew_origin_name = None
            try:
                picture = man['avatar']['image_360x360']
            except:
                picture = None
            if not picture:
                try:
                    picture = man['avatar']['image_240x240']
                except:
                    picture = unknown_person
            info.append({'id': crew_id, 'type': crew_type, 'name': crew_name, 'name_original': crew_origin_name, 'thumb': picture})
        self.c.commit()
        return info

    # Write login and password to DB
    def login_data_to_db(self, usr, pwd, qual, lang, subt):
        if self.table_exist('account'):
            self.clear_table('account')
        else:
            self.create_login_table()

        self.cu.execute("INSERT INTO account(id, login, password, quality, audio_language, subtitle) VALUES (1, ?, ?, ?, ?, ?)", (usr, base64.b64encode(pwd), qual, lang, subt))
        self.c.commit()
        xbmc.log('[%s]: account was writen to db' % addon_name)

    # Write cookies to DB
    def cookie_to_db(self, cookies):
        if self.table_exist('account'):
            self.cu.execute("UPDATE account SET cookie = '%s' WHERE id = 1" % cookies)
            self.c.commit()
            xbmc.log('[%s]: cookie was writen to db' % addon_name)

    # Update account in DB
    def update_account_in_db(self, field, data):
        if not self.table_exist('account'):
            self.create_login_table()
        else:
            if field == 'password':
                data = base64.b64encode(data)
            self.cu.execute("SELECT * FROM account")
            if len(self.cu.fetchall()) == 0:
                self.cu.execute("INSERT INTO account(id) VALUES (1)")
            self.cu.execute("UPDATE account SET %s = '%s' WHERE id = 1" % (field, data))
            self.c.commit()
            xbmc.log('[%s]: %s was updated in db' % (addon_name, field))

    # Get account from db
    def get_login_from_db(self):
        self.cu.execute("SELECT * FROM account")
        try:
            var = self.cu.fetchall()[0]
        except:
            var = None
        try:
            return {'login': var[1], 'password': base64.b64decode(var[2]), 'cookie': var[3], 'user_id': var[4],
                    'card_num': var[5], 'card_type': var[6], 'quality': var[7], 'audio_language': var[8], 'subtitle': var[9]}
        except:
            return {'login': '', 'password': '', 'cookie': '', 'user_id': '', 'card_num': '', 'card_type': '', 'quality':'', 'audio_language': '', 'subtitle': ''}

    # Create Table
    def create_login_table(self):
        self.cu.execute("CREATE TABLE account (id, login, password, cookie, user_id, card_num, card_type, quality, audio_language, subtitle)")
        self.c.commit()
        self.cu.execute("INSERT INTO account(id) VALUES (1)")
        self.c.commit()
        xbmc.log('[%s]: table "account" was created' % addon_name)