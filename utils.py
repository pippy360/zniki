import re
from database import databaseFunctions


def isUserInBoardUserList(currentUser, boardId):
	boardInfo = databaseFunctions.getBoardInfo(boardId)
	if boardInfo['isPrivate'] != 'True':
		return True

	if not currentUser.is_authenticated():
		return False

	userId = currentUser.get_id()
	if userId == boardInfo['adminId']:
		return True
	elif userId in boardInfo['usersList']:
		return True
	else:
		return False

def canAddUser(currentUser, boardId):
	if not currentUser.is_authenticated():
		return False

	boardInfo = databaseFunctions.getBoardInfo(boardId)
	#check if he's the admin
	#then check if he's a mod with the permission
	pass

def canKickUser(currentUser, boardId):
	if not currentUser.is_authenticated():
		return False

	boardInfo = databaseFunctions.getBoardInfo(boardId)
	#check if he's the admin
	pass

def canRemovePost(currentUser, boardId):
	if not currentUser.is_authenticated():
		return False

	boardInfo = databaseFunctions.getBoardInfo(boardId)
	#check if he's the admin
	pass


#all the isValid* functions return a status dict
#status = {
#	'isValid': False,
#	'reason' : '',#Reason why it is not valid 
#}
MAX_EMAIL_SIZE 	  = 100
MIN_EMAIL_SIZE 	  = 3
MAX_PASSWORD_SIZE = 100
MIN_PASSWORD_SIZE = 4
MAX_USERNAME_SIZE = 30
MIN_USERNAME_SIZE = 3

def isValidEmail(email):
	if email == None:
		return {'isValid':False, 'reason':'Invalid Email'}

	email = (str(email)).lower()
	if len(email) > MAX_EMAIL_SIZE:
		return {'isValid':False, 'reason':'Email was more than '+str(MAX_EMAIL_SIZE)+' characters'}

	if len(email) < MIN_EMAIL_SIZE:
		return {'isValid':False, 'reason':'Email was lass than '+str(MIN_EMAIL_SIZE)+' characters'}

	if re.match(r"[^@]+@[^@]+\.[^@]+", email) != None:
		return {'isValid':True, 'reason':''}
	else:
		return {'isValid':False, 'reason':'Invalid Email'}


def isValidUsername(username):
	if username == None:
		return {'isValid':False, 'reason':'Invalid Username'}

	username = (str(username)).lower()
	if len(username) > MAX_USERNAME_SIZE:
		return {'isValid':False, 'reason':'Username was more than '+str(MAX_USERNAME_SIZE)+' characters'}

	if len(username) < MIN_USERNAME_SIZE:
		return {'isValid':False, 'reason':'Username was lass than '+str(MIN_USERNAME_SIZE)+' characters'}

	if re.match("^[a-zA-Z0-9_.-]+$", username) != None:
		return {'isValid':True, 'reason':''}
	else:
		return {'isValid':False, 'reason':'Invalid Password'}


def isValidPassword(password):
	if password == None:
		return {'isValid':False, 'reason':'Invalid Password'}

	password = str(password)
	if len(password) > MAX_PASSWORD_SIZE:
		return {'isValid':False, 'reason':'Password was more than '+str(MAX_PASSWORD_SIZE)+' characters'}

	if len(password) < MIN_PASSWORD_SIZE:
		return {'isValid':False, 'reason':'Password was lass than '+str(MIN_PASSWORD_SIZE)+' characters'}

	if re.match(r'[A-Za-z0-9@#$%^&+=]{3,}', password) != None:
		return {'isValid':True, 'reason':''}
	else:
		return {'isValid':False, 'reason':'Invalid Password'}

#
#Groups and threads
#
MAX_GROUP_NAME_SIZE = 60
MIN_GROUP_NAME_SIZE = 4
MAX_SUBJECT_SIZE = 60
MIN_SUBJECT_SIZE = 4
MAX_COMMENT_SIZE = 400
MIN_COMMENT_SIZE = 1

def isValidGroupName(groupName):
	if groupName == None:
		return {'isValid':False, 'reason':'Invalid Group Name'}

	groupName = str(groupName)
	if len(groupName) > MAX_GROUP_NAME_SIZE:
		return {'isValid':False, 'reason':'Group name was more than '+str(MAX_GROUP_NAME_SIZE)+' characters'}

	if len(groupName) < MIN_GROUP_NAME_SIZE:
		return {'isValid':False, 'reason':'Group name was lass than '+str(MIN_GROUP_NAME_SIZE)+' characters'}

	if re.match(r'[A-Za-z0-9@#$%^&+= ]{3,}', groupName) != None:
		return {'isValid':True, 'reason':''}
	else:
		return {'isValid':False, 'reason':'Invalid Group Name'}

def isValidThreadSubject(subject):
	if subject == None:
		return {'isValid':False, 'reason':'Invalid Subject'}

	subject = str(subject)
	if len(subject) > MAX_SUBJECT_SIZE:
		return {'isValid':False, 'reason':'Subject was more than '+str(MAX_SUBJECT_SIZE)+' characters'}

	if len(subject) < MIN_SUBJECT_SIZE:
		return {'isValid':False, 'reason':'Subject was lass than '+str(MIN_SUBJECT_SIZE)+' characters'}

	if re.match(r'[A-Za-z0-9@#$%^&+= ]{3,}', subject) != None:
		return {'isValid':True, 'reason':''}
	else:
		return {'isValid':False, 'reason':'Invalid Subject'}

def isValidThreadComment(comment):
	if comment == None:
		return {'isValid':False, 'reason':'Invalid Comment'}

	comment = str(comment)
	if len(comment) > MAX_COMMENT_SIZE:
		return {'isValid':False, 'reason':'Comment was more than '+str(MAX_COMMENT_SIZE)+' characters'}

	if len(comment) < MIN_COMMENT_SIZE:
		return {'isValid':False, 'reason':'Comment was lass than '+str(MIN_COMMENT_SIZE)+' characters'}

	return {'isValid':True, 'reason':''}
