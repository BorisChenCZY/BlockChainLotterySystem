import socket
import BlockVOTE.P2P.settings as config
import P2P.NetworkException as exception
import traceback

class SocketUtil(object):

    # _instance_lock = threading.Lock()

    # def __init__(self):
    #     pass
    #
    # def __new__(cls, *args, **kwargs):
    #     if not hasattr(SocketUtil, "_instance"):
    #         with SocketUtil._instance_lock:
    #             if not hasattr(SocketUtil, "_instance"):
    #                 SocketUtil._instance = object.__new__(cls)
    #     return SocketUtil._instance

    @staticmethod
    def get_time_stamp(addr):
        if type(addr[0]) != str or type(addr[1]) != int:
            raise exception.FormatException()
        # Create a socket (SOCK_STREAM means a TCP socket)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # Connect to server and send data
            sock.connect(addr)
            sock.sendall(b'timestamp')
            # Receive data from the server and shut down
            received = sock.recv(1024).decode()
            print("Received: {}".format(received))
        finally:
            sock.close()
        return float(received)


    @staticmethod
    def send( msg, target):
        if type(msg) != bytes:
            raise exception.FormatException
        if type(target[0]) != str or type(target[1]) != int:
            raise exception.FormatException()
        # Create a socket (SOCK_STREAM means a TCP socket)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # Connect to server and send data
            sock.connect(target)
            print("connected to {}".format(target))
            sock.sendall(msg)
            print("initial request sent")
        except:
            sock.close()
        sock.close()
        return True

    @staticmethod
    def token_send(addr, token):
        if type(token) != int:
            raise exception.FormatException
        if type(addr[0]) != str or type(addr[1]) != int:
            raise exception.FormatException()
        # 对config列表内的miner尝试链接，成功则交出对应的id的token
        cur_token = token

        while 1:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            cur_token += 1
            token_holder = config.CONNECTION_LIST[cur_token % len(config.CONNECTION_LIST)]
            try:
                # Connect to server and send data
                sock.connect(token_holder)
                msg = bytes("<token><{}><{}>".format(addr, cur_token), encoding='utf-8')
                sock.sendall(msg)
                tag = True
            except:
                if token_holder == addr:
                    return False
                print("fail to give token {} to {}".format(cur_token, token_holder))
                sock.close()
                tag = False
            sock.close()
            if tag:
                print("success to give token {} to {}".format(cur_token, token_holder))
                break
        return True

    @staticmethod
    def get_host_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
        return ip



    @staticmethod
    def broadcast(connection_list, msg, my):
        if type(msg) != bytes:
            raise exception.FormatException
        if type(my) !=tuple:
            raise exception.FormatException
        for addr in connection_list:
            if addr != my:
                print("broadcasting to {}".format(addr))
                SocketUtil.send(msg,addr)




