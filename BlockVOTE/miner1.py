from BlockVOTE.Miner import Miner
from BlockVOTE.P2P.Node import BQUEUE
from BlockVOTE.VoteInfo import VoteInfo
import datetime
if __name__ == '__main__':
<<<<<<< HEAD
    addr = ("10.20.126.89", 3000)
=======
    addr = ("10.20.7.144",3001)
>>>>>>> master
    miner = Miner.instance(addr, "zsq1", 0)
    # voteInfo = VoteInfo(datetime.datetime.now().timestamp(), b'target', b'pubkey', (2, [3]), b'sign')
    # miner.add_vote(bytes(voteInfo))
    # block = miner.pack_block()
    # voteInfo = VoteInfo(datetime.datetime.now().timestamp(), b'target', b'pubkey', (3, [3]), b'sign')
    # miner.add_vote(bytes(voteInfo))
    # block = miner.pack_block()
    # voteInfo = VoteInfo(datetime.datetime.now().timestamp(), b'target', b'pubkey', (4, [1]), b'sign')
    # miner.add_vote(bytes(voteInfo))
    # block = miner.pack_block()
    # miner.votereceiver()


