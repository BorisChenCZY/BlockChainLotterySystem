import socketserver
from socketserver import BaseRequestHandler as BRH
import time

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
            print( "{} wrote:".format(self.client_address[0]))
            print(data)
            # just send back the same data, but upper-cased
            self.request.sendall(bytes(str(time.time()),encoding='utf-8'))


if __name__ == "__main__":
    HOST, PORT = "localhost", 9999
    # Create the server, binding to localhost on port 9999
    server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.handle_request()
    server.serve_forever()