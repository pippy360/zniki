import postDatabase
import threadDatabase
import boardDatabase
import fileDatabase

threadsPerPage = 5

def createBoard(name):
	boardDatabase.incrementBoardCount()
	boardId = boardDatabase.getBoardCount()
	boardDatabase.addBoard(boardId, name)
	return boardId

def createThread(boardId, subject, message, attachedFileId, creatorId=None):
	#TODO: replace with get threadId()
	threadId = boardDatabase.incrementBoardThreadCount(boardId)
	#TODO: replace with get threadId()
	threadId = str(boardDatabase.getBoardThreadCount(boardId))
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

#FIXME: this function should not be in the databaseFunctions, it's a frontend thing
def genPageButtons(boardId, pageNo):
	#see how many buttons there shoud be and active the active one !
	#calc the number of pages !!!
	threadsNo = boardDatabase.getBoardThreadCount(boardId)
	pages = (threadsNo/threadsPerPage)+1;
	result = []
	for x in range(pages):
		if int(x+1) == int(pageNo):
			result.append({'number':str(x+1), 'active':str(True) })
		else:
			result.append({'number':str(x+1), 'active':str(False)})
	return result

def addFileToDatabase(boardId, threadId, postId, fileInfo, creatorIP):
	return fileDatabase.addFile(boardId, threadId, postId, postId, fileInfo, creatorIP)

#FIXME: this function should MAYBE not be in the databaseFunctions, it's a frontend thing
def getPagePreview(boardId, pageNo):
	board = boardDatabase.getBoardInfo(boardId)
	board['threads'] = [] 
	threadIdList = boardDatabase.getBoardThreadListRange(boardId, 
		(pageNo-1)*(threadsPerPage), (pageNo)*(threadsPerPage)-1)
	for threadId in threadIdList:
		board['threads'].append(getThreadPreview(boardId, threadId))

	return board

def getBoardName(boardId):
	return boardDatabase.getBoardName(boardId)

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
