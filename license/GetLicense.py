# -*- coding: UTF-8 -*-
####################################
# TODO：从license.lic中解密出MAC地址
####################################
import os
import uuid
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
class ServerLicense:

    seperateKey = "9wshy&#)800"
    aesKey = "8652mk57jd%142$#"
    aesIv = "abc6789defg^&*45"
    aesMode = AES.MODE_CBC  # 使用CBC模式

    def getHwAddr(self,ifname):
        return uuid.uuid1().urn[-12:];

    def decrypt(self,text):
        try:
            cryptor = AES.new(self.aesKey, self.aesMode, self.aesIv)
            # destr=base64.b64decode( text)
            # print(destr)
            plain_text = cryptor.decrypt( a2b_hex(text.encode('utf-8')))
            print(type(plain_text))
            plain_text=str(plain_text,'utf-8')
            return plain_text.rstrip('\0')
        except Exception:
            print(Exception.args)
            return ""

    def getLicenseInfo(self,filePath = None):
        if filePath == None:
            filePath = "./license.lic"

        if not os.path.isfile(filePath):
            return False, "Invalid"

        encryptText = "";
        with open(filePath, "r") as licFile:
            encryptText = licFile.read()
            licFile.close()
        try:
            hostInfo = self.getHwAddr('eth0')
        except IOError:
            hostInfo = self.getHwAddr('eno1')

        decryptText = self.decrypt(encryptText)
        pos = decryptText.find(self.seperateKey)
        if -1 == pos:
            return False, "Invalid"
        licHostInfo = self.decrypt(decryptText[0:pos])
        #licenseStr = decryptText[pos + len(self.seperateKey):]
        # print licHostInfo, licenseStr

        if licHostInfo[:12] == hostInfo:
            return True
        else:
            exit()

if __name__ == "__main__":
    license=ServerLicense()
    status = license.getLicenseInfo()
    print( status)
