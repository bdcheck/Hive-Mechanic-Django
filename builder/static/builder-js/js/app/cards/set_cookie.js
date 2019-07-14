var modules = ["material", 'cards/node', 'jquery', ];

define(modules, function (mdc, Node) {
    class SetCookieNode extends Node {
        constructor(definition, sequence) {
            super(definition, sequence);
        }

        editBody() {
            var body = '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12">' +
                       '  <div class="mdc-text-field mdc-text-field--outlined" id="' + this.cardId + '_cookie_name_field" style="width: 100%">' + 
                       '    <input class="mdc-text-field__input"style="width: 100%" id="' + this.cardId + '_cookie_name_value" />' + 
                       '    <div class="mdc-notched-outline">' + 
                       '      <div class="mdc-notched-outline__leading"></div>' + 
                       '      <div class="mdc-notched-outline__notch">' + 
                       '        <label for="' + this.cardId + '_cookie_name_value" class="mdc-floating-label">Cookie Name</label>' + 
                       '      </div>' + 
                       '      <div class="mdc-notched-outline__trailing"></div>' + 
                       '    </div>' + 
                       '  </div>' + 
                       '</div>' + 
                       '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12">' +
                       '  <div class="mdc-text-field mdc-text-field--outlined" id="' + this.cardId + '_cookie_value_field" style="width: 100%">' + 
                       '    <input class="mdc-text-field__input" style="width: 100%" id="' + this.cardId + '_cookie_value_value" />' + 
                       '    <div class="mdc-notched-outline">' + 
                       '      <div class="mdc-notched-outline__leading"></div>' + 
                       '      <div class="mdc-notched-outline__notch">' + 
                       '        <label for="' + this.cardId + '_cookie_value_value" class="mdc-floating-label">Cookie Value</label>' + 
                       '      </div>' + 
                       '      <div class="mdc-notched-outline__trailing"></div>' + 
                       '    </div>' + 
                       '  </div>' + 
                       '</div>' + 
                       '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-7 mdc-typography--caption" style="padding-top: 8px;">' +
                       '  The cookie will be set and the system will proceed to the next action.' +
                       '</div>' +
                       '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-5" style="padding-top: 8px; text-align: right;">' +
			    	   '  <button class="mdc-icon-button" id="' + this.cardId + '_next_edit">' +
                       '    <i class="material-icons mdc-icon-button__icon" aria-hidden="true">create</i>' +
    			       '  </button>' + 
				       '  <button class="mdc-icon-button" id="' + this.cardId + '_next_goto">' +
				       '    <i class="material-icons mdc-icon-button__icon" aria-hidden="true">navigate_next</i>' +
				       '  </button>' +
	    		       '</div>' +
		    	       '<div class="mdc-dialog" role="alertdialog" aria-modal="true" id="' + this.cardId + '-edit-dialog"  aria-labelledby="' + this.cardId + '-dialog-title" aria-describedby="' + this.cardId + '-dialog-content">' +
			           '  <div class="mdc-dialog__container">' +
			           '    <div class="mdc-dialog__surface">' +
    			       '      <h2 class="mdc-dialog__title" id="' + this.cardId + '-dialog-title">Choose Destination</h2>' +
	    		       '      <div class="mdc-dialog__content" id="' + this.cardId + '-dialog-content">';

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
			return '<div class="mdc-typography--body1" style="margin: 16px;">' + this.definition['cookie'] + ' = ' + this.definition['value'] + '</div>';
        }

        initialize() {
			super.initialize();
			
			const me = this;

			const nameField = mdc.textField.MDCTextField.attachTo(document.getElementById(this.cardId + '_cookie_name_field'));
			nameField.value = this.definition['cookie'];

			$('#' + this.cardId + '_cookie_name_value').on("change keyup paste", function() {
				var value = $('#' + me.cardId + '_cookie_name_value').val();
				
				me.definition['cookie'] = value;
				
				me.sequence.markChanged(me.id);
			});

			const valueField = mdc.textField.MDCTextField.attachTo(document.getElementById(this.cardId + '_cookie_value_field'));
			valueField.value = this.definition['value'];

			$('#' + this.cardId + '_cookie_value_value').on("change keyup paste", function() {
				var value = $('#' + me.cardId + '_cookie_value_value').val();
				
				me.definition['value'] = value;
				
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

		updateReferences(oldId, newId) {
			if (this.definition['next'] == oldId) {
				this.definition['next'] = newId;
			}
		}

        destinationNodes(sequence) {
			var nodes = super.destinationNodes(sequence);

			for (var i = 0; i < sequence.definition['items'].length; i++) {
				var item = sequence.definition['items'][i];

				if (this.definition['next'] == item['id']) {
					nodes.push(Node.createCard(item, sequence));
				}
			}

			return nodes;
        }

		cardType() {
			return 'Set Cookie';
		}

		static cardName() {
			return 'Set Cookie';
		}

		static createCard(cardName) {
			var card = {
				"name": cardName, 
				"type": "set-cookie", 
				"cookie": "cookie-name",
				"value": "cookie-value",
				"id": Node.uuidv4()
			}; 
			
			return card;
		}
    }

    Node.registerCard('set-cookie', SetCookieNode);
    
    return SetCookieNode;
});