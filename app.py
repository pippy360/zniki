from database import databaseFunctions
import redis
import filesAPI
import thumbnailGenerator
from flask import Flask, render_template, request, send_file, redirect, url_for
from flask.ext import login
import loginLogic
import utils
app = Flask(__name__)
app.config['SECRET_KEY'] = '123456790'


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

threadsPerPage = 5
MAX_SUBJECT_LENGTH = 50
MAX_COMMENT_LENGTH = 10000

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

	if request.args.get('error') != None:
		errors = [{'message':request.args.get('error'),'class':'bg-danger'}]

	return render_template("index.html", errors=errors, boardList=boardList)

@app.route("/board/<boardId>/thread/<threadId>")
@app.route("/board/<boardId>/thread/<threadId>/")
def showThread(threadId,boardId,errors=[]):
	if request.args.get('error') != None:
		errors = [{'message':request.args.get('error'),'class':'bg-danger'}]

	thread = databaseFunctions.getThread(boardId, threadId)

	if thread == None:
		return redirect('/?error=Error: Thread doesn\'t exist.')
	boardName = databaseFunctions.getBoardName(boardId)
	return render_template("thread.html", boardName=boardName, boardId=boardId, 
							thread=thread, threadId=threadId,errors=errors)

@app.route("/board/<boardId>/thread/<threadId>/post", methods=['POST'])
def post(boardId, threadId):
	if request.form.get('postContent') or (len(request.files) > 0 and request.files.get('photo') != None 
			and request.files.get('photo').filename != ''):

		if (request.form.get('postContent') != None 
			and len(request.form.get('postContent')) > MAX_COMMENT_LENGTH):
			return redirect('/boardId/'+boardId+'/thread/'+threadId+
				'?error=Error: Comment exceeded max length ('+str(MAX_COMMENT_LENGTH)+' characters).')

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
										request.form.get('postContent'), fileId, creatorId=creatorId)
		else:
			databaseFunctions.createPost(boardId, threadId, 
										request.form.get('postContent'), creatorId=creatorId)

		return redirect('/board/'+boardId+'/thread/'+threadId)
	else:
		return redirect('/board/'+boardId+'/thread/'+threadId+'?error=Error: Comment was empty.')

@app.route('/<boardId>/threadSubmit', methods=['POST'])
def threadSubmitPage(boardId):
	threadId = ''
	if (request.form.get('subject') != None and request.form.get('comment') != None 
		and request.files.get('photo') != None):
		if (request.files.get('photo') == None or request.files.get('photo').filename == ''):
			return redirect('/?error=Error: No file uploaded.')

		if (request.form.get('subject') != None 
			and len(request.form.get('subject')) > MAX_SUBJECT_LENGTH):
			return redirect('/?error=Error: Subject exceeded max length ('+str(MAX_SUBJECT_LENGTH)+' characters).')

		if (request.form.get('comment') != None 
			and len(request.form.get('comment')) > MAX_COMMENT_LENGTH):
			return redirect('/?error=Error: Comment exceeded max length ('+str(MAX_COMMENT_LENGTH)+' characters).')


		status = filesAPI.handleUploadFormSubmit(request.files)
		if not status['isValid']:
			return redirect('/?error='+status['reason'])

		if login.current_user.is_authenticated():
			creatorId = login.current_user.userId
		else:
			creatorId = None

		fileId = databaseFunctions.addFileToDatabase(status['fileInfo'], "192.0.0.1")
		threadId = databaseFunctions.createThread(boardId, request.form['subject'], 
												request.form['comment'], fileId, creatorId=creatorId)
		return redirect('/')
	else:
		return redirect('/')#pass it here and pass on an error message

@app.route('/createNewGroup')
def createNewGroupPage():
	return render_template('createNewGroup.html')

@app.route('/createNewGroupSubmit', methods=['POST'])
def createNewGroupSubmitPage():
	groupName = request.form.get("input_groupName")
	if groupName == None:
		return redirect('/createNewGroup?error=Error: Invalid Group Name')

	isPrivate = request.form.get("privateGroup")
	isPrivate = (isPrivate == 'True')

	#create a new board
	databaseFunctions.createBoard(groupName, isPrivate, login.current_user.userId)
	return redirect('/')

@app.route('/<boardId>/addUsersSubmit', methods=['POST'])
@login.login_required
def addUsersSubmitPage(boardId):
	newUser = request.form.get("input_newUser")
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
	return render_template('createNewThread.html',boardId=boardId)

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
	if login.current_user.userId == boardInfo['adminId']:
		databaseFunctions.changeBoardName(boardId, newName)
		return redirect('/'+boardId+'/settings')
	else:
		return redirect('/')

@app.route('/<boardId>/changeGroupPasswordSubmit', methods=['post'])
def changeGroupPasswordSubmitPage(boardId):
	boardInfo   = databaseFunctions.getBoardInfo(boardId)
	newPassword = request.form.get('input_newPassword')
	if login.current_user.userId == boardInfo['adminId']:
		databaseFunctions.changeBoardPassword(boardId, newPassword)
		return redirect('/'+boardId+'/settings')
	else:
		return redirect('/')

@app.route('/<boardId>/togglePrivate')
@login.login_required
def togglePrivatePage(boardId,errors=[]):
	boardInfo = databaseFunctions.getBoardInfo(boardId)

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

	#make sure they're non empty

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
	
	if username == None or username == '':
		return redirect('/login?error=Error: Invalid username')
	elif password1 == None or password1 == '':
		return redirect('/login?error=Error: Invalid Password')
	elif email == None or email == '':
		return redirect('/login?error=Error: Invalid Email')
	elif not password1 == password2:
		return redirect('/login?error=Error: Passwords did not match')
	else:
		returnCode = databaseFunctions.addUser(email, username, password1, 0)
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

	returnCode = databaseFunctions.addFriend(login.current_user.userId, friendStringId)
	if returnCode == 0:
		return redirect('/dashboard?friends=1&success=Success: Friend Added')
	elif returnCode == -1:
		return redirect('/dashboard?friends=1&error=Error: User Doesn\' exist')
	elif returnCode == -2:
		return redirect('/dashboard?friends=1&error=Error: That user is already your friend')
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
	if newUsername != None and newUsername != '' and utils.isValidUsername(newUsername):
		if databaseFunctions.changeUsername(login.current_user.userId, newUsername) == -1:
			return redirect('/changeUsername?error=Error: Username Taken&settings=1')
		else:
			return redirect('/dashboard?success=Success: Username Changed&settings=1')
	
	return redirect('/changeUsername?error=Error: Invalid Username')

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
	if newEmail != None and newEmail != '' and utils.isValidEmail(newEmail):
		if databaseFunctions.changeEmail(login.current_user.userId, newEmail) == -1:
			return redirect('/changeEmail?error=Error: Email Taken&settings=1')
		else:
			return redirect('/dashboard?success=Success: Email Changed&settings=1')
	
	return redirect('/changeEmail?error=Error: Invalid email address')

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
	if (request.form.get('input_oldPassword') != None and request.form.get('input_newPassword1') != None 
			and request.form.get('input_newPassword2') != None):
		oldPassword  = request.form.get('input_oldPassword')
		newPassword1 = request.form.get('input_newPassword1')
		newPassword2 = request.form.get('input_newPassword2')

		oldPasswordHash = oldPassword;
		if oldPasswordHash != login.current_user.passwordHash:#the old password
			return redirect('/changePassword?error=Error: Wrong Old password.')
		elif newPassword1 != newPassword2:
			return redirect('/changePassword?error=Error: New Passwords didn\'t Match')

		newPasswordHash = newPassword1

		databaseFunctions.changePasswordHash(login.current_user.userId, newPasswordHash)
		return redirect('/dashboard?success=Success: Password Changed')
	else:
		return redirect('/dashboard?error=Error: Password Change Failed, darn it :(')

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
