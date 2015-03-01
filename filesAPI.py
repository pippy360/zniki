#FIXME: THE TEMP FILES AREN'T BEING REMOVED
import time
import random
import base64
import hashlib
import shutil
import os
from processing import detect

MAX_FILE_SIZE = 5000000#FIXME: HARDCODED!

#fileInfo here is unused, it's just to show the layout of the dict
fileInfo = {
  'fileLocation': '',
  'extension': '',
  'size': ''
  #todo: finish this
}


#gets the fileinfo and then saves it, 
#returns the fileinfo with the location of the file
#returns a "status" dict (see layout 2 lines below)
def handleUploadFormSubmit(filesMultiDict, tempHiddenLocation="./tempFileStore/", 
                            finalLocation="./static/storage/"):
  status = {
    'isValid': False,
    'reason': '',#human readable Error/Reason isValid is false
    'databaseId': '',#file Id not to be decided until 
    'fileInfo': {}
  }
  f = filesMultiDict['photo']
  return handleRecivedFile(f, tempHiddenLocation, finalLocation, status)
  

#this takes in a flask fileStorageObj, moves it to a hidden (from public access) folder
#then it checks if it's a valid file and if so it moves it to it's finalLocation
#it it's invalid then it's deleted
def handleRecivedFile( fileStorageObj, tempHiddenLocation, finalLocation, status ):
  path = saveTempFile( fileStorageObj, tempHiddenLocation )
  status['fileInfo'] = getFileInfo( path )
  
  if status['fileInfo'] == None:
    status['isValid'] = False
    status['reason'] = 'Error: Bad file type uploaded.'
    os.remove(path)
    return status

  status['fileInfo']['fileLocation'] = finalLocation

  status = isValidFile( status['fileInfo'], status )
  if status['isValid']:
    shutil.move(path, os.path.join(finalLocation, status['fileInfo']['filename']) )
  else:
    os.remove(path)

  return status

def saveTempFile( fileStorageObj, tempHiddenLocation ):
  fileHash = getBeautifulHash( fileStorageObj );
  fileName, fileExtension = os.path.splitext( fileStorageObj.filename )
  fileStorageObj.seek( 0 )#otherwise it writes a 0 byte file
  path = os.path.join(tempHiddenLocation, fileHash+fileExtension)
  fileStorageObj.save( path )
  return path

def handleExistingFile( fileInfo ):
  return databaseFunctions.getFileIdByHash( fileInfo['hash'] )

def getFileInfo( path ):
  result = detect.detect( path )
  if result == None:
    return None

  result['size'] = os.path.getsize(path)
  f = open( path )
  f.seek(0)

  result['hash'] = getBeautifulHash( f )
  #get extension, just get it from the filename ATM
  fileName, fileExtension = os.path.splitext( path )
  result['extension'] = fileExtension

  result['filename'] = result['hash'] + result['extension']

  f.close()
  return result


def getBeautifulHash( f ):
  tempHash = get_hash( f )
  return to_id( tempHash )

def get_hash(f):
  f.seek(0)
  return hashlib.md5(f.read()).digest()

def isValidFile( fileInfo, status ):
  if not fileInfo['type'] in ['image']:#FIXME: hardcoded
    status['isValid'] = False
    status['reason']  = 'Error: File is not a valid image! '
  elif fileInfo['size'] < 0:
    status['isValid'] = False
    status['reason']  ='Error: File Size less than 0 ??? WTF ???'
  elif fileInfo['size'] > MAX_FILE_SIZE:
    status['isValid'] = False
    status['reason']  = 'Error: File too big!'
  else:
    status['isValid'] = True
  
  return status

to_id = lambda h: base64.b64encode(h)[:12].replace('/', '_').replace('+', '-')
