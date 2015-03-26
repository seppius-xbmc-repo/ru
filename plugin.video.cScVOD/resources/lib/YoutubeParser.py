import re
from urllib2 import Request, urlopen

class youtube_url:

    def get_youtube_link2(self, url):
        video_tulpe = []
        film_quality = []
        video_url = url
        error = None
        ret = None
        if url.find('youtube') > -1:
            split = url.split('=')
            ret = split.pop()
            if ret.startswith('youtube_gdata'):
                tmpval = split.pop()
                if tmpval.endswith('&feature'):
                    tmp = tmpval.split('&')
                    ret = tmp.pop(0)
            video_id = ret
            video_url = None
            try:
                answer = (urlopen(Request('http://93.188.161.233/parse/youtube_api.php?id=' + video_id, None, {'User-agent': 'Mozilla/5.0 nStreamVOD 0.1',
                                                                                                                     'Connection': 'Close'})).read())
                reg = re.findall('<iframe src="(.*?)" quality="(.*?)"/>', answer)
                for src, quality in reg:
                    video_url = src
                    break
            except Exception as ex:
                print 'No Youtube video', ex
            return video_url




