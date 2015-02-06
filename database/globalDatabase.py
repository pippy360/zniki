import redis

keyFormat = 'global_{0}'
globalRedisDB = redis.StrictRedis( '127.0.0.1', 6379 )#TODO: move to config file

board_count_key = 'board_count'
file_count_key 	= 'file_count'

def getBoardCount():
	return globalRedisDB.get(board_count_key)
	
def incrementBoardCount():
	globalRedisDB.incr(board_count_key)

def getFileCount():
	return globalRedisDB.get(file_count_key)
	
def incrementFileCount():
	globalRedisDB.incr(file_count_key)
