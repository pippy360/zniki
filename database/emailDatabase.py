import redis

keyFormat = 'email_{0}'
email_list_key = 'all_emails_list'
emailRedisDB = redis.StrictRedis( '127.0.0.1', 6379 )

def getAllEmails():
	return emailRedisDB.lrange(email_list_key, 0, -1)

def addEmail(email, userId):
	emailRedisDB.lpush(email_list_key, email)
	key = _emailKey(email)
	emailRedisDB.set(key, userId)

def removeEmail(email):
	emailRedisDB.lrem(email_list_key, email)
	key = _emailKey(email)
	emailRedisDB.delete(key)

def getEmailUserId(email):
	key = _emailKey(email)
	return emailRedisDB.get(key)

def _emailKey(email):
	return keyFormat.format(email)
