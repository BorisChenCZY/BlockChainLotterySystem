import sqlite3
import settings
from block.block_hashfunc import hash

class BlockReader():
    def __init__(self):
        self.conn = sqlite3.connect(settings.BLOCK_DATABASE_DIR)
        self.cursor = self.conn.cursor()
    
    def getVoteResult(self, target):
        self._getAll("select * from Result where target=?", (target,))
        return self.allResult

    def getBlock(self, block_id):
        self._getOne("select * from Block where id=?", (block_id,))
        return self.oneResult
        
    def getBlocks(self):
        self._getAll("select * from Block")
        return self.allResult
    
    def _getOne(self, sql, params=()):
        self.cursor.execute(sql, params)
        self.oneResult = self.cursor.fetchone()

    def _getMany (self, size, sql, params=()):
        self.cursor.execute(sql, params)
        self.manyResult = self.cursor.fetchmany(size)
        
    def _getAll(self, sql, params=()):
        self.cursor.execute(sql, params)
        self.allResult = self.cursor.fetchall()
    
    def __del__(self):
        self.cursor.close()
        self.conn.close()