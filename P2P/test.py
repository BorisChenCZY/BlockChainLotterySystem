import P2P.Node as node


if __name__ == "__main__":
    addr = ("localhost", 9999)
    a = node.Node(addr)
    a.serving()