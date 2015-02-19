import postDatabase
import threadDatabase
import boardDatabase
import fileDatabase
import globalDatabase
import userDatabase
import usernameDatabase
import emailDatabase

def getNewId():
	globalDatabase.incrementGlobalCount()
	return str(globalDatabase.getGlobalCount())

def createBoard(name):
	globalDatabase.incrementGlobalCount()
	boardId = globalDatabase.getGlobalCount()
	globalDatabase.addBoardIdToBoardList(boardId)
	boardDatabase.addBoard(boardId, name)
	return boardId

def getAllBoards():
	result = []
	for boardId in globalDatabase.getBoardList():
		result.append(boardDatabase.getBoardInfo(boardId))

	return result

#returns the id of the thread and the id of the OP's post
def createThread(boardId, subject, message, attachedFileId, creatorIP=None, creatorId=None):
	#TODO: replace with get threadId()
	threadId = str(boardDatabase.getBoardThreadCount(boardId))
	threadDatabase.addNewThread(boardId, threadId, subject)
	boardDatabase.addThreadIdToThreadList(boardId, threadId)
	firstPostId = createPost(boardId, threadId, message, attachedFileId, creatorIP, creatorId)
	return threadId

def createPost(boardId, threadId, message, attachedFileId=None, creatorIP=None, creatorId=None):
	boardDatabase.incrementBoardPostCount(boardId)
	postId = str(boardDatabase.getBoardPostCount(boardId))
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


#     #   #####   #######  ######  
#     #  #     #  #        #     # 
#     #  #        #        #     # 
#     #   #####   #####    ######  
#     #        #  #        #   #   
#     #  #     #  #        #    #  
 #####    #####   #######  #     # 


#returns -1 if username is already taken
def changeUsername(userId, newUsername):
	userInfo = userDatabase.getUserInfo(userId)
	if not usernameDatabase.getUsernameUserId(newUsername) == None:
		return -1
	
	usernameDatabase.removeUsername( userInfo['username'] )
	userDatabase.changeUsername(userId, newUsername)
	usernameDatabase.addUsername(newUsername, userId)

#returns -1 if email is already taken
def changeEmail(userId, newEmail):
	userInfo = userDatabase.getUserInfo(userId)
	if not emailDatabase.getEmailUserId(newEmail) == None:
		return -1

	emailDatabase.removeEmail( userInfo['email'] )
	userDatabase.changeEmail(userId, newEmail)
	emailDatabase.addEmail(newEmail, userId)

def changePasswordHash(userId, newPasswordHash):
	userDatabase.changePasswordHash(userId, newPasswordHash)

def getUsernameUserId(username):
	return usernameDatabase.getUsernameUserId(username)

def getUserInfo(userId):
	return userDatabase.getUserInfo(userId)

def getUserInfo(userId):
	return userDatabase.getUserInfo(userId)

def getEmailUserId(email):
	return emailDatabase.getEmailUserId(email)

def getProjectListRange(start, end):
	return globalDatabase.getProjectListRange(start, end)

def getProjectInfo(projectId):
	return projectDatabase.getProjectInfo(projectId)

def getProjectCount():
	return globalDatabase.getProjectCount()

#TODO: make this return status with the userId
#return 0 if success, -1 if username already exists, -2 if email already exists
def addUser(email, username, passwordHash, reputation):
	#make sure the username and email don't match existing ones
	if not usernameDatabase.getUsernameUserId(username) == None:
		return -1
		
	if not emailDatabase.getEmailUserId(email) 			== None:
		return -2

	userId = getNewId()
	emailDatabase.addEmail(email, userId)
	usernameDatabase.addUsername(username, userId)
	userDatabase.addUser(userId, email, username, passwordHash, False, reputation)
	return 0

def getAllPendingUsers():
	result = []
	pendingUsersList = pendingUserDatabase.getAllPendingUsers()
	for userId in pendingUsersList:
		temp = pendingUserDatabase.getUserInfo(userId)
		temp['userId'] = userId
		result.append( temp )

	return result
