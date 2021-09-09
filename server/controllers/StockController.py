import json
from queue import Queue
import threading
from server import Server_Golang
from flask import redirect,render_template
from pandas.core.frame import DataFrame
from datetime import datetime
from server.controllers import BacktestStrategy
from server.models import StockModel

def to_dict(result):
    temp_dic = dict()
    for ind,value in enumerate(result):
        if type(value) == DataFrame:
            #temp_dic[str(result.index[ind])] = value.to_json()
            continue
        temp_dic[str(result.index[ind])] = str(value)
    return temp_dic

#顯示在templates中的網頁
def show_HTML(name):
    return render_template(name)

#跑回側
def run_test(number,money):
    
    try:
        temp_data = StockModel.getStockInfo(number)
        result = json.loads(temp_data.result)
        data_date = datetime.strptime(result["End"],"%Y-%m-%d %H:%M:%S")
        today = datetime.today().date()
        data_date = data_date.date()
        if data_date == today:
            return redirect(Server_Golang +'/stock?stock=' + number)
    except:
        pass
    
    StockModel.deletStockInfo(number)
    q = Queue()
    temp_thread = threading.Thread(target=BacktestStrategy.go_DONCH_test,args=[number,money,q])
    temp_thread.start()
    temp_thread.join()
    if q.empty():
        return redirect(Server_Golang  +'/index')
    StockModel.setSearchHistory(number)
    result = q.get()
    action = q.get()
    html = q.get()
    result = json.dumps(to_dict(result))
    action = json.dumps(action)
    StockModel.addStockInfo(number,html,result,action)
    return redirect(Server_Golang  +'/stock?stock=' + number)


def reciveMsg(indata):
    result = json.loads(indata)
    if result["firstNum"] == 1:
        if result["secondNum"] == 1:
            run_test(result["msg"],500000)