from Chain import *
import datetime
import sqlite3

MINOR_DB = "Miner.sqlite"
MINOR_TABLE_OFF = "Miner"
VOTES_IN_A_BLOCK = 10

class MinerError(Exception):
    pass

class Miner:
    __chain = None
    def __init__(self, chain, t):
        """
        :str chain: the name of the chain
        :int t: type of the chain. If the chain already exists, set t = 0,
                otherwise set t = 1
        """
        if type(chain) != str:
            raise MinerError("chain must be str, but not {}".format(type(chain)))
        if type(t) != int:
            raise MinerError("type must be int, but not {}".format(type(t)))
        self.__chain = Chain(chain)

        if t == 0:
            self.__load_chain()
        else:
            self.__chain.create()

    def __load_chain(self):
        # todo load chain
        self.__chain.load()
        pass

    def add_block(self, block):
        if type(block) is not bytes:
            raise MinerError("block must be bytes, but not {}".format(type(block)))
        block = VoteBlock.load(block)
        if not block.check():
            raise MinerError("Block not valid")
        self.__chain.add_block(block)

    # this function should not belong here
    def add_vote(self, voteInfo):
        if type(voteInfo) is not bytes:
            raise MinerError("voteInfo must be bytes, but not {}".format(type(voteInfo)))
        voteInfo = VoteInfo.load(voteInfo)
        self.__chain.add_vote(voteInfo, -1)

    def check_vote(self, voteInfo):
        pass

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
        self.__chain.add_block(voteBlock)
        return voteBlock


if __name__ == '__main__':
    miner = Miner("test", 0)
    # voteInfo = VoteInfo(datetime.datetime.now().timestamp(), b'target', b'pubkey', (2, [3]), b'sign')
    # miner.add_vote(bytes(voteInfo))
    # voteInfo = VoteInfo(datetime.datetime.now().timestamp(), b'target', b'pubkey', (3, [3]), b'sign')
    # miner.add_vote(bytes(voteInfo))
    # voteInfo = VoteInfo(datetime.datetime.now().timestamp(), b'target', b'pubkey', (4, [1]), b'sign')
    # miner.add_vote(bytes(voteInfo))
    block = miner.pack_block()
    # bytes(block)
