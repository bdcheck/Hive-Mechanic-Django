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
        
        cardIcon() {
            return '<i class="fas fa-question" style="margin-right: 16px; font-size: 20px; "></i>';
        }

        editHtml() {
            var htmlString  = '<div class="mdc-card" id="' + this.cardId + '" style="' + this.style() + '" data-node-id="' + this.id + '">';
                htmlString += '  <div class="mdc-layout-grid" style="margin: 0; padding-left: 16px; padding-right: 16px; padding-bottom: 16px;">';
                htmlString += '    <div class="mdc-layout-grid__inner">';
                htmlString += '      <div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12">';
                htmlString += '        <div class="mdc-typography--headline6" style="margin-bottom: 16px;">';
                htmlString += '          ' + this.cardIcon() + this.cardType();
                htmlString += '          <span class="mdc-menu-surface--anchor" style="float: right;">';
                htmlString += '            <i class="material-icons mdc-icon-button__icon" aria-hidden="true" id="' + this.cardId + '_menu_open">more_vert</i>';
                htmlString += '            <div class="mdc-menu mdc-menu-surface" id="' + this.cardId + '_menu">';
                htmlString += '              <ul class="mdc-list" role="menu" aria-hidden="true" aria-orientation="vertical" tabindex="-1">';
                htmlString += '                <li class="mdc-list-item" role="menuitem">';
                htmlString += '                  <span class="mdc-list-item__text">Advanced Settings&#8230;</span>';
                htmlString += '                </li>';
                htmlString += '              </ul>';
                htmlString += '            </div>';
                htmlString += '          </span>';
                htmlString += '        </div>';
                htmlString += '      </div>';
                htmlString += '      <div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12">';
                htmlString += '        <div class="mdc-text-field mdc-text-field--outlined" id="' + this.cardId + '_name" style="width: 100%">';
                htmlString += '          <input class="mdc-text-field__input" type="text" id="' + this.cardId + '_name_value">';
                htmlString += '          <div class="mdc-notched-outline">';
                htmlString += '            <div class="mdc-notched-outline__leading"></div>';
                htmlString += '            <div class="mdc-notched-outline__notch">';
                htmlString += '              <label for="' + this.cardId + '_name_value" class="mdc-floating-label">Card Name</label>';
                htmlString += '            </div>';
                htmlString += '            <div class="mdc-notched-outline__trailing"></div>';
                htmlString += '          </div>';
                htmlString += '        </div>';
                htmlString += '      </div>';
                htmlString += this.editBody();
                htmlString += '      <div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12 mdc-typography--caption" id="' + this.cardId + '_comment" ></div>';
                htmlString += '    </div>';
                htmlString += '  </div>';
                htmlString += '</div>';
                htmlString += '<div class="mdc-dialog" id="' + this.cardId + '-advanced-dialog">';
                htmlString += '  <div class="mdc-dialog__container">';
                htmlString += '    <div class="mdc-dialog__surface" role="alertdialog" aria-modal="true" aria-labelledby="' + this.cardId + '-advanced-dialog-title" aria-describedby="' + this.cardId + '-advanced-dialog-content" style="min-width: 480px; max-width: 720px;">';
                htmlString += '      <h2 class="mdc-dialog__title" id="' + this.cardId + '-advanced-dialog-title">' + this.cardName() + '</h2>';
                htmlString += '      <div class="mdc-dialog__content" id="' + this.cardId + '-advanced-dialog-content" style="padding-top: 8px;">';
                htmlString += this.advancedEditBody();
                htmlString += '      </div>';
                htmlString += '      <footer class="mdc-dialog__actions">';
                htmlString += '        <button type="button" class="mdc-button mdc-dialog__button" data-mdc-dialog-action="delete" style="margin-right: auto;">';
                htmlString += '          <span class="mdc-button__label">Remove Card</span>';
                htmlString += '        </button>';
                htmlString += '        <button type="button" class="mdc-button mdc-dialog__button" data-mdc-dialog-action="close">';
                htmlString += '          <span class="mdc-button__label">Close</span>';
                htmlString += '        </button>';
                htmlString += '      </footer>';
                htmlString += '    </div>';
                htmlString += '  </div>';
                htmlString += '  <div class="mdc-dialog__scrim"></div>';
                htmlString += '</div>';

            return htmlString;
        }
        
        /* Error / validity checking */
        issues(sequence) {
            var issues = [];
            
            if (this.definition['name'] == undefined || this.definition['name'].trim().length == 0) {
	            issues.push(['Please provide a node name.', 'node', this.definition['id'], this.cardName()]);
            }

            if (this.definition['id'] == undefined || this.definition['id'].trim().length == 0) {
	            issues.push(['Please provide a node ID.', 'node', this.definition['id']], this.cardName());
            }
            
            var destinations = this.destinationNodes(sequence);
            
            for (var i = 0; i < destinations.length; i++) {
            	var destination = destinations[i];
            	
            	if (destination == null || destination == undefined) {
		            issues.push(['Empty destination node.', 'node', this.definition['id'], this.cardName()]);
            	} else if (this.id == destination.id) {
		            issues.push(['Node references self in destination.', 'node', this.definition['id'], this.cardName()]);
            	}
            }
            
            return issues;
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

            const idField = mdc.textField.MDCTextField.attachTo(document.getElementById(this.cardId + '_advanced_identifier'));
            idField.value = this.id;

            $('#' + this.cardId + '_advanced_identifier_value').on("change paste", function() {
                var value = $('#' + me.cardId + '_advanced_identifier_value').val();

                var oldId = me.definition['id'];
                var newId = value;

                const sources = me.sourceNodes(me.sequence);

                for (var i = 0; i < sources.length; i++) {
                    sources[i].updateReferences(oldId, newId);
                }

                me.definition['id'] = value;

                me.sequence.markChanged(me.id);
            });

            const commentField = mdc.textField.MDCTextField.attachTo(document.getElementById(this.cardId + '_advanced_comment_field'));
            
            if (this.definition['comment'] != undefined) {
                commentField.value = this.definition['comment'];
                
                this.updateCommentDisplay(this.definition['comment']);
            } else {
                this.updateCommentDisplay("");
            }           

            $('#' + this.cardId + '_advanced_comment_value').on("change keyup paste", function() {
                var value = $('#' + me.cardId + '_advanced_comment_value').val();
                
                me.definition['comment'] = value;

                me.updateCommentDisplay(me.definition['comment']);
                
                me.sequence.markChanged(me.id);
            });

            const advancedDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById(this.cardId + '-advanced-dialog'));

            advancedDialog.listen("MDCDialog:closed", function (event) {
                if (event.detail['action'] == 'delete') {
                    me.sequence.removeCard(me.id);
                }
            });

            const menu = mdc.menu.MDCMenu.attachTo(document.getElementById(this.cardId + '_menu'));

            menu.listen("MDCMenu:selected", function (event) {
                advancedDialog.open();
            });
            
            $("#" + this.cardId + "_menu_open").click(function(eventObj) {
                eventObj.preventDefault();
                
                menu.open = (menu.open == false);
            });
        }
        
        updateCommentDisplay(comment) {
            if (comment == null || comment == "") {
                $('#' + this.cardId + '_comment').hide();
            } else {
                $('#' + this.cardId + '_comment').show();
                $('#' + this.cardId + '_comment').text(comment);
            }
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

        advancedEditBody() {
            var htmlString  = '<div class="mdc-layout-grid" style="margin: 0; padding: 0;">';
                htmlString += '  <div class="mdc-layout-grid__inner">';
            
                htmlString += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12">';
                htmlString += '  <div class="mdc-text-field mdc-text-field--outlined" id="' + this.cardId + '_advanced_identifier" style="width: 100%">';
                htmlString += '    <input class="mdc-text-field__input" type="text" id="' + this.cardId + '_advanced_identifier_value">';
                htmlString += '    <div class="mdc-notched-outline">';
                htmlString += '      <div class="mdc-notched-outline__leading"></div>';
                htmlString += '      <div class="mdc-notched-outline__notch">';
                htmlString += '        <label for="' + this.cardId + '_advanced_identifier_value" class="mdc-floating-label">Card Identifier</label>';
                htmlString += '      </div>';
                htmlString += '      <div class="mdc-notched-outline__trailing"></div>';
                htmlString += '    </div>';
                htmlString += '  </div>';
                htmlString += '</div>';
                htmlString += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12">';
                htmlString += '  <div class="mdc-text-field mdc-text-field--textarea" id="' + this.cardId + '_advanced_comment_field" style="width: 100%">';
                htmlString += '    <textarea class="mdc-text-field__input" rows="4" style="width: 100%" id="' + this.cardId + '_advanced_comment_value"></textarea>';
                htmlString += '    <div class="mdc-notched-outline">';
                htmlString += '      <div class="mdc-notched-outline__leading"></div>';
                htmlString += '      <div class="mdc-notched-outline__notch">';
                htmlString += '        <label for="' + this.cardId + '_advanced_comment_value" class="mdc-floating-label">Comment</label>';
                htmlString += '      </div>';
                htmlString += '      <div class="mdc-notched-outline__trailing"></div>';
                htmlString += '    </div>';
                htmlString += '  </div>';
                htmlString += '</div>';

                htmlString += '  </div>';
                htmlString += '</div>';

            return htmlString
        }

        viewHtml() {
            var htmlString  = '<div class="mdc-card" id="' + this.cardId + '" style="' + this.style() + '"  data-node-id="' + this.id + '">';
                htmlString += '  <h6 class="mdc-typography--headline6" style="margin: 16px; margin-bottom: 0;">' + this.cardIcon() + this.cardName() + '</h6>';
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
            var includedIds = [];

            for (var i = 0; i < window.dialogBuilder.definition.sequences.length; i++) {
                var sequenceDef = window.dialogBuilder.definition.sequences[i];
                
                for (var j = 0; j < sequenceDef["items"].length; j++) {
                    var item = sequenceDef["items"][j];

                    var node = this.sequence.resolveNode(sequenceDef["id"] + "#" + item["id"]);
                    
                    if (node != null) {
                        var destinations = node.destinationNodes(sequence);

                        var isSource = false;

                        for (var k = 0; k < destinations.length && isSource == false; k++) {
                            var destination = destinations[k];

                            if (this.id == destination.id) {
                                isSource = true;
                            }
                        }

                        if (isSource && includedIds.indexOf(node.id) == -1) {
                            sources.push(node);
                            includedIds.push(node.id);
                        }
                    }
                }
            }

            return sources;
        }

        onClick(callback) {
            $('#' + this.cardId).click(function(eventObj) {
                callback();
            });
        }
        
        lookupCardName(cardId) {
            if (cardId != "") {
                var node = this.sequence.resolveNode(cardId);
                
                if (node != null) {
                    cardId = node.cardName();
                }
            }
            
            return cardId;
        }
        
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