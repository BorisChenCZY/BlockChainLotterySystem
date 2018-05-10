import threading
import P2P.Node as node
import time
import P2P.SocketUtil as util
if __name__ == "__main__":
    addr = ("localhost", 3333)
    a = node.Node(addr)
    t1 = threading.Thread(target=a.serving)
    t1.start()
    for i in range(3):
        print("-----------------------------")
        msg = bytes(str(i) + '+3333', encoding='utf-8')
        util.SocketUtil.send(msg, ("localhost", 9999))
        time.sleep(5)