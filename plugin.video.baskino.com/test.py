import base64

import binascii
import json

from Crypto.Cipher import AES

from lib.pyaes import Encrypter, AESModeOfOperationCBC

partner_id = 918
domain_id = 515601
_mw_adb = False
video_token = 'add4fb87365dc508'
e = '617adae21a8aedc4e13938619b62f4ecdd3b947cd64620569df257d333e4f11d'


def pad(s):
    block_size = 16
    return s + (block_size - len(s) % block_size) * chr(block_size - len(s) % block_size)


def unpad(s):
    return s[0:-ord(s[-1])]


class EncryptedData:
    def __init__(self):
        pass

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, separators=(',', ':'))


t = EncryptedData()
t.a = partner_id
t.b = domain_id
t.c = _mw_adb
t.d = "8156109e46b295466542f3587f35f0fe"
t.e = video_token
t.f = "Mozilla/5.0"

n = 'c46b534f9def34b0f2040a503d978eed'

r = t.toJSON()

key = e
iv = n
line = ""

encr = AESModeOfOperationCBC(binascii.a2b_hex(key), binascii.a2b_hex(iv))
encrypter = Encrypter(encr)
ciphertext = bytes()
ciphertext += encrypter.feed(r)
ciphertext += encrypter.feed()

encryptor = AES.new(binascii.a2b_hex(key), AES.MODE_CBC, binascii.a2b_hex(iv))
encrypted2 = encryptor.encrypt(pad(r))


print ("Cipher1 (CBC): ")
print (base64.standard_b64encode(ciphertext))
print ("Cipher2 (CBC): ")
print (base64.standard_b64encode(encrypted2))
