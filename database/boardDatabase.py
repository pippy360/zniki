import redis

keyFormat = 'board_{0}'
boardRedisDB = redis.StrictRedis( '127.0.0.1', 6379 )#TODO: move to config file
board_count_key = 'board_count'

def getBoardCount():
	return boardRedisDB.get(board_count_key)
	
def incrementBoardCount():
	boardRedisDB.incr(board_count_key)

def addBoard(boardId, name):
	boardInfo = {
		'name': name,
		'threadCount':'0'
	}
	key = _boardKey(boardId)
	boardRedisDB.hmset(key+'_info', boardInfo)

def addThreadIdToThreadList(boardId, threadId):
	key = _boardKey(boardId)
	boardRedisDB.lpush( key+'_threadList', threadId )

def incrementBoardThreadCount(boardId):
	key = _boardKey(boardId)
	boardRedisDB.hincrby(key+'_info', 'threadCount', 1)

def getBoardThreadCount(boardId):
	key = _boardKey(boardId)
	return int(boardRedisDB.hget(key+'_info', 'threadCount'))

def getBoardName(boardId):
	key = _boardKey(boardId)
	return boardRedisDB.hget(key+'_info','name')

def getBoardInfo(boardId):
	key = _boardKey(boardId)
	return boardRedisDB.hgetall(key+'_info')
	
def getBoardThreadListAll(boardId):
	return getBoardThreadListRange(boardId, 0, -1)

def getBoardThreadListRange(boardId, start, end):
	key = _boardKey(boardId)
	return boardRedisDB.lrange(key+'_threadList', start, end)

def moveThreadToFront(boardId, threadId):
	key = _boardKey(boardId)
	atom = boardRedisDB.pipeline()
	atom.lrem(key+'_threadList', 1, threadId)
	atom.lpush(key+'_threadList', threadId)
	atom.execute()

def _boardKey(boardId):
	return keyFormat.format(boardId)
