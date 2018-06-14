import sqlite3
import settings
from block.block_hashfunc import hash

class BlockReader():
    def __init__(self):
        self.conn = sqlite3.connect(settings.BLOCK_DATABASE_DIR)
        self.cursor = self.conn.cursor()

    def getMinerList (self):
        self._getAll("select * from miner_list")
        return self.allResult
    
    def getVoteResult(self, target):
        self._getAll("select selection, count(selection) from Result where target=? group by selection", (target,))
        return self.allResult

    def getBlock(self, block_id):
        self._getOne("select id,hash,prehash,count(*),generator from Block where id=?", (block_id,))
        return self.oneResult
        
    def getBlocks(self):
        self._getAll("select * from Block")
        return self.allResult
    
    def getSingleBlockInfo(self, block_id):
        self._getAll("select v.target,v.pubkey,r.selection,v.timestamp from Vote v join Result r on r.target = v.target where v.block_id=?", (block_id,))
        return self.allResult
    
    def getBlockInfos(self):
        self._getAll("select id,hash,prehash,count(*),generator from Vote LEFT join Block b on b.id = block_id group by block_id",())
        return self.allResult
    
    def existTarget(self, target):
        self._getOne("select * from Vote where target=?", (target,))
        if(self.oneResult):
            return True
        else:
            return False
    
    def _getOne(self, sql, params=()):
        self.cursor.execute(sql, params)
        self.oneResult = self.cursor.fetchone()

    def _getMany(self, size, sql, params=()):
        self.cursor.execute(sql, params)
        self.manyResult = self.cursor.fetchmany(size)
        
    def _getAll(self, sql, params=()):
        self.cursor.execute(sql, params)
        self.allResult = self.cursor.fetchall()
    
    def __del__(self):
        self.cursor.close()
        self.conn.close()