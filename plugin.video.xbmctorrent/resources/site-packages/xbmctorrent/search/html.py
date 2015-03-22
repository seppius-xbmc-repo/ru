# -*- coding: utf-8 -*-

import re, htmlentitydefs

RE = {
    'space': re.compile('[ ]{2,}', re.U|re.S),
    'cl': re.compile('[\n]{2,}', re.U|re.S),
    'br': re.compile('<\s*br[\s/]*>', re.U|re.S),
    'inner': re.compile('<[^>]*>[^<]+<\s*/[^>]*>', re.U|re.S),
    'html': re.compile('<[^>]*>', re.U|re.S),
    'entity': re.compile('&#?\w+;', re.U)
}

UNSUPPORT = {
    '&#151;': '-'
}

class Clear:
    def text(self, text, inner=False):
        text = self._unsupport(text).replace(u'\r', u'\n')
        text = RE['br'].sub(u'\n', text)
        if inner:
            text = RE['inner'].sub(u'', text)
        text = RE['html'].sub(u'', text)
        text = self.char(text)
        text = RE['space'].sub(u' ', text)
        return RE['cl'].sub(u'\n', text).strip()
    
    def string(self, text, space=u''):
        return self.text(text).replace(u'\n', space).strip()
    
    def char(self, text):
        return RE['entity'].sub(self._unescape, self._unsupport(text))
    
    def _unsupport(self, text):
        for tag, value in UNSUPPORT.iteritems():
            text = text.replace(tag, value)
        return text
    
    def _unescape(self, m):
        text = m.group(0)
        if text[:2] == u"&#":
            try:
                if text[:3] == u"&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text
