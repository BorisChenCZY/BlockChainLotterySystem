from BlockVOTE.Miner import Miner
from BlockVOTE.P2P.Node import BQUEUE
if __name__ == '__main__':
    addr = ("localhost", 2222)
    miner = Miner.instance(addr, "new", 0)
    miner.block_recv(BQUEUE)