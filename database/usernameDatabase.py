import redis

keyFormat = 'email_{0}'
usernameRedisDB = redis.StrictRedis( '127.0.0.1', 6379 )

def addUsername( username, userId ):
  key = _usernameKey(username)
  usernameRedisDB.set(key, userId)

def removeUsername( username ):
  key = _usernameKey(username)
  usernameRedisDB.delete(key)

def getUsernameUserId(username):
  key = _usernameKey(username)
  return usernameRedisDB.get(key)

def _usernameKey(username):
  return keyFormat.format(username)
