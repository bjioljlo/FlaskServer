from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import redis
import yaml
import os
from yaml.loader import SafeLoader

server_filePath = os.getcwd()#取得目錄路徑
server_flask = Flask(__name__)#初始化server
#取得config
def get_config():
    with open(server_filePath + '/server/config/config.yaml','r') as f:
        data = yaml.load(f,Loader=SafeLoader)
        return data
config_data = get_config()
#連線redis DB
DB_redis = redis.Redis(host=config_data['ResisDB']['IP'],port=config_data['ResisDB']['Port'],decode_responses=True,db=config_data['ResisDB']['DB'])  
#設定mysql DB
server_flask.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
server_flask.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://" + config_data['MysqlDB']['User'] + ":" + config_data['MysqlDB']['Password'] + "@" + config_data['MysqlDB']['IP'] + ":"+ str(config_data['MysqlDB']['Port']) +"/"+config_data['MysqlDB']['DB']
server_flask.config['SQLALCHEMY_POOL_RECYCLE'] = 3600
#連線mysql DB
DB_mysql = SQLAlchemy(server_flask)
#Golang server url
Server_Golang = 'http://'+ config_data['GolangServer']['IP']+':'+ str(config_data['GolangServer']['Port'])
#註冊網址RESTful
from server.router import Router
Router.RegisterRouters()
#開啟socket
from server.packages import socket
from server.controllers import StockController
Server_Socket = socket.SocketServer(config_data["FlaskServer"]["SocketHost"],config_data["FlaskServer"]["SocketPort"],StockController.reciveMsg)
Server_Socket.Run()






