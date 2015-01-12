import redis

keyFormat = 'thread_{0}_{1}'
threadRedisDB = redis.StrictRedis( '127.0.0.1', 6379 )#TODO: move to config file

def addNewThread(boardId, threadId, subject):
	threadInfo = {
		'threadId':threadId,
		'post_count':'0',
		'subject':subject
	}
	key = _threadKey(boardId, threadId)
	threadRedisDB.hmset(key+'_info', threadInfo)

def addPostIdToPostList(boardId, threadId, postId):
	key = _threadKey(boardId, threadId)
	threadRedisDB.rpush( key+'_postList', postId )

def incrementThreadPostCount(boardId, threadId):
	key = _threadKey(boardId, threadId)
	threadRedisDB.hincrby(key+'_info', 'post_count', 1)

def getThreadPostCount(boardId, threadId):
	key = _threadKey(boardId, threadId)
	return threadRedisDB.hget(key+'_info', 'post_count')

def getThreadInfo(boardId, threadId):
	key = _threadKey(boardId, threadId)
	return threadRedisDB.hgetall(key+'_info')
	
def getThreadPostListAll(boardId, threadId):
	return getThreadPostListRange(boardId, threadId, 0, -1)

def getThreadPostListRange(boardId, threadId, start, end):
	key = _threadKey(boardId, threadId)
	return threadRedisDB.lrange(key+'_postList', start, end)

def _threadKey(boardId, threadId):
	return keyFormat.format( boardId, threadId )
