import redis

keyFormat = 'global_{0}'
globalRedisDB = redis.StrictRedis( '127.0.0.1', 6379 )#TODO: move to config file

file_count_key 	= 'file_count'

global_count_key = 'global_count'
board_list_key = 'board_list'

def getBoardList():
	return globalRedisDB.lrange(board_list_key, 0, -1)

def addBoardIdToBoardList(boardId):
	globalRedisDB.lpush(board_list_key, boardId)

def removeBoardList(boardId):
	pass

def getGlobalCount():
	if globalRedisDB.get(global_count_key) == None:
		globalRedisDB.set(global_count_key, 0)

	return int(globalRedisDB.get(global_count_key))
	
def incrementGlobalCount():
	globalRedisDB.incr(global_count_key)

def getFileCount():
	return globalRedisDB.get(file_count_key)
	
def incrementFileCount():
	globalRedisDB.incr(file_count_key)
