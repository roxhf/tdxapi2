#!/usr/bin/env python
#coding: utf-8
from ctypes import *
import asyncio,json,logging,websockets, MySQLdb,os
from decimal import Decimal
# logging.basicConfig(level=logging.INFO,
#                     format='%(asctime)s %(thread)d %(threadName)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
#                     datefmt='%a, %d %b %Y %H:%M:%S',
#                     filename='out.log',
#                     filemode='w',
#                     handlers= FileHandler(StreamHandler())
#                     )
root_logger= logging.getLogger()
root_logger.setLevel(logging.INFO) # or whatever
handler = logging.FileHandler('out.log', 'w', 'utf-8') # or whatever
handler.setFormatter = logging.Formatter('%(asctime)s %(thread)d %(threadName)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s') # or whatever
root_logger.addHandler(handler)
hllset=dict()
result = create_string_buffer(1024 * 2048)
err_info = create_string_buffer(4048 * 4048)
def  loggg_r(dataline):
    print(dataline)
    root_logger.info(dataline)

def TdApiXInit():
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

hllDll = TdApiXInit()
async def lid2hllDll(websocket,account_id):
    """
    :param websocket:
    :param lid:
    :param account:
    :return:
    """
    print(id)

    if str(account_id) in hllset:
        loggg_r('无需登录')
        return hllset[str(account_id)]
    else:
        if int(account_id)>0:
            accsql = 'select * from lmq_stock_account  where id='+str(account_id)
            account = execlesql(accsql, 1)
        else:
            return 0
        broker = str(account['broker'])
        qsid2ipdata = qsid2ip[broker]
        client_id = hllDll.LogonEx(c_char_p(str(account['broker']).encode('utf-8')),
                                   c_char_p(qsid2ipdata['ip'].encode('utf-8')),
                                   c_int(qsid2ipdata['port']),
                                   c_char_p(account['clienver'].encode('utf-8')),
                                   c_int(0), c_int(8),
                                   c_char_p(account['lid'].encode('utf-8')),
                                   c_char_p(account['lid'].encode('utf-8')),
                                   c_char_p(account['pwd'].encode('utf-8')),
                                   c_char_p(b"\0"), err_info)
        #hllset[lid]
        if client_id == -1:
            loggg_r('账号登陆错误')
            b = err_info.value.decode('gbk')
            data=make_result2arr(b)
            print(data)
            print(client_id, b)
            hllDll.CloseTdx()
            # await websocket.send('0')
        else:
            hllset[str(account['id'])]=client_id
        loggg_r('登录成功'+str(client_id))
        return client_id


def loadqsid():

    data3 = json.load(open('./qsid2ip.json','r',encoding = "utf-8"))
    # print(data3)
    return data3
qsid2ip=loadqsid()
async def read_zhiling(websocket):
    while True:
        recv_str = await websocket.recv()
        return recv_str

# CheckBroker检测证券账户
# {"operation": "CheckBroker", "LID": "83939003888", "user": "83939003888", "password": "584520", "broker": 122,
#  "clienver": "1.17"}


async def BrokerLogin(websocket):
    loggg_r(123)
    readjson = await read_zhiling(websocket)
    #'{"operation":"BrokerLogin","LID":"83939003888","user":"83939003888","password":"584520","broker":122,"clienver":null,"id":"31"}'
    readjson = json.loads(readjson)
    print(readjson)
    client_id= await lid2hllDll(websocket,readjson['id'])
    if client_id == -1:
        print('登陆错误')
        hllDll.CloseTdx()
        await websocket.send('0')
    else:
        hllDll.QueryData(client_id, c_int(0), result, err_info)
        print(client_id, result.value.decode('gbk'))
        await websocket.send(str(client_id))

async def CheckBroker(websocket):
    loggg_r('----------------CheckBroker-------------------------')
    readjson = await read_zhiling(websocket)
    readjson = json.loads(readjson)
    print(readjson)
    hllDll=TdApiXInit()
    result = create_string_buffer(1024 * 2048)
    err_info = create_string_buffer(4048 * 4048)
    print(readjson['broker'])
    broker=str( readjson['broker'])
    qsid2ipdata=qsid2ip[broker]

    client_id = hllDll.LogonEx(c_char_p(broker.encode('utf-8')),
                               c_char_p(qsid2ipdata['ip'].encode('utf-8')),
                               c_int(qsid2ipdata['port'].encode('utf-8')),
                               c_char_p(readjson['clienver'].encode('utf-8')),
                               c_int(0), c_int(8),
                               c_char_p(readjson['LID'].encode('utf-8')),
                               c_char_p(readjson['LID'].encode('utf-8')),
                               c_char_p(readjson['password'].encode('utf-8')),
                               c_char_p(b"\0"), err_info)

    if client_id == -1:
        print('登陆错误')
        hllDll.CloseTdx()
        await websocket.send('0')
    else:
        hllDll.QueryData(client_id, c_int(0), result, err_info)
        print(client_id, result.value.decode('gbk'))
        await websocket.send(str(client_id))
        hllDll.Logoff(client_id)
        hllDll.CloseTdx()
    # await counter(websocket,'')
    loggg_r('----------------CheckBroker----------end---------------')

def execlesql(sql,type=0):
    """
    :param sql:
    :param type:0 1 2
    :return:
    """
    dbconfig = json.load(open('config.json', 'r', encoding="utf-8"))
    db = MySQLdb.connect(dbconfig['hostname'], dbconfig['username'], dbconfig['password'], dbconfig['database'], charset='utf8')
    # 使用 cursor() 方法创建一个游标对象 cursor
    data=[];
    cursor = db.cursor()
    try:
        if type==0:
            cursor.execute(sql)
            db.commit()
        if type==1:
            cursor.execute(sql)
            db.commit()
            data = cursor.fetchone()
            columns = [column[0] for column in cursor.description]
            data =dict(zip(columns, data))
        if type==2:
            cursor = db.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(sql)
            data = cursor.fetchall()
            db.commit()
    except:
        db.rollback()
    db.close()

    return data


def getAccount(account_id):
    accsql = 'select * from lmq_stock_account  where id=' + str(account_id)
    account = execlesql(accsql, 1)
    loggg_r(account)
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


async def Trade_CommitOrder(websocket,readjson,id):#下单
    #readjson = await read_zhiling(websocket)
    # json_encode(array('req' = > 'Trade_CommitOrder', 'rid' = > build_rid_no(),
    #   'para' = > array('Code' => $code, 'Count' => $count,
    #                   'EType' => $etype, 'OType' => $otype,
    #                     'PType' => $ptype, 'Price' => $price)));
    # await websocket.send('08551112512')
    loggg_r('----------------Trade_CommitOrder-------------------------')
    readjson = json.loads(readjson)
    print(readjson)
    para=readjson['para']
    Code=para['Code']
    Count = para['Count']
    EType = para['EType']#市场类型1深圳 2上海
    OType = para['OType']#//1买入 2卖出
    PType = para['PType']#//1、限价委托//5市价委托
    Price = para['Price']
    account=getAccount(id)
    if EType==1:
        Gddm =account['sz_code']
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
    client_id = await lid2hllDll(websocket, id)
    hllDll.SendOrder(client_id, c_int(OType), c_int(PType), c_char_p(Gddm.encode('utf-8')), c_char_p(Code.encode('utf-8')), c_float(Price), c_int(Count), result, err_info)
    resultdata = make_result2arr(data=result.value.decode('gbk'))
    loggg_r(resultdata)
    senddata = packegdata(resultdata, readjson['rid'])
    loggg_r(senddata)
    await websocket.send(senddata)
    #更新数据到数据库stock_tmp
    updateStockTmp(resultdata)
    loggg_r('----------------Trade_CommitOrder----------end---------------')

def updateStockTmp(resultdata):
    loggg_r(resultdata)
    result=resultdata[1]
    sql='INSERT INTO lmq_stock_temp ( broker_id, deal_no, sub_id, lid, jytName, soruce,'\
        +' login_name, gupiao_code, gupiao_name, trust_date, trust_time, trust_no, trust_price, trust_count, volume, amount, flag1, flag2, gudong_code, cancel_order_flag, '
    +'cancel_order_count, `type`, status, add_time, beizhu, info, type_today, type_today_back, type_history)'+\
    ' VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,)'\
        ()

def make_result2arr(data):
    zhanghulist = []
    for item in data.split('\n'):
        itemvaule = item.split('\t')
        zhanghulist.append(itemvaule)
    return  zhanghulist

async def Trade_QueryData(websocket,readjson,id):#更新查询资金信息到数据表
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

    loggg_r('----------------Trade_QueryData-------------------------')
    client_id=await lid2hllDll(websocket,id)
    QueryType=int(readjson['para']['QueryType'])
    hllDll.QueryData(client_id, c_int(QueryType-1), result, err_info)
    zhanghulist = make_result2arr(data=result.value.decode('gbk'))
    loggg_r(zhanghulist)
    senddata = packegdata(zhanghulist, readjson['rid'])
    if QueryType==1:#//更新查询资金信息到数据表
        update_account_info(zhanghulist,id)
    if QueryType == 2:#获取持仓
         loggg_r(zhanghulist)
    if QueryType == 3:#当日委托
        loggg_r(zhanghulist)
    if QueryType == 4:#当日成交
        loggg_r(zhanghulist)
    if QueryType == 5:#可撤单
        loggg_r(zhanghulist)
    if QueryType == 6:#新查询股东代码信息到数据表
        #update_gudong(zhanghulist,id)
        loggg_r(zhanghulist)
    await websocket.send(json.dumps(senddata, ensure_ascii=False))
    loggg_r('----------------Trade_QueryData---------end----------------')
async def Trade_SellAll():
    loggg_r('')
def getStockTmp(orderid):
    loggg_r(orderid)

async def Trade_CancelOrder(websocket,readjson,id):
    #array('OrderID' = > $orderid, 'Type' = > $type);
    loggg_r('----------------Trade_CancelOrder-------------------------')
    loggg_r(readjson)
    client_id = await lid2hllDll(websocket, id)
    # QueryType = int(readjson['para'])
    orderid=readjson['OrderID']
    pszhth=orderid
    account = getAccount(id)
    type=readjson['Type']
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
        pszExchangeID='0'
    if type == 2:
        Gddm = account['sh_code']
        pszExchangeID = '1'
    stocktmpinfo=getStockTmp(orderid)


    hllDll.CancelOrder(client_id,
                       c_char_p(pszExchangeID.encode('utf-8')),
                       c_char_p(Gddm.encode('utf-8')),
                       c_char_p(stocktmpinfo['gupiao_code'].encode('utf-8')),#股票代码
                       c_char_p(pszhth.encode('utf-8')),
                       result,
                       err_info)
    resultdata=make_result2arr(data=result.value.decode('gbk'))
    senddata = packegdata(resultdata, readjson['rid'])
    await websocket.send(json.dumps(senddata, ensure_ascii=False))
    loggg_r('----------------Trade_CancelOrder--------end-----------------')
def update_gudong(data,stock_account_id):
    loggg_r(data)
    account1 = data[1]
    sh_code=account1[4]
    account2 = data[2]
    sz_code = account2[4]
    sql = 'update lmq_stock_account_info set sh_code="'+sh_code+'",sz_code="'+sz_code+'" where stock_account_id='+str(stock_account_id)
    loggg_r(sql)
    execlesql(sql)

def update_account_info(data,lid):
    print(data)
    account=data[1]
    sql= 'update lmq_stock_account_info set balance='+str(Decimal(account[1]).quantize(Decimal('0.00')))+',account_money='+str(Decimal(account[2]).quantize(Decimal('0.00'))) +',freeze_money='+str(Decimal(account[3]).quantize(Decimal('0.00')))         +',desirable_money='+str(Decimal(account[8]).quantize(Decimal('0.00')))+', market_value='+str(Decimal(account[4]).quantize(Decimal('0.00')))        +',    total_money='+str(Decimal(account[5]).quantize(Decimal('0.00')))+',    ck_profit='+str(Decimal(account[8]).quantize(Decimal('0.00')))         +' where stock_account_id='+str(lid)
    print(sql)
    # 执行SQL语句
    #execlesql(sql )


def packegdata(data,rid,ret=0,error=''):
    returnarr=dict()
    returnarr['error']=error
    returnarr['ret']=ret
    returnarr['rid'] = rid
    returnarr['data']=data
    return returnarr

async def traderegister(websocket,recv_json):
    readjson = await read_zhiling(websocket)
    #array('com' = > 'trade_id', 'id' = > $trade_id
    print(readjson)
    readjson=json.loads(readjson)
    if readjson['req'] == 'Trade_QueryData':#查询

        await Trade_QueryData(websocket, readjson,recv_json['id'])
    if readjson['req']  == 'Trade_QueryHisData':  # 历史
        await Trade_QueryHisData(websocket, readjson,recv_json['id'])
    if readjson['req']  == 'Trade_QueryQuote':  # 询价
        await Trade_QueryQuote(websocket, readjson,recv_json['id'])
    if readjson['req']  == 'Trade_CommitOrder':  # 下单
        await Trade_CommitOrder(websocket,readjson,recv_json['id'])
    if readjson['req'] == 'Trade_SellAll':  # 一键清仓
        await Trade_SellAll(websocket)
    if readjson['req'] == 'Trade_CancelOrder':  # 撤单
        await Trade_CancelOrder(websocket,readjson,recv_json['id'])
    if readjson['req'] == 'Market_TimeData':  #交易时间
        loggg_r()
async def Trade_QueryQuote(websocket,readjson,id):
    Codes=readjson['Codes']
    client_id = await lid2hllDll(websocket, id)
    #hllset[1];
    hllDll.QueryQuote(client_id, c_char_p(Codes.encode('utf-8')),result, err_info)
    resultdata = make_result2arr(data=result.value.decode('gbk'))
    loggg_r(resultdata)
    senddata = packegdata(resultdata, readjson['rid'])
    loggg_r(senddata)
    await websocket.send(senddata)

async def Trade_QueryHisData(websocket,readjson,id):
    #Codes=readjson['Codes']
    client_id = await lid2hllDll(websocket, id)
    #hllset[1];
    loggg_r('----------------Trade_QueryHisData-------------------------')
    #array('JsonType' => '1', 'QueryType' => $type, 'BeginDay' => $beginday, 'EndDay' => $endday)
    para=readjson['para']
    QueryType=para['QueryType']
    QueryType=str(QueryType)
    BeginDay=para['BeginDay']
    EndDay = para['EndDay']
    hllDll.QueryHisData(client_id,
                     c_char_p(QueryType.encode('utf-8')),
                    c_char_p(BeginDay.encode('utf-8')),
                    c_char_p(EndDay.encode('utf-8')),
                    result,
                    err_info)
    resultdata = make_result2arr(data=result.value.decode('gbk'))
    loggg_r(resultdata)
    senddata = packegdata(resultdata, readjson['rid'])
    loggg_r(senddata)
    await websocket.send(senddata)
    loggg_r('----------------Trade_QueryHisData---end----------------------')
def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError:
        return False;
    return True

async def register(websocket):
    recv_str = await websocket.recv()
    print(recv_str)
    if is_json(recv_str):
        recv_json = json.loads(recv_str)
        await traderegister(websocket, recv_json)
    else:
        if recv_str == 'TradeArr':
            await CheckBroker(websocket)
        if recv_str == 'double':
            await CheckBroker(websocket)
        if recv_str == 'BrokerLogin':
            await BrokerLogin(websocket)
        if recv_str == 'BrokerOut':
            #loggg_r('BrokerOut//')
            await BrokerOut(websocket)
        if recv_str == 'CheckBroker':#检测证券账户
            await CheckBroker(websocket)
        if recv_str == 'Trade_CheckStatus':
            await CheckBroker(websocket)
        if recv_str == 'Market_ListCount':
            await CheckBroker(websocket)

async def BrokerOut(websocket):
    loggg_r('----------------BrokerOut-------------------------')
    readjson = await read_zhiling(websocket)
    readjson = json.loads(readjson)
    loggg_r(readjson)
    if readjson['operation']=='BrokerOut':
        id=readjson['id']
        if str(id) in  hllset.keys():
            client_id=hllset[str(id)]
            if client_id>0:
                hllDll.Logoff(client_id)
                await websocket.send('1')
        else:
            await websocket.send('1')

    loggg_r('----------------BrokerOut------end-------------------')




async def counter(websocket, path):
    # register(websocket) sends user_event() to websocket
    await  register(websocket)
if __name__ == '__main__':
    # main()
    accsql = 'SELECT	acc.* FROM	lmq_stock_account_info info LEFT JOIN lmq_stock_account acc on 	acc.id = info.stock_account_id WHERE	info.id = ' + str(
        9)
    account_result = execlesql(accsql, 1)
    loggg_r(account_result)
    accsql = 'SELECT * FROM	lmq_stock_account_info'
    account_result = execlesql(accsql, 2)
    loggg_r(account_result)

    f = open('c:/pythonpid.txt', 'w+', encoding='utf-8')
    f.write(str(os.getpid()))
    f.close()

    config_json = json.load(open('./config.json', 'r', encoding="utf-8"))
    loggg_r('server listened on '+config_json['ip']+':'+str(config_json['port']))
    asyncio.get_event_loop().run_until_complete(websockets.serve(counter, config_json['ip'], config_json['port']))
    asyncio.get_event_loop().run_forever()


    # print(qsid2ip['122'])
    # print(type(qsid2ip))





