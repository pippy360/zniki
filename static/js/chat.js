function generateChatHTML(idName, partnerName, partialResponse, boardId, postId) {
	//TODO: have a link or something instead
	var about = "about post " + postId + " at board " + boardId;

	return '' +
	'<li id="' + idName + '"><div class="chat-container">' + 
	'  <div class="chat-errors></div>' +
	'  <div class="chat-header"><span>Chat with ' + partnerName + '</span><span class="chat-close-button"><a>close</a></span>' + 
	'    <span class="chat-header-about"></br>' + about + '</span>' +
	'  </div>' +
	'  <div class="chat-log"></div>' +
	'  <div class="chat-status"></div>' +
	'  <textarea class="chat-text-input">' + partialResponse + '</textarea>' +
	'</div></li>';
}

function generateReplyHTML(idName, handle, text, pending) {
	return '' +
	'<div id="' + idName + '" class="chat-log-entry">' +
	(pending? '<span class="fa fa-refresh fa-spin"></span>' : '') + 
	'  <span class="chat-log-handle">' + handle + ':</span>' +
	'  <span class="chat-log-text">' + text + '</span>' +
	'</div>';
}

//elem: jQuery selector on chat div
//only call this once the server has legitimized the chat (has given us a chatId)
function ChatLogic(elem, chatId, partnerName, boardId, postId, initialMode) {
	this.mode = initialMode;

	this.elem = elem;
	this.logElem = elem.find(".chat-log");
	this.statusElem = elem.find(".chat-status");
	this.entryElem = elem.find("textarea");

	this.partnerName = partnerName;
	this.chatId = chatId;
	this.boardId = boardId;
	this.postId = postId;

	//number of replies received
	this.state = 0;

	//used in closures below
	var logicThis = this;

	this.entryElem.keydown(function(ev) {
		if (ev.which == 13) { //enter key
			ev.preventDefault();
			var text = logicThis.entryElem.val();

			if (text.length > 0 && logicThis.mode == "active") {
				//put it in the local chat log, but with a "confirmation pending" marker
				var debugText = '' + (logicThis.state+1) + '|' + text;
				var pendingReplyHTML = generateReplyHTML("chat-" + logicThis.chatId + '-' + (logicThis.state+1), "me", debugText, true);
				logicThis.logElem.append(pendingReplyHTML);
				var postDiv = logicThis.logElem.children().last();
				logicThis.entryElem.val(""); //clear the field
				logicThis.postMessage(text, postDiv, 1500);
				logicThis.scrollToBottom();
			}
		}
	});

	var closeButton = this.elem.find(".chat-close-button > a");
	closeButton.click(function(ev) {
		logicThis.logMessage("user requested we close");
		logicThis.endChat("user requested");
	});
}

ChatLogic.prototype.logMessage = function(str) {
	console.log('chat id ' + this.chatId + ', with ' + this.partnerName + ', on board ' + this.boardId + ', about post ' + this.postId + ' -> ' + str);
}

ChatLogic.prototype.postMessage = function(text, div, timeout) {
	$.ajax("/chatPost", {
		type: "POST",
		//accepts: "text/event-stream",
		async: true,
		cache: false,
		context: this,
		contentType: "application/json",
		dataType: "json",
		data: JSON.stringify({
			'chatId': this.chatId, 
			'msg': text
		}),
		timeout: 2500,
		success: function(data, status, jqXHR) {
			//clear the pending marker
			div.find(".fa-refresh").remove();
			this.state = Number(data['state']);
		},
		error: function(jqXHR, status, err) {
			if (jqXHR.status == 403) {
				this.logMessage("server nuked the chat");
				this.die("chat had been ended", 5);
			}
			//this.postMessage(text, div, timeout * 2);
		}
	});
}

ChatLogic.prototype.endChat = function(reason) {
	$.ajax("/chatEnd", {
		type: "POST",
		//accepts: "text/event-stream",
		async: true,
		cache: false,
		context: this,
		contentType: "application/json",
		dataType: "json",
		data: JSON.stringify({
			'chatId': this.chatId,
			'reason': "user request"
		}),
		timeout: 2500,
		success: function(data, status, jqXHR) {
			//clear the pending marker
			this.logMessage("server confirmed chat ended");
			this.die();
		},
		error: function(jqXHR, status, err) {
			if (jqXHR.status == 403) {
				this.logMessage("server nuked the chat");
				this.die();
			}
			else { 
				//some other kind of error, so we better tell the user
				this.elem.find(".chat-errors").append('</br><span>failed to tell the server to end the chat</span>');
			}
		}
	});
} 

ChatLogic.prototype.flash = function(color) {
	if (!color) {
		color = "#fb9";
	}
	var original = this.elem.css("backgroundColor");
	var elem = this.elem;
	elem.show();
	$('#chat-list').show();

	elem.animate({backgroundColor: color}, 300).animate({backgroundColor: original}, 300);
}

ChatLogic.prototype.flashRed = function() {
	this.flash("#fb9");
}

ChatLogic.prototype.flashGreen = function() {
	this.flash("#9fb");
}

ChatLogic.prototype.scrollToBottom = function() {
	this.logElem.scrollTop(this.logElem.prop("scrollHeight"));
}

//local only chat deletion
ChatLogic.prototype.die = function(message, timeout) {
	if (message) {
		this.elem.find(".chat-errors").append('</br><span>' + message + '</span>');
		var errorIndicator = this.elem.find(".chat-errors").find("span:last");
	}

	if (!timeout) {
		timeout = 0;
	}

	if (timeout > 0) {
		var logic = this;
		var intervalId = window.setInterval(function() {
			errorIndicator.html(message + "</br>self desutrct in " + timeout);
			timeout--;

			if (timeout < 0) {
				window.clearInterval(intervalId);
				logic.elem.slideUp(function() {
					$(this).remove(); //this destroys the entire chat div, including the logic object
				}); 
			}
		}, 1000);
	}
	else {
		this.elem.slideUp(function() {
			$(this).remove(); //this destroys the entire chat div, including the logic object
		}); 
	}
}

/*ChatLogic.prototype.receiveReply = function(newState, reply) {
	this.logMessage("received reply");
}*/



/* TODO
try {
	this.webSocket = new EventSource(this.sourceUrl);
}

if (this.webSocket) {
	this.webSocket.onmessage = function(msg) {
		var match = msg.match(/^(\d+):(.*)$/);
		if (match) {
			this.receiveReply(match[1], match[2]);
		}
		else {
			logicThis.logMessage("bad message form server:" + msg);
		}
	}

	this.webSocket.onerror = function(e) {
		logicThis.logMessage("event source error");
			//TODO: try to restart or something
		}
}
*/

function handleChatUpdates(data) {
	//TODO: local states are already collected in the poll function, 
	//but it's more correct to collect them again; it should be ok
	var chatList = $("#chat-list");
	var localStates = {};

	chatList.children().each(function() {
		var logic = $(this).data("logic");
		if (logic.mode == "active") {
			localStates[logic.chatId] = logic.state;
		}
	});

	var endedChats = $.extend({}, localStates);
	var newChats = {};
	var chatList = $("#chat-list");

	for (var chatId in data) {
		if (!(chatId in localStates)) {
			//new chat
			var info = data[chatId];
			newChats[chatId] = info;

			console.log("new chat we didn't know about, with " + info['partnerName']);

			//create chat UI
			var newChatId = "chat-" + chatId;
			var newChatHTML = generateChatHTML(newChatId, info['partnerName'], "", info['boardId'], info['postId']);
			chatList.append(newChatHTML);

			var elem = $('#' + newChatId);
			var logic = new ChatLogic(elem, chatId, info['partnerName'], info['boardId'], info['postId'], "active");
			elem.data("logic", logic);
			logic.flashRed();

			chatList.show(); //@@
		}
		else {
			delete endedChats[chatId];
		}
	}

	//now endedChats contains chats we have locally but that the server implies have ended
	//so remove them; TODO: don't remove them directly, tell the user why this happened
	for (var chatId in endedChats) {
		var chatElem = $('#chat-' + chatId);
		var logic = chatElem.data("logic");
		logic.logMessage("we're being nuked");
		logic.die("server ended chat");
	}

	//finally, receive updates
	for (var chatId in data) {
		var updates = data[chatId]['updates'];
		var chatElem = $('#chat-' + chatId);
		var logic = chatElem.data("logic");
		var handles = [
			"me", //me
			logic.partnerName //them
		];

		if (!$.isEmptyObject(updates)) {
			logic.logMessage("got updates");

			for (var updateState in updates) {
				var dir = updates[updateState][0];
				var msg = updates[updateState][1];
				msg = updateState + '|' + msg; //DEBUG, for now

				var existing = chatElem.find('#' + chatId + '-' + updateState);
				if (existing.length == 1) {
					var existingText = existing.find('.chat-log-text').text();
					existing.find(".fa-refresh").remove(); //the pending indicator

					if (existingText != msg) {
						logic.logMessage('update #' + updateState + ' has a different content than our local one');
						existingText.text(msg);
					}
				}
				else if (existing.length == 0) {
					//reply does not exist locally, so add it
					var replyHTML = generateReplyHTML(chatId + '-' + updateState, handles[dir], msg, false);
					logic.logElem.append(replyHTML);
					logic.scrollToBottom();
				}
				else {
					//wtf
					logic.logMessage("!!! multiple replies with the same state !!!");
				}

				//TODO: maybe it's not safe to assume that the last update will have the highest state
				logic.state = Number(updateState);
			}
		}
	}
}

$CHAT_POLL_TIMEOUT_ID = null;
function chatPoll(timeout, again) {
	var chatList = $("#chat-list");
	var localStates = {};

	chatList.children().each(function(elem) {
		var logic = $(this).data("logic");
		if (logic.mode == "active") {
			localStates[logic.chatId] = logic.state;
		}
	});

	$.ajax("/chatPoll", {
		type: "POST",
		accepts: "text/event-stream",
		async: true,
		cache: false,
		contentType: "application/json",
		dataType: "json",
		data: JSON.stringify({'states': localStates}),
		timeout: timeout,
		success: function(data, status, jqXHR) {
			handleChatUpdates(data);
			if (timeout > 300) {
				timeout -= 100;
			}
			if (again) {
				$CHAT_POLL_TIMEOUT_ID = window.setTimeout(function() {
					chatPoll(timeout, again); //subtractive decrease
				}, 1000);
			}
		},
		error: function(jqXHR, status, err) {
			console.log("chat polling error: " + status + "; " + err);
			if (status == "timeout" && again) {
				//retry with longer timeout
				timeout = Math.floor(timeout * 1.5); //multiplicative increase

				if (again) {
					$CHAT_POLL_TIMEOUT_ID = window.setTimeout(function() {
						chatPoll(timeout, again); //subtractive decrease
					}, 1000);
				}
			}
		}
	});
}

function beginChat(boardId, postId, partnerName) {
	var chatList = $("#chat-list");
	chatList.show();

	//first make sure the chat about this board/post doesn't already exist
	var existingLogic = null;
	chatList.each(function() {
		var logic = $(this).data("logic");
		if (logic.boardId == boardId && logic.postId == postId) {
			existingLogic = logic;
			return false; //stop looping
		}
	});

	if (existingLogic) {
		existingLogic.flashGreen();
		existingLogic.entryElem.focus();
		return;
	}

	//initialize html
	var elemId = 'chat-new-' + chatList.children().length;
	var listItemHTML = generateChatHTML(elemId, partnerName, "", boardId, postId);
	chatList.append(listItemHTML);

	var listItem = $("#" + elemId);
	var chatLogicInst = new ChatLogic(listItem, "-1", partnerName, boardId, postId, "starting");
	listItem.data("logic", chatLogicInst);

	//only show the header until the chats is legitimized
	var header = listItem.find(".chat-header");
	header.find("span:first").text("Starting chat with " + partnerName);
	header.nextAll().hide();

	$.ajax("/chatBegin", {
		type: "POST",
		//accepts: "text/event-stream",
		async: true,
		cache: false,
		context: listItem, 
		contentType: "application/json",
		dataType: "json",
		data: JSON.stringify({'boardId': boardId, 'postId': postId}),
		timeout: 2500,
		success: function(data, status, jqXHR) {
			console.log("server legitimized chat with " + partnerName + ", chatId: " + data['chatId'] + ", state: " + data['state']);
			chatLogicInst.chatId = data['chatId'];
			chatLogicInst.mode = "active";

			//change header reveal the rest of the chat elements
			header.find("span:first").text("Chat with " + partnerName);
			header.nextAll().show();
			chatLogicInst.flashGreen();
			chatLogicInst.entryElem.focus();

			//TODO: we have the chat state, but we can't be sure we also have all the replies, so keep the local chat state to whatever it was
			//(by default, 0)

			//rename li element for easier selection
			this.attr("id", "chat-" + data['chatId']);
			this.fadeTo(0, 1);
		},
		error: function(jqXHR, status, err) {
			chatLogicInst.logMessage("begin chat: " + status + '; ' + err);
			chatLogicInst.die("failed to begin chat", 5);

			//TODO: retry maybe
		}
	});
}

$(document).ready(function() {
	//enable chat functionality
	$('#chat-panel').show(); //TODO: might keep this hidden (and hide it later on) if there are no active chats
	$('#chat-list').hide();

	$('#chat-toggle').click(function() {
		var container = $('#chat-list');
		if (!container.is(":visible")) {
			if (container.children().length > 0) {
				container.show();
			}
		}
		else {
			container.hide();
		}
	});

	//decorate each post header with a chat initiation link
	$('div .postHeader').each(function(index, elem) {
		var t = $(this);
		var postUserSpan = t.find(".postHeaderUsername");
		var postIdSpan = t.find(".postHeaderPostId");

		var postUser = postUserSpan.text().match(/^([^ ]+)/)[1];
		var postId = postIdSpan.text().match(/(\d+)/)[1];

		var chatLink = $(document.createElement('a'));
		chatLink.html("chat");
		chatLink.attr("href", "");
		chatLink.attr("title", "chat with " + postUser + " about this post");
		t.append(chatLink);

		chatLink.click(function(ev) {
			ev.preventDefault(); //don't reload the page
			beginChat($BOARD_ID, postId, postUser); //$BOARD_ID should be set by a little script from thread.html
		});
	});

	//$CHAT_POLL_INTERVAL_ID = window.setInterval(1500, chatPoll);
	//poll for now
	chatPoll(1000, true);
});
