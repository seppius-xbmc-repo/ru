def Decode(param):
    #-- define variables
    loc_3 = [0,0,0,0]
    loc_4 = [0,0,0]
    loc_2 = ''
    #-- define hash parameters for decoding
    dec = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='
    hash1 = ["Z", "v", "6", "W", "m", "y", "g", "X", "b", "o", "V", "d", "k", "t", "M", "Q", "u", "5", "D", "e", "J", "s", "z", "f", "L", "="]
    hash2 = ["a", "G", "9", "w", "1", "N", "l", "T", "I", "R", "7", "2", "n", "B", "4", "H", "3", "U", "0", "p", "Y", "c", "i", "x", "8", "q"]


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
