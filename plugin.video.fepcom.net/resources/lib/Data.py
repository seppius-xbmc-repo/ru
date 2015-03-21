import sqlite3
import xbmc
import os, time

def lower_str(s):
    return s.lower()

class Data(object):

    def __init__(self, *args, **kwargs):
        self.Auth = kwargs.get('Auth')
        db = xbmc.translatePath(os.path.join(self.Auth.Data_path, r'fepcom_net.db3'))
        #---
        try:
            self.con = sqlite3.connect(db)
            self.con.create_function("lower", 1, lower_str)
            self.cur = self.con.cursor()
        except:
            print 'Error'

    def __del__(self):
        self.con.close()

    #-- check if serial exists
    def is_Serial_exist(self, id):
        try:
            self.cur.execute("SELECT COUNT(*) FROM serial WHERE id=:Id", {"Id": id})
            self.con.commit()
        except sqlite3.Error as e:
            print "An error occurred:", e.args[0]

        if self.cur.fetchone()[0] == 0:
            return False
        else:
            return True

    #-- add new serial
    def add_Serial(self, rec):
        if self.is_Serial_exist(rec[0]) == True:
            return
        try:
            self.cur.execute("INSERT INTO serial(id, name, orig, url, year, director, actors, country, descr, image, genre, rubric) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)", rec)
        except sqlite3.Error as e:
            print "An error occurred:", e.args[0]
        self.con.commit()
    #-- get serial
    def get_Serial(self, rubric, genre, country, search, page_len, page):
        sql = "SELECT * FROM serial"+self.sql_Serial(rubric, genre, country, search)+" ORDER BY name"
        if page_len > 0:
            sql = sql + ' LIMIT %s,%s'%((page-1)*page_len, page_len)

        self.cur.execute(sql)
        self.con.commit()
        return self.cur.fetchall()

    #-- get serial count
    def get_Serial_Count(self, rubric, genre, country, search):
        sql = "SELECT count(*) FROM serial"+self.sql_Serial(rubric, genre, country, search)
        self.cur.execute(sql)
        self.con.commit()
        return self.cur.fetchone()[0]

    #-- create serial SQL where statement
    def sql_Serial(self, rubric, genre, country, search):
        sql_where = ''
        #--
        if rubric <> '' or genre <> '' or country <> '' or search <> '':
            #-- rubric
            if rubric <> '':
                sql_where += ' rubric LIKE "%'+rubric+'%" '
            #-- genre
            if genre <> '':
                if sql_where <> '':
                    sql_where += ' AND '
                sql_where += ' genre LIKE "%'+genre+'%" '
            #-- country
            if country <> '':
                if sql_where <> '':
                    sql_where += ' AND '
                sql_where += ' country LIKE "%'+country+'%" '
            #-- search
            if search <> '':
                if sql_where <> '':
                    sql_where += ' AND '
                sql_where += ' lower(name) LIKE "%'+search+'%" '
            #-- where
            if sql_where <> '':
                sql_where = ' WHERE '+sql_where

        return sql_where

    #-- add new genre
    def add_Genre(self, new_genre):
        if new_genre == '':
            return

        self.cur.execute("SELECT COUNT(*) FROM genre WHERE genre=:Id", {"Id": new_genre})
        self.con.commit()
        if self.cur.fetchone()[0] == 0:
            self.cur.execute("INSERT INTO genre(genre) VALUES(?)", [new_genre])
            self.con.commit()

    #-- get genre
    def get_Genre(self, min_genre):
        self.cur.execute("SELECT genre FROM genre WHERE serial_cnt >= :Cnt ORDER BY serial_cnt DESC", {"Cnt": min_genre})
        self.con.commit()
        return self.cur.fetchall()

    #-- update genre statistics
    def upd_Genre(self):
        self.cur.execute("SELECT genre FROM genre")
        self.con.commit()
        for c in self.cur.fetchall():
            #-- get serial count
            self.cur.execute("SELECT count(*) FROM serial WHERE genre LIKE '%'||:Id||'%'", {"Id": c[0]})
            self.con.commit()
            serial_cnt = self.cur.fetchone()[0]
            #-- get genre count
            self.cur.execute("SELECT count(*) FROM genre WHERE :Id LIKE '%'||genre||'%'", {"Id": c[0]})
            self.con.commit()
            country_cnt = self.cur.fetchone()[0]
            #-- update genre statistic
            self.cur.execute("UPDATE genre SET serial_cnt = ?, genre_cnt = ? WHERE genre = ?", [serial_cnt, country_cnt, c[0]])
            self.con.commit()

    #-- add new country
    def add_Country(self, new_country):
        if new_country == '':
            return

        self.cur.execute("SELECT COUNT(*) FROM country WHERE country=:Id", {"Id":  new_country})
        if self.cur.fetchone()[0] == 0:
            self.cur.execute("INSERT INTO country(country) VALUES(?)", [new_country])
            self.con.commit()

    #-- get country
    def get_Country(self, min_country):
        self.cur.execute("SELECT country FROM country WHERE serial_cnt >= :Cnt ORDER BY serial_cnt DESC", {"Cnt": min_country})
        self.con.commit()
        return self.cur.fetchall()

    #-- update country statistics
    def upd_Country(self):
        self.cur.execute("SELECT country FROM country")
        for c in self.cur.fetchall():
            #-- get serial count
            self.cur.execute("SELECT count(*) FROM serial WHERE country LIKE '%'||:Id||'%'", {"Id": c[0]})
            serial_cnt = self.cur.fetchone()[0]
            #-- get country count
            self.cur.execute("SELECT count(*) FROM country WHERE :Id LIKE '%'||country||'%'", {"Id": c[0]})
            country_cnt = self.cur.fetchone()[0]
            #-- update country statistic
            self.cur.execute("UPDATE country SET serial_cnt = ?, country_cnt = ? WHERE country = ?", [serial_cnt, country_cnt, c[0]])
            self.con.commit()

    #-- add new rubric
    def add_Rubric(self, new_rubric):
        self.cur.execute("SELECT COUNT(*) FROM rubric WHERE rubric=:Id", {"Id":  new_rubric})
        if self.cur.fetchone()[0] == 0:
            self.cur.execute("INSERT INTO rubric(rubric) VALUES(?)", [new_rubric])
            self.con.commit()

    #-- get rubric
    def get_Rubric(self):
        self.cur.execute("SELECT rubric FROM rubric")
        self.con.commit()
        return self.cur.fetchall()

    #-- get system info
    def get_Info(self, rubric):
        self.cur.execute("SELECT Page_Loaded FROM rubric WHERE rubric=:Id", {"Id":  rubric})
        self.con.commit()
        return self.cur.fetchone()[0]

    #-- update system info
    def upd_Info(self, rubric, page):
        update_date = time.strftime('%Y-%m-%d %H:%M:%S')

        self.cur.execute("UPDATE rubric SET Page_Loaded = ?, Last_Update = ? WHERE rubric = ?", [page, update_date, rubric])
        self.con.commit()