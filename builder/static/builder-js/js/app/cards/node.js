var modules = ["material", 'jquery'];

define(modules, function (mdc) {
	class Node {
		constructor(definition, sequence) {
			this.definition = definition;
			this.sequence = sequence;
			this.id = definition['id'];
            this.cardId = Node.uuidv4();
		}

		cardName() {
			if (this.definition['name'] != undefined) {
				return this.definition['name'];
			}

			return this.definition['type'];
		}

		cardType() {
			return this.definition['type'];
		}

		editHtml() {
			var htmlString  = '<div class="mdc-card" id="' + this.cardId + '" style="' + this.style() + '" data-node-id="' + this.id + '">';
				htmlString += '  <div class="mdc-layout-grid" style="margin: 0; padding-left: 16px; padding-right: 16px; padding-bottom: 16px;">';
				htmlString += '    <div class="mdc-layout-grid__inner">';
				htmlString += '      <div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12">';
				htmlString += '        <div class="mdc-typography--caption" style="text-align: right; margin-bottom: 8px;">' + this.cardType() + '</div>';
				htmlString += '        <div class="mdc-text-field mdc-text-field--outlined" id="' + this.cardId + '_name" style="width: 100%">';
				htmlString += '          <input class="mdc-text-field__input" type="text" id="' + this.cardId + '_name_value">';
				htmlString += '          <div class="mdc-notched-outline">';
				htmlString += '            <div class="mdc-notched-outline__leading"></div>';
				htmlString += '            <div class="mdc-notched-outline__notch">';
				htmlString += '              <label for="' + this.cardId + '_name_value" class="mdc-floating-label">Name</label>';
				htmlString += '            </div>';
				htmlString += '            <div class="mdc-notched-outline__trailing"></div>';
				htmlString += '          </div>';
				htmlString += '        </div>';
				htmlString += '      </div>';
				htmlString += '      <div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12">';
				htmlString += '        <div class="mdc-text-field mdc-text-field--outlined" id="' + this.cardId + '_identifier" style="width: 100%">';
				htmlString += '          <input class="mdc-text-field__input" type="text" id="' + this.cardId + '_identifier_value">';
				htmlString += '          <div class="mdc-notched-outline">';
				htmlString += '            <div class="mdc-notched-outline__leading"></div>';
				htmlString += '            <div class="mdc-notched-outline__notch">';
				htmlString += '              <label for="' + this.cardId + '_identifier_value" class="mdc-floating-label">Node ID</label>';
				htmlString += '            </div>';
				htmlString += '            <div class="mdc-notched-outline__trailing"></div>';
				htmlString += '          </div>';
				htmlString += '        </div>';
				htmlString += '      </div>';
				htmlString += this.editBody();
				htmlString += '    </div>';
				htmlString += '  </div>';
				htmlString += '</div>';

			return htmlString;
		}

		initialize() {
			const me = this;

			const nameField = mdc.textField.MDCTextField.attachTo(document.getElementById(this.cardId + '_name'));
			nameField.value = this.cardName();

			$('#' + this.cardId + '_name_value').on("change keyup paste", function() {
				var value = $('#' + me.cardId + '_name_value').val();

				me.definition['name'] = value;
				
				me.sequence.markChanged(me.id);
			});

			const idField = mdc.textField.MDCTextField.attachTo(document.getElementById(this.cardId + '_identifier'));
			idField.value = this.id;

			$('#' + this.cardId + '_identifier_value').on("change paste", function() {
				var value = $('#' + me.cardId + '_identifier_value').val();
				
				console.log("SETTING ID: " + value);
				
				var oldId = me.definition['id'];
				var newId = value;
				
				const sources = me.sourceNodes(me.sequence);

				console.log("SOURCES: " + sources.length);
				
				for (var i = 0; i < sources.length; i++) {
					sources[i].updateReferences(oldId, newId);
				}

				me.definition['id'] = value;

//				me.sequence.updateId(oldId, newId);

				me.sequence.markChanged(me.id);
			});
		}
		
		updateReferences(oldId, newId) {
			console.log('TODO: Implement "updateReferences" in ' + this.cardName());
		}

		editBody() {
			var htmlString  = '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12">';
			    htmlString += this.viewBody();
			    htmlString += '</div>';

			return htmlString
		}

		viewHtml() {
			var htmlString  = '<div class="mdc-card" id="' + this.cardId + '" style="' + this.style() + '"  data-node-id="' + this.id + '">';
				htmlString += '  <h6 class="mdc-typography--headline6" style="margin: 16px; margin-bottom: 0;">' + this.cardName() + '</h6>';
				htmlString += '  <h6 class="mdc-typography--subtitle1" style="margin: 16px; margin-bottom: 0; margin-top: 0;">' + this.id + '</h6>';
				htmlString += this.viewBody();
				htmlString += '</div>';

			return htmlString;
		}

		viewBody() {
			return '<div class="mdc-typography--body1" style="margin: 16px;"><pre>' + JSON.stringify(this.definition, null, 2) + '</pre></div>';
		}


		style() {
			return "background-color: #ffffff; margin-bottom: 10px;";
		}

		destinationNodes(sequence) {
			return [];
		}

		sourceNodes(sequence) {
			var sources = [];

			for (var i = 0; i < sequence.definition['items'].length; i++) {
				var item = sequence.definition['items'][i];

				var node = Node.createCard(item, sequence);

				var destinations = node.destinationNodes(sequence);

				var isSource = false;

				for (var j = 0; j < destinations.length && isSource == false; j++) {
					var destination = destinations[j];

					if (this.id == destination.id) {
						isSource = true;
					}
				}

				if (isSource) {
					sources.push(node);
				}
			}

			return sources;
		}

		onClick(callback) {
			$('#' + this.cardId).click(function(eventObj) {
				callback();
			});
		}
		
//		updateDestination(oldId, newId) {
//			con
//		}

		static createCard(definition, sequence) {
			if (window.dialogBuilder.cardMapping != undefined) {
				var classObj = window.dialogBuilder.cardMapping[definition['type']];

				if (classObj != undefined) {
					return new classObj(definition, sequence);
				}
			}

			return new Node(definition, sequence);
		}

		static canCreateCard(definition, sequence) {
			if (window.dialogBuilder.cardMapping != undefined) {
				var classObj = window.dialogBuilder.cardMapping[definition['type']];

				return (classObj != undefined);
			}

			return false;
		}

		static registerCard(name, classObj) {
			if (window.dialogBuilder.cardMapping == undefined) {
				window.dialogBuilder.cardMapping = {};
			}

			window.dialogBuilder.cardMapping[name] = classObj;
		}

		static uuidv4() {
			return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
				var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
				return v.toString(16);
			});
		}
		
		static cardName() {
			return 'Node';
		}
	}

	return Node;
});