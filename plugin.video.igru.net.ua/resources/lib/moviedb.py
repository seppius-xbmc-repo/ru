#!/usr/bin/python
# -*- coding: utf-8 -*-
#/*
# *      Copyright (C) 2011 Silen
# *
# *
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# */
import urllib2, urllib, re, cookielib, sys, time, os
from datetime import date

try:
    from hashlib import md5 as md5
except:
    import md5

import xbmcaddon, xbmc
Addon = xbmcaddon.Addon(id='plugin.video.igru.net.ua')

# load XML library
try:
    sys.path.append(os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib'))
    from ElementTree  import Element, SubElement, ElementTree
except:
    sys.path.insert(0, os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib'))
    from ElementTree  import Element, SubElement, ElementTree

#-- define Movie DB class (XML based) ------------------------------------------
class MovieDB:
    #-- init
    def __init__(self, mode):
        #--
        Addon = xbmcaddon.Addon(id='plugin.video.igru.net.ua')
        self.path = os.path.join(Addon.getAddonInfo('path'), r'resources', r'data')

        today = date.today()
        #--
        if mode == 'UPDATE':
            #load current serial list
            try:
                self.tree = ElementTree()
                self.tree.parse(os.path.join(self.path, 'movies.xml'))
                self.xml = self.tree.getroot()
                self.xml.find("LAST_UPDATE").text = today.isoformat()
                self.movies  = self.xml.find('MOVIES')
                self.types   = self.xml.find('TYPES')
                self.years   = self.xml.find('YEARS')
                self.info = "Update FEPCOM.NET Info"
                self.isUpdate= 1
                self.pinfo   = self.xml.find("LOADED_PAGES")
            except:
                # create XML structure
                self.xml = Element("IGRU_NET_UA")
                SubElement(self.xml, "LAST_UPDATE").text = today.isoformat()
                self.movies  = SubElement(self.xml, "MOVIES")
                self.types   = SubElement(self.xml, "TYPES")
                self.years   = SubElement(self.xml, "YEARS")
                self.info = "Reload FEPCOM.NET Info"
                self.isUpdate= 0
                self.pinfo   = SubElement(self.xml, "LOADED_PAGES")
        elif mode == 'READ':
             self.tree = ElementTree()
             self.tree.parse(os.path.join(self.path, 'movies.xml'))
             self.xml = self.tree.getroot()
             self.last_update = self.xml.find("LAST_UPDATE").text
             self.movies  = self.xml.find('MOVIES')
             self.types   = self.xml.find('TYPES')
             self.years   = self.xml.find('YEARS')
             self.info = "Update FEPCOM.NET Info"
             self.isUpdate= -1
             self.pinfo   = self.xml.find("LOADED_PAGES")
             self.pinfo.text = ''
        else:
            # create XML structure
            self.xml = Element("IGRU_NET_UA")
            SubElement(self.xml, "LAST_UPDATE").text = today.isoformat()
            self.movies  = SubElement(self.xml, "MOVIES")
            self.types   = SubElement(self.xml, "TYPES")
            self.years   = SubElement(self.xml, "YEARS")
            self.info = "Reload FEPCOM.NET Info"
            self.isUpdate= 0
            self.pinfo   = SubElement(self.xml, "LOADED_PAGES")


    #-- system functions -------------------------------------------------------
    def getkey(self, elem):
        return elem.text

    def getkey_name(self, elem):
        return elem.findtext("name")

    def f_md5(self, str):
        rez = md5(str.encode('utf8'))
        return rez.hexdigest()

    def movie_sort_compare(self, a, b):
        return cmp(a['name'], b['name'])

    #-- check if movie exists --------------------------------------------------
    def Is_Movie_Exists(self, url):
        is_found = 0

        for rec in self.movies:
            if rec.find('url').text == url:
                is_found = 1
                break

        return is_found

    #-- get number of loaded pages ---------------------------------------------
    def Get_Loaded_Pages(self, id):
        try:
            pages = int(self.pinfo.find('r'+str(id)).text)
        except:
            pages = 0

        return pages

    #-- set number of loaded pages ---------------------------------------------
    def Set_Loaded_Pages(self, id, pages):
        try:
            self.pinfo.find('r'+str(id)).text = str(pages)
        except:
            SubElement(self.pinfo, 'r'+str(id)).text = str(pages)

    #-- save to file -----------------------------------------------------------
    def Save_to_XML(self):
        #-- sort serials/categories/years
        self.movies[:]  = sorted(self.movies, key=self.getkey)
        self.types[:]   = sorted(self.types,  key=self.getkey_name)
        self.years[:]   = sorted(self.years,  key=self.getkey_name, reverse=True)
        #-- save to XML file
        ElementTree(self.xml).write(os.path.join(self.path, 'movies.xml'), encoding='utf-8')

    #-- add movie --------------------------------------------------------------
    def Add_Movie(self, movie):
        # add info to XML
        xml_movie_hash = 'mov_' + self.f_md5(movie['origin'] + movie['year'])
        #check if movie info exists
        xml_movie = self.movies.find(xml_movie_hash)
        if xml_movie is None:   #-- create new record
            # create serial record in XML
            xml_movie = SubElement(self.movies, xml_movie_hash)
            xml_movie.text = movie['name']
            SubElement(xml_movie, "origin").text   = movie['origin']
            SubElement(xml_movie, "url").text      = movie['url']
            SubElement(xml_movie, "genre").text    = movie['genre']
            SubElement(xml_movie, "director").text = movie['director']
            SubElement(xml_movie, "actors").text   = movie['actor']
            SubElement(xml_movie, "text").text     = movie['descr']
            SubElement(xml_movie, "img").text      = movie['image']
            # add year info
            SubElement(xml_movie, "year").text     = movie['year']
            year_hash = self.Get_Movie_Year(movie['year'])
            # add movie category info
            SubElement(xml_movie, "categories")
            cat = xml_movie.find("categories")
            for cat_rec in movie['category']:
                cat_hash = self.Get_Movie_Type(cat_rec)
                if cat.find(cat_hash) is None:
                    SubElement(cat, cat_hash)

    #-- get type ---------------------------------------------------------------
    def Get_Movie_Type(self, type_name):
        #-- store movie's category in XML
        xml_type_hash = 'st_'+self.f_md5(type_name)
        # check if type exists
        type = self.types.find(xml_type_hash)
        if type is None:
            type = SubElement(self.types, xml_type_hash)
            SubElement(type, "name").text = type_name
        #--
        return xml_type_hash

    #-- get year ---------------------------------------------------------------
    def Get_Movie_Year(self, year_name):
        #-- store movie's year in XML
        xml_type_hash = 'yr_'+self.f_md5(year_name)
        # check if year exists
        year = self.years.find(xml_type_hash)
        if year is None:
            year = SubElement(self.years, xml_type_hash)
            SubElement(year, "name").text = year_name
        #--
        return xml_type_hash

    #-- get type list ----------------------------------------------------------
    def Get_List_Type(self):
        return self.types

     #-- get year list ---------------------------------------------------------
    def Get_List_Year(self):
        return self.years

     #-- get movie list ----------------------------------------------------------
    def Get_List_Movie(self, par_tag, par_year, par_type_hash):
        movie_list = []

        for rec in self.movies:
            #-- get movie info
            i = self.Get_Movie_Info(rec)

            if unicode(i['year']).isnumeric():
                i_year      = int(i['year'])
            else:
                i_year      = 0
            # checkout by category or name/year
            if par_tag <> '*' and par_tag <> '':
                if par_tag not in i['name']:
                        continue
            if par_year <> '':
                if int(par_year) <> i_year:
                    continue
            if par_type_hash <> '':
                if rec.find('categories').find(par_type_hash) is None:
                    continue

            movie_list.append(i)
        #-- sort list
        movie_list.sort(self.movie_sort_compare)

        return movie_list, len(movie_list)

    #---------- get movie info -----------------------------------------------------
    def Get_Movie_Info(self, rec):
        mi = []
        mi = {}
        #-- name
        mi['name']     = rec.text.encode('utf8')
        #-- origin name
        try:    mi['origin']      = rec.find('origin').text.encode('utf8')
        except: mi['origin']      = ''
        #-- image
        try:    mi['img']          = rec.find('img').text.encode('utf8')
        except: mi['img']          = ''
        #-- url
        try:    mi['url']          = rec.find('url').text.encode('utf8')
        except: mi['url']          = ''
        #-- year
        try:    mi['year']         = rec.find('year').text.encode('utf8')
        except: mi['year']         = ''
        if unicode(mi['year'].decode('utf8')).strip().isnumeric(): pass
        else:
            try:
                mi['year'] = re.compile('([0-9][0-9][0-9][0-9])', re.MULTILINE|re.DOTALL).findall(mi['year'])[0]
            except:
                mi['year']= '0000'
        #-- genre
        try:    mi['genre']        = rec.find('genre').text.encode('utf8')
        except: mi['genre']        = ''
        #-- director
        try:    mi['director']     = rec.find('director').text.encode('utf8')
        except: mi['director']     = ''
        #-- actors
        try:    mi['actors']       = rec.find('actors').text.encode('utf8')
        except: mi['actors']       = ''
        #-- description
        try:    mi['text']         = rec.find('text').text.encode('utf8')
        except: mi['text']         = ''
        #-----
        return mi
    #---------------------------------------------------------------------------