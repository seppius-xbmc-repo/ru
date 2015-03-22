import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'site-packages'))
from installer import invoke_installer

try:
    invoke_installer()

    from xbmctorrent import monkey_patches
    from xbmctorrent import plugin

    if __name__ == '__main__':
        plugin.run()

except Exception, e:
    import xbmc
    import traceback
    map(xbmc.log, traceback.format_exc().split("\n"))
    raise
