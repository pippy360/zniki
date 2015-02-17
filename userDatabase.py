import redis

keyFormat = 'active_user_{0}'
activeRedisDB = redis.StrictRedis( '127.0.0.1', 6379 )

def addUser(userId, email, username, passwordHash, apiKey, isAdmin):
  user = {
    'email':email,
    'username':username,
    'passwordHash':passwordHash,
    'apiKey':apiKey,
    'isAdmin':isAdmin
  }
  key = _activeKey(userId)
  activeRedisDB.hmset(key, user)

def changeUsername(userId, newUsername):
  key = _activeKey(userId)
  activeRedisDB.hset(key, 'username', newUsername)

def changePasswordHash(userId, newPasswordHash):
  key = _activeKey(userId)
  activeRedisDB.hset(key, 'passwordHash', newPasswordHash)

def removeUser(userId):
  key = _activeKey(userId)
  activeRedisDB.delete(key)

def getUserInfo(userId):
  key = _activeKey(userId)
  return activeRedisDB.hgetall(key)

def _activeKey(userId):
  return keyFormat.format(userId)
