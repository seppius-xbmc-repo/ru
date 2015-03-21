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
            kb.setHeading('Поиск по имени фильма')
          else:
            kb = RussianKeyboard.Keyboard(self.Auth.Addon, self.search, 'Поиск по имени фильма')

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
        self.serial_img   = currentControl.getSelectedItem().getProperty('serial_img')
        self.serial_url   = currentControl.getSelectedItem().getProperty('serial_url')
        self.PLAY()

  def onAction(self, action):

    if self.getFocusId() == 201:
        #-- next page
        if int(action.getButtonCode()) == 61569 and int(self.getFocus().getSelectedItem().getProperty('ID')) == 1:
            if self.page < self.max_page:
                self.page = self.page+1
                if self.page == self.max_page:
                    self.win.setProperty('Page', 'Last')
                else:
                    self.win.setProperty('Page', 'Between')
                self.Reload_Serial()

        #-- previous page
        if int(action.getButtonCode()) == 61568 and int(self.getFocus().getSelectedItem().getProperty('ID')) == 20:
            if self.page > 1:
                self.page = self.page-1
                if self.page == 1:
                    self.win.setProperty('Page', 'First')
                else:
                    self.win.setProperty('Page', 'Between')
                self.Reload_Serial()
                self.getFocus().selectItem(19)

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
    cnt = 1
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
        item.setProperty('ID',    str(cnt))
        serial_list.addItem(item)

        cnt += 1
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
  def Get_Play_List(self):
    pl_url = self.serial_url
    img    = self.serial_img

    # create play list
    pl=xbmc.PlayList(1)
    pl.clear()

    #-- get playlist details -----
    html = self.Auth.get_HTML(pl_url)
    if html=='':
        return pl

    soup = BeautifulSoup(html, fromEncoding="windows-1251")

    all_video = soup.findAll('object', {'type' : 'application/x-shockwave-flash'})
    part = 1

    if len(all_video) == 0:
        return pl

    for rec in all_video:
        i_name = self.serial_name
        if len(all_video) > 1:
            i_name = i_name + ' (часть '+str(part)+')'
            part = part+1
        #--- get UPPOD flash parameters
        flash_param = str(rec.find('param', {'name' : 'flashvars'})['value'])
        video = re.compile('file=(.+?)&', re.MULTILINE|re.DOTALL).findall(flash_param)
        video_url = video[0]

        if video_url.find('http:') == -1:
            video_url = xppod.Decode(video_url)

        video_url = video_url.split(' or ') #[0]
        video_url = video_url[len(video_url)-1]

        i = xbmcgui.ListItem(i_name, video_url, thumbnailImage=img)
        i.setProperty('IsPlayable', 'true')
        pl.add(video_url, i)

    return pl

  #-----------------------------------------------------------------------------
  def PLAY(self):
        name        = self.serial_name
        # get play list
        pl = self.Get_Play_List()

        #--- show video
        #try:
        kwargs={'playlist':pl, 'name': name}
        self.Auth.Player(**kwargs)
        self.Reload_Serial()
        #except:
        #    pass

  #------ get number of pages ----------------------------------------------------
  def get_Number_of_Pages(self, url):
    html = self.Auth.get_HTML(url)
    # -- parsing web page --------------------------------------------------
    soup = BeautifulSoup(html, fromEncoding="windows-1251")

    page = 1

    for rec in soup.find('div', {'class':'navigation'}).findAll('a'):
        try:
            if int(rec.text) > page:
                page = int(rec.text)
        except:
            pass

    return page

  #------ process rubric -----------------------------------------------------------
  def Update_Rubric(self, url, i_rubric, data):
    global Update_flag
    #-- get total pages at website
    total_pages = self.get_Number_of_Pages(url)
    #-- get number of loaded pages for rubric
    loaded_pages = data.get_Info(i_rubric)
    print loaded_pages

    page = 1
    while page <= max(2, total_pages-loaded_pages) and Update_flag == 'ON':
        self.getControl(901).setLabel(str(page)+'/'+str(max(2, total_pages-loaded_pages)))
        page_url = url+'/page/'+str(page)+'/'
        html = self.Auth.get_HTML(page_url)
        # -- parsing web page --------------------------------------------------
        soup = BeautifulSoup(html, fromEncoding="windows-1251")

        for rec in soup.findAll('div', {'class':'short_post_link'}):
            try:
                self.Load_Page(rec.find('a')['href'], i_rubric, data)
            except:
                pass

        page += 1

    #-- update system info
    data.upd_Info(i_rubric, total_pages)
  #-- autoupdate local database ------------------------------------------------
  def Update_DB(self):
        global Update_flag

        xbmc.executebuiltin('Notification(FEPCOM.net,%s,2000,%s)'%('Начато обновление локальной базы', os.path.join(self.Auth.Addon.getAddonInfo('path'), 'start.png')))
        #-- create data
        kwargs={'Auth': self.Auth}
        d = Data(**kwargs)
        #--
        if Update_flag == 'ON':
            url = 'http://fepcom.net/filmy-onlajn/'
            rubric_ = u'Фильмы'
            self.Update_Rubric(url, rubric_, d)

        if Update_flag == 'ON':
            url = 'http://fepcom.net/dokumentalnoe-kino/'
            rubric_ = u'Документальное кино'
            self.Update_Rubric(url, rubric_, d)

        if Update_flag == 'ON':
            url = 'http://fepcom.net/retro-onlajn/'
            rubric_ = u'Ретро кино'
            self.Update_Rubric(url, rubric_, d)

        if Update_flag == 'ON':
            url = 'http://fepcom.net/yumor/'
            rubric_ = u'Юмор'
            self.Update_Rubric(url, rubric_, d)

        #-- update statistics
        d.upd_Country()
        d.upd_Genre()

        if Update_flag == 'ON':
            xbmc.executebuiltin('Notification(FEPCOM.net,%s,2000,%s)'%('Завершено обновление локальной базы', os.path.join(self.Auth.Addon.getAddonInfo('path'), 'stop.png')))

        self.win.setProperty('Update', 'OFF')


  #-- load and parse web page for serial list update ---------------------------
  def Load_Page(self, url, i_rubric, Data):
    #-- get movie info
    html = self.Auth.get_HTML(url)
    #-- parsing web page
    soup = BeautifulSoup(html, fromEncoding="windows-1251")
    #-- check if page have video
    if len(soup.findAll('object', {'type':'application/x-shockwave-flash'})) < 1:
        return

    #-- get movie info
    rec = soup.find('div', {'class' : 'post'})

    #-- get image
    try:
        i_image = rec.find('div', {'class' : 'post_content'}).find('img')['src']
    except:
        try:
            i_image = re.compile('src="(.+?)"', re.MULTILINE|re.DOTALL).findall(str(rec.find('div', {'class' : 'post_content'}).find('img')))
        except:
            print '**** IMG!!'
            return empty
    if i_image.find('http://') == -1:
        i_image = 'http://fepcom.net'+i_image

    #-- get name
    i_name = unescape(rec.find('h1').text)
    #-- get url
    i_url = url

    #-- get movie info
    info = rec.find('div', {'class' : 'post_content'})

    o_name      = '-'
    i_year      = '-'
    i_country   = '-'
    i_genre     = '-'
    i_director  = '-'
    i_actors    = '-'
    i_text      = '-'

    for inf in info.findAll("strong"):
        header = inf.text.replace(':', '').encode('utf-8')
        if header == 'Оригинальное название':
            o_name = unescape(str(inf.nextSibling).strip())
        elif header == 'Год выхода на экран':
            i_year = unescape(str(inf.nextSibling).strip())
        elif header == 'Страна':
            i_country = unescape(str(inf.nextSibling).strip())
        elif header == 'Фильм относится к жанру':
            i_genre = unescape(str(inf.nextSibling).strip())
        elif header == 'Постановщик':
            i_director = unescape(str(inf.nextSibling).strip())
        elif header == 'Актеры, принявшие участие в съемках':
            i_actors = unescape(str(inf.nextSibling).strip())
        elif header == 'Краткое описание':
            i_text = unescape(str(inf.nextSibling))

    if i_name == o_name:
        o_name = ''

    full_text = i_text
    if o_name != '':
        full_text = full_text+(u'\nОригинальное название: ')+o_name
    if i_actors != '':
        full_text = full_text+(u'\nАктеры: ')+i_actors

    movie_id = f_md5((i_name + i_year).encode('utf-8')).hexdigest()
    movie = (movie_id, i_name, o_name, i_url, i_year, i_director, i_actors, i_country.title(), i_text, i_image, i_genre.title(), i_rubric)

    if Data.is_Serial_exist(movie_id) == False:
        data.add_Serial(movie)

        for c in i_country.replace('-',',').replace('/',',').replace('.',',').title().split(','):
            Data.add_Country(c.strip())

        for g in i_genre.title().split(','):
            Data.add_Genre(g.strip())

        print i_name.encode('utf-8')

