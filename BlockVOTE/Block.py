import hashlib


def f(info):
    return bytes(hashlib.sha3_512(info).hexdigest().encode("utf-8"))


HASH_FUNC = f


class BlockInfoError(Exception):
    pass


class Block:
    __id = None
    __prehash = None
    __hash = None
    __info = None

    def __init__(self, id=None, prehash=None, hash = None, info=None):
        if (id):
            self.set_id(id)
        if (prehash):
            self.set_prehash(prehash)
        if (info):
            self.set_info(info)
        if (hash):
            self.set_hash(hash)

    def set_hash(self, hash):
        if (type(hash) != bytes):
            raise BlockInfoError("hash must be bytes")
        self.__hash = hash

    def set_id(self, id):
        if (type(id) != int):
            raise BlockInfoError("id must be int")
        self.__id = id

    def set_prehash(self, hash):
        if (type(hash) != bytes):
            raise BlockInfoError("hash must be bytes")
        self.__prehash = hash

    def set_info(self, info):
        if (type(info) != bytes):
            raise BlockInfoError("Info must by bytes")
        if (len(info) > 1024):
            raise BlockInfoError("Info size must under 1M(1024Bytes)")
        self.__info = info

    def close(self):
        if (self.__info == None):
            raise BlockInfoError("No information inside block")
        self.__hash = f(self.__info)
        # print(self.__hash)

    def get_info(self):
        return self.__info

    def get_prehash(self):
        return self.__prehash

    def get_hash(self):
        if (not self.__hash):
            raise BlockInfoError("You need to close the block first or set hash of the block (blocl.set_hash())")
        return self.__hash

    def get_id(self):
        return self.__id

    def __bytes__(self):
        if (not self.__id):
            raise BlockInfoError("You need to set the id of the block first.")
        if (not self.__prehash):
            raise BlockInfoError("You need to set the prehash of the block first")
        if (not self.__info):
            raise BlockInfoError("You need to set the info of the block first")
        if (not self.__hash):
            raise BlockInfoError("You need to set the hash of the block first")
        return self.__id.to_bytes(4, "little") + b'/' + \
               self.__prehash + b'/' + \
               self.__hash + b'/' + \
               self.__info

    def check(self):
        return self.__hash == HASH_FUNC(self.__info)

    @staticmethod
    def load(block):
        if(type(block) != bytes):
            raise BlockInfoError("block must be bytes")
        components = block.split(b"/")

        id = int.from_bytes(components[0], byteorder='little')
        prehash = components[1]
        hash = components[2]
        info = components[3]
        return Block(id, prehash, hash, info)


if __name__ == "__main__":
    # test
    block = Block(id=1, prehash=b"prehash")
    block.set_info("Hello World".encode("utf-8"))
    print(block.get_info())
    block.close()
    print(block.get_hash())
    bs = bytes(block)
    block = Block.load(bs)
    print(block.get_hash())
    print(block.get_id())
    print(block.check())
