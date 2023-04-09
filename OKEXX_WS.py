import json
from datetime import datetime
from BASE_WS import BaseWebsocket
import zlib
import pandas as pd
from M_STG import short_stg
class OKEX_DATA_WS(BaseWebsocket):
    def __init__(self,on_tick_back:short_stg,ping_interval=20):
        host_pub="wss://ws.okex.com:8443/ws/v5/public"
        host_pri="wss://ws.okex.com:8443/ws/v5/private"
        host="wss://real.okex.com:8443/ws/v3?brokerId=181"
        self.on_tick_back=on_tick_back
        super(OKEX_DATA_WS,self).__init__(host=host_pub,ping_interval=ping_interval)

    def on_open(self):
        print(f"websocket open at:{datetime.now()}")
        # self.subscribe_topic(op="subscribe", channel="mark-price", symbol="BTC-USDT-SWAP")
        self.subscribe_topic("subscribe", "tickers", "BTC-USDT-SWAP")
        # self.subscribe_topic1("subscribe","positions","FUTURES","","BTC-USDT-SWAP",)
        # {
        #     "event": "subscribe",
        #     "arg": {
        #         "channel": "positions",
        #         "instType": "FUTURES",
        #         "uly": "BTC-USD",
        #         "instId": "BTC-USD-200329"
        #     }
        # }

    def on_close(self):
        print(f"websocket close at:{datetime.now()}")
    def on_msg(self, data):
        # decompress=zlib.decompressobj(
        #     -zlib.MAX_WBITS
        # )
        # msg=json.loads(decompress.decompress(data))
        # print(data)
        res=(json.loads(data))
        for key in res:
            if key=='data':
                ress=pd.DataFrame(res[key])
                if self.on_tick_back:
                    self.on_tick_back(ress.iloc[0]['askPx'])
                # return (ress.iloc[0]['askPx'])
        # if self.on_tick_back:
        #     self.on_tick_back(data)
        # print(data['data'])
        # data=msg['data']
        # print(data)
        # if 'table' in msg:
        #     if msg['table']=='swap/mark_price':
        #         mark_price={
        #             "timestamp":data['timestamp'],
        #             "instrument_id":data['instrument_id'],
        #             "mark_price":float(data['mark_price'])
        #         }
        # if "event" in msg:
        #     if msg['event'] == 'login' and msg['success']:
        #         # print("登录成功。。")
        #         self.subscribe_topic()
    def on_error(self, exception_type: type, exception_value: Exception, tb):
        print(f"websocket触发异常，状态码：{exception_type}，信息：{exception_value}")
    def subscribe_topic(self,op,channel,symbol):
        self.send_msg({
            "op": op,
            "args":[{
                "channel": channel,
                "instId": symbol
            }]
        })

    # def subscribe_topic(self,op:str,channel:str,symbol:str):
    #     self.send_msg(
    #         {
    #             "op":op,
    #             "args":[
    #                 channel+":"+symbol
    #             ]
    #         }
    #     )

if __name__ == '__main__':
    ws=OKEX_DATA_WS(on_tick_back=short_stg.on_tick)
    # symbol = "BTC-USDT-SWAP"
    ws.start()