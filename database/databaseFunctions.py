import postDatabase
import threadDatabase
import boardDatabase
import fileDatabase
import globalDatabase

threadsPerPage = 5

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
	print 'done the first one'
	return threadId

def createPost(boardId, threadId, message, attachedFileId=None, creatorIP=None, creatorId=None):
	boardDatabase.incrementBoardPostCount(boardId)
	postId = boardDatabase.getBoardPostCount(boardId)
	print 'creating post with id'
	print attachedFileId
	print postId
	threadDatabase.addPostIdToPostList(boardId, threadId, postId)
	postDatabase.addPost(boardId, postId, message, attachedFileId, creatorIP, creatorId)
	boardDatabase.moveThreadToFront(boardId, threadId)
	return postId

#FIXME: this function should not be in the databaseFunctions, it's a frontend thing
def genPageButtons(boardId, pageNo):
	#see how many buttons there shoud be and active the active one !
	#calc the number of pages !!!
	threadsNo = boardDatabase.getBoardThreadCount(boardId)
	pages = (threadsNo/threadsPerPage)+1
	result = []
	for x in range(pages):
		if int(x+1) == int(pageNo):
			result.append({'number':str(x+1), 'active':str(True) })
		else:
			result.append({'number':str(x+1), 'active':str(False)})
	return result

def addFileToDatabase(fileInfo, creatorIP):
	globalDatabase.incrementFileCount()
	fileId = globalDatabase.getFileCount()
	fileDatabase.addFile(fileId, fileInfo, creatorIP)
	print 'file added'
	print fileId
	return fileId

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

def getPost(boardId, postId):
	#also get the file info
	postInfo = postDatabase.getPost(boardId, postId)
	fileId = postInfo['attachedFileId']
	if fileId != "" and fileId != None and fileId != 'NULL':
		fileInfo = fileDatabase.getFileInfo(fileId)
		postInfo['fileinfo'] = fileInfo

	print 'postInfo'
	print postInfo
	return postInfo

def getAllPosts(boardId, threadId):
	return getPostsRange(boardId, threadId, 0, -1)

def getPostsRange(boardId, threadId, start, end):
	tempList = threadDatabase.getThreadPostListRange(boardId, threadId, start, end)	
	result = []
	for postId in tempList:
		result.append(getPost(boardId, postId))

	return result
