#/*
# *
# * TuneIn Radio for XBMC.
# *
# * Copyright (C) 2013 Brian Hornsby
# *
# * This program is free software: you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation, either version 3 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program.  If not, see <http://www.gnu.org/licenses/>.
# *
# */

import xbmc
import xbmcgui
import sys
import os
import urllib
import urllib2
import urlparse
import xbmcsettings as settings
import xbmcutils as utils


def cancel_progressdialog(progressdialog):
    return progressdialog.iscanceled()


def update_progressdialog(addonsettings, progressdialog, downloadfile, bytes_so_far, chunk_size, total_size):
    percent = float(bytes_so_far) / total_size
    percent = int(round(percent * 99, 0))
    progressdialog.update(percent, os.path.basename(downloadfile), addonsettings.get_string(4002) % (bytes_so_far, total_size))


def __download(url, path, addonsettings, progressdialog=None, chunk_size=8192, cancelhook=None, reporthook=None):
    response = urllib2.urlopen(url)
    downloadfile = os.path.join(
        path, os.path.basename(urlparse.urlsplit(url)[2]))
    total_size = response.info().getheader('Content-Length').strip()
    total_size = int(total_size)
    bytes_so_far = 0
    result = True
    if os.path.exists(downloadfile):
        filename = os.path.basename(urlparse.urlsplit(url)[2])
        if not utils.yesno(addonsettings.get_string(4000), addonsettings.get_string(4003) % filename, addonsettings.get_string(4006)):
            xbmc.log('[XBMC Download] File already exists. Do not overwrite.',
                     xbmc.LOGINFO)
            return (False, downloadfile)
    file = open(downloadfile, 'wb')
    while 1:
        chunk = response.read(chunk_size)
        bytes_so_far += len(chunk)
        if not chunk:
            break
        if cancelhook and cancelhook(progressdialog):
            xbmc.log(
                '[XBMC Download] Download has been cancelled', xbmc.LOGINFO)
            if os.path.exists(downloadfile):
                os.remove(downloadfile)
            result = False
            break
        file.write(chunk)
        if reporthook:
            reporthook(addonsettings, progressdialog,
                       downloadfile, bytes_so_far, chunk_size, total_size)
    file.close()
    return (result, downloadfile)


def download(url, downloadpath, addonid, background=False, debug=False):
    if debug == True:
        xbmc.log('[XBMC Download] download', xbmc.LOGDEBUG)
        xbmc.log('[XBMC Download] url: %s' % url, xbmc.LOGDEBUG)
        xbmc.log(
            '[XBMC Download] downloadpath: %s' % downloadpath, xbmc.LOGDEBUG)
        xbmc.log('[XBMC Download] addonid: %s' % addonid, xbmc.LOGDEBUG)
        xbmc.log('[XBMC Download] background: %s' % background, xbmc.LOGDEBUG)

    result = (False, '')
    addonsettings = settings.Settings(addonid, sys.argv)
    if background == False:
        progressdialog = xbmcgui.DialogProgress()
        progressdialog.create(addonsettings.get_string(4000))
        progressdialog.update(0, addonsettings.get_string(4001))
    if not os.path.exists(downloadpath):
        os.makedirs(downloadpath)
    try:
        if background == False:
            result = __download(url, downloadpath, addonsettings, progressdialog, cancelhook=cancel_progressdialog, reporthook=update_progressdialog)
        else:
            result = __download(url, downloadpath, addonsettings)
    except urllib2.URLError, e:
        xbmc.log('[XBMC Download] URLError: %s' % (e), xbmc.LOGERROR)
        result = (False, None)

    if background == False:
        progressdialog.close()
    elif result[0] == True:
        filename = os.path.basename(urlparse.urlsplit(url)[2])
        command = 'Notification(%s, %s)' % (addonsettings.get_string(
            4000), (addonsettings.get_string(4004) % (filename)))
        xbmc.executebuiltin(command)
    else:
        filename = os.path.basename(urlparse.urlsplit(url)[2])
        command = 'Notification(%s, %s)' % (addonsettings.get_string(
            4000), (addonsettings.get_string(4005) % (filename)))
        xbmc.executebuiltin(command)

    return result

if __name__ == '__main__':
    result = download(sys.argv[1], urllib.unquote_plus(sys.argv[2]), sys.argv[
                      3], sys.argv[4] == 'True', sys.argv[5] == 'True')
