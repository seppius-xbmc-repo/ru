# -*- coding: utf-8 -*-
import os, urllib, time, re
import xbmc, xbmcgui, xbmcaddon, xbmcplugin
from copy import deepcopy

import sqlite3, math
import threading
import xppod

try:
    from hashlib import md5 as md5
except:
    import md5

from BeautifulSoup  import BeautifulSoup

from Data           import Data
from GenreSelect    import GenreSelectDialog
from CountrySelect  import CountrySelectDialog
from RubricSelect   import RubricSelectDialog
import RussianKeyboard

import HTMLParser
hpar = HTMLParser.HTMLParser()

Update_flag = ''

KEY_BUTTON_BACK = 275
KEY_KEYBOARD_ESC = 61467

SERIAL_LIST     = 201
SERIAL_NUM      = 100

SEASON_LIST     = 301
MOVIE_LIST      = 401

class MainScreen(xbmcgui.WindowXML):
  def __init__(self, *args, **kwargs):
    xbmcgui.WindowXML.__init__(self)
    self.Auth = kwargs.get('Auth')
    self.icon = xbmc.translatePath(os.path.join(self.Auth.Addon_path, r'icon.png'))
    #---
    self.mode = 'Serial'
    self.country = ''
    self.genre = ''
    self.rubric = ''
    self.search = ''
    self.serial_name = ''
    self.serial_img = ''
    self.serial_url = ''
    self.serial_descr = ''
    self.pl_url = ''

    self.focus  = SERIAL_LIST
    self.list = []
    self.isStart = True

  def __del__(self):
    try:
        self.conn.close()
    except:
        pass

  def f_md5(self, str):
    try:
        rez = md5(str)
    except:
        rez = md5.md5(str)
    return rez

  def unescape(self, text):
    try:
        text = hpar.unescape(text)
    except:
        text = hpar.unescape(text.decode('utf8'))

    try:
        text = unicode(text, 'utf-8')
    except:
        text = text

    return text

  def onInit(self):
    xbmcgui.WindowXML.onInit(self)
    self.win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
    self.version = '[B][COLOR=FF00CCFF]ver. '+self.Auth.Addon.getAddonInfo('version')+'[/COLOR][/B]'
    self.getControl(900).setLabel(self.version)
    self.getControl(141).setLabel('<<')
    self.getControl(142).setLabel('>>')
    self.getControl(144).setLabel('<')
    self.getControl(145).setLabel('>')

    self.Auth.player.stop()

    if self.isStart == True:
        global Update_flag
        Update_flag = 'ON'
         #-- load serial list
        self.page = 1
        self.win.setProperty('Page', 'First')
        self.win.setProperty('onUp', '140')

        #-- check if auto-update of local DB should be used
        self.auto_update    = self.Auth.Addon.getSetting('auto_update')

        #-- if Auto Update is enabled - run update
        if self.auto_update == 'true':
            self.win.setProperty('Update', 'ON')
            self.thread = threading.Thread(target = self.Update_DB)
            self.thread.setDaemon(True)
            self.thread.start()

        #-- check if page should be used
        self.use_page  = self.Auth.Addon.getSetting('use_page')
        self.win.setProperty('is_Page', self.use_page)
        self.page_size = int(self.Auth.Addon.getSetting('page_size'))
        #-- initially reload list of serials
        self.Reload_Serial()
        self.isStart = False

  def onClick(self, controlId):
    currentControl = self.getControl(controlId)
    #-- main menu -----------------------------------
    if controlId == 131 or controlId == 132: #-- Exit
      if self.mode == 'Movie':
            currentControl.setLabel('Выход')
            self.mode = 'Serial'
            self.win.setProperty('Mode', self.mode)
            xbmc.sleep(500)
            self.win.setFocusId(SERIAL_LIST)
      else:
        global Update_flag
        Update_flag = 'OFF'
        self.close()

    if controlId == 121: #-- Genre
      self.genre_changed = False
      try:
          kwargs={'MainScreen': self}
          aw = GenreSelectDialog('tvp_genreDialog.xml', self.Auth.Addon.getAddonInfo('path'), **kwargs)
          aw.doModal()
          del aw

          if self.genre_changed == True:
            self.page = 1
            self.Reload_Serial()
      except:
        pass

    if controlId == 122: #-- Country
      self.country_changed = False
      try:
          kwargs={'MainScreen': self}
          aw = CountrySelectDialog('tvp_countryDialog.xml', self.Auth.Addon.getAddonInfo('path'), **kwargs)
          aw.doModal()
          del aw

          if self.country_changed == True:
            self.page = 1
            self.Reload_Serial()
      except:
        pass

    if controlId == 123: #-- Rubric
      self.rubric_changed = False
      try:
          kwargs={'MainScreen': self}
          aw = RubricSelectDialog('tvp_rubricDialog.xml', self.Auth.Addon.getAddonInfo('path'), **kwargs)
          aw.doModal()
          del aw

          if self.rubric_changed == True:
            self.page = 1
            self.Reload_Serial()
      except:
        pass

    if controlId == 151: #-- Search by serial name
      try:
          #-- if standard XBMC keyboard is selected
          if self.Auth.Addon.getSetting('xbmc_keyboard') == 'true':
            kb = xbmc.Keyboard()
            kb.setHeading('Поиск по имени сериала')
          else:
            kb = RussianKeyboard.Keyboard(self.Auth.Addon, self.search, 'Поиск по имени сериала')

          kb.doModal()
          if kb.isConfirmed():
            text = kb.getText()
            #--
            self.page = 1
            self.search = text
            self.focus = controlId
            if self.search== '':
                self.getControl(151).setLabel('...')
            else:
                self.getControl(151).setLabel(self.search)
            self.Reload_Serial()
      except:
        pass

    #-- page control ----------------------------------
    if controlId == 141: #-- previous page -10
      try:
          if self.page-10 < 1:
            self.page = 1
          else:
            self.page = self.page-10
          if self.page == 1:
            self.win.setProperty('Page', 'First')
          else:
            self.win.setProperty('Page', 'Between')
          self.Reload_Serial()
      except:
        pass

    if controlId == 144: #-- previous page
      try:
          self.page = self.page-1
          if self.page == 1:
            self.win.setProperty('Page', 'First')
          else:
            self.win.setProperty('Page', 'Between')
          self.Reload_Serial()
      except:
        pass

    if controlId == 145: #-- next page
      try:
          self.page = self.page+1
          if self.page == self.max_page:
            self.win.setProperty('Page', 'Last')
          else:
            self.win.setProperty('Page', 'Between')
          self.Reload_Serial()
      except:
        pass

    if controlId == 142: #-- next page +10
      try:
          if self.page+10 > self.max_page:
            self.page = self.max_page
          else:
            self.page = self.page+10

          if self.page == self.max_page:
            self.win.setProperty('Page', 'Last')
          else:
            self.win.setProperty('Page', 'Between')
          self.Reload_Serial()
      except:
        pass

    #-- serial list -----------------------------------
    if controlId == 201:
        self.serial_name  = currentControl.getSelectedItem().getProperty('serial_name')
        self.serial_descr = currentControl.getSelectedItem().getProperty('serial_descr')
        self.serial_img   = currentControl.getSelectedItem().getProperty('serial_img')
        self.serial_url   = currentControl.getSelectedItem().getProperty('serial_url')
        self.mode = 'Movie'
        self.getControl(131).setLabel('Назад')
        self.getControl(132).setLabel('Назад')
        #-- load movie list
        self.Reload_Movie()

    #-- movie list -----------------------------------
    if controlId == 401:
        self.PLAY()

  def onAction(self, action):
    if action == 10:
        if self.mode == 'Movie':
            self.getControl(131).setLabel('Выход')
            self.getControl(132).setLabel('Выход')
            self.mode = 'Serial'
            self.win.setProperty('Mode', self.mode)
            xbmc.sleep(500)
            self.win.setFocusId(SERIAL_LIST)
            return
        else:
            global Update_flag
            Update_flag = 'OFF'
    xbmcgui.WindowXML.onAction(self, action)

  #----- Serial ----------------------------------------------------------------
  def Reload_Serial(self):
    self.st = time.time()
     #-- load serial list
    serial_list = self.getControl(SERIAL_LIST)
    serial_list.reset()
    #---
    self.win.setProperty('Mode', u'Loader')
    xbmc.sleep(500)
    #---
    (list, serial_count) = self.getSerialData()
    #-- set number of found serials
    self.max_page = int(math.ceil(serial_count*1.0/self.page_size))
    if self.max_page <= 1:
        self.win.setProperty('Max_Page', 'false')
    else:
        self.win.setProperty('Max_Page', 'true')

    self.getControl(SERIAL_NUM).setLabel('[COLOR=FF33CC00]'+str(serial_count)+'[/COLOR]')
    self.getControl(143).setLabel('[COLOR=FF809AAD]'+str(self.page)+'/'+str(self.max_page)+'[/COLOR]')
    #-- set serial list
    for rec in list:
        name = rec['name']
        item = xbmcgui.ListItem(name, thumbnailImage = rec['img'])

        #-- serial description
        descr = []
        if len(rec['country']) > 0:
          descr.append(u'[COLOR=66FFFFFF]Страна  :[/COLOR] %s' % rec['country'])
        if len(rec['genre']) > 0:
          descr.append(u'[COLOR=66FFFFFF]Жанр    :[/COLOR] %s' % rec['genre'])
        if len(rec['rubric']) > 0:
          descr.append(u'[COLOR=66FFFFFF]Рубрика :[/COLOR] %s' % rec['rubric'])
        if len(rec['year']) > 0:
          descr.append(u'[COLOR=66FFFFFF]Год     :[/COLOR] %s' % rec['year'])
        if len(rec['director']) > 0:
          descr.append(u'[COLOR=66FFFFFF]Режисер :[/COLOR] %s' % rec['director'])
        if len(rec['actors']) > 0:
          descr.append(u'[COLOR=66FFFFFF]Актеры  :[/COLOR] %s' % rec['actors'])
        descr.append('')
        descr.append(rec['descr'])

        item.setInfo(type='video', infoLabels={ 'plot':       u'[CR]'.join(descr)})

        # -- serial info
        label2=[]
        if len(rec['name_orig']) > 0:
          label2.append(rec['name_orig'])
        if len(rec['country']) > 0:
          label2.append(u'[COLOR=66FFFFFF]Страна:[/COLOR] %s' % rec['country'])
        if len(rec['genre']) > 0:
          label2.append(u'[COLOR=66FFFFFF]Жанр:[/COLOR] %s' % rec['genre'])
        if len(rec['rubric']) > 0:
          label2.append(u'[COLOR=66FFFFFF]Рубрика:[/COLOR] %s' % rec['rubric'])
        item.setLabel2(u'[CR]'.join(label2))

        #item.setProperty('watch_started', 'True')
        item.setProperty('serial_name',     name)
        item.setProperty('serial_img',      rec['img'])
        item.setProperty('serial_url',      rec['url'])
        item.setProperty('serial_descr',    u'[CR]'.join(descr))
        serial_list.addItem(item)
    #---
    self.win.setProperty('Mode', self.mode)
    xbmc.sleep(500)
    self.win.setFocusId(self.focus)

  def getSerialData(self):
    list = []
    for rec in self.Auth.Data.get_Serial(self.rubric, self.genre, self.country, self.search, self.page_size, self.page):
            list.append({'name': rec[1], 'img': rec[9], 'descr': rec[8], 'country': rec[7], 'genre': rec[10], 'name_orig': rec[2], 'rubric': rec[11], 'url': rec[3], 'year': rec[4], 'director': rec[5], 'actors': rec[6]})

    #-- get serial count
    serial_count = self.Auth.Data.get_Serial_Count(self.rubric, self.genre, self.country, self.search)

    #-- return serials list
    return list, serial_count

    #----- Serial Season -------------------------------------------------------
  def Reload_Season(self):
     #-- load season list
    season_list = self.getControl(SEASON_LIST)
    season_list.reset()
    #---
    self.win.setProperty('Mode', u'Loader')
    xbmc.sleep(500)
    #---
    list = self.getSeasonData()
    #-- set serial list
    for rec in list:
        name = rec['name']
        item = xbmcgui.ListItem(name, thumbnailImage = rec['img'])
        item.setInfo(type='video', infoLabels={ 'plot':        rec['descr']})

        label2=[]
        if len(rec['name_orig']) > 0:
          label2.append(rec['name_orig'])
        if len(rec['season_number']) > 0:
          label2.append(u'[COLOR=66FFFFFF]Сезон:[/COLOR] %s' % rec['season_number'])
        if len(rec['year']) > 0:
          label2.append(u'[COLOR=66FFFFFF]Год:[/COLOR] %s' % rec['year'])
        item.setLabel2(u'[CR]'.join(label2))

        #item.setProperty('watch_started', 'True')
        item.setProperty('season_id', rec['season_id'])
        season_list.addItem(item)
    #---
    self.win.setProperty('Mode', self.mode)
    xbmc.sleep(500)
    self.win.setFocusId(SEASON_LIST)

  def getSeasonData(self):
    api_key =self.Auth.API_key
    #--
    url = 'http://api.seasonvar.ru/'
    #-- set country

    values = {
            'key'           : api_key,
            'command'       : u'getSeasonList',
            'name'          : self.serial_name
            }

    post = urllib.urlencode(values,'unicode-escape')
    html = self.Auth.get_HTML(url, post)
    data = json.loads(html)
    #-- parse data
    list = []
    for rec in data:
        #-- serial name
        try:
            name = rec['name']
        except:
            name = 'N/A'

        try:
            name_orig = rec['name_original']
        except:
            name_orig = ''

        #-- serial poster
        try:
            img = rec['poster']
        except:
            img = self.icon
        #-- serial description
        try:
            descr = rec['description']
        except:
            descr = ''

        #-- season number
        try:
            season_number = rec['season_number']
        except:
            season_number = ''

        #-- season id
        try:
            season_id = rec['id']
        except:
            season_id = ''

        #-- season year
        try:
            season_year = rec['year']
        except:
            season_year = ''

        list.append({'name':name, 'img': img, 'descr': descr, 'year':season_year, 'season_id': season_id, 'season_number':season_number, 'name_orig':name_orig})

    #-- return season list
    return list

    #----- Serial Season Parts -------------------------------------------------
  def Reload_Movie(self):
    del self.list[:]

    #-- load movie list
    movie_list = self.getControl(MOVIE_LIST)
    movie_list.reset()
    #---
    self.win.setProperty('Mode', u'Loader')
    xbmc.sleep(500)
    #---
    list = self.getMovieData()
    #-- set serial list
    for rec in list:
        name = rec['name']
        if len(rec['name_orig'])>0:
            name = name + ' - ' + rec['name_orig']
        #name = name + ' (' + rec['season_number'] + u' сезон)'
        self.getControl(413).setLabel(name)

        for mov in rec['movie']:
            item = xbmcgui.ListItem(mov['movie_name'], thumbnailImage = rec['img'])
            item.setProperty('url', mov['url'])
            item.setProperty('img', rec['img'])

            item.setInfo(type='video', infoLabels={ 'plot':        rec['descr']})
            #item.setProperty('watched', 'True')

            movie_list.addItem(item)

            #-- add new item to the list
            self.list.append({'name': mov['movie_name'], 'url': mov['url'], 'img': rec['img']})
    #---
    self.win.setProperty('Mode', self.mode)
    xbmc.sleep(500)
    self.win.setFocusId(MOVIE_LIST)


  def getMovieData(self):
    list = []
    #-- get serial play list & parameters  -------------------------------------
    html = self.Auth.get_HTML(self.serial_url, None, 'http://serialu.net/media/uppod.swf')

    # -- parsing web page
    html = re.compile('<body>(.+?)<\/body>', re.MULTILINE|re.DOTALL).findall(html)[0]
    soup = BeautifulSoup(html)
    pl_url = ''

    is_multiseason = len(soup.findAll('object', {'type':'application/x-shockwave-flash'}))

    for rec in soup.findAll('object', {'type':'application/x-shockwave-flash'}):
        if is_multiseason > 1:
            season = rec.parent.previousSibling.previousSibling.text+r' '
        else:
            season = r''

        for par in rec.find('param', {'name':'flashvars'})['value'].split('&'):
            if par.split('=')[0] == 'pl':
                pl_url = par[3:]

        if pl_url.find('http:') == -1:
            pl_url = xppod.Decode(pl_url)

        #-- get playlist details ---------------------------------------------------
        html = self.Auth.get_HTML(pl_url, None, 'http://serialu.net/media/uppod.swf')
        self.pl_url = pl_url

        # -- check if playlist is encoded
        if html.find('{"playlist":[') == -1:
            html = xppod.Decode(html).encode('utf-8').split(' or ')[0] #-- TODO: make smart choice

        # -- parsing web page
        s_url = ''
        s_num = 0
        movie_list = []
        for rec in re.compile('{(.+?)}', re.MULTILINE|re.DOTALL).findall(html.replace('{"playlist":[', '')):
            for par in rec.replace('"','').split(','):
                if par.split(':')[0]== 'comment':
                    name = str(s_num+1) + ' серия' #par.split(':')[1]+' '
                if par.split(':')[0]== 'file':
                    if 'http' in par.split(':')[1]:
                        s_url = par.split(':')[1]+':'+par.split(':')[2]
                    else:
                        s_url = xppod.Decode(par.split(':')[1]).split(' or ')[0]
            s_num += 1

            # mark part for history
            name = season.encode('utf-8') + name

            movie_list.append({'movie_name': name, 'url': s_url})
            #if h_part <> '-':
            #    if name == h_part:
            #        name = '[COLOR FF00FF00]'+name+'[/COLOR]'
        #-- parse data
        list.append({'name':self.serial_name, 'img': self.serial_img, 'descr': self.serial_descr, 'season_number':s_num, 'name_orig':'', 'movie': movie_list})

    #-- return movie list
    return list

  #-----------------------------------------------------------------------------
  def Get_Play_List(self, selected):
    pl_url = self.pl_url
    img    = self.serial_img

    # create play list
    pl=xbmc.PlayList(1)
    pl.clear()

    #-- get playlist details -----
    html = self.Auth.get_HTML(pl_url, None, 'http://serialu.net/media/uppod.swf')
    if html=='':
        return pl

    # -- check if playlist is encoded
    if html.find('{"playlist":[') == -1:
        html = xppod.Decode(html).encode('utf-8')

    # -- parsing web page
    s_url = ''
    s_num = 0
    is_Found = False
    for rec in re.compile('{(.+?)}', re.MULTILINE|re.DOTALL).findall(html.replace('{"playlist":[', '')):
        for par in rec.replace('"','').split(','):
            if par.split(':')[0]== 'comment':
                name = str(s_num+1) + ' серия' #par.split(':')[1]+' '
            if par.split(':')[0]== 'file':
                if 'http' in par.split(':')[1]:
                    s_url = par.split(':')[1]+':'+par.split(':')[2]
                else:
                    s_url = xppod.Decode(par.split(':')[1]).split(' or ') #[0]
                    s_url = s_url[len(s_url)-1]
        s_num += 1

        if name == selected.getLabel():
            is_Found = True

        if is_Found == True :
            i = xbmcgui.ListItem(self.serial_name+' '+name, path = urllib.unquote(selected.getProperty('url')), thumbnailImage=selected.getProperty('img'))
            i.setProperty('IsPlayable', 'true')
            pl.add(s_url, i)
            if self.Auth.Addon.getSetting('continue_play') == 'false':
                break
    return pl

  #-----------------------------------------------------------------------------
  def PLAY(self):
        name        = self.getControl(413).getLabel()
        list        = self.getControl(MOVIE_LIST)
        selected    = list.getSelectedItem()

        # get play list
        pl = self.Get_Play_List(selected)

        #--- show video
        #try:
        kwargs={'playlist':pl, 'name': name}
        self.Auth.Player(**kwargs)
        self.Reload_Movie()
        #except:
        #    pass

  #-- autoupdate local database ------------------------------------------------
  def Update_DB(self):
        global Update_flag

        xbmc.executebuiltin('Notification(SEASONVAR.ru,%s,2000,%s)'%('Начато обновление локальной базы', os.path.join(self.Auth.Addon.getAddonInfo('path'), 'start.png')))
        #-- create data
        kwargs={'Auth': self.Auth}
        d = Data(**kwargs)
        #-- get number of loaded pages
        loaded_pages = d.get_Info()
        #-- get number of web pages from site
        url='http://serialu.net/page/1/'
        html = self.Auth.get_HTML(url)

        total_pages = 1
        match=re.compile('<div class="wp-pagenavi">(.+?)</div>', re.MULTILINE|re.DOTALL).findall(html)
        page=re.compile('<a href="(.+?)/page/(.+?)</a>', re.MULTILINE|re.DOTALL).findall(match[0])

        for rec in page:
            v = re.compile('(.+?)/" title="(.+?)"', re.MULTILINE|re.DOTALL).findall(rec[1])
            if len(v) > 0:
                if total_pages < int(v[0][0]):
                    total_pages = int(v[0][0])

        #-- update list of serials
        i=1
        while i <= max(10, total_pages-loaded_pages) and Update_flag == 'ON':
            self.getControl(901).setLabel(str(i)+'/'+str(max(10, total_pages-loaded_pages)))
            self.Load_Page(i, d)
            i=i+1

        if Update_flag == 'ON':
            #-- update system info
            d.upd_Info(total_pages)
            xbmc.executebuiltin('Notification(SEASONVAR.ru,%s,2000,%s)'%('Завершено обновление локальной базы', os.path.join(self.Auth.Addon.getAddonInfo('path'), 'stop.png')))

        self.win.setProperty('Update', 'OFF')


  #-- load and parse web page for serial list update ---------------------------
  def Load_Page(self, i, Data):
    global Update_flag

    url='http://serialu.net/page/'+ str(i)+'/'
    #---
    html = self.Auth.get_HTML(url)
    html_container = re.compile('<div class="container">(.+?)<div class="navigation">', re.MULTILINE|re.DOTALL).findall(html)

    # -- parsing web page ----------
    soup = BeautifulSoup(''.join(html_container[0].replace('<p>', '  ').replace('</p>', '')))

    serials = soup.findAll("div", { "class" : "entry" })
    for ser in serials:
        if Update_flag == 'OFF': return
        try:
            # check if process was cancelled
            # --
            i_name  = self.unescape(ser.find("h2").find("a").text.strip())
            i_url   = ser.find("h2").find("a")["href"]
            #-- detail info
            i_rubric = ''
            for r in ser.find('div', {'class':'cat'}).findAll('a', {'rel':"category tag"}):
                Data.add_Rubric(r.text.capitalize())
                i_rubric = i_rubric + r.text.capitalize() +', '

            info = ser.find("div", { "class" : "content" })
            try:
                i_image = info.find("img")["src"]
            except:
                ser_name = i_name.replace(u'”', u'"').replace(u'“',u'"').replace(u'«',u'"').replace(u'»',u'"')
                search_mask = '<img .+alt="'+ser_name+'"(.+?) src="(.+?)"'
                img_alt = re.compile(search_mask, re.MULTILINE|re.DOTALL).findall(unicode(html, 'utf-8'))
                try:
                    i_image = img_alt[0][1]
                except:
                    i_image = '-'
                    print ('  '+i_name + u' - image not found').encode('utf-8')
                    print ser.encode('utf-8')

            o_name      = '-'
            i_year      = '-'
            i_country   = '-'
            i_genre     = '-'
            i_director  = '-'
            i_actors    = '-'
            i_text      = '-'

            for inf in info.findAll("strong"):
                if inf.text.encode('utf-8') == 'Оригинальное название:':
                    o_name = self.unescape(str(inf.nextSibling).strip())
                elif inf.text.encode('utf-8') == 'Год выхода на экран:':
                    i_year = self.unescape(str(inf.nextSibling).strip())
                elif inf.text.encode('utf-8') == 'Страна:':
                    i_country = self.unescape(str(inf.nextSibling).strip())
                elif inf.text.encode('utf-8') == 'Сериал относится к жанру:':
                    i_genre = self.unescape(str(inf.nextSibling).strip())
                elif inf.text.encode('utf-8') == 'Постановщик':
                    i_director = self.unescape(str(inf.nextSibling).strip())
                elif inf.text.encode('utf-8') == 'Актеры, принявшие участие в съемках:':
                    i_actors = self.unescape(str(inf.nextSibling).strip())
                elif inf.text.encode('utf-8') == 'Краткое описание:':
                    i_text = self.unescape(str(inf.nextSibling))
                elif inf.text.encode('utf-8') == 'Сериал относится к жанру:':
                    i_genre = self.unescape(str(inf.nextSibling))

            if i_name == o_name:
                o_name = ''

            full_text = i_text
            if o_name != '':
                full_text = full_text+(u'\nОригинальное название: ')+o_name
            if i_actors != '':
                full_text = full_text+(u'\nАктеры: ')+i_actors

            serial_id = self.f_md5((i_name + i_year).encode('utf-8')).hexdigest()

            rec = (serial_id, i_name, o_name, i_url, i_year, i_director, i_actors, i_country.title(), i_text, i_image, i_genre.title(), i_rubric)
            if Data.is_Serial_exist(serial_id) == False:
                Data.add_Serial(rec)

                for c in i_country.replace('-',',').replace('/',',').replace('.',',').title().split(','):
                    Data.add_Country(c.strip())

                for g in i_genre.title().split(','):
                    Data.add_Genre(g.strip())

                print i_name.encode('utf-8')
        except:
            pass