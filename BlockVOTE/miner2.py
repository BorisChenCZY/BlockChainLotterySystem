from BlockVOTE.Miner import Miner
from BlockVOTE.P2P.Node import BQUEUE
if __name__ == '__main__':
    addr = ("10.20.7.144", 3001)
    miner = Miner.instance(addr, "", 0)
    miner.queue_recv(BQUEUE)