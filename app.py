from database import databaseFunctions
import redis
import filesAPI
import thumbnailGenerator
from flask import Flask, render_template, request, send_file, redirect, url_for
from flask.ext import login
import loginLogic
import utils
app = Flask(__name__)
app.config['SECRET_KEY'] = '8pp3dStringb38rb'


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

@app.route("/board/<boardId>/thread/<threadId>")
@app.route("/board/<boardId>/thread/<threadId>/")
def showThread(threadId,boardId,errors=[]):
	if request.args.get('error') != None:
		errors = [{'message':request.args.get('error'),'class':'bg-danger'}]

	thread = databaseFunctions.getThread(boardId, threadId)

	if login.current_user.is_authenticated():
		userSettings = databaseFunctions.getBoardUserSettings(boardId, login.current_user.get_id())
	else: 
		userSettings = databaseFunctions.getBoardUserSettings(boardId, None)

	if thread == None:
		return redirect('/?error=Error: Thread doesn\'t exist.')
	boardName = databaseFunctions.getBoardName(boardId)
	return render_template("thread.html", userSettings=userSettings, boardName=boardName, boardId=boardId, 
							thread=thread, threadId=threadId,errors=errors)

@app.route("/board/<boardId>/thread/<threadId>/post", methods=['POST'])
def post(boardId, threadId):
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
			status = filesAPI.handleUploadFormSubmit(request.files)
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

@app.route('/<boardId>/threadSubmit', methods=['POST'])
def threadSubmitPage(boardId):
	threadId = ''
	subject = request.form.get('subject')
	comment = request.form.get('comment')
	if subject != None and comment != None and request.files.get('photo') != None:
		
		if request.files.get('photo').filename == '':
			return redirect('/'+boardId+'/createNewConv?error=Error: No file uploaded.')

		status = utils.isValidThreadSubject(subject)
		if not status['isValid']:
			return redirect('/'+boardId+'/createNewConv?error=Error: '+status['reason'])

		status = utils.isValidThreadComment(comment)
		if not status['isValid']:
			return redirect('/'+boardId+'/createNewConv?error=Error: '+status['reason'])

		status = filesAPI.handleUploadFormSubmit(request.files)
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

@app.route('/createNewGroup')
@login.login_required
def createNewGroupPage():
	return render_template('createNewGroup.html')

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
	newUser = request.form.get("input_newUser")
	
	if newUser == None or newUser == '':
		return redirect('/'+boardId+'/settings?error=Error: Invalid username or email address ')

	newUser = newUser.lower()
	newUserId = databaseFunctions.getUserIdFromIdString(newUser)
	if newUserId == None:
		return redirect('/'+boardId+'/settings?error=Error: The username "'+newUser+'" didn\'t match any users')

	boardInfo = databaseFunctions.getBoardInfo(boardId)
	if boardInfo == None:
		return redirect('/'+boardId+'/settings?error=Error: Invalid board Id')

	if (login.current_user.userId == boardInfo['adminId'] 
			or login.current_user.userId in boardInfo['modsList']):
		if boardInfo['isPrivate'] == 'True':
			databaseFunctions.addUserToBoard(newUserId, boardId)
			return redirect('/'+boardId+'/settings?success=Success: user added')
		else:
			return redirect('/'+boardId+'/settings?error=Error: Not a private board')
	else:
		return redirect('/'+boardId+'/settings?error=Error: You are not an Admin or Mod of this board')

	return redirect('/')

@app.route('/<boardId>/addModsSubmit', methods=['POST'])
def addModsSubmitPage(boardId):
	newMod = request.form.get("input_newMod")

	if newMod == None or newMod == '':
		return redirect('/'+boardId+'/settings?error=Error: Invalid username or email address ')

	newMod = newMod.lower()
	newModId = databaseFunctions.getUserIdFromIdString(newMod)
	if newModId == None:
		return redirect('/'+boardId+'/settings?error=Error: The username "'+newMod+'" didn\'t match any users')

	boardInfo = databaseFunctions.getBoardInfo(boardId)
	if boardInfo == None:
		return redirect('/'+boardId+'/settings?error=Error: Invalid board Id')

	if login.current_user.get_id() == boardInfo['adminId'] :
		databaseFunctions.addModToBoard(newModId, boardId)
		return redirect('/'+boardId+'/settings?success=Success: mod added')
	else:
		return redirect('/'+boardId+'/settings?error=Error: You are not an admin of this board')

	return redirect('/')

@app.route('/<boardId>/createNewConv')
def createNewConversationPage(boardId):
	errors = []
	if request.args.get('error') != None:
		errors = [{'message':request.args.get('error'),'class':'bg-danger'}]
	if request.args.get('success') != None:
		errors = [{'message':request.args.get('success'),'class':'bg-success'}]

	return render_template('createNewThread.html',boardId=boardId, errors=errors)

#FIXME: thread submit is currently used instead of this
#@app.route('/<boardId>/createNewConvSubmit')
#def createNewConversationSubmitPage(boardId):
#	return render_template('/')

#TODO: remove
@app.route('/baseLayoutTest')
def baseTest():
	return render_template("baseLayout.html",
		errors=[{'message':'something here', 'class':'bg-danger'}])

@app.route('/thumb')
def thumb():
	return thumbnailGenerator.handleThumbnailRequest(request)

#FIXME: this function should not be in the databaseFunctions, it's a frontend thing
def genPageButtons(boardId, pageNo):
	#see how many buttons there shoud be and active the active one !
	pages = getNumberOfPages(boardId)
	result = []
	for x in range(pages):
		if int(x+1) == int(pageNo):
			result.append({'number':str(x+1), 'active':str(True) })
		else:
			result.append({'number':str(x+1), 'active':str(False)})
	return result

def getNumberOfPages(boardId):
	threadsNo = databaseFunctions.getBoardThreadCount(boardId)
	pages = (threadsNo/threadsPerPage)
	if threadsNo%threadsPerPage != 0:
		pages += 1

	return pages

#FIXME: this function should MAYBE not be in the databaseFunctions, it's a frontend thing
def getPagePreview(boardId, pageNo):
	board = databaseFunctions.getBoardInfo(boardId)
	board['threads'] = [] 
	threadIdList = databaseFunctions.getBoardThreadListRange(boardId, 
		(pageNo-1)*(threadsPerPage), (pageNo)*(threadsPerPage)-1)
	for threadId in threadIdList:
		board['threads'].append(getThreadPreview(boardId, threadId))

	return board

def getThreadPreview(boardId, threadId):
	thread = databaseFunctions.getThreadInfo(boardId, threadId)
	thread['posts'] = []
	thread['posts'].extend( databaseFunctions.getPostsRange(boardId, threadId, 0, 0) )
	thread['posts'].extend( databaseFunctions.getPostsRange(boardId, threadId, -5, -1) )

	return thread

@app.route('/board/<boardId>/thread/<threadId>/removePost/<postId>')
@login.login_required
def removePostPage(boardId, threadId, postId):
	databaseFunctions.removePost(boardId, threadId, postId)
	return redirect('/board/'+boardId+'/thread/'+threadId)

@app.route('/board/<boardId>/thread/<threadId>/deleteThread')
@login.login_required
def deleteThread(boardId, threadId):
	databaseFunctions.removeThread(boardId, threadId)
	return redirect('/')

#not used, using javascript instead
##insert a <wbr></wbr> every n chars
#def formatPosts(posts, every=64):
#	for post in posts:
#	    lines = []
#	    for i in xrange(0, len(post['message']), every):
#	        lines.append(post['message'][i:i+every])
#	    post['message']= '<wbr></wbr>'.join(lines)
#
#	return posts


 #####                              
#     # #####   ####  #    # #####  
#       #    # #    # #    # #    # 
#  #### #    # #    # #    # #    # 
#     # #####  #    # #    # #####  
#     # #   #  #    # #    # #      
 #####  #    #  ####   ####  #      


@app.route('/<boardId>/changeGroupNameSubmit', methods=['post'])
def changeGroupNameSubmitPage(boardId):
	boardInfo = databaseFunctions.getBoardInfo(boardId)
	newName   = request.form.get('input_newName')

	status = isValidGroupName(newName)
	if not status['isValid']:
		return redirect('/'+boardId+'/settings?error=Error: '+status['reason'])

	if login.current_user.userId == boardInfo['adminId']:
		databaseFunctions.changeBoardName(boardId, newName)
		return redirect('/'+boardId+'/settings')
	else:
		return redirect('/')

@app.route('/<boardId>/changeGroupPasswordSubmit', methods=['post'])
def changeGroupPasswordSubmitPage(boardId):
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
	addUsers 	= request.form.get('addUsers', False)
	kickUsers 	= request.form.get('kickUsers', False)
	removePosts = request.form.get('removePosts', False)
	databaseFunctions.setModPermissions(boardId, modId, addUsers, 
										kickUsers, removePosts)
	return redirect('/'+boardId+'/settings')

@app.route('/<boardId>/togglePrivate')
@login.login_required
def togglePrivatePage(boardId,errors=[]):
	boardInfo = databaseFunctions.getBoardInfo(boardId)
	if boardInfo['isPrivate'] == 'True':
		databaseFunctions.makeBoardPublic(boardId)
	else:
		databaseFunctions.makeBoardPrivate(boardId)
	return redirect('/'+boardId+'/settings')

@app.route('/<boardId>/settings')
@login.login_required
def settingsPage(boardId,errors=[]):
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
	databaseFunctions.removeModFromBoard(boardId, modId)
	return redirect('/'+boardId+'/settings?success=Success: Mod Removed')

@app.route('/<boardId>/kickUser/<userId>')
@login.login_required
def kickUserPage(boardId, userId,errors=[]):
	databaseFunctions.removeUserFromBoard(boardId, userId)
	return redirect('/'+boardId+'/settings?success=Success: User Kicked')

@app.route('/<boardId>/deleteBoard')
@login.login_required
def deleteBoardPage(boardId):
	boardInfo = databaseFunctions.getBoardInfo(boardId)
	if login.current_user.userId == boardInfo['adminId']:
		databaseFunctions.removeBoard(boardId)
	
	return redirect('/')

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
	
	print 'hashing password --'+password1+'--'
	passwordHash = loginLogic.hashPassword(password1);
	print 'hashing password --'+password1+'--'
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

		oldPasswordHash = oldPassword;
		#check if they gave the right old password
		if loginLogic.checkUserPassword(login.current_user, oldPasswordHash):
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

@app.route('/changeUserProfilePicSubmit', methods=['post'])
@login.login_required
def changeUserProfilePicSubmitPage():
	if (len(request.files) > 0 and request.files.get('profilePic') != None 
				and request.files.get('profilePic').filename != ''):

		status = filesAPI.handleUploadFormSubmit(request.files)
		if not status['isValid']:
			return redirect('/thread/')

		fileId = databaseFunctions.addFileToDatabase(status['fileInfo'], "192.0.0.1")
		databaseFunctions.changeUserProfilePic(login.current_user.get_id(), fileId)
		return redirect('/thread/')
	else:
		return redirect('/thread/')


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
