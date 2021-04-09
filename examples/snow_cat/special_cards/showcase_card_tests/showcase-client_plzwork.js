var modules = ["material", 'cards/node', 'jquery'];

define(modules, function (mdc, Node) {
    class ShowcaseNode extends Node {
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
			
			var me = this;

            var destinationNodes = me.destinationNodes(me.sequence);

            body += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12" style="padding-top: 8px;">';
            body += '  <div class="mdc-typography--subtitle2">Patterns</div>';
            body += '</div>';
            
            for (var i = 0; i < this.definition['patterns'].length; i++) {
                var patternDef = this.definition['patterns'][i];

                var found = false;
                var foundNode = undefined;

				var id = patternDef["action"];
                
                for (var j = 0; j < destinationNodes.length; j++) {
                    const destinationNode = destinationNodes[j];

				
					if (destinationNode["id"] == id || (this.sequence['definition']['id'] + "#" + destinationNode["id"]) == id) {
                        found = true;
                        foundNode = destinationNode;
                    }
                }

                if (found == false) {
                	var node = me.sequence.resolveNode(id);
                	
                	if (node != null) {
                        found = true;
                        foundNode = node;
                	}
                }
				body += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-8">';
                body += '  <div class="mdc-select mdc-select--outlined" id="' + this.cardId + '_pattern_operation_' + i + '">';
                body += '    <div class="mdc-select__anchor" style="width: 100%">';
                body += '      <i class="mdc-select__dropdown-icon"></i>';
                body += '      <div class="mdc-select__selected-text" aria-labelledby="outlined-select-label"></div>';
                body += '      <div class="mdc-notched-outline">';
                body += '        <div class="mdc-notched-outline__leading"></div>';
                body += '        <div class="mdc-notched-outline__notch">';
                body += '          <label id="outlined-select-label" class="mdc-floating-label">Variable&#8230;</label>';
                body += '        </div>';
                body += '        <div class="mdc-notched-outline__trailing"></div>';
                body += '      </div>';
                body += '    </div>';
                body += '    <div class="mdc-select__menu mdc-menu mdc-menu-surface">';
                body += '      <ul class="mdc-list">';
                body += '        <li class="mdc-list-item mdc-list-item--selected" data-value="" aria-selected="true"></li>';
                body += '        <li class="mdc-list-item" data-value="begins_with">Begins with&#8230;</li>';
                body += '        <li class="mdc-list-item" data-value="ends_with">Ends with&#8230;</li>';
                body += '        <li class="mdc-list-item" data-value="equals">Equals&#8230;</li>';
                body += '        <li class="mdc-list-item" data-value="not_equals">Does not equal&#8230;</li>';
                body += '        <li class="mdc-list-item" data-value="contains">Contains&#8230;</li>';
                body += '        <li class="mdc-list-item" data-value="not_contains">Does not contain&#8230;</li>';
                body += '      </ul>';
                body += '    </div>';
                body += '  </div>';
                body += '</div>';

                body += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-8">';
                body += '  <div class="mdc-text-field mdc-text-field--outlined" id="' + this.cardId + '_pattern_value_' + i + '"  style="width: 100%">';
                body += '    <input type="text" class="mdc-text-field__input" id="' + this.cardId + '_pattern_value_' + i + '_value">';
                body += '    <div class="mdc-notched-outline">';
                body += '      <div class="mdc-notched-outline__leading"></div>';
                body += '      <div class="mdc-notched-outline__notch">';
                body += '        <label for="' + this.cardId + '_pattern_value_' + i + '_value" class="mdc-floating-label">Value</label>';
                body += '      </div>';
                body += '      <div class="mdc-notched-outline__trailing"></div>';
                body += '    </div>';
                body += '  </div>';
                body += '</div>';

                body += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-4" style="text-align: right;">';
                body += '  <button class="mdc-icon-button" id="' + this.cardId + '_pattern_edit_' + i + '">';
                body += '    <i class="material-icons mdc-icon-button__icon" aria-hidden="true">link</i>'; 
                body += '  </button>';
                
                if (found) {
                    body += '  <button class="mdc-icon-button" id="' + this.cardId + '_pattern_click_' + i + '">';
                    body += '    <i class="material-icons mdc-icon-button__icon" aria-hidden="true">search</i>';
                    body += '  </button>';
                }

                body += '</div>';

                body += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12">';
                body += '  <hr>';
                body += '</div>';
            }

            body += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-7">';
            body += '  <p class="mdc-typography--body1">Pattern Not Found: </p>';
            body += '</div>';
			body += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-5" style="text-align: right;">';

			body += '  <button class="mdc-icon-button" id="' + this.cardId + '_pattern_edit_not_found">';
			body += '    <i class="material-icons mdc-icon-button__icon" aria-hidden="true">link</i>';
			body += '  </button>';
			
			if (this.definition["not_found_action"] != undefined) {
				body += '  <button class="mdc-icon-button" id="' + this.cardId + '_pattern_click_not_found">';
				body += '    <i class="material-icons mdc-icon-button__icon" aria-hidden="true">search</i>';
				body += '  </button>';
			}

			body += '</div>';

            body += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12" style="text-align: right;">';
            body += '<button class="mdc-button mdc-button--raised" id="' + this.cardId + '_add_pattern">';
            body += '  <span class="mdc-button__label">Add Pattern</span>';
            body += '</button>';
            body += '</div>';

            body += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12" style="padding-top: 8px;">';
            body += '  <div class="mdc-typography--subtitle2">Timeout Parameters</div>';
            body += '</div>';
            body += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-7">';
            body += '  <div class="mdc-text-field mdc-text-field--outlined" id="' + this.cardId + '_timeout_count"  style="width: 30%">';
            body += '    <input type="text" class="mdc-text-field__input" id="' + this.cardId + '_timeout_count_value">';
            body += '    <div class="mdc-notched-outline">';
            body += '      <div class="mdc-notched-outline__leading"></div>';
            body += '      <div class="mdc-notched-outline__notch">';
            body += '        <label for="' + this.cardId + '_timeout_count_value" class="mdc-floating-label">Qty.</label>';
            body += '      </div>';
            body += '      <div class="mdc-notched-outline__trailing"></div>';
            body += '    </div>';
            body += '  </div>';
            body += '  <div class="mdc-select mdc-select--outlined" id="' + this.cardId + '_timeout_unit" style="width: 60%; float: right;">';
            body += '    <div class="mdc-select__anchor" style="width: 100%">';
            body += '      <i class="mdc-select__dropdown-icon"></i>';
            body += '      <div class="mdc-select__selected-text" aria-labelledby="outlined-select-label"></div>';
            body += '      <div class="mdc-notched-outline">';
            body += '        <div class="mdc-notched-outline__leading"></div>';
            body += '        <div class="mdc-notched-outline__notch">';
            body += '          <label id="outlined-select-label" class="mdc-floating-label">Unit</label>';
            body += '        </div>';
            body += '        <div class="mdc-notched-outline__trailing"></div>';
            body += '      </div>';
            body += '    </div>';
            body += '    <div class="mdc-select__menu mdc-menu mdc-menu-surface">';
            body += '      <ul class="mdc-list">';
            body += '        <li class="mdc-list-item" data-value="second" aria-selected="true">Seconds</li>';
            body += '        <li class="mdc-list-item" data-value="minute" aria-selected="true">Minutes</li>';
            body += '        <li class="mdc-list-item" data-value="hour" aria-selected="true">Hours</li>';
            body += '        <li class="mdc-list-item" data-value="day" aria-selected="true">Days</li>';
            body += '      </ul>';
            body += '    </div>';
            body += '  </div>';
            body += '</div>';

            body += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-5" style="text-align: right;">';

			body += '  <button class="mdc-icon-button" id="' + this.cardId + '_timeout_edit">';
			body += '    <i class="material-icons mdc-icon-button__icon" aria-hidden="true">link</i>';
			body += '  </button>';

            var found = false;
            var foundNode = undefined;
            
            for (var j = 0; j < destinationNodes.length; j++) {
                const destinationNode = destinationNodes[j];
                
                if (this.definition["timeout"] != undefined) {
					if (destinationNode["id"] == this.definition["timeout"]["action"]) {
						found = true;
						foundNode = destinationNode;
					}
                }
            }

			if (found == false && this.definition["timeout"] != undefined) {
				var node = me.sequence.resolveNode(this.definition["timeout"]["action"]);
				
				if (node != null) {
					found = true;
					foundNode = node;
				}
			}
            
            if (found) {
                body += '  <button class="mdc-icon-button" id="' + this.cardId + '_timeout_click">';
                body += '    <i class="material-icons mdc-icon-button__icon" aria-hidden="true">search</i>';
                body += '  </button>';
            }

            body += '</div>';

            body += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12 mdc-typography--caption">';

            if (found) {
            	if (foundNode["definition"]["name"] != undefined) {
	                body += 'Action: ' + foundNode["definition"]["name"];
            	} else {
	                body += 'Action: ' + foundNode["definition"]["id"];
            	}
            } else {
                body += 'Click + to add an action.';
            }

            body += '</div>';

            body += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12 mdc-typography--caption" style="padding-top: 8px;">';
            body += '  Processes response to prior message and proceeds to the first action to match response.';
            body += '</div>';

            body += '<div class="mdc-dialog" role="alertdialog" aria-modal="true" id="' + this.cardId + '-edit-dialog"  aria-labelledby="' + this.cardId + '-dialog-title" aria-describedby="' + this.cardId + '-dialog-content">';
            body += '  <div class="mdc-dialog__container">';
            body += '    <div class="mdc-dialog__surface">';
            body += '      <h2 class="mdc-dialog__title" id="' + this.cardId + '-dialog-title">Choose Destination</h2>';
            body += '      <div class="mdc-dialog__content" id="' + this.cardId + '-dialog-content">';
            body += me.sequence.chooseDestinationMenu(this.cardId);
            body += '      </div>';
            body += '      <footer class="mdc-dialog__actions">';
            body += '        <button type="button" class="mdc-button mdc-dialog__button" data-mdc-dialog-action="remove">';
            body += '          <span class="mdc-button__label">Remove Pattern</span>';
            body += '        </button>';
            body += '        <button type="button" class="mdc-button mdc-dialog__button" data-mdc-dialog-action="close">';
            body += '          <span class="mdc-button__label">Continue</span>';
            body += '        </button>';
            body += '      </footer>';
            body += '    </div>';
            body += '  </div>';
            body += '  <div class="mdc-dialog__scrim"></div>';
            body += '</div>';
            
			return body;
        }

		humanizePattern(pattern, action) {
			if (action == undefined || action == "?" || action == null || action == "") {
				action = "?";
			}
			
			action = this.lookupCardName(action);
	
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
				
				return "If response starts with " + humanized + ", go to <em>" + action + '</em>.';
			} else if (pattern== ".*") {
				return "If response is anything, go to <em>" + action + '</em>.';
			} else {
				return "If response is \"" + pattern + "\", go to <em>" + action + '</em>.';
			}
			
			return "If responses matches \"" + pattern + "\", go to <em>" + action + '</em>.';
		}
		
		viewBody() {
			var summary = ""; 
        	
			summary += '<div class="mdc-typography--body1" style="margin: 16px;">' + this.definition['message'] + '</div>'; 
			
			for (var i = 0; i < this.definition['patterns'].length; i++) {
                var patternDef = this.definition['patterns'][i];
                
                var humanized = this.humanizePattern(patternDef["pattern"], patternDef["action"]);
                
                summary += '<div class="mdc-typography--body1" style="margin: 16px;">' + humanized + '</div>';
            }
            
            if (this.definition['not_found_action'] != undefined && this.definition['not_found_action'] != '') {
	        	var action = this.lookupCardName(this.definition['not_found_action']);

                summary += '<div class="mdc-typography--body1" style="margin: 16px;">';
		    	summary += "If responses doesn't match a prior pattern, go to <em>" + action + '</em>.';
		    	summary += '</div>';
            }
            
            if (this.definition['timeout'] != undefined) {
				if (this.definition['timeout']['action'] != undefined && this.definition['timeout']['action'] != '') {
		        	var action = this.lookupCardName(this.definition['timeout']['action']);

					summary += '<div class="mdc-typography--body1" style="margin: 16px;">';
					summary += "If no responses is received within " + this.definition['timeout']["duration"] + " " + this.definition['timeout']["units"] + "(s), go to <em>" + action + "</em>.";
					summary += '</div>';
				}
            }
			return summary;
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
			
			me.sequence.initializeDestinationMenu(me.cardId, function(selected) {
				if (me.selectedPattern >= 0 && event.detail.action == "remove") {
					me.definition['patterns'].splice(me.selectedPattern, 1);
					
					me.sequence.markChanged(me.id);

					me.sequence.loadNode(me.definition);
				} else {
					if (me.selectedPattern >= 0) {
						me.definition['patterns'][me.selectedPattern]["action"] = selected;

						me.sequence.markChanged(me.id);
						me.sequence.loadNode(me.definition);
					} else if (me.selectedPattern == -1) { // Not found
						me.definition["not_found_action"] = selected;
					
						me.sequence.markChanged(me.id);
						me.sequence.loadNode(me.definition);
					} else if (me.selectedPattern == -2) { // Not found
						if (me.definition["timeout"] == undefined) {
							me.definition["timeout"] = {};
						}

						me.definition["timeout"]["action"] = selected;
					
						me.sequence.markChanged(me.id);
						me.sequence.loadNode(me.definition);
					}
				}
			});
			
			const dialog = mdc.dialog.MDCDialog.attachTo(document.getElementById(me.cardId + '-edit-dialog'));

			dialog.listen('MDCDialog:closed', (event) => {
				if (me.selectedPattern >= 0 && event.detail.action == "remove") {
					me.definition['patterns'].splice(me.selectedPattern, 1);
					
					me.sequence.markChanged(me.id);

					me.sequence.loadNode(me.definition);
				}
			});

			var updatePattern = function(action, operation, pattern) {
                me.dialog.markChanged(me.id);
                
                if (pattern.value == "") {
                    action["pattern"] = "";
                } else if (operation == "begins_with") {
                    action["pattern"] = "^" + pattern;
                } else if (operation == "ends_with") {
                    action["pattern"] = pattern + "$";
                } else if (operation == "equals") {
                    action["pattern"] = "^" + pattern + "$";
                } else if (operation == "not_contains") {
                    action["pattern"] = "(?!" + pattern + ")";
                } else if (operation == "not_equals") {
                    action["pattern"] = "^(?!" + pattern + ")$";
                } else {
                    action["pattern"] = pattern;
                }
            };

			var updateViews = function(pattern, operationField, patternField) {
            	var patternValue = "";
            	var operationValue = "";
            	
            	if (pattern == "") {
            		operationField.value = "contains";
            		patternField.value = "";
            	} else if (pattern.startsWith("^(?!") && pattern.endsWith(")$")) {
            		operationField.value = "not_equals";
            		patternField.value = pattern.replace("^(?!", "").replace(")$", "");
            	} else if (pattern.startsWith("(?!") && pattern.endsWith(")")) {
            		operationField.value = "not_contains";
            		patternField.value = pattern.replace("(?!", "").replace(")", "");
            	} else if (pattern.startsWith("(?!") && pattern.endsWith(")")) {
            		operationField.value = "not_contains";
            		patternField.value = pattern.replace("(?!", "").replace(")", "");
            	} else if (pattern.startsWith("^") && pattern.endsWith("$")) {
            		operationField.value = "equals";
            		patternField.value = pattern.replace("^", "").replace("$", "");
            	} else if (pattern.startsWith("^")) {
            		operationField.value = "begins_with";
            		patternField.value = pattern.replace("^", "");
            	} else if (pattern.endsWith("$")) {
            		operationField.value = "ends_with";
            		patternField.value = pattern.replace("$", "");
            	} else {
            		operationField.value = "contains";
            		patternField.value = pattern;
            	}
            };
			
            for (var i = 0; i < this.definition['patterns'].length; i++) {
                const patternDef = this.definition['patterns'][i];
                
                const identifier = this.cardId + '_pattern_value_' + i;

                const patternField = mdc.textField.MDCTextField.attachTo(document.getElementById(identifier));

                const operationId = this.cardId + '_pattern_operation_' + i;
                const operationSelect = mdc.select.MDCSelect.attachTo(document.getElementById(operationId));

                updateViews(patternDef['pattern'], operationSelect, patternField);

                const patternIndex = i;
                
                $("#" + identifier).on("change keyup paste", function() {
                    var value = $('#' + identifier + '_value').val();
                
                    patternDef["pattern"] = value;
                
                    me.sequence.markChanged(me.id);

					window.setTimeout(function() {
						updatePattern(me.definition['patterns'][patternIndex], operationSelect.value, patternField.value);
					}, 250);

                });

                operationSelect.listen('MDCSelect:change', () => {
					window.setTimeout(function() {
						updatePattern(me.definition['patterns'][patternIndex], operationSelect.value, patternField.value);
					}, 250);
                });
                
                const currentIndex = i;

                $('#' + this.cardId + '_pattern_click_' + i).on("click", function() {
                    var destinationNodes = me.destinationNodes(me.sequence);
                    
                    for (var i = 0; i < destinationNodes.length; i++) {
						const destinationNode = destinationNodes[i];

						if (patternDef["action"].endsWith(destinationNode["id"])) {
							$("[data-node-id='" + destinationNode["id"] + "']").css("background-color", "#ffffff");
						} else {
							$("[data-node-id='" + destinationNode["id"] + "']").css("background-color", "#e0e0e0");
						}
                    }
                });

                $('#' + this.cardId + '_pattern_edit_' + i).on("click", function() {
                	me.selectedPattern = currentIndex;
                	
//                	var pattern = me.definition["patterns"][currentIndex];
//                	
//                	if (pattern["action"] != undefined) {
//	                	destination.value = pattern["action"];
//	                }
	                
	                $('#' + me.cardId + '-edit-dialog [data-mdc-dialog-action="remove"]').show();
					
					dialog.open();
                });
            }	

			$('#' + this.cardId + '_pattern_click_not_found').on("click", function() {
				var destinationNodes = me.destinationNodes(me.sequence);
				
				for (var i = 0; i < destinationNodes.length; i++) {
					const destinationNode = destinationNodes[i];
					
					if (me.definition["not_found_action"].endsWith(destinationNode["id"])) {
						$("[data-node-id='" + destinationNode["id"] + "']").css("background-color", "#ffffff");
					} else {
						$("[data-node-id='" + destinationNode["id"] + "']").css("background-color", "#e0e0e0");
					}
				}
			});

			$('#' + this.cardId + '_timeout_click').on("click", function() {
				var destinationNodes = me.destinationNodes(me.sequence);
				
				var found = false;
		
				for (var i = 0; i < destinationNodes.length; i++) {
					const destinationNode = destinationNodes[i];
					
					if (me.definition["timeout"]["action"].endsWith(destinationNode["id"])) {
						$("[data-node-id='" + destinationNode["id"] + "']").css("background-color", "#ffffff");
					} else {
						$("[data-node-id='" + destinationNode["id"] + "']").css("background-color", "#e0e0e0");
					}
				}
				
				if (found == false) {
					console.log("ADD NODE (TIMEOUT)");
					console.log(me.definition["timeout"]);
				}
			});

            const timeoutCountField = mdc.textField.MDCTextField.attachTo(document.getElementById(this.cardId + '_timeout_count'));
            const timeoutUnitField = mdc.select.MDCSelect.attachTo(document.getElementById(this.cardId + '_timeout_unit'));
            
            if (this.definition["timeout"] != undefined) {
                if (this.definition["timeout"]["duration"] != undefined) {
		            timeoutCountField.value = this.definition["timeout"]["duration"];
	            }

                if (this.definition["timeout"]["units"] != undefined) {
		            timeoutUnitField.value = this.definition["timeout"]["units"];
				}
            }
            
			$('#' + this.cardId + '_timeout_count_value').change(function(eventObj) {
				var value = $('#' + me.cardId + '_timeout_count_value').val();
				
				if (me.definition["timeout"] == undefined) {
					me.definition["timeout"] = {};
				}
		
				me.definition["timeout"]["duration"] = value;

				me.sequence.markChanged(me.id);
			});

			timeoutUnitField.listen('MDCSelect:change', () => {
				console.log('Selected option at index ' + timeoutUnitField.selectedIndex + ' with value "' + timeoutUnitField.value + '"');

				timeoutUnitField.value;
				
				if (me.definition["timeout"] == undefined) {
					me.definition["timeout"] = {};
				}
		
				me.definition["timeout"]["units"] = timeoutUnitField.value;

				me.sequence.markChanged(me.id);
			});
           
            $('#' + this.cardId + '_add_pattern').on("click", function() {
                me["definition"]["patterns"].push({
                    "action": "",
                    "pattern": "?"
                });

                me.sequence.loadNode(me.definition);    
                me.sequence.markChanged(me.id);
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

			if (this.definition['not_found_action'] == undefined || this.definition['not_found_action'].trim().length == 0) {
	            issues.push(['No "not found" action provided.', 'node', this.definition['id'], this.cardName()]);
            }

//            if (this.definition['timeout'] == undefined || this.definition['timeout']['action'] == undefined || this.definition['timeout']['action'].trim().length == 0) {
//	            issues.push(['No "timeout" action provided.', 'node', this.definition['id'], this.cardName()]);
//            }

            for (var i = 0; i < this.definition['patterns'].length; i++) {
                var pattern = this.definition['patterns'][i];
                
				if (pattern['action'] == undefined || pattern['action'].trim().length == 0) {
					issues.push(['No action provided for pattern "' + pattern['pattern'] + '".', 'node', this.definition['id'], this.cardName()]);
				}
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
			   
			   if (this.definition['timeout'] != undefined) {
				   if (this.definition['timeout']['action'] != undefined) {
					   if (nextIds.indexOf(this.definition['timeout']['action']) == -1) {
						   nextIds.push(this.definition['timeout']['action']);
					   }
				   }
			   }
   
			   for (var i = 0; i < nextIds.length; i++) {
				   var id = nextIds[i];
				   
				   var pushed = false;
   
				   for (var j = 0; j < this.sequence.definition['items'].length; j++) {
					   var item = this.sequence.definition['items'][j];
   
					   if (item['id'] == id || (this.sequence['definition']['id'] + "#" + item['id']) == id) {
						   var node = Node.createCard(item, sequence);
   
						   nodes.push(node);
						   
						   pushed = true;
					   }
				   }
				   
				   if (pushed == false) {
					   var node = this.sequence.resolveNode(id);
				   
					   if (node != null) {
						   nodes.push(node);
					   }
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
			for (var i = 0; i < this.definition['patterns'].length; i++) {
                var pattern = this.definition['patterns'][i];
                
                if (pattern['action'] == oldId) {
	                pattern['action'] = newId;

					if (newId == null) {
						delete pattern['action'];
					}
                }
            }

            if (this.definition['not_found_action'] != undefined) {
                if (this.definition['not_found_action'] == oldId) {
	                this.definition['not_found_action'] = newId;

					if (newId == null) {
						delete this.definition['not_found_action'];
					}
                }
			}

            if (this.definition['timeout'] != undefined) {
                if (this.definition['timeout']['action'] != undefined) {
					if (this.definition['timeout']['action'] == oldId) {
						this.definition['timeout']['action'] = newId;

						if (newId == null) {
							delete this.definition['timeout']['action'];
						}
					}
                }
            }
		}

		cardType() {
			return 'Showcase Card';
		}
		
		static cardName() {
			return 'Showcase Card';
		}

		static createCard(cardName) {
			var card = {
				"name": cardName, 
				"context": "(Context goes here...)", 
				"message": "(Message goes here...)", 
				"patterns": [], 
				"timeout": {
					"duration": 15,
			        "units": "minute", 
					"action": null
				},
				"type": "showcase-card", 
				"id": Node.uuidv4(),
				"next": null
			}; 
			
			return card;
		}
    }

    Node.registerCard('showcase-card', ShowcaseNode);
    
    return ShowcaseNode;
});
