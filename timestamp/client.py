import socket
import time
import P2P.SocketUtil as util

if __name__ == "__main__":
    addr = ("localhost", 9999)
    i = 0
    while i<10:
        timestamp = util.SocketUtil.request_time_stamp(addr)
        time.sleep(5)
        i+=1



