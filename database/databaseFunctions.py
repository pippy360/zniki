from sets import Set
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

def createBoard(name, isPrivate, adminId):
	globalDatabase.incrementGlobalCount()
	boardId = globalDatabase.getGlobalCount()
	globalDatabase.addBoardIdToBoardList(boardId)
	#add it to the admins board list
	userDatabase.addAdminBoard(adminId, boardId)

	if not isPrivate:
		globalDatabase.addBoardIdToPublicBoardList(boardId)

	boardDatabase.addBoard(boardId, name, isPrivate, adminId)
	return boardId

def getAllBoards():
	result = []
	for boardId in globalDatabase.getBoardList():
		result.append(getBoardInfo(boardId))

	return result

#returns the id of the thread and the id of the OP's post
def createThread(boardId, subject, message, attachedFileId, creatorIP=None, creatorId=None):
	threadId = boardDatabase.incrementBoardThreadCount(boardId)
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
	board = boardDatabase.getBoardInfo(boardId)
	board['boardId'] = boardId
	board['modsList'] = boardDatabase.getModsIdsList(boardId)
	board['usersList'] = boardDatabase.getAllBoardUsers(boardId)
	return board

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
	#convert the creatorId into a name (either username or anonymouse)
	userId = postInfo.get('creatorId');
	if userId == 'NULL':
		postInfo['creatorName'] = 'Anonymous'
	else:
		userData = userDatabase.getUserInfo(userId)
		if userData == {}:
			postInfo['creatorName'] = 'Deleted'
		else:
			postInfo['creatorName'] = userData['username']

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

def getPostsRange(boardId, threadId, start, end):
	tempList = threadDatabase.getThreadPostListRange(boardId, threadId, start, end)	
	result = []
	for postId in tempList:
		result.append(getPost(boardId, postId))

	return result

def addModToBoard(newModId, boardId):
	boardInfo = getBoardInfo(boardId)
	if newModId in boardInfo['modsList']:
		return

	if not newModId in boardInfo['usersList']:
		addUserToBoard(newModId, boardId)

	boardDatabase.addBoardMod(boardId, newModId)
	userDatabase.addModBoard(newModId, boardId)

def addUserToBoard(newUserId, boardId):
	boardInfo = getBoardInfo(boardId)
	if newUserId in boardInfo['usersList']:
		return

	boardDatabase.addBoardUser(boardId, newUserId)
	userDatabase.addPrivateBoard(newUserId, boardId)

def getAllBoardMods(boardId):
	result = []
	modIdsList = boardDatabase.getModsIdsList(boardId)
	for modId in modIdsList:
		mod = boardDatabase.getModsPermissions(boardId, modId)
		mod['userInfo'] = getUserInfo(modId)
		result.append(mod)

	return result

def getAllBoardUsers(boardId):
	result = []
	userIdsList = boardDatabase.getAllBoardUsers(boardId)
	for userId in userIdsList:
		result.append(getUserInfo(userId))

	return result

def changeBoardName(boardId, newName):
	boardDatabase.changeBoardName(boardId, newName)

def changeBoardPassword(boardId, newName):
	boardDatabase.changeBoardPassword(boardId, newName)

def getModsPermissions(boardId, modId):
	return boardDatabase.getModsPermissions(boardId, modId)

def removeModFromBoard(boardId, modId):
	boardDatabase.removeBoardMod(boardId, modId)
	userDatabase.removeModBoard(modId, boardId)

def removeUserFromBoard(boardId, userId):
	removeModFromBoard(boardId, userId)
	boardDatabase.removeBoardUser(boardId, userId)
	userDatabase.removePrivateBoard(userId, boardId)

def removeThread(boardId, threadId):
	pass

def removePost(boardId, threadId, postId):
	postDatabase.removePost(boardId, postId)
	threadDatabase.removePostIdFromPostList(boardId, threadId, postId)

def setModPermissions(boardId, modId, addPeopleP=False,
						kickUserP=False, deletePostP=False):
	boardDatabase.setModPermissions(boardId, modId, addPeopleP, 
						kickUserP, deletePostP)

def makeBoardPublic(boardId):
	boardDatabase.makeBoardPublic(boardId)
	globalDatabase.addBoardIdToPublicBoardList(boardId)

def makeBoardPrivate(boardId):
	boardDatabase.makeBoardPrivate(boardId)
	globalDatabase.removeBoardIdFromPublicBoardList(boardId)

def removeBoard(boardId):
	boardInfo = getBoardInfo(boardId)
	for userId in boardInfo['usersList']:
		removeUserFromBoard(boardId, userId)

	boardDatabase.removeBoard(boardId)
	globalDatabase.removeBoardIdFromBoardList(boardId)
	print 'boardInfo[isPrivate]'
	print boardInfo['isPrivate']

	if boardInfo['isPrivate'] == 'False':
		globalDatabase.removeBoardIdFromPublicBoardList(boardId)

	#now remove from admin
	userDatabase.removeAdminBoard(boardInfo['adminId'], boardId)
	removeUserFromBoard(boardId, boardInfo['adminId'])

	#now delete the board key !!
	boardDatabase.removeBoard(boardId)

def removeThread(boardId, threadId):
	boardDatabase.removeThreadIdFromThreadList(boardId, threadId)
	threadDatabase.removeThread(boardId, threadId)
	#FIXME: make sure all posts are deleted

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

#todo: return a dict here instead !!
#returns 0 on success, 
#returns -1 if the username/email doens't exist
#returns -2 if you guys are already friends
#returns -3 if you're trying to add yourself
def addFriend(userId, friendStringId):
	#make sure the username/email exists
	friendId = usernameDatabase.getUsernameUserId(friendStringId)
	if friendId == None: 
		friendId = emailDatabase.getEmailUserId(friendStringId)
		if friendId == None:
			return -1
	elif friendId in userDatabase.getFriends(userId):
		return -2
	elif friendId == userId:
		return -3

	userDatabase.addFriend(userId, friendId)
	return 0

def getFriends(userId):
	result = []
	for tempId in userDatabase.getFriends(userId):
		result.append(userDatabase.getUserInfo(tempId))

	return result

def changePasswordHash(userId, newPasswordHash):
	userDatabase.changePasswordHash(userId, newPasswordHash)

def getUsernameUserId(username):
	return usernameDatabase.getUsernameUserId(username)

def getUserInfo(userId):
	result = userDatabase.getUserInfo(userId)
	result['userId'] = userId
	return result

def getUserIdFromIdString(idString):
	userId = usernameDatabase.getUsernameUserId(idString)
	if userId == None: 
		userId = emailDatabase.getEmailUserId(idString)
		if userId == None:
			return None
	return userId	

def getUserInfoFromIdString(idString):
	return getUserInfo(getUserIdFromIdString(idString))

def getEmailUserId(email):
	return emailDatabase.getEmailUserId(email)

def getProjectListRange(start, end):
	return globalDatabase.getProjectListRange(start, end)

def getProjectInfo(projectId):
	return projectDatabase.getProjectInfo(projectId)

def getProjectCount():
	return globalDatabase.getProjectCount()

def getAllUsernames():
	return usernameDatabase.getAllUsernames()

def getAllEmails():
	return emailDatabase.getAllEmails()

def changeUserProfilePic(userId, fileId):
	userDatabase.changeUserProfilePic(userId, fileId)

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

#TODO:FIXME:
def removeUser(userId):
	userInfo = getUserInfo(userId)
	usernameDatabase.removeUsername(userInfo['username'])
	emailDatabase.removeEmail(userInfo['email'])
	userDatabase.removeUser(userId)
	#go through the lists a user is part of and remove him


######      #      #####   #######       #####   #######  #     # 
#     #    # #    #     #  #            #     #  #        ##    # 
#     #   #   #   #        #            #        #        # #   # 
######   #     #  #  ####  #####        #  ####  #####    #  #  # 
#        #######  #     #  #            #     #  #        #   # # 
#        #     #  #     #  #            #     #  #        #    ## 
#        #     #   #####   #######       #####   #######  #     # 


#get the board info along with the OP post all the threads in that board
def getBoardInfoPreview(boardId, currentUserId=None):
	threadIds = boardDatabase.getBoardThreadListAll(boardId)
	threads = []
	for threadId in threadIds:
		thread = threadDatabase.getThreadInfo(boardId, threadId)
		thread['posts'] = getPostsRange(boardId, threadId, 0, 0)
		threads.append(thread)

	board = getBoardInfo(boardId)

	board['boardId'] = boardId
	board['threads'] = threads
	board['userSettings'] = getBoardUserSettings(boardId, currentUserId)

	return board

def getBoardUserSettings(boardId, currentUserId=None):
	result = {}
	board = getBoardInfo(boardId)
	if currentUserId != None:
		if currentUserId == board['adminId']:
			result['role'] = 'Admin'
		elif currentUserId in board['modsList']:
			result['role']  = 'Mod'
			result['perms'] =  getModsPermissions(boardId, currentUserId)
		else:
			result['role'] = 'User'
	else:
		result['role'] = 'Anon'

	return result

def getAllBoardsPreview(boardList, userId=None):
	if boardList == None:
		return []

	result = []
	for boardId in boardList:
		result.append(getBoardInfoPreview(boardId, userId))
	return result

def getAllPublicBoardsPreview():
	boardList = globalDatabase.getPublicBoardList()
	return getAllBoardsPreview(boardList)

def getIndexPageInfoForUser(userId):
	boardList  = set(globalDatabase.getPublicBoardList())
	boardList |= set(userDatabase.getAdminBoards(userId))
	boardList |= set(userDatabase.getPrivateBoards(userId))
	
	return getAllBoardsPreview(boardList, userId)