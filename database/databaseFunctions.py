import postDatabase
import threadDatabase
import boardDatabase
import fileDatabase
import globalDatabase

def createBoard(name):
	globalDatabase.incrementBoardCount()
	boardId = globalDatabase.getBoardCount()
	boardDatabase.addBoard(boardId, name)
	return boardId

#returns the id of the thread and the id of the OP's post
def createThread(boardId, subject, message, attachedFileId, creatorIP=None, creatorId=None):
	#TODO: replace with get threadId()
	threadId = boardDatabase.incrementBoardThreadCount(boardId)
	#TODO: replace with get threadId()
	threadId = str(boardDatabase.getBoardThreadCount(boardId))
	threadDatabase.addNewThread(boardId, threadId, subject)
	boardDatabase.addThreadIdToThreadList(boardId, threadId)
	firstPostId = createPost(boardId, threadId, message, attachedFileId, creatorIP, creatorId)
	return threadId

def createPost(boardId, threadId, message, attachedFileId=None, creatorIP=None, creatorId=None):
	boardDatabase.incrementBoardPostCount(boardId)
	postId = boardDatabase.getBoardPostCount(boardId)
	threadDatabase.addPostIdToPostList(boardId, threadId, postId)
	postDatabase.addPost(boardId, postId, message, attachedFileId, creatorIP, creatorId)
	boardDatabase.moveThreadToFront(boardId, threadId)
	return postId

def getBoardThreadCount(boardId):
	return boardDatabase.getBoardThreadCount(boardId)

def getBoardInfo(boardId):
	return boardDatabase.getBoardInfo(boardId)

def addFileToDatabase(fileInfo, creatorIP):
	globalDatabase.incrementFileCount()
	fileId = globalDatabase.getFileCount()
	fileDatabase.addFile(fileId, fileInfo, creatorIP)
	return fileId

def getFileInfo(fileId):
	return fileDatabase.getFileInfo(fileId)

def getBoardName(boardId):
	return boardDatabase.getBoardName(boardId)

def getThread(boardId, threadId):
	thread = threadDatabase.getThreadInfo(boardId, threadId)
	if thread == {} or thread == None:
		return None
	thread['posts'] = getAllPosts(boardId, threadId)
	#make sure there is at least one post 
	return thread

def getPost(boardId, postId):
	#also get the file info
	postInfo = postDatabase.getPost(boardId, postId)
	fileId = postInfo['attachedFileId']
	if fileId != "" and fileId != None and fileId != 'NULL':
		fileInfo = fileDatabase.getFileInfo(fileId)
		postInfo['fileinfo'] = fileInfo

	return postInfo

def getAllPosts(boardId, threadId):
	return getPostsRange(boardId, threadId, 0, -1)

def getBoardThreadListRange(boardId, start, end):
	return boardDatabase.getBoardThreadListRange(boardId, start, end)

def getThreadInfo(boardId, threadId):
	return threadDatabase.getThreadInfo(boardId, threadId)

def getBoardInfo(boardId):
	return boardDatabase.getBoardInfo(boardId)

def getPostsRange(boardId, threadId, start, end):
	tempList = threadDatabase.getThreadPostListRange(boardId, threadId, start, end)	
	result = []
	for postId in tempList:
		result.append(getPost(boardId, postId))

	return result
