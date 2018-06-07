PORT = 3080
import socketserver
import socketio
from aiohttp import web
# class MyTCPHandler(socketserver.BaseRequestHandler):
#     """
#     The request handler class for our server.
#
#     It is instantiated once per connection to the server, and must
#     override the handle() method to implement communication to the
#     client.
#     """
#
#     def handle(self):
#         # self.request is the TCP socket connected to the client
#         self.data = self.request.recv(1024).strip()
#         print("{} wrote:".format(self.client_address[0]))
#         print(self.data)
#         # just send back the same data, but upper-cased
#         self.request.sendall("connect".encode("utf-8"))
#
#
# with socketserver.TCPServer(("localhost", PORT), MyTCPHandler) as server:
#     server.serve_forever()


sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)

@sio.on('connect')
def connect(sid, environ):
    print('connect', sid)

@sio.on("Vote")
def vote(sid, data):
    print("sid:{}, data:{}".format(sid, data))
    return "OK", 123

web.run_app(app)
print("hello world")