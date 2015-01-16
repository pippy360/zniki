
#fixme: ATM it uses fileId rather than the searchableId, fix that

#TODO: create a function called getthumbnail that checks cache if not there then createsthumbnail

from flask import send_file
import os.path
import Image
import math
from database   import databaseFunctions, databaseObjects

thumbnailCacheFolder = './static/cache/'

def handleThumbnailRequest( request ):
  height  = int( request.args['height'] )
  thumbWidth   = int( request.args['width'] )

  fileId = request.args.get('fileId')
  if fileId != None:    
    fileInfo = databaseFunctions.getFileInfo( fileId )
    print 'fileInfo'
    print fileInfo
    if fileInfo['fileType'] == databaseObjects.FileTypes.image:
      thumbPath = createImageThumbnail( fileInfo['fileLocation'], fileInfo['filename'], (thumbWidth,height) )
    elif fileInfo['fileType'] == databaseObjects.FileTypes.video:
      thumbPath = createVideoThumbnail( fileInfo['fileLocation'], fileInfo['filename'], (thumbWidth,height) )
    else:
      print 'ERROR: BAD FILETYPE : ' + fileInfo['fileType'] 
  else:
    imageLocation = request.args['imageLocation']
    imageFilename = request.args['imageFilename']
    thumbPath = createImageThumbnail( imageLocation, imageFilename, (thumbWidth,height) )

  return send_file( thumbPath, mimetype='image/png')


def createImageThumbnail( imageLocation, imageFilename, thumbSize, maintainAspectRatio=True ):
  orginalImg = Image.open( imageLocation + imageFilename )
  imageSize = orginalImg.size

  if maintainAspectRatio:
    thumbSize = calcThumbnailSize( imageSize, thumbSize )

  thumbPath = thumbnailCacheFolder + genThumbFilename( imageFilename, thumbSize )
  #check if thumbnail is in cache
  if os.path.isfile( thumbPath ):
    return thumbPath

  thumb = orginalImg.resize( thumbSize, Image.ANTIALIAS )
  thumb.save( thumbPath )

  return thumbPath


def genThumbFilename( imageFilename, thumbSize ):
  #rip the extension
  filename, fileExtension = os.path.splitext( imageFilename )
  return "thumbnail_{0}_{1}_{2}{3}".format( filename, thumbSize[0], thumbSize[1], fileExtension )


def calcThumbnailSize( imageSize, thumbSize ):
  x, y = imageSize

  if x > thumbSize[0]:
    y = max(y * thumbSize[0] / x, 1)
    x = thumbSize[0]

  if y > thumbSize[1]:
    x = max(x * thumbSize[1] / y, 1)
    y = thumbSize[1]

  return x, y

def createVideoThumbnail( videoLocation, videoFilename, thumbSize, maintainAspectRatio=True ):
  #you need to know the video dimensions if we want to maintainAspectRatio
  return None


