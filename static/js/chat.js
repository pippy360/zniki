
function chat(elem) {
	self.elem = elem;
	self.chatId = null;
	self.adminId = null;
	self.pollIntervalId = null;
}

chat.prototype.poll = function() {
	//$.ajax()
}

chat.prototype.post = function() {

}

$(document).ready(function() {
	$('#chat-toggle').click(function() {
		var container = $('#chat-container');
		if (!container.is(":visible")) {
			if (container.children().length > 0) {
				container.show();
			}
		}
		else {
			container.hide();
		}
	});
});