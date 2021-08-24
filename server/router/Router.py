from server.controllers import StockController
from server import server_flask
from server.models import StockModel

def RegisterRouters():
    @server_flask.route('/')
    def hello():
        return StockController.show_HTML('index.html')
            
    @server_flask.route('/add/num1=<num1>&num2=<num2>', methods=['GET'])
    def add(num1,num2):
        print(num1 + num2)
        return str(int(num1) + int(num2))

    @server_flask.route('/stock/num1=<num1>&num2=<num2>',methods=['GET'])
    def stock(num1,num2):
        return StockController.run_test(str(num1),int(num2))