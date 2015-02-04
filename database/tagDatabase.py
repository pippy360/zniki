import redis

keyFormat = 'keyword_{0}'
tagRedisDB = redis.StrictRedis( '127.0.0.1', 6379 )

def addTagsToProject( projectId, tagsList ):
  if isinstance( tagsList, basestring):#if a string is passed in convert it to a list of one element
    tagsList = [ tagsList ]

  for tag in tagsList:
    key = _tagKey(tag)
    tagRedisDB.sadd( key, projectId )

def getIntersection( keywords ):
  fixed = []
  for keyword in keywords:
    key = _tagKey( keyword )
    fixed.append( key )

  return tagRedisDB.sinter( fixed )

def removeFileIdFromTag( projectId, tag ):
  #TODO: what happens if it doesn't exist ??
  key = _tagKey(tag)
  keywordRedisDB.srem( key, projectId )

def getMatchingProjects( keyword ):
  key = _tagKey(keyword)
  return keywordRedisDB.smembers( key )

def _tagKey(tag):
  return keyFormat.format(tag)
