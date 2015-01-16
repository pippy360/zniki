#FIXME: THE TEMP FILES AREN'T BEING REMOVED
import time
import random
import base64
import hashlib
import shutil
import os
from database   import databaseFunctions
from processing import detect

MAX_FILE_SIZE = 1000000#TODO: GET THIS FROM 


#the idea here is that we want to keep the temp files not publicly accessible
filesLocation = './static/storage/'
tempDir       = './static/temp/'
def hanldeUploadFormSubmit(request, boardId, threadId, postId):
  status = {
    'isValid': False,
    'reason': '',#human readable Error/Reason isValid is false
    'databaseId': '',#file Id not to be decided until 
    'fileInfo': {}
  }
  print request.files
  print request.form
  f       = request.files['photo']
  status  = handleRecivedFile(f, tempDir, filesLocation, status)
  return databaseFunctions.addFileToDatabase(boardId, threadId, postId, status['fileInfo'], "10.0.0.1")

#this takes in a flask fileStorageObj, moves it to a hidden (from public access) folder
#then it checks if it's a valid file and if so it moves it to it's finalLocation
#it it's invalid then it's deleted
def handleRecivedFile( fileStorageObj, tempHiddenLocation, finalLocation, status ):
  path = saveTempFile( fileStorageObj )
  status['fileInfo'] = getFileInfo( path )
  status['fileInfo']['fileLocation'] = finalLocation
  
  status = isValidFile( status['fileInfo'], status )
  if status['isValid']:
    shutil.move(path, os.path.join(finalLocation, status['fileInfo']['filename']) )
  else:
    os.remove(path)

  return status

def saveTempFile( fileStorageObj ):
  fileHash = getBeautifulHash( fileStorageObj );
  fileName, fileExtension = os.path.splitext( fileStorageObj.filename )
  fileStorageObj.seek( 0 )#otherwise it writes a 0 byte file
  path = os.path.join(tempDir, fileHash+fileExtension)
  fileStorageObj.save( path )
  return path

def handleExistingFile( fileInfo ):
  return databaseFunctions.getFileIdByHash( fileInfo['hash'] )

def getVisuallyIdenticalFile( fingerprint ):
  #compare the fingerprint with the stored ones and find an exact match
  return None

def getFileInfo( path ):
  result = detect.detect( path )

  result['size'] = os.path.getsize(path)
  f = open( path )
  f.seek(0)

  result['hash'] = getBeautifulHash( f )
  #get extension, just get it from the filename ATM
  fileName, fileExtension = os.path.splitext( path )
  result['extension'] = fileExtension

  result['filename'] = result['hash'] + result['extension']

  result['visualFingerprint'] = calcVisualFingerprint( f )
  #then just the file type specific stuff
  #put type specific stuff into functions

  f.close()
  return result

def calcVisualFingerprint( f ):
  pass

#TODO: USE THIS
def getBasicFileInfo():
  pass

def getBeautifulHash( f ):
  tempHash = get_hash( f )
  return to_id( tempHash )

def get_hash(f):
  f.seek(0)
  return hashlib.md5(f.read()).digest()

def isValidFile( fileInfo, status ):
  if fileInfo['size'] < 0:
    status['isValid'] = False
    status['reason']  ='File Size less than 0 ??? WTF ???'
  elif fileInfo['size'] > MAX_FILE_SIZE:
    status['isValid'] = False
    status['reason']  = 'File too big!'
  elif not fileInfo['type'] in ['image','video']:#FIXME: hardcoded, also gifs are video !
    status['isValid'] = False
    status['reason']  = 'File is not a valid image! file type detected ' + fileInfo['type']
  else:
    status['isValid'] = True
  
  return status

def getNewFileId():
  #the number of the file uploaded,
  #TODO: make the file ID system easy enough that people can write down the values manually
  pass

to_id = lambda h: base64.b64encode(h)[:12].replace('/', '_').replace('+', '-')
