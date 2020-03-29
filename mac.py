import uuid,base64
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex

seperateKey = "d#~0^38J:" # 随意输入一组字符串
aesKey = "123456789abcdefg" # 加密与解密所使用的密钥，长度必须是16的倍数
aesIv = "abcdefg123456789" # initial Vector,长度要与aesKey一致
aesMode = AES.MODE_CBC  # 使用CBC模式

mac = uuid.uuid1()
mac.urn
print(uuid.uuid1())
print(uuid.uuid1().urn[-12:])

aes = AES.new(aesKey,aesMode,aesIv) #创建一个aes对象

en_text = aes.encrypt(uuid.uuid1().urn[-12:]+('\0'*4)) #加密明文
print(en_text)
en_text = base64.encodebytes(en_text) #将返回的字节型数据转进行base64编码
print(en_text)
en_text = en_text.decode('utf8') #将字节型数据转换成python中的字符串类型
print(en_text.strip())
basestrt="123456"
encodebytes=base64.encodebytes(basestrt.encode('utf-8'))
print(encodebytes)




