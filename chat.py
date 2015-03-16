from flask import Flask
from database import databaseFunctions
import random

#chats are tied to posts and involve two participants:
#at some point in the past, the *poster* has made a post (either the start of a new thread, or a reply)
#the *initiator* sees the post and begins a chat instance with the poster, about that specific post (and board)

#the chat instance gets an id
#hence, each unique (boardId, postId, initiatorId) tuple is a unique chat, and can be identified by its corresponding chatId

#the chat instance has a state counter, which is incremented on every reply

#the server has the final say on the ordering of messages
#so that if the client sent a message but it was not yet seen by the server
#and the server got a reply from the other participant,
#even if that reply was typed after the first one,
#the newer reply will be recorded in the log as being received before the older one

#however, this strict ordering is not enforced client side, since once a reply is typed, it will not be moved around

#the clients maintain their own state counters, which represent that state of the local chat log
#clients can request historical replies up to a point.

#say, when a user logs in on a different computer/browser/clears their offline data,
#the entire (recent) chat history must be downloaded

#TODO: redis backend
#probably best to use the pub/sub system since it is scalable

class Chat:
	chats = {} #chatId -> Chat
	byUser = {} #userId -> [Chat] the user is a participant of
	bpf = {} #(boardId, postId, fromId) -> Chat

	def __init__(self, chatId, fromId, toId, boardId, postId):
		self.id = chatId

		#user initiating the chat
		self.fromId = fromId

		#user receiving the initiation
		self.toId = toId

		#what the chat is about (something that toId wrote)
		self.boardId = boardId
		#self.threadId = threadId #not sure it's possible to get a threadId from a postId right now
		self.postId = postId

		#actual state of the chat
		self.state = 0

		#entire chat log
		self.log = [] #(state, sender, message)

	def __repr__(self):
		return "%s to %s, id: %s, state %d" % (self.fromId, self.toId, self.id, self.state)

	def post(self, sender, message):
		self.state += 1
		self.log.append((self.state, sender, message, ))



#returns the chatId
def getChatId(boardId, postId, initiatorId):
	key = (boardId, postId, initiatorId)
	if key in Chat.bpf:
		return Chat.bpf[key].id

	else:
		return None

#this will probably be changed to thread-info like object
def getChatInfo(chatId):
	if chatId in Chat.chats:
		return Chat.chats[chatId]

	else:
		return None

#returns whether the chat exists and the user is part of it
def isUserInChat(userId, chatId):
	if chatId not in Chat.chats:
		return False

 	ch = Chat.chats[chatId]
 	if userId != ch.fromId and userId != ch.toId:
 		return False

 	return True

def getAllChatsWithUser(userId):
	ret = []
	if userId in Chat.byUser:
		for ch in Chat.byUser[userId]:
			ret.append(ch.id)

	return ret

#all parameters must be valid and chat must not exist already
def beginChat(boardId, postId, initiatorId, receiverId):
	#TODO: id generation could be done in a differently
	chatId = '0'
	while chatId in Chat.chats:
		chatId = str(random.randint(1, 10000))

	ch = Chat(chatId, initiatorId, receiverId, boardId, postId)
	Chat.chats[chatId] = ch

	if initiatorId in Chat.byUser:
		Chat.byUser[initiatorId].append(ch)
	else:
		Chat.byUser[initiatorId] = [ch]

	if receiverId in Chat.byUser:
		Chat.byUser[receiverId].append(ch)
	else:
		Chat.byUser[receiverId] = [ch]

	Chat.bpf[(boardId, postId, initiatorId)] = ch

	return chatId

def endChat(chatId):
	assert chatId in Chat.chats

	ch = Chat.chats[chatId]
	del Chat.chats[chatId]
	del Chat.bpf[(ch.boardId, ch.postId, ch.fromId)]
	Chat.byUser[ch.fromId].remove(ch)
	Chat.byUser[ch.toId].remove(ch)


#chat must exist and userId must be a participant of the chat
#returns the new state of the chat
def postInChat(chatId, userId, message):
	ch = Chat.chats[chatId]
	assert ch != None
	assert isUserInChat(userId, chatId)

	ch.post(userId, message)
	return ch.state

#chat must exist
#returns updates newer than currentState
def getUpdates(chatId, userId, currentState):
	ch = Chat.chats[chatId]
	assert ch != None

	ret = {}
	if currentState < ch.state:
		for (state, sender, message) in ch.log:
			if state > currentState:
				direction = 0 if sender == userId else 1
				ret[state] = (direction, message)

	return ret