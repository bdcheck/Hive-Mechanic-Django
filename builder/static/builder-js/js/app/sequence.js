var modules = ["material", 'cards/node', 'jquery'];

if (window.dialogBuilder.cards != undefined) {
    var cards = window.dialogBuilder.cards;

    for (var i = 0; i < cards.length; i++) {
        modules.push(cards[i]);
    }
}

define(modules, function (mdc, Node) {
    class Sequence {
        constructor(definition) {
            this.definition = definition;
            this.changeListeners = [];
        }

        allActions() {
            var actions = [];

            for (var i = 0; i < this.definition["items"].length; i++) {
                var item = this.definition["items"][i];

                var action = {"id": item["id"]};

                if (item["name"] != undefined) {
                    action["name"] = item["name"];
                } else {
                    action["name"] = item["id"];
                }

                actions.push(action);
            }

            return actions;
        }

        name() {
            return this.definition['name'];
        }

        identifier() {
            return this.definition['id'];
        }

        selectInitialNode(nodeId) {
            if (typeof nodeId == 'undefined') {
                throw "Undefined Node Id";
            }

            $("#sequence_breadcrumbs").html(this.name());

            if (nodeId == null || nodeId == undefined) {
                this.loadNode(this.definition.items[0]);
            } else {
                var loaded = false;

                for (var i = 0; loaded == false && i < this.definition.items.length; i++) {
                    var item = this.definition.items[i];

                    if (nodeId == item["id"] || nodeId.endsWith("#" + item["id"])) {
                        this.loadNode(item);

                        loaded = true;
                    }
                }

                if (loaded == false) {
                    this.loadNode(this.definition.items[0]);
                }
            }
        }

        loadNode(definition) {
            var me = this;

            if (definition != undefined) {
                for (var i = 0; i < window.dialogBuilder.definition.sequences.length; i++) {
                    var sequence = window.dialogBuilder.definition.sequences[i];

                    if (sequence["id"] != this.definition["id"]) {
                        for (var j = 0; j < sequence["items"].length; j++) {
                            var item = sequence["items"][j];

                            if (item["id"] == definition["id"]) {
                                window.dialogBuilder.loadSequence(sequence, definition['id']);

                                return;
                            }
                        }
                    }
                }

                var node = Node.createCard(definition, this);

                var current = $("#builder_current_node");

                var html = node.editHtml();

                current.html(html);

                node.initialize();

                if ($("#sequence_breadcrumbs").children("#breadcrumb-" + node.id).length > 0) {
                    var match = $("#sequence_breadcrumbs").children("#breadcrumb-" + node.id);
                    var last = $("#sequence_breadcrumbs").children().last();

                    while (match.attr("id") != last.attr("id")) {

                        last.remove();

                        last = $("#sequence_breadcrumbs").children().last();
                    }
                } else {
                    var chevron = '<i class="material-icons" style="font-size: 0.75rem;">chevron_right</i>';
                    var breadcrumb = '<a id="breadcrumb-' + node.id + '" href="#">' + node.cardName() + '</a>';

                    $("#sequence_breadcrumbs").append(chevron + breadcrumb);

                    $("#breadcrumb-" + node.id).click(function(eventObj) {
                        eventObj.preventDefault();

                        me.loadNode(definition);

                        return false;
                    })
                }

                var destinations = $("#builder_next_nodes");

                var destinationNodes = node.destinationNodes(this);

                var destinationHtml = '';

                for (var i = 0; i < destinationNodes.length; i++) {
                    destinationHtml += destinationNodes[i].viewHtml();
                }

                destinations.html(destinationHtml);

                for (var i = 0; i < destinationNodes.length; i++) {
                    const destinationNode = destinationNodes[i];

                    $("#" + destinationNode["cardId"]).css("background-color", "#E0E0E0");

                    destinationNode.onClick(function() {
                        me.loadNode(destinationNode.definition);
                    });
                }

                var sources = $("#builder_source_nodes");

                var sourceNodes = node.sourceNodes(this);

                var sourceHtml = '';

                for (var i = 0; i < sourceNodes.length; i++) {
                    sourceHtml += sourceNodes[i].viewHtml();
                }

                sources.html(sourceHtml);

                for (var i = 0; i < sourceNodes.length; i++) {
                    const sourceNode = sourceNodes[i];

                    sourceNode.onClick(function() {
                        me.loadNode(sourceNode.definition);
                    });
                }
            } else {
                me.addCard(function(cardId) {
                    for (var j = 0; j < me.definition["items"].length; j++) {
                        var item = me.definition["items"][j];

                        if (item["id"] == cardId) {
                            me.loadNode(item);

                            return;
                        }
                    }
                });
            }
        }

        checkCorrectness() {
            var items = this.definition.items;

            for (var i = 0; i < items.length; i++) {
                var item = items[i];

                if (Node.canCreateCard(item, this) == false) {
                    console.log("Cannot create node for item:");
                    console.log(item);
                }
            }
        }

        addChangeListener(changeFunction) {
            this.changeListeners.push(changeFunction);
        }

        removeChangeListener(changeFunction) {
            var index = this.changeListeners.indexOf(changeFunction);

            if (index >= 0) {
                this.changeListeners.splice(index, 1);
            }
        }

        markChanged(changedId) {
            for (var i = 0; i < this.changeListeners.length; i++) {
                this.changeListeners[i](changedId);
            }
        }

        removeCard(identifier) {
            var removeIndex = -1;

            for (var i = 0; i < this.definition.items.length; i++) {
                var item = this.definition.items[i];

                if (item['id'] == identifier) {
                    removeIndex = i;
                }
            }

            if (removeIndex == -1) {
                for (var i = 0; i < this.definition.items.length; i++) {
                    var item = this.definition.items[i];

                    if (item['id'] == this.definition["id"] + "#" + identifier) {
                        removeIndex = i;
                    }
                }
            }

            if (removeIndex != -1) {
                var node = Node.createCard(item, this);

                var sources = node.sourceNodes(this);
                var destinations = node.destinationNodes(this);

                for (var i = 0; i < sources.length; i++) {
                    var node = sources[i];

                    node.updateReferences(identifier, null);
                    node.updateReferences(this.definition["id"] + "#" + identifier, null);
                }

                for (var i = 0; i < destinations.length; i++) {
                    var node = destinations[i];

                    node.updateReferences(identifier, null);
                    node.updateReferences(this.definition["id"] + "#" + identifier, null);
                }

                this.definition.items.splice(removeIndex, 1);

                this.markChanged(null);

                window.dialogBuilder.reloadSequences();
                window.dialogBuilder.loadSequence(this.definition, null);
            }
        }

        issues() {
            var sequenceIssues = [];

            var seenIds = [];

            for (var i = 0; i < this.definition.items.length; i++) {
                var item = this.definition.items[i];

                var node = Node.createCard(item, this);

                var id = item['id'];

                if (seenIds.indexOf(id) == -1) {
                    var nodeIssues = node.issues(this);

                    sequenceIssues = sequenceIssues.concat(nodeIssues)
                    seenIds.push(id);
                } else {
                    sequenceIssues.push(['Duplicate ID "' + id + '" in "' + this.definition['name'] + '".', 'sequence', this.definition["id"]]);
                }
            }

            return sequenceIssues;
        }

        chooseDestinationSelect(cardId) {
            var body = '';
            body += '<div class="mdc-select mdc-select--outlined" id="' + cardId + '_destination" style="width: 100%; margin-top: 8px;">';
            body += '  <i class="mdc-select__dropdown-icon"></i>';
            body += '    <select class="mdc-select__native-control" id="">';
            body += '      <option value="" disabled selected></option>';

            var actions = this.allActions();

            for (var i = 0; i < actions.length; i++) {
                var action = actions[i];

                body += '      <option value="' + action['id'] + '">' + action['name'] + '</option>';
            }

            body += '      <option value="add_card">Add&#8230;</option>';
            body += '    </select>';
            body += '  <div class="mdc-notched-outline">';
            body += '    <div class="mdc-notched-outline__leading"></div>';
            body += '    <div class="mdc-notched-outline__notch">';
            body += '      <label class="mdc-floating-label">Destination</label>';
            body += '    </div>';
            body += '    <div class="mdc-notched-outline__trailing"></div>';
            body += '  </div>';
            body += '</div>';

            return body;
        }

        refreshDestinationSelect(cardId) {
            var selectId = '#' + cardId + '_destination select';

            $(selectId).empty();

            $(selectId).append('<option value="" disabled selected></option>');

            var actions = this.allActions();

            for (var i = 0; i < actions.length; i++) {
                var action = actions[i];

                $(selectId).append('<option value="' + action['id'] + '">' + action['name'] + '</option>');
            }

            $(selectId).append('<option value="add_card">Add&#8230;</option>');
        }

        chooseDestinationMenu(cardId) {
            var me = this;
            var body = '';

            body += '    <ul class="mdc-list mdc-dialog__content dialog_card_selection_menu" role="menu" aria-hidden="true" aria-orientation="vertical" tabindex="-1">';

            $.each(window.dialogBuilder.definition.sequences, function(index, value) {
                body += '      <li class="mdc-list-item mdc-list-item--with-one-line prevent-menu-close" role="menuitem" id="' + cardId + '_destination_sequence_' + value['id'] + '">';
                body += '        <span class="mdc-list-item__ripple"></span>';
                body += '        <span class="mdc-list-item__text mdc-list-item__start">' + value['name'] + '</span>';
                body += '        <span class="mdc-layout-grid--align-right mdc-list-item__end material-icons destination_disclosure_icon">arrow_right</span>';
                body += '      </li>';

                var items = value['items'];

                for (var i = 0; i < items.length; i++) {
                    var item = items[i];

                    body += '     <li class="mdc-list-item mdc-list-item--with-one-line builder-destination-item ' + cardId + '_destination_sequence_' + value['id'] + '_item" role="menuitem" id="' + cardId + '_destination_item_' + item['id'] + '" data-node-id="' + value['id'] + '#' + item['id'] + '">';
                    body += '       <span class="mdc-list-item__ripple"></span>';
                    body += '       <span class="mdc-list-item__text mdc-list-item__start">' + item["name"] + '</span>';
                    body += '     </li>';
                }

                body += '      <li class="mdc-list-divider" role="separator"></li>';
            });

            body += '      <li class="mdc-list-item mdc-list-item--with-one-line" role="menuitem" id="' + cardId + '_destination_item_add_card">';
            body += '        <span class="mdc-list-item__ripple"></span>';
            body += '        <span class="mdc-list-item__text mdc-list-item__start">Add&#8230;</span>';
            body += '        <span class="mdc-layout-grid--align-right mdc-list-item__end material-icons">add</span>';
            body += '      </li>';

            body += '    </ul>';

            return body;
        }

        refreshDestinationMenu(updateFunction) {
            $("#select-card-destination-edit-dialog-menu").html("");

            var me = this;
            var body = '';

            $.each(window.dialogBuilder.definition.sequences, function(index, value) {
                var sequenceBody = "";

                sequenceBody += '      <li class="mdc-list-item mdc-list-item--with-one-line prevent-menu-close" role="menuitem" id="choose_destination_sequence_' + value['id'] + '">';
                sequenceBody += '        <span class="mdc-list-item__ripple"></span>';
                sequenceBody += '        <span class="mdc-list-item__text mdc-list-item__start">' + value['name'] + '</span>';
                sequenceBody += '        <span class="mdc-layout-grid--align-right mdc-list-item__end material-icons destination_disclosure_icon">arrow_right</span>';
                sequenceBody += '      </li>';

                var items = value['items'];

                for (var i = 0; i < items.length; i++) {
                    var item = items[i];

                    sequenceBody += '     <li class="mdc-list-item mdc-list-item--with-one-line builder-destination-item choose_destination_sequence_' + value['id'] + '_item" role="menuitem" id="choose_destination_item_' + item['id'] + '" data-node-id="' + value['id'] + '#' + item['id'] + '">';
                    sequenceBody += '       <span class="mdc-list-item__ripple"></span>';
                    sequenceBody += '       <span class="mdc-list-item__text mdc-list-item__start">' + item["name"] + '</span>';
                    sequenceBody += '     </li>';
                }

                sequenceBody += '      <li class="mdc-list-divider" role="separator"></li>';

                $("#select-card-destination-edit-dialog-menu").append(sequenceBody);
            });

            var addCardBody = '      <li class="mdc-list-item mdc-list-item--with-one-line" role="menuitem" id="choose_destination_item_add_card">';
            addCardBody    += '        <span class="mdc-list-item__ripple"></span>';
            addCardBody    += '        <span class="mdc-list-item__text mdc-list-item__start">Add&#8230;</span>';
            addCardBody    += '        <span class="mdc-layout-grid--align-right mdc-list-item__end material-icons">add</span>';
            addCardBody    += '      </li>';

            $("#select-card-destination-edit-dialog-menu").append(addCardBody);

            const options = document.querySelectorAll('.dialog_card_selection_menu .mdc-list-item');

            for (let option of options) {
                $(option).off('click');

                option.addEventListener('click', (event) => {
                    let prevent = event.currentTarget.classList.contains('prevent-menu-close');

                    if (prevent) {
                        event.stopPropagation();

                        var id = event.currentTarget.id;

                        id = id.replace('choose_destination_sequence_', '')

                        $(".builder-destination-item").hide();

                        var icon = '#choose_destination_sequence_' + id + ' .destination_disclosure_icon';

                        var isVisible = $(icon).html() == "arrow_drop_down";

                        $(".destination_disclosure_icon").text("arrow_right");

                        if (isVisible) {
                            $(icon).text("arrow_right");

                            $('.choose_destination_sequence_' + id + '_item').hide();
                        } else {
                            $('#choose_destination_sequence_' + id + " .destination_disclosure_icon").text("arrow_drop_down");

                            $('.choose_destination_sequence_' + id + '_item').show();
                        }
                    } else {
                        var nodeId = $(event.currentTarget).attr("data-node-id");

                        var id = event.currentTarget.id;

                        id = id.replace('choose_destination_item_', '')

                        if (id == "add_card") {
                            window.dialogBuilder.chooseDestinationDialog.close();

                            me.addCard(window.dialogBuilder.chooseDestinationDialogCallback);
                        } else {
                            window.dialogBuilder.chooseDestinationDialogCallback(nodeId);
                        }
                    }
                });
            }

            $(".builder-destination-item").hide();

            window.dialogBuilder.chooseDestinationDialogCallback = updateFunction;
        }

        initializeDestinationMenu() {
            var me = this;

            const options = document.querySelectorAll('.dialog_card_selection_menu .mdc-list-item');

            for (let option of options) {
                $(option).off('click');

                option.addEventListener('click', (event) => {
                    let prevent = event.currentTarget.classList.contains('prevent-menu-close');

                    if (prevent) {
                        event.stopPropagation();

                        var id = event.currentTarget.id;

                        id = id.replace('choose_destination_sequence_', '')

                        $(".builder-destination-item").hide();

                        var icon = '#choose_destination_sequence_' + id + ' .destination_disclosure_icon';

                        var isVisible = $(icon).html() == "arrow_drop_down";

                        $(".destination_disclosure_icon").text("arrow_right");

                        if (isVisible) {
                            $(icon).text("arrow_right");

                            $('.choose_destination_sequence_' + id + '_item').hide();
                        } else {
                            $('#choose_destination_sequence_' + id + " .destination_disclosure_icon").text("arrow_drop_down");

                            $('.choose_destination_sequence_' + id + '_item').show();
                        }
                    } else {
                        var nodeId = $(event.currentTarget).attr("data-node-id");

                        var id = event.currentTarget.id;

                        id = id.replace('choose_destination_item_', '');
                        
                        console.log('CLICKED ID: ' + id);

                        if (id == "add_card") {
                            me.addCard(window.dialogBuilder.chooseDestinationDialogCallback);
                        } else {
                            window.dialogBuilder.chooseDestinationDialogCallback(nodeId);
                        }
                    }
                });
            }

            $(".builder-destination-item").hide();
        }

        addCard(callback) {
            $("#add-card-name-value").val("");


            // window.dialogBuilder.newCardSelect.value = '';

            const nameField = mdc.textField.MDCTextField.attachTo(document.getElementById('add-card-name'));

            var me = this;

            var listener = {
                handleEvent: function (event) {
                    if (event.detail.action == "add_card") {
                        var cardName = nameField.value
                        var cardType = $("input[name='add-card-options']:checked").val(); //  window.dialogBuilder.newCardSelect.value;
                        
                        if (cardName.trim() == '') {
							var selectedCard = $("input[name='add-card-options']:checked").parent().parent().parent().find('label').text();

							cardName = 'New ' + selectedCard + ' Card';
						}

                        var cardClass = window.dialogBuilder.cardMapping[cardType];

                        var cardDef = cardClass.createCard(cardName);
                        cardDef['id'] = Node.newNodeId(cardName, me);

                        if (me.definition["items"].includes(cardDef) == false) {
                            me.definition["items"].push(cardDef);
                        }

                        callback(cardDef["id"]);

                        window.dialogBuilder.addCardDialog.unlisten('MDCDialog:closed', this);
                   }
                }
            };

			$('input[type=radio][name=add-card-options]').change(function() {
				var cardName = nameField.value;
				
				if (cardName.trim() == '' || (cardName.startsWith('New ') && cardName.endsWith(' Card'))) {
					var selectedCard = $(this).parent().parent().parent().find('label').text();
				
					cardName = 'New ' + selectedCard + ' Card';
					
					nameField.value = cardName;
				}
			});

            window.dialogBuilder.addCardDialog.listen('MDCDialog:closed', listener);

            window.dialogBuilder.addCardDialog.open();
        }

        resolveNode(nodeId) {
            if (nodeId == null) {
                return null;
            }
            
            if (nodeId.includes("#") == false) {
            	nodeId = this.definition["id"] + "#" + nodeId;
            }
            
            if (nodeId.startsWith(this.definition["id"] + "#")) {
                for (var i = 0; i < this.definition["items"].length; i++) {
                    var item = this.definition["items"][i];

                    if (nodeId.endsWith("#" + item["id"])) {
                        return Node.createCard(item, this);
                    }
                }
            } else {
                for (var i = 0; i < window.dialogBuilder.definition.sequences.length; i++) {
                    var sequence = window.dialogBuilder.definition.sequences[i];

                    if (nodeId.startsWith(sequence["id"] + "#")) {
                        return this.loadSequence(sequence).resolveNode(nodeId);
                    }
                }
            }

            return null;
        }

        loadSequence(definition) {
            var sequence = new Sequence(definition);

            sequence.checkCorrectness();

            return sequence;
        }
    }

    var sequence = {}

    sequence.loadSequence = function(definition) {
        var sequence = new Sequence(definition);

        sequence.checkCorrectness();

        return sequence;
    }

    return sequence;
});
