#!/usr/bin/python
# -*- coding: utf-8 -*-
# Writer (c) 2013, otaranda@hotmail.com
# Rev. 1.2.3

import os, sys
import xbmc, xbmcaddon, xbmcgui
from pyxbmct.addonwindow import *

__addon__ = xbmcaddon.Addon()
__addonversion__ = __addon__.getAddonInfo('version')
__addonid__ = __addon__.getAddonInfo('id')
__addonname__ = __addon__.getAddonInfo('name')
__addon_path__ = __addon__ .getAddonInfo('path').decode('utf-8')
__addon_lng__ = __addon__ .getLocalizedString

_SERVICE_ID_ = 'script.service.rodina.tv'
_RODINA_ID_ = 'plugin.video.rodina.tv'

def log(message, level = 1):
    print '[%s LOG]: %s' % (__addonname__, message.encode('utf8'))


class RodinaService:

    def __init__(self):
        self.Player = RodinaPlayer()
        self._daemon()

    def _daemon(self):
        while not xbmc.abortRequested:
            xbmc.sleep(1000)

        log('abort requested')


class RodinaPlayer(xbmc.Player):

    def __init__(self):
        self.arch_play = 'false'
        self.lng = {'title' : __addon_lng__(30900)}
            
        xbmcaddon.Addon(_RODINA_ID_).setSetting('arch_on', 'false')

        
#    def onPlayBackStarted(self):
#        log('player starts')
#        self.arch_play = xbmcaddon.Addon(_RODINA_ID_).getSetting('arch_on')
#        if(self.arch_play == 'true'):
#            self.vwin = VideoWin()
#            self.vwin.doModal()
         

    def onPlayBackEnded(self):
        self.onPlayBackStopped()

    def onPlayBackStopped(self):
#        log('player stops')
        self.arch_play = 'false'
        xbmcaddon.Addon(_RODINA_ID_).setSetting('arch_on', 'false')

#    def onPlayBackPaused(self):
#        log('player pauses')

#    def onPlayBackResumed(self):
#        log('player resumes')

    def onPlayBackSeek(self, stime, seekOffset):
        log('## Playback Seek ##')
#        log('#seekOffset: %s #' % seekOffset)
#        log('#time: %s #' % stime)
        self.newSeek()
        
    def onPlayBackSeekChapter(self, chapter):
        log('## Playback BackSeekChapter')
#        log('#chapter: %s #' % chapter)
        self.newSeek()

    def onPlayBackSpeedChanged(self, speed):
        log('## Playback BackSpeedChanged')  
#        log('#speed: %s #' % speed)
        self.newSeek()   
        
    def newSeek(self):
        log('## New Playback Seek ##')
        self.arch_play = xbmcaddon.Addon(_RODINA_ID_).getSetting('arch_on')
        if self.arch_play == 'true':        
            stime = self.getTime()
            self.pause()
            
            pystep = MyPyStep(self.lng['title'])
            pystep .doModal()
            seek = pystep.hvalue + pystep.value - 50.0
            del pystep
            
            if seek != None and seek != 0:
                seek = int(seek * 60)
                params = 'mode=seek&time=%s&seek=%s' % (int(float(stime)), seek)
                script = 'special://home/addons/%s/default.py' % 'plugin.video.rodina.tv'
                xbmc.executebuiltin('XBMC.RunScript(%s, %d, %s)' % (script, 99, params))
                
            self.pause()
      
ACTION_PREVIOUS_MENU = 10
ACTION_SELECT_ITEM = 7
ACTION_HIGHLIGHT_ITEM = 8
ACTION_PARENT_DIR = 9
ACTION_BACK  = 92

ACTION_MOUSE_LEFT_CLICK   =    100
ACTION_MOUSE_DOUBLE_CLICK =    103
ACTION_MOUSE_WHEEL_UP     =    104
ACTION_MOUSE_WHEEL_DOWN   =    105


class MyPyStep(AddonDialogWindow):

    def __init__(self, title=''):
        # Call the base class' constructor.
        super(MyPyStep, self).__init__(title)
        
        self.lng = {'label' : __addon_lng__(30901),
                    'min'   : __addon_lng__(30902),
                    'cancel': __addon_lng__(30903),
                    'ok'    : __addon_lng__(30904),
                    'sec'   : __addon_lng__(30905),
                    'hour'  : __addon_lng__(30906) }
                    
        # Set width, height and the grid parameters
        self.setGeometry(800, 300, 5, 7)
        # Call set controls method
        self.set_controls()
        # Call set navigation method.
        self.set_navigation()
        # Connect exit events
        self.connectEventList([ACTION_NAV_BACK, ACTION_PREVIOUS_MENU, ACTION_PARENT_DIR], self.close)

        self.value = 50.0
        self.hvalue = 0

    def set_controls(self):
        # Image control
        self.title = Label(self.lng['label'], alignment=ALIGN_CENTER)
        self.placeControl(self.title, 0, 0, columnspan=7)
        # Text label
        self.label = Label('0 ' + self.lng['min'] + ' 0 ' + self.lng['sec'],
                            alignment=ALIGN_CENTER)
        self.placeControl(self.label, 2, 0, columnspan=7)
        
        self.slider = Slider()
        self.placeControl(self.slider, 3, 2, columnspan=3)
        self.slider.setPercent(50)
        
        # Connect key and mouse events for slider update feedback.
        self.connectEventList([ ACTION_MOVE_LEFT, 
                                ACTION_MOVE_RIGHT,
                                ACTION_HIGHLIGHT_ITEM,
                                ACTION_MOUSE_DRAG, 
                                ACTION_MOUSE_LEFT_CLICK,
                                ACTION_MOUSE_DOUBLE_CLICK,
                                ACTION_MOUSE_WHEEL_UP,
                                ACTION_MOUSE_WHEEL_DOWN ], self.slider_update)
        self.connect(ACTION_SELECT_ITEM, self.slider_enter)
        
        # Cancel button
        self.cancel_button = Button(self.lng['cancel'])
        self.placeControl(self.cancel_button, 4, 1, columnspan=2)
        # Connect Cancel button
        self.connect(self.cancel_button, self.close)

        # Ok button
        self.ok_button = Button(self.lng['ok'])
        self.placeControl(self.ok_button, 4, 4, columnspan=2)
        # Connect Ok button
        self.connect(self.ok_button, self.Ok)
        
        # plus 30 button
        self.p30_button = Button('+30 %s'%self.lng['sec'])
        self.placeControl(self.p30_button, 3, 5)
        self.connect(self.p30_button, self.p30)        

        # plus 5 button
        self.p5_button = Button('+5 %s'%self.lng['min'])
        self.placeControl(self.p5_button, 3, 6)
        self.connect(self.p5_button, self.p5)
        
        # minus 30 button
        self.m30_button = Button('-30 %s'%self.lng['sec'])
        self.placeControl(self.m30_button, 3, 1)
        self.connect(self.m30_button, self.m30)        

        # minus 5 button
        self.m5_button = Button('-5 %s'%self.lng['min'])
        self.placeControl(self.m5_button, 3, 0)
        self.connect(self.m5_button, self.m5)  
        
        # plus 60 button
        self.p60_button = Button('+60 %s'%self.lng['min'])
        self.placeControl(self.p60_button, 2, 6)
        self.connect(self.p60_button, self.p60)      
        
        # minus 60 button
        self.m60_button = Button('-60 %s'%self.lng['min'])
        self.placeControl(self.m60_button, 2, 0)
        self.connect(self.m60_button, self.m60)  
                
               
    def set_navigation(self):
        """Set up keyboard/remote navigation between controls."""
        self.cancel_button.controlUp(self.slider)
        self.cancel_button.controlDown(self.slider)
        self.cancel_button.controlLeft(self.m30_button)
        self.cancel_button.controlRight(self.ok_button)
        
        self.ok_button.controlUp(self.slider)
        self.ok_button.controlDown(self.slider)
        self.ok_button.controlLeft(self.cancel_button)
        self.ok_button.controlRight(self.p30_button)
        
        self.slider.controlUp(self.cancel_button)
        self.slider.controlDown(self.ok_button)
        
        self.p30_button.controlUp(self.slider)
        self.p30_button.controlDown(self.ok_button)
        self.p30_button.controlLeft(self.ok_button)
        self.p30_button.controlRight(self.p5_button)        
        
        self.p5_button.controlUp(self.p60_button)
        self.p5_button.controlDown(self.ok_button)
        self.p5_button.controlLeft(self.p30_button)
        self.p5_button.controlRight(self.m5_button)   
        
        self.m30_button.controlUp(self.slider)
        self.m30_button.controlDown(self.cancel_button)
        self.m30_button.controlLeft(self.m5_button)
        self.m30_button.controlRight(self.cancel_button)     
        
        self.m5_button.controlUp(self.m60_button)
        self.m5_button.controlDown(self.cancel_button)
        self.m5_button.controlLeft(self.p5_button)
        self.m5_button.controlRight(self.m30_button)  

        self.p60_button.controlUp(self.ok_button)
        self.p60_button.controlDown(self.p5_button)
        self.p60_button.controlLeft(self.slider)
        self.p60_button.controlRight(self.m60_button) 

        self.m60_button.controlUp(self.cancel_button)
        self.m60_button.controlDown(self.m5_button)
        self.m60_button.controlLeft(self.p60_button)
        self.m60_button.controlRight(self.slider) 
        
        # Set initial focus.
        self.setFocus(self.slider)
        
    def label_update(self):
        # Update slider value label when the slider nib moves
        try:
            val = self.value - 50.0
            sval = '%d %s %d %s' % (int(val), self.lng['min'], 
                                abs(60*(val - int(val))), self.lng['sec'])
            if self.hvalue:
                sval = '%d %s %s' % (self.hvalue/60, self.lng['hour'], sval)
            self.label.setLabel( sval )
        except (RuntimeError, SystemError):
            pass

    def slider_update(self):
        # Update slider value label when the slider nib moves
        try:
            if self.getFocus() == self.slider:
                self.value = self.slider.getPercent()
                self.label_update()
                
        except (RuntimeError, SystemError):
            pass
            
    def slider_enter(self):
        try:
            if self.getFocus() == self.slider:
                self.slider_update()
                self.Ok()
        except (RuntimeError, SystemError):
            pass               
            
    def close(self):
        self.value = None
        self.hvalue = None
        super(MyPyStep, self).close()
        
    def Ok(self):
        super(MyPyStep, self).close()
        
    def p30(self):
        self.value += 0.5
        if self.value > 100.0: self.value = 100.0
        self.label_update()
        self.slider.setPercent(self.value)
        
    def p5(self):
        self.value += 5.0
        if self.value > 100.0: self.value = 100.0
        self.label_update()
        self.slider.setPercent(self.value)
        
    def m30(self):
        self.value -= 0.5
        if self.value < 0.0: self.value = 0.0
        self.label_update()
        self.slider.setPercent(self.value)
        
    def m5(self):
        self.value -= 5.0
        if self.value < 0.0: self.value = 0.0
        self.label_update()
        self.slider.setPercent(self.value)

    def p60(self):
        self.hvalue += 60.0
        self.label_update()
        
    def m60(self):
        self.hvalue -= 60.0
        self.label_update()
        

    def setAnimation(self, control):
        # Set fade animation for all add-on window controls
        control.setAnimations([('WindowOpen', 'effect=fade start=0 end=100 time=500',),
                                ('WindowClose', 'effect=fade start=100 end=0 time=500',)])
                                
                                                

if __name__ == '__main__':
    log('script version %s started' % __addonversion__)
    RodinaService()
    del RodinaPlayer
    del RodinaService
    log('script version %s stopped' % __addonversion__)


