#coding: utf-8

from ctypes import *
import asyncio,json,logging,websockets, MySQLdb,os,uuid
from decimal import Decimal
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
            plain_text = cryptor.decrypt( a2b_hex(text.encode('utf-8')))
            plain_text=str(plain_text,'utf-8')
            return plain_text.rstrip('\0')
        except Exception:
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
            return False
        licHostInfo = self.decrypt(decryptText[0:pos])
        #licenseStr = decryptText[pos + len(self.seperateKey):]
        # print licHostInfo, licenseStr

        if licHostInfo[:12] == hostInfo:
            # print('授权成功')
            return True
        else:
            return False



class MoniterServer():
    # logging.basicConfig(level=logging.INFO,
    #                     format='%(asctime)s %(thread)d %(threadName)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    #                     datefmt='%a, %d %b %Y %H:%M:%S',
    #                     filename='out.log',
    #                     filemode='w',
    #                     handlers= FileHandler(StreamHandler())
    #                     )
    root_logger = logging.getLogger()

    qsid2ip = {}
    hllset = dict()
    result = create_string_buffer(1024 * 2048)
    err_info = create_string_buffer(4048 * 4048)
    hllDll=set()

    def loggg_r(self,dataline):
        print(dataline)
        self.root_logger.info(dataline)

    def TdApiXInit(self):
        hllDll = WinDLL("TdApiX.dll")
        hllDll.OpenTdx()

        clientID_int = c_int * 1
        clientID_arr = clientID_int()

        Category_int = c_int * 1
        Category_arr = Category_int()

        PriceType_int = c_int * 1
        PriceType_arr = PriceType_int()

        Gddm_char = c_char * 1
        Gddm_arr = Gddm_char()

        Zqdm_char = c_char * 1
        Zqdm_arr = Zqdm_char()

        Price_float = c_float * 1
        Price_arr = Price_float()

        Quantity_int = c_int * 1
        Quantity_arr = Quantity_int()
        return hllDll

    #hllDll = TdApiXInit()

    async def lid2hllDll(self,websocket, account_id):
        """
        :param websocket:
        :param lid:
        :param account:
        :return:
        """
        print(id)

        if str(account_id) in self.hllset:
            self. loggg_r('无需登录')
            return self.hllset[str(account_id)]
        else:
            if int(account_id) > 0:
                accsql = 'select * from lmq_stock_account  where id=' + str(account_id)
                account = self.execlesql(accsql, 1)
            else:
                return 0
            broker = str(account['broker'])
            qsid2ipdata = self.qsid2ip[broker]
            client_id = self.hllDll.LogonEx(c_char_p(str(account['broker']).encode('utf-8')),
                                       c_char_p(qsid2ipdata['ip'].encode('utf-8')),
                                       c_int(qsid2ipdata['port']),
                                       c_char_p(account['clienver'].encode('utf-8')),
                                       c_int(0), c_int(8),
                                       c_char_p(account['lid'].encode('utf-8')),
                                       c_char_p(account['lid'].encode('utf-8')),
                                       c_char_p(account['pwd'].encode('utf-8')),
                                       c_char_p(b"\0"), self.err_info)
            # hllset[lid]
            if client_id == -1:
                self.loggg_r('账号登陆错误')
                b = self.err_info.value.decode('gbk')
                data = self.make_result2arr(b)

                self.loggg_r( b)
                self.hllDll.CloseTdx()
                # await websocket.send('0')
            else:
                self.hllset[str(account['id'])] = client_id
            self.loggg_r('登录成功' + str(client_id))
            return client_id

    def loadqsid(loadqsid):

        data3 = json.load(open('./qsid2ip.json', 'r', encoding="utf-8"))
        # print(data3)
        return data3



    async def read_zhiling(self,websocket):
        while True:
            recv_str = await websocket.recv()
            return recv_str

    # CheckBroker检测证券账户
    # {"operation": "CheckBroker", "LID": "83939003888", "user": "83939003888", "password": "584520", "broker": 122,
    #  "clienver": "1.17"}


    async def BrokerLogin(self,websocket):
        # self.loggg_r(123)
        readjson = await self.read_zhiling(websocket)
        # '{"operation":"BrokerLogin","LID":"83939003888","user":"83939003888","password":"584520","broker":122,"clienver":null,"id":"31"}'
        readjson = json.loads(readjson)
        self.loggg_r(readjson)
        client_id = await self.lid2hllDll(websocket, readjson['id'])
        if client_id == -1:
            print('登陆错误')
            self.hllDll.CloseTdx()
            await websocket.send('0')
        else:
            self.hllDll.QueryData(client_id, c_int(0), self.result, self.err_info)
            print(client_id, self.result.value.decode('gbk'))
            await websocket.send(str(client_id))

    async def CheckBroker(self,websocket):
        self.loggg_r('----------------CheckBroker-------------------------')
        readjson = await self.read_zhiling(websocket)
        readjson = json.loads(readjson)
        print(readjson)
        hllDll = self.TdApiXInit()
        # result = create_string_buffer(1024 * 2048)
        # err_info = create_string_buffer(4048 * 4048)
        print(readjson['broker'])
        broker = str(readjson['broker'])
        qsid2ipdata = self.qsid2ip[broker]

        client_id = hllDll.LogonEx(c_char_p(broker.encode('utf-8')),
                                   c_char_p(qsid2ipdata['ip'].encode('utf-8')),
                                   c_int(qsid2ipdata['port'].encode('utf-8')),
                                   c_char_p(readjson['clienver'].encode('utf-8')),
                                   c_int(0), c_int(8),
                                   c_char_p(readjson['LID'].encode('utf-8')),
                                   c_char_p(readjson['LID'].encode('utf-8')),
                                   c_char_p(readjson['password'].encode('utf-8')),
                                   c_char_p(b"\0"), self.err_info)

        if client_id == -1:
            print('登陆错误')
            hllDll.CloseTdx()
            await websocket.send('0')
        else:
            hllDll.QueryData(client_id, c_int(0), self.result, self.err_info)
            print(client_id, self.result.value.decode('gbk'))
            await websocket.send(str(client_id))
            hllDll.Logoff(client_id)
            hllDll.CloseTdx()
        # await counter(websocket,'')
            self.loggg_r('----------------CheckBroker----------end---------------')

    def execlesql(self,sql, type=0):
        """
        :param sql:
        :param type:0 1 2
        :return:
        """
        dbconfig = json.load(open('config.json', 'r', encoding="utf-8"))
        db = MySQLdb.connect(dbconfig['hostname'], dbconfig['username'], dbconfig['password'], dbconfig['database'],
                             charset='utf8')
        # 使用 cursor() 方法创建一个游标对象 cursor
        data = [];
        cursor = db.cursor()
        try:
            if type == 0:
                cursor.execute(sql)
                db.commit()
            if type == 1:
                cursor.execute(sql)
                db.commit()
                data = cursor.fetchone()
                columns = [column[0] for column in cursor.description]
                data = dict(zip(columns, data))
            if type == 2:
                cursor = db.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute(sql)
                data = cursor.fetchall()
                db.commit()
        except:
            db.rollback()
        db.close()

        return data

    def getAccount(self,account_id):
        accsql = 'select * from lmq_stock_account  where id=' + str(account_id)
        account = self.execlesql(accsql, 1)
        self.loggg_r(account)
        return account

    # /*
    #  * 判断是否为A股股票
    #  */
    # public static function market_type($code){
    #     switch (substr($code,0,1)){
    #         case '0':return 1;break;
    #         case '3':return 1;break;
    #         case '6':return 2;break;
    #         default: return 5;break;//5、出错
    #     }
    # }


    async def Trade_CommitOrder(self,websocket, readjson, id):  # 下单
        # readjson = await read_zhiling(websocket)
        # json_encode(array('req' = > 'Trade_CommitOrder', 'rid' = > build_rid_no(),
        #   'para' = > array('Code' => $code, 'Count' => $count,
        #                   'EType' => $etype, 'OType' => $otype,
        #                     'PType' => $ptype, 'Price' => $price)));
        # await websocket.send('08551112512')
        self.loggg_r('----------------Trade_CommitOrder-------------------------')
        readjson = json.loads(readjson)
        print(readjson)
        para = readjson['para']
        Code = para['Code']
        Count = para['Count']
        EType = para['EType']  # 市场类型1深圳 2上海
        OType = para['OType']  # //1买入 2卖出
        PType = para['PType']  # //1、限价委托//5市价委托
        Price = para['Price']
        account = self.getAccount(id)
        if EType == 1:
            Gddm = account['sz_code']
        if EType == 2:
            Gddm = account['sh_code']
        # /// <summary>
        # /// 下委托交易证券
        # /// </summary>
        # /// <param name="ClientID">客户端ID</param>
        # /// <param name="Category">表示委托的种类，0买入 1卖出  2融资买入  3融券卖出 </param>
        # /// <param name="PriceType">表示报价方式 0上海限价委托 深圳限价委托 1(市价委托)深圳对方最优价格  2(市价委托)深圳本方最优价格  3(市价委托)深圳即时成交剩余撤销  4(市价委托)上海五档即成剩撤 深圳五档即成剩撤 5(市价委托)深圳全额成交或撤销 6(市价委托)上海五档即成转限价
        # /// <param name="Gddm">股东代码, 交易上海股票填上海的股东代码；交易深圳的股票填入深圳的股东代码</param>
        # /// <param name="Zqdm">证券代码</param>
        # /// <param name="Price">委托价格</param>
        # /// <param name="Quantity">委托数量</param>
        # /// <param name="Result">同上,其中含有委托编号数据</param>
        # /// <param name="ErrInfo">同上</param>
        client_id = await self.lid2hllDll(websocket, id)
        self.hllDll.SendOrder(client_id, c_int(OType), c_int(PType), c_char_p(Gddm.encode('utf-8')),
                         c_char_p(Code.encode('utf-8')), c_float(Price), c_int(Count), self.result, self.err_info)
        resultdata = self.make_result2arr(data=self.result.value.decode('gbk'))
        self.loggg_r(resultdata)
        senddata = self.packegdata(resultdata, readjson['rid'])
        self.loggg_r(senddata)
        await websocket.send(senddata)
        # 更新数据到数据库stock_tmp
        self.updateStockTmp(resultdata)
        self.loggg_r('----------------Trade_CommitOrder----------end---------------')

    def updateStockTmp(self,resultdata):
        self.loggg_r(resultdata)
        result = resultdata[1]
        sql = 'INSERT INTO lmq_stock_temp ( broker_id, deal_no, sub_id, lid, jytName, soruce,' \
              + ' login_name, gupiao_code, gupiao_name, trust_date, trust_time, trust_no, trust_price, trust_count, volume, amount, flag1, flag2, gudong_code, cancel_order_flag, '
        +'cancel_order_count, `type`, status, add_time, beizhu, info, type_today, type_today_back, type_history)' + \
        ' VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,)' \
            ()

    def make_result2arr(self,data):
        zhanghulist = []
        for item in data.split('\n'):
            itemvaule = item.split('\t')
            zhanghulist.append(itemvaule)
        return zhanghulist

    async def Trade_QueryData(self,websocket, readjson, id):  # 更新查询资金信息到数据表
        """
        :param websocket:
        :param readjson:{"req":"Trade_QueryData","rid":1585307277,"para":{"JsonType":1,"QueryType":1}}
        :param id:
        :return:
        """
        #

        # accsql='SELECT	* FROM	lmq_stock_account acc  WHERE	acc.id = '+str(id)
        # account= execlesql(accsql,1)
        # print(account)

        self.loggg_r('----------------Trade_QueryData-------------------------')
        client_id = await self.lid2hllDll(websocket, id)
        QueryType = int(readjson['para']['QueryType'])
        self.hllDll.QueryData(client_id, c_int(QueryType - 1), self.result, self.err_info)
        zhanghulist = self.make_result2arr(data=self.result.value.decode('gbk'))
        self. loggg_r(zhanghulist)
        senddata = self.packegdata(zhanghulist, readjson['rid'])
        if QueryType == 1:  # //更新查询资金信息到数据表
            self. update_account_info(zhanghulist, id)
        if QueryType == 2:  # 获取持仓
            self.loggg_r(zhanghulist)
        if QueryType == 3:  # 当日委托
            self. loggg_r(zhanghulist)
        if QueryType == 4:  # 当日成交
            self. loggg_r(zhanghulist)
        if QueryType == 5:  # 可撤单
            self.loggg_r(zhanghulist)
        if QueryType == 6:  # 新查询股东代码信息到数据表
            # update_gudong(zhanghulist,id)
            self.loggg_r(zhanghulist)
        await websocket.send(json.dumps(senddata, ensure_ascii=False))
        self.loggg_r('----------------Trade_QueryData---------end----------------')

    async def Trade_SellAll(self):
        self.loggg_r('')

    def getStockTmp(self,orderid):
        self.loggg_r(orderid)

    async def Trade_CancelOrder(self,websocket, readjson, id):
        # array('OrderID' = > $orderid, 'Type' = > $type);
        self.loggg_r('----------------Trade_CancelOrder-------------------------')
        self.loggg_r(readjson)
        client_id = await self.lid2hllDll(websocket, id)
        # QueryType = int(readjson['para'])
        orderid = readjson['OrderID']
        pszhth = orderid
        account = self.getAccount(id)
        type = readjson['Type']
        # /// <summary>
        # /// 撤委托
        # /// </summary>
        # /// <param name="ClientID">客户端ID</param>
        # /// <param name="pszExchangeID">交易所ID， 上海1，深圳0(招商证券普通账户深圳是2)</param>
        # /// <param name="pszStockAccount"> 股东账号
        # /// <param name="pszStockCode"> 股票代码
        # /// <param name="pszhth">表示要撤的目标委托的编号</param>
        # /// <param name="pszResult">同上</param>
        # /// <param name="pszErrInfo">同上</param>

        if type == 1:
            Gddm = account['sz_code']
            pszExchangeID = '0'
        if type == 2:
            Gddm = account['sh_code']
            pszExchangeID = '1'
        stocktmpinfo = self.getStockTmp(orderid)

        self.hllDll.CancelOrder(client_id,
                           c_char_p(pszExchangeID.encode('utf-8')),
                           c_char_p(Gddm.encode('utf-8')),
                           c_char_p(stocktmpinfo['gupiao_code'].encode('utf-8')),  # 股票代码
                           c_char_p(pszhth.encode('utf-8')),
                                self.result,
                                self.err_info)
        resultdata = self.make_result2arr(data=self.result.value.decode('gbk'))
        senddata = self.packegdata(resultdata, readjson['rid'])
        await websocket.send(json.dumps(senddata, ensure_ascii=False))
        self.loggg_r('----------------Trade_CancelOrder--------end-----------------')

    def update_gudong(self,data, stock_account_id):
        self.loggg_r(data)
        account1 = data[1]
        sh_code = account1[4]
        account2 = data[2]
        sz_code = account2[4]
        sql = 'update lmq_stock_account_info set sh_code="' + sh_code + '",sz_code="' + sz_code + '" where stock_account_id=' + str(
            stock_account_id)
        self.loggg_r(sql)
        self.execlesql(sql)

    def update_account_info(self,data, lid):
        # print(data)
        account = data[1]
        sql = 'update lmq_stock_account_info set balance=' + str(
            Decimal(account[1]).quantize(Decimal('0.00'))) + ',account_money=' + str(
            Decimal(account[2]).quantize(Decimal('0.00'))) + ',freeze_money=' + str(
            Decimal(account[3]).quantize(Decimal('0.00'))) + ',desirable_money=' + str(
            Decimal(account[8]).quantize(Decimal('0.00'))) + ', market_value=' + str(
            Decimal(account[4]).quantize(Decimal('0.00'))) + ',    total_money=' + str(
            Decimal(account[5]).quantize(Decimal('0.00'))) + ',    ck_profit=' + str(
            Decimal(account[8]).quantize(Decimal('0.00'))) + ' where stock_account_id=' + str(lid)
        print(sql)
        # 执行SQL语句
        # execlesql(sql )

    def packegdata(self,data, rid, ret=0, error=''):
        returnarr = dict()
        returnarr['error'] = error
        returnarr['ret'] = ret
        returnarr['rid'] = rid
        returnarr['data'] = data
        return returnarr

    async def traderegister(self,websocket, recv_json):
        readjson = await self.read_zhiling(websocket)
        # array('com' = > 'trade_id', 'id' = > $trade_id
        self.loggg_r(readjson)
        # print()
        readjson = json.loads(readjson)
        if readjson['req'] == 'Trade_QueryData':  # 查询

            await self.Trade_QueryData(websocket, readjson, recv_json['id'])
        if readjson['req'] == 'Trade_QueryHisData':  # 历史
            await self.Trade_QueryHisData(websocket, readjson, recv_json['id'])
        if readjson['req'] == 'Trade_QueryQuote':  # 询价
            await self.Trade_QueryQuote(websocket, readjson, recv_json['id'])
        if readjson['req'] == 'Trade_CommitOrder':  # 下单
            await self.Trade_CommitOrder(websocket, readjson, recv_json['id'])
        if readjson['req'] == 'Trade_SellAll':  # 一键清仓
            await self.Trade_SellAll(websocket)
        if readjson['req'] == 'Trade_CancelOrder':  # 撤单
            await self.Trade_CancelOrder(websocket, readjson, recv_json['id'])
        if readjson['req'] == 'Market_TimeData':  # 交易时间
            self.loggg_r()

    async def Trade_QueryQuote(self,websocket, readjson, id):
        Codes = readjson['Codes']
        client_id = await self.lid2hllDll(websocket, id)
        # hllset[1];
        self.hllDll.QueryQuote(client_id, c_char_p(Codes.encode('utf-8')), self.result, self.err_info)
        resultdata = self.make_result2arr(data=self.result.value.decode('gbk'))
        self.loggg_r(resultdata)
        senddata = self.packegdata(resultdata, readjson['rid'])
        self.loggg_r(senddata)
        await websocket.send(senddata)

    async def Trade_QueryHisData(self,websocket, readjson, id):
        # Codes=readjson['Codes']
        client_id = await self.lid2hllDll(websocket, id)
        # hllset[1];
        self.loggg_r('----------------Trade_QueryHisData-------------------------')
        # array('JsonType' => '1', 'QueryType' => $type, 'BeginDay' => $beginday, 'EndDay' => $endday)
        para = readjson['para']
        QueryType = para['QueryType']
        QueryType = str(QueryType)
        BeginDay = para['BeginDay']
        EndDay = para['EndDay']
        self.hllDll.QueryHisData(client_id,
                            c_char_p(QueryType.encode('utf-8')),
                            c_char_p(BeginDay.encode('utf-8')),
                            c_char_p(EndDay.encode('utf-8')),
                                 self.result,
                                 self.err_info)
        resultdata = self.make_result2arr(data=self.result.value.decode('gbk'))
        self.loggg_r(resultdata)
        senddata = self.packegdata(resultdata, readjson['rid'])
        self.loggg_r(senddata)
        await websocket.send(senddata)
        self.loggg_r('----------------Trade_QueryHisData---end----------------------')

    def is_json(self,myjson):
        try:
            json.loads(myjson)
        except ValueError:
            print(ValueError.args)
            return False;
        return True

    async def register(self,websocket):
        recv_str = await websocket.recv()
        #print(recv_str)
        if self.is_json(recv_str):
            recv_json = json.loads(recv_str)
            await self.traderegister(websocket, recv_json)
        else:
            if recv_str == 'TradeArr':
                await self.CheckBroker(websocket)
            if recv_str == 'double':
                await self.CheckBroker(websocket)
            if recv_str == 'BrokerLogin':
                await self.BrokerLogin(websocket)
            if recv_str == 'BrokerOut':
                # loggg_r('BrokerOut//')
                await self.BrokerOut(websocket)
            if recv_str == 'CheckBroker':  # 检测证券账户
                await self.CheckBroker(websocket)
            if recv_str == 'Trade_CheckStatus':
                await self.CheckBroker(websocket)
            if recv_str == 'Market_ListCount':
                await self.CheckBroker(websocket)

    async def BrokerOut(self,websocket):
        self.loggg_r('----------------BrokerOut-------------------------')
        readjson = await self.read_zhiling(websocket)
        readjson = json.loads(readjson)
        self.loggg_r(readjson)
        if readjson['operation'] == 'BrokerOut':
            id = readjson['id']
            if str(id) in self.hllset.keys():
                client_id = self.hllset[str(id)]
                if client_id > 0:
                    self.hllDll.Logoff(client_id)
                    await websocket.send('1')
            else:
                await websocket.send('1')

                self.loggg_r('----------------BrokerOut------end-------------------')

    async def counter(self,websocket, path):
        # register(websocket) sends user_event() to websocket
        await  self.register(websocket)


    def writepid(self):
        f = open('c:/pythonpid.txt', 'w+', encoding='utf-8')
        f.write(str(os.getpid()))
        f.close()

    def start(self):
        self.root_logger.setLevel(logging.INFO)  # or whatever
        handler = logging.FileHandler('out.log', 'w', 'utf-8')  # or whatever
        handler.setFormatter = logging.Formatter(
            '%(asctime)s %(thread)d %(threadName)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')  # or whatever
        self.root_logger.addHandler(handler)
        self.qsid2ip  = self.loadqsid()
        self.writepid()
        self.hllDll=self.TdApiXInit()

        config_json = json.load(open('./config.json', 'r', encoding="utf-8"))
        self.loggg_r('server listened on ' + config_json['ip'] + ':' + str(config_json['port']))
        license = ServerLicense()
        status = license.getLicenseInfo()
        # print(status)
        if status==True:
            asyncio.get_event_loop().run_until_complete(websockets.serve(self.counter, config_json['ip'], config_json['port']))
            asyncio.get_event_loop().run_forever()


