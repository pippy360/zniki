import globalDatabase
import projectDatabase
import fileDatabase
import tagDatabase

def addNewProject(creatorId, title, shortDescription, longDescription, 
				gitUrl, wikiUrl, attachedFileId, tags):
	#TODO: replace with get threadId()
	projectId = getNewId()
	projectDatabase.addNewProject(projectId, creatorId, title, shortDescription, 
		longDescription, gitUrl, wikiUrl, attachedFileId, tags);
	globalDatabase.addProjectIdToProjectList(projectId)
	tagDatabase.addTagsToProject(projectId, tags)
	return projectId

def getProjectListRange(start, end):
	return globalDatabase.getProjectListRange(start, end)

def addFileToDatabase(fileInfo, creatorIP):
	pass

def getThreadInfo(projectId):
	return projectDatabase.getProjectInfo(projectId)

def getProjectInfo(projectId):
	return projectDatabase.getProjectInfo(projectId)

def getNewId():
	globalDatabase.incrementProjectCount()
	return str(globalDatabase.getProjectCount())

def getProjectCount():
	return globalDatabase.getProjectCount()