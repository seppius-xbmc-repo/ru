#!/usr/bin/python
# -*- coding: utf-8 -*-

import httplib
import urllib
import urllib2
import re
import sys,subprocess
import os
import socket
import threading
import time
import random
import json


import xbmcgui
import xbmc
import xbmcaddon
import xbmcvfs

aceport=62062
Addon = xbmcaddon.Addon(id='script.module.torrent.ts')
language = Addon.getLocalizedString
server_ip=Addon.getSetting('ip_addr')
if Addon.getSetting('save')=='true': save=True
else: save=False
if Addon.getSetting('log')=='true': alog=True
else: alog=False
if (sys.platform == 'win32') or (sys.platform == 'win64'): pwin=True
else: pwin=False
if Addon.getSetting('pausable')=='true': pausable=True
else: pausable=False
if Addon.getSetting('autoexit')=='true': autoexit=True
else: autoexit=False
if Addon.getSetting('autobuf')=='true': autobuf=True
else: autobuf=False
addon_icon    = Addon.getAddonInfo('icon')

def show_Msg(heading, message, times = 3000, pics = addon_icon):
    try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading.encode('utf-8'), message.encode('utf-8'), times, pics.encode('utf-8')))
    except Exception, e:
        print( '[%s]: ShowMessage: Transcoding UTF-8 failed [%s]' % (addon_id, e), 2 )
        try: xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s, "%s")' % (heading, message, times, pics))
        except Exception, e:
            print( '[%s]: ShowMessage: exec failed [%s]' % (addon_id, e), 3 )

class Logger():
    
    def __init__(self,Name):
        self.name=Name
        self.link=None
    def out(self,txt):
        if alog:
            print "%s:%s"%(self.name,txt)


class _TSPlayer(xbmc.Player):

    def __init__( self):

        self.log=Logger("TSPlayer")
        self.log.out('init')
        self.active=True
        self.link=None
        self.vod=True
        self.duration=None
        self.coms=[]
    def onPlayBackPaused( self ):
        self.log.out('paused')
        
    def onPlayBackStarted( self ):
        self.log.out('started')
        if self.vod:
            try: 
                self.duration= int(xbmc.Player().getTotalTime()*1000)
                comm='DUR '+self.link.replace('\r','').replace('\n','')+' '+str(self.duration)
                self.coms.append(comm)
            except: pass
        
        comm='PLAYBACK '+self.link.replace('\r','').replace('\n','')+' 0'
        self.coms.append(comm)
        
    def onPlayBackResumed(self):
        self.log.out("play resume")
        
    def onPlayBackEnded(self):
        self.log.out("play ended")
        self.active=False
        comm='PLAYBACK '+self.link.replace('\r','').replace('\n','')+' 100'
        self.coms.append(comm)
        
    def onPlayBackStopped(self):
        self.log.out("play stop")
        self.active=False
    def __del__(self):
        self.log.out('fckn del')
    


class TSengine():

    def __init__(self):
        if xbmc.Player().isPlaying(): xbmc.Player().stop()

        self.log=Logger("TSEngine")
        self.push=Logger('OUT')
        self.alive=True
        self.progress = xbmcgui.DialogProgress()
        self.player=None
        self.files={}
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self._sock.setblocking(0)
        self._sock.settimeout(3)
        self.progress.create("AceStream Client","Инициализация")
        self.tsserv =None
        self.conn=False
        self.title=None
        self.filename=None
        self.mode=None
        self.url=None
        self.local=False
        self.saved=False
        self.pos=[25,50,75,100]
        self.save=False
        l=False
        while xbmc.Player().isPlaying(): 
            l=True
            if xbmc.abortRequested:
                self.log.out("XBMC is shutting down")
                return False
            if self.progress.iscanceled():
                return False
            xbmc.sleep(300)
        Addon.setSetting('active','1')
        if l: xbmc.sleep(500)
    def ts_init(self):
       
        
        self.tsserv = TSServ(self._sock)
        self.tsserv.start()
        #comm="HELLOBG"
        #self.TSpush(comm)
        comm="HELLOBG"
        self.TSpush(comm)
        self.progress.update(0,"Ждем ответа"," ")
        while not self.tsserv.version:
            if xbmc.abortRequested:
                self.log.out("XBMC is shutting down")
                return False
            if self.progress.iscanceled():
                return False
            time.sleep(1)
        ready='READY'
        if self.tsserv.key:

            import hashlib
            sha1 = hashlib.sha1()
            pkey=self.tsserv.pkey
            sha1.update(self.tsserv.key+pkey)
            key=sha1.hexdigest()
            pk=pkey.split('-')[0]
            key="%s-%s"%(pk,key)
            ready='READY key=%s'% key
        if self.progress.iscanceled():
            self.err=1
            return False	
        self.TSpush(ready)
        return True
    
    def sm(self,msg):
        show_Msg('AceStream',msg)
    
    def connect(self):
        server_ip='127.0.0.1'
        servip=Addon.getSetting('ip_addr')
        aceport=62062
        self.log.out('Trying to connect')
        self.progress.update(0,'Пробуем подключиться',' ')
        if pwin:
            res=self.startWin()
            aceport=self.getWinPort()
            if not aceport: 
                res=self.startWin()
                if not res: return False
        else:
            #print sepver_ip
            #print aceport
            self.log.out('try to connect to linux ace')
            self.log.out('Connecting to %s:%s'%(servip,aceport))
            try:
                self._sock.connect((servip, 62062))
                self.log.out('Connected to %s:%s'%(servip,62062))
                return True
            except:
                res=self.startLin()
                if not res: return False
        i=30
        while (i>1):
            self.progress.update(0,'Waiting ASEngine','%s'%i)
            
            try:
                if pwin: aceport=self.getWinPort()
                self._sock.connect((servip, aceport))
                self.log.out('Connected to %s:%s'%(servip,aceport))     
                i=0
                return True
            except:
                self.log.out('Failed to connect to %s:%s'%(servip,aceport))   
            if self.progress.iscanceled():
                return False
                break
            i=i-1
            xbmc.sleep(1000)
        self.sm('Cant connect')
        return False
            
                
    def startLin(self):
        self.log.out('try to start Lin engine;;')
        import subprocess
        try:
            proc = subprocess.Popen(["acestreamengine","--client-console"])
        except:
            try:  proc = subprocess.Popen('acestreamengine-client-console')
            except: 
                try: 
                    subprocess.Popen(Addon.getSetting('prog'))
                except:
                    try:
                        xbmc.executebuiltin('XBMC.StartAndroidActivity("org.acestream.engine")')
                    except:
                        self.sm('Not Installed')
                        self.log.out('Not Installed')
                        self.progress.update(0,'AceStream not installed','')
                        return False
        
        self.log.out('Engine starting')
        return True
    
    def startWin(self):
        try:
            import _winreg
            t = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, 'Software\\TorrentStream')
            needed_value =  _winreg.QueryValueEx(t , 'EnginePath')[0]
            path= needed_value.replace('tsengine.exe','')
            self.log.out("Try to start %s"%needed_value)
            self.progress.update(0,'Starting TSEngine','')
            os.startfile(needed_value)
            self.log.out('TSEngine starting')
        except: 
            try:
                import _winreg
                t = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, 'Software\AceStream')
                needed_value =  _winreg.QueryValueEx(t , 'EnginePath')[0]
                path= needed_value.replace('ace_engine.exe','')
                self.log.out("Try to start %s"%needed_value)
                self.progress.update(0,'Starting ASEngine','')
                os.startfile(needed_value)
                self.log.out('ASEngine starting')
            except:
                self.sm('Not Installed')
                self.log.out('Not Installed')
                self.progress.update(0,'AceStream not installed','')
                return False
        return True
    def getWinPort(self):
    
        try:
            import _winreg
            t = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, 'Software\\TorrentStream')
            needed_value =  _winreg.QueryValueEx(t , 'EnginePath')[0]
            path= needed_value.replace('tsengine.exe','')
            pfile= os.path.join( path,'acestream.port')
            gf = open(pfile, 'r')
            aceport=int(gf.read())
        except: 
            try:
                import _winreg
                t = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, 'Software\\AceStream')
                needed_value =  _winreg.QueryValueEx(t , 'EnginePath')[0]
                path= needed_value.replace('ace_engine.exe','')
                pfile= os.path.join( path,'acestream.port')
                gf = open(pfile, 'r')
                aceport=int(gf.read())
            except: 
                
                return False
        self.log.out('get aceport - %s'%aceport)
        return aceport
    def TSpush(self,command):
        
        self.push.out(command)
        try:
            self._sock.send(command+'\r\n')
        except: 
            self.push.out("!!!Error!!!")
    
    def get_link(self, index=0, title='', icon='', thumb=''):
        
        if Addon.getSetting('save')=='true' and Addon.getSetting('folder'): save=True
        else: save=False
        self.save=save
        self.title=title
        self.log.out("play")
        self.tsserv.ind=index
        self.progress.update(89,'Запускается воспроизведение','')
        for k,v in self.files.iteritems():
            if v==index: self.filename=urllib.unquote(k).replace('/','_').replace('\\','_')
        try:    
            avail=os.path.exists(self.filename.decode('utf-8'))
        except:
            try:
                avail=os.path.exists(self.filename)
                self.filename=self.filename.encode('utf-8')
            except: self.filename='temp.avi'
        self.log.out('Starting file:%s'%self.filename)
        
        if self.save and Addon.getSetting('folder'):
            try: self.filename=Addon.getSetting('folder')+self.filename
            except: 
                try:
                    self.filename=Addon.getSetting('folder').decode('utf-8')+self.filename
                except:
                    self.filename=None
                    self.save=False
        
        try: self.log.out('Get filename to save:%s'%self.filename)
        except: self.log.out('Get filename to save:%s'%self.filename.encode('utf-8'))
        try: tt=os.path.exists(self.filename.decode('utf-8'))
        except: tt=os.path.exists(self.filename)
        if self.save and tt:
            
            self.local=True
            try: self.tsserv.got_url=self.filename.decode('utf-8')
            except: self.tsserv.got_url=self.filename
            self.active=True
            self.progress.close()
            return self.tsserv.got_url
        spons=''
        if self.mode!='PID': spons=' 0 0 0'
        comm='START '+self.mode+ ' ' + self.url + ' '+ str(index) + spons
        self.TSpush(comm)
        self.progress.update(89,'Ожидание ссылки на воспроизведение','')
        while not self.tsserv.got_url and not self.progress.iscanceled() and not self.tsserv.err:
            self.progress.update(int(self.tsserv.proc),self.tsserv.label,self.tsserv.line)
            xbmc.sleep(200)
            if xbmc.abortRequested:
                self.log.out("XBMC is shutting down")
                break
        if self.tsserv.err: self.sm('Failed to load file')
        self.progress.update(100,'Запускается воспроизведение','')
        
        
        xbmc.sleep(500)
        if self.tsserv.event and self.save:
            if not tt:
                self.progress.update(0,"Сохраняю файл на диск"," ")
                try: comm='SAVE %s path=%s'%(self.tsserv.event[0]+' '+self.tsserv.event[1],urllib.quote(self.filename))
                except: comm='SAVE %s path=%s'%(self.tsserv.event[0]+' '+self.tsserv.event[1],urllib.quote(self.filenam.encode('utf-8')))
                self.TSpush(comm)
                self.tsserv.event=None
                succ=True
                
                while not tt and not self.progress.iscanceled():
                    if xbmc.abortRequested or self.progress.iscanceled():
                        self.log.out("XBMC is shutting down")
                        succ=False
                        break
                    xbmc.sleep(200)
                    try: tt=os.path.exists(self.filename.decode('utf-8'))
                    except: tt=os.path.exists(self.filename)
                if not succ: return False
                xbmc.sleep(1000)
            else: self.local=True
            try: self.tsserv.got_url=self.filename.decode('utf-8')
            except: self.tsserv.got_url=self.filename
            self.local=True
        self.active=True
        self.progress.close()
        return self.tsserv.got_url
        #self.local=True
        #return "G:\\0.7.5\\Fringe.s04e06.rus.LostFilm.TV.avi"
    
    def play_url_ind(self, index=0, title='', icon='', thumb=''):
        self.log.out('play')

        self.player=_TSPlayer()
        lnk=self.get_link(index,title,icon,thumb)
        if not lnk: return False
        self.player.link=lnk
        self.player.vod=True
        if self.progress:self.progress.close()
        item = xbmcgui.ListItem(title,thumb,icon,path=lnk)
        if self.local: 
            xbmcvfs.rename(lnk,lnk)
            xbmc.Player().play(lnk,item)

        else: 
            self.player.play(lnk,item)
            while self.player.active and not self.local: 
                self.loop()
                xbmc.sleep(300)
                if xbmc.abortRequested:
                    self.log.out("XBMC is shutting down")
                    break
            self.log.out('ended play')
      
    def loop(self):
        if self.local: return
        pos=self.pos
        self.log.out('1')
        if len(self.player.coms)>0:
            comm=self.player.coms[0]
            self.player.coms.remove(comm)
            self.TSpush(comm)
        self.log.out('2')
        if self.player.isPlaying():
            if self.player.getTotalTime()>0: cpos= int((1-(self.player.getTotalTime()-self.player.getTime())/self.player.getTotalTime())*100)
            else: cpos=0
            if cpos in pos: 
                pos.remove(cpos)
                comm='PLAYBACK '+self.player.link.replace('\r','').replace('\n','')+' %s'%cpos
                self.TSpush(comm)
        self.log.out('3')
        if self.tsserv.event and self.save:
            self.log.out('Try to save file in loop')
            try: comm='SAVE %s path=%s'%(self.tsserv.event[0]+' '+self.tsserv.event[1],urllib.quote(self.filename))
            except: comm='SAVE %s path=%s'%(self.tsserv.event[0]+' '+self.tsserv.event[1],urllib.quote(self.filenam.encode('utf-8')))
            self.TSpush(comm)
            self.tsserv.event=None
            succ=True
            self.saved=True
        self.log.out('4')
        if self.saved:
            self.log.out('4.1')
            try: tt=os.path.exists(self.filename.decode('utf-8'))
            except: tt=os.path.exists(self.filename)
            if  self.player.isPlaying() and tt: 
                xbmc.sleep(3000)
                self.log.out('Start local file')
                self.tsserv.got_url=self.filename
                self.local=True
                self.sm('Start Local File')
                try: time1=self.player.getTime()
                except: time1=0
                
                i = xbmcgui.ListItem("***%s"%self.title)
                i.setProperty('StartOffset', str(time1))
                self.log.out('Play local file')
                
                try:
                    xbmcvfs.rename(self.filename.decode('utf-8'),self.filename.decode('utf-8'))
                    xbmc.Player().play(self.filename.decode('utf-8'),i)
                except: 
                    xbmcvfs.rename(self.filename,self.filename)
                    xbmc.Player().play(self.filename,i)
                self.local=True
                self.player.active=False 
                saved=False
                self.save=False

        self.log.out('loop succ')

    def load_torrent(self, torrent, mode, host=server_ip, port=aceport ):
        self.mode=mode
        self.url=torrent
        if not self.connect(): 
            
            return False
        if not self.ts_init(): 
            self.sm('Initialization Failed')
            return False
        self.conn=True
        self.progress.update(0,"Загрузка торрента","")
        
        if mode!='PID': spons=' 0 0 0'
        else: spons=''
        comm='LOADASYNC '+ str(random.randint(0, 0x7fffffff)) +' '+mode+' ' + torrent + spons
        self.TSpush(comm)

        while not self.tsserv.files and not self.progress.iscanceled():
            if xbmc.abortRequested:
                self.log.out("XBMC is shutting down")
                break
            if self.tsserv.err:
                self.log.out("Failed to load files")
                break
            xbmc.sleep(200)
        if self.progress.iscanceled(): 
            return False
        if not self.tsserv.files: 
            self.sm('Failed to load list files')
            return False
        self.filelist=self.tsserv.files
        self.file_count = self.tsserv.count
        self.files={}
        self.progress.update(89,'Загрузка','')
        if self.file_count>1:
            flist=json.loads(self.filelist)
            for list in flist['files']:
                self.files[urllib.unquote_plus(urllib.quote(list[0]))]=list[1]
        elif self.file_count==1:
            flist=json.loads(self.filelist)
            list=flist['files'][0]
            self.files[urllib.unquote_plus(urllib.quote(list[0]))]=list[1]

        self.progress.update(100,'Загрузка данных завершена','')
        
        return "Ok"

    def end(self):
        
        self.active=False
        comm='SHUTDOWN'
        if self.conn:self.TSpush(comm)
        self.log.out("Ending")
        try: self._sock.shutdown(socket.SHUT_WR)
        except: pass
        if self.tsserv: self.tsserv.active=False
        if self.tsserv: self.tsserv.join()
        self.log.out("end thread")
        self._sock.close()
        self.log.out("socket closed")
        if self.progress:self.progress.close()
        
    def __del__(self):

        Addon.setSetting('active','0')
        
class TSServ(threading.Thread):

    def __init__(self,_socket):
        self.pkey='n51LvQoTlJzNGaFxseRK-uvnvX-sD4Vm5Axwmc4UcoD-jruxmKsuJaH0eVgE'
        threading.Thread.__init__(self)
        self.log=Logger("TSServer")
        self.inc=Logger('IN')
        self.log.out("init")
        self.sock=_socket
        self.daemon = True
        self.active = True
        self.err = False
        self.buffer=65020
        self.temp=""
        self.msg=None
        
        self.version=None

        self.fileslist=None
        self.files=None
        self.key=None
        self.count=None
        self.ind=None
        
        self.got_url=None
        self.event=None
        self.proc=0
        self.label=''
        self.line=''
        self.pause=False
    def run(self):
        while self.active and not self.err:

            try:
                self.last_received=self.sock.recv(self.buffer)
            except: self.last_received=''

            ind=self.last_received.find('\r\n')
            cnt=self.last_received.count('\r\n')

            if ind!=-1 and cnt==1:
                self.last_received=self.temp+self.last_received[:ind]
                self.temp=''
                self.exec_com()
            elif cnt>1:
                fcom=self.last_received
                ind=1
                while ind!=-1:
                    ind=fcom.find('\r\n')
                    self.last_received=fcom[:ind]
                    self.exec_com()
                    fcom=fcom[(ind+2):]
            elif ind==-1: 
                self.temp=self.temp+self.last_received
                self.last_received=None



        self.log.out('Daemon Dead')
                
    def exec_com(self):
        
        self.inc.out(self.last_received)
        line=self.last_received
        comm=self.last_received.split(' ')[0]
        params=self.last_received.split(' ')[1::]

        self.msg=line
        print comm
        if comm=='HELLOTS':
            try: self.version=params[0].split('=')[1]
            except: self.version='1.0.6'
            try: 
                if params[2].split('=')[0]=='key': self.key=params[2].split('=')[1]
            except: 
                try: self.key=params[1].split('=')[1]
                except: self.key=None
            
        elif comm=='LOADRESP':
            fil = line
            ll= fil[fil.find('{'):len(fil)]
            self.fileslist=ll

            json_files=json.loads(self.fileslist)
            try:
                aa=json_files['infohash']
                if json_files['status']==2:
                    self.count=len(json_files['files'])
                if json_files['status']==1:
                    self.count=1
                if json_files['status']==0:
                    self.count=None
                self.files=self.fileslist.split('\n')[0]
                self.fileslist=None
                self.log.out("files:%s"%self.files) 
            except:
                self.count=None
                self.fileslist=None
                self.err=True
        elif comm=='EVENT':
            if self.last_received.split(' ')[1]=='cansave':
                event=self.last_received.split(' ')[2:4]
                ind= event[0].split('=')[1]
                if int(ind)==int(self.ind): self.event=event
            if self.last_received.split(' ')[1]=='getuserdata':
                self.sock.send('USERDATA [{"gender": 1}, {"age": 3}]\r\n')
                
        elif comm=='START' or comm=='PLAY': 
            servip=Addon.getSetting('ip_addr')
            self.got_url=self.last_received.split(' ')[1].replace('127.0.0.1',servip) # если пришло PLAY URL, то забираем себе ссылку
            self.log.out('Get Link:%s'%self.got_url)
            self.params=self.last_received.split(' ')[2:]
            if 'stream=1' in self.params: self.log.out('Live Stream')
            else: self.log.out('VOD Stream')
        elif comm=='RESUME': self.pause=0
        elif comm=='PAUSE': self.pause=1   
        if comm=="STATUS": self.showStats(line)   
        
    def showStats(self,params):
        params=params.split(' ')[1]
        ss=re.compile('main:[a-z]+',re.S)
        s1=re.findall(ss, params)[0]
        st=s1.split(':')[1]
        self.proc=0
        self.label=" "
        self.line=" "
        
        if st=='idle':
            self.label='Простаивание'
        elif st=='starting':
            self.label='Запускается'
        elif st=='err':
            self.label='Ошибка движка'
            self.err="dl"
        elif st=='check': 
            self.label='Проверка'
            self.proc=int(params.split(';')[1])
        elif st=='prebuf': 
        
            self.proc=int( params.split(';')[1] )+0.1
            self.label='Предварительная буферизация'
            self.line='Сиды:%s Скорость:%sKb/s'%(params.split(';')[8],params.split(';')[5])  
        elif st=='loading':
            self.label='Загружается' 
    def end(self):
        self.active = False
        self.daemon = False
        self.log.out('Daemon Fully Dead')
        