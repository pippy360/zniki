import redis

keyFormat = 'active_user_{0}'
activeRedisDB = redis.StrictRedis( '127.0.0.1', 6379 )
friends_list_key = '_friends'
admin_boards_list_key = '_admin_boards'
mod_boards_list_key = '_mods_boards'
private_boards_list_key = '_private_boards'

def addUser(userId, email, username, passwordHash, isAdmin, reputation, profilePicFileId=None):

  hasProfilePic = (profilePicFileId != None)
  user = {
    'email':email,
    'username':username,
    'passwordHash':passwordHash,
    'reputation':reputation,
    'isAdmin':isAdmin,
    'hasProfilePic':hasProfilePic,
    'profilePicFileId':''
  }
  key = _activeKey(userId)
  activeRedisDB.hmset(key, user)

def changeUsername(userId, newUsername):
  key = _activeKey(userId)
  activeRedisDB.hset(key, 'username', newUsername)

def changeEmail(userId, newEmail):
  key = _activeKey(userId)
  activeRedisDB.hset(key, 'email', newEmail)

def changePasswordHash(userId, newPasswordHash):
  key = _activeKey(userId)
  activeRedisDB.hset(key, 'passwordHash', newPasswordHash)

def removeUser(userId):
  key = _activeKey(userId)
  activeRedisDB.delete(key)

def getUserInfo(userId):
  key = _activeKey(userId)
  return activeRedisDB.hgetall(key)

def changeUserProfilePic(userId, fileId):
  key = _activeKey(userId)
  activeRedisDB.hset(key, 'profilePicFileId', fileId)
  activeRedisDB.hset(key, 'hasProfilePic', True)


#friends
def getFriends(userId):
  key = _activeKey(userId)
  return activeRedisDB.lrange(key+friends_list_key, 0, -1)

def addFriend(userId, friendId):
  key = _activeKey(userId)
  return activeRedisDB.lpush(key+friends_list_key, friendId)

def removeFriend(userId, friendId):
  key = _activeKey(userId)
  pass



#boards
#-admin
def getAdminBoards(userId):
  key = _activeKey(userId)
  return activeRedisDB.lrange(key+admin_boards_list_key, 0, -1)

def addAdminBoard(userId, boardId):
  key = _activeKey(userId)
  activeRedisDB.lpush(key+admin_boards_list_key, boardId)
  
def removeAdminBoard(userId, boardId):
  key = _activeKey(userId)
  activeRedisDB.lrem(key+admin_boards_list_key, 0, boardId)

#-mods
def getModBoards(userId):
  key = _activeKey(userId)
  return activeRedisDB.lrange(key+mod_boards_list_key, 0, -1)

def addModBoard(userId, boardId):
  key = _activeKey(userId)
  activeRedisDB.lpush(key+mod_boards_list_key, boardId)

def removeModBoard(userId, boardId):
  key = _activeKey(userId)
  activeRedisDB.lrem(key+mod_boards_list_key, 0, boardId)

#-private
def getPrivateBoards(userId):
  key = _activeKey(userId)
  return activeRedisDB.lrange(key+private_boards_list_key, 0, -1)

def addPrivateBoard(userId, boardId):
  key = _activeKey(userId)
  activeRedisDB.lpush(key+private_boards_list_key, boardId)

def removePrivateBoard(userId, boardId):
  key = _activeKey(userId)
  activeRedisDB.lrem(key+private_boards_list_key, 0, boardId)  


#formats a key
def _activeKey(userId):
  return keyFormat.format(userId)
