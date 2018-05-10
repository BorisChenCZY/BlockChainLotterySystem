import socket

import P2P.NetworkException as exception


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
    def request_time_stamp(addr):
        if type(addr[0]) != str or type(addr[1]) != int:
            raise exception.FormatException()
        # Create a socket (SOCK_STREAM means a TCP socket)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # Connect to server and send data
            sock.connect(addr)
            sock.sendall(b'time')
            # Receive data from the server and shut down
            received = sock.recv(1024).decode()
            print("Received: {}".format(received))
        finally:
            sock.close()
        return received


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
            sock.sendall(msg)
        except:
            sock.close()
        sock.close()
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
    def broadcast(msg, connection_list):
        if type(msg) != bytes:
            raise exception.FormatException
        for addr in connection_list:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.connect(addr)
                sock.sendall(msg)
            except:
                sock.close()
            sock.close()




