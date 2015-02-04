import redis

keyFormat = 'global_{0}'
globalRedisDB = redis.StrictRedis( '127.0.0.1', 6379 )#TODO: move to config file
project_count_key = 'project_count'
project_list_key = 'project_list'

def getProjectCount():
	if globalRedisDB.get(project_count_key) == None:
		globalRedisDB.set(project_count_key, 0)

	return int(globalRedisDB.get(project_count_key))
	
def incrementProjectCount():
	globalRedisDB.incr(project_count_key)

def addProjectIdToProjectList(projectId):
	key = _globalKey(project_list_key)
	globalRedisDB.lpush( key, projectId )
	
def getProjectListAll():
	return getProjectListRange(0, -1)

def getProjectListRange(start, end):
	key = _globalKey(project_list_key)
	return globalRedisDB.lrange(key, start, end)

#this function probably won't ever be needed
def moveProjectToFront(projectId):
	key = _globalKey(project_list_key)
	atom = globalRedisDB.pipeline()
	atom.lrem(key, 1, projectId)
	atom.lpush(key, projectId)
	atom.execute()

def _globalKey(inputStr):
	return keyFormat.format(inputStr)
