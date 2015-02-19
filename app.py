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


postRedisDB = redis.StrictRedis( '127.0.0.1', 6379 )
postRedisDB.flushall()


boardId = databaseFunctions.createBoard("Home")
boardId = databaseFunctions.createBoard("Home")
boardId = databaseFunctions.createBoard("Home")
boardId = databaseFunctions.createBoard("Home")

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

	boardList = databaseFunctions.getAllBoards()
	if request.args.get('error') != None:
		errors = [{'message':request.args.get('error'),'class':'bg-danger'}]

	return render_template("index.html", errors=errors, boardList=boardList)

@app.route("/thread/<threadId>/post", methods=['POST'])
def post(threadId):
	if request.form.get('postContent') or (len(request.files) > 0 and request.files.get('photo') != None 
			and request.files.get('photo').filename != ''):

		if (request.form.get('postContent') != None 
			and len(request.form.get('postContent')) > MAX_COMMENT_LENGTH):
			return redirect('/thread/'+threadId+'?error=Error: Comment exceeded max length ('+str(MAX_COMMENT_LENGTH)+' characters).')

		if (len(request.files) > 0 and request.files.get('photo') != None 
			and request.files.get('photo').filename != ''):
			status = filesAPI.handleUploadFormSubmit(request.files)
			if not status['isValid']:
				return redirect('/thread/'+threadId+'?error='+status['reason'])

			fileId = databaseFunctions.addFileToDatabase(status['fileInfo'], "192.0.0.1")
			databaseFunctions.createPost(boardId, threadId, 
										request.form.get('postContent'), fileId)
		else:
			databaseFunctions.createPost(boardId, threadId, 
										request.form.get('postContent'))

		return redirect('/thread/'+threadId)
	else:
		return redirect('/thread/'+threadId+'?error=Error: Comment was empty.')

@app.route("/thread/<threadId>")
@app.route("/thread/<threadId>/")
def showThread(threadId,errors=[]):
	if request.args.get('error') != None:
		errors = [{'message':request.args.get('error'),'class':'bg-danger'}]

	thread = databaseFunctions.getThread(boardId, threadId)

	if thread == None:
		return redirect('/?error=Error: Thread doesn\'t exist.')
	boardName = databaseFunctions.getBoardName(boardId)
	return render_template("thread.html", boardName=boardName, 
							thread=thread, threadId=threadId,errors=errors)

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
	print 'status'
	print status
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

		return redirect('/?success=Success: Account created !')

	return redirect('/login?error=Error: Sign up failed')

@app.route('/threadSubmit', methods=['POST'])
def threadSubmitPage():
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

		fileId = databaseFunctions.addFileToDatabase(status['fileInfo'], "192.0.0.1")
		threadId = databaseFunctions.createThread(boardId, request.form['subject'], 
												request.form['comment'], fileId)
		return redirect('/thread/'+threadId)
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

	#create a new board
	databaseFunctions.createBoard(groupName)
	return redirect('/')

@app.route('/<boardId>/createNewConv')
def createNewConversationPage(boardId):
	return render_template('createNewThread.html')

@app.route('/<boardId>/createNewConvSubmit')
def createNewConversationSubmitPage(boardId):
	return render_template('createNewThread.html')

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
