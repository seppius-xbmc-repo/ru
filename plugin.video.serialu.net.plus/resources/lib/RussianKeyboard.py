# -*- coding: utf-8 -*-

import xbmcgui, xbmc, xbmcaddon

LANG_RU = 1
LANG_EN = 2
LETTERS_ENG_SMALL = u'abcdefghijklmnopqrstuvwxyz'
LETTERS_ENG_BIG   = u'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
LETTERS_RUS_SMALL = u'абвгдежзийклмнопрстуфхцчшщъыьэюя'
LETTERS_RUS_BIG   = u'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
SYMBOLS = u')!@#$%^&*([]{}-_=+;:\'",.<>/?\|`~'
MAP = {
  LANG_RU: {
    True:  LETTERS_RUS_BIG,
    False: LETTERS_RUS_SMALL,
  },
  LANG_EN: {
    True:  LETTERS_ENG_BIG,
    False: LETTERS_ENG_SMALL,
  },
}
BTN_BACKSPACE = 8
BTN_SPACE = 32
BTN_DONE = 300
BTN_SHIFT = 302
BTN_CAPS = 303
BTN_SYM = 304
BTN_IP = 307
BTN_LANG = 308
BTN_PREV = 305
BTN_NEXT = 306
BTN_DIGITS = range(48, 57 + 1)
BTN_LETTERS = range(65, 100 + 1)
BTN_SYMBOLS = BTN_DIGITS + BTN_LETTERS
LABEL_TEXT = 310
HEADER_TEXT = 311

class KeyboardWindow(xbmcgui.WindowXMLDialog):
  def __init__(self, *args, **kwargs):
    self.inputString = kwargs.get('default') or u''
    self.heading = kwargs.get('heading') or u''

    self.value = list()
    self.pos = 0
    #---
    self.STATE_SHIFT = False
    self.STATE_CAPS = False
    self.STATE_SYM = False
    self.STATE_LANG = LANG_RU
    xbmcgui.WindowXMLDialog.__init__(self, *args, **kwargs)

  def onInit(self):
    self.getControl(HEADER_TEXT).setLabel(self.heading)
    #--
    label = list(self.value)
    label.insert(self.pos, '[COLOR=FF00FF00]|[/COLOR]')
    self.getControl(LABEL_TEXT).setLabel("".join(label))
    #---
    self.confirmed = False
    self.updateState()

  def isConfirmed(self):
    return self.confirmed

  def getText(self):
    return self.inputString

  def getSymbol(self, code):
    try:
      idx = BTN_SYMBOLS.index(code)
    except: return u''

    if idx <= 9:
      return unicode(idx)

    if self.STATE_SYM:
      array = SYMBOLS
    elif self.STATE_LANG in [LANG_RU, LANG_EN]:
      array = MAP[self.STATE_LANG][self.STATE_SHIFT != self.STATE_CAPS]

    if len(array) > idx - 10:
      return unicode(array[idx - 10])

    return ''

  def updateState(self):
    for i in range(len(BTN_SYMBOLS)):
      c_code = BTN_SYMBOLS[i]
      c = self.getControl(c_code)
      symbol = self.getSymbol(c_code)
      if len(symbol) == 0: symbol = ' '
      c.setLabel(str(symbol.encode('utf-8')))

  def onClick(self, control_id):
    control = self.getControl(control_id)

    if control_id == BTN_SHIFT:
      self.STATE_SHIFT = control.isSelected()

    elif control_id == BTN_CAPS:
      self.STATE_CAPS = control.isSelected()

    elif control_id == BTN_SYM:
      self.STATE_SYM = control.isSelected()

    elif control_id == BTN_IP:
      dialog = xbmcgui.Dialog()
      value = dialog.numeric( 3, 'IP Address', '0.0.0.0' )
      self.value += list(value)
      self.pos += len(list(value))

    elif control_id == BTN_LANG:
      if self.STATE_SYM:
        self.STATE_SYM = False
        self.getControl(BTN_SYM).setSelected(False)
      else:
        if self.STATE_LANG == LANG_RU:
          self.STATE_LANG = LANG_EN
        else:
          self.STATE_LANG = LANG_RU

    elif control_id == BTN_SPACE:
      self.value.insert(self.pos, ' ')
      self.pos += 1

    elif control_id == BTN_PREV:
      if self.pos > 0: self.pos += -1

    elif control_id == BTN_NEXT:
      if self.pos < len(self.value): self.pos += 1

    elif control_id == BTN_BACKSPACE:
      if self.pos > 0:
        self.value.pop(self.pos-1)
        self.pos += -1

    elif control_id in BTN_SYMBOLS:
      symbol = self.getSymbol(control_id)
      if len(symbol) > 0:
        self.value.insert(self.pos, symbol)
        self.pos += 1
      self.STATE_SHIFT = False
      self.getControl(BTN_SHIFT).setSelected(False)

    elif control_id == BTN_DONE:
      text = ''.join(self.value)
      if not text: text = ''
      self.inputString = text.encode('utf-8')
      self.confirmed = True
      self.close()

    label = list(self.value)
    label.insert(self.pos, '[COLOR=FF00FF00]|[/COLOR]')
    self.getControl(LABEL_TEXT).setLabel("".join(label))
    self.updateState()

class Keyboard(object):
  def __init__(self, addon, default='', heading=''):
    self.confirmed = False
    self.inputString = default
    self.heading = heading
    self.Addon= addon

  def doModal(self):
    kwargs = {'default': self.inputString, 'heading': self.heading}
    self.win = KeyboardWindow("RussianDialogKeyboard.xml", self.Addon.getAddonInfo('path'), **kwargs)
    self.win.doModal()
    self.confirmed = self.win.isConfirmed()
    self.inputString = self.win.getText()
    del self.win

  def setHeading(self, heading):
    self.heading = heading

  def isConfirmed(self):
    return self.confirmed

  def getText(self):
    return self.inputString
