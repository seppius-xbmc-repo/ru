import re, os, urllib, urllib2, sys, urlparse
import xbmc, xbmcgui, xbmcplugin, xbmcaddon, xbmcvfs
import shutil
import subprocess
import HTMLParser
hpar = HTMLParser.HTMLParser()


class XPpod():
    #----------------- init ----------------------------------------------------
    def __init__(self, Addon):
        self.Addon = Addon
        self.url = []

        if Addon.getSetting('SWF_Path') == '':
            self.path = os.path.join(Addon.getAddonInfo('path'), r'resources', r'swf')
        else:
            self.path = Addon.getSetting('SWF_Path')

    #---------- get web page -------------------------------------------------------
    def get_HTML(self, url, post = None, ref = None):
        request = urllib2.Request(url, post)

        host = urlparse.urlsplit(url).hostname
        if ref==None:
            ref='http://'+host

        request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
        request.add_header('Host',   host)
        request.add_header('Accept', '*/*')
        request.add_header('Accept-Language', 'ru-RU')
        request.add_header('Referer', ref)

        try:
            f = urllib2.urlopen(request, timeout=360)
        except IOError, e:
            if hasattr(e, 'reason'):
               xbmc.log('We failed to reach a server.'+str(e.reason))
            elif hasattr(e, 'code'):
               xbmc.log('The server couldn\'t fulfill the request.'+str(e.code))

        html = f.read()

        return html

    #-------------------------------------------------------------------------------
    # Юppod decoder (for seasonvar.ru)
    #-------------------------------------------------------------------------------
    def Decode(self, param, swf_player = None, page_url = None, cj = None):
        #-- load cookies
        if cj:
            hr  = urllib2.HTTPCookieProcessor(cj)
            opener = urllib2.build_opener(hr)
            urllib2.install_opener(opener)

        is_OK = True
        #-- get hash keys
        f = open(xbmc.translatePath(os.path.join(self.Addon.getAddonInfo('path'), r'resources', r'lib', r'hash.key')), 'r')
        hash_key = f.read()
        f.close()
        rez = self.Decode_String(param, hash_key)

        print('-----------------')

        if not 'html://' in rez and not '/list.xml' in rez and not 'playlist' in rez and not '/playls/' in rez:
            if self.Addon.getSetting('External_PhantomJS') == 'true':
                url = 'http://'+self.Addon.getSetting('PhantomJS_IP')+':'+self.Addon.getSetting('PhantomJS_Port')
                values = {'swf_url' :	page_url}
                post = urllib.urlencode(values)
                try:
                    hash_key = self.get_HTML(url, post)
                except:
                    hash_key = self.get_HTML(url, post)

                rez = self.Decode_String(param, hash_key)

                if 'html:' in rez or '.xml' in rez or 'playlist' in rez or '/playls/' in rez:
                    #-- save new hash keys
                    swf = open(xbmc.translatePath(os.path.join(self.Addon.getAddonInfo('path'), r'resources', r'lib', r'hash.key')), 'w')
                    swf.write(hash_key)
                    swf.close()
                    #-- exit from search
                    is_OK = True

            elif os.path.isdir(self.path) == True:
                print '** Decompile SWF to get hash'
                hash_list = self.Get_SWF_Hash(swf_player, page_url)
                #-- assemble hash key
                hash_key = hash_list[0]+'\n'+hash_list[1]
                rez = self.Decode_String(param, hash_key)

                if 'html:' in rez or '.xml' in rez or 'playlist' in rez or '/playls/' in rez:
                    #-- save new hash keys
                    swf = open(xbmc.translatePath(os.path.join(self.Addon.getAddonInfo('path'), r'resources', r'lib', r'hash.key')), 'w')
                    swf.write(hash_list[0]+'\n'+hash_list[1])
                    swf.close()
                    #-- exit from search
                    is_OK = True

        if is_OK == False:
            rez = ''

        return rez

    #---------------------------------------------------------------------------
    def Decode_String(self, param, hash_key):
        try:
            #-- define variables
            loc_3 = [0,0,0,0]
            loc_4 = [0,0,0]
            loc_2 = ''

            #-- define hash parameters for decoding
            dec = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='
            hash1 = hash_key.split('\n')[0]
            hash2 = hash_key.split('\n')[1]

##            print '** Try to decode'
##            print '**     HASH1: '+hash1
##            print '**     HASH2: '+hash2

            #-- decode
            for i in range(0, len(hash1)):
                re1 = hash1[i]
                re2 = hash2[i]

                param = param.replace(re1, '___')
                param = param.replace(re2, re1)
                param = param.replace('___', re2)

            i = 0
            while i < len(param):
                j = 0
                while j < 4 and i+j < len(param):
                    loc_3[j] = dec.find(param[i+j])
                    j = j + 1

                loc_4[0] = (loc_3[0] << 2) + ((loc_3[1] & 48) >> 4);
                loc_4[1] = ((loc_3[1] & 15) << 4) + ((loc_3[2] & 60) >> 2);
                loc_4[2] = ((loc_3[2] & 3) << 6) + loc_3[3];

                j = 0
                while j < 3:
                    if loc_3[j + 1] == 64:
                        break

                    loc_2 += unichr(loc_4[j])

                    j = j + 1

                i = i + 4;
        except:
            loc_2 = ''

        return loc_2

    #---------------------------------------------------------------------------
    def Get_SWF_Hash(self, swf_player, page_url):
        #---- clean up SWF folder ----------------------------------------------
        try:
            print '** Clean up SWF folder'
            shutil.rmtree(os.path.join(self.path,'player-0'))
            xbmcvfs.delete(os.path.join(self.path,'player-0.abc'))
            xbmcvfs.delete(os.path.join(self.path,'player.swf'))
        except:
            print '** Failed to clean up SWF folder'
            pass

        #---- get SWF ----------------------------------------------------------
        url = swf_player
        swf = open(os.path.join(self.path, 'player.swf'), 'wb')
        post = None

        code = self.get_HTML(url, post, page_url) #'http://seasonvar.ru')
        swf.write(code)
        swf.close()

        zcode = code[0:3] #-- type of SWF compression

        #---- decode SWF -------------------------------------------------------
        startupinfo = None

        if zcode == 'CWS':
            if os.name == 'nt':
                prog = '"'+os.path.join(self.path,'swfdecompress.exe"')+' "'+os.path.join(self.path,'player.swf"')
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= 1
            else:
                prog = [os.path.join(self.path,'swfdecompress'), os.path.join(self.path,'player.swf')]

            try:
                process = subprocess.Popen(prog, stdin= subprocess.PIPE, stdout= subprocess.PIPE, stderr= subprocess.PIPE,shell= False, startupinfo=startupinfo)
                process.wait()
            except:
                print('ERROR 0')

        if os.name == 'nt':
            prog = '"'+os.path.join(self.path,'abcexport.exe"')+' "'+os.path.join(self.path,'player.swf"')
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= 1
        else:
            prog = [os.path.join(self.path,'abcexport'), os.path.join(self.path,'player.swf')]

        try:
            process = subprocess.Popen(prog, stdin= subprocess.PIPE, stdout= subprocess.PIPE, stderr= subprocess.PIPE,shell= False, startupinfo=startupinfo)
            process.wait()
        except:
            print('ERROR 1')

        if os.name == 'nt':
            prog = '"'+os.path.join(self.path, 'rabcdasm.exe"')+' "'+os.path.join(self.path,'player-0.abc"')
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= 1
        else:
            prog = [os.path.join(self.path,'rabcdasm'), os.path.join(self.path,'player-0.abc')]

        try:
            process = subprocess.Popen(prog, stdin= subprocess.PIPE, stdout= subprocess.PIPE, stderr= subprocess.PIPE,shell= False, startupinfo=startupinfo)
            process.wait()
        except:
            print('ERROR 2')

        #---- grab hash for decoder ----------------------------------------------------
        fname = os.path.join(self.path,'player-0','com','uppod', 'Uppod.class.asasm')

        f = open(fname, 'r')
        code = f.read()
        f.close

        hash_list = []

        for rec in re.compile('findpropstrict      QName\(PackageNamespace\(""\), "Array"\)(.+?)constructprop', re.MULTILINE|re.DOTALL).findall(code):
            hash = ''
            for l in rec.replace(' ','').replace('\n','').split('pushstring'):
                if l <> '':
                    hash += l.replace('"','')
            if hash <> '':
                hash_list.append(hash)

        return hash_list
