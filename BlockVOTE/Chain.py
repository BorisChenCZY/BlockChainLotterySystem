import sqlite3
from BlockVOTE.VoteBlock import *
from BlockVOTE.VoteInfo import *
from BlockVOTE.P2P.timeaddr import TIMESTAMP_SERVER_ADDR
from BlockVOTE.P2P.SocketUtil import SocketUtil
class ChainError(Exception):
    pass

DATABASE_PATH = "./test.sqlite"
BLOCK_TABLE_OFF = "Block"
VOTE_TABLE_OFF = "Vote"
RESULT_TABLE_OFF = "Result"

#changed: ues timestamp server
def get_timestamp():
    return SocketUtil.get_time_stamp(TIMESTAMP_SERVER_ADDR)

class Chain:
    __conn = None
    __c = None
    __name = None
    __loaded = None

    def __init__(self, name):
        self.__name = name
        self.__conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
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
        blocks = self.get_chain(0)
        if blocks == None:
            return
        pre_hash = b"0"
        for block in blocks:
            # print(pre_hash, block.get_prehash())
            if(block.get_prehash() != pre_hash):
                raise ChainError("Invalid Chain Detected!")
            pre_hash = block.get_hash()
            block.check()


    def duplicate_vote(self, voteInfo):
        # true for duplicate
        if(type(voteInfo) != VoteInfo):
            raise ChainError("Must input voteInfo")
        timestamp = float(voteInfo.get_timestamp())
        pubkey = voteInfo.get_pubkey()
        self.__c.execute(
            """
            select vote_id from {} where pubkey = "{pubkey}" and timestamp  =  {timestamp}
            """.format(self.__name + VOTE_TABLE_OFF, pubkey = pubkey, timestamp = timestamp)
        )
        return len(self.__c.fetchall()) != 0


    def create(self):
        n = self.__get_table()
        print(n)
        if(self.__name + BLOCK_TABLE_OFF in n or self.__name + VOTE_TABLE_OFF in n):
            raise ChainError("The chain already exists")

        try:
            self.__c.execute("""
              CREATE TABLE {name} (id INTEGER PRIMARY KEY AUTOINCREMENT
                                  , hash BLOB
                                  , prehash BLOB
                                  , generator VARCHAR 
                                  , timestamp FLOAT 
                                  );
              """.format(name = self.__name + BLOCK_TABLE_OFF))

            self.__c.execute(
                """
                CREATE TABLE {name} (vote_id INTEGER PRIMARY KEY AUTOINCREMENT
                                    , block_id int
                                    , timestamp float
                                    , target BLOB
                                    , pubkey BLOB
                                    , info VARCHAR 
                                    , sign BLOB
                                    , status int);
                """.format(name = self.__name + VOTE_TABLE_OFF)
            )

            self.__c.execute(
                """
                CREATE TABLE {name} (target BLOB
                                    , pubkey BLOB
                                    , prob_id int 
                                    , selection int
                                    );
                """.format(name = self.__name + RESULT_TABLE_OFF)
            )

            self.__c.execute(
                """
                INSERT INTO {name} VALUES (0, "0", "不存在的", "创世链", "牛逼");
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

    def add_block(self, block, localMachine):
        self.__verify_block(block)

        id = block.get_id()

        prehash = block.get_prehash().decode("utf-8")
        hash = block.get_hash().decode("utf-8")
        voteInfos = block.get_vote_infos()

        self.__c.execute("""
                        INSERT INTO {} VALUES ({id}, "{hash}", "{prehash}", "{localMachine}", {timestamp})
                        """.format(self.__name + BLOCK_TABLE_OFF, id=id, hash=hash, prehash=prehash, timestamp = get_timestamp(), localMachine = localMachine))
        self.__conn.commit()

        for voteInfo in voteInfos:
            self.add_vote(voteInfo, id)

    def get_block(self, id):
        if(type(id) != int):
            raise ChainError("id must be int, not {}".format(type(id)))

        self.__c.execute("SELECT id, hash, prehash from {} where id={}".format(self.__name + BLOCK_TABLE_OFF, id))
        id, hash, prehash = self.__c.fetchone()
        voteBlock = VoteBlock(id, prehash.encode('utf-8'), hash.encode('utf-8'))

        self.__c.execute("SELECT * from {} where block_id={}".format(self.__name + VOTE_TABLE_OFF, id))

        for args in self.__c.fetchall():
            voteInfo = Chain.parse_voteInfo(args)
            voteBlock.add_info(voteInfo)

        # print(bytes(voteBlock))

        # print(voteBlock.check())
        if not voteBlock.check():
            raise ChainError("block not valid!")
        return voteBlock

    def get_chain(self,lst):
        maxid = self.get_last_block()[0]
        if maxid:
            blocks = []
            for each in range(lst+1,maxid+1):
                blocks.append(self.get_block(each))
            return blocks

    @staticmethod
    def parse_voteInfo(args):
        vote_id, id, timestamp, target, pubkey, info, sign, status = args
        vote = VoteInfo.parse_info(info)
        voteInfo = VoteInfo(timestamp, target.encode("utf-8"), pubkey.encode("utf-8"), vote, sign.encode("utf-8"))
        if not voteInfo.check():
            raise ChainError("voteInfo not valid (sign check failed)")
        return voteInfo

    def __verify_block(self, block):
        if(type(block) is not VoteBlock):
            raise ChainError("block must by VoteBlock, not {}".format(type(block)))
        if(not block.check()):
            raise ChainError("block not valid (self info check failed)")
        lb = self.get_last_block()
        # print("block id:",block.get_id())
        if(lb[1] != block.get_prehash().decode("utf-8")):
            print(block.get_prehash().decode("utf-8"), "!=", lb[1])
            raise ChainError("block not valid (prehash check failed)")
        if(lb[0] != block.get_id() - 1):
            raise ChainError("block not valid (id not successive)")
        return True

    def test(self):
        return self.get_last_block()

    def add_vote(self, voteInfo, id):
        """
        thit method is to add voteInfo that has not written or comfirmed into the chain
        :param voteInfo:
        :return:
        """
        if type(voteInfo) is not VoteInfo:
            raise ChainError("voteInfo must by VoteInfo, but not {}".format(type(voteInfo)))
        if not voteInfo.check():
            raise ChainError("voteInfo inside block not valid!")
        timestamp = float(voteInfo.get_timestamp())
        target = voteInfo.get_target().decode("utf-8")
        pubkey = voteInfo.get_pubkey().decode("utf-8")
        info = voteInfo.get_info().decode("utf-8")
        sign = voteInfo.get_sign().decode("utf-8")
        if id == -1:
            status = 0
            id = "NULL"
        else:
            status = 1

        self.__c.execute("""
                         INSERT INTO {} VALUES (NULL, {blockid}, {timestamp}, "{target}", "{pubkey}", "{info}", "{sign}", {status})
                         """.format(self.__name + VOTE_TABLE_OFF, blockid=id, timestamp=timestamp, target=target, pubkey=pubkey, info=info, sign=sign, status = status))
        self.__conn.commit()

        if(id != -1):
            prob_id = voteInfo.get_prob_id()
            selections = voteInfo.get_selection()
            self.__c.execute('DELETE FROM {} WHERE target="{target}" and pubkey = "{pubkey}" and prob_id = {prob_id}'.format(self.__name+RESULT_TABLE_OFF, target=target, pubkey=  pubkey, prob_id = prob_id))
            self.__conn.commit()
            for selection in selections:
                self.__c.execute("""
                                 INSERT INTO {} VALUES ("{target}", "{pubkey}", {prob_id}, {selection})
                                 """.format(self.__name+RESULT_TABLE_OFF, target=target, pubkey=pubkey, prob_id=prob_id, selection=selection))
            self.__conn.commit()
        # self.__c.execute()

    def get_uncomfirmed_votes(self):
        self.__c.execute("""
                        SELECT * from {} where block_id is null order by timestamp
                        """.format(self.__name + VOTE_TABLE_OFF))
        votes = []
        for args in self.__c.fetchall():
            voteInfo = Chain.parse_voteInfo(args)
            if not voteInfo.check():
                raise ChainError("voteInfo not valid (sign check failed)")
            votes.append(voteInfo)
        return votes

    def remove_vote(self, voteInfo):
        if type(voteInfo) is not VoteInfo:
            raise ChainError("voteInfo must be VoteInfo")
        block_id = -1
        timestamp = float(voteInfo.get_timestamp())
        target = voteInfo.get_target().decode("utf-8")
        pubkey = voteInfo.get_pubkey().decode("utf-8")
        info = voteInfo.get_info().decode("utf-8")
        sign = voteInfo.get_sign().decode("utf-8")
        self.__c.execute('DELETE FROM {} where block_id is NULL and timestamp={} and target="{}" and pubkey="{}" and info="{}" and sign="{}"'.
                         format(self.__name+VOTE_TABLE_OFF, timestamp, target, pubkey, info, sign))
        self.__conn.commit()
        print('DELETE FROM {} where block_id is NULL and timestamp={} and target="{}" and pubkey="{}" and info="{}" and sign="{}"'.
              format(self.__name+VOTE_TABLE_OFF, timestamp, target, pubkey, info, sign))



if __name__ == "__main__":
    chain = Chain("")
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

    print(123, chain.duplicate_vote(voteInfo))