var modules = ["material", 'cards/node', 'jquery', ];

define(modules, function (mdc, Node) {
    class ProcessCookieNode extends Node {
        constructor(definition, sequence) {
            super(definition, sequence);
        }

        editBody() {
            var body = '';
            var me = this;

            var destinationNodes = me.destinationNodes(me.sequence);

            body += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12" style="padding-top: 8px;">';
            body += '  <div class="mdc-typography--subtitle2">Patterns</div>';
            body += '</div>';
            
            for (var i = 0; i < this.definition['patterns'].length; i++) {
                var patternDef = this.definition['patterns'][i];

                var found = false;
                var foundNode = undefined;
                
                for (var j = 0; j < destinationNodes.length; j++) {
                    const destinationNode = destinationNodes[j];
                    
                    if (destinationNode["id"] == patternDef["action"]) {
                        found = true;
                        foundNode = destinationNode;
                    }
                }

                body += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-7">';
                body += '  <div class="mdc-text-field mdc-text-field--outlined" id="' + this.cardId + '_pattern_value_' + i + '"  style="width: 100%">';
                body += '    <input type="text" class="mdc-text-field__input" id="' + this.cardId + '_pattern_value_' + i + '_value">';
                body += '    <div class="mdc-notched-outline">';
                body += '      <div class="mdc-notched-outline__leading"></div>';
                body += '      <div class="mdc-notched-outline__notch">';
                body += '        <label for="' + this.cardId + '_pattern_value_' + i + '_value" class="mdc-floating-label">Response Matches</label>';
                body += '      </div>';
                body += '      <div class="mdc-notched-outline__trailing"></div>';
                body += '    </div>';
                body += '  </div>';
                
                if (found) {
                	if (foundNode["definition"]["name"] != undefined) {
	                    body += '<div class="mdc-typography--caption">Action: ' + foundNode["definition"]["name"] + '</div>';                
                	} else {
	                    body += '<div class="mdc-typography--caption">Action: ' + foundNode["definition"]["id"] + '</div>';                
                	}
                } else {
                    body += '<div class="mdc-typography--caption">Click + to add an action.</div>';                
                }
                
                body += '</div>';
                body += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-5" style="text-align: right;">';

                body += '  <button class="mdc-icon-button" id="' + this.cardId + '_pattern_edit_' + i + '">';
                body += '    <i class="material-icons mdc-icon-button__icon" aria-hidden="true">create</i>';
                body += '  </button>';
                
                if (found) {
                    body += '  <button class="mdc-icon-button" id="' + this.cardId + '_pattern_click_' + i + '">';
                    body += '    <i class="material-icons mdc-icon-button__icon" aria-hidden="true">navigate_next</i>';
                    body += '  </button>';
                }

                body += '</div>';
            }

            body += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-7">';
            body += '  <p class="mdc-typography--body1">Pattern Not Found: </p>';
            body += '</div>';
			body += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-5" style="text-align: right;">';

			body += '  <button class="mdc-icon-button" id="' + this.cardId + '_pattern_edit_not_found">';
			body += '    <i class="material-icons mdc-icon-button__icon" aria-hidden="true">create</i>';
			body += '  </button>';
			
			if (this.definition["not_found_action"] != undefined) {
				body += '  <button class="mdc-icon-button" id="' + this.cardId + '_pattern_click_not_found">';
				body += '    <i class="material-icons mdc-icon-button__icon" aria-hidden="true">navigate_next</i>';
				body += '  </button>';
			}

			body += '</div>';

            body += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12" style="text-align: right;">';
            body += '<button class="mdc-button mdc-button--raised" id="' + this.cardId + '_add_pattern">';
            body += '  <span class="mdc-button__label">Add Pattern</span>';
            body += '</button>';
            body += '</div>';

            body += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12 mdc-typography--caption" style="padding-top: 8px;">';
            body += '  Processes cookie to and proceeds to the first action to matches.';
            body += '</div>';

            body += '<div class="mdc-dialog" role="alertdialog" aria-modal="true" id="' + this.cardId + '-edit-dialog"  aria-labelledby="' + this.cardId + '-dialog-title" aria-describedby="' + this.cardId + '-dialog-content">';
            body += '  <div class="mdc-dialog__container">';
            body += '    <div class="mdc-dialog__surface">';
            body += '      <h2 class="mdc-dialog__title" id="' + this.cardId + '-dialog-title">Choose Destination</h2>';
            body += '      <div class="mdc-dialog__content" id="' + this.cardId + '-dialog-content">';
            body += '        <div class="mdc-select mdc-select--outlined" id="' + this.cardId + '_destination" style="width: 100%; margin-top: 8px;">';
            body += '          <i class="mdc-select__dropdown-icon"></i>';
            body += '          <select class="mdc-select__native-control">';
            body += '            <option value="" disabled selected></option>';
            
            var actions = me.sequence.allActions();
            
            for (var i = 0; i < actions.length; i++) {
            	var action = actions[i];

	            body += '            <option value="' + action['id'] + '">' + action['name'] + '</option>';
            }

            body += '            <option value="add">Add&#8230;</option>';
            body += '          </select>';
            body += '          <div class="mdc-notched-outline">';
            body += '            <div class="mdc-notched-outline__leading"></div>';
            body += '            <div class="mdc-notched-outline__notch">';
            body += '              <label class="mdc-floating-label">Destination</label>';
            body += '            </div>';
            body += '            <div class="mdc-notched-outline__trailing"></div>';
            body += '          </div>';
            body += '        </div>';
            body += '      </div>';
            body += '      <footer class="mdc-dialog__actions">';
            body += '        <button type="button" class="mdc-button mdc-dialog__button" data-mdc-dialog-action="remove">';
            body += '          <span class="mdc-button__label">Remove</span>';
            body += '        </button>';
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
        	var summary = ""; 
        	
            for (var i = 0; i < this.definition['patterns'].length; i++) {
                var patternDef = this.definition['patterns'][i];
                
                var humanized = this.humanizePattern(patternDef["pattern"], patternDef["action"]);
                
                summary += '<div class="mdc-typography--body1" style="margin: 16px;">' + humanized + '</div>';
            }

            if (this.definition['not_found_action'] != undefined && this.definition['not_found_action'] != '') {
                summary += '<div class="mdc-typography--body1" style="margin: 16px;">';
		    	summary += "If cookie doesn't match a prior pattern, go to " + this.definition['not_found_action'] + '.';
		    	summary += '</div>';
            }
            
            return summary;
        }
        
        initialize() {
            super.initialize();
            
            var me = this;

			const destination = mdc.select.MDCSelect.attachTo(document.getElementById(me.cardId + '_destination'));

			destination.listen('MDCSelect:change', () => {
				console.log('Selected option at index ' + destination.selectedIndex + ' with value "' + destination.value + '"');
			});

			const dialog = mdc.dialog.MDCDialog.attachTo(document.getElementById(me.cardId + '-edit-dialog'));

			dialog.listen('MDCDialog:closed', (event) => {
				if (me.selectedPattern >= 0 && event.detail.action == "remove") {
					me.definition['patterns'].splice(me.selectedPattern, 1);
					
					me.sequence.markChanged(me.id);

					me.sequence.loadNode(me.definition);
				} else {
					if (me.selectedPattern >= 0) {
						me.definition['patterns'][me.selectedPattern]["action"] = destination.value;

						me.sequence.markChanged(me.id);
						me.sequence.loadNode(me.definition);
					} else if (me.selectedPattern == -1) { // Not found
						me.definition["not_found_action"] = destination.value;
					
						me.sequence.markChanged(me.id);
						me.sequence.loadNode(me.definition);
					}
				}
			});            

            for (var i = 0; i < this.definition['patterns'].length; i++) {
                const patternDef = this.definition['patterns'][i];
                
                const identifier = this.cardId + '_pattern_value_' + i;

                const patternField = mdc.textField.MDCTextField.attachTo(document.getElementById(identifier));

                patternField.value = patternDef["pattern"];
                
                $("#" + identifier).on("change keyup paste", function() {
                    var value = $('#' + identifier + '_value').val();
                
                    patternDef["pattern"] = value;
                
                    me.sequence.markChanged(me.id);
                });
                
                const currentIndex = i;

                $('#' + this.cardId + '_pattern_click_' + i).on("click", function() {
                    var destinationNodes = me.destinationNodes(me.sequence);
                    
                    for (var i = 0; i < destinationNodes.length; i++) {
						const destinationNode = destinationNodes[i];

						if (destinationNode["id"] == patternDef["action"]) {
							$("[data-node-id='" + destinationNode["id"] + "']").css("background-color", "#ffffff");
						} else {
							$("[data-node-id='" + destinationNode["id"] + "']").css("background-color", "#e0e0e0");
						}
                    }
                });

                $('#' + this.cardId + '_pattern_edit_' + i).on("click", function() {
                	me.selectedPattern = currentIndex;
                	
                	var pattern = me.definition["patterns"][currentIndex];
                	
                	if (pattern["action"] != undefined) {
	                	destination.value = pattern["action"];
	                }
	                
	                $('#' + me.cardId + '-edit-dialog [data-mdc-dialog-action="remove"]').show();
					
					dialog.open();
                });
            }

			$('#' + this.cardId + '_pattern_edit_not_found').on("click", function() {
				me.selectedPattern = -1;
				
				if (me.definition["not_found_action"] != undefined) {
					destination.value = me.definition["not_found_action"];
				}

                $('#' + me.cardId + '-edit-dialog [data-mdc-dialog-action="remove"]').hide();
				
				dialog.open();
			});
          
            $('#' + this.cardId + '_add_pattern').on("click", function() {
                me["definition"]["patterns"].push({
                    "action": "",
                    "pattern": "?"
                });

                me.sequence.loadNode(me.definition);    
                me.sequence.markChanged(me.id);
            });

			$('#' + this.cardId + '_pattern_click_not_found').on("click", function() {
				var destinationNodes = me.destinationNodes(me.sequence);
				
				for (var i = 0; i < destinationNodes.length; i++) {
					const destinationNode = destinationNodes[i];
					
					if (destinationNode["id"] == me.definition["not_found_action"]) {
						$("[data-node-id='" + destinationNode["id"] + "']").css("background-color", "#ffffff");
					} else {
						$("[data-node-id='" + destinationNode["id"] + "']").css("background-color", "#e0e0e0");
					}
				}
			});
        }

        destinationNodes(sequence) {
            var nodes = super.destinationNodes();

            var nextIds = [];

            for (var i = 0; i < this.definition['patterns'].length; i++) {
                var pattern = this.definition['patterns'][i];

                if (nextIds.indexOf(pattern['action']) == -1) {
	                nextIds.push(pattern['action']);
	            }
            }

            if (this.definition['not_found_action'] != undefined) {
                if (nextIds.indexOf(this.definition['not_found_action']) == -1) {
	                nextIds.push(this.definition['not_found_action']);
                }
			}

            for (var i = 0; i < nextIds.length; i++) {
                var id = nextIds[i];

                for (var j = 0; j < sequence.definition['items'].length; j++) {
                    var item = sequence.definition['items'][j];

                    if (item['id'] == id) {
                        // console.log(item);

                        var node = Node.createCard(item, sequence);

                        nodes.push(node);
                    }
                }
            }

            return nodes;
        }

		updateReferences(oldId, newId) {
            for (var i = 0; i < this.definition['patterns'].length; i++) {
                var pattern = this.definition['patterns'][i];
                
                if (pattern['action'] == oldId) {
	                pattern['action'] = newId;
                }
            }

            if (this.definition['not_found_action'] != undefined) {
                if (this.definition['not_found_action'] == oldId) {
	                this.definition['not_found_action'] = newId;
                }
			}
		}
        
        cardType() {
            return 'Process Cookie';
        }
        
        humanizePattern(pattern, action) {
        	if (action == undefined || action == "?" || action == null || action == "") {
        		action = "?";
        	}

        	if (pattern.startsWith("^[") && pattern.endsWith("]")) {
        		var matches = [];
        		
        		for (var i = 2; i < pattern.length - 1; i++) {
        			matches.push("" + pattern[i]);
        		}
        		
        		var humanized = "";
        		
        		for (var i = 0; i < matches.length; i++) {
        			if (humanized.length > 0) {
        				if (i < matches.length - 1) {
        					humanized += ", ";
        				} else if (matches.length > 2){
        					humanized += ", or ";
        				} else {
        					humanized += " or ";
        				}
        			}
        			
        			humanized += "\"" + matches[i] + "\"";
        		}
        		
        		return "If cookie starts with " + humanized + ", go to " + action + '.';
        	} else if (pattern== ".*") {
        		return "If cookie is anything, go to " + action + '.';
        	} else {
        		return "If cookie is \"" + pattern + "\", go to " + action + '.';
        	}
        	
            return "If cookie matches \"" + pattern + "\", go to " + action + '.';
        }

		static cardName() {
			return 'Process Cookie';
		}

		static createCard(cardName) {
			var card = {
				"name": cardName, 
				"patterns": [], 
				"type": "process-cookie", 
				"id": Node.uuidv4()
			}; 
			
			return card;
		}
    }

    Node.registerCard('process-cookie', ProcessCookieNode);
});