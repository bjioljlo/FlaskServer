import pandas as pd
from server import DB_mysql, DB_redis

class StockDayInfo(DB_mysql.Model):
    __tablename__ = ""
    Date = DB_mysql.Column(DB_mysql.DateTime, primary_key=True)
    Open = DB_mysql.Column(DB_mysql.Float)
    High = DB_mysql.Column(DB_mysql.Float)
    Low = DB_mysql.Column(DB_mysql.Float)
    Close = DB_mysql.Column(DB_mysql.Float)
    AdjClose = DB_mysql.Column(DB_mysql.Float)
    Volume = DB_mysql.Column(DB_mysql.Integer)
    def __init__(self,name,Date,Open,High,Low,Close,AdjClose,Volume):
        self.__tablename__ = name
        self.Date = Date
        self.Open = Open
        self.High = High
        self.Low = Low
        self.Close = Close
        self.AdjClose = AdjClose
        self.Volume = Volume

def addStockDayInfo(stockInfo):
    tableee = stockInfo.__table__
    tableee.name = stockInfo.__tablename__
    stockInfo.__table__ = tableee
    DB_mysql.session.add(stockInfo)
    DB_mysql.session.commit()

def createStockDayTable(stockInfo):
    temp_table = stockInfo.__table__
    temp_table.name = stockInfo.__tablename__
    stockInfo.__table__ = temp_table
    stockInfo.__table__.create(DB_mysql.session.bind)

def deleteStockDayTable(name):
    temp_table = StockDayInfo.__table__
    temp_table.name = name
    StockDayInfo.__table__ = temp_table
    StockDayInfo.__table__.drop(DB_mysql.session.bind)

def saveStockDay(name,data):
    data.to_sql(name=name,con=DB_mysql.engine)

def readStockDay(name):
    dataframe = pd.DataFrame()
    try:
        dataframe = pd.read_sql(sql = name,con=DB_mysql.engine,index_col='Date')
        return dataframe
    except Exception as e:
        print('SQL Error {}'.format(e.args))
       

class StockBackInfo():
    def __init__(self,name):
        self.name = name
        try:
            Temp = DB_redis.lrange(str(name),0,-1)
            self.action = Temp[0]
            self.result = Temp[1]
            self.inDB = True
        except:
            self.inDB = False

def getStockInfo(name):
    data = StockBackInfo(name)
    return data

def addStockInfo(name,*data):
    DB_redis.lpush(str(name),*data)

def deletStockInfo(name):
    DB_redis.delete(str(name))

def setSearchHistory(name):
    try:
        DB_redis.lrem("SearchHistory",0,str(name))
    except:
        pass
    DB_redis.lpush("SearchHistory",str(name))
    DB_redis.ltrim("SearchHistory",0,4)