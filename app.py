from database import databaseFunctions
import redis
import filesAPI
import thumbnailGenerator
from flask import Flask, render_template, request, send_file, redirect, url_for
app = Flask(__name__)



postRedisDB = redis.StrictRedis( '127.0.0.1', 6379 )
postRedisDB.flushall()


boardId = databaseFunctions.createBoard("Home")

threadsPerPage = 5
MAX_SUBJECT_LENGTH = 50
MAX_COMMENT_LENGTH = 10000

@app.route("/")
@app.route("/home")
@app.route("/home/")
@app.route("/index.html")
def showIndex():
	return showPage(1)

@app.route("/page/<int:pageNo>")
@app.route("/page/<int:pageNo>/")
def showPage(pageNo, errors=[]):
	if request.args.get('error') != None:
		errors = [{'message':request.args.get('error'),'class':'bg-danger'}]

	#for new boards
	if getNumberOfPages(boardId) == 0:
		return render_template("index.html", 
			page={
				'name': databaseFunctions.getBoardName(boardId),
				'threads': [],
		 	}, 
			errors=errors)

	pageNo = str(pageNo)
	if int(pageNo) < 0 or int(pageNo) > getNumberOfPages(boardId):
		return redirect('/?error=Error: page number '+pageNo+' does not exist')

	page = getPagePreview(boardId, int(pageNo))
	return render_template("index.html", page=page, 
		pageButtons=genPageButtons(boardId, pageNo), errors=errors)

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

@app.route('/threadSubmit', methods=['POST'])
def login():
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


if __name__ == "__main__":
	app.debug = True
	app.run()
