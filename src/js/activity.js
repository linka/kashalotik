/*
	Switches classes for the element, given itself or by id. If any class is none, 
	turnes always the one available.
*/
function switchclass(elem, primClass, secClass) {
	if (typeof(elem) == "string") {
		elem = document.getElementById(elem);
	}
	
	if (elem == null) {
		return;
	}
	
	if (primClass == null)
		elem.className = secClass;
	else if (secClass == null)
		elem.className = primClass;
	else if (elem.className == primClass)
		elem.className = secClass;
	else
		elem.className = primClass;
};

function setlink(srcElemId, targetElemId, lnkBase) {
	var keycode;
	if (window.event) keycode = window.event.keyCode;
	else if (e) keycode = e.which;
	else return true;
	if (keycode == 13)
	{       
		location.replace(document.getElementById(targetElemId).href);
	}
	else
	{
		var elem = document.getElementById(srcElemId);
		document.getElementById(targetElemId).href = lnkBase + encodeURI(elem.value);
	}
}

function setFocus(elemId) {
	document.getElementById(elemId).focus();
}

function correctsize(srcElemId, targetElemId) {
	var target = document.getElementById(targetElemId);
	var src = document.getElementById(srcElemId);
	var height = src.offsetHeight;
	target.height = height;
}

function findDescByAttr(element, attrName, attrVal) {
	if ( element.hasChildNodes() ) {
		var nodes = element.childNodes;
		for (var i=0; i < nodes.length; i++) {
			try {
				if (nodes[i].getAttribute(attrName) == attrVal) {
						return nodes[i];
				}
			}
			catch (e) {}
			
			if ( nodes[i].hasChildNodes() ) {
				var res = findDescByAttr(nodes[i], attrName, attrVal);
				if (res != null) {
					return res;
				}
			}
		}
	}
	return null;
}

function dosort(sortElemId, sortClassPas, sortClassAct,
								targetParentId, childTagFilter, targetSortId, valueType) {
	var sortElem = document.getElementById(sortElemId);
	// Clear all sortings first
	var sortings = sortElem.parentNode.childNodes; 
	for (var i=0; i < sortings.length; i++) {
		if (sortings[i].nodeName == "A") {
			switchclass(sortings[i].id, sortClassPas, null);
		}
	}
	
	// Set current sorting as active
	switchclass(sortElemId, sortClassAct, null);
	
	// Get direction
	var direction = 1;
	var dirElem = findDescByAttr(sortElem, "name", "direction");
	if (dirElem.className == "down") {
		direction = -1;
	}
	// Switch direction class to next
	switchclass(dirElem, "down", "up");
	
	// Order elements in necessary direction
	orderElements(targetParentId, childTagFilter, direction, targetSortId, valueType);
}

function orderElements(parentid, childTag, direction, sortid) {
	var parent = document.getElementById(parentid);
	var elems = new Array();
	var nodes = parent.childNodes;
	for (var i=0; i < nodes.length; i++) {
		if (nodes[i].nodeName == childTag) {
			elems.push(nodes[i]);
		}
	}
	
	var toRem = elems.slice(0);
	for (var i=0; i < toRem.length; i++) {
		parent.removeChild(toRem[i]);
	}
	toRem = null;
	
	function cmpFunc(e1, e2) {
		var tmp1 = findDescByAttr(e1, "id", sortid);
		var tmp2 = findDescByAttr(e2, "id", sortid);
		
		var c1 = (tmp1 != null) ? new String(tmp1.innerHTML) : '↑'; 
		var c2 = (tmp2 != null) ? new String(tmp2.innerHTML) : '↑';
		
		return direction * c1.localeCompare(c2);
	}
	
	elems.sort(cmpFunc);
	
	for (var i=0; i < elems.length; i++) {
		parent.appendChild(elems[i]);
	}
	
	elems = null;
}

/* Set cookies */
function setCookie(name, value, exdays)
{
	var exdate = new Date();
	exdate.setDate(exdate.getDate() + exdays);
	var cookie_value = escape(value) + ((exdays==null) ? "" : "; expires="+exdate.toUTCString());
	document.cookie = name + "=" + cookie_value;
}

/*
	Activates input place holders for Firefox and IE. Should be loaded 
	with window.
	
	3rd party.
*/
function activatePlaceholders() {
	var detect = navigator.userAgent.toLowerCase(); 
	
	if (detect.indexOf("safari") > 0) return false;
	
	var inputs = document.getElementsByTagName("input");
	for (var i=0;i<inputs.length;i++) {
		if (inputs[i].getAttribute("type") == "text") {
			if (inputs[i].getAttribute("placeholder") && inputs[i].getAttribute("placeholder").length > 0) {
				inputs[i].value = inputs[i].getAttribute("placeholder");
				inputs[i].onclick = function() {
					if (this.value == this.getAttribute("placeholder")) {
					this.value = "";
					}
				return false;
				}
				inputs[i].onblur = function() {
					if (this.value.length < 1) {
						this.value = this.getAttribute("placeholder");
					}
				}
			}
		}
	}
};


