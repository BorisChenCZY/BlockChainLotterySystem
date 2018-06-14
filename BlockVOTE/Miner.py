from BlockVOTE.Chain import *
import datetime
import sqlite3
import socketserver
import asyncio
import socketio
import json
import threading
import multiprocessing
from BlockVOTE.Chain import Chain, get_timestamp
from BlockVOTE.P2P.timeaddr import TIMESTAMP_SERVER_ADDR
from BlockVOTE.P2P import Node
from BlockVOTE.P2P.SocketUtil import SocketUtil
import BlockVOTE.P2P.settings as config
from BlockVOTE.P2P.Node import BQUEUE,VQUEUE,TQUEUE
from aiohttp import web
from RSA import *
import queue

from BlockVOTE.VoteBlock import VoteBlock
from BlockVOTE.VoteInfo import VoteInfo

MINOR_DB = "Miner.sqlite"
MINOR_TABLE_OFF = "Miner"
VOTES_IN_A_BLOCK = 10
QUEUE = queue.Queue()
CQUEUE = queue.Queue()

class MinerError(Exception):
    pass



class Miner:
    __chain = None
    _instance_lock = threading.Lock()
    __sio = None
    __cnt = 0

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
        self.__chain = Chain(self.__chain_name)
        if t == 0:
            self.__load_chain()
        else:
            self.__chain.create()
        self.addr = addr
        # miner server
        self.node = Node.Node(self.addr)
        self.server = threading.Thread(target=self.node.serving)
        self.server.start()
        # update current chain
        self.update_chain()
        # IPC
        self.queueinfo = threading.Thread(target=self.get_queue_info)
        self.queueinfo.start()
        # 若当前miner为config中的第一个miner那么让他持有token
        if self.addr == config.CONNECTION_LIST[0]:
            self.token = 0
            self.start_time = SocketUtil.get_time_stamp(TIMESTAMP_SERVER_ADDR)
        else:
            self.token = -1
            self.start_time = SocketUtil.get_time_stamp(TIMESTAMP_SERVER_ADDR)

        # http server
        self.votereceiver()



    def get_queue_info(self):
        while 1:
            self.queue_recv(BQUEUE)
            self.queue_recv(VQUEUE)
            self.queue_recv(TQUEUE)

    def votereceiver(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
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
            print(d)
            # ----------------- new information
            msg = d['msg']
            sig = d['sign']
            key_info = d['pubkey']
            target = msg['target']
            prob_num = msg['prob_num']
            selection = msg['selection']
            # print(msg, sign, pubkey)


            # ----------------- new information
            # data = d["data"]
            # sig = d["sign"]
            # key_info = data['pubkey']
            # target = data['target']
            # prob_num = data['prob_num']
            # selection = data['selection']

            key_info = key_info.encode("utf-8")

            vote = "{}:{}".format(prob_num,selection)

            voteInfo = VoteInfo(get_timestamp(), target=target.encode("utf-8"), pubkey=key_info,
                                vote=(prob_num, selection), sign=sig.encode("utf-8"))

            now = self.get_timestamp()
            # broadcast to other miner
            header = bytes('<send vote><{}>'.format(self.addr),encoding='utf-8')
            msg = header + bytes(voteInfo)
            SocketUtil.broadcast(config.CONNECTION_LIST, msg, self.addr)
            self.__chain.add_vote(voteInfo, -1)

            # 生成block需要先获得token，两种情况下都可以打包block：
            # 1.将指定时间内vote池中的所有vote加入block中
            # 2.当前接收到五个voteinfo自动打包
            print(self.token, self.__cnt)
            self.pass_token()
            return "OK", 123


        web.run_app(app, port=8080)

    def pass_token(self):
        if self.token >= 0:
            self.__cnt += 1
            cur_time = SocketUtil.get_time_stamp(TIMESTAMP_SERVER_ADDR)
            delta = datetime.datetime.fromtimestamp(cur_time) - datetime.datetime.fromtimestamp(self.start_time)
            delta = delta.seconds
            if self.__cnt >= 5 or delta > 10:
                self.__cnt = 0
                print("auto packing...")
                blk = self.pack_block()
                # broadcast block to other miner
                info = bytes('<send block><{}>'.format(str(self.addr)), encoding='utf-8') + bytes(blk)
                print("broadcast new generated block {} ".format(blk.get_id()))
                SocketUtil.broadcast(config.CONNECTION_LIST, info, self.addr)
                # 将token加一交给config中的下一个人
                cur_token = self.token
                if SocketUtil.token_send(self.addr, cur_token):
                    # 如果成功交出token
                    self.token = -1

    @classmethod
    def instance(cls, addr, chain, t):
        with Miner._instance_lock:
            if not hasattr(Miner, "_instance"):
                Miner._instance = Miner(addr, chain, t)
        return Miner._instance

    def __load_chain(self):
        # todo load chain
        self.__chain.load()
        pass

    def queue_recv(self, queue):
        while not queue.empty():
            item = queue.get()
            # 判断拿出的元素时block还是vote
            # 新miner更新自己的block
            if isinstance(item[0],VoteBlock):
                self.add_block(bytes(item[0]),item[1])
                print("block added")
            # 从其他miner那里拿到的vote
            elif isinstance(item[0],VoteInfo):
                if self.__chain.duplicate_vote(item[0]):
                    print("vote existed")
                else:
                    self.add_vote(bytes(item[0]))
                    print("vote added")
                    self.pass_token()
            # 从其他miner传过来的token
            elif isinstance(item[0],int):
                print("received token: ", item[0])
                self.token = item[0]
                self.start_time = SocketUtil.get_time_stamp(TIMESTAMP_SERVER_ADDR)
            queue.task_done()


    def update_chain(self):
        lastid = self.__chain.get_last_block()[0]
        blocks = self.__chain.get_chain(0)
        QUEUE.put((self.addr, lastid))
        CQUEUE.put((self.addr, blocks))
        # broadcast for chain info
        print('max id', self.__chain.get_last_block()[0])
        print("initial broadcasting...")
        msg = bytes('<request chain><{}><{}>'.format(str(self.addr),lastid), encoding='utf-8')
        SocketUtil.broadcast(config.CONNECTION_LIST, msg, self.addr)
        print("broadcast done")

    def add_block(self, block, localmachine):
        if type(block) is not bytes:
            raise MinerError("block must be bytes, but not {}".format(type(block)))
        block = VoteBlock.load(block)
        if not block.check():
            raise MinerError("Block not valid")
        voteInfos = block.get_vote_infos()
        for voteInfo in voteInfos:
            self.__chain.remove_vote(voteInfo)
        self.__chain.add_block(block, localmachine)


    # this function should not belong here
    def add_vote(self, voteInfo):
        if type(voteInfo) is not bytes:
            raise MinerError("voteInfo must be bytes, but not {}".format(type(voteInfo)))
        voteInfo = VoteInfo.load(voteInfo)
        self.__chain.add_vote(voteInfo, -1)

    # todo
    def check_vote(self, voteInfo):
        pass

    # todo
    def check_block(self, blockInfo):
        pass

    def pack_block(self):
        lid, lhash, lprehash = self.__chain.get_last_block()
        voteBlock = VoteBlock(lid + 1, lhash.encode("utf-8"))

        votes = self.__chain.get_uncomfirmed_votes()
        pack = votes[:VOTES_IN_A_BLOCK]
        if(len(pack) == 0):
            return None

        for voteInfo in pack:
            voteBlock.add_info(voteInfo)
            self.__chain.remove_vote(voteInfo)

        voteBlock.close()
        self.__chain.add_block(voteBlock,self.addr)
        return voteBlock

    def get_timestamp(self):
        timestamp = SocketUtil.get_time_stamp(TIMESTAMP_SERVER_ADDR)
        return timestamp

