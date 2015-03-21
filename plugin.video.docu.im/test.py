#-------------------------------------------------------------------------------
# Юppod decoder (for serialu.net)
#-------------------------------------------------------------------------------

# hash = "0123456789WGXMHRUZID=NQVBLihbzaclmepsJxdftioYkngryTwuvihv7ec41D6GpBtXx3QJRiN5WwMf=ihngU08IuldVHosTmZz9kYL2bayE"

def Decode(param):
    #-- define variables
    loc_3 = [0,0,0,0]
    loc_4 = [0,0,0]
    loc_2 = ''
    #-- define hash parameters for decoding
    dec = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='
    hash1 = ["Z", "v", "6", "W", "m", "y", "g", "X", "b", "o", "V", "d", "k", "t", "M", "Q", "u", "5", "D", "e", "J", "s", "z", "f", "L", "="];
    hash2 = ["a", "G", "9", "w", "1", "N", "l", "T", "I", "R", "7", "2", "n", "B", "4", "H", "3", "U", "0", "p", "Y", "c", "i", "x", "8", "q"];

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
            try:
                loc_2 += unichr(loc_4[j])
            except:
                pass
            j = j + 1

        i = i + 4;

    return loc_2

#-------------------------------------------------------------------------------
str = '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ZuayZnFMXwgt4E6=oXtPZg5iS57vXneBZvhj41h1avmvsdoT7Xgw77ee7F7ws7o5Sk2z71cm5jFZ4m73HjYg7mFU77HWO5e3w1hzodfrJg2c2woJ51fjpjt9X5E6P7Wz8FWzZwosbjesbjbiyihsbkDcpmWzJd6BIw732FWzOgWzTFfm40HN4Ffs2XAD4itsTQ5Wy0HfTFfm40Hiagfs2XADy0ysTQ5Wy0HNTFfm40HiOFfs2XAD4dosbzfsb1aeIv7sbjesbkYDITA98N6dZwogINUnIdym81gBOjEU4i5Gav6j2S6Bs0H9wuluSugipktDJDYHS1JfXQetoEyDHwajHXhDHwg=Zu2SsSf2PdFmavgGSwUnaTl6piAVxSauITyt2ToR5dgkIjmj4gaUavmwp7li5ktz7m5UX7oF2nm=ZuayZnFMXwgt4E6=oXtPZg5iS57vXneBZvhj41h1avmvsdoT7Xgw77ee7F7ws7o5Sk2z71cm5jFZ4m73HjYg7mFU77HWO5e3w1hzodfrJg2c2woJ51fjpjt9X5E6P7Wz8FWzZwosbjesbjbiyigsbkDcpmWzJd6BIw732FWzOgWzTFfm40Hfygfs2XAD4itsTQ5Wy0ynTFfm40HiaFfs2XAD4iAlTFfm40HfyC2sTQ5Wy0EWTFfm40HD4Ffs2XAD4dFsbzfsb1aeIv7sbjesbkYDITA98N6dZwogINUnIdym81gBOjEU4i5Gav6j2S6Bs0H9wDmCSTh1HnFQXv2aZ1h1aEYDpge0X1mBIQ78557Usw2c4Nf2PdFmavgGSwUnaTl6piAVxSauITyt2ToR5dgkIjmj4gaUavmwp7li5ktz7m5UX7oF2nm=ZuayZnFMXwgt4E6=oXtPZg5iS57vXneBZvhj41h1avmvsdoT7Xgw77ee7F7ws7o5Sk2z71cm5jFZ4m73HjYg7mFU77HWO5e3w1hzodfrJg2c2woJ51fjpjt9X5E6P7Wz8FWzZwosbjesbjbiO0tsbkDcpmWzJd6BIw732FWzOgWzTFfm40HfaFfs2XAD4d7sTQ5Wy0HfTFfm40HD4gfs2XADy0tsTQ5Wy04WTFfm40HiyFfs2XAD4itsTQ5Wy0yjTFfm40HD4mfs2XADy0Fsbzfsb1aeIv7sbjesbkYDITA98N6dZwogINUnIdym81gBOjEU4i5Gav6j2S6Bs0H9wiFvJnldXkeda0YoIEeg7X7y57Yo2nHm7j7PIu7P7iyPHzf2PdFmavgGSwUnaTl6piAVxSauITyt2ToR5dgkIjmj4gaUavmwp7li5ktz7m5UX7oF2nm=ZuayZnFMXwgt4E6=oXtPZg5iS57vXneBZvhj41h1avmvsdoT7Xgw77ee7F7ws7o5Sk2z71cm5jFZ4m73HjYg7mFU77HWO5e3w1hzodfrJg2c2woJ51fjpjt9X5E6P7Wz8FWzZwosbjesbjbiO0FsbkDcpmWzJd6BIw732FWzOgWzTFfm40HfyFfs2XAD4iasTQ5Wy04mTFfm40HiJStsTQ5Wy0F1TFfm40Hia7fs2XADy0YsTQ5Wy0HWTFfm40Hia7fs2XADy0hsTQ5Wy04MTFfm40HD4gfs2XAD4i7sTQ5Wy0yzTFfm40HDJmWz8FWza1gca7WzOgWzskoBs0RG8uaeav7G81oGJu53ZwD94XniyS6nIdym8dmWy0eISTt4oQY1aiYr5mhRawUfSdBKJX75owmcJ5yT5dBJ4XoB8FD/JT7nZw6YI1ogp0mV40B6Yk2BsDFm2vhXZw23Pw4N7kgnI7aUw0ySsvYT7Xgy7E7dXwer2nm=HThyZ5EWXdeF4E6=7XyYo5aOS1mRZv4NZvanI5aiaF27O7a7w1g577af7FoK2dYwZi7S47Ri7wUC417T5Tg770AUS1UZZvYQIvBz7dfmaFhSIvy94QeyHXD6TCbcTCYeaFWzOgWz4j4M4gWzxSfVTCYjIdmBawUDTCb9TCYsTQ5Wy0F1TFfm40HD4Ffs2XAD4ihsTQ5Wy0ynTFfm40HDygfs2XADyvblTFfm40Hi4ztsTQ5Wy0HNTFfm40Hi4Ffs2XADy0ysTQ5Wy0onTFfm40HD4Ffs2XAD4i7sbzfsb1aeIv7sbjesbkYDITA98N6dZwogINUnIdym81gBOjEU4i5Gav6j2S6Bs0H9wdYMZ1fosugJpv2NyjHNyF7f4vhNIgYKo5mvsQYEOQyHoSf2PdFmavgGSwUnaTl6piAVxSauITyt2ToR5dgkIjmj4gaUavmwp7li5ktz7m5UX7oF2nm=ZuayZnFMXwgt4E6=oXtPZg5iS57vXneBZvhj41h1avmvsdoT7Xgw77ee7F7ws7o5Sk2z71cm5jFZ4m73HjYg7mFU77HWO5e3w1hzodfrJg2c2woJ51fjpjt9X5E6P7Wz8FWzZwosbjesbjbiO0ysbkDcpmWzJd6BIw732FWzOgWzTFfm40HfJgfs2XAD4i7sTQ5Wy0ygTFfm40HiaFfs2XAD4itsTQ5Wy0HWTFfm40HiyFfs2XAD4d5lTFfm40HfyFfs2XAD4iAlTFfm40Hf4gfs2XAD4ihsTQ5Wy0ynTFfm40HDymfs2XAD4ihsbzfsb1aeIv7sbjesbkYDITA98N6dZwogINUnIdym81gBOjEU4i5Gav6j2S6Bs0H9wD7gydgWavyewEfPa0nWZnor2ncNwvhQ21ae7Q4dpnh8XNf2PdFmavgGSwUnaTl6piAVxSauITyt2ToR5dgkIjmj4gaUavmwp7li5ktz7m5UX7oF2nm=ZuayZnFMXwgt4E6=oXtPZg5iS57vXneBZvhj41h1avmvsdoT7Xgw77ee7F7ws7o5Sk2z71cm5jFZ4m73HjYg7mFU77HWO5e3w1hzodfrJg2c2woJ51fjpjt9X5E6P7Wz8FWzZwosbjesbjbiO0osbkDcpmWzJd6BIw732FWzOgWzTFfm40HNymfs2XAD4i7sTQ5Wy0yzTFfm40Hia7fs2XAD4iYsTQ5Wy04mTFfm40HiJStsTQ5Wy04NbFfs2XAD4iasTQ5Wy04mTFfm40HiJgfs2XAD4i7sTQ5Wy04uTFfm40HiaFfs2XAD4d7sTQ5Wy04UbFfs2XAD4dysTQ5Wy04WTFfm40HD47fs2XAD4dFsTQ5Wy04mTCbcTCY1ZwfgTCb9TCYN2vmWOzLG21gnawL3av6j2SUeIXRfOX4m8doGJu5GITADOgBuadefo72F7g7go7a4y1m3Jg7eaDgayEyv7mRu2vmm454cTX6h2woeIDg3av7MPTcWOuD12dmiHT7DZFyeadM6JiYwpwoB7kgJ4mYWJg27O5m5oTayZ1BdXwetpEmeHXtPZn5WXde74DgFonUKIwhRJiYRa1oBokyn7m5U7g7ZZ7o77kF57EeuJgary7bfwjy7InbNa72op77540gKIgeRJn2cZdYTIQ7nwFYcJuRWpnmtPXmsbzfsb1gnTCb9TCbN4ilmTCY68QBsb1yGIwmgIkosbjesbgfs2XAD4XFsTQ5Wy04MTFfm40HiJgfs2XAD4dYsTQ5Wy04MbFfs2XAD4wFsTQ5Wy04MTFfm40HiyFWz8FWza1gca7WzOgWzskoBs0RG8uaeav7G81oGJu53ZwD94XniyS6nIdym8dmWy0eIa0a7OFhdI5m=owFoZ72vZFg5OTnuSDUUoue54vf4Xkgo8FD/JT7nZw6YI1ogp0mV40B6Yk2BsDFm2vhXZw23Pw4N7kgnI7aUw0ySsvYT7Xgy7E7dXwer2nm=HThyZ5EWXdeF4E6=7XyYo5aOS1mRZv4NZvanI5aiaF27O7a7w1g577af7FoK2dYwZi7S47Ri7wUC417T5Tg770AUS1UZZvYQIvBz7dfmaFhSIvy94QeyHXD6TCbcTCYeaFWzOgWz4j4MygWzxSfVTCYjIdmBawUDTCb9TCYsTQ5Wy0EWTFfm40Hi4gfs2XADy0tsTQ5Wy04WTFfm40Hi4Ffs2XAD4d4lTFfm40HfJgfs2XAD4ihsTQ5Wy0ynTFfm40HiJ7fs2XAD4d7sTQ5Wy0yzTFfm40HDJmfs2XAD4dosbzfsb1aeIv7sbjesbkYDITA98N6dZwogINUnIdym81gBOjEU4i5Gav6j2S6Bs0H9wDom5XYBInydI5mhpXFvZ7tO502BXindZkyUok2UIkhj5Nf2PdFmavgGSwUnaTl6piAVxSauITyt2ToR5dgkIjmj4gaUavmwp7li5ktz7m5UX7oF2nm=ZuayZnFMXwgt4E6=oXtPZg5iS57vXneBZvhj41h1avmvsdoT7Xgw77ee7F7ws7o5Sk2z71cm5jFZ4m73HjYg7mFU77HWO5e3w1hzodfrJg2c2woJ51fjpjt9X5E6P7Wz8FWzZwosbjesbjbiO02sbkDcpmWzJd6BIw732FWzOgWzTFfm40HfJ7fs2XAD4dYsTQ5Wy04mTFfm40Hia7fs2XAD4dasTQ5Wy04WTFfm40HD4gfs2XADy0tsTQ5Wy04WTCbcTCY1ZwfgTCb9TCYN2vmWOzLG21gnawL3av6j2SUeIXRfOX4m8doGJu5GITADOgB=7D7YyFeus5ED5ERU4ug071gG7gycwFeBOEm3ywYBIjlcTX6h2woeIDg3av7MPTcWOuD12dmiHT7DZFyeadM6JiYwpwoB7kgJ4mYWJg27O5m5oTayZ1BdXwetpEmeHXtPZn5WXde74DgFonUKIwhRJiYRa1oBokyn7m5U7g7ZZ7o77kF57EeuJgary7bfwjy7InbNa72op77540gKIgeRJn2cZdYTIQ7nwFYcJuRWpnmtPXmsbzfsb1gnTCb9TCbN4ilMTCY68QBsb1yGIwmgIkosbjesbgfs2XAD4wFsTQ5Wy0ygTFfm40HD4Ffs2XAD4d7sTQ5Wy0yzTFfm40HDJNtsTQ5Wy0EWTFfm40HD4Ffs2XADy0YsTQ5Wy0HiTFfm40HD4FWz8FWza1gca7WzOgWzskoBs0RG8uaeav7G81oGJu53ZwD94XniyS6nIdym8dmWy0eIIdUvZ1yDS72EOQtCwX7tHuedImAiovWDyv5UyQYwomFe8FD/JT7nZw6YI1ogp0mV40B6Yk2BsDFm2vhXZw23Pw4N7kgnI7aUw0ySsvYT7Xgy7E7dXwer2nm=HThyZ5EWXdeF4E6=7XyYo5aOS1mRZv4NZvanI5aiaF27O7a7w1g577af7FoK2dYwZi7S47Ri7wUC417T5Tg770AUS1UZZvYQIvBz7dfmaFhSIvy94QeyHXD6TCbcTCYeaFWzOgWz4j4MO7WzxSfVTCYjIdmBawUDTCb9TCYsTQ5Wy0bWTFfm40Hia7fs2XAD4iFsTQ5Wy04MTFfm40HiaCtsTQ5Wy0EiTFfm40HD4mfs2XAD4iosbzfsb1aeIv7sbjesbkYDITA98N6dZwogINUnIdym81gBOjEU4i5Gav6j2S6Bs0H9wDMDyX24ZgaSpn2t2gYo2go55gliZTt74d6e2uyv5n2i7Sf2PdFmavgGSwUnaTl6piAVxSauITyt2ToR5dgkIjmj4gaUavmwp7li5ktz7m5UX7oF2nm=ZuayZnFMXwgt4E6=oXtPZg5iS57vXneBZvhj41h1avmvsdoT7Xgw77ee7F7ws7o5Sk2z71cm5jFZ4m73HjYg7mFU77HWO5e3w1hzodfrJg2c2woJ51fjpjt9X5E6P7Wz8FWzZwosbjesbjbiOXtsbkm2xSY6'


print Decode(str)