import socketserver
from socketserver import BaseRequestHandler as BRH
from BlockVOTE.P2P.SocketUtil import SocketUtil
from BlockVOTE.Chain import Chain
from BlockVOTE.VoteBlock import VoteBlock
from BlockVOTE.VoteInfo import VoteInfo
import BlockVOTE.P2P.NetworkException as exception
import threading
from multiprocessing import Process
import socket
import re
import BlockVOTE.P2P.settings as config
import queue

BQUEUE = queue.Queue()
VQUEUE = queue.Queue()
# TQUEUE = queue.Queue()
DATA = set()
BLOCK = set()
VOTE = set()

def decode_addr(string):
    s = re.findall(r'[^(,)]+', string)
    s[0] = s[0].lstrip("'")
    s[0] = s[0].rstrip("'")
    return s[0], int(s[1])

def _queue_conn(queue):
    lst = []
    while not queue.empty():
        lst.append(queue.get())
        queue.task_done()
    return lst



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
                data = self.request.recv(4096).strip()
            except:
                self.request.close()

            if not data:
                break
            else:
                print("receive: ", data)
                from BlockVOTE.Miner import QUEUE,CQUEUE
                # data format: <msg type><msg sender><msg content>
                decod = re.findall(r'[^<>]+', data.decode('utf-8'))
                if data not in DATA:
                    DATA.add(data)
                    if decod[0] == 'request chain':
                        mylst = _queue_conn(QUEUE)
                        for ouraddr, ourlst in mylst:
                            lst = int(decod[2])
                            addr = decode_addr(decod[1])
                            if ourlst <= lst:
                                info = bytes('<send block><{}>'.format(ouraddr), encoding='utf-8')
                                print(info)
                                SocketUtil.send(info, addr)
                            else:
                                for ouraddr, chain_info in _queue_conn(CQUEUE):
                                    chain_info = chain_info[lst:]
                                    # send each block in chain
                                    print("sending chain...")
                                    for block in chain_info:
                                        a = bytes(block)
                                        info = bytes('<send block><{}>'.format(str(self.request.getsockname())), encoding='utf-8') + a
                                        print("block id ",block.get_id())
                                        SocketUtil.send(info, addr)

                    elif decod[0] == 'send block':
                        addr = decode_addr(decod[1])
                        if len(decod)>2:
                            abte = bytes(decod[2],encoding='utf-8')
                            block = VoteBlock.load(abte)
                            print("adding block...")
                            if block.get_hash() not in BLOCK:
                                BLOCK.add(block.get_hash())
                                BQUEUE.put(block)
                                info = bytes('<receive block><{}><{}>'.format(str(self.request.getsockname()),str(block.get_id())),encoding='utf-8')
                                SocketUtil.send(info, addr)
                            else:
                                info = bytes('<receive block><{}><{}>'.format(str(self.request.getsockname()), str(-1)),encoding='utf-8')
                                SocketUtil.send(info, addr)
                        else:
                            print("sender is out of date")

                    elif decod[0] == 'send vote':
                        addr = decode_addr(decod[1])
                        abte = bytes(decod[2], encoding='utf-8')
                        vote = VoteInfo.load(abte)
                        print("adding vote...")
                        if vote.get_info() not in VOTE:
                            VOTE.add(vote.get_info())
                            VQUEUE.put(vote)
                            info = bytes('<receive vote><{}><{}>'.format(str(self.request.getsockname()), str(vote.get_info())), encoding='utf-8')
                            SocketUtil.send(info, addr)
                        else:
                            info = bytes('<receive vote><{}><{}>'.format(str(self.request.getsockname()), str(-1)),
                                         encoding='utf-8')
                            SocketUtil.send(info, addr)

                    elif decod[0] == 'receive block':
                        print(decod)
                        if decod[2] == '-1':
                            print('{} already has this block'.format(decod[1]))
                        else:
                            print('{} receive block{} from {}'.format(decod[1],decod[2],str(self.request.getsockname())))

                    elif decod[0] == 'receive vote':
                        print(decod)
                        if decod[2] == '-1':
                            print('{} already has this vote'.format(decod[1]))
                        else:
                            print('{} receive vote{} from {}'.format(decod[1],decod[2],str(self.request.getsockname())))

                    # elif decod[0] == 'timestamp':
                    #     print('timestamp is ',decod[2])
                    #     TQUEUE.put(decod[2])


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





