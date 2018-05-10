import socketserver
from socketserver import BaseRequestHandler as BRH
from P2P.SocketUtil import SocketUtil
import P2P.NetworkException as exception
import socket
import P2P.settings as config

DATA = set()

class MyTCPHandler(BRH):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """


    def handle(self):
        global DATA
        # self.request is the TCP socket connected to the client
        while 1:
            try:
                data = self.request.recv(1024).strip()
                print(data)
            except:
                self.request.close()
            if not data:
                break
            if data not in DATA:
                DATA.add(data)
                SocketUtil.broadcast(data, config.CONNECTION_LIST)


class Node:


    def __init__(self, addr):
        self.addr = addr
        config.CONNECTION_LIST.remove(self.addr)


    def serving(self):
        server = socketserver.TCPServer(self.addr, MyTCPHandler)
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.handle_request()
        server.serve_forever()





