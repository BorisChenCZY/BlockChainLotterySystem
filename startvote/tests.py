import block.model_block as bm
import datetime
block = bm.BlockReader()
# print(block.getVoteResult())
print(block.getBlocks())
print(datetime.datetime.now().timestamp())