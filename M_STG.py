import OKEX_HTTP
import pandas as pd
from ding_bot import DingDingWebHook
pd.set_option("expand_frame_repr",False)
import talib
class qqq():
    cnt=0
    que={}
    def add(self,numb):
        self.cnt=self.cnt+1
        self.que[self.cnt]=numb
    def ext(self):
        for i in range(1,self.cnt):
            self.que[i]=self.que[i+1]
        self.cnt=self.cnt-1
    def size(self):
        return self.cnt
    def quar(self,nb):
        return self.que[nb]
class xxx():
    cnt=0
    que={}
    def add(self,numb):
        self.cnt=self.cnt+1
        self.que[self.cnt]=numb
    def ext(self):
        for i in range(1,self.cnt):
            self.que[i]=self.que[i+1]
        self.cnt=self.cnt-1
    def size(self):
        return self.cnt
    def quar(self,nb):
        return self.que[nb]
class short_stg(object):
    hpq=qqq()
    lwq=xxx()
    flag = 0
    longbl = 0
    shortbl = 0
    bt = 0
    ls = 0
    pos_list=0
    blup1=0
    blup2=0
    blmd1=0
    blmd2=0
    bldw1=0
    bldw2=0
    hp=0
    lp=0
    http_cl=None
    now_pos=0
    now_tick=0
    act=0
    symbol=None
    long_entry_price=0
    short_entry_price=0
    winid=""
    winbg=0
    def __init__(self,http_cl:OKEX_HTTP.OKEX_FUTURE_http,timef:str):
        self.my_secret = 'SECd9ca319eed07d2626182c8eace7a7a7fccafee6635cc93ac9a5ea5e6d879f3a2'
        self.my_url = 'https://oapi.dingtalk.com/robot/send?access_token=0bd7d9367869ce22f34958e9fa964ec922d2f2260eb129ac7f325dd32f11a5bc'
        self.dingding = DingDingWebHook(secret=self.my_secret, url=self.my_url)
        self.http_cl=http_cl
        self.symbol = "BTC-USDT-SWAP"
        # print(self.symbol)
        self.timef=timef
        self.http_cl.set_lev(instId="BTC-USDT-SWAP", mgnMode="cross", lever="100")
        my_data = {
            "msgtype": "text",
            "text": {
                "content": "盯盘机器人已经上线目前盯盘币对：BTC ETH LTC TRX ETC"
            },
            "at": {
                "atMobiles": [],
                "isAtAll": False,
            }
        }
        self.dingding.send_meassage(my_data)
        self.act=False
        self.http_cl.set_pos("net_mode")
        self.on_15min_kline(instId=self.symbol,timef=self.timef)
        self.on_hl(instId=self.symbol)
        self.bt=0
        self.winbg=0
        self.flag=0
        self.shortbl=1
        self.longbl=1
        self.last_send_high=""
        self.last_send_low=""
        self.last_send_high1 = ""
        self.last_send_low1 = ""
    def on_15min_kline(self,instId:str,timef:str):
        res=self.http_cl.get_kline(instId,timef,"80")
        # 返回的第一条K线数据可能不是完整周期k线，返回值数组顺分别为是：[ts, o, h, l, c]
        df=pd.DataFrame(res,columns={"open_time":0,"open":1,"high":2,"low":3,"close":4})
        df=df[['open_time','open','high','low','close']]
        df['open_time']=pd.to_datetime(df['open_time'],unit='ms')
        # df = df.sort_values(by='open_time', ascending=True)
        # self.http_cl.place_order(instId=self.symbol,tdMode="cross",ccy="USDT",side="sell",ordType="market",sz="300")
        # print(self.symbol)
        df = df.sort_values(by='open_time', ascending=True)
        self.cal(df,instId,timef)

    def on_hl(self, instId: str):
        res = self.http_cl.get_kline(instId, "5m", "80")
        # 返回的第一条K线数据可能不是完整周期k线，返回值数组顺分别为是：[ts, o, h, l, c]
        df = pd.DataFrame(res, columns={"open_time": 0, "open": 1, "high": 2, "low": 3, "close": 4})
        df = df[['open_time', 'open', 'high', 'low', 'close']]
        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
        # df = df.sort_values(by='open_time', ascending=True)
        # self.http_cl.place_order(instId=self.symbol,tdMode="cross",ccy="USDT",side="sell",ordType="market",sz="300")
        # print(self.symbol)
        df = df.sort_values(by='open_time', ascending=True)
        # self.calhl(df)

    def calhl(self,df):
        self.win = 2
        if self.hpq.size() < 50:
            # df = df.sort_values(by='open_time', ascending=False)
            for xx in range(1, 51):
                x = 50 - xx
                self.upflagDownFrontier = True
                self.upflagUpFrontier0 = True
                self.upflagUpFrontier1 = True
                self.upflagUpFrontier2 = True
                self.upflagUpFrontier3 = True
                self.upflagUpFrontier4 = True
                self.downflagDownFrontier = True
                self.downflagUpFrontier0 = True
                self.downflagUpFrontier1 = True
                self.downflagUpFrontier2 = True
                self.downflagUpFrontier3 = True
                self.downflagUpFrontier4 = True
                for i in range(1, self.win + 1):
                    self.upflagDownFrontier = self.upflagDownFrontier and (
                                df.iloc[i - self.win - x - 1]['high'] < df.iloc[-self.win - x - 1]['high'])
                    self.upflagUpFrontier0 = self.upflagUpFrontier0 and (
                                df.iloc[-self.win - x - i - 1]['high'] < df.iloc[-self.win - x - 1]['high'])
                    self.upflagUpFrontier1 = self.upflagUpFrontier1 and (
                                df.iloc[-self.win - x - 1 - 1]['high'] <= df.iloc[-self.win - x - 1]['high'] and
                                df.iloc[-self.win - x - i - 1 - 1]['high'] < df.iloc[-self.win - x - 1]['high'])
                    self.upflagUpFrontier2 = self.upflagUpFrontier2 and (
                                df.iloc[-self.win - x - 1 - 1]['high'] <= df.iloc[-self.win - x - 1]['high'] and
                                df.iloc[-self.win - x - 2 - 1]['high'] <= df.iloc[-self.win - x - 1]['high'] and
                                df.iloc[-self.win - x - i - 2 - 1]['high'] < df.iloc[-self.win - x - 1]['high'])
                    self.upflagUpFrontier3 = self.upflagUpFrontier3 and (
                                df.iloc[-self.win - x - 1 - 1]['high'] <= df.iloc[-self.win - x - 1]['high'] and
                                df.iloc[-self.win - x - 2 - 1]['high'] <= df.iloc[-self.win - x - 1]['high'] and
                                df.iloc[-self.win - x - 3 - 1]['high'] <= df.iloc[-self.win - x - 1]['high'] and
                                df.iloc[-self.win - x - i - 3 - 1]['high'] < df.iloc[-self.win - x - 1]['high'])
                    self.upflagUpFrontier4 = self.upflagUpFrontier4 and (
                                df.iloc[-self.win - x - 1 - 1]['high'] <= df.iloc[-self.win - x - 1]['high'] and
                                df.iloc[-self.win - x - 2 - 1]['high'] <= df.iloc[-self.win - x - 1]['high'] and
                                df.iloc[-self.win - x - 3 - 1]['high'] <= df.iloc[-self.win - x - 1]['high'] and
                                df.iloc[-self.win - x - 4 - 1]['high'] <= df.iloc[-self.win - x - 1]['high']
                                and df.iloc[-self.win - x - i - 4 - 1]['high'] < df.iloc[-self.win - x - 1]['high'])
                self.flagUpFrontier = self.upflagUpFrontier0 or self.upflagUpFrontier1 or self.upflagUpFrontier2 or self.upflagUpFrontier3 or self.upflagUpFrontier4
                self.upFractal = (self.upflagDownFrontier and self.flagUpFrontier)
                # print(x,self.upFractal)
                if self.upFractal:
                    # print(df.iloc[-self.win-x-1]['open_time'])
                    # print(self.upFractal)
                    # print(df.iloc[-self.win-x-1]['high'])
                    highp = df.iloc[-self.win - x - 1]['high']
                elif self.hpq.size():
                    highp = self.hpq.quar(self.hpq.size())
                else:
                    highp = df.iloc[-self.win - x - 1]['high']
                if self.hpq.size() < 50:
                    self.hpq.add(highp)
                elif self.hpq.size() == 50:
                    self.hpq.ext()
                    self.hpq.add(highp)

                for i in range(1, self.win + 1):
                    self.downflagDownFrontier = self.downflagDownFrontier and (
                                df.iloc[i - self.win - x - 1]['low'] > df.iloc[-self.win - x - 1]['low'])
                    self.downflagUpFrontier0 = self.downflagUpFrontier0 and (
                                df.iloc[-self.win - x - i - 1]['low'] > df.iloc[-self.win - x - 1]['low'])
                    self.downflagUpFrontier1 = self.downflagUpFrontier1 and (
                                df.iloc[-self.win - x - 1 - 1]['low'] >= df.iloc[-self.win - x - 1]['low'] and
                                df.iloc[-self.win - x - i - 1 - 1]['low'] > df.iloc[-self.win - x - 1]['low'])
                    self.downflagUpFrontier2 = self.downflagUpFrontier2 and (
                                df.iloc[-self.win - x - 1 - 1]['low'] >= df.iloc[-self.win - x - 1]['low'] and
                                df.iloc[-self.win - x - 2 - 1]['low'] >= df.iloc[-self.win - x - 1]['low'] and
                                df.iloc[-self.win - x - i - 2 - 1]['low'] > df.iloc[-self.win - x - 1]['low'])
                    self.downflagUpFrontier3 = self.downflagUpFrontier3 and (
                                df.iloc[-self.win - x - 1 - 1]['low'] >= df.iloc[-self.win - x - 1]['low'] and
                                df.iloc[-self.win - x - 2 - 1]['low'] >= df.iloc[-self.win - x - 1]['low'] and
                                df.iloc[-self.win - x - 3 - 1]['low'] >= df.iloc[-self.win - x - 1]['low'] and
                                df.iloc[-self.win - x - i - 3 - 1]['low'] > df.iloc[-self.win - x - 1]['low'])
                    self.downflagUpFrontier4 = self.downflagUpFrontier4 and (
                                df.iloc[-self.win - x - 1 - 1]['low'] >= df.iloc[-self.win - x - 1]['low'] and
                                df.iloc[-self.win - x - 2 - 1]['low'] >= df.iloc[-self.win - x - 1]['low'] and
                                df.iloc[-self.win - x - 3 - 1]['low'] >= df.iloc[-self.win - x - 1]['low'] and
                                df.iloc[-self.win - x - 4 - 1]['low'] >= df.iloc[-self.win - x - 1]['low'] and
                                df.iloc[-self.win - x - i - 4 - 1]['low'] > df.iloc[-self.win - x - 1]['low'])
                self.flagDownFrontier = self.downflagUpFrontier0 or self.downflagUpFrontier1 or self.downflagUpFrontier2 or self.downflagUpFrontier3 or self.downflagUpFrontier4
                self.downFractal = (self.downflagDownFrontier and self.flagDownFrontier)

                if self.downFractal:
                    lowp = df.iloc[-self.win - x - 1]['low']
                    # print(df.iloc[-self.win-x-1]['low'])
                    # print(df.iloc[-self.win - x - 1]['open_time'])
                    # print(self.downFractal)
                elif self.lwq.size():
                    lowp = self.lwq.quar(self.lwq.size())
                else:
                    lowp = df.iloc[-self.win - x - 1]['low']
                if self.lwq.size() < 50:
                    self.lwq.add(lowp)
                elif self.lwq.size() == 50:
                    self.lwq.ext()
                    self.lwq.add(lowp)
            # print(df)
            # print(self.lwq.size())
            # print(self.hpq.size())
        else:
            # df = df.sort_values(by='open_time', ascending=True)
            self.upflagDownFrontier = True
            self.upflagUpFrontier0 = True
            self.upflagUpFrontier1 = True
            self.upflagUpFrontier2 = True
            self.upflagUpFrontier3 = True
            self.upflagUpFrontier4 = True
            self.downflagDownFrontier = True
            self.downflagUpFrontier0 = True
            self.downflagUpFrontier1 = True
            self.downflagUpFrontier2 = True
            self.downflagUpFrontier3 = True
            self.downflagUpFrontier4 = True
            for i in range(1, self.win + 1):
                self.upflagDownFrontier = self.upflagDownFrontier and (
                        df.iloc[i - self.win - 1]['high'] < df.iloc[-self.win - 1]['high'])
                self.upflagUpFrontier0 = self.upflagUpFrontier0 and (
                        df.iloc[-self.win - i - 1]['high'] < df.iloc[-self.win - 1]['high'])
                self.upflagUpFrontier1 = self.upflagUpFrontier1 and (
                        df.iloc[-self.win - 1 - 1]['high'] <= df.iloc[-self.win - 1]['high'] and
                        df.iloc[-self.win - i - 1 - 1]['high'] < df.iloc[-self.win - 1]['high'])
                self.upflagUpFrontier2 = self.upflagUpFrontier2 and (
                        df.iloc[-self.win - 1 - 1]['high'] <= df.iloc[-self.win - 1]['high'] and
                        df.iloc[-self.win - 2 - 1]['high'] <= df.iloc[-self.win - 1]['high'] and
                        df.iloc[-self.win - i - 2 - 1]['high'] < df.iloc[-self.win - 1]['high'])
                self.upflagUpFrontier3 = self.upflagUpFrontier3 and (
                        df.iloc[-self.win - 1 - 1]['high'] <= df.iloc[-self.win - 1]['high'] and
                        df.iloc[-self.win - 2 - 1]['high'] <= df.iloc[-self.win - 1]['high'] and
                        df.iloc[-self.win - 3 - 1]['high'] <= df.iloc[-self.win - 1]['high'] and
                        df.iloc[-self.win - i - 3 - 1]['high'] < df.iloc[-self.win - 1]['high'])
                self.upflagUpFrontier4 = self.upflagUpFrontier4 and (
                        df.iloc[-self.win - 1 - 1]['high'] <= df.iloc[-self.win - 1]['high'] and
                        df.iloc[-self.win - 2 - 1]['high'] <= df.iloc[-self.win - 1]['high'] and
                        df.iloc[-self.win - 3 - 1]['high'] <= df.iloc[-self.win - 1]['high'] and
                        df.iloc[-self.win - 4 - 1]['high'] <= df.iloc[-self.win - 1]['high']
                        and df.iloc[-self.win - i - 4 - 1]['high'] < df.iloc[-self.win - 1]['high'])
            self.flagUpFrontier = self.upflagUpFrontier0 or self.upflagUpFrontier1 or self.upflagUpFrontier2 or self.upflagUpFrontier3 or self.upflagUpFrontier4
            self.upFractal = (self.upflagDownFrontier and self.flagUpFrontier)
            # print(x,self.upFractal)
            if self.upFractal:
                # print(df.iloc[-self.win-x-1]['open_time'])
                # print(self.upFractal)
                highp = df.iloc[-self.win - 1]['high']
            elif self.hpq.size():
                highp = self.hpq.quar(self.hpq.size())
            else:
                highp = df.iloc[-self.win - 1]['high']
            if self.hpq.size() < 50:
                self.hpq.add(highp)
            elif self.hpq.size() == 50:
                self.hpq.ext()
                self.hpq.add(highp)
            for i in range(1, self.win + 1):
                self.downflagDownFrontier = self.downflagDownFrontier and (
                        df.iloc[i - self.win - 1]['low'] > df.iloc[-self.win - 1]['low'])
                self.downflagUpFrontier0 = self.downflagUpFrontier0 and (
                        df.iloc[-self.win - i - 1]['low'] > df.iloc[-self.win - 1]['low'])
                self.downflagUpFrontier1 = self.downflagUpFrontier1 and (
                        df.iloc[-self.win - 1 - 1]['low'] >= df.iloc[-self.win - 1]['low'] and
                        df.iloc[-self.win - i - 1 - 1]['low'] > df.iloc[-self.win - 1]['low'])
                self.downflagUpFrontier2 = self.downflagUpFrontier2 and (
                        df.iloc[-self.win - 1 - 1]['low'] >= df.iloc[-self.win - 1]['low'] and
                        df.iloc[-self.win - 2 - 1]['low'] >= df.iloc[-self.win - 1]['low'] and
                        df.iloc[-self.win - i - 2 - 1]['low'] > df.iloc[-self.win - 1]['low'])
                self.downflagUpFrontier3 = self.downflagUpFrontier3 and (
                        df.iloc[-self.win - 1 - 1]['low'] >= df.iloc[-self.win - 1]['low'] and
                        df.iloc[-self.win - 2 - 1]['low'] >= df.iloc[-self.win - 1]['low'] and
                        df.iloc[-self.win - 3 - 1]['low'] >= df.iloc[-self.win - 1]['low'] and
                        df.iloc[-self.win - i - 3 - 1]['low'] > df.iloc[-self.win - 1]['low'])
                self.downflagUpFrontier4 = self.downflagUpFrontier4 and (
                        df.iloc[-self.win - 1 - 1]['low'] >= df.iloc[-self.win - 1]['low'] and
                        df.iloc[-self.win - 2 - 1]['low'] >= df.iloc[-self.win - 1]['low'] and
                        df.iloc[-self.win - 3 - 1]['low'] >= df.iloc[-self.win - 1]['low'] and
                        df.iloc[-self.win - 4 - 1]['low'] >= df.iloc[-self.win - 1]['low'] and
                        df.iloc[-self.win - i - 4 - 1]['low'] > df.iloc[-self.win - 1]['low'])
            self.flagDownFrontier = self.downflagUpFrontier0 or self.downflagUpFrontier1 or self.downflagUpFrontier2 or self.downflagUpFrontier3 or self.downflagUpFrontier4
            self.downFractal = (self.downflagDownFrontier and self.flagDownFrontier)
            if self.downFractal:
                lowp = df.iloc[-self.win - 1]['low']
            elif self.lwq.size():
                lowp = self.lwq.quar(self.lwq.size())
            else:
                lowp = df.iloc[-self.win - 1]['low']
            if self.lwq.size() < 50:
                self.lwq.add(lowp)
            elif self.lwq.size() == 50:
                self.lwq.ext()
                self.lwq.add(lowp)
        self.hp = 0.0
        for i in range(1, self.hpq.size() + 1):
            self.hp = max(self.hp, float(self.hpq.quar(i)))
        self.lp = 99999999.0
        for i in range(1, self.lwq.size() + 1):
            self.lp = min(self.lp, float(self.lwq.quar(i)))
        # print(self.hp,self.lp)
        self.act = True

    def on_tick(self,tick_data):
        pass
        if self.act==False:
            return
        self.now_tick=float(tick_data)
        if self.longbl==1 and self.bt==0:
            if self.now_tick<self.blmd1+self.now_tick*0.001 and self.now_tick>self.blmd1-self.now_tick*0.001:
                self.longbl=0
        if self.shortbl==1 and self.bt==0  :
            if self.now_tick<self.blmd1+self.now_tick*0.001 and self.now_tick>self.blmd1-self.now_tick*0.001:
                self.shortbl=0
        if self.bt==0:
            if self.now_tick>self.hp:
                if self.now_tick>self.blup1:
                    if 1:
                        if self.longbl==0:
                            self.longbl=1
                            self.bt=1
                            self.ls=self.blmd1
                            print("long",self.now_tick)
                            self.http_cl.place_order(instId=self.symbol, tdMode="cross", ccy="USDT",
                                                     side="buy", ordType="market", sz="1")
                            self.long_entry_price=self.now_tick+2
            elif self.now_tick<self.lp:
                if self.now_tick<self.bldw1:
                    if 1:
                        if self.shortbl==0:
                            self.shortbl=1
                            self.bt=-1
                            self.ls=self.blmd1
                            print("short",self.now_tick)
                            self.http_cl.place_order(instId=self.symbol, tdMode="cross", ccy="USDT",
                                                     side="sell", ordType="market", sz="1")
                            self.short_entry_price=self.now_tick-2


        if self.bt>0 and self.now_pos>0:
            if self.now_tick>self.long_entry_price+0.0012*self.long_entry_price and self.winbg==0:
                self.winid=self.http_cl.place_order(instId=self.symbol,tdMode="cross",ccy="USDT",
                                         side="sell",ordType="limit",sz=str(abs(self.now_pos)),px=str(1.002*self.long_entry_price))
                self.winid=self.winid['ordId']
                self.winbg=1
            elif self.now_tick<self.ls or self.now_tick<self.long_entry_price*0.998:
                if self.winbg:
                    self.http_cl.cancel_ord(instId=self.symbol,ordId=self.winid)
                    self.winbg=0
                self.http_cl.place_order(instId=self.symbol, tdMode="cross", ccy="USDT",
                                             side="sell", ordType="limit", sz=str(abs(self.now_pos)),
                                             px=str(self.now_tick - 2))
                self.bt=0
        elif self.bt<0 and self.now_pos<0:
            if self.now_tick<self.short_entry_price-self.short_entry_price*0.0012 and self.winbg==0:
                self.winid=self.http_cl.place_order(instId=self.symbol,tdMode="cross",ccy="USDT",
                                         side="buy",ordType="limit",sz=str(abs(self.now_pos)),px=str(0.998*self.short_entry_price))
                self.winbg=1
                self.winid=self.winid['ordId']
            elif self.now_tick>self.ls or self.now_tick>self.short_entry_price*1.002:
                if self.winbg:
                    self.http_cl.cancel_ord(instId=self.symbol,ordId=self.winid)
                    self.winbg=0
                self.http_cl.place_order(instId=self.symbol, tdMode="cross", ccy="USDT",
                                             side="buy", ordType="limit", sz=str(abs(self.now_pos)),
                                             px=str(self.now_tick - 2))
                self.bt=0
        if self.bt and self.winbg:
            if self.now_pos==0:
                self.winbg=0
                self.bt=0


    def get_pos(self):
        self.post_list=self.http_cl.get_pos("SWAP")
        # print("s")
        # print(self.post_list)
        if len(self.post_list):
            lst=pd.DataFrame(self.post_list)
            self.now_pos=int(lst.iloc[0]['pos'])
        else:
            self.now_pos=0
        # print(self.now_pos)
    def cal(self,df,sb:str,timef:str):
        # print("-")
        self.bollwind=20
        df=df.drop(df.tail(1).index)
        # print(df)
        current_bar=df.iloc[-1]
        # df = df.sort_values(by='open_time', ascending=True)
        # df['bollup'],df['bollmid'],df['bolldw']=talib._ta_lib.BBANDS(df['close'],timeperiod=self.bollwind,nbdevup=2,nbdevdn=2,matype=0)
        df['macd'],df['signal'],df['hist']=talib._ta_lib.MACD(df['close'],12,26,9)
        last_1=df.iloc[-1]
        last_2=df.iloc[-2]
        # self.blup1=last_1['bollup']
        # self.blup2=last_2['bollup']
        # self.blmd1=last_1['bollmid']
        # self.blmd2=last_2['bollmid']
        # self.bldw1=last_1['bolldw']
        # self.bldw2=last_2['bolldw']
        self.macd_hist1=last_1['hist']
        self.macd_hist2=last_2['hist']
        # print(df.iloc[-1]['open_time'])
        # print("5上轨道:",self.blup1,self.blup2)
        # print("5中轨道:",self.blmd1,self.blmd2)
        # print("5下轨道:",self.bldw1,self.bldw2)
        # print("15min_macd_hist1",self.macd_hist1)
        # print("15min_macd_hist2",self.macd_hist2)
        last_macd_high_val = -1.0
        last_macd_high_loc = 0
        last_macd_low_val = -1.0
        last_macd_low_loc = 0
        last_macd_high_hist = 0.0
        last_macd_low_hist = 0.0
        self.fractals_win=4

        for x in range(1, 66):
            if df.iloc[-x-self.fractals_win-1]['hist']<0 :
                continue
            self.upflagDownFrontier = True
            self.upflagUpFrontier0 = True
            self.upflagUpFrontier1 = True
            self.upflagUpFrontier2 = True
            self.upflagUpFrontier3 = True
            self.upflagUpFrontier4 = True

            for i in range(1, self.fractals_win + 1):
                self.upflagDownFrontier = self.upflagDownFrontier and (
                        df.iloc[i - self.fractals_win - x - 1]['hist'] < df.iloc[-self.fractals_win - x - 1]['hist'])
                self.upflagUpFrontier0 = self.upflagUpFrontier0 and (
                        df.iloc[-self.fractals_win - x - i - 1]['hist'] < df.iloc[-self.fractals_win - x - 1]['hist'])
                self.upflagUpFrontier1 = self.upflagUpFrontier1 and (
                        df.iloc[-self.fractals_win - x - 1 - 1]['hist'] <= df.iloc[-self.fractals_win - x - 1]['hist'] and
                        df.iloc[-self.fractals_win - x - i - 1 - 1]['hist'] < df.iloc[-self.fractals_win - x - 1]['hist'])
                self.upflagUpFrontier2 = self.upflagUpFrontier2 and (
                        df.iloc[-self.fractals_win - x - 1 - 1]['hist'] <= df.iloc[-self.fractals_win - x - 1]['hist'] and
                        df.iloc[-self.fractals_win - x - 2 - 1]['hist'] <= df.iloc[-self.fractals_win - x - 1]['hist'] and
                        df.iloc[-self.fractals_win - x - i - 2 - 1]['hist'] < df.iloc[-self.fractals_win - x - 1]['hist'])
                self.upflagUpFrontier3 = self.upflagUpFrontier3 and (
                        df.iloc[-self.fractals_win - x - 1 - 1]['hist'] <= df.iloc[-self.fractals_win - x - 1]['hist'] and
                        df.iloc[-self.fractals_win - x - 2 - 1]['hist'] <= df.iloc[-self.fractals_win - x - 1]['hist'] and
                        df.iloc[-self.fractals_win - x - 3 - 1]['hist'] <= df.iloc[-self.fractals_win - x - 1]['hist'] and
                        df.iloc[-self.fractals_win - x - i - 3 - 1]['hist'] < df.iloc[-self.fractals_win - x - 1]['hist'])
                self.upflagUpFrontier4 = self.upflagUpFrontier4 and (
                        df.iloc[-self.fractals_win - x - 1 - 1]['hist'] <= df.iloc[-self.fractals_win - x - 1]['hist'] and
                        df.iloc[-self.fractals_win - x - 2 - 1]['hist'] <= df.iloc[-self.fractals_win - x - 1]['hist'] and
                        df.iloc[-self.fractals_win - x - 3 - 1]['hist'] <= df.iloc[-self.fractals_win - x - 1]['hist'] and
                        df.iloc[-self.fractals_win - x - 4 - 1]['hist'] <= df.iloc[-self.fractals_win - x - 1]['hist']
                        and df.iloc[-self.fractals_win - x - i - 4 - 1]['hist'] < df.iloc[-self.fractals_win - x - 1]['hist'])

            self.flagUpFrontier = self.upflagUpFrontier0 or self.upflagUpFrontier1 or self.upflagUpFrontier2 or self.upflagUpFrontier3 or self.upflagUpFrontier4
            self.upFractal = (self.upflagDownFrontier and self.flagUpFrontier)

            if self.upFractal:
                last_macd_high_hist=df.iloc[ -self.fractals_win -x-1]['hist']
                last_macd_high_loc=df.iloc[-self.fractals_win-x-1]['open_time']
                last_macd_high_val=df.iloc[-self.fractals_win-x-1]['high']
                for j in range(0,self.fractals_win-2):
                    last_macd_high_val = max(last_macd_high_val, df.iloc[-self.fractals_win - x - 1 + j]['high'])
                    last_macd_high_val = max(last_macd_high_val, df.iloc[-self.fractals_win - x - 1 - j]['high'])
                # print(last_macd_high_loc,last_macd_high_hist)
                break
        for x in range(1, 66):
            if df.iloc[-x-self.fractals_win-1]['hist']>0 :
                continue
            self.downflagDownFrontier = True
            self.downflagUpFrontier0 = True
            self.downflagUpFrontier1 = True
            self.downflagUpFrontier2 = True
            self.downflagUpFrontier3 = True
            self.downflagUpFrontier4 = True
            for i in range(1, self.fractals_win + 1):
                self.downflagDownFrontier = self.downflagDownFrontier and (
                        df.iloc[i - self.fractals_win - x - 1]['hist'] > df.iloc[-self.fractals_win - x - 1]['hist'])
                self.downflagUpFrontier0 = self.downflagUpFrontier0 and (
                        df.iloc[-self.fractals_win - x - i - 1]['hist'] > df.iloc[-self.fractals_win - x - 1]['hist'])
                self.downflagUpFrontier1 = self.downflagUpFrontier1 and (
                        df.iloc[-self.fractals_win - x - 1 - 1]['hist'] >= df.iloc[-self.fractals_win - x - 1]['hist'] and
                        df.iloc[-self.fractals_win - x - i - 1 - 1]['hist'] > df.iloc[-self.fractals_win - x - 1]['hist'])
                self.downflagUpFrontier2 = self.downflagUpFrontier2 and (
                        df.iloc[-self.fractals_win - x - 1 - 1]['hist'] >= df.iloc[-self.fractals_win - x - 1]['hist'] and
                        df.iloc[-self.fractals_win - x - 2 - 1]['hist'] >= df.iloc[-self.fractals_win - x - 1]['hist'] and
                        df.iloc[-self.fractals_win - x - i - 2 - 1]['hist'] > df.iloc[-self.fractals_win - x - 1]['hist'])
                self.downflagUpFrontier3 = self.downflagUpFrontier3 and (
                        df.iloc[-self.fractals_win - x - 1 - 1]['hist'] >= df.iloc[-self.fractals_win - x - 1]['hist'] and
                        df.iloc[-self.fractals_win - x - 2 - 1]['hist'] >= df.iloc[-self.fractals_win - x - 1]['hist'] and
                        df.iloc[-self.fractals_win - x - 3 - 1]['hist'] >= df.iloc[-self.fractals_win - x - 1]['hist'] and
                        df.iloc[-self.fractals_win - x - i - 3 - 1]['hist'] > df.iloc[-self.fractals_win - x - 1]['hist'])
                self.downflagUpFrontier4 = self.downflagUpFrontier4 and (
                        df.iloc[-self.fractals_win - x - 1 - 1]['hist'] >= df.iloc[-self.fractals_win - x - 1]['hist'] and
                        df.iloc[-self.fractals_win - x - 2 - 1]['hist'] >= df.iloc[-self.fractals_win - x - 1]['hist'] and
                        df.iloc[-self.fractals_win - x - 3 - 1]['hist'] >= df.iloc[-self.fractals_win - x - 1]['hist'] and
                        df.iloc[-self.fractals_win - x - 4 - 1]['hist'] >= df.iloc[-self.fractals_win - x - 1]['hist'] and
                        df.iloc[-self.fractals_win - x - i - 4 - 1]['hist'] > df.iloc[-self.fractals_win - x - 1]['hist'])

            self.flagDownFrontier = self.downflagUpFrontier0 or self.downflagUpFrontier1 or self.downflagUpFrontier2 or self.downflagUpFrontier3 or self.downflagUpFrontier4
            self.downFractal = (self.downflagDownFrontier and self.flagDownFrontier)

            if self.downFractal:
                last_macd_low_hist=df.iloc[-self.fractals_win-x-1]['hist']
                last_macd_low_loc=df.iloc[-self.fractals_win-x-1]['open_time']
                last_macd_low_val=df.iloc[-self.fractals_win-x-1]['low']
                for j in range(0,self.fractals_win-2):
                    last_macd_low_val=min(last_macd_low_val,df.iloc[-self.fractals_win-x-1+j]['low'])
                    last_macd_low_val=min(last_macd_low_val,df.iloc[-self.fractals_win-x-1-j]['low'])
                break
        now_min=99999999.0
        now_max=0.0
        for j in range(1,3):
            now_min=min(now_min,float(df.iloc[-j]['low']))
            now_max=max(now_max,float(df.iloc[-j]['high']))

        print("当前时间：",df.iloc[-1]['open_time'],"symbol:",sb)
        print("high_hist_time",last_macd_high_loc)
        print("val:",last_macd_high_hist)
        print(last_macd_high_val)
        print("low_hist_time",last_macd_low_loc)
        print("val:", last_macd_low_hist)
        print(last_macd_low_val)
        print(now_max,now_min)
        # print(type(now_min))
        if df.iloc[-2]['hist']<df.iloc[-3]['hist'] and df.iloc[-1]['hist']>df.iloc[-2]['hist']:
            if now_min<float(last_macd_low_val) and df.iloc[-1]['hist']>last_macd_low_hist:
                # print(df.iloc[-1]['open_time'], "当前时间、", "symbol:", sb)
                # print("底背离")
                if self.last_send_low!=df.iloc[-1]['open_time']:
                    self.last_send_low=df.iloc[-1]['open_time']
                    my_data = {
                        "msgtype": "text",
                        "text": {
                            "content":  "当前时间:" +str(df.iloc[-1]['open_time']) + "\n"+"symbol:" + str(sb) +"周期"+timef+ "\n" + "底背离！"
                        },
                        "at": {
                            "atMobiles": [],
                            "isAtAll": False,
                        }
                    }
                    self.dingding.send_meassage(my_data)

        elif df.iloc[-2]['hist']>df.iloc[-3]['hist'] and df.iloc[-1]['hist']<df.iloc[-2]['hist']:
            if now_max>float(last_macd_high_val) and df.iloc[-1]['hist']<last_macd_high_hist:
                # print(df.iloc[-1]['open_time'], "当前时间、", "symbol:", sb)
                # print("顶背离")
                if self.last_send_high != df.iloc[-1]['open_time']:
                    self.last_send_high = df.iloc[-1]['open_time']
                    my_data = {
                        "msgtype": "text",
                        "text": {
                            "content": "当前时间:" + str(df.iloc[-1]['open_time']) + "\n" + "symbol:" + str(sb) +"周期"+timef+  "\n" + "顶背离！"
                        },
                        "at": {
                            "atMobiles": [],
                            "isAtAll": False,
                        }
                    }
                    self.dingding.send_meassage(my_data)
            pass
        if df.iloc[-1]['hist']<0 and df.iloc[-1]['hist']>df.iloc[-2]['hist']:
            if df.iloc[-1]['hist']>last_macd_low_hist and df.iloc[-2]['hist']<df.iloc[-3]['hist']:
                # print(df.iloc[-1]['open_time'], "当前时间、", "symbol:", sb)
                # print("macd底部抬高")
                if self.last_send_low1 != df.iloc[-1]['open_time']:
                    self.last_send_low1 = df.iloc[-1]['open_time']
                    my_data = {
                        "msgtype": "text",
                        "text": {
                            "content": "当前时间:" + str(df.iloc[-1]['open_time']) + "\n" + "symbol:" + str(sb) +"周期"+timef+  "\n" + "macd底部抬高！"
                        },
                        "at": {
                            "atMobiles": [],
                            "isAtAll": False,
                        }
                    }
                    self.dingding.send_meassage(my_data)
        elif df.iloc[-1]['hist']>0 and df.iloc[-1]['hist']<df.iloc[-2]['hist']:
            if df.iloc[-1]['hist']<last_macd_high_hist and df.iloc[-2]['hist']>df.iloc[-3]['hist']:
                # print(df.iloc[-1]['open_time'], "当前时间、", "symbol:", sb)
                # print("macd顶部降低")
                if self.last_send_high1 != df.iloc[-1]['open_time']:
                    self.last_send_high1 = df.iloc[-1]['open_time']
                    my_data = {
                        "msgtype": "text",
                        "text": {
                            "content": "当前时间:" + str(df.iloc[-1]['open_time']) + "\n" + "symbol:" + str(
                                sb) +"周期"+timef+ "\n" + "macd顶部降低！"
                        },
                        "at": {
                            "atMobiles": [],
                            "isAtAll": False,
                        }
                    }
                    self.dingding.send_meassage(my_data)
            pass

# if __name__ == '__main__':
