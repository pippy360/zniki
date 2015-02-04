from database import databaseFunctions
import redis
import filesAPI
from flask import Flask, render_template, request, send_file, redirect, url_for
app = Flask(__name__)


postRedisDB = redis.StrictRedis( '127.0.0.1', 6379 )
postRedisDB.flushall()

projectId = databaseFunctions.addNewProject("user_id_02", "Some Project About Something", 
	"dicta sunt explicabo."+
	" Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit"+
	" aut fugit, sed quia consequuntur magni dolores eos qui ratione"+
	" voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem"+
	" illum qui dolorem eum fugiat quo voluptas nulla pariatur?", "",
	 "http://github.com/something", "http://wiki.com/somethingElse", 
	 "file_id_001", [ "something", "cats", "nothing", "Ireland", "vague" ])

projectId = databaseFunctions.addNewProject("user_id_02", "A big long project", 
	"dicta sunt explicabo."+
	" Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit"+
	" aut fugit, sed quia consequuntur magni dolores eos qui ratione"+
	" voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem"+
	" ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia"+
	" non numquam eius modi tempora incidunt ut labore et dolore magnam"+
	" aliquam quaerat voluptatem. Ut enim ad minima veniam, quis nostrum"+
	" exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid"+
	" ex ea commodi consequatur? Quis autem vel eum iure reprehenderit "+
	"qui in ea voluptate velit esse quam nihil molestiae consequatur, vel"+
	" illum qui dolorem eum fugiat quo voluptas nulla pariatur?", "",
	 "http://github.com/something", "http://wiki.com/somethingElse", 
	 "file_id_001", [ "Ireland", "USA", "london" ])

projectId = databaseFunctions.addNewProject("user_id_02", "Cat Chat", 
	"Are you thinking of adopting a rescued cat or kitten? Perhaps you are looking "
	+"for a friendly family cat or a loving"
	+" feline companion? Could you offer a caring "
	+"home to a kitten or two, or a rural home for "
	+"neutered feral cats? There are thousands of cats and "
	+"kittens of all ages, types and personalities needing homes, "
	+"in rescue centres throughout the UK and Ireland", "",
	 "http://github.com/something", "http://wiki.com/somethingElse", 
	 "file_id_001", [ "cats", "chat", "mice", "Ireland" ])


AMOUNT_OF_MOST_RECENT = 15#the amount of most recent projects to show on the index page
AMOUNT_OF_PROJECTS_PER_SEARCH_PAGE = 15
@app.route("/")
@app.route("/home")
@app.route("/home/")
@app.route("/index.html")
def showIndex():
	recentProjectsIds = databaseFunctions.getProjectListRange(0, AMOUNT_OF_MOST_RECENT)
	print 'recentProjectsIds'
	print recentProjectsIds
	recentProjects = []
	for projectId in recentProjectsIds:
		recentProjects.append( databaseFunctions.getProjectInfo(projectId) )

	print 'recentProjects'
	print recentProjects
	return render_template("index.html", recentProjects=recentProjects)

@app.route("/s/<query>")
@app.route("/s/<query>/")
def showSearch(query):
	return showSearchPage(query, 0)

@app.route("/s/<query>/<pageNo>")
@app.route("/s/<query>/<pageNo>/")
def showSearchPage(query, pageNo):
	pageNo = str(pageNo)
	if int(pageNo) < 0:
		return render_template("baseLayout.html", 
			errors=[{'message':'bad page number !','class':'bg-danger'}])

	#get the query
	tags = query.split()
	
	#//get the results with the tags
	#get the intersec of the query	

	genPageButtons(1,0)
	
	return render_template("search.html")

@app.route("/r/<projectId>")
@app.route("/r/<projectId>/")
def showProj(projectId):
	return showIndex()
	#return render_template("index.html")

#TODO: allow editing of projects
@app.route("/r/<projectId>/edit", methods=['POST'])
def editProj(projectId):
	if request.form.get('postContent'):
		pass
	else:
		pass

@app.route('/projSubmit', methods=['POST'])
def projSubmit():
	threadId = ''
	if request.form.get('subject') != None and request.form.get('comment') != None:
		threadId = databaseFunctions.createThread(boardId, request.form['subject'], 
			request.form['comment'], request)
		return redirect('/thread/'+threadId)
	else:
		return redirect('/')#pass it here and pass on an error message

#TODO: remove
@app.route('/baseLayoutTest')
def baseTest():
	return render_template("baseLayout.html",errors=[{'message':'something here', 'class':'bg-danger'}])

def genPageButtons(resultsNo, pageNo):
	pages = (resultsNo/AMOUNT_OF_PROJECTS_PER_SEARCH_PAGE)+1;
	result = []
	for x in range(pages):
		if int(x+1) == int(pageNo):
			result.append({'number':str(x+1), 'active':str(True) })
		else:
			result.append({'number':str(x+1), 'active':str(False)})
	return result


if __name__ == "__main__":
	app.debug = True
	app.run()
