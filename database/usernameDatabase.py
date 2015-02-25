import redis

keyFormat = 'username_{0}'
username_list_key = 'all_username_list'
usernameRedisDB = redis.StrictRedis( '127.0.0.1', 6379 )

def getAllUsernames():
	return usernameRedisDB.lrange(username_list_key, 0, -1)

def addUsername(username, userId):
	usernameRedisDB.lpush(username_list_key, username)
	key = _usernameKey(username)
	usernameRedisDB.set(key, userId)

def removeUsername(username):
	usernameRedisDB.lrem(username_list_key, 0, username)
	key = _usernameKey(username)
	usernameRedisDB.delete(key)

def getUsernameUserId(username):
	key = _usernameKey(username)
	return usernameRedisDB.get(key)

def _usernameKey(username):
	return keyFormat.format(username)
