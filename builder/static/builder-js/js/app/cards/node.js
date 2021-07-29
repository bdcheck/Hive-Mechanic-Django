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
                htmlString += '    <div class="mdc-layout-grid__inner" style="row-gap: 8px;">';
                htmlString += '      <div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12">';
                htmlString += '        <div class="mdc-typography--headline6" style="margin-bottom: 16px;">';
                htmlString += '          <span>' + this.cardIcon() + '</span>';
                htmlString += '          <span style="vertical-align: top;">' + this.cardType() + '</span>';
                htmlString += '          <div class="mdc-menu-surface--anchor" style="float: right;">';
                htmlString += '            <i class="material-icons mdc-icon-button__icon" aria-hidden="true" id="' + this.cardId + '_menu_open">more_vert</i>';
                htmlString += '            <div class="mdc-menu mdc-menu-surface" id="' + this.cardId + '_menu">';
                htmlString += '              <ul class="mdc-list" role="menu" aria-hidden="true" aria-orientation="vertical" tabindex="-1">';
                htmlString += '                <li class="mdc-list-item mdc-list-item mdc-list-item--with-one-line" role="menuitem">';
                htmlString += '                  <span class="mdc-list-item__ripple"></span>';
                htmlString += '                  <span class="mdc-list-item__text mdc-list-item__start">Advanced Settings&#8230;</span>';
                htmlString += '                </li>';
                htmlString += '              </ul>';
                htmlString += '            </div>';
                htmlString += '          </div>';
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
                htmlString += '    <div class="mdc-dialog__surface">';
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

            const optionsMenu = mdc.menuSurface.MDCMenuSurface.attachTo(document.getElementById(this.cardId + '_menu'));

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

            var element = $('#' + this.cardId + '-advanced-dialog').detach();
            $('body').append(element);

            const advancedDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById(this.cardId + '-advanced-dialog'));

            advancedDialog.listen("MDCDialog:closed", function (event) {
                if (event.detail['action'] == 'delete') {
                    me.sequence.removeCard(me.id);
                }
            });

            const menu = mdc.menu.MDCMenu.attachTo(document.getElementById(this.cardId + '_menu'));
            menu.setFixedPosition(true);

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

        editFields() {
            return [];
        }

        fetchLocalizedValue(bundle) {
            var keys = Object.keys(bundle);

            keys.sort(function(one, two) {
                var diff = two.length - one.length;

                if (diff != 0) {
                    return diff;
                }

                if (one < two) {
                    return -1;
                } else if (one > two) {
                    return 1;
                }

                return 0;
            });

            for (var i = 0; i < navigator.language.lengths; i++) {
                var language = navigator.languages[i].toLowerCase();

                for (var j = 0; j < keys.length; j++) {
                    var key = keys[j].toLowerCase();

                    if (language.startsWith(key)) {
                        return bundle[key];
                    }
                }
            }

            return bundle[keys[0]];
        }

        fetchLocalizedConstant(term) {
            var constants = {
                'begins_with': {
                    'en': 'Begins with...'
                },
                'ends_with': {
                    'en': 'Ends with...'
                },
                'equals': {
                    'en': 'Equals/is...'
                },
                'not_equals': {
                    'en': 'Does not equal / is not...'
                },
                'contains': {
                    'en': 'Contains...'
                },
                'not_contains': {
                    'en': 'Does not contain...'
                },
                'no_action_defined': {
                    'en': 'No action defined...'
                }
            };

            this.addTerms(constants);

            var keys = Object.keys(constants[term]);

            for (var i = 0; i < navigator.languages.length; i++) {
                var language = navigator.languages[i].toLowerCase();

                for (var j = 0; j < keys.length; j++) {
                    var key = keys[j].toLowerCase();

                    if (language.startsWith(key)) {
                        return constants[term][key];
                    }
                }
            }

            return term;
        }

        addTerms(terms) {
            // Override in subclasses...
        }

        createImageUrlField(field) {
            var me = this;

            var fieldLines = [];

            fieldLines.push('<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-' + field['width'] + '">');
            fieldLines.push('  <div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12">');
            fieldLines.push('    <img src="https://via.placeholder.com/150" id="' + me.cardId + '_' + field['field'] + '_preview" style="max-width: 100%; margin-bottom: 8px;">');
            fieldLines.push('  </div>');
            fieldLines.push('  <div class="mdc-text-field mdc-text-field--outlined" id="' + me.cardId + '_' + field['field'] + '_field" style="width: 100%; margin-top: 4px;">');
            fieldLines.push('    <input class="mdc-text-field__input"style="width: 100%" id="' + me.cardId + '_' + field['field'] + '_value" />');
            fieldLines.push('    <div class="mdc-notched-outline">');
            fieldLines.push('      <div class="mdc-notched-outline__leading"></div>');
            fieldLines.push('      <div class="mdc-notched-outline__notch">');
            fieldLines.push('        <label for="' + me.cardId + '_' + field['field'] + '_value" class="mdc-floating-label">' + me.fetchLocalizedValue(field['label']) + '</label>');
            fieldLines.push('      </div>');
            fieldLines.push('      <div class="mdc-notched-outline__trailing"></div>');
            fieldLines.push('    </div>');
            fieldLines.push('  </div>');
            fieldLines.push('</div>');

            return fieldLines.join('\n');
        }

        createTextField(field) {
            var me = this;

            var fieldLines = [];

            fieldLines.push('<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-' + field['width'] + '">');
            fieldLines.push('  <div class="mdc-text-field mdc-text-field--outlined" id="' + me.cardId + '_' + field['field'] + '_field" style="width: 100%; margin-top: 4px;">');
            fieldLines.push('    <input class="mdc-text-field__input"style="width: 100%" id="' + me.cardId + '_' + field['field'] + '_value" />');
            fieldLines.push('    <div class="mdc-notched-outline">');
            fieldLines.push('      <div class="mdc-notched-outline__leading"></div>');
            fieldLines.push('      <div class="mdc-notched-outline__notch">');
            fieldLines.push('        <label for="' + me.cardId + '_' + field['field'] + '_value" class="mdc-floating-label">' + me.fetchLocalizedValue(field['label']) + '</label>');
            fieldLines.push('      </div>');
            fieldLines.push('      <div class="mdc-notched-outline__trailing"></div>');
            fieldLines.push('    </div>');
            fieldLines.push('  </div>');
            fieldLines.push('</div>');

            return fieldLines.join('\n');
        }

        createTextArea(field) {
            var me = this;

            var fieldLines = [];

            fieldLines.push('<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-' + field['width'] + '">');
            fieldLines.push('  <label class="mdc-text-field mdc-text-field--textarea mdc-text-field--outlined" id="' + me.cardId + '_' + field['field'] + '_field" style="width: 100%; margin-top: 4px;">');
            fieldLines.push('    <span class="mdc-notched-outline">');
            fieldLines.push('      <span class="mdc-notched-outline__leading"></span>');
            fieldLines.push('      <span class="mdc-notched-outline__notch">');
            fieldLines.push('        <span class="mdc-floating-label" for="' + me.cardId + '_' + field['field'] + '_value">' + me.fetchLocalizedValue(field['label']) + '</span>');
            fieldLines.push('      </span>');
            fieldLines.push('      <span class="mdc-notched-outline__trailing"></span>');
            fieldLines.push('    </span>');
            fieldLines.push('    <span class="mdc-text-field__resizer">');
            fieldLines.push('      <textarea class="mdc-text-field__input" rows="4" style="width: 100%" id="' + me.cardId + '_' + field['field'] + '_value"></textarea>');
            fieldLines.push('    </span>');
            fieldLines.push('  </label>');
            fieldLines.push('</div>');

            return fieldLines.join('\n');
        }

        createReadOnly(field) {
            var me = this;

            var fieldLines = [];

            var style = 'body1';

            if (field['style'] != undefined) {
                style = field['style'];
            }

            var helpClass = '';

            if (field['is_help']) {
                helpClass = 'hive_mechanic_help';
            }

            if (field['value'] == '----') {
                fieldLines.push('<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-' + field['width'] + ' mdc-typography--' + style + ' ' + helpClass + '">');
                fieldLines.push('  <hr style="height: 1px; border: none; color: #9D9E9D; background-color: #9D9E9D;" />');
                fieldLines.push('</div>');
            } else {
                fieldLines.push('<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-' + field['width'] + ' mdc-typography--' + style + ' ' + helpClass + '" style="display: flex; align-items: center;">');
                fieldLines.push('  <div>' + me.fetchLocalizedValue(field['value']) + '</div>');
                fieldLines.push('</div>');
            }

            if (field['width'] != 12 && helpClass != '') {
                fieldLines.push('<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-' + field['width'] + ' mdc-typography--' + style + ' hive_mechanic_help_filler">&nbsp;&nbsp;</div>');
            }

            return fieldLines.join('\n');
        }

        createSelect(field) {
            var me = this;

            var fieldLines = [];

            fieldLines.push('<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-' + field['width'] + ' mdc-typography--caption">');

            fieldLines.push('  <div class="mdc-select mdc-select--outlined" id="' + me.cardId + '_' + field['field'] + '" style="width: 100%; margin-top: 4px;">');
            fieldLines.push('    <div class="mdc-select__anchor">');
            fieldLines.push('      <span class="mdc-notched-outline">');
            fieldLines.push('        <span class="mdc-notched-outline__leading"></span>');
            fieldLines.push('        <span class="mdc-notched-outline__notch">');
            fieldLines.push('          <span class="mdc-floating-label">' + me.fetchLocalizedValue(field['label']) + '</span>');
            fieldLines.push('        </span>');
            fieldLines.push('        <span class="mdc-notched-outline__trailing"></span>');
            fieldLines.push('      </span>');
            fieldLines.push('      <span class="mdc-select__selected-text-container">');
            fieldLines.push('        <span class="mdc-select__selected-text"></span>');
            fieldLines.push('      </span>');
            fieldLines.push('      <span class="mdc-select__dropdown-icon">');
            fieldLines.push('        <svg class="mdc-select__dropdown-icon-graphic" viewBox="7 10 10 5" focusable="false">');
            fieldLines.push('          <polygon class="mdc-select__dropdown-icon-inactive" stroke="none" fill-rule="evenodd" points="7 10 12 15 17 10"></polygon>');
            fieldLines.push('          <polygon class="mdc-select__dropdown-icon-active" stroke="none" fill-rule="evenodd" points="7 15 12 10 17 15"></polygon>');
            fieldLines.push('        </svg>');
            fieldLines.push('      </span>');
            fieldLines.push('    </div>');

            fieldLines.push('    <div class="mdc-select__menu mdc-menu mdc-menu-surface" role="listbox">');
            fieldLines.push('      <ul class="mdc-list" role="listbox">');
            
            if (Array.isArray(field['options'])) { 
                $.each(field['options'], function(index, option) {
                    fieldLines.push('          <li class="mdc-list-item" data-value="' + option['value'] + '" role="option">');
                    fieldLines.push('            <span class="mdc-list-item__ripple"></span>                ');
                    fieldLines.push('            <span class="mdc-list-item__text">' + me.fetchLocalizedValue(option['label']) + '<span>');
                    fieldLines.push('          </li>');
                });
            }

            fieldLines.push('      </ul>');
            fieldLines.push('    </div>');
            fieldLines.push('  </div>');
            fieldLines.push('</div>');

            return fieldLines.join('\n');
        }

        createCardReference(field) {
            var me = this;

            var fieldLines = [];

            fieldLines.push('<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-' + field['width'] + '" style="text-align: right; display: flex; align-items: center; justify-content: right;">');
            fieldLines.push('  <button class="mdc-icon-button" id="' + me.cardId + '_' + field['field'] + '_edit">');
            fieldLines.push('    <i class="material-icons mdc-icon-button__icon" aria-hidden="true">link</i>');
            fieldLines.push('  </button>');
            fieldLines.push('  <button class="mdc-icon-button" id="' + me.cardId + '_' + field['field'] + '_goto">');
            fieldLines.push('    <i class="material-icons mdc-icon-button__icon" aria-hidden="true">keyboard_arrow_right</i>');
            fieldLines.push('  </button>');
            fieldLines.push('</div>');

            return fieldLines.join('\n');
        }

        createList(field) {
            var me = this;

            var fieldLines = [];

            var fieldName = field['field'];

            fieldLines.push('<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12">');
            fieldLines.push('  <div class="mdc-typography--subtitle2">' + me.fetchLocalizedValue(field['label']) + '</div>');
            fieldLines.push('</div>');

            fieldLines.push('<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12">');
            fieldLines.push('  <div id="' + me.cardId + '__' + fieldName + '__items"></div>');
            fieldLines.push('</div>');

            if (field['add_item_label'] != undefined) {
                fieldLines.push('<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12" style="text-align: right;">');
                fieldLines.push('  <button class="mdc-button mdc-button--raised" id="' +  me.cardId + '__' + fieldName + '__add_item">');
                fieldLines.push('    <span class="mdc-button__label">' + me.fetchLocalizedValue(field['add_item_label']) + '</span>');
                fieldLines.push('  </button>');
                fieldLines.push('</div>');
            }

            return fieldLines.join('\n');
        }

        createStructure(field) {
            var me = this;

            var fieldLines = [];

            var fieldName = field['field'];

            fieldLines.push('<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12">');
            fieldLines.push('  <div class="mdc-typography--subtitle2">' + me.fetchLocalizedValue(field['label']) + '</div>');
            fieldLines.push('</div>');

            fieldLines.push('<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12">');
            fieldLines.push('  <div id="' + me.cardId + '__' + fieldName + '" class="mdc-layout-grid__inner"></div>');
            fieldLines.push('</div>');

            return fieldLines.join('\n');
        }

        createPattern(field) {
            var me = this;

            var fieldLines = [];

            var fieldName = field['field'];

            var operations = [
                'begins_with',
                'ends_with',
                'equals',
                'not_equals',
                'contains',
                'not_contains',
            ];

            if (field['operations'] != undefined) {
                operations = field['operations'];
            }

            fieldLines.push('<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-' + field['operation_width'] + ' mdc-typography--caption" style="margin-bottom: 8px;">');
            fieldLines.push('  <div class="mdc-select mdc-select--outlined" id="' + me.cardId + '_' + field['field'] + '__operation" style="width: 100%;">');
            fieldLines.push('    <div class="mdc-select__anchor">');
            fieldLines.push('      <span class="mdc-notched-outline">');
            fieldLines.push('        <span class="mdc-notched-outline__leading"></span>');
            fieldLines.push('        <span class="mdc-notched-outline__notch">');
            fieldLines.push('          <span class="mdc-floating-label">' + me.fetchLocalizedValue(field['operation_label']) + '</span>');
            fieldLines.push('        </span>');
            fieldLines.push('        <span class="mdc-notched-outline__trailing"></span>');
            fieldLines.push('      </span>');
            fieldLines.push('      <span class="mdc-select__selected-text-container">');
            fieldLines.push('        <span class="mdc-select__selected-text"></span>');
            fieldLines.push('      </span>');
            fieldLines.push('      <span class="mdc-select__dropdown-icon">');
            fieldLines.push('        <svg class="mdc-select__dropdown-icon-graphic" viewBox="7 10 10 5" focusable="false">');
            fieldLines.push('          <polygon class="mdc-select__dropdown-icon-inactive" stroke="none" fill-rule="evenodd" points="7 10 12 15 17 10"></polygon>');
            fieldLines.push('          <polygon class="mdc-select__dropdown-icon-active" stroke="none" fill-rule="evenodd" points="7 15 12 10 17 15"></polygon>');
            fieldLines.push('        </svg>');
            fieldLines.push('      </span>');
            fieldLines.push('    </div>');

            fieldLines.push('    <div class="mdc-select__menu mdc-menu mdc-menu-surface" role="listbox">');
            fieldLines.push('      <ul class="mdc-list" role="listbox">');

            $.each(operations, function(index, operation) {
                fieldLines.push('          <li class="mdc-list-item" data-value="' + operation + '" role="option">');
                fieldLines.push('            <span class="mdc-list-item__ripple"></span>                ');
                fieldLines.push('            <span class="mdc-list-item__text">' + me.fetchLocalizedConstant(operation) + '<span>');
                fieldLines.push('          </li>');
            });

            fieldLines.push('      </ul>');
            fieldLines.push('    </div>');
            fieldLines.push('  </div>');
            fieldLines.push('</div>');


            fieldLines.push('<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-' + field['content_width'] + '">');
            fieldLines.push('  <div class="mdc-text-field mdc-text-field--outlined" id="' + me.cardId + '_' + field['field'] + '__content_field" style="width: 100%">');
            fieldLines.push('    <input class="mdc-text-field__input"style="width: 100%" id="' + me.cardId + '_' + field['field'] + '__content_value" />');
            fieldLines.push('    <div class="mdc-notched-outline">');
            fieldLines.push('      <div class="mdc-notched-outline__leading"></div>');
            fieldLines.push('      <div class="mdc-notched-outline__notch">');
            fieldLines.push('        <label for="' + me.cardId + '_' + field['field'] + '__content_value" class="mdc-floating-label">' + me.fetchLocalizedValue(field['content_label']) + '</label>');
            fieldLines.push('      </div>');
            fieldLines.push('      <div class="mdc-notched-outline__trailing"></div>');
            fieldLines.push('    </div>');
            fieldLines.push('  </div>');
            fieldLines.push('</div>');

            return fieldLines.join('\n');
        }

        addListFieldItem(field, itemDefinition) {
            var me = this;

            var fieldName = field['field'];

            var listContainerId = me.cardId + '__' + fieldName + '__items';

            var itemIndex = $('#' + listContainerId + ' .' + me.cardId + '__' + fieldName + '__item').length;

            var templateLines = [];

            templateLines.push('<div class="' + me.cardId + '__' + fieldName + '__item mdc-layout-grid__inner" style="row-gap: 8px; margin-top: 8px;">');

            $.each(field['template'], function(index, template) {
                var templateField = jQuery.extend(true, {}, template);

                templateField['original_field'] = templateField['field'];

                templateField['field'] = fieldName + '__' + templateField['field'] + '__' + itemIndex;

                templateLines.push(me.createField(templateField));
            });

            templateLines.push('</div>');

            $('#' + listContainerId).append(templateLines.join('\n'));

            $.each(field['template'], function(index, template) {
                var templateField = jQuery.extend(true, {}, template);

                templateField['original_field'] = templateField['field'];

                templateField['field'] = fieldName + '__' + templateField['field'] + '__' + itemIndex;

                itemDefinition[templateField['field']] = itemDefinition[templateField['original_field']];

                me.initializeField(templateField, itemDefinition, function(newValue) {
                    itemDefinition[templateField['original_field']] = newValue;

                    me.sequence.markChanged(me.id);
                });
            });
        }

        addStructureFieldItem(field, itemDefinition) {
            var me = this;

            var fieldName = field['field'];

            var listContainerId = me.cardId + '__' + field['parent_field'];

            var fieldHtml = me.createField(field);

            $('#' + listContainerId).append(fieldHtml);

            me.initializeField(field, itemDefinition, function(newValue) {
                itemDefinition[fieldName] = newValue;

                me.sequence.markChanged(me.id);
            });
        }

        createField(field) {
            var fieldLines = [];

            if (field['width'] == undefined) {
                field['width'] = 12;
            }

            if (field['parent_field'] != undefined) {
                field = jQuery.extend(true, {}, field);

                field['original_field'] = field['field'];
                field['field'] = field['parent_field'] + '__' + field['field'];
            }

            if (field['type'] == 'integer') {
                if (field['input'] == 'text') {
                    fieldLines.push(this.createTextField(field));
                }
            } else if (field['type'] == 'text') {
                if (field['multiline']) {
                    fieldLines.push(this.createTextArea(field));
                } else {
                    fieldLines.push(this.createTextField(field));
                }
            } else if (field['type'] == 'choice') {
                fieldLines.push(this.createSelect(field));
            } else if (field['type'] == 'readonly') {
                fieldLines.push(this.createReadOnly(field));
            } else if (field['type'] == 'card') {
                fieldLines.push(this.createCardReference(field));
            } else if (field['type'] == 'list') {
                fieldLines.push(this.createList(field));
            } else if (field['type'] == 'structure') {
                fieldLines.push(this.createStructure(field));
            } else if (field['type'] == 'pattern') {
                fieldLines.push(this.createPattern(field));
            } else if (field['type'] == 'image-url') {
                fieldLines.push(this.createImageUrlField(field));
            } else {
                // TODO: Unknown Card Type
            }

            return fieldLines.join('\n');
        }

        initializeField(field, definition, onUpdate) {
            var me = this;

            console.log("INITING...");
            console.log(field);
            console.log(definition);

            var fieldName = field['field'];

            if (field['parent_field'] != undefined) {
                fieldName = field['parent_field'] + '__' + fieldName;
            }

            if (field['type'] == 'integer') {
                const fieldWidget = mdc.textField.MDCTextField.attachTo(document.getElementById(me.cardId + '_' + fieldName + '_field'));

                if (definition[field['field']] == undefined && definition[field['default']] != undefined) {
                    definition[field['field']] = field['default'];
                }

                if (definition[field['field']] != undefined) {
                    fieldWidget.value = definition[field['field']];
                }

                $('#' + me.cardId + '_' + fieldName + '_value').on("change keyup paste", function() {
                    var value = $('#' + me.cardId + '_' + fieldName + '_value').val();

                    me.sequence.markChanged(me.id);

                    onUpdate(parseInt(value));
                });
            } else if (field['type'] == 'image-url') {
                const fieldWidget = mdc.textField.MDCTextField.attachTo(document.getElementById(me.cardId + '_' + fieldName + '_field'));

                if (definition[field['field']] == undefined && definition[field['default']] != undefined) {
                    definition[field['field']] = field['default'];
                }

                if (definition[field['field']] != undefined) {
                    fieldWidget.value = definition[field['field']];
                    
                    $('#' + me.cardId + '_' + field['field'] + '_preview').attr('src', fieldWidget.value);
                }

                $('#' + me.cardId + '_' + fieldName + '_value').on("change keyup paste", function() {
                    var value = $('#' + me.cardId + '_' + fieldName + '_value').val();

                    $('#' + me.cardId + '_' + field['field'] + '_preview').attr('src', value);

                    me.sequence.markChanged(me.id);

                    onUpdate(value);
                });
            } else if (field['type'] == 'choice') {
                if (Array.isArray(field['options'])) { 
                    const choiceField = mdc.select.MDCSelect.attachTo(document.getElementById(me.cardId + '_' + fieldName));

                    if (definition[field['field']] != undefined) {
                        choiceField.value = definition[field['field']];
                    }

                    choiceField.listen('MDCSelect:change', function() {
                        onUpdate(choiceField.value);
                    });

                    me.sequence.markChanged(me.id);
                } else {
                    // Fetch values and update structure and re-render
                    $.get(field['options'], function(data) {
                        field['options'] = data;
                        
                        var optionLines = [];

                        $.each(data, function(index, option) {
                            optionLines.push('          <li class="mdc-list-item" data-value="' + option['value'] + '" role="option">');
                            optionLines.push('            <span class="mdc-list-item__ripple"></span>                ');
                            optionLines.push('            <span class="mdc-list-item__text">' + me.fetchLocalizedValue(option['label']) + '<span>');
                            optionLines.push('          </li>');
                        });
                        
                        $('#' + me.cardId + '_' + fieldName + ' ul.mdc-list').html(optionLines.join('')); 
                        
                        me.initializeField(field, definition, onUpdate);
                    });
                }
            } else if (field['type'] == 'text') {
                const fieldWidget = mdc.textField.MDCTextField.attachTo(document.getElementById(me.cardId + '_' + fieldName + '_field'));

                if (definition[field['field']] != undefined) {
                    fieldWidget.value = definition[field['field']];
                }

                $('#' + me.cardId + '_' + fieldName + '_value').on("change keyup paste", function() {
                    var value = fieldWidget.value;

                    me.sequence.markChanged(me.id);

                    onUpdate(value);
                });
            } else if (field['type'] == 'readonly') {
                // Do nothing...
            } else if (field['type'] == 'card') {
                $('#' + me.cardId + '_' + fieldName + '_edit').on("click", function() {
                    me.sequence.refreshDestinationMenu(function(destination) {
                        window.dialogBuilder.chooseDestinationDialog.close();

                        onUpdate(destination)

                        me.sequence.markChanged(me.id);
                        me.sequence.loadNode(me.definition);
                    });

                    window.dialogBuilder.chooseDestinationDialog.open();
                });

                $('#' + me.cardId + '_' + fieldName + '_goto').on("click", function() {
                    var destinationNodes = me.destinationNodes(me.sequence);

                    for (var i = 0; i < destinationNodes.length; i++) {
                        const destinationNode = destinationNodes[i];

                        if (definition[field['field']] != undefined && definition[field['field']].endsWith(destinationNode["id"])) {
                            $("[data-node-id='" + destinationNode["id"] + "']").css("background-color", "#ffffff");
                        } else {
                            $("[data-node-id='" + destinationNode["id"] + "']").css("background-color", "#e0e0e0");
                        }
                    }
                });

                if (definition[field['field']] == null || definition[field['field']] == undefined) {
                    $('#' + me.cardId + '_' + fieldName + '_goto').hide();
                } else {
                    $('#' + me.cardId + '_' + fieldName + '_goto').show();
                }
            } else if (field['type'] == 'list') {
                $('#' + me.cardId + '__' + fieldName + '__add_item').on("click", function() {
                    definition[field['field']].push({});

                    me.sequence.loadNode(me.definition);
                    me.sequence.markChanged(me.id);
                });

                $.each(definition[field['field']], function(index, item) {
                    me.addListFieldItem(field, item);
                });
            } else if (field['type'] == 'structure') {
                $.each(field['fields'], function(index, itemField) {
                    itemField['parent_field'] = field['field'];

                    me.addStructureFieldItem(itemField, definition[field['field']]);
                });
            } else if (field['type'] == 'pattern') {
                const operationField = mdc.select.MDCSelect.attachTo(document.getElementById(me.cardId + '_' + fieldName + '__operation'));
                const contentField = mdc.textField.MDCTextField.attachTo(document.getElementById(me.cardId + '_' + fieldName + '__content_field'));

                var actualFieldName = field['field'];

                if (field['original_field'] != undefined) {
                    actualFieldName = field['original_field'];
                }

                if (definition[actualFieldName] != undefined) {
                    contentField.value = definition[actualFieldName];
                    me.updatePatternView(contentField.value, operationField, contentField);
                }

                operationField.listen('MDCSelect:change', function() {
                    me.updatePatternValue(operationField.value, contentField.value, onUpdate);

                    me.updatePatternView(definition[actualFieldName], operationField, contentField);
                });

                $('#' + me.cardId + '_' + fieldName + '__content_value').on("change keyup paste", function() {
                    me.updatePatternValue(operationField.value, $('#' + me.cardId + '_' + fieldName + '__content_value').val(), onUpdate);

                    me.updatePatternView(definition[actualFieldName], operationField, contentField);
                });
            } else {
                // TODO: Unknown Card Type
            }
        }

        updatePatternView(pattern, operationField, patternField) {
            var oldOperationValue = operationField.value;
            var newOperationValue = oldOperationValue;

            var oldPatternValue = patternField.value;
            var newPatternValue = oldPatternValue;

            if (pattern == "") {
                newOperationValue = "contains";
                newPatternValue = "";
            } else if (pattern.startsWith("^(?!") && pattern.endsWith(")$")) {
                newOperationValue = "not_equals";
                newPatternValue = pattern.replace("^(?!", "").replace(")$", "");
            } else if (pattern.startsWith("(?!") && pattern.endsWith(")")) {
                newOperationValue = "not_contains";
                newPatternValue = pattern.replace("(?!", "").replace(")", "");
            } else if (pattern.startsWith("(?!") && pattern.endsWith(")")) {
                newOperationValue = "not_contains";
                newPatternValue = pattern.replace("(?!", "").replace(")", "");
            } else if (pattern.startsWith("^") && pattern.endsWith("$")) {
                newOperationValue = "equals";
                newPatternValue = pattern.replace("^", "").replace("$", "");
            } else if (pattern.startsWith("^")) {
                newOperationValue = "begins_with";
                newPatternValue = pattern.replace("^", "");
            } else if (pattern.endsWith("$")) {
                newOperationValue = "ends_with";
                newPatternValue = pattern.replace("$", "");
            } else {
                newOperationValue = "contains";
                newPatternValue = pattern;
            }

            if (newOperationValue != oldOperationValue) {
                operationField.value = newOperationValue;
            }

            if (newPatternValue != oldPatternValue) {
                patternField.value = newPatternValue;
            }
        };

        updatePatternValue(operation, pattern, onUpdated) {
            var patternValue = "";

            if (pattern == "") {
                patternValue = "";
            } else if (operation == "begins_with") {
                patternValue = "^" + pattern;
            } else if (operation == "ends_with") {
                patternValue = pattern + "$";
            } else if (operation == "equals") {
                patternValue = "^" + pattern + "$";
            } else if (operation == "not_contains") {
                patternValue = "(?!" + pattern + ")";
            } else if (operation == "not_equals") {
                patternValue = "^(?!" + pattern + ")$";
            } else {
                patternValue = pattern;
            }

            onUpdated(patternValue);
        };

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

                return "[TRANSLATE] If response starts with " + humanized + ", go to <em>" + action + '</em>.';
            } else if (pattern== ".*") {
                return "[TRANSLATE] If response is anything, go to <em>" + action + '</em>.';
            } else {
                return "[TRANSLATE] If response is \"" + pattern + "\", go to <em>" + action + '</em>.';
            }

            return "[TRANSLATE] If responses matches \"" + pattern + "\", go to <em>" + action + '</em>.';
        }

        editFields() {
            var me = this;

            var fields = this.cardFields();

            var fieldLines = [];

            $.each(fields, function(index, field) {
                fieldLines.push(me.createField(field));
            });

            return fieldLines.join('\n');
        }

        initializeFields() {
            var fields = this.cardFields();

            var me = this;

            $.each(fields, function(index, field) {
                var onUpdate = function(newValue) {
                    me.definition[field['field']] = newValue;

                    me.sequence.markChanged(me.id);
                };

                if (field['type'] == 'integer') {
                    me.initializeField(field, me.definition, onUpdate);
                } else if (field['type'] == 'image-url') {
                    me.initializeField(field, me.definition, onUpdate);
                } else if (field['type'] == 'choice') {
                    me.initializeField(field, me.definition, onUpdate);
                } else if (field['type'] == 'text') {
                    me.initializeField(field, me.definition, onUpdate);
                } else if (field['type'] == 'readonly') {
                    // Do nothing...
                } else if (field['type'] == 'card') {
                    me.initializeField(field, me.definition, onUpdate);
                } else if (field['type'] == 'list') {
                    me.initializeField(field, me.definition, function() {});
                } else if (field['type'] == 'structure') {
                    me.initializeField(field, me.definition, function() {});
                } else if (field['type'] == 'pattern') {
                    me.initializeField(field, me.definition, onUpdate);
                } else {
                    // TODO: Unknown Card Type
                }
            });
            
            window.setTimeout(me.sequence.initializeDestinationMenu, 250);

            if (window.dialogBuilder.helpToggle.checked) {
                $(".hive_mechanic_help").show()
            } else {
                $(".hive_mechanic_help").hide()
            }
        }

        editBody() {
            return this.editFields();

            // var htmlString  = '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12">';
            //     htmlString += this.viewBody();
            //     htmlString += '</div>';
            //
            // return htmlString
        }

        advancedEditBody() {
            var htmlString  = '<div class="mdc-layout-grid" style="margin: 0; padding: 0;">';
                htmlString += '  <div class="mdc-layout-grid__inner" style="row-gap: 16px;">';
                htmlString += '    <div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12">';
                htmlString += '      <div class="mdc-text-field mdc-text-field--outlined" id="' + this.cardId + '_advanced_identifier" style="width: 100%">';
                htmlString += '        <input class="mdc-text-field__input" type="text" id="' + this.cardId + '_advanced_identifier_value">';
                htmlString += '        <div class="mdc-notched-outline">';
                htmlString += '          <div class="mdc-notched-outline__leading"></div>';
                htmlString += '          <div class="mdc-notched-outline__notch">';
                htmlString += '            <label for="' + this.cardId + '_advanced_identifier_value" class="mdc-floating-label">Card Identifier</label>';
                htmlString += '          </div>';
                htmlString += '          <div class="mdc-notched-outline__trailing"></div>';
                htmlString += '        </div>';
                htmlString += '      </div>';
                htmlString += '    </div>';
                htmlString += '    <div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12">';
                htmlString += '      <div class="mdc-text-field mdc-text-field--textarea mdc-text-field--outlined" id="' + this.cardId + '_advanced_comment_field" style="width: 100%">';
                htmlString += '        <div class="mdc-notched-outline">';
                htmlString += '          <div class="mdc-notched-outline__leading"></div>';
                htmlString += '          <div class="mdc-notched-outline__notch">';
                htmlString += '            <label for="' + this.cardId + '_advanced_comment_value" class="mdc-floating-label">Comment</label>';
                htmlString += '          </div>';
                htmlString += '          <div class="mdc-notched-outline__trailing"></div>';
                htmlString += '        </div>';
                htmlString += '        <textarea class="mdc-text-field__input" rows="4" style="width: 100%" id="' + this.cardId + '_advanced_comment_value"></textarea>';
                htmlString += '      </div>';
                htmlString += '    </div>';
                htmlString += '  </div>';
                htmlString += '</div>';

            return htmlString
        }

        viewHtml() {
            var htmlString  = '<div class="mdc-card" id="' + this.cardId + '" style="' + this.style() + '"  data-node-id="' + this.id + '">';
                htmlString += '  <h6 class="mdc-typography--headline6" style="margin: 16px; margin-bottom: 0;"><span style="float: right">' + this.cardIcon() + '</span>' + this.cardName() + '</h6>';
                // htmlString += '  <h6 class="mdc-typography--caption" style="margin: 16px; margin-bottom: 0; margin-top: 0;">' + this.id + '</h6>';
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

        static cardIdExists(cardId, sequence) {
            if (cardId != "") {
                var node = sequence.resolveNode(cardId);

                if (node != null) {
                    return true;
                }
            }

            return false;
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

        static newNodeId(cardName, sequence) {
            var newIdBase = Node.slugify(cardName);
            
            if (Node.cardIdExists(newIdBase, sequence) == false) {
                return newIdBase;
            }
            
            var index = 1;
            
            var newId = newIdBase + '-' + index;
            
            while (Node.cardIdExists(newId, sequence)) {
                index += 1;

                newId = newIdBase + '-' + index;
            }
            
            return newId;
        }
        
        static slugify(text){
            return text.toString().toLowerCase()
                .replace(/\s+/g, '-')           // Replace spaces with -
                .replace(/[^\w\-]+/g, '')       // Remove all non-word chars
                .replace(/\-\-+/g, '-')         // Replace multiple - with single -
                .replace(/^-+/, '')             // Trim - from start of text
                .replace(/-+$/, '');            // Trim - from end of text
        }

        static cardName() {
            return 'Node';
        }
    }

    return Node;
});