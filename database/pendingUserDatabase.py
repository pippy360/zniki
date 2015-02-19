import redis

PENDING_USER_LIST_KEY = 'list_of_pending_users'

keyFormat = 'pending_user_{0}'
pendingRedisDB = redis.StrictRedis( '127.0.0.1', 6379 )

def addUser(userId, email, username, passwordHash):
  user = {
    'email':email,
    'username':username,
    'passwordHash':passwordHash
  }
  
  _addToPendingUserList(userId)

  key = _pendingKey(userId)
  pendingRedisDB.hmset(key, user)

def removeUser(userId):
  _removeFromPendingUserList(userId)
  key = _pendingKey(userId)
  pendingRedisDB.delete(key)

def getUserInfo(userId):
  key = _pendingKey(userId)
  return pendingRedisDB.hgetall(key)

def _addToPendingUserList(userId):
  pendingRedisDB.sadd( PENDING_USER_LIST_KEY, userId )

def _removeFromPendingUserList(userId):
  pendingRedisDB.srem( PENDING_USER_LIST_KEY, userId )

#returns the id's
def getAllPendingUsers():
  return pendingRedisDB.smembers( PENDING_USER_LIST_KEY )

def _pendingKey(userId):
  return keyFormat.format(userId)
