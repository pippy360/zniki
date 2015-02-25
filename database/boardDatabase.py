import redis

keyFormat = 'board_{0}'
boardRedisDB = redis.StrictRedis( '127.0.0.1', 6379 )#TODO: move to config file

board_post_key 		= "_post_count"
board_mod_key_list 	= "_mods_list"
board_mod_key 		= "_mod_"
board_user_key 		= "_users"

def incrementBoardPostCount(boardId):
	key = _boardKey(boardId)
	boardRedisDB.incr(key+board_post_key)

def getBoardPostCount(boardId):
	key = _boardKey(boardId)
	return boardRedisDB.get(key+board_post_key)

def addBoard(boardId, name, isPrivate, adminId, password=None):
	boardInfo = {
		'adminId': adminId,
		'isPrivate': isPrivate,
		'name': name,
		'threadCount':'0',
		'password': password
	}
	key = _boardKey(boardId)
	boardRedisDB.hmset(key+'_info', boardInfo)

def getBoardName(boardId):
	key = _boardKey(boardId)
	return boardRedisDB.hget(key+'_info','name')

def getBoardInfo(boardId):
	key = _boardKey(boardId)
	return boardRedisDB.hgetall(key+'_info')

#users - only used if private

def getAllBoardUsers(boardId):
	key = _boardKey(boardId)
	return boardRedisDB.lrange(key+board_user_key, 0, -1)

def addBoardUser(boardId, userId):
	key = _boardKey(boardId)
	boardRedisDB.lpush(key+board_user_key, userId)

def changeBoardName(boardId, newName):
	key = _boardKey(boardId)
	boardRedisDB.hset(key+'_info', 'name', newName)

def changeBoardPassword(boardId, newPass):
	key = _boardKey(boardId)
	boardRedisDB.hset(key+'_info', 'password', newPass)

def removeBoardUser(boardId, userId):
	pass

#mods

def setModPermissions(boardId, modId, addPeopleP=False, 
						kickUserP=False, deletePostP=False):
	key = _boardKey(boardId)
	perms = {
		'addUsers': addPeopleP,
		'kickUsers': kickUserP,
		'removePosts': deletePostP
	}
	boardRedisDB.hmset(key+board_mod_key+modId, perms)

def getModsPermissions(boardId, modId):
	key = _boardKey(boardId)
	return boardRedisDB.hgetall(key+board_mod_key+modId)

def getModsIdsList(boardId):
	key = _boardKey(boardId)
	return boardRedisDB.lrange(key+board_mod_key_list, 0, -1)

def addBoardMod(boardId, modId):
	key = _boardKey(boardId)
	boardRedisDB.lpush(key+board_mod_key_list, modId)
	setModPermissions(boardId, modId)

def removeBoardMod(boardId, modId):
	pass

#threads
def addThreadIdToThreadList(boardId, threadId):
	key = _boardKey(boardId)
	boardRedisDB.lpush( key+'_threadList', threadId )

def moveThreadToFront(boardId, threadId):
	key = _boardKey(boardId)
	atom = boardRedisDB.pipeline()
	atom.lrem(key+'_threadList', 1, threadId)
	atom.lpush(key+'_threadList', threadId)
	atom.execute()

def incrementBoardThreadCount(boardId):
	key = _boardKey(boardId)
	boardRedisDB.hincrby(key+'_info', 'threadCount', 1)

def getBoardThreadCount(boardId):
	key = _boardKey(boardId)
	return int(boardRedisDB.hget(key+'_info', 'threadCount'))

def getBoardThreadListAll(boardId):
	return getBoardThreadListRange(boardId, 0, -1)

def getBoardThreadListRange(boardId, start, end):
	key = _boardKey(boardId)
	return boardRedisDB.lrange(key+'_threadList', start, end)


def _boardKey(boardId):
	return keyFormat.format(boardId)
