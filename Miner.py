from Chain import *
import sqlite3

MINOR_DB = "Miner.sqlite"
MINOR_TABLE_OFF = "Miner"

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
            raise MinerError("block must by bytes, but not {}".format(type(block)))
        block = VoteBlock.load(block)
        if not block.check():
            raise MinerError("Block not valid")
        self.__chain.add_block(block)

    # this function should not belong here
    def add_vote(self, voteInfo):
        if type(voteInfo) is not VoteInfo:
            raise MinerError("voteInfo must be VoteInfo, but not {}".format(type(voteInfo)))
        pass
