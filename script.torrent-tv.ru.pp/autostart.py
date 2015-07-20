import defines
import os
from xml.etree.ElementTree import ElementTree

print 'STARTUP TTVPROXY'
dom = ElementTree()
dom.parse(defines.ADDON_PATH + '/resources/settings.xml')
xset = None
skins = []
for set in dom.find('category').findall('setting'):
    if set.attrib['id'] == 'skin':
        skins.append(set.attrib['values'])
        xset = set

if os.path.exists(defines.DATA_PATH + '/resources/skins/'):
    dirs = os.listdir(defines.DATA_PATH + '/resources/skins/');
    xset.attrib['values'] = "st.anger|"+"|".join(dirs);
    dom.write(defines.ADDON_PATH + '/resources/settings.xml', 'utf-8')   
else:
    xset.attrib['values'] = "st.anger"
    dom.write(defines.ADDON_PATH + '/resources/settings.xml', 'utf-8')         