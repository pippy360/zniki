import redis

keyFormat = 'file_{0}'
postRedisDB = redis.StrictRedis( '127.0.0.1', 6379 )#TODO: move to config file

def addFile(fileId, fileInfo, creatorIP, creatorId=None):
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
		'creatorId':	creatorId,
		'creatorIP':	creatorIP
	}

	#add it to the redis database
	key = keyFormat.format( boardId, threadId, fileId )
	postRedisDB.hmset( key, fileData )

def getFileInfo(fileId):
	key = keyFormat.format( fileId )
	return postRedisDB.hgetall( key )
