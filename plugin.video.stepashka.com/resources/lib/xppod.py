import base64

def Correction(path):
    fname = path+'/code.dat'
    f = open(fname, 'r')
    ret = base64.b64decode(f.read())
    f.close()
    return ret, '<string>', 'exec'


#-------------------------------------------------------------------------------
# ?ppod decoder (for seasonvar.ru)
#-------------------------------------------------------------------------------

def Decode(param):
    #-- define variables
    loc_3 = [0,0,0,0]
    loc_4 = [0,0,0]
    loc_2 = ''
    #-- define hash parameters for decoding
    dec = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='
    #hash1 = ["J", "p", "v", "n", "s", "R", "0", "3", "T", "m", "w", "u", "9", "x", "g", "a", "G", "L", "U", "X", "z", "t", "b", "7", "H", "="]
    #hash2 = ["f", "N", "W", "5", "e", "l", "V", "D", "y", "Z", "I", "i", "M", "o", "Q", "1", "B", "8", "2", "6", "c", "d", "4", "Y", "k", "C"]

    hash1 = ["G", "d", "R", "0", "M", "Y", "4", "v", "6", "u", "t", "i", "f", "c", "s", "l", "B", "5", "n", "2", "V", "Z", "J", "m", "L", "="]
    hash2 = ["1", "w", "Q", "o", "9", "U", "a", "N", "x", "D", "X", "7", "z", "H", "y", "3", "e", "g", "T", "W", "b", "8", "k", "I", "p", "r"]

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

    return loc_2