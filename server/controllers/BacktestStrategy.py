
from numpy import fabs, true_divide
from server.controllers import ChannelFunctions
from server.models import StockModel
from backtesting import Strategy,Backtest #引入回測和交易策略功能
import talib
import math
import pandas as pd
import yfinance as yf
from pandas_datareader import data
import pandas as pd
from datetime import datetime
from server import server_filePath

class BacktestStrategyInfo():
    def __init__(self):
        self.account_money = 500000 #@param {type:"integer"}
        self.dollar_per_point =  1000#@param {type:"integer"}
        self.start_day = "2010-01-01"#@param {type:"date"}
        self.end_day = "2021-08-04"#@param {type:"date"}
        #允許只下多單還是空單
        self.open_long_trade = True #@param {type:"boolean"}
        self.open_short_trade = False #@param {type:"boolean"}
        self.tomorrow_action = {}
    def save_action(self,Date,buy_sell,UnitNumber,BuyPrice,SellPrice,long_short):
        self.tomorrow_action['Date'] = str(Date)
        self.tomorrow_action['Buy_sell'] = str(buy_sell)
        self.tomorrow_action['UnitNumber'] = str(UnitNumber)
        self.tomorrow_action['BuyPrice'] = str(BuyPrice)
        self.tomorrow_action['SellPrice'] = str(SellPrice)
        self.tomorrow_action['long_short'] = str(long_short)

use_BacktestInfo = BacktestStrategyInfo()

# 唐西奇回測策略
class DONCHCross(Strategy): #使用backtesting.py的Strategy功能
    buy_price = 0
    break_susses = False
    break_price = 0
    is_long_or_short = 0
    next_buy_price_long = 0
    next_buy_price_short = 0
    stop_price_long = 0
    stop_price_short = 0
    now_cash = 0
    clear_trade_mark = False
    backtestInfo = use_BacktestInfo
    def init(self):
        super().init()
        # Precompute the two moving averages
        high = pd.Series(self.data.High)
        low = pd.Series(self.data.Low)
        NATR = talib.ATR(self.data['High'],self.data['Low'],self.data['Close'],20)
        self.now_cash = self.equity
        D_up,D_mid,D_low = ChannelFunctions.DONCH(high,low)
        D_up_55,D_mid_55,D_low_55 = ChannelFunctions.DONCH(high,low,55)
        D_up_10,D_mid_10,D_low_10 = ChannelFunctions.DONCH(high,low,10)

        # Precompute signal
        signal_down = (low <= D_low) & (low.shift() > D_low.shift())
        signal_up = (high >= D_up) & (high.shift() < D_up.shift())
        # Precompute signal
        signal_down_55 = (low <= D_low_55) & (low.shift() > D_low_55.shift())
        signal_up_55 = (high >= D_up_55) & (high.shift() < D_up_55.shift())
        # Precompute signal
        signal_down_10 = (low <= D_low_10) & (low.shift() > D_low_10.shift())
        signal_up_10 = (high >= D_up_10) & (high.shift() < D_up_10.shift())
        # combine signal
        signal = signal_up.copy()
        signal[signal_down] = -1
        # combine signal
        signal_55 = signal_up_55.copy()
        signal_55[signal_down_55] = -1
        # combine signal
        signal_10 = signal_up_10.copy()
        signal_10[signal_down_10] = -1
        # plot sma

        # set signal to trade
        self.signal = self.I(lambda x: signal, 'signal')
        self.signal_55 = self.I(lambda x: signal_55, 'signal_55')
        self.signal_10 = self.I(lambda x: signal_10, 'signal_10')
        self.D_up = self.I(lambda x: D_up, 'D_up')
        self.D_mid = self.I(lambda x: D_mid, 'D_mid')
        self.D_low = self.I(lambda x: D_low, 'D_low')
        self.NATR = self.I(lambda x: NATR, 'NATR')

    def next(self):
        super().next()
        entry_size = self.signal[-1]
        entry_size_55 = self.signal_55[-1]
        entry_size_10 = self.signal_10[-1]
        close = self.data.Close[-1]
        date = self.data.index[-1]
        NATR = self.NATR[-1]
        
        if self.trades.__len__() > 0:
          print(str(date) + '--目前持有:' + str(self.trades.__len__()) + '張單')
        else:
          if self.clear_trade_mark == True:
            if self.equity < self.now_cash * 0.9:
              self.now_cash = math.floor(self.now_cash * 0.8)
              self.clear_trade_mark = False
              print(str(date) + '--資金部位限縮-now_cash-' + str(self.now_cash))
            elif self.equity > self.now_cash:
              self.now_cash = math.floor(self.equity)
              self.clear_trade_mark = False
              print(str(date) + '--資金部位更新-now_cash-' + str(self.now_cash))
            else:
              self.clear_trade_mark = False
          
        Unit = (self.now_cash * 0.01) / (NATR * self.backtestInfo.dollar_per_point)  
        if self.backtestInfo.open_long_trade == True:
          #突破忽略計算(多頭)
          if self.break_price > 0 and self.is_long_or_short > 0:
            if close > self.break_price - float(2*NATR):
              self.break_susses = True
            else:
              #失敗RESET
              self.break_susses = False
              self.break_price = 0
              self.is_long_or_short = 0
          
          if entry_size > 0 or entry_size_55 > 0:
            self.break_price = close
            self.is_long_or_short = 1

        if self.backtestInfo.open_short_trade == True:
          #突破忽略計算(空頭)
          if self.break_price > 0 and self.is_long_or_short < 0:
            if close < self.break_price + float(2*NATR):
              self.break_susses = True
            else:
              #失敗RESET
              self.break_susses = False
              self.break_price = 0
              self.is_long_or_short = 0
          
          if entry_size < 0 or entry_size_55 < 0:
            self.break_price = close
            self.is_long_or_short = -1

        if self.backtestInfo.open_long_trade == True:
          #反向突破10日最低價，認賠殺出!!
          if self.trades.__len__() > 0 and entry_size_10 < 0:
            for trade in self.trades:
              if trade.is_long:
                trade.close()
                self.next_buy_price_long = 0
                self.clear_trade_mark = True
                print('--'+"多單殺出:",close,self.trades.__len__(),self.stop_price_long)
                self.backtestInfo.save_action(str(date),'sell',self.trades.__len__(),close,self.stop_price_long,'long')
        if self.backtestInfo.open_short_trade == True:
          #正向突破10日最高價，認賠殺出!!
          if self.trades.__len__() > 0 and entry_size_10 > 0:
            for trade in self.trades:
              if trade.is_short:
                trade.close()
                self.next_buy_price_short = 0
                self.clear_trade_mark = True
                print('--'+"空單殺出:",close,self.trades.__len__(),self.stop_price_short)
                self.backtestInfo.save_action(str(date),'sell',self.trades.__len__(),close,self.stop_price_short,'short')
        if self.backtestInfo.open_long_trade == True:
          #股價下跌2N以上，止損賣出!!
          if self.trades.__len__() > 0 and close <= self.stop_price_long:
            for trade in self.trades:
              if trade.is_long:
                trade.close()
                self.next_buy_price_long = 0
                self.clear_trade_mark = True
                print('--'+"多單止損:",close,self.trades.__len__(),self.stop_price_long)
                self.backtestInfo.save_action(str(date),'sell',self.trades.__len__(),close,self.stop_price_long,'long')
        if self.backtestInfo.open_short_trade == True:
          #股價上升2N以上，止損賣出!!
          if self.trades.__len__() > 0 and close >= self.stop_price_short:
            for trade in self.trades:
              if trade.is_short:
                trade.close()
                self.next_buy_price_short = 0
                self.clear_trade_mark = True
                print('--'+"空單止損:",close,self.trades.__len__(),self.stop_price_short)
                self.backtestInfo.save_action(str(date),'sell',self.trades.__len__(),close,self.stop_price_short,'short')
        if self.trades.__len__() == 0:
          self.next_buy_price_short = 0
          self.next_buy_price_long = 0
          self.stop_price_long = 0
          self.stop_price_short = 0

        if self.backtestInfo.open_long_trade == True:
          #正向突破20日最高價，進場做多!!
          Temp_sl = close - (2*NATR)#止損價格
          Temp_size = math.floor(float(Unit))#一次購買單位
          if Temp_size <= 0:
            print('--Size=' + str(Temp_size) + ' is too small')
            return
          if Temp_sl < 0:
            Temp_sl = 0
          if self.trades.__len__() < 1:#突破點進場
            if entry_size > 0 and self.break_susses == False:
              print('--'+"20 多單進場:size="+str(math.floor(float(Unit))*self.backtestInfo.dollar_per_point),'sl = ' + str(Temp_sl))
              self.next_buy_price_long = close + (NATR/2)
              self.buy(size = math.floor(float(Unit))*self.backtestInfo.dollar_per_point)
              self.stop_price_long = Temp_sl
              self.backtestInfo.save_action(str(date),'buy',self.trades.__len__(),close,self.stop_price_long,'long')
              return
            if entry_size_55 > 0:
              print('--' +"55 多單進場:size="+str(math.floor(float(Unit))*self.backtestInfo.dollar_per_point),'sl = ' + str(Temp_sl))
              self.next_buy_price_long = close + (NATR/2)
              self.buy(size = math.floor(float(Unit))*self.backtestInfo.dollar_per_point)
              self.stop_price_long = Temp_sl
              self.backtestInfo.save_action(str(date),'buy',self.trades.__len__(),close,self.stop_price_long,'long')
              return
          elif self.trades.__len__() < 4 and self.next_buy_price_long > 0:#突破之後加碼的地方
            if close > self.next_buy_price_long:
              self.next_buy_price_long = close + (NATR/2)
              print('--' +"多單加碼:size="+str(math.floor(float(Unit))*self.backtestInfo.dollar_per_point),'sl = ' + str(Temp_sl) +'-' +str(self.trades.__len__()))
              self.stop_price_long = Temp_sl
              self.buy(size = math.floor(float(Unit))*self.backtestInfo.dollar_per_point) 
              self.backtestInfo.save_action(str(date),'buy',self.trades.__len__(),close,self.stop_price_long,'long')
              return

        if self.backtestInfo.open_short_trade == True:
          #反向突破20日最低價，進場做空!!
          Temp_sl = close + (2*NATR)#止損價格
          Temp_size = math.floor(float(Unit))#一次購買單位
          if Temp_size <= 0:
            print('--Size=' + str(Temp_size) + ' is too small')
            return
          if Temp_sl < 0:
            Temp_sl = 0
          if self.trades.__len__() < 1:#突破點進場
            if entry_size < 0 and self.break_susses == False:
              print('--'+"20 空單進場:size="+str(math.floor(float(Unit))*self.backtestInfo.dollar_per_point),'sl = ' + str(Temp_sl))
              self.next_buy_price_short = close - (NATR/2)
              self.sell(size = math.floor(float(Unit))*self.backtestInfo.dollar_per_point)
              self.stop_price_short = Temp_sl
              self.backtestInfo.save_action(str(date),'buy',self.trades.__len__(),close,self.stop_price_short,'short')
              return
            if entry_size_55 < 0:
              print('--' +"55 空單進場:size="+str(math.floor(float(Unit))*self.backtestInfo.dollar_per_point),'sl = ' + str(Temp_sl))
              self.next_buy_price_short = close - (NATR/2)
              self.sell(size = math.floor(float(Unit))*self.backtestInfo.dollar_per_point)
              self.stop_price_short = Temp_sl
              self.backtestInfo.save_action(str(date),'buy',self.trades.__len__(),close,self.stop_price_short,'short')
              return
          elif self.trades.__len__() < 4 and self.next_buy_price_short > 0:#突破之後加碼的地方
            if close < self.next_buy_price_short:
              self.next_buy_price_short = close - (NATR/2)
              print('--' +"空單加碼:size="+str(math.floor(float(Unit))*self.backtestInfo.dollar_per_point),'sl = ' + str(Temp_sl) +'-' +str(self.trades.__len__()))
              self.stop_price_short = Temp_sl
              self.sell(size = math.floor(float(Unit))*self.backtestInfo.dollar_per_point) 
              self.backtestInfo.save_action(str(date),'buy',self.trades.__len__(),close,self.stop_price_short,'short')
              return     

#唐西奇回測
def go_DONCH_test(number,money,q):
  if type(number) != str:
    return False
  if type(money) != int:
    return False
  target_stock = number
  account_money = money
  df = getStockInfo(target_stock)#pandas讀取資料，並將第1欄作為索引欄
  if df.empty: return False
  test = Backtest(df, DONCHCross, cash=account_money, commission=.004)
  #指定回測程式為test，在Backtest函數中依序放入(資料來源、策略、現金、手續費)

  result = test.run()
  #執行回測程式並存到result中

  print(result) #直接print文字結果

  test.plot(filename=server_filePath+"/server/templates" + '/' + target_stock + '.html',open_browser=False)
  f = open(server_filePath+"/server/templates" + '/' + target_stock + '.html','r')
  q.put(result)
  q.put(use_BacktestInfo.tomorrow_action)
  q.put(f.read())
  return True

#讀取
def getStockInfo(stock):
        target_stock = stock
        #filename = server.server_filePath + '/server/TempData/' + target_stock + '.csv'
        #if os.path.isfile(filename) == True:
        try:
            #df = pd.read_csv(server.server_filePath + '/server/TempData/' + target_stock + '.csv', index_col=0) #pandas讀取資料，並將第1欄作為索引欄
            df = StockModel.readStockDay(target_stock)
            try:#SQL有資料要看是否最新
                df[datetime.today()]
                mask = df.index >= use_BacktestInfo.start_day
                result = df[mask]
                result = result.dropna(axis = 0,how = 'any')
                return result
            except:#SQL有資料但不是最新刪除整張表
                StockModel.deleteStockDayTable(target_stock)
                print("SQL Table is not newer:" + str(target_stock))
        except:
          print("SQL No Table:" + str(target_stock))
        #SQL沒資料抓取一整包
        yf.pdr_override()
        start_date = datetime(2005,1,1)
        end_date = datetime.today()#設定資料起訖日期
        df = data.get_data_yahoo([target_stock], start_date, end_date,index_col=0)
        if df.empty:
          print("yahoo no data:" + str(target_stock))
          return df
        StockModel.saveStockDay(target_stock,df)
        #df.to_csv(filename)
        mask = df.index >= use_BacktestInfo.start_day
        result = df[mask]
        result = result.dropna(axis = 0,how = 'any')
        print("SQL Table update sussese:" + str(target_stock))
        return result

#存進去sql
