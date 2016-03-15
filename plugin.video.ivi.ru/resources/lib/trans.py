# -*- coding: utf-8 -*-
# -*- test-case-name: pytils.test.test_translit -*-
"""
Simple transliteration
"""

import re
#from pytils.utils import takes, returns

TRANSTABLE = (
        (u"'", u"'"),
        (u'"', u'"'),
        (u"‘", u"'"),
        (u"’", u"'"),
        (u"«", u'"'),
        (u"»", u'"'),
        (u"“", u'"'),
        (u"”", u'"'),
        (u"–", u"-"),  # en dash
        (u"—", u"-"),  # em dash
        (u"‒", u"-"),  # figure dash
        (u"−", u"-"),  # minus
        (u"…", u"..."),
        (u"№", u"#"),
        ## upper
        # three-symbols replacements
        (u"Щ", u"Sch"),
        # on russian->english translation only first replacement will be done
        # i.e. Sch
        # but on english->russian translation both variants (Sch and SCH) will play
        (u"Щ", u"SCH"),
        # two-symbol replacements
        (u"Ё", u"Yo"),
        (u"Ё", u"YO"),
        (u"Ж", u"Zh"),
        (u"Ж", u"ZH"),
        (u"Ц", u"Ts"),
        (u"Ц", u"TS"),
        (u"Ч", u"Ch"),
        (u"Ч", u"CH"),
        (u"Ш", u"Sh"),
        (u"Ш", u"SH"),
        (u"Ы", u"Yi"),
        (u"Ы", u"YI"),
        (u"Ю", u"Yu"),
        (u"Ю", u"YU"),
        (u"Я", u"Ya"),
        (u"Я", u"YA"),
        # one-symbol replacements
        (u"А", u"A"),
        (u"Б", u"B"),
        (u"В", u"V"),
        (u"Г", u"G"),
        (u"Д", u"D"),
        (u"Е", u"E"),
        (u"З", u"Z"),
        (u"И", u"I"),
        (u"Й", u"J"),
        (u"К", u"K"),
        (u"Л", u"L"),
        (u"М", u"M"),
        (u"Н", u"N"),
        (u"О", u"O"),
        (u"П", u"P"),
        (u"Р", u"R"),
        (u"С", u"S"),
        (u"Т", u"T"),
        (u"У", u"U"),
        (u"Ф", u"F"),
        (u"Х", u"H"),
        (u"Э", u"E"),
        (u"Ъ", u"`"),
        (u"Ь", u"'"),
        ## lower
        # three-symbols replacements
        (u"щ", u"sch"),
        # two-symbols replacements
        (u"ё", u"yo"),
        (u"ж", u"zh"),
        (u"ц", u"ts"),
        (u"ч", u"ch"),
        (u"ш", u"sh"),
        (u"ы", u"yi"),
        (u"ю", u"yu"),
        (u"я", u"ya"),
        # one-symbol replacements
        (u"а", u"a"),
        (u"б", u"b"),
        (u"в", u"v"),
        (u"г", u"g"),
        (u"д", u"d"),
        (u"е", u"e"),
        (u"з", u"z"),
        (u"и", u"i"),
        (u"й", u"j"),
        (u"к", u"k"),
        (u"л", u"l"),
        (u"м", u"m"),
        (u"н", u"n"),
        (u"о", u"o"),
        (u"п", u"p"),
        (u"р", u"r"),
        (u"с", u"s"),
        (u"т", u"t"),
        (u"у", u"u"),
        (u"ф", u"f"),
        (u"х", u"h"),
        (u"э", u"e"),
        (u"ъ", u"`"),
        (u"ь", u"'"),
        # Make english alphabet full: append english-english pairs
        # for symbols which is not used in russian-english
        # translations. Used in slugify.
        (u"c", u"c"),
        (u"q", u"q"),
        (u"y", u"y"),
        (u"x", u"x"),
        (u"w", u"w"),
        (u"1", u"1"),
        (u"2", u"2"),
        (u"3", u"3"),
        (u"4", u"4"),
        (u"5", u"5"),
        (u"6", u"6"),
        (u"7", u"7"),
        (u"8", u"8"),
        (u"9", u"9"),
        (u"0", u"0"),
        )  #: Translation table

RU_ALPHABET = [x[0] for x in TRANSTABLE] #: Russian alphabet that we can translate
EN_ALPHABET = [x[1] for x in TRANSTABLE] #: English alphabet that we can detransliterate
ALPHABET = RU_ALPHABET + EN_ALPHABET #: Alphabet that we can (de)transliterate


def detranslify(in_string):
	
    # в unicode
  #  try:
  #      russian = unicode(in_string)
  #  except UnicodeDecodeError:
  #      raise ValueError("We expects if in_string is 8-bit string," + \
  #                       "then it consists only ASCII chars, but now it doesn't. " + \
  #                       "Use unicode in this case.")
	russian = unicode(in_string)
	for symb_out, symb_in in TRANSTABLE:
		russian = russian.replace(symb_in, symb_out)

	return russian
