from database import databaseFunctions
import redis
from flask import Flask, render_template, request, send_file, redirect, url_for
app = Flask(__name__)



postRedisDB = redis.StrictRedis( '127.0.0.1', 6379 )
postRedisDB.flushall()


boardId = databaseFunctions.createBoard("New Board Test")

threadId = databaseFunctions.createThread(boardId, "I love NY", "hey check out my new thread", "file_001")
threadId = databaseFunctions.createThread(boardId, "I love NY", "hey check out my new thread", "file_001")
threadId = databaseFunctions.createThread(boardId, "I love NY", "hey check out my new thread", "file_001")
threadId = databaseFunctions.createThread(boardId, "I love NY", "hey check out my new thread", "file_001")
threadId = databaseFunctions.createThread(boardId, "I love NY", "hey check out my new thread", "file_001")
threadId = databaseFunctions.createThread(boardId, "I love NY", "hey check out my new thread", "file_001")
threadId = databaseFunctions.createThread(boardId, "I love NY", "hey check out my new thread", "file_001")
threadId = databaseFunctions.createThread(boardId, "I love NY", "hey check out my new thread", "file_001")
threadId = databaseFunctions.createThread(boardId, "I love NY", "hey check out my new thread", "file_001")
threadId = databaseFunctions.createThread(boardId, "I love NY", "hey check out my new thread", "file_001")
threadId = databaseFunctions.createThread(boardId, "I love NY", "hey check out my new thread", "file_001")
threadId = databaseFunctions.createThread(boardId, "I love NY", "hey check out my new thread", "file_001")
threadId = databaseFunctions.createThread(boardId, "I love NY", "hey check out my new thread", "file_001")
threadId = databaseFunctions.createThread(boardId, "I love NY", "hey check out my new thread", "file_001")

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

threadId = databaseFunctions.createThread(boardId, "Thread about cheese", "hey check out my new thread hey check out my new threadhey check out my new threadhey check out my new thread", "file_001")

databaseFunctions.createPost(boardId, threadId, "This man is "+
	"making something. He has that ability. It's got style and personality. I love it.")
databaseFunctions.createPost(boardId, threadId, "This is post 2")
databaseFunctions.createPost(boardId, threadId, "This is post 3")
databaseFunctions.createPost(boardId, threadId, "This is post 4")
databaseFunctions.createPost(boardId, threadId, "something here to test")


threadId = databaseFunctions.createThread(boardId, "School books", "hey check out my new thread 324", "file_001")

databaseFunctions.createPost(boardId, threadId, "This is post 1")
databaseFunctions.createPost(boardId, threadId, "This is post 2")
databaseFunctions.createPost(boardId, threadId, "This is post 3")
databaseFunctions.createPost(boardId, threadId, "This is post 4")
databaseFunctions.createPost(boardId, threadId, "This is post 5")


threadId = databaseFunctions.createThread(boardId, "subject", "hey check out my new thread sdf", "file_001")

databaseFunctions.createPost(boardId, threadId, "This is post 1")
databaseFunctions.createPost(boardId, threadId, "This is post 2")
databaseFunctions.createPost(boardId, threadId, "This is post 3")
databaseFunctions.createPost(boardId, threadId, "This is post 4")
databaseFunctions.createPost(boardId, threadId, "This is post 5")

@app.route("/")
@app.route("/home")
@app.route("/home/")
@app.route("/index.html")
def showIndex():
	return showPage(1)

@app.route("/page/<pageNo>")
@app.route("/page/<pageNo>/")
def showPage(pageNo):
	pageNo = str(pageNo)
	if int(pageNo) < 0:
		return render_template("baseLayout.html", 
			errors=[{'message':'bad page number !','class':'bg-danger'}])

	page = databaseFunctions.getPagePreview(boardId, int(pageNo))
	return render_template("index.html", page=page, 
		pageButtons=databaseFunctions.genPageButtons(boardId, pageNo))

@app.route("/thread/<threadId>/post", methods=['POST'])
def post(threadId):
	if request.form.get('postContent'):
		databaseFunctions.createPost(boardId, threadId, request.form.get('postContent'))
		return redirect('/thread/'+threadId)
	else:
		return redirect('/thread/'+threadId)

@app.route("/thread/<threadId>")
@app.route("/thread/<threadId>/")
def showThread(threadId):
	thread = databaseFunctions.getThread(boardId, threadId)
	boardName = databaseFunctions.getBoardName(boardId)
	return render_template("thread.html", boardName=boardName, thread=thread, threadId=threadId)

@app.route('/threadSubmit', methods=['POST'])
def login():
	threadId = ''
	if request.form.get('subject') != None and request.form.get('comment') != None:
		threadId = databaseFunctions.createThread(boardId, request.form['subject'], request.form['comment'], "file_001")
		return redirect('/thread/'+threadId)
	else:
		return redirect('/')#pass it here and pass on an error message

#TODO: remove
@app.route('/baseLayoutTest')
def baseTest():
	return render_template("baseLayout.html",errors=[{'message':'something here', 'class':'bg-danger'}])


if __name__ == "__main__":
	app.debug = True
	app.run()
