#!/usr/bin/env python
# *
# *  Copyright (C) 2014-2015 Roman Miroshnychenko
# *  Copyright (C) 2012-2013 Garrett Brown
# *  Copyright (C) 2010      j48antialias
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
# *  along with XBMC; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# *
# *  Based on code by j48antialias:
# *  https://anarchintosh-projects.googlecode.com/files/addons_xml_generator.py

from __future__ import print_function
import os
import sys
import hashlib
from traceback import print_exc

# Compatibility with 3.0, 3.1 and 3.2 not supporting u'' literals
if sys.version < '3':
    import codecs
    open = codecs.open

    def u(x):
        return codecs.unicode_escape_decode(x)[0]
else:
    def u(x):
        return x


class Generator:
    '''
    Generates a new addons.xml file from each addons addon.xml file
    and a new addons.xml.md5 hash file. Must be run from the root of
    the checked-out repo. Only handles single depth folder structure.
    '''
    def __init__(self):
        # generate files
        self._generate_addons_file()
        self._generate_md5_file()
        # notify user
        print('Finished updating addons xml and md5 files')

    def _generate_addons_file(self):
        cwd = os.path.dirname(os.path.abspath(__file__))
        # addon list
        addons = os.listdir(cwd)
        # final addons text
        addons_xml = u('<?xml version=\'1.0\' encoding=\'UTF-8\' standalone=\'yes\'?>\n<addons>\n')
        # loop thru and add each addons addon.xml file
        for addon in addons:
            try:
                # skip any file or .svn folder or .git folder
                if not os.path.isdir(addon) or addon == '.svn' or addon == '.git':
                    continue
                # create path
                _path = os.path.join(addon, 'addon.xml')
                # split lines for stripping
                with open(_path, 'r', encoding='UTF-8') as fo:
                    xml_lines = fo.read().splitlines()
                # new addon
                addon_xml = ''
                # loop thru cleaning each line
                for line in xml_lines:
                    # skip encoding format line
                    if (line.find('<?xml') >= 0):
                        continue
                    # add line
                    if sys.version < '3':
                        addon_xml += unicode(line.rstrip() + '\n')
                    else:
                        addon_xml += line.rstrip() + '\n'
                # we succeeded so add to our final addons.xml text
                addons_xml += addon_xml.rstrip() + '\n\n'
                for zip_file in os.listdir(os.path.join(cwd, addon)):
                    if os.path.splitext(zip_file)[1] != '.zip':
                        continue
                    zip_name = os.path.join(cwd, addon, zip_file)
                    with open(zip_name, 'rb') as fo:
                        m = hashlib.md5(fo.read()).hexdigest()
                    with open(zip_name + '.md5', 'wb') as fo:
                        fo.write(m.encode('utf-8'))
            except Exception as e:
                # missing or poorly formatted addon.xml
                print('Excluding %s for %s' % (_path, e))
        # clean and add closing tag
        addons_xml = addons_xml.strip() + u('\n</addons>\n')
        # save file
        self._save_file(addons_xml.encode('UTF-8'), file='addons.xml')

    def _generate_md5_file(self):
        # create a new md5 hash
        with open('addons.xml', 'r', encoding='UTF-8') as fo:
            m = hashlib.md5(fo.read().encode('UTF-8')).hexdigest()

        # save file
        try:
            self._save_file(m.encode('UTF-8'), file='addons.xml.md5')
        except:
            # oops
            print('An error occurred creating addons.xml.md5 file!')
            print_exc()

    def _save_file(self, data, file):
        with open(file, 'wb') as fo:
            fo.write(data)


if __name__ == '__main__':
    # start
    Generator()