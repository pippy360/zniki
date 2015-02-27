import redis

keyFormat = 'post_{0}_{1}'
postRedisDB = redis.StrictRedis( '127.0.0.1', 6379 )#TODO: move to config file

#only adds the post to the post database, the thread object (in the thread DB must also be updated)
def addPost(boardId, postId, message, attachedFileId=None, creatorIP=None, creatorId=None):
	#get the time
	if attachedFileId == None:
		attachedFileId = 'NULL'
	if creatorId == None:
		creatorId = 'NULL'

	post = {
		'postId': postId,
		'time_long': ' ',
		'time': ' ',
		'message': message,
		'creatorIP': creatorIP,
		'creatorId': creatorId,
		'attachedFileId':attachedFileId
	}
	#add it to the redis database
	key = keyFormat.format( boardId, postId )
	postRedisDB.hmset( key, post )

def getPost(boardId, postId):
	key = keyFormat.format( boardId, postId )
	return postRedisDB.hgetall( key )

def removePost(boardId, postId):
	key = keyFormat.format( boardId, postId )
	postRedisDB.delete(key)
