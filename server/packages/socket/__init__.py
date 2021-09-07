import socket

def Run(HOST,PORT,callback = None):
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
            callback(indata.decode(),500000)
            conn.send(outdata.encode())