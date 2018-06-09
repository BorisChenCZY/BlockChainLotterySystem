from BlockVOTE.Chain import *
import datetime
import sqlite3
import socketserver
import socketio
import json
import threading
from BlockVOTE.P2P import Node
from BlockVOTE.P2P.SocketUtil import SocketUtil
import BlockVOTE.P2P.settings as config
from aiohttp import web
from RSA import *
import queue
MINOR_DB = "Miner.sqlite"
MINOR_TABLE_OFF = "Miner"
VOTES_IN_A_BLOCK = 10
QUEUE = queue.Queue()
CQUEUE = queue.Queue()

class MinerError(Exception):
    pass

class Miner:
    __sio = None
    __cnt = 0
    _instance_lock = threading.Lock()


    def __init__(self, addr, chainname, t):
        """
        :str chain: the name of the chain
        :int t: type of the chain. If the chain already exists, set t = 0,
                otherwise set t = 1
        """
        if type(chainname) != str:
            raise MinerError("chain must be str, but not {}".format(type(chain)))
        if type(t) != int:
            raise MinerError("type must be int, but not {}".format(type(t)))
        self.__chain_name = chainname
        self.chain = Chain(self.__chain_name)
        if t == 0:
            self.__load_chain()
        else:
            self.chain.create()

        self.addr = addr
        self.node = Node.Node(self.addr)
        self.server = threading.Thread(target=self.node.serving)
        self.server.start()
        self.update_chain()
        self.__sio = socketio.AsyncServer()
        app = web.Application()
        self.__sio.attach(app)


        @self.__sio.on('connect')
        def connect(sid, environ):
            print('connect', sid)

        @self.__sio.on("Vote")
        def vote(sid, data):
            d = json.loads(data)
            # 对接收到的信息中的投票平台公钥是否在自己公钥池中，在就直接解密，然后得到用户投票信息和用户公钥；
            data = d["data"]
            sig = d["sign"]
            key_info = data['pubkey']
            target = data['target']
            prob_num = data['prob_num']
            selection = data['selection']


            key_info = key_info.encode("utf-8")

            vote = "{}:{}".format(data['prob_num'], data['selection'])

            voteInfo = VoteInfo(get_timestamp(), target=target.encode("utf-8"), pubkey=key_info, vote=(prob_num, selection), sign = sig.encode("utf-8"))
            self.__chain.add_vote(voteInfo)
            self.__cnt += 1
            if self.__cnt >= 5:
                self.__cnt = 0
                self.pack_block()
            self.block_recv(BQUEUE)
            return "OK", 123

        web.run_app(app, port=addr[1])

        # update current chain

    @classmethod
    def instance(cls, addr, chain, t):
        with Miner._instance_lock:
            if not hasattr(Miner, "_instance"):
                Miner._instance = Miner(addr, chain, t)
        return Miner._instance

    def __load_chain(self):
        # todo load chain
        self.chain.load()
        pass

    def block_recv(self, queue):
        while not queue.empty():
            block = queue.get()
            self.chain.add_block(block)
            print("adding sucess")
            queue.task_done()

    def update_chain(self):

        lastid = self.chain.get_last_block()[0]
        blocks = self.chain.get_chain(0)
        QUEUE.put((self.addr, lastid))
        CQUEUE.put((self.addr, blocks))
        # broadcast for chain info
        print('max id', self.chain.get_last_block()[0])
        print("initial broadcasting...")
        msg = bytes('<request chain><{}><{}>'.format(str(self.addr),lastid), encoding='utf-8')
        SocketUtil.broadcast(msg, config.CONNECTION_LIST)

    def add_block(self, block):
        if type(block) is not bytes:
            raise MinerError("block must be bytes, but not {}".format(type(block)))
        block = VoteBlock.load(block)
        if not block.check():
            raise MinerError("Block not valid")
        self.chain.add_block(block)

    # this function should not belong here
    def add_vote(self, voteInfo):
        if type(voteInfo) is not bytes:
            raise MinerError("voteInfo must be bytes, but not {}".format(type(voteInfo)))
        voteInfo = VoteInfo.load(voteInfo)
        self.chain.add_vote(voteInfo, -1)

    def check_vote(self, voteInfo):
        pass

    def check_block(self, blockInfo):
        pass

    def pack_block(self):
        lid, lhash, lprehash = self.chain.get_last_block()
        voteBlock = VoteBlock(lid + 1, lhash.encode("utf-8"))

        votes = self.chain.get_uncomfirmed_votes()
        pack = votes[:VOTES_IN_A_BLOCK]
        if(len(pack) == 0):
            return None

        for voteInfo in pack:
            voteBlock.add_info(voteInfo)
            self.chain.remove_vote(voteInfo)

        voteBlock.close()
        self.chain.add_block(voteBlock)
        return voteBlock

    def get_timestamp(self):
        #todo zhang
        pass


