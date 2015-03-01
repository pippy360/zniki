from database import databaseFunctions
import redis
import filesAPI
import thumbnailGenerator
from flask import Flask, render_template, request, send_file, redirect, url_for, abort, jsonify
from flask.ext import login
import loginLogic
import utils
import chat

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
			return redirect('/boardId/'+boardId+'/thread/'+threadId+'?error=Error: Comment exceeded max length ('+str(MAX_COMMENT_LENGTH)+' characters).')

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



#     #   #####   #######  ######  
#     #  #     #  #        #     # 
#     #  #        #        #     # 
#     #   #####   #####    ######  
#     #        #  #        #   #   
#     #  #     #  #        #    #  
 #####    #####   #######  #     # 

@app.route('/dashboard')
@login.login_required
def dashboardPage(errors=[]):
	errors = []
	if request.args.get('error') != None:
		errors = [{'message':request.args.get('error'),'class':'bg-danger'}]
	if request.args.get('success') != None:
		errors = [{'message':request.args.get('success'),'class':'bg-success'}]
	return render_template('dashboard.html',errors=errors)

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


#chat
@app.route('/chatBegin', methods=['POST']) #ajax
@login.login_required
def chatBegin():
	json = request.get_json()
	if json == None:
		abort(400) #we are expecting "application/json"

	initiatorId = login.current_user.userId
	boardId = json['boardId']
	postId = json['postId']

	#now we must find out the userId of the poster of that postId for the relevant board and post therein
	postInfo = databaseFunctions.getPost(boardId, postId)
	receiverId = postInfo.get('creatorId')

	if initiatorId == receiverId: #that's not very productive
		abort(403)

	#make sure the chat doesn't alredy exist
	chatId = chat.getChatId(boardId, postId, initiatorId)

	if chatId != None:
		print 'warning: trying to initiate existing chat from user %s about board %s and post %s (to user %s)' % \
			(initiatorId, boardId, postId, receiverId)
		ch = chat.getChatInfo(chatId)
		return jsonify(chatId = ch.id, state = ch.state)

	else:
		print 'initiating chat from user %s about board %s and post %s (to user %s)' % \
			(initiatorId, boardId, postId, receiverId)
		chatId = chat.beginChat(boardId, postId, initiatorId, receiverId)
		return jsonify(chatId = chatId, state = 0)

@app.route('/chatEnd', methods=['POST']) #ajax
@login.login_required
def chatEnd():
	json = request.get_json()
	if json == None:
		abort(400) #we are expecting "application/json"

	userId = login.current_user.userId
	chatId = json['chatId']
	reason = ''
	if 'reason' in json:
		reason = json['reason']

	print 'user %s requested we end chat %s, because: %s', userId, chatId, reason

	if not chat.isUserInChat(userId, chatId):
		print 'but either the chat does not exist or the user is not part of the chat'
		abort(403)

	chat.endChat(chatId)
	return jsonify(dummy = "dummy") #I think we absolutely have to return something

@app.route('/chatPost', methods=['POST']) #ajax
@login.login_required
def chatPost():
	json = request.get_json()
	if json == None:
		abort(400) #we are expecting "application/json"

	userId = login.current_user.userId
	chatId = json['chatId']
	text = json['msg']

	print 'chat post from user %s on chat %s' % (userId, chatId)
	print 'chat message: %s' % text

	if not chat.isUserInChat(userId, chatId):
		print 'but either the chat does not exist or the user is not part of the chat'
		abort(403)

	newState = chat.postInChat(chatId, userId, text)
	return jsonify(state = newState)

@app.route('/chatPoll', methods=['POST']) #ajax
@login.login_required
def chatPoll():
	json = request.get_json()
	if json == None:
		abort(400) #we are expecting "application/json"

	userId = login.current_user.userId
	clientStates = json['states'] #should be a {chatId => state} object

	#convert state counters to integers
	for k, v in clientStates.iteritems():
		clientStates[k] = int(v)

	print 'chat poll request from user %s, with states %s' % (userId, str(clientStates))
	updates = {}

	#give user updates on the chats they know about
	#as well as new ones they're not aware of

	allChats = chat.getAllChatsWithUser(userId)
	for chatId in allChats:
		clientState = 0
		if chatId in clientStates:
			clientState = clientStates[chatId]

		chatInfo = chat.getChatInfo(chatId)
		otherId = chatInfo.fromId if userId == chatInfo.toId else chatInfo.toId
		otherName = databaseFunctions.getUserInfo(otherId)['username']

		if chatInfo.state > 0 or userId == chatInfo.fromId:
			#this check exists so that a poster is not immediately told of a new chat,
			#before the initiator has typed the first reply
			updates[chatId] = {
				'boardId': chatInfo.boardId,
				'postId': chatInfo.postId,
				'partnerName': otherName,
				'updates': chat.getUpdates(chatId, userId, clientState)
			}

	#TODO: check if user is trying to get updates for chats they're not part of
	#if chat.isUserInChat(userId, chatId):
	
	#TODO: tell the client somehow when a chat has ended, why it has ended

	print 'returning', updates
	return jsonify(**updates)

# @app.route('/chatStream', methods=['POST']) #web socket
# @login.login_required
# def chatPost():
#   if json == None:
# 	  abort(500) #we are expecting "application/json"
#   print 'begin-chat request, json:', json
# 
# 	userId = login.current_user.userId
# 	chatId = request.form.get('chatId')
# 	clientState = request.form.get('state')

# 	#return flask.Response(event_stream(), mimetype="text/event-stream")



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
