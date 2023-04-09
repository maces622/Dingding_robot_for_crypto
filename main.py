# Press the green button in the gutter to run the script.
import time
import talib
from datetime import datetime
import logging
format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=format, filename='ema_strategy.txt')
logging.getLogger('apscheduler').setLevel(logging.WARNING)  # 设置apscheduler日记类型.
import BASE_WS
import OKEXX_WS
import OKEX_HTTP
import apscheduler
from M_STG import short_stg
from backgroundsc import BackgroundScheduler
import websocket
class okexfuture(object):
    def __init__(self,key=None,secret=None,passphrase=None,host=None,timeout=5):
        self.key=key
        self.secret=secret
        self.passphrase=passphrase
        self.host = host if host else "https://www.okex.com/"
        self.recv_window = 5000
        self.timeout = timeout
        self.order_count_lock = Lock()
        self.order_count = 1_000_000
    #打包参数
    def build_parameters(self, params: dict):
        keys = list(params.keys())
        keys.sort()
        return '&'.join([f"{key}={params[key]}" for key in params.keys()])

if __name__ == '__main__':
    key = "5df88318-fb04-474f-8560-5fff0218ab1d"
    passphrase = "FeifeiisPig3@"
    secret = "074941A9DCE6C0EA8547123C4F3045DB"
    exchange = OKEX_HTTP.OKEX_FUTURE_http(key=key, secret=secret, passphrase=passphrase)

    boll_stg=short_stg(http_cl=exchange,timef="15m")
    ok_ws=OKEXX_WS.OKEX_DATA_WS(on_tick_back=boll_stg.on_tick)
    sch=BackgroundScheduler(timezone='Asia/Shanghai')
    symbol1="BTC-USDT-SWAP"
    symbol2="ETH-USDT-SWAP"
    symbol3="LTC-USDT-SWAP"
    symbol4 = "ETC-USDT-SWAP"
    symbol5 = "TRX-USDT-SWAP"
    ok_ws.start()

    sch.add_job(boll_stg.on_15min_kline,trigger='cron',args=(symbol1,"15m",),minute='*/5')
    sch.add_job(boll_stg.on_15min_kline,trigger='cron',args=(symbol2,"15m",),minute='*/5')
    sch.add_job(boll_stg.on_15min_kline, trigger='cron', args=(symbol3, "15m",), minute='*/5')
    sch.add_job(boll_stg.on_15min_kline, trigger='cron', args=(symbol4, "15m",), minute='*/5')
    sch.add_job(boll_stg.on_15min_kline, trigger='cron', args=(symbol5, "15m",), minute='*/5')
    # sch.add_job(boll_stg.get_pos,trigger='cron',second='*/1'),
    # sch.add_job(boll_stg.on_hl,trigger='cron',args=(symbol,),minute='*/5')
    sch.start()
    # See PyCharm help at https://www.jetbrains.com/help/pycharm/
    while True:
        time.sleep(0.3)