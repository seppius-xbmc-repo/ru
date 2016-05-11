import os

import xbmc
import xbmcvfs
try:
    import sqlite3
    from sqlite3 import dbapi2 as sqlite
except:
    pass


# Originally posted by dimnik @ xbmc.ru
def get_play_count(filename):
    # Obtaining playback counter
    play_count = False
    if not filename or sqlite is None:
        return play_count

    # get path to database and determine videobase filename
    basepath = xbmc.translatePath("special://database")
    for basefile in xbmcvfs.listdir(basepath)[1]:
        if 'MyVideos' in basefile:
            videobase = basefile
            # connect to database
            db = sqlite.connect(os.path.join(basepath, videobase))
            try:
                sqlcur = db.execute('SELECT playCount FROM files WHERE strFilename like ?', ('%'+filename+'%',))
                res_playCount = sqlcur.fetchall()
                if res_playCount:
                    # check in the result data for at the least one played current file
                    if any(plcount > 0 for plcount in res_playCount):
                        play_count = True
            except:
                print 'Error connection to table file. Database is may be busy'
            db.close()

    return play_count
