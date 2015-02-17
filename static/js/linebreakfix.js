String.prototype.chunk = function(n) {
    var ret = [];
    for(var i=0, len=this.length; i < len; i += n) {
       ret.push(this.substr(i, n))
    }
    return ret
};

$( document ).ready(function(){
	$('.threadFirstPostMessage').each(function(){
		$(this).html( $(this).html().chunk(35).join("<wbr></wbr>") )
	})
	$('.postMessage').each(function(){
		$(this).html( $(this).html().chunk(35).join("<wbr></wbr>") )
	})
})