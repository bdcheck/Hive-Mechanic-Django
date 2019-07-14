var modules = ["material", 'cards/node', 'jquery', ];

define(modules, function (mdc, Node) {
	class SendPictureNode extends Node {
		constructor(definition, sequence) {
			super(definition, sequence);
	
			this.messageId = Node.uuidv4();
			this.nextButtonId = Node.uuidv4();
		}

		editBody() {
			var body = '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12">';
			body += '  <img src="' + this.definition['image'] + '" id="' + this.messageId + '_preview" style="max-width: 100%;">';
			body += '</div>';
			body += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-7">';
			body += '  <div class="mdc-text-field mdc-text-field--outlined" id="' + this.messageId + '" style="width: 100%">';
			body += '    <input class="mdc-text-field__input" type="text" id="' + this.messageId + '_value">';
			body += '    <div class="mdc-notched-outline">';
			body += '      <div class="mdc-notched-outline__leading"></div>';
			body += '      <div class="mdc-notched-outline__notch">';
			body += '        <label for="' + this.messageId + '_value" class="mdc-floating-label">Image URL</label>';
			body += '      </div>';
			body += '      <div class="mdc-notched-outline__trailing"></div>';
			body += '    </div>';
			body += '  </div>';
			body += '</div>';
			body += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-5" style="text-align: right;">';
			body += '  <button class="mdc-icon-button" id="' + this.cardId + '_next_edit">';
            body += '    <i class="material-icons mdc-icon-button__icon" aria-hidden="true">create</i>';
    		body += '  </button>';
			body += '  <button class="mdc-icon-button" id="' + this.cardId + '_next_goto">';
			body += '    <i class="material-icons mdc-icon-button__icon" aria-hidden="true">navigate_next</i>';
			body += '  </button>';
			body += '</div>';
            body += '<div class="mdc-dialog" role="alertdialog" aria-modal="true" id="' + this.cardId + '-edit-dialog"  aria-labelledby="' + this.cardId + '-dialog-title" aria-describedby="' + this.cardId + '-dialog-content">';
            body += '  <div class="mdc-dialog__container">';
            body += '    <div class="mdc-dialog__surface">';
            body += '      <h2 class="mdc-dialog__title" id="' + this.cardId + '-dialog-title">Choose Destination</h2>';
			body += '      <div class="mdc-dialog__content" id="' + this.cardId + '-dialog-content">';
            body += this.sequence.chooseDestinationSelect(this.cardId);
            body += '      </div>';
            body += '      <footer class="mdc-dialog__actions">';
            body += '        <button type="button" class="mdc-button mdc-dialog__button" data-mdc-dialog-action="close">';
            body += '          <span class="mdc-button__label">Save</span>';
            body += '        </button>';
            body += '      </footer>';
            body += '    </div>';
            body += '  </div>';
            body += '  <div class="mdc-dialog__scrim"></div>';
            body += '</div>';
            
            return body;
				   
		}

		viewBody() {
			return '<div class="mdc-typography--body1" style="margin: 16px;"><img src="' + this.definition['image'] + '" style="max-width: 100%;"></div>';
		}

		initialize() {
			super.initialize();
			
			const me = this;
	
			const messageField = mdc.textField.MDCTextField.attachTo(document.getElementById(this.messageId));
			messageField.value = this.definition['image'];
	
			$('#' + this.messageId + '_value').change(function(eventObj) {
				var value = $('#' + me.messageId + '_value').val();
		
				me.definition['image'] = value;
		
				$('#' + me.messageId + '_preview').attr('src', value);

				me.sequence.markChanged(me.id);
			});

			const destination = mdc.select.MDCSelect.attachTo(document.getElementById(me.cardId + '_destination'));

			destination.listen('MDCSelect:change', () => {
				console.log('Selected option at index ' + destination.selectedIndex + ' with value "' + destination.value + '"');
				
				if (destination.value == 'add_card') {
					me.sequence.addCard(me.cardId, function(node_id) {
						console.log("ADDED: ", node_id);
					});
				}
			});

			const dialog = mdc.dialog.MDCDialog.attachTo(document.getElementById(me.cardId + '-edit-dialog'));

			dialog.listen('MDCDialog:closed', (event) => {
				this.definition['next'] = destination.value;

				me.sequence.markChanged(me.id);
				me.sequence.loadNode(me.definition);
			});

			$('#' + this.cardId + '_next_edit').on("click", function() {
				if (me.definition["next"] != undefined) {
					destination.value = me.definition["next"];
				}
				
				dialog.open();
			});

			$('#' + this.cardId + '_next_goto').on("click", function() {
				var destinationNodes = me.destinationNodes(me.sequence);
				
				var found = false;
				
				for (var i = 0; i < destinationNodes.length; i++) {
					const destinationNode = destinationNodes[i];

					if (destinationNode["id"] == me.definition["next"]) {
						$("[data-node-id='" + destinationNode["id"] + "']").css("background-color", "#ffffff");
					} else {
						$("[data-node-id='" + destinationNode["id"] + "']").css("background-color", "#e0e0e0");
					}
				}
			});
		}

		destinationNodes(sequence) {
			var nodes = super.destinationNodes(sequence);

			for (var i = 0; i < sequence.definition['items'].length; i++) {
				var item = sequence.definition['items'][i];

				if (this.definition['next'] == item['id']) {
					var node = Node.createCard(item, sequence);

					nodes.push(node);
				}
			}

			return nodes;
		}

		updateReferences(oldId, newId) {
			if (this.definition['next'] == oldId) {
				this.definition['next'] = newId;
			}
		}
		
		cardType() {
			return 'Send Picture';
		}
		
		static cardName() {
			return 'Send Picture';
		}

		static createCard(cardName) {
			var card = {
				"name": cardName, 
				"type": "send-picture", 
				"image": "https://via.placeholder.com/150",
				"id": Node.uuidv4()
			}; 
			
			return card;
		}
	}
	
	Node.registerCard('send-picture', SendPictureNode);
});