var modules = ["material", 'cards/node', 'jquery', ];

define(modules, function (mdc, Node) {
	class ProcessCookieNode extends Node {
		constructor(definition, sequence) {
			super(definition, sequence);
		}

		editBody() {
			return super.editBody();
		}

		viewBody() {
			return super.viewBody();
		}

		initialize() {

		}

		destinationNodes(sequence) {
			var nodes = super.destinationNodes(sequence);

			var patterns = this.definition['patterns'];

			for (var i = 0; i < sequence.definition['items'].length; i++) {
				var item = sequence.definition['items'][i];

				for (var j = 0; j < patterns.length; j++) {
					var pattern = patterns[j];
					
					if (pattern['action'] == item['id']) {
						nodes.push(Node.createCard(item, sequence));
					}
				}
			}

			return nodes;
		}
	}

	Node.registerCard('process-cookie', ProcessCookieNode);
});