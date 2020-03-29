#read txt method two
#coding: utf-8
name=''
for line2 in open("./json.txt",mode='r',encoding = "utf-8"):
    #print(line2)
    line2=line2.strip()
    if line2=='':
        continue
    nameindex=line2.find('//')
    if nameindex>-1:
        name=line2.replace('//','')
    loadindex=line2.find('lpFuncLogonEx')
    if loadindex>-1:
        loadindex =loadindex+14
        line2=line2[loadindex:]
        line2=line2[:-2]
       # print(line2)
        line2arr=line2.split(',')
        #print(line2arr)
        #"55.XY", "61.132.54.83", 7718, "7.04", 1, 9, "1", "1", "1", "1", szErrInfo
        print(line2arr[0]+":{")
        print('"ip":'+line2arr[1]+',')
        print('"port":' + line2arr[2] + ',')
        print('"name":"' +name + '"')
        print('},')
        # "55.XY": {
        #              "ip": "61.132.54.83",
        #              "port": 7718,
        #              "name": "华泰证券"
        #          },
sss=''
for index in range(30):
    sss+='%s,'
print(sss)