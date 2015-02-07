from database import databaseFunctions
import redis
import filesAPI
import thumbnailGenerator
from flask import Flask, render_template, request, send_file, redirect, url_for
app = Flask(__name__)



postRedisDB = redis.StrictRedis( '127.0.0.1', 6379 )
postRedisDB.flushall()


boardId = databaseFunctions.createBoard("Home")

fileData = {
		'originalFilename': '98XY8luppNRc.jpg',
		'hash':     'hash',
		'filename':     '98XY8luppNRc.jpg',
		'fileLocation': './static/storage/',
		'extension':    'extension',
		'mimetype':     '',
		'metadata': 'metadata',
		'type':     'image'
	}


fileId 	 = databaseFunctions.addFileToDatabase(fileData, "192.0.0.1")
threadId = databaseFunctions.createThread(boardId, "I love NY", "hey check out my new thread", fileId)
fileId 	 = databaseFunctions.addFileToDatabase(fileData, "192.0.0.1")
threadId = databaseFunctions.createThread(boardId, "I love NY", "hey check out my new thread", fileId)
fileId 	 = databaseFunctions.addFileToDatabase(fileData, "192.0.0.1")
threadId = databaseFunctions.createThread(boardId, "I love NY", "hey check out my new thread", fileId)
fileId 	 = databaseFunctions.addFileToDatabase(fileData, "192.0.0.1")
threadId = databaseFunctions.createThread(boardId, "I love NY", "hey check out my new thread", fileId)
fileId 	 = databaseFunctions.addFileToDatabase(fileData, "192.0.0.1")
threadId = databaseFunctions.createThread(boardId, "I love NY", "hey check out my new thread", fileId)
fileId 	 = databaseFunctions.addFileToDatabase(fileData, "192.0.0.1")
threadId = databaseFunctions.createThread(boardId, "I love NY", "hey check out my new thread", fileId)
fileId 	 = databaseFunctions.addFileToDatabase(fileData, "192.0.0.1")
threadId = databaseFunctions.createThread(boardId, "I love NY", "hey check out my new thread", fileId)
fileId 	 = databaseFunctions.addFileToDatabase(fileData, "192.0.0.1")
threadId = databaseFunctions.createThread(boardId, "I love NY", "hey check out my new thread", fileId)
fileId 	 = databaseFunctions.addFileToDatabase(fileData, "192.0.0.1")
threadId = databaseFunctions.createThread(boardId, "I love NY", "hey check out my new thread", fileId)
fileId 	 = databaseFunctions.addFileToDatabase(fileData, "192.0.0.1")
threadId = databaseFunctions.createThread(boardId, "I love NY", "hey check out my new thread", fileId)
fileId 	 = databaseFunctions.addFileToDatabase(fileData, "192.0.0.1")
threadId = databaseFunctions.createThread(boardId, "I love NY", "hey check out my new thread", fileId)
fileId 	 = databaseFunctions.addFileToDatabase(fileData, "192.0.0.1")
threadId = databaseFunctions.createThread(boardId, "I love NY", "hey check out my new thread", fileId)
fileId 	 = databaseFunctions.addFileToDatabase(fileData, "192.0.0.1")
threadId = databaseFunctions.createThread(boardId, "I love NY", "hey check out my new thread", fileId)
fileId 	 = databaseFunctions.addFileToDatabase(fileData, "192.0.0.1")
threadId = databaseFunctions.createThread(boardId, "I love NY", "hey check out my new thread", fileId)
databaseFunctions.createPost(boardId, threadId, "Eating something")
databaseFunctions.createPost(boardId, threadId, "This is post 1")
databaseFunctions.createPost(boardId, threadId, "This is post 2")
databaseFunctions.createPost(boardId, threadId, "This is post 3")
databaseFunctions.createPost(boardId, threadId, "This is post 4")
databaseFunctions.createPost(boardId, threadId, "This is post 5")
databaseFunctions.createPost(boardId, threadId, "Sed ut perspiciatis "+
	"unde omnis iste natus error sit voluptatem accusantium doloremque laudantium")
databaseFunctions.createPost(boardId, threadId, " totam rem aperiam, "+
	"eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae")
databaseFunctions.createPost(boardId, threadId, "Something fruit")
databaseFunctions.createPost(boardId, threadId, "dicta sunt explicabo."+
	" Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit"+
	" aut fugit, sed quia consequuntur magni dolores eos qui ratione"+
	" voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem"+
	" ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia"+
	" non numquam eius modi tempora incidunt ut labore et dolore magnam"+
	" aliquam quaerat voluptatem. Ut enim ad minima veniam, quis nostrum"+
	" exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid"+
	" ex ea commodi consequatur? Quis autem vel eum iure reprehenderit "+
	"qui in ea voluptate velit esse quam nihil molestiae consequatur, vel"+
	" illum qui dolorem eum fugiat quo voluptas nulla pariatur?")

threadId = databaseFunctions.createThread(boardId, "Thread about cheese", "hey check out my new thread hey check out my new threadhey check out my new threadhey check out my new thread", fileId)

databaseFunctions.createPost(boardId, threadId, "This man is "+
	"making something. He has that ability. It's got style and personality. I love it.")
databaseFunctions.createPost(boardId, threadId, "This is post 2")
databaseFunctions.createPost(boardId, threadId, "This is post 3")
databaseFunctions.createPost(boardId, threadId, "This is post 4")
databaseFunctions.createPost(boardId, threadId, "something here to test")


threadId = databaseFunctions.createThread(boardId, "School books", "hey check out my new thread 324", fileId)

databaseFunctions.createPost(boardId, threadId, "This is post 1")
databaseFunctions.createPost(boardId, threadId, "This is post 2")
databaseFunctions.createPost(boardId, threadId, "This is post 3")
databaseFunctions.createPost(boardId, threadId, "This is post 4")
databaseFunctions.createPost(boardId, threadId, "This is post 5")


threadId = databaseFunctions.createThread(boardId, "subject", "hey check out my new thread sdf", fileId)

databaseFunctions.createPost(boardId, threadId, "This is post 1")
databaseFunctions.createPost(boardId, threadId, "This is post 2")
databaseFunctions.createPost(boardId, threadId, "This is post 3")
databaseFunctions.createPost(boardId, threadId, "This is post 4")
databaseFunctions.createPost(boardId, threadId, "This is post 5")

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
