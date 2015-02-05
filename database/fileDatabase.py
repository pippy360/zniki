import redis

keyFormat = 'file_{0}_{1}_{2}'
postRedisDB = redis.StrictRedis( '127.0.0.1', 6379 )#TODO: move to config file

def addFile(boardId, threadId, postId, fileId, fileInfo, creatorIP, creatorId=None):
	if creatorId == None:
		creatorId = 'NULL'

	fileData = {
		'databaseId'  : fileId,
		'originalFilename': fileInfo['filename'],
		'fileHash':     fileInfo['hash'],
		'filename':     fileInfo['filename'],
		'fileLocation': fileInfo['fileLocation'],
		'extension':    fileInfo['extension'],
		'mimetype':     '',
		'fileMetadata': fileInfo['metadata'],
		'fileType':     fileInfo['type'],
		'postId': 		postId,
		'creatorId':	creatorId,
		'creatorIP':	creatorIP
	}

	#add it to the redis database
	key = keyFormat.format( boardId, threadId, fileId )
	postRedisDB.hmset( key, fileData )

def getFileInfo(boardId, threadId, postId, fileId):
	key = keyFormat.format( boardId, threadId, fileId )
	return postRedisDB.hgetall( key )
