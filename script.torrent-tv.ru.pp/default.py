# Copyright (c) 2013 Torrent-TV.RU
# Writer (c) 2011, Welicobratov K.A., E-mail: 07pov23@gmail.com
# Edited (c) 2015, Vorotilin D.V., E-mail: dvor85@mail.ru

import sys
import defines

# append pydev remote debugger
if defines.DEBUG:
    # Make pydev debugger works for auto reload.
    # Note pydevd module need to be copied in XBMC\system\python\Lib\pysrc
    #Add "sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), '..')))" to 
    #d:\Program Files (x86)\Kodi\system\python\Lib\pysrc\_pydev_imps\_pydev_pluginbase.py
    try:
        import pysrc.pydevd as pydevd  # with the addon script.module.pydevd, only use `import pydevd`
        # stdoutToServer and stderrToServer redirect stdout and stderr to eclipse console
        pydevd.settrace('localhost', stdoutToServer=True, stderrToServer=True)
    except:
        t, v, tb = sys.exc_info()        
        sys.stderr.write("Error: {0}:{1} | You must add org.python.pydev.debug.pysrc to your PYTHONPATH.".format(t, v))
        import traceback
        traceback.print_tb(tb)
        del tb
        sys.exit(0)
    

import mainform 
from okdialog import OkDialog

def checkPort(params):
    if not defines.checkPort(params):
        dialog = OkDialog("okdialog.xml", defines.SKIN_PATH, defines.ADDON.getSetting('skin'))
        dialog.setText("Порт %s закрыт. Для стабильной работы сервиса и трансляций, настоятельно рекомендуется его открыть." % defines.ADDON.getSetting('outport'))
        dialog.doModal()

if __name__ == '__main__':
    if not defines.ADDON.getSetting('skin'):
        defines.ADDON.setSetting('skin', 'st.anger')
    if defines.ADDON.getSetting("skin") == "default":
        defines.ADDON.setSetting("skin", "st.anger")
    if not defines.ADDON.getSetting("login"):
        defines.ADDON.setSetting("login", "anonymous")
        defines.ADDON.setSetting("password", "anonymous")

    #thr = defines.MyThread(checkPort, defines.ADDON.getSetting("outport"))
    #thr.start()

    print defines.ADDON_PATH
    print defines.SKIN_PATH
    
    defines.MyThread(defines.Autostart, defines.AUTOSTART).start()
    
    w = mainform.WMainForm("mainform.xml", defines.SKIN_PATH, defines.ADDON.getSetting('skin'))
    w.doModal()
    defines.showMessage('Close plugin')
    del w
    