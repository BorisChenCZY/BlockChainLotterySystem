import sqlite3
from VoteBlock import *
class ChainError(Exception):
    pass

DATABASE_PATH = "./test.sqlite"
BLOCK_TABLE_OFF = "Block"
VOTE_TABLE_OFF = "Vote"

#temporarily
def get_timestamp():
    import datetime
    return datetime.datetime.now().timestamp()

class Chain:
    __conn = None
    __c = None
    __name = None
    __loaded = None

    def __init__(self, name):
        self.__name = name
        self.__conn = sqlite3.connect(DATABASE_PATH)
        self.__c = self.__conn.cursor()

    def __get_table(self):
        self.__c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        n = self.__c.fetchall()
        names = []
        for name in n:
            names.append(name[0])
        return names

    def get_last_block(self):
        if not self.__loaded:
            raise ChainError("Chain not loaded")
        self.__c.execute(
            """
            select max(id), hash, prehash from {};
            """.format(self.__name + BLOCK_TABLE_OFF)
        )
        return self.__c.fetchone()


    def load(self):
        # todo check the chain is valid
        self.__loaded = True

    def create(self):
        n = self.__get_table()
        if(self.__name + BLOCK_TABLE_OFF in n or self.__name + VOTE_TABLE_OFF in n):
            raise ChainError("The chain already exists")

        try:
            self.__c.execute("""
              CREATE TABLE {name} (id INTEGER PRIMARY KEY AUTOINCREMENT
                                  , hash BLOB
                                  , prehash BLOB
                                  );
              """.format(name = self.__name + BLOCK_TABLE_OFF))

            self.__c.execute(
                """
                CREATE TABLE {name} (block_id int
                                    , timestamp float
                                    , target BLOB
                                    , pubkey BLOB
                                    , info VARCHAR 
                                    , sign BLOB);
                """.format(name = self.__name + VOTE_TABLE_OFF)
            )

            self.__c.execute(
                """
                INSERT INTO {name} VALUES (0, "0", "不存在的");
                """
            .format(name=self.__name + BLOCK_TABLE_OFF))
            self.__conn.commit()
        except Exception:
            n = self.__get_table()
            if(self.__name + BLOCK_TABLE_OFF in n):
                self.__c.execute("DROP TABLE {};".format(self.__name + BLOCK_TABLE_OFF))
            if(self.__name + VOTE_TABLE_OFF in n):
                self.__c.execute("DROP TABLE {};".format(self.__name + VOTE_TABLE_OFF))
            self.__conn.commit()
            raise ChainError("Create chain failed.")

        self.__loaded = True

    def add_block(self, block):
        self.__verify_block(block)

        id = block.get_id()

        prehash = block.get_prehash().decode("utf-8")
        hash = block.get_hash().decode("utf-8")
        voteInfos = block.get_vote_infos()

        self.__c.execute("""
                        INSERT INTO {} VALUES ({id}, "{hash}", "{prehash}")
                        """.format(self.__name + BLOCK_TABLE_OFF, id=id, hash=hash, prehash=prehash))
        self.__conn.commit()

        for voteInfo in voteInfos:
            print(bytes(voteInfo))
            timestamp = float(voteInfo.get_timestamp())
            target = voteInfo.get_target().decode("utf-8")
            pubkey = voteInfo.get_pubkey().decode("utf-8")
            info = voteInfo.get_info().decode("utf-8")
            sign = voteInfo.get_sign().decode("utf-8")
            self.__c.execute("""
                             INSERT INTO {} VALUES ({blockid}, {timestamp}, "{target}", "{pubkey}", "{info}", "{sign}")
                             """.format(self.__name + VOTE_TABLE_OFF, blockid=id, timestamp=timestamp, target=target, pubkey=pubkey, info=info, sign=sign))
        self.__conn.commit()

    def get_block(self, id):
        if(type(id) != int):
            raise ChainError("id must be int, not {}".format(type(id)))

        self.__c.execute("SELECT * from {} where id={}".format(self.__name + BLOCK_TABLE_OFF, id))
        id, hash, prehash = self.__c.fetchone()
        voteBlock = VoteBlock(id, prehash.encode('utf-8'), hash.encode('utf-8'))

        self.__c.execute("SELECT * from {} where block_id={}".format(self.__name + VOTE_TABLE_OFF, id))

        for id, timestamp, target, pubkey, info, sign in self.__c.fetchall():
            vote = VoteInfo.parse_info(info)
            voteInfo = VoteInfo(timestamp, target.encode("utf-8"), pubkey.encode("utf-8"), vote, sign.encode("utf-8"))
            voteBlock.add_info(voteInfo)

        # print(bytes(voteBlock))

        # print(voteBlock.check())
        if not voteBlock.check():
            raise ChainError("block not valid!")
        return voteBlock

    def __verify_block(self, block):
        if(type(block) is not VoteBlock):
            raise ChainError("block must by VoteBlock, not {}".format(type(block)))
        if(not block.check()):
            raise ChainError("block not valid (self info check failed)")
        lb = self.get_last_block()
        if(lb[1] != block.get_prehash().decode("utf-8")):
            raise ChainError("block not valid (prehash check failed)")
        if(lb[0] != block.get_id() - 1):
            raise ChainError("block not valid (id not successive)")
        return True

    def test(self):
        return self.get_last_block()

if __name__ == "__main__":
    chain = Chain("test")
    # chain.create()
    chain.load()
    print(chain.test())

    timestamp = datetime.datetime.now().timestamp() # current time
    pubkey = b'pubkey'
    target = b'target'
    sign = b'sign'
    vote = (1, [1, 2, 3])
    voteInfo = VoteInfo(timestamp = timestamp, target = target, pubkey=pubkey, vote=vote, sign=sign)

    voteBlock = VoteBlock(id=1, prehash=b'0', hash=b'hash')
    voteBlock.add_info(voteInfo)
    voteBlock.close()

    print(bytes(voteBlock))
    print(voteBlock.check())

    # chain.add_block(voteBlock)

    chain.get_block(1)