// Derived from https://github.com/sheppard/python-requirejs

let context = this;

window = {
	'dialogBuilder': {}
};

var console = {
    'history': [],
    'log': function() {
        console.history.push([].map.call(arguments, function(cell) {
            return "" + cell;
        }).join(' '));
    },
    'get': function(key) {
    	return console[key];
    }
};

var define = function(modules, callback) {
	var new_modules = [];
	
	for (var i = 0; i < modules.length; i++) {
		if (modules[i] == 'cards/node') {
			modules[i] = 'Node';
		}

		if (context[modules[i]] != undefined) {
			new_modules.push(context[modules[i]]);
		} else {
			new_modules.push('?');
		}
	}

	var module = callback.apply(null, new_modules);
	
	if (module != undefined) {
		if (module.name != undefined) {
			context[module.name] = module;
		} else if (module.loadSequence != undefined) {
			context['sequence'] = module;
		}
	}
};
