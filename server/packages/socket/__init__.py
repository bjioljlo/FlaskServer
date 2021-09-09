import socket
import threading

class SocketServer():
    def __init__(self,Host,Port,callback=None):
        self.Host = Host
        self.Port = Port
        self.callback = callback
    def Run(self):
        self.temp_threading = threading.Thread(target=SocketRun,args=[self.Host,self.Port,self.callback])
        self.temp_threading.start()
    def Stop(self):
        self.temp_threading.join(0.1)


def SocketRun(HOST,PORT,callback = None):
    print('server start at: %s:%s' % (HOST, PORT))
    print('wait for connection...')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(5)
    while True:
        conn,addr = s.accept()
        print('connected by ' + str(addr))
        while True:
            indata = conn.recv(1024)
            if len(indata) == 0: # connection closed
                conn.close()
                print('client closed connection.')
                break
            print('recv: ' + indata.decode())
            outdata = 'echo ' + indata.decode()
            callback(indata.decode())
            conn.send(outdata.encode())