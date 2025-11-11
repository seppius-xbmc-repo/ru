#!/usr/bin/python3
""" addons.xml generator """

from hashlib import md5
import xml.etree.ElementTree as ET
from pathlib import Path

class Generator:
    """
        Generates a new addons.xml file from each addons addon.xml file.
        Must be run from the root of the checked-out repo. Only handles
        single depth folder structure.
    """
    def __init__( self ):
        # generate file
        self._generate_addons_file()
        self._generate_md5_file()

    def _generate_addons_file(self):

        # final addons
        root = ET.Element("addons")
        # loop thru and add each addons addon.xml file
        for dir in [d for d in Path(".").iterdir()
                      if d.is_dir() and d.name != ".git" and d.name != ".svn"]:
            try:
                addon = ET.parse(dir / "addon.xml")
                root.append(addon.getroot())
            except Exception as e:
                # missing or poorly formatted addon.xml
                print(f'Excluding {dir / "addon.xml"} for {e}')
        addons = ET.ElementTree(root)
        ET.indent(addons)
        addons.write("addons.xml", encoding="utf-8", xml_declaration=True)

    def _generate_md5_file( self ):
        with open(Path(".") / "addons.xml", "rb") as file, \
             open(Path(".") / "addons.xml.md5", "wb") as file_md5:
            hash = md5(file.read())
            file_md5.write(hash.digest())

if ( __name__ == "__main__" ):
    # start
    Generator()
