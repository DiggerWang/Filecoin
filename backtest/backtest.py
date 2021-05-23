import joblib
import backtrader as bt
import pandas as pd
import numpy as np
import datetime

back_begin = datetime.date(2021, 3, 27)


"""
Strategy using Neural Network
"""
class Strategy_NN(bt.Strategy):
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.model = joblib.load('clf.m')
        self.xtest = pd.read_csv('xtest.csv').values
        self.order = []
        self.trade_list = []
 
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status == order.Rejected:
            self.log(f"order is rejected : order_ref:{order.ref}  order_info:{order.info}")
        if order.status == order.Margin:
            self.log(f"order need more margin : order_ref:{order.ref}  order_info:{order.info}")
        if order.status == order.Cancelled:
            self.log(f"order is concelled : order_ref:{order.ref}  order_info:{order.info}")
        if order.status == order.Partial:
            self.log(f"order is partial : order_ref:{order.ref}  order_info:{order.info}")
        if order.status == order.Completed:
            if order.isbuy():
                self.log("buy result : buy_price : {} , buy_cost : {} , commission : {}".format(
                            order.executed.price,order.executed.value,order.executed.comm))
            else:
                self.log("sell result : sell_price : {} , sell_cost : {} , commission : {}".format(
                            order.executed.price,order.executed.value,order.executed.comm))
    
    
    def notify_trade(self, trade):
        if trade.isclosed:
            self.log('closed symbol is : {} , total_profit : {} , net_profit : {}' .format(
                            trade.getdataname(),trade.pnl, trade.pnlcomm))
            self.trade_list.append([self.datas[0].datetime.date(0),trade.getdataname(),trade.pnl,trade.pnlcomm])
            
        if trade.isopen:
            self.log('open symbol is : {} , price : {} ' .format(
                            trade.getdataname(),trade.price))
        

    def next(self):
        if self.data.datetime.date() >= back_begin:
            try:
                y = self.model.predict(self.xtest[0,:].reshape(1,-1))
            except IndexError:
                y = None
            self.xtest = self.xtest[1:,:]
            
            if (not self.position):
                lots = int( self.broker.getvalue()/self.datas[0].close[0] )
                if y == 1:
                    self.log('BUY CREATE, %.2f' % self.datas[0].close[0])
                    self.buy(size=lots)
            elif (self.position.size > 0):
                if y == 0:
                    self.log('SELL CREATED {}'.format(self.datas[0].close[0]))
                    self.close()


"""
Strategy of MACD
"""
class Strategy_macd(bt.Strategy):
    params=(('p1',12),('p2',26),('p3',9),)
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.fc_all = pd.read_csv('fc_all.csv')
        self.order = []
        self.trade_list = []
        self.macdhist = bt.ind.MACDHisto(self.data,
                        period_me1=self.p.p1, 
                        period_me2=self.p.p2, 
                        period_signal=self.p.p3)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status == order.Rejected:
            self.log(f"order is rejected : order_ref:{order.ref}  order_info:{order.info}")
        if order.status == order.Margin:
            self.log(f"order need more margin : order_ref:{order.ref}  order_info:{order.info}")
        if order.status == order.Cancelled:
            self.log(f"order is concelled : order_ref:{order.ref}  order_info:{order.info}")
        if order.status == order.Partial:
            self.log(f"order is partial : order_ref:{order.ref}  order_info:{order.info}")
        if order.status == order.Completed:
            if order.isbuy():
                self.log("buy result : buy_price : {} , buy_cost : {} , commission : {}".format(
                            order.executed.price,order.executed.value,order.executed.comm))
            else:
                self.log("sell result : sell_price : {} , sell_cost : {} , commission : {}".format(
                            order.executed.price,order.executed.value,order.executed.comm))
    
    
    def notify_trade(self, trade):
        if trade.isclosed:
            self.log('closed symbol is : {} , total_profit : {} , net_profit : {}' .format(
                            trade.getdataname(),trade.pnl, trade.pnlcomm))
            self.trade_list.append([self.datas[0].datetime.date(0),trade.getdataname(),trade.pnl,trade.pnlcomm])
            
        if trade.isopen:
            self.log('open symbol is : {} , price : {} ' .format(
                            trade.getdataname(),trade.price))
        

    def next(self):
        if self.data.datetime.date() >= back_begin:
            if not self.position:
                lots = int( self.broker.getvalue()/self.datas[0].close[0] )
                if self.macdhist > 0:
                    self.order=self.buy(size=lots)
            else:
                if self.macdhist < 0:
                    self.close()


"""
Strategy of BBand
"""
class Strategy_bband(bt.Strategy):
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.fc_all = pd.read_csv('fc_all.csv')
        self.order = []
        self.trade_list = []
        self.line_top = bt.ind.BollingerBands(self.data).top
        self.line_bot = bt.ind.BollingerBands(self.data).bot

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status == order.Rejected:
            self.log(f"order is rejected : order_ref:{order.ref}  order_info:{order.info}")
        if order.status == order.Margin:
            self.log(f"order need more margin : order_ref:{order.ref}  order_info:{order.info}")
        if order.status == order.Cancelled:
            self.log(f"order is concelled : order_ref:{order.ref}  order_info:{order.info}")
        if order.status == order.Partial:
            self.log(f"order is partial : order_ref:{order.ref}  order_info:{order.info}")
        if order.status == order.Completed:
            if order.isbuy():
                self.log("buy result : buy_price : {} , buy_cost : {} , commission : {}".format(
                            order.executed.price,order.executed.value,order.executed.comm))
            else:
                self.log("sell result : sell_price : {} , sell_cost : {} , commission : {}".format(
                            order.executed.price,order.executed.value,order.executed.comm))
    
    
    def notify_trade(self, trade):
        if trade.isclosed:
            self.log('closed symbol is : {} , total_profit : {} , net_profit : {}' .format(
                            trade.getdataname(),trade.pnl, trade.pnlcomm))
            self.trade_list.append([self.datas[0].datetime.date(0),trade.getdataname(),trade.pnl,trade.pnlcomm])
            
        if trade.isopen:
            self.log('open symbol is : {} , price : {} ' .format(
                            trade.getdataname(),trade.price))
        

    def next(self):
        if self.data.datetime.date() >= back_begin:
            if not self.position:
                lots = int( self.broker.getvalue()/self.datas[0].close[0] )
                if self.data.close[0] < self.line_bot:
                    self.order=self.buy(size=lots)
            else:
                if self.data.close[0] > self.line_top:
                    self.close()


"""
Strategy of RSI
"""
class Strategy_rsi(bt.Strategy):
    params=(('short',30),('long',70),)
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.order = []
        self.trade_list = []
        self.rsi = bt.indicators.RSI_SMA(self.data.close, period=21)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status == order.Rejected:
            self.log(f"order is rejected : order_ref:{order.ref}  order_info:{order.info}")
        if order.status == order.Margin:
            self.log(f"order need more margin : order_ref:{order.ref}  order_info:{order.info}")
        if order.status == order.Cancelled:
            self.log(f"order is concelled : order_ref:{order.ref}  order_info:{order.info}")
        if order.status == order.Partial:
            self.log(f"order is partial : order_ref:{order.ref}  order_info:{order.info}")
        if order.status == order.Completed:
            if order.isbuy():
                self.log("buy result : buy_price : {} , buy_cost : {} , commission : {}".format(
                            order.executed.price,order.executed.value,order.executed.comm))
            else:
                self.log("sell result : sell_price : {} , sell_cost : {} , commission : {}".format(
                            order.executed.price,order.executed.value,order.executed.comm))
    
    
    def notify_trade(self, trade):
        if trade.isclosed:
            self.log('closed symbol is : {} , total_profit : {} , net_profit : {}' .format(
                            trade.getdataname(),trade.pnl, trade.pnlcomm))
            self.trade_list.append([self.datas[0].datetime.date(0),trade.getdataname(),trade.pnl,trade.pnlcomm])
            
        if trade.isopen:
            self.log('open symbol is : {} , price : {} ' .format(
                            trade.getdataname(),trade.price))
        

    def next(self):
        if self.data.datetime.date() >= back_begin:
            if not self.position:
                lots = int( self.broker.getvalue()/self.datas[0].close[0] )
                if self.rsi < self.params.short:
                    self.order=self.buy(size=lots)
            else:
                if self.rsi > self.params.long:
                    self.close()

def main():
    cerebro = bt.Cerebro()
    cerebro.addsizer(bt.sizers.FixedSize, stake=1000) 

    fc = bt.feeds.GenericCSVData(dataname='fc_all.csv',dtformat=('%Y-%m-%d'),datetime=0,high=1,low=2,open=3,close=4,volume=5,openinterest=-1)
    cerebro.adddata(fc)
    
    cerebro.broker.setcash(1000000.0)
    cerebro.addstrategy(Strategy_NN)
    #cerebro.addobserver(bt.observers.Benchmark)
    cerebro.broker.set_coc(True)  # 设置以当日收盘价成交
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.plot(start=back_begin)


if __name__ == '__main__':
    main()