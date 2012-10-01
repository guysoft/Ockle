var CanvizUtils = function() {
}

CanvizUtils.escapeHtml = function(str) {
	return str.escapeHTML();
}

CanvizUtils.writeAttribute = function(e, attr, val) {
	return e.writeAttribute(attr, val);
}

CanvizUtils.setStyle = function(e, styles) {
	return e.setStyle(styles);
}

CanvizUtils.createElement = function(type, attrs) {
	return new Element(type, attrs);
}

CanvizUtils.setHtml = function(e, content) {
	return e.update(content);
}

CanvizUtils.setOpacity = function(e, o) {
	return jQuery(e).fadeTo(0, o);
}

CanvizUtils.bind = function(o, f) {
    return f.bind(o);
}

CanvizUtils.ajaxGet = function(url, params, onComplete) {
	// Canviz receives directly the text as the callback parameter
	// so we extract the text here
	var extractor = function(response) { 
		onComplete(response.responseText) 
	};
	new Ajax.Request(url, {
		method: 'get',
		parameters: params,
		onComplete: extractor
	});
}

CanvizUtils.extend = function(destination, source) {
	Object.extend(destination, source);
}

CanvizUtils.createClass = function() {
	return Class.create.apply(null, arguments);
}
