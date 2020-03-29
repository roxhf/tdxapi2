from MainServer import MoniterServer
from MainServer import ServerLicense
if __name__ == '__main__':
    # license = ServerLicense()
    # status = license.getLicenseInfo()
    # print(status)
    moniter=MoniterServer()
    moniter.start()