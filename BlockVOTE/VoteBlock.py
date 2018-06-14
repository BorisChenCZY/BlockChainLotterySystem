from Block import *
from BlockVOTE.VoteInfo import *
import re
class VoteBlockError(Exception):
    pass

class VoteBlock(Block):


    def __init__(self, id=None, prehash=None, hash=None):
        super().__init__(id, prehash, hash)
        self.__vote_infos = []
        self.__infov = b""
        # __vote_infos = []

    def add_info(self, voteInfo):
        if(type(voteInfo) != VoteInfo):
            raise VoteInfoError("voteInfo must be VoteInfo object")
        if(len(self.__infov) + len(bytes(voteInfo)) > 1024*1024):
            return False
        self.__infov += b"^" + bytes(voteInfo)
        self.__vote_infos.append(voteInfo)
        super(VoteBlock, self).set_info(self.__infov)

    def get_vote_infos(self):
        return self.__vote_infos

    def close(self):
        super(VoteBlock, self).close()
        
    def check(self):
        for voteInfo in self.__vote_infos:
            voteInfo.check()
        return True

    @staticmethod
    def load(block):
        if(type(block) != bytes):
            raise BlockInfoError("block must be bytes")
        components = block.split(b"//")


        id = int.from_bytes(components[0], byteorder='little')
        prehash = components[1]
        hash = components[2]
        info = components[3]
        voteInfos = info.split(b"^")

        voteBlock = VoteBlock(id, prehash, hash)

        for vote in voteInfos:
            if vote == b'':
                continue
            voteInfo = VoteInfo.load(vote)
            voteBlock.add_info(voteInfo)
        if not voteBlock.check():
            raise BlockInfoError("Block not valid!")
        return voteBlock



if __name__ == "__main__":

    timestamp = datetime.datetime.now().timestamp() # current time
    pubkey = b'pubkey'
    target = b'target'
    sign = b'sign'
    vote = (1, [1, 2, 3])
    voteInfo = VoteInfo(timestamp = datetime.datetime.now().timestamp(), target = target, pubkey=pubkey, vote=vote, sign=sign)

    voteBlock = VoteBlock(id=1, prehash=b'prehash', hash=b'hash')
    voteBlock.add_info(voteInfo)
    voteBlock.close()


    print(voteBlock.get_hash())

    timestamp = datetime.datetime.now().timestamp()  # current time
    pubkey = b'pubkey'
    target = b'target'
    sign = b'sign'
    vote = (1, [1, 2, 3])
    voteInfo = VoteInfo(timestamp=datetime.datetime.now().timestamp(), target=target, pubkey=pubkey, vote=vote,
                        sign=sign)

    voteBlock = VoteBlock(id=1, prehash=b'prehash', hash=b'hash')
    voteBlock.add_info(voteInfo)
    voteBlock.close()
    print(voteBlock.get_hash())

    # bs = bytes(voteBlock)
    # voteBlock1 = VoteBlock.load(bs)
    # print(voteBlock1.check())

