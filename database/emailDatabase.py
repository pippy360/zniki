import redis

keyFormat = 'email_{0}'
emailRedisDB = redis.StrictRedis( '127.0.0.1', 6379 )

def addEmail( email, userId ):
  key = _emailKey(email)
  emailRedisDB.set(key, userId)

def removeEmail( email ):
  key = _emailKey(email)
  emailRedisDB.delete(key)

def getEmailUserId(email):
  key = _emailKey(email)
  return emailRedisDB.get(key)

def _emailKey(email):
  return keyFormat.format(email)
