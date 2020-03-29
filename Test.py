from ctypes import *
import sys
import os.path

hllDll = WinDLL("TdApiX.dll")

hllDll.OpenTdx()

result = create_string_buffer(1024 * 2048)
err_info = create_string_buffer(4048 * 4048)

clientID_int = c_int*1
clientID_arr = clientID_int()

Category_int = c_int*1
Category_arr = Category_int()

PriceType_int = c_int*1
PriceType_arr = PriceType_int()

Gddm_char = c_char*1
Gddm_arr = Gddm_char()

Zqdm_char = c_char*1
Zqdm_arr = Zqdm_char()

Price_float = c_float*1
Price_arr = Price_float()

Quantity_int = c_int*1
Quantity_arr = Quantity_int()


client_id = hllDll.LogonEx(c_char_p(b"122\0"), c_char_p(b"183.3.217.11\0"), c_int(7708), c_char_p(b"1.17\0"), c_int(0), c_int(8), c_char_p(b"83939003888\0"), c_char_p(b"83939003888\0"), c_char_p(b"584520\0"), c_char_p(b"\0"), err_info)


if client_id == -1:
    b = err_info.value.decode('gbk')
    print(client_id, b)
    sys.exit()
else:
#查询操作码：0资金  1股份   2当日委托  3当日成交     4可撤单   5股东代码  6融资余额   7融券余额  8可融证券 9信用资产查询

#资金
    hllDll.QueryData(client_id, c_int(0), result, err_info)
    print(client_id, result.value.decode('gbk'))
#股份
    hllDll.QueryData(client_id, c_int(1), result, err_info)
    print(client_id, result.value.decode('gbk'))
		#当日委托
    hllDll.QueryData(client_id, c_int(2), result, err_info)
    print(client_id, result.value.decode('gbk'))
		#当日成交
    hllDll.QueryData(client_id, c_int(3), result, err_info)
    print(client_id, result.value.decode('gbk'))
	#可撤单
    hllDll.QueryData(client_id, c_int(6), result, err_info)
    print(client_id, result.value.decode('gbk'))
    print(client_id, err_info.value.decode('gbk'))
    print('下单----------------------------')
    hllDll.QueryData(client_id, c_int(5), result, err_info)
    print(client_id, result.value.decode('gbk'))
    print('下单----------------------------')
    #下单
    # hllDll.SendOrder(client_id, c_int(0), c_int(2), c_char_p(b"83939003888\0"), c_char_p(b"510050\0"), c_float(2.655), c_int(100), result, err_info)
    # print(client_id, result.value.decode('gbk'))
    # print(client_id, err_info.value.decode('gbk'))
    # print('下单-------------------------end---')
    #
    #
    # #撤单
    # hllDll.CancelOrder(client_id, c_char_p(b"0\0"), c_char_p(b"\0"), c_char_p(b"\0"), c_char_p(b"10\0"), result, err_info);
    # print(client_id, result.value.decode('gbk'))
    # print(client_id, err_info.value.decode('gbk'))

	
    #查询行情

    hllDll.QueryQuote(client_id, c_char_p(b"510050\0"), result, err_info)
    print(client_id, result.value.decode('gbk'))
    print(client_id, err_info.value.decode('gbk'))

    hllDll.QueryData(client_id, c_int(1), result, err_info)
    print(client_id, result.value.decode('gbk'))
	
    hllDll.Logoff(client_id)
    hllDll.CloseTdx()
