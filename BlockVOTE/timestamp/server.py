import socketserver
from socketserver import BaseRequestHandler as BRH
import datetime
from BlockVOTE.P2P.timeaddr import TIMESTAMP_SERVER_ADDR

class MyTCPHandler(BRH):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    def handle(self):
        # self.request is the TCP socket connected to the client
        while 1:
            try:
                data = self.request.recv(1024).strip()
            except:
                self.request.close()
            if not data:
                break
            else:
                print("{} request {}".format(str(self.request.getpeername()), str(data, encoding='utf-8')))
                ts = bytes(str(datetime.datetime.now().timestamp()), encoding='utf-8')
                self.request.sendall(ts)


if __name__ == "__main__":
    HOST, PORT = TIMESTAMP_SERVER_ADDR
    # Create the server, binding to localhost on port 9999
    server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.handle_request()
    server.serve_forever()