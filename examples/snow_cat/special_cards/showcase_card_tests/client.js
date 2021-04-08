var modules = ["material", 'cards/node', 'jquery'];

define(modules, function (mdc, Node) {
    class SendMessageNode extends Node {
        constructor(definition, sequence) {
            super(definition, sequence);
        }

		cardIcon() {
			return '<i class="fas fa-comment-dots" style="margin-right: 16px; font-size: 20px; "></i>';
		}

        editBody() {
            var body = '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12">' +
                       '  <div class="mdc-text-field mdc-text-field--textarea" id="' + this.cardId + '_message_field" style="width: 100%">' + 
                       '    <textarea class="mdc-text-field__input" rows="4" style="width: 100%" id="' + this.cardId + '_message_value"></textarea>' + 
                       '    <div class="mdc-notched-outline">' + 
                       '      <div class="mdc-notched-outline__leading"></div>' + 
                       '      <div class="mdc-notched-outline__notch">' + 
                       '        <label for="' + this.cardId + '_message_value" class="mdc-floating-label">Message</label>' + 
                       '      </div>' + 
                       '      <div class="mdc-notched-outline__trailing"></div>' + 
                       '    </div>' + 
                       '  </div>' + 
                       '</div>' + 
                       '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-7 mdc-typography--caption" style="padding-top: 8px;">' +
                       '  The message above will be sent to the user and the system will proceed to the next card.' +
                       '</div>' +
                       '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-5" style="padding-top: 8px; text-align: right;">' +
			    	   '  <button class="mdc-icon-button" id="' + this.cardId + '_next_edit">' +
                       '    <i class="material-icons mdc-icon-button__icon" aria-hidden="true">link</i>' +
    			       '  </button>' + 
				       '  <button class="mdc-icon-button" id="' + this.cardId + '_next_goto">' +
				       '    <i class="material-icons mdc-icon-button__icon" aria-hidden="true">search</i>' +
				       '  </button>' +
	    		       '</div>' +
		    	       '<div class="mdc-dialog" role="alertdialog" aria-modal="true" id="' + this.cardId + '-edit-dialog"  aria-labelledby="' + this.cardId + '-dialog-title" aria-describedby="' + this.cardId + '-dialog-content">' +
			           '  <div class="mdc-dialog__container">' +
			           '    <div class="mdc-dialog__surface">' +
    			       '      <h2 class="mdc-dialog__title" id="' + this.cardId + '-dialog-title">Choose Destination</h2>' +
	    		       '      <div class="mdc-dialog__content" id="' + this.cardId + '-dialog-content">';

	    	console.log(this.sequence.chooseDestinationMenu)

            body += this.sequence.chooseDestinationMenu(this.cardId);
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
			return '<div class="mdc-typography--body1" style="margin: 16px;">' + this.definition['message'] + '</div>';
        }

        initialize() {
			super.initialize();
			
			const me = this;

			const messageField = mdc.textField.MDCTextField.attachTo(document.getElementById(this.cardId + '_message_field'));
			messageField.value = this.definition['message'];

			$('#' + this.cardId + '_message_value').on("change keyup paste", function() {
				var value = $('#' + me.cardId + '_message_value').val();
				
				me.definition['message'] = value;
				
				me.sequence.markChanged(me.id);
			});

			me.sequence.initializeDestinationMenu(me.cardId, function(selected) {
				me.definition['next'] = selected;

				me.sequence.markChanged(me.id);
				me.sequence.loadNode(me.definition);
			});

			const dialog = mdc.dialog.MDCDialog.attachTo(document.getElementById(me.cardId + '-edit-dialog'));

			$('#' + this.cardId + '_next_edit').on("click", function() {
				dialog.open();
			});

			$('#' + this.cardId + '_next_goto').on("click", function() {
				var destinationNodes = me.destinationNodes(me.sequence);
				
				var found = false;
				
				for (var i = 0; i < destinationNodes.length; i++) {
					const destinationNode = destinationNodes[i];

                    if (me.definition["next"].endsWith(destinationNode["id"])) {
						$("[data-node-id='" + destinationNode["id"] + "']").css("background-color", "#ffffff");
					} else {
						$("[data-node-id='" + destinationNode["id"] + "']").css("background-color", "#e0e0e0");
					}
				}
			});
        }

        issues(sequence) {
            var issues = super.issues(sequence);
            
            if (this.definition['message'] == undefined || this.definition['message'].trim().length == 0) {
	            issues.push(['No message provided.', 'node', this.definition['id'], this.cardName()]);
            }

            if (this.definition['next'] == undefined || this.definition['next'] == null || this.definition['next'].trim().length == 0) {
	            issues.push(['No next destination node selected.', 'node', this.definition['id'], this.cardName()]);
            }
            
            return issues;
        }

        destinationNodes(sequence) {
            var nodes = super.destinationNodes(sequence);

			var id = this.definition['next'];

            for (var i = 0; i < this.sequence.definition['items'].length; i++) {
                var item = this.sequence.definition['items'][i];
                                
				if (item['id'] == id || (this.sequence['definition']['id'] + "#" + item['id']) == id) {
                    nodes.push(Node.createCard(item, sequence));
                }
            }
           
           	if (nodes.length == 0) {
				var node = this.sequence.resolveNode(id);
				
				if (node != null) {
					nodes.push(node);
				} else {
					delete this.definition['next'];
				}
           	} 

            return nodes;
        }

		updateReferences(oldId, newId) {
			if (this.definition['next'] == oldId) {
				this.definition['next'] = newId;

				if (newId == null) {
					delete this.definition['next'];
				}
			}
		}

		cardType() {
			return 'Send Message';
		}
		
		static cardName() {
			return 'Send Message';
		}

		static createCard(cardName) {
			var card = {
				"name": cardName, 
				"context": "(Context goes here...)", 
				"message": "(Message goes here...)", 
				"type": "send-message", 
				"id": Node.uuidv4(),
				"next": null
			}; 
			
			return card;
		}
    }

    Node.registerCard('send-message', SendMessageNode);
    
    return SendMessageNode;
});
