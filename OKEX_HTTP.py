"""
    1. Binance http requests.

"""

import requests
import time
from enum import Enum
from threading import Thread, Lock
from datetime import datetime
import hmac
import hashlib
import base64
from urllib.parse import urlencode
import json
import pandas as pd
import ccxt
class OrderStatus(object):
    NEW              = "NEW"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED           = "FILLED"
    CANCELED         = "CANCELED"
    PENDING_CANCEL   = "PENDING_CANCEL"
    REJECTED         = "REJECTED"
    EXPIRED          = "EXPIRED"

class dirc(Enum):
    long=1
    short=2
    sell=3
    cover=4
class order_type(Enum):
    normal=0
    Post_only=1
    Fok=2# 全部成交or立即取消
    Ioc=3#立即成交取消剩余
    Market=4
class order_type_v5(Enum):
    market="market"
    limit='limit'
    post_only="post_only"
    fok="fok"
    ioc="ioc"

class RequestMethod(Enum):
    """
    请求的方法.
    """
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
class MgnMode(Enum):
    isolated="ioslated"
    cross="cross"
    # 如果ccy有效传值，该参数值只能为cross。
class Interval(Enum):
    """
    请求的K线数据..
    """
    MINUTE_1    = '1m'
    MINUTE_3    = '3m'
    MINUTE_5    = '5m'
    MINUTE_15   = '15m'
    MINUTE_30   = '30m'
    HOUR_1      = '1h'
    HOUR_2      = '2h'
    HOUR_4      = '4h'
    HOUR_6      = '6h'
    HOUR_8      = '8h'
    HOUR_12     = '12h'
    DAY_1       = '1d'
    DAY_3       = '3d'
    WEEK_1      = '1w'
    MONTH_1     = '1M'

class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"


class OKEX_FUTURE_http(object):
    def __init__(self, key=None, secret=None, host=None, passphrase=None,timeout=5):
        self.key = key
        self.secret = secret
        self.passphrase=passphrase
        self.host = host if host else "https://www.okex.com"
        self.recv_window = 5000
        self.timeout = timeout
        self.order_count_lock = Lock()
        self.order_count = 1_000_000

    def build_parameters(self, params: dict):
        keys = list(params.keys())
        keys.sort()
        return '&'.join([f"{key}={params[key]}" for key in params.keys()])
    def get_ts(self):
        now=datetime.utcnow()
        ts=now.isoformat("T","milliseconds")
        return ts+'Z'
    def _sign(self, method, path, query_params=None, request_body=None):
        timestamp = self.get_ts()
        if query_params:
            path = path + '?' + urlencode(query_params)

        if request_body:
            data = json.dumps(request_body)  #
            msg = timestamp + method + path + data
        else:
            msg = timestamp + method + path
        # print(msg)
        digest = hmac.new(self.secret.encode('utf-8'), msg.encode('utf-8'), digestmod=hashlib.sha256).digest()
        signature = base64.b64encode(digest).decode('utf-8')
        headers = {
            'OK-ACCESS-KEY': self.key,
            'OK-ACCESS-SIGN': signature,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': self.passphrase,
            # 'x-simulated-trading':"1",
            'Content-Type': 'application/json'

        }
        # print(headers)
        return headers
    # def get_symbols(self):
    #     path = '/api/spot/v3/instruments'
    #     url = self.host + path
    #     headers = self._sign('GET', path)  # 请求的路径 火币
    #     json_data = requests.get(url, headers=headers).json()
    #     return json_data


    def _timestamp(self):
        return int(time.time() * 1000)
    def _new_order_id(self):
        with self.order_count_lock:
            self.order_count += 1
            return self.order_count
    def order_id(self):
        return str(self._timestamp() + self._new_order_id())
    def get_kline(self,instId:str,bar:str,limit:str):
        path="/api/v5/market/mark-price-candles"
        para={
            "instId":instId,
            "bar":bar,
            "limit":limit
        }
        headers = self._sign('GET', query_params=para,path=path)
        url=self.host+path
        json_data=requests.get(url,headers=headers,params=para,timeout=self.timeout).json()
        return json_data['data']

    # def get_kline(self, symbol, interval: Interval,
    #               start_time=None, end_time=None, limit=500, max_try_time=10):
    #     path = f"/api/swap/v3/instruments/{symbol}/candles"
    #     params={}
    #     headers=self._sign("GET",path,query_params=params)
    #     data=requests.get(self.host+path,headers=headers,timeout=self.timeout).json()
    #     return data
    ########################### the following request is for private data ########################

    # def place_order(self, client_oid:str,instrument_id: str, size: str, type:dirc, order_type:order_type, price:str,match_price:str):
    #     path = "/api/swap/v3/orders"
    #     params = {
    #         # "client_oid": client_oid,
    #         "size": size,
    #         "type": type,
    #         "instrument_id": instrument_id,
    #         "price": price,
    #         "match_price": match_price,
    #         "order_type": order_type
    #     }


    def get_accounts(self):
        path = '/api/v5/account/balance'
        headers = self._sign('GET', path)
        url = self.host + path
        json_data = requests.get(url, headers=headers,timeout=self.timeout).json()
        return json_data

    # posSide在双向持仓且保证金模式为逐仓条件下必填，且仅可选择
    # long或short，其他情况下非必填，默认net；仅适用于交割 / 永续
    def set_lev(self,instId:str,mgnMode:str,lever:str,ccy=None,posSide="net"):
        path="/api/v5/account/set-leverage"
        body={
            "instId": instId,
            "lever": lever,
            "mgnMode": mgnMode,
            "posSide":posSide
              }
        url=self.host+path
        headers=self._sign('POST',path,request_body=body)
        json_data=requests.post(url,data=json.dumps(body),headers=headers,timeout=self.timeout).json()
        print(json_data)
    def set_pos(self,posMode:str):
        path="/api/v5/account/set-position-mode"
        body={
            "posMode":posMode
        }
        url=self.host+path
        headers = self._sign('POST', path, request_body=body)
        json_data = requests.post(url, data=json.dumps(body), headers=headers, timeout=self.timeout).json()
        res=json_data['data']
        return res
    def place_order(self, instId:str,tdMode:str,ccy:str,side:str
                    ,ordType:str,sz:str,px=None):
        path = "/api/v5/trade/order"
        body = {
            # "client_oid": client_oid,
            "instId":instId,
            "tdMode":tdMode,
            "ccy":ccy,
            "side":side,
            "ordType":ordType,
            "sz":sz,
            "px":px
        }
        url=self.host+path
        headers=self._sign('POST',path,request_body=body)
        json_data=requests.post(url,data=json.dumps(body),headers=headers,timeout=self.timeout).json()
        return json_data['data'][0]
    def get_pos(self,typ:str):
        path='/api/v5/account/positions'
        params={
            "instType":typ,
        }
        url=self.host+path
        headers=self._sign('GET',path=path,query_params=params)
        json_data=requests.get(url,params=params,headers=headers,timeout=self.timeout).json()
        return (json_data['data'])
    #保证金模式：isolated：逐仓 ；cross：全仓
    #非保证金模式：cash：非保证金
    # conditional：单向止盈止损
    # oco：双向止盈止损
    # trigger：计划委托
    def order_alog(self,instId:str,ccy:str,tdMode:str,side:str,ordType:str,sz:str,
                   orderPx:str,triggerPx:str):
        path="/api/v5/trade/order-algo"
        body={
            "instId":instId,
            "tdMode":tdMode,
            "side":side,
            "ccy":ccy,
            "ordType":ordType,
            "sz":sz,
            "triggerPx":triggerPx,
            "orderPx":orderPx
        }
        url=self.host+path
        headers=self._sign('POST',path=path,request_body=body)
        json_data=requests.post(url,data=json.dumps(body),headers=headers,timeout=self.timeout).json()
        # return json_data
        print(json_data)
    def cancel_ord(self,instId:str,ordId:str):
        path="/api/v5/trade/cancel-order"
        body={
            "instId":instId,
            "ordId":ordId
        }
        url=self.host+path
        headers=self._sign('POST',path=path,request_body=body)
        json_data=requests.post(url,data=json.dumps(body),headers=headers,timeout=self.timeout).json()
        print (json_data)
#
if __name__ == '__main__':
#     # import pandas as pd
    key = "5df88318-fb04-474f-8560-5fff0218ab1d"
    passphrase = "FeifeiisPig3@"
    secret = "074941A9DCE6C0EA8547123C4F3045DB"
    exchange=OKEX_FUTURE_http(key=key,secret=secret,passphrase=passphrase)
    # print(exc.get_ts())
    # print(exc.get_symbols())
    # print(pd.DataFrame(exchange.get_kline("BTC-USD-SWAP","15m","100")))
    print(exchange.get_accounts())
    # symbol="BTC-USDT-i"
    # exchange.set_lev(instId="BTC-USDT-SWAP",mgnMode="cross",lever="100")
    # exchange.set_pos("net_mode")
    # res=exchange.place_order(instId=symbol,tdMode="cross",ccy="USDT",side="buy",ordType="limit"
    #                      ,sz="1",px="50000")
    # print(res)
    # # print(res)
    # ress=res['data'][0]
    # ord_id=res['ordId']
    # print(type(ord_id))
    # exchange.cancel_ord(symbol,"299622896683589632")
    # res=exchange.get_pos(typ="SWAP")
    # print(res)
    # if not res:
    #     print(0)
    # else:
    #     print(res)
    # print(exchange.place_order(instId=symbol,tdMode="cross",ccy="USDT",side="sell",ordType="market",sz="10.0"))
    # exchange.order_alog(instId=symbol,tdMode="cross",ordType="trigger",ccy="USDT",sz="1",side="sell",triggerPx="6600",orderPx="6600")
    # exchange.cancel_ord(instId=symbol,ordId="297746675326656512")
    # 表头分别为[timestamp, open, high, low, close, volume, currency_volume]
    # print(str(abs(-234.3)))
    # print(float("13"))
