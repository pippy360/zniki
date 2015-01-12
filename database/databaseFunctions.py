import postDatabase
import threadDatabase
import boardDatabase

def createBoard(name):
	boardDatabase.incrementBoardCount()
	boardId = boardDatabase.getBoardCount()
	boardDatabase.addBoard(boardId, name)
	return boardId

def createThread(boardId, subject, message, attachedFileId, creatorId=None):
	threadId = boardDatabase.incrementBoardThreadCount(boardId)#TODO: replace with get threadId()
	threadId = boardDatabase.getBoardThreadCount(boardId)#TODO: replace with get threadId()
	threadDatabase.addNewThread(boardId, threadId, subject)
	boardDatabase.addThreadIdToThreadList(boardId, threadId)
	firstPostId = createPost(boardId, threadId, message, attachedFileId, creatorId)
	return threadId

def createPost(boardId, threadId, message, attachedFileId=None, creatorId=None):
	threadDatabase.incrementThreadPostCount(boardId, threadId)
	postId = threadDatabase.getThreadPostCount(boardId, threadId)
	threadDatabase.addPostIdToPostList(boardId, threadId, postId)
	postDatabase.addPost(boardId, threadId, postId, message, attachedFileId, creatorId)
	#TODO: this could do with better explaining, 
	#there's no reason this should be in the board database
	boardDatabase.moveThreadToFront(boardId, threadId)
	return postId

def getPagePreview(boardId, page):
	board = boardDatabase.getBoardInfo(boardId)
	board['threads'] = [] 
	threadIdList = boardDatabase.getBoardThreadListRange(boardId, 0, 4)
	for threadId in threadIdList:
		board['threads'].append(getThreadPreview(boardId, threadId))

	return board

def getThread(boardId, threadId):
	thread = threadDatabase.getThreadInfo(boardId, threadId)
	thread['posts'] = getAllPosts(boardId, threadId)
	return thread


def getThreadPreview(boardId, threadId):
	thread = threadDatabase.getThreadInfo(boardId, threadId)
	thread['posts'] = []
	thread['posts'].extend( getPostsRange(boardId, threadId, 0, 0) )
	thread['posts'].extend( getPostsRange(boardId, threadId, -5, -1) )
	return thread

def getPost(boardId, threadId, postId):
	return postDatabase.getPost(boardId, threadId, postId)

def getAllPosts(boardId, threadId):
	return getPostsRange(boardId, threadId, 0, -1)

def getPostsRange(boardId, threadId, start, end):
	tempList = threadDatabase.getThreadPostListRange(boardId, threadId, start, end)	
	result = []
	for postId in tempList:
		result.append(postDatabase.getPost(boardId, threadId, postId))

	return result