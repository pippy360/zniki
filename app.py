from database import databaseFunctions
import redis
import filesAPI
import thumbnailGenerator
from flask import Flask, render_template, request, send_file, redirect, url_for
from flask.ext import login
import loginLogic
import utils
app = Flask(__name__)
app.config['SECRET_KEY'] = '8p3234p3d'


#postRedisDB = redis.StrictRedis( '127.0.0.1', 6379 )
#postRedisDB.flushall()
#
#fileData = {
#		'originalFilename': '98XY8luppNRc.jpg',
#		'hash':     'hash',
#		'filename':     '98XY8luppNRc.jpg',
#		'fileLocation': './static/storage/',
#		'extension':    'extension',
#		'mimetype':     '',
#		'metadata': 'metadata',
#		'type':     'image'
#	}
#boardId 	= databaseFunctions.createBoard("Home")
#fileId 	 	= databaseFunctions.addFileToDatabase(fileData, "192.0.0.1")
#threadId 	= databaseFunctions.createThread(boardId, "I love NY", "hey check out my new thread", fileId)
#boardId = databaseFunctions.createBoard("Jets and Cars")
#boardId = databaseFunctions.createBoard("School")
#boardId = databaseFunctions.createBoard("Dogs and Cats")


@app.route("/")
@app.route("/home")
@app.route("/home/")
@app.route("/index.html")
def showIndex():
	errors = []
	if request.args.get('error') != None:
		errors = [{'message':request.args.get('error'),'class':'bg-danger'}]
	if request.args.get('success') != None:
		errors = [{'message':request.args.get('success'),'class':'bg-success'}]
	
	if login.current_user.is_authenticated():
		boardList = databaseFunctions.getIndexPageInfoForUser(login.current_user.userId)
	else:
		boardList = databaseFunctions.getAllPublicBoardsPreview()

	boardList = sorted(boardList, key=lambda board: board['name'])

	if request.args.get('error') != None:
		errors = [{'message':request.args.get('error'),'class':'bg-danger'}]

	return render_template("index.html", errors=errors, boardList=boardList)

#TODO: remove
#@app.route('/baseLayoutTest')
#def baseTest():
#	return render_template("baseLayout.html",
#		errors=[{'message':'something here', 'class':'bg-danger'}])

@app.route('/thumb')
def thumb():
	return thumbnailGenerator.handleThumbnailRequest(request)

 #####                              
#     # #####   ####  #    # #####  
#       #    # #    # #    # #    # 
#  #### #    # #    # #    # #    # 
#     # #####  #    # #    # #####  
#     # #   #  #    # #    # #      
 #####  #    #  ####   ####  #      

@app.route('/createNewGroup')
@login.login_required
def createNewGroupPage():
	errors = []
	if request.args.get('error') != None:
		errors = [{'message':request.args.get('error'),'class':'bg-danger'}]
	if request.args.get('success') != None:
		errors = [{'message':request.args.get('success'),'class':'bg-success'}]
	
	return render_template('createNewGroup.html', errors=errors)

@app.route('/createNewGroupSubmit', methods=['POST'])
@login.login_required
def createNewGroupSubmitPage():
	groupName = request.form.get("input_groupName")
	status = utils.isValidGroupName(groupName)
	if not status['isValid']:
		return redirect('/createNewGroup?error=Error: '+status['reason'])

	isPrivate = request.form.get("privateGroup")
	isPrivate = (isPrivate == 'True')

	#create a new board
	databaseFunctions.createBoard(groupName, isPrivate, login.current_user.userId)
	return redirect('/')

@app.route('/<boardId>/addUsersSubmit', methods=['POST'])
@login.login_required
def addUsersSubmitPage(boardId):
	#check if the user is a part of this board
	if not utils.canAddUser(login.current_user, boardId):
		return redirect('/?error=Error: You do not have permission to add users')

	newUser = request.form.get("input_newUser")	
	if newUser == None or newUser == '':
		return redirect('/'+boardId+'/settings?error=Error: Invalid username or email address ')

	newUser = newUser.lower()
	newUserId = databaseFunctions.getUserIdFromIdString(newUser)
	if newUserId == None:
		return redirect('/'+boardId+'/settings?error=Error: The username "'+newUser+'" didn\'t match any users')
	elif newUserId == login.current_user.get_id():
		return redirect('/'+boardId+'/settings?error=Error: You can\'t add yourself')

	boardInfo = databaseFunctions.getBoardInfo(boardId)
	if boardInfo == None:
		return redirect('/'+boardId+'/settings?error=Error: Invalid board Id')
	elif newUserId == boardInfo['adminId']:
		return redirect('/'+boardId+'/settings?error=Error: You can\'t add the admin as a user') 
	elif newUserId in boardInfo['usersList']: 
		return redirect('/'+boardId+'/settings?error=Error: '+newUser+' is already a member of this group')
	
	if boardInfo['isPrivate'] == 'True':
		databaseFunctions.addUserToBoard(newUserId, boardId)
		return redirect('/'+boardId+'/settings?success=Success: user added')
	else:
		return redirect('/'+boardId+'/settings?error=Error: Not a private board')

	return redirect('/')

@app.route('/<boardId>/addModsSubmit', methods=['POST'])
@login.login_required
def addModsSubmitPage(boardId):
	#check if the user is a part of this board
	if not utils.isAdmin(login.current_user, boardId):
		return redirect('/?error=Error: You do not have permission to add users')

	newMod = request.form.get("input_newMod")

	if newMod == None or newMod == '':
		return redirect('/'+boardId+'/settings?error=Error: Invalid username or email address ')

	newMod = newMod.lower()
	newModId = databaseFunctions.getUserIdFromIdString(newMod)
	if newModId == None:
		return redirect('/'+boardId+'/settings?error=Error: The username "'+newMod+'" didn\'t match any users')
	elif newModId == login.current_user.get_id():
		return redirect('/'+boardId+'/settings?error=Error: you can\'t add yourself as a mod !')

	boardInfo = databaseFunctions.getBoardInfo(boardId)
	if boardInfo == None:
		return redirect('/'+boardId+'/settings?error=Error: Invalid board Id')

	databaseFunctions.addModToBoard(newModId, boardId)
	return redirect('/'+boardId+'/settings?success=Success: mod added')

@app.route('/<boardId>/changeGroupNameSubmit', methods=['post'])
@login.login_required
def changeGroupNameSubmitPage(boardId):
	#check if the user is a part of this board
	if not utils.isAdmin(login.current_user, boardId):
		return redirect('/?error=Error: You do not have permission to add users')

	boardInfo = databaseFunctions.getBoardInfo(boardId)
	newName   = request.form.get('input_newName')

	status = utils.isValidGroupName(newName)
	if not status['isValid']:
		return redirect('/'+boardId+'/settings?error=Error: '+status['reason'])

	if login.current_user.userId == boardInfo['adminId']:
		databaseFunctions.changeBoardName(boardId, newName)
		return redirect('/'+boardId+'/settings')
	else:
		return redirect('/')

@app.route('/<boardId>/changeGroupPasswordSubmit', methods=['post'])
@login.login_required
def changeGroupPasswordSubmitPage(boardId):
	#check if the user is a part of this board
	if not utils.isAdmin(login.current_user, boardId):
		return redirect('/?error=Error: You do not have permission to add users')

	boardInfo   = databaseFunctions.getBoardInfo(boardId)
	newPassword = request.form.get('input_newPassword')
	
	status = isValidPassword(newPassword)
	if not status['isValid']:
		return redirect('/'+boardId+'/settings?error=Error: '+status['reason'])

	if login.current_user.userId == boardInfo['adminId']:
		databaseFunctions.changeBoardPassword(boardId, newPassword)
		return redirect('/'+boardId+'/settings')
	else:
		return redirect('/')

@app.route('/<boardId>/changeModPerms/<modId>', methods=['post'])
@login.login_required
def changeModPermsPage(boardId, modId,errors=[]):
	#check if the user is a part of this board
	if not utils.isAdmin(login.current_user, boardId):
		return redirect('/?error=Error: You do not have permission to add users')

	addUsers 	= request.form.get('addUsers', False)
	kickUsers 	= request.form.get('kickUsers', False)
	removePosts = request.form.get('removePosts', False)
	databaseFunctions.setModPermissions(boardId, modId, addUsers, 
										kickUsers, removePosts)
	return redirect('/'+boardId+'/settings')

@app.route('/<boardId>/togglePrivate')
@login.login_required
def togglePrivatePage(boardId,errors=[]):
	#check if the user is a part of this board
	if not utils.isAdmin(login.current_user, boardId):
		return redirect('/?error=Error: You do not have permission to add users')

	boardInfo = databaseFunctions.getBoardInfo(boardId)
	if boardInfo['isPrivate'] == 'True':
		databaseFunctions.makeBoardPublic(boardId)
	else:
		databaseFunctions.makeBoardPrivate(boardId)
	return redirect('/'+boardId+'/settings')

@app.route('/<boardId>/settings')
@login.login_required
def settingsPage(boardId,errors=[]):
	#check if the user is a part of this board
	#NO NEED FOR THIS SECURITY CHECK, IT'S HANDLED BETTER BELOW
	#if not utils.isAdmin(login.current_user, boardId) 
	#		and not utils.isMod(login.current_user, boardId):
	#	return redirect('/?error=Error: You do not have permission to add users')

	if request.args.get('error') != None:
		errors = [{'message':request.args.get('error'),'class':'bg-danger'}]
	if request.args.get('success') != None:
		errors = [{'message':request.args.get('success'),'class':'bg-success'}]

	#make sure the user is the admin, render them the settings page
	boardInfo = databaseFunctions.getBoardInfo(boardId)
	if boardInfo == None:
		return redirect('/?error=Error: Invalid board Id')

	if login.current_user.userId == boardInfo['adminId']:
		return render_template('groupSettings.html', perm='Admin', boardId=boardId,
								boardInfo=boardInfo,
								mods =databaseFunctions.getAllBoardMods(boardId),
								users=databaseFunctions.getAllBoardUsers(boardId),
								errors=errors)

	elif login.current_user.userId in boardInfo['modsList']:
		modPerms = databaseFunctions.getModsPermissions(boardId, login.current_user.userId)
		return render_template('groupSettings.html', perm='Mod', boardId=boardId, 
								modPerms=modPerms,
								boardInfo=boardInfo,
								users=databaseFunctions.getAllBoardUsers(boardId),
								errors=errors)
	else:
		return redirect('/?error=Error: mods and admins ONLY')

@app.route('/<boardId>/removeMod/<modId>')
@login.login_required
def removeModPage(boardId, modId,errors=[]):
	#check if the user is a part of this board
	if not utils.isAdmin(login.current_user, boardId):
		return redirect('/?error=Error: You do not have permission to add users')

	databaseFunctions.removeModFromBoard(boardId, modId)
	return redirect('/'+boardId+'/settings?success=Success: Mod Removed')

@app.route('/<boardId>/kickUser/<userId>')
@login.login_required
def kickUserPage(boardId, userId,errors=[]):
	#check if the user is a part of this board
	if not utils.canKickUser(login.current_user, boardId):
		return redirect('/?error=Error: You do not have permission to add users')

	boardInfo = databaseFunctions.getBoardInfo(boardId)
	if login.current_user.get_id() != boardInfo['adminId'] and userId in boardInfo['modsList']:
		return redirect('/'+boardId+'/settings?error=Error: You can\' remove a user who is also a mod')

	databaseFunctions.removeUserFromBoard(boardId, userId)
	return redirect('/'+boardId+'/settings?success=Success: User Kicked')

@app.route('/<boardId>/deleteBoard')
@login.login_required
def deleteBoardPage(boardId):
	#check if the user is a part of this board
	if not utils.isAdmin(login.current_user, boardId):
		return redirect('/?error=Error: You do not have permission to add users')

	boardInfo = databaseFunctions.getBoardInfo(boardId)
	if login.current_user.userId == boardInfo['adminId']:
		databaseFunctions.removeBoard(boardId)
	
	return redirect('/')

#######                                         
   #     #    #  #####   ######    ##    #####  
   #     #    #  #    #  #        #  #   #    # 
   #     ######  #    #  #####   #    #  #    # 
   #     #    #  #####   #       ######  #    # 
   #     #    #  #   #   #       #    #  #    # 
   #     #    #  #    #  ######  #    #  #####  


@app.route('/<boardId>/createNewConv')
def createNewConversationPage(boardId):
	#check if the user is allowed to post to this board
	if not utils.isUserInBoardUserList(login.current_user, boardId):
		return redirect('/?error=Error: You do not have permission to view this page')

	errors = []
	if request.args.get('error') != None:
		errors = [{'message':request.args.get('error'),'class':'bg-danger'}]
	if request.args.get('success') != None:
		errors = [{'message':request.args.get('success'),'class':'bg-success'}]

	return render_template('createNewThread.html',boardId=boardId, errors=errors)

@app.route('/board/<boardId>/thread/<threadId>/deleteThread')
@login.login_required
def deleteThread(boardId, threadId):
	#check if the user is allowed to post to this board
	if not utils.canRemovePost(login.current_user, boardId):
		return redirect('/?error=Error: You do not have permission to view this page')

	databaseFunctions.removeThread(boardId, threadId)
	return redirect('/')

@app.route('/<boardId>/threadSubmit', methods=['POST'])
def threadSubmitPage(boardId):
	#check if the user is a part of this board	
	if not utils.isUserInBoardUserList(login.current_user, boardId):
		return redirect('/?error=Error: You do not have permission to view this page')

	threadId = ''
	subject = request.form.get('subject')
	comment = request.form.get('comment')

	#check if the user is a part of this board	
	if not utils.isUserInBoardUserList(login.current_user, boardId):
		return redirect('/?error=Error: You do not have permission to view this page')

	if subject != None and comment != None and request.files.get('photo') != None:
		
		if request.files.get('photo').filename == '':
			return redirect('/'+boardId+'/createNewConv?error=Error: No file uploaded.')

		status = utils.isValidThreadSubject(subject)
		if not status['isValid']:
			return redirect('/'+boardId+'/createNewConv?error=Error: '+status['reason'])

		status = utils.isValidThreadComment(comment)
		if not status['isValid']:
			return redirect('/'+boardId+'/createNewConv?error=Error: '+status['reason'])

		status = filesAPI.handleUploadFormSubmit(request.files['photo'])
		if not status['isValid']:
			return redirect('/'+boardId+'/createNewConv?error='+status['reason'])

		if login.current_user.is_authenticated():
			creatorId = login.current_user.userId
		else:
			creatorId = None

		fileId = databaseFunctions.addFileToDatabase(status['fileInfo'], "192.0.0.1")
		threadId = databaseFunctions.createThread(boardId, subject, 
												comment, fileId, creatorId=creatorId)
		return redirect('/')
	else:
		return redirect('/')#pass it here and pass on an error message


@app.route("/board/<boardId>/thread/<threadId>")
@app.route("/board/<boardId>/thread/<threadId>/")
def showThreadPage(boardId, threadId, errors=[]):
	#check if the user is a part of this board
	thread = databaseFunctions.getThread(boardId, threadId)
	if thread == None:
		return redirect('/?error=Error: Thread doesn\'t exist.')

	if not utils.isUserInBoardUserList(login.current_user, boardId):
		return redirect('/?error=Error: You do not have permission to view this page')

	if request.args.get('error') != None:
		errors = [{'message':request.args.get('error'),'class':'bg-danger'}]


	if login.current_user.is_authenticated():
		userSettings = databaseFunctions.getBoardUserSettings(boardId, login.current_user.get_id())
	else: 
		userSettings = databaseFunctions.getBoardUserSettings(boardId, None)

	boardName = databaseFunctions.getBoardName(boardId)
	return render_template("thread.html", userSettings=userSettings, boardName=boardName, boardId=boardId, 
							thread=thread, threadId=threadId,errors=errors)


@app.route("/board/<boardId>/thread/<threadId>/post", methods=['POST'])
def post(boardId, threadId):
	#check if the user is a part of this board	
	if not utils.isUserInBoardUserList(login.current_user, boardId):
		return redirect('/?error=Error: You do not have permission to view this page')

	comment = request.form.get('postContent')
	if comment or (len(request.files) > 0 and request.files.get('photo') != None 
			and request.files.get('photo').filename != ''):

		status = utils.isValidThreadComment(comment)
		if not status['isValid']:
			return redirect('/boardId/'+boardId+'/thread/'+threadId+
				'?error=Error: '+status['reason'])

		if login.current_user.is_authenticated():
			creatorId = login.current_user.userId;
		else:
			creatorId = None

		if (len(request.files) > 0 and request.files.get('photo') != None 
				and request.files.get('photo').filename != ''):
			status = filesAPI.handleUploadFormSubmit(request.files['photo'])
			if not status['isValid']:
				return redirect('/thread/'+threadId+'?error='+status['reason'])

			fileId = databaseFunctions.addFileToDatabase(status['fileInfo'], "192.0.0.1")
			databaseFunctions.createPost(boardId, threadId, 
										comment, fileId, creatorId=creatorId)
		else:
			databaseFunctions.createPost(boardId, threadId, 
										comment, creatorId=creatorId)

		return redirect('/board/'+boardId+'/thread/'+threadId)
	else:
		return redirect('/board/'+boardId+'/thread/'+threadId+'?error=Error: Comment was empty.')

@app.route('/board/<boardId>/thread/<threadId>/removePost/<postId>')
@login.login_required
def removePostPage(boardId, threadId, postId):
	#check if the user is allowed to post to this board
	if not utils.canRemovePost(login.current_user, boardId):
		return redirect('/?error=Error: You do not have permission to view this page')

	databaseFunctions.removePost(boardId, threadId, postId)
	return redirect('/board/'+boardId+'/thread/'+threadId)

#     #   #####   #######  ######  
#     #  #     #  #        #     # 
#     #  #        #        #     # 
#     #   #####   #####    ######  
#     #        #  #        #   #   
#     #  #     #  #        #    #  
 #####    #####   #######  #     # 


@app.route('/login')
def loginPage():
	errors = []
	if request.args.get('error') != None:
		errors = [{'message':request.args.get('error'),'class':'bg-danger'}]
	if request.args.get('success') != None:
		errors = [{'message':request.args.get('success'),'class':'bg-success'}]
	return render_template('login.html', errors=errors)

@app.route('/loginSubmit', methods=['POST'])
def loginSubmitPage():
	userStringId = request.form.get('input_usernameLogin')
	password 	 = request.form.get('input_passwordLogin')

	if userStringId == None or userStringId == '':
		return redirect('/login?error=Error: Bad Username or Email Address')

	userStringId = userStringId.lower()
	status = loginLogic.loginUser(userStringId, password)
	if not status['isValid']:
		return redirect('/login?error='+status['reason'])

	return redirect('/')

#FIXME: MORE CHECKING HERE !!!
@app.route('/signUpSubmit', methods=['POST'])
def signUpSubmitPage():
	username 	 = request.form.get('input_usernameSignup')
	password1 	 = request.form.get('input_passwordSignup1')
	password2 	 = request.form.get('input_passwordSignup2')
	email 	 	 = request.form.get('input_emailSignup')
	
	status = utils.isValidUsername(username)
	if not status['isValid']:
		return redirect('/login?error=Error: '+status['reason'])
	
	status = utils.isValidPassword(password1)
	if not status['isValid']:
		return redirect('/login?error=Error: '+status['reason'])

	status = utils.isValidEmail(email)
	if not status['isValid']:
		return redirect('/login?error=Error: '+status['reason'])
	
	passwordHash = loginLogic.hashPassword(password1);
	if not password1 == password2:
		return redirect('/login?error=Error: Passwords did not match')
	else:
		email 	 = email.lower()#Emails are always stored as lowercase
		username = username.lower()#Usernames are always stored as lowercase
		returnCode = databaseFunctions.addUser(email, username, passwordHash, 0)
		if returnCode == -1:
			return redirect('/login?error=Error: Username Taken')
		elif returnCode == -2:
			return redirect('/login?error=Error: Email Taken')

		loginLogic.loginUser(username, password1)
		return redirect('/?success=Success: Account created !')

	return redirect('/login?error=Error: Sign up failed')


@app.route('/dashboard')
@login.login_required
def dashboardPage(errors=[]):
	errors = []
	if request.args.get('error') != None:
		errors = [{'message':request.args.get('error'),'class':'bg-danger'}]
	if request.args.get('success') != None:
		errors = [{'message':request.args.get('success'),'class':'bg-success'}]
	return render_template('dashboard.html',errors=errors, 
							emails=databaseFunctions.getAllEmails(),
							usernames=databaseFunctions.getAllUsernames(),
							friends=databaseFunctions.getFriends(login.current_user.userId))

@app.route('/addFriend', methods=['POST'])
@login.login_required
def addFriendPage():
	friendStringId = request.form.get('friendStringId')
	if friendStringId == None or friendStringId == '':
		return redirect('/dashboard?friends=1&error=Error: Invalid Friend Id')

	friendStringId = friendStringId.lower()
	returnCode = databaseFunctions.addFriend(login.current_user.userId, friendStringId)
	if returnCode == 0:
		return redirect('/dashboard?friends=1&success=Success: Friend Added')
	elif returnCode == -1:
		return redirect('/dashboard?friends=1&error=Error: User Doesn\' exist')
	elif returnCode == -2:
		return redirect('/dashboard?friends=1&error=Error: That user is already your friend')
	elif returnCode == -3:
		return redirect('/dashboard?friends=1&error=Error: You can\'t add yourself silly!')
	else:
		return redirect('/dashboard?friends=1&error=Error: Something weird happened O_o')

@app.route('/logout')
@login.login_required
def logoutPage(errors=[]):
	login.logout_user()
	return redirect('/?success=You are now logged out')


@app.route('/changeUsername')
@login.login_required
def changeUsernamePage():
	errors = []
	if request.args.get('error') != None:
		errors = [{'message':request.args.get('error'),'class':'bg-danger'}]
	if request.args.get('success') != None:
		errors = [{'message':request.args.get('success'),'class':'bg-success'}]
	return render_template('changeUsername.html',errors=errors)

@app.route('/changeUsernameSubmit', methods=['POST'])
@login.login_required
def changeUsernameSubmitPage():
	newUsername = request.form.get('input_newUsername')
	status = utils.isValidUsername(newUsername)
	if status['isValid']:
		newUsername = newUsername.lower()
		if databaseFunctions.changeUsername(login.current_user.userId, newUsername) == -1:
			return redirect('/changeUsername?error=Error: Username Taken&settings=1')
		else:
			return redirect('/dashboard?success=Success: Username Changed&settings=1')
	else:
		return redirect('/changeUsername?error=Error: '+status['reason'])

@app.route('/changeEmail')
@login.login_required
def changeEmailPage():
	errors = []
	if request.args.get('error') != None:
		errors = [{'message':request.args.get('error'),'class':'bg-danger'}]
	if request.args.get('success') != None:
		errors = [{'message':request.args.get('success'),'class':'bg-success'}]
	return render_template('changeEmail.html',errors=errors)

@app.route('/changeEmailSubmit', methods=['POST'])
@login.login_required
def changeEmailSubmitPage():
	newEmail = request.form.get('input_newEmail')
	status = utils.isValidEmail(newEmail)
	if status['isValid']:
		newEmail = newEmail.lower()
		if databaseFunctions.changeEmail(login.current_user.userId, newEmail) == -1:
			return redirect('/changeEmail?error=Error: Email Taken&settings=1')
		else:
			return redirect('/dashboard?success=Success: Email Changed&settings=1')
	else:
		return redirect('/changeEmail?error=Error: '+status['reason'])

@app.route('/changePassword')
@login.login_required
def changePasswordPage():
	errors = []
	if request.args.get('error') != None:
		errors = [{'message':request.args.get('error'),'class':'bg-danger'}]
	if request.args.get('success') != None:
		errors = [{'message':request.args.get('success'),'class':'bg-success'}]
	return render_template('changePassword.html', errors=errors)

@app.route('/changePasswordSubmit', methods=['POST'])
@login.login_required
def changePasswordSubmitPage():
	oldPassword  = request.form.get('input_oldPassword')
	newPassword1 = request.form.get('input_newPassword1')
	newPassword2 = request.form.get('input_newPassword2')
	status = utils.isValidPassword(newPassword1)
	if status['isValid']:

		if loginLogic.checkUserPassword(login.current_user, oldPassword):
			return redirect('/changePassword?error=Error: Wrong Old password.')
		elif newPassword1 != newPassword2:
			return redirect('/changePassword?error=Error: New Passwords didn\'t Match')

		newPasswordHash = newPassword1

		databaseFunctions.changePasswordHash(login.current_user.userId, newPasswordHash)
		return redirect('/dashboard?success=Success: Password Changed')
	else:
		return redirect('/dashboard?error=Error: '+status['reason'])

@app.route('/deleteAccount')
@login.login_required
def deleteAccountPage():
	databaseFunctions.removeUser(login.current_user.userId)
	login.logout_user()
	return redirect('/')

@app.route('/<boardId>/leaveGroup')
@login.login_required
def leaveGroupPage(boardId):
	databaseFunctions.removeUserFromBoard(boardId, login.current_user.get_id())
	return redirect('/')

@app.route('/changeUserProfilePicSubmit', methods=['POST'])
@login.login_required
def changeUserProfilePicSubmitPage():
	if (len(request.files) > 0 and request.files.get('profilePic') != None 
				and request.files.get('profilePic').filename != ''):

		status = filesAPI.handleUploadFormSubmit(request.files['profilePic'])
		if not status['isValid']:
			return redirect('/dashboard?settings=1&error=Error: Invalid File')

		fileId = databaseFunctions.addFileToDatabase(status['fileInfo'], "192.0.0.1")
		databaseFunctions.changeUserProfilePic(login.current_user.get_id(), fileId)
		return redirect('/dashboard?settings=1')
	else:
		return redirect('/dashboard?settings=1')


def init_login():
	login_manager = login.LoginManager()
	login_manager.init_app(app)

	# Create user loader function
	@login_manager.user_loader
	def load_user(user_id):
		return loginLogic.getUserFromId(user_id)

	@login_manager.unauthorized_handler
	def showLoginPage():
		return redirect("/login")


init_login()

if __name__ == "__main__":
	app.debug = True
	app.run()
