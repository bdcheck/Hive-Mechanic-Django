requirejs.config({
    shim: {
        jquery: {
            exports: "$"
        },
        cookie: {
            exports: "Cookies"
        },
        bootstrap: {
            deps: ["jquery"]
        },
    },
    baseUrl: "/static/builder-js/js/app",
    paths: {
        app: '/static/builder-js/js/app',
        material: "/static/builder-js/vendor/material-components-web-11.0.0",
        jquery: "/static/builder-js/vendor/jquery-3.4.0.min",
        cookie: "/static/builder-js/vendor/js.cookie"
    }
});

requirejs(["material", "app/sequence", "cookie", "cards/node", "jquery"], function(mdc, sequence, Cookies, Node) {
    const drawer = mdc.drawer.MDCDrawer.attachTo(document.querySelector('.mdc-drawer'));

    const topAppBar = mdc.topAppBar.MDCTopAppBar.attachTo(document.getElementById('app-bar'));

    const warningDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('builder-outstanding-issues-dialog'));

    window.dialogBuilder.selectCardsDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('builder-select-card-dialog'));

    window.dialogBuilder.restartGameDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('builder-reset-game-dialog'));

    window.dialogBuilder.restartGameDialog.listen('MDCDialog:closed', (result) => {
    	console.log("ACTION: ");
    	console.log(result);
	});

    const activityName = mdc.textField.MDCTextField.attachTo(document.getElementById('builder-activity-setting-activity-name'));
    var initialCardSelect = null;

    var selectedSequence = null;

    topAppBar.setScrollTarget(document.getElementById('main-content'));

    topAppBar.listen('MDCTopAppBar:nav', () => {
        drawer.open = !drawer.open;
    });

    function onSequenceChanged(changedId) {
        $("#action_save").text("save");

        if (window.dialogBuilder.definition.sequences != undefined) {
            var issues = [];

            $(".outstanding-issue-item").remove();

            for (var i = 0; i < window.dialogBuilder.definition.sequences.length; i++) {

                var loadedSequence = sequence.loadSequence(window.dialogBuilder.definition.sequences[i]);

                var sequenceIssues = loadedSequence.issues();

                issues = issues.concat(sequenceIssues);
            }

            if (issues.length > 0) {
                for (var i = 0; i < issues.length; i++) {
                    var issue = issues[i];

                    var item = '<li class="mdc-list-item prevent-menu-close outstanding-issue-item" role="menuitem" id="builder-outstanding-issues-dialog-' + issue[2] + '">';
                    item +=    '  <span class="mdc-list-item__text">';
                    item +=    '    <span class="mdc-list-item__primary-text">' + issue[0] + '</span>';
                    item +=    '    <span class="mdc-list-item__secondary-text">' + issue[3] + '</span>';
                    item +=    '  </span>';
                    item +=    '</li>';

                    $(item).insertBefore(".outstanding-issue-items .mdc-list-divider");
                }

                $("#action_save").text("warning");

                const options = document.querySelectorAll('.outstanding-issue-item');

                for (let option of options) {
                    option.addEventListener('click', (event) => {
                        var id = event.currentTarget.id;

                        id = id.replace('builder-outstanding-issues-dialog-', '')

                        for (var i = 0; i < window.dialogBuilder.definition.sequences.length; i++) {
                            var sequence = window.dialogBuilder.definition.sequences[i];

                            for (var j = 0; j < sequence["items"].length; j++) {
                                var item = sequence["items"][j];

                                if (item["id"] == id) {
                                    window.dialogBuilder.loadSequence(sequence, id);

                                    warningDialog.close();

                                    return;
                                }
                            }
                        }
                    });
                }
            }
        }

        $("#action_save").show();
    }

    function slugify(text){
        return text.toString().toLowerCase()
            .replace(/\s+/g, '-')           // Replace spaces with -
            .replace(/[^\w\-]+/g, '')       // Remove all non-word chars
            .replace(/\-\-+/g, '-')         // Replace multiple - with single -
            .replace(/^-+/, '')             // Trim - from start of text
            .replace(/-+$/, '');            // Trim - from end of text
    }

    window.dialogBuilder.removeSequence = function(sequenceDefinition) {
        window.dialogBuilder.definition.sequences = window.dialogBuilder.definition.sequences.filter(function(value) {
            return value != sequenceDefinition;
        });

        window.dialogBuilder.reloadSequences();

        window.dialogBuilder.loadSequence(window.dialogBuilder.definition.sequences[0], null);

        $("#action_save").show();
    }

    function cleanDefinition(definition) {
    	if (definition == null) {
    		return null;
    	} else if (Array.isArray(definition)) {
    		var cleanArray = [];

            $.each(definition, function(index, item) {
                cleanArray.push(cleanDefinition(item));
            });

            return cleanArray;
    	} else if (typeof definition === 'object') {
    		var cleanObject = {};

            $.each(Object.keys(definition), function(index, key) {
            	if (key.indexOf('__') == -1) {
	            	cleanObject[key] = cleanDefinition(definition[key])
            	}
            });

    		return cleanObject;
    	}

    	return definition;
    }

    var editListener = undefined;

    var removeListener = undefined;

    window.dialogBuilder.loadSequence = function(definition, initialId) {
        if (selectedSequence != null) {
            selectedSequence.removeChangeListener(onSequenceChanged);
        }

        selectedSequence = sequence.loadSequence(definition);

        $(".mdc-top-app-bar__title").html(selectedSequence.name());

        selectedSequence.addChangeListener(onSequenceChanged);

        $("#action_edit_sequence").off("click");

        $("#action_edit_sequence").click(function(eventObj) {
            eventObj.preventDefault();

            $("#edit-sequence-name-value").val(selectedSequence.name());

            window.dialogBuilder.editSequenceDialog.unlisten('MDCDialog:closed', editListener);

            editListener = {
                handleEvent: function (event) {
                    if (event.detail.action == "update_sequence") {
                        var name = $("#edit-sequence-name-value").val();

                        definition["name"] = name;
                        $(".mdc-top-app-bar__title").html(name);

                        window.dialogBuilder.reloadSequences();

                        $("#action_save").show();

                        window.dialogBuilder.editSequenceDialog.unlisten('MDCDialog:closed', this);
                   }
                }
            };

            window.dialogBuilder.editSequenceDialog.listen('MDCDialog:closed', editListener);

            window.dialogBuilder.editSequenceDialog.open()
        });

        $("#action_remove_sequence").click(function(eventObj) {
            eventObj.preventDefault();

            $("#remove-sequence-name-value").html(selectedSequence.name());

            window.dialogBuilder.removeSequenceDialog.unlisten('MDCDialog:closed', removeListener);

            removeListener = {
                handleEvent: function (event) {
                    if (event.detail.action == "remove_sequence") {
                        var name = $("#edit-sequence-name-value").val();

                        window.dialogBuilder.removeSequence(definition);

                        window.dialogBuilder.editSequenceDialog.unlisten('MDCDialog:closed', this);
                   }
                }
            };

            window.dialogBuilder.removeSequenceDialog.listen('MDCDialog:closed', removeListener);

            window.dialogBuilder.removeSequenceDialog.open()
        });

        selectedSequence.selectInitialNode(initialId);
    };

    $("#action_save").hide();

    window.dialogBuilder.reloadSequences = function() {
        var items = [];

        $.each(window.dialogBuilder.definition.sequences, function(index, value) {
            items.push('<li class="mdc-list-item mdc-list-item--with-one-line select_sequence" href="#" data-index="' + index +'">');
            items.push('<span class="mdc-list-item__ripple"></span>');
            items.push('<span class="material-icons mdc-list-item__start" aria-hidden="true">view_module</span>');
            items.push('<span class="mdc-list-item__text mdc-list-item__end" style="margin-left: 16px;">' + value['name'] + '</span>');
            items.push('</li>');
        });

        items.push('<li class="mdc-list-item mdc-list-item--with-one-line add_sequence" href="#" style="margin-top: 2em;">');
        items.push('<span class="mdc-list-item__ripple"></span>');
        items.push('<span class="material-icons mdc-list-item__start" aria-hidden="true">add_box</span>');
        items.push('<span class="mdc-list-item__text mdc-list-item__end" style="margin-left: 16px;">Add Sequence</span>');
        items.push('</li>');

        items.push('<div role="separator" class="mdc-list-divider"></div>');

        items.push('<li class="mdc-list-item mdc-list-item--with-one-line go_home" href="#" style="margin-top: 1em;">');
        items.push('<span class="mdc-list-item__ripple"></span>');
        items.push('<span class="material-icons mdc-list-item__start" aria-hidden="true">home</span>');
        items.push('<span class="mdc-list-item__text mdc-list-item__end" style="margin-left: 16px;">Return to Home</span>');
        items.push('</li>');

        $("#sequences_list").html(items.join(""));

		const sequencesList = mdc.list.MDCList.attachTo(document.getElementById('sequences_list'));

        $(".select_sequence").off("click");
        $(".select_sequence").click(function(eventObj) {
			$("#settings-view").hide();
			$("#editor-view").show();

            window.dialogBuilder.loadSequence(window.dialogBuilder.definition.sequences[$(eventObj.target).data("index")], null);
        });

        $(".add_sequence").off("click");
        $(".add_sequence").click(function(eventObj) {
            var listener = {
                handleEvent: function (event) {
                    if (event.detail.action == "add_sequence") {
                        var sequenceName = $("#add-sequence-name-value").val();

                        var sequence = {
                            "id": slugify(sequenceName),
                            "type": "sequence",
                            "name": sequenceName,
                            "items": []
                        }

                        window.dialogBuilder.definition.sequences.push(sequence);

                        window.dialogBuilder.reloadSequences();

                        var last = window.dialogBuilder.definition.sequences.length - 1;

                        window.dialogBuilder.loadSequence(window.dialogBuilder.definition.sequences[last], null);

                        window.dialogBuilder.addSequenceDialog.unlisten('MDCDialog:closed', this);
                   }
                }
            };

            window.dialogBuilder.addSequenceDialog.listen('MDCDialog:closed', listener);

            window.dialogBuilder.addSequenceDialog.open();
        });

        $(".go_home").off("click");
        $(".go_home").click(function(eventObj) {
            location.href = '/builder/';
        });

        var allCardSelectContent =  '';

        $.each(window.dialogBuilder.definition.sequences, function(index, value) {
            allCardSelectContent += '<li class="mdc-list-divider" role="separator"></li>';
            allCardSelectContent += '<li class="mdc-list-item mdc-list-item--with-one-line prevent-menu-close" role="menuitem" id="all_cards_destination_sequence_' + value['id'] + '">';
            allCardSelectContent += '  <span class="mdc-list-item__ripple"></span>';
            allCardSelectContent += '  <span class="mdc-list-item__text mdc-list-item__start">' + value['name'] + '</span>';
            allCardSelectContent += '  <span class="mdc-list-item__end mdc-layout-grid--align-right material-icons destination_disclosure_icon">arrow_right</span>';
            allCardSelectContent += '</li>';

            var items = value['items'];

            for (var i = 0; i < items.length; i++) {
                var item = items[i];

                allCardSelectContent += '<li class="mdc-list-item mdc-list-item--with-one-line all-cards-select-item all_cards_destination_sequence_' + value['id'] + '_item" role="menuitem" id="all_cards_destination_item_' + item['id'] + '" data-node-id="' + value['id'] + '#' + item['id'] + '">';
	            allCardSelectContent += '  <span class="mdc-list-item__ripple"></span>';
                allCardSelectContent += '  <span class="mdc-list-item__text mdc-list-item__start">' + item["name"] + '</span>';
                allCardSelectContent += '</li>';
            }
        });


        $("#select-all-cards-items").html(allCardSelectContent);

        $(".all-cards-select-item").hide();

        $("#select-all-cards .mdc-list-item").off("click");

        const options = document.querySelectorAll('#select-all-cards-items .mdc-list-item');

        for (let option of options) {
            option.addEventListener('click', (event) => {
                let prevent = event.currentTarget.classList.contains('prevent-menu-close');

                if (prevent) {
                    event.stopPropagation();

                    var id = event.currentTarget.id;

                    id = id.replace('all_cards_destination_sequence_', '')

                    $(".all-cards-select-item").hide();

                    var icon = "#all_cards_destination_sequence_" + id + " .destination_disclosure_icon";

                    var isVisible = $(icon).html() == "arrow_drop_down";

                    $(".destination_disclosure_icon").text("arrow_right");

                    if (isVisible) {
                        $(icon).text("arrow_right");

                        $(".all_cards_destination_sequence_" + id + '_item').hide();
                    } else {
                        $("#all_cards_destination_sequence_" + id + " .destination_disclosure_icon").text("arrow_drop_down");

                        $(".all_cards_destination_sequence_" + id + '_item').show();
                    }
                } else {
                    $(".all-cards-select-item").hide();
                    $(".destination_disclosure_icon").text("arrow_right");

                    window.dialogBuilder.selectCardsDialog.close();

                    var nodeId = $(event.currentTarget).attr("data-node-id");

                    var id = event.currentTarget.id;

                    id = id.replace("all_cards_destination_item_", '');

                    window.dialogBuilder.loadNodeById(id);
                }
            });
        }
    }

    window.dialogBuilder.loadNodeById = function(cardId) {
        var me = this;

        for (var i = 0; i < window.dialogBuilder.definition.sequences.length; i++) {
            var sequence = window.dialogBuilder.definition.sequences[i];

            if (sequence["id"] != cardId) {
                for (var j = 0; j < sequence["items"].length; j++) {
                    var item = sequence["items"][j];

                    if (item["id"] == cardId) {
                        window.dialogBuilder.loadSequence(sequence, item['id']);

						$('#' + item['id'] + '-advanced-dialog').remove();

                        var node = Node.createCard(item, sequence);

                        var current = $("#builder_current_node");

                        var html = node.editHtml();

                        current.html(html);

                        node.initialize();

                        return;
                    }
                }
            }
        }
    };

    $.getJSON(window.dialogBuilder.source, function(data) {
        window.dialogBuilder.definition = data;

        if (window.dialogBuilder.definition['interrupts'] != undefined) {
            var toRemove = [];

            for (var i = 0; i < window.dialogBuilder.definition['interrupts'].length; i++) {
                var interrupt = window.dialogBuilder.definition['interrupts'][i];

                if (interrupt['pattern'] == '' || interrupt['action'] == '') {
                    toRemove.push(i);
                }
            }

            while (toRemove.length > 0) {
                var removeIndex = toRemove.pop();

                window.dialogBuilder.definition['interrupts'].splice(removeIndex, 1);
            }
        }

        $("#action_save").off("click");

        $("#action_save").click(function(eventObj) {
            eventObj.preventDefault();

            if (window.dialogBuilder.update != undefined) {
                if ($("#action_save").text() == "warning") {
                    warningDialog.open();
                } else {
                	var clean = cleanDefinition(window.dialogBuilder.definition);

                    window.dialogBuilder.update(clean, function() {
                        $("#action_save").hide();
                    }, function(error) {
                        console.log(error);
                    });
                }
            }
        });

        $("#action_select_card").off("click");

        $("#action_select_card").click(function(eventObj) {
            eventObj.preventDefault();

            window.dialogBuilder.selectCardsDialog.open();
        });

        $("#action_reset_game").off("click");

        $("#action_reset_game").click(function(eventObj) {
            eventObj.preventDefault();

            window.dialogBuilder.restartGameDialog.open();
        });

        var keys = Object.keys(window.dialogBuilder.cardMapping);

        keys.sort(function(one, two) {
            var oneNodeClass = window.dialogBuilder.cardMapping[one];
            var oneName = oneNodeClass.cardName();

            var twoNodeClass = window.dialogBuilder.cardMapping[two];
            var twoName = twoNodeClass.cardName();
            
            if (oneName < twoName) {
                return -1;
            } else if (oneName > twoName) {
                return 1;
            }
            
            return 0;
        });

        for (var i = 0; i < keys.length; i++) {
            var key = keys[i];

            var nodeClass = window.dialogBuilder.cardMapping[key];

            var name = nodeClass.cardName();

            if (name == Node.cardName()) {
                name = key;
            }

//            var cardItem = '<li class="mdc-list-item" data-value="' + key + '" role="option">' +
//						   ' <span class="mdc-list-item__ripple"></span>' +
//						   ' <span class="mdc-list-item__text">' + name + '<span>' +
//						   '</li>';

            var cardItem = '';

			cardItem += '<li class="mdc-list-item mdc-list-item--with-one-line prevent-menu-close" role="radio" tabindex="' + i + '" style="padding-left: 0; padding-right: 0;">';
			cardItem += '  <span class="mdc-list-item__graphic">';
			cardItem += '    <div class="mdc-radio">';
			cardItem += '      <input class="mdc-radio__native-control" type="radio" id="add-card-option-' + i + '" name="add-card-options" value="' + key + '">';
			cardItem += '      <div class="mdc-radio__background">';
			cardItem += '        <div class="mdc-radio__outer-circle"></div>';
			cardItem += '        <div class="mdc-radio__inner-circle"></div>';
			cardItem += '      </div>';
			cardItem += '    </div>';
			cardItem += '  </span>';
			cardItem += '  <label id="add-card-option-' + i + '-label" for="add-card-option-' + i + '" class="mdc-list-item__text" style="padding-top: 8px;">' + name + '</label>';
			cardItem += '</li>';

            $("#add-card-select-widget").append(cardItem);
        }

        window.dialogBuilder.addCardDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('add-card-dialog'));
        mdc.textField.MDCTextField.attachTo(document.getElementById('add-card-name'));

        // window.dialogBuilder.newCardSelect = mdc.select.MDCSelect.attachTo(document.getElementById('add-card-type'));
        // window.dialogBuilder.newCardSelect = mdc.radio.MDCRadio.attachTo(document.getElementById('add-card-type'));

        window.dialogBuilder.addSequenceDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('add-sequence-dialog'));
        mdc.textField.MDCTextField.attachTo(document.getElementById('add-sequence-name'));

        window.dialogBuilder.editSequenceDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('edit-sequence-dialog'));
        mdc.textField.MDCTextField.attachTo(document.getElementById('edit-sequence-name'));

        window.dialogBuilder.removeSequenceDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('remove-sequence-dialog'));

        window.dialogBuilder.helpToggle = mdc.switchControl.MDCSwitch.attachTo(document.getElementById('hive-help-switch'));

		$('#hive-help-switch-toggle').change(function() {
			if (window.dialogBuilder.helpToggle.checked) {
				$(".hive_mechanic_help_filler").hide()
				$(".hive_mechanic_help").show()
			} else {
				$(".hive_mechanic_help").hide()
				$(".hive_mechanic_help_filler").show()
			}
		});

		$(".hive_mechanic_help").hide();

	    window.dialogBuilder.chooseDestinationDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('select-card-destination-edit-dialog'));

        if (Array.isArray(window.dialogBuilder.definition)) {
            var game_def = {
                "sequences": window.dialogBuilder.definition,
                "interrupts": [],
                "name": "",
                "initial-card": null
            };

            window.dialogBuilder.definition = game_def;
        }

        window.dialogBuilder.loadSequence(window.dialogBuilder.definition.sequences[0], null);

        const warning = document.getElementById('builder-outstanding-issues-dialog-save');

        warning.addEventListener('click', (event) => {
			var clean = cleanDefinition(window.dialogBuilder.definition);

            window.dialogBuilder.update(clean, function() {
                $("#action_save").hide();

                warningDialog.close();
            }, function(error) {
                console.log(error);
            });

            return;
        });

        window.setTimeout(window.dialogBuilder.reloadSequences, 500);
    });

    $("#action_open_settings").off("click");

    var updatePattern = function(action, operation, pattern) {
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

    var chooseDestinationMenu = function(identifier) {
        var me = this;
        var body = '';

        body += '    <ul class="mdc-list mdc-dialog__content dialog_card_selection_menu" role="menu" aria-hidden="true" aria-orientation="vertical" tabindex="-1">';

        $.each(window.dialogBuilder.definition.sequences, function(index, value) {
            body += '      <li class="mdc-list-item mdc-list-item--with-one-line prevent-menu-close" role="menuitem" id="' + identifier + '_destination_sequence_' + value['id'] + '">';
            body += '        <span class="mdc-list-item__ripple"></span>';
            body += '        <span class="mdc-list-item__text mdc-list-item__start">' + value['name'] + '</span>';
            body += '        <span class="mdc-list-item__end material-icons mdc-layout-grid--align-right destination_disclosure_icon">arrow_right</span>';
            body += '      </li>';

            var items = value['items'];

            for (var i = 0; i < items.length; i++) {
                var item = items[i];

                body += '     <li class="mdc-list-item mdc-list-item--with-one-line builder-destination-item ' + identifier + '_destination_sequence_' + value['id'] + '_item" role="menuitem" id="' + identifier + '_destination_item_' + item['id'] + '" data-node-id="' + value['id'] + '#' + item['id'] + '">';
                body += '       <span class="mdc-list-item__ripple"></span>';
                body += '       <span class="mdc-list-item__text">' + item["name"] + '</span>';
                body += '     </li>';
            }

            body += '      <li class="mdc-list-divider" role="separator"></li>';
        });

        body += '    </ul>';

        return body;
    };

    var initializeDestinationMenu = function(identifier, onSelect) {
        var me = this;

        const options = document.querySelectorAll('.dialog_card_selection_menu .mdc-list-item');

        for (let option of options) {
            option.addEventListener('click', (event) => {
                let prevent = event.currentTarget.classList.contains('prevent-menu-close');

                if (prevent) {
                    event.stopPropagation();

                    var id = event.currentTarget.id;

                    id = id.replace(identifier + '_destination_sequence_', '')

                    $(".builder-destination-item").hide();

                    var icon = "#" + identifier + '_destination_sequence_' + id + " .destination_disclosure_icon";

                    var isVisible = $(icon).html() == "arrow_drop_down";

                    $(".destination_disclosure_icon").text("arrow_right");

                    if (isVisible) {
                        $(icon).text("arrow_right");

                        $("." + identifier + '_destination_sequence_' + id + '_item').hide();
                    } else {
                        $("#" + identifier + '_destination_sequence_' + id + " .destination_disclosure_icon").text("arrow_drop_down");

                        $("." + identifier + '_destination_sequence_' + id + '_item').show();
                    }
                } else {
                    var nodeId = $(event.currentTarget).attr("data-node-id");

                    onSelect(nodeId);
                }
            });
        }

        $(".builder-destination-item").hide();
    }

    $("#action_open_settings").click(function(eventObj) {
        eventObj.preventDefault();

        var refreshSettingsInterrupts = function() {
            $("#activity_settings_interrupts").empty();

            for (var i = 0; i < window.dialogBuilder.definition.interrupts.length; i++) {
                const interrupt = window.dialogBuilder.definition.interrupts[i];
                const identifier = 'activity_interrupt_pattern_' + i + '_response_value';

                var interruptBody = '';

                interruptBody += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-5">';
                interruptBody += '  <div class="mdc-select mdc-select--outlined" id="activity_interrupt_pattern_' + i + '" style="width: 100%;">';
                interruptBody += '    <div class="mdc-select__anchor">';
                interruptBody += '      <span class="mdc-notched-outline">';
                interruptBody += '        <span class="mdc-notched-outline__leading"></span>';
                interruptBody += '        <span class="mdc-notched-outline__notch">';
                interruptBody += '      	<span id="outlined-select-label" class="mdc-floating-label">Incoming Response&#8230;</span>';
                interruptBody += '        </span>';
                interruptBody += '        <span class="mdc-notched-outline__trailing"></span>';
                interruptBody += '      </span>';
                interruptBody += '      <span class="mdc-select__selected-text-container">';
                interruptBody += '        <span class="mdc-select__selected-text"></span>';
                interruptBody += '      </span>';
                interruptBody += '      <span class="mdc-select__dropdown-icon">';
                interruptBody += '        <svg';
                interruptBody += '      	  class="mdc-select__dropdown-icon-graphic"';
                interruptBody += '      	  viewBox="7 10 10 5" focusable="false">';
                interruptBody += '      	<polygon';
                interruptBody += '      		class="mdc-select__dropdown-icon-inactive"';
                interruptBody += '      		stroke="none"';
                interruptBody += '      		fill-rule="evenodd"';
                interruptBody += '      		points="7 10 12 15 17 10">';
                interruptBody += '      	</polygon>';
                interruptBody += '      	<polygon';
                interruptBody += '      		class="mdc-select__dropdown-icon-active"';
                interruptBody += '      		stroke="none"';
                interruptBody += '      		fill-rule="evenodd"';
                interruptBody += '      		points="7 15 12 10 17 15">';
                interruptBody += '      	</polygon>';
                interruptBody += '        </svg>';
                interruptBody += '      </span>';
                interruptBody += '    </div>';
                interruptBody += '    <div class="mdc-select__menu mdc-menu mdc-menu-surface mdc-menu-surface--fullwidth">';
                interruptBody += '      <ul class="mdc-list" role="listbox" aria>';
                
				interruptBody += '      <li class="mdc-list-item mdc-list-item--with-one-line" role="menuitem" data-value="begins_with">';
				interruptBody += '        <span class="mdc-list-item__ripple"></span>';
				interruptBody += '        <span class="mdc-list-item__text mdc-list-item__start">Begins with&#8230;</span>';
				interruptBody += '      </li>';

				interruptBody += '      <li class="mdc-list-item mdc-list-item--with-one-line" role="menuitem" data-value="ends_with">';
				interruptBody += '        <span class="mdc-list-item__ripple"></span>';
				interruptBody += '        <span class="mdc-list-item__text mdc-list-item__start">Ends with&#8230;</span>';
				interruptBody += '      </li>';

				interruptBody += '      <li class="mdc-list-item mdc-list-item--with-one-line" role="menuitem" data-value="equals">';
				interruptBody += '        <span class="mdc-list-item__ripple"></span>';
				interruptBody += '        <span class="mdc-list-item__text mdc-list-item__start">Equals&#8230;</span>';
				interruptBody += '      </li>';

				interruptBody += '      <li class="mdc-list-item mdc-list-item--with-one-line" role="menuitem" data-value="not_equals">';
				interruptBody += '        <span class="mdc-list-item__ripple"></span>';
				interruptBody += '        <span class="mdc-list-item__text mdc-list-item__start">Does not equal&#8230;</span>';
				interruptBody += '      </li>';

				interruptBody += '      <li class="mdc-list-item mdc-list-item--with-one-line" role="menuitem" data-value="contains">';
				interruptBody += '        <span class="mdc-list-item__ripple"></span>';
				interruptBody += '        <span class="mdc-list-item__text mdc-list-item__start">Contains&#8230;</span>';
				interruptBody += '      </li>';

				interruptBody += '      <li class="mdc-list-item mdc-list-item--with-one-line" role="menuitem" data-value="not_contains">';
				interruptBody += '        <span class="mdc-list-item__ripple"></span>';
				interruptBody += '        <span class="mdc-list-item__text mdc-list-item__start">Does not contain&#8230;</span>';
				interruptBody += '      </li>';

                interruptBody += '      </ul>';
                interruptBody += '    </div>';
                interruptBody += '  </div>';
                interruptBody += '</div>';

                interruptBody += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-4">';
                interruptBody += '  <div class="mdc-text-field mdc-text-field--outlined" id="activity_interrupt_pattern_' + i + '_response">';
                interruptBody += '    <input type="text" class="mdc-text-field__input" id="activity_interrupt_pattern_' + i + '_response_value">';
                interruptBody += '    <div class="mdc-notched-outline">';
                interruptBody += '      <div class="mdc-notched-outline__leading"></div>';
                interruptBody += '      <div class="mdc-notched-outline__notch">';
                interruptBody += '        <label for="activity_interrupt_pattern_' + i + '_response_value" class="mdc-floating-label">Value</label>';
                interruptBody += '      </div>';
                interruptBody += '      <div class="mdc-notched-outline__trailing"></div>';
                interruptBody += '    </div>';
                interruptBody += '  </div>';
                interruptBody += '</div>';

                interruptBody += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-3" style="text-align: right;">';
                interruptBody += '  <button class="mdc-icon-button" id="activity_interrupt_pattern_' + i + '_response_choose">';
                interruptBody += '    <i class="material-icons mdc-icon-button__icon" aria-hidden="true">link</i>';
                interruptBody += '  </button>';

                if (interrupt["action"] != undefined && interrupt["action"] != "") {
                    interruptBody += '  <button class="mdc-icon-button" id="activity_interrupt_pattern_' + i + '_response_click">';
                    interruptBody += '    <i class="material-icons mdc-icon-button__icon" aria-hidden="true">search</i>';
                    interruptBody += '  </button>';
                   }

                interruptBody += '</div>';

                $("#activity_settings_interrupts").append(interruptBody);

                const patternField = mdc.textField.MDCTextField.attachTo(document.getElementById('activity_interrupt_pattern_' + i + '_response'));
                const operationSelect = mdc.select.MDCSelect.attachTo(document.getElementById('activity_interrupt_pattern_' + i));

                window.setTimeout(function() {
                    updateViews(interrupt["pattern"], operationSelect, patternField);

                    operationSelect.listen('MDCSelect:change', () => {
                        updatePattern(interrupt, operationSelect.value, patternField.value);

                        $("#action_save").show();
                    });
                });

                $("#" + identifier).on("change keyup paste", function() {
                    updatePattern(interrupt, operationSelect.value, patternField.value);

                    $("#action_save").show();
                });

                $('#activity_interrupt_pattern_' + i + '_response_choose').on("click", function() {
                    const chooseDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('select-interrupt-dialog'));

                    $("#select-interrupt-dialog-content").html(chooseDestinationMenu("select-interrupt"));

                    initializeDestinationMenu("select-interrupt", function(nodeId) {
                        interrupt["action"] = nodeId;

                        refreshSettingsInterrupts();
                    });

                    chooseDialog.open();
                });

                $('#activity_interrupt_pattern_' + i + '_response_click').on("click", function() {
                    window.dialogBuilder.loadNodeById(interrupt["action"].split("#")[1]);
                    
					$("#settings-view").hide();
					$("#editor-view").show();
                });
            }
        };

        refreshSettingsInterrupts();

        var initialCardList = '    <ul class="mdc-list mdc-dialog__content initial_dialog_card_selection_menu" role="menu" aria-hidden="true" aria-orientation="vertical" tabindex="-1">';

        $.each(window.dialogBuilder.definition.sequences, function(index, value) {
        	if (index > 0) {
  	            initialCardList += '      <li class="mdc-list-divider" role="separator"></li>';
			}

			initialCardList += '      <li class="mdc-list-item mdc-list-item--with-one-line prevent-menu-close" role="menuitem" id="builder-activity-setting-initial-card-list-sequence-' + value['id'] + '">';
			initialCardList += '        <span class="mdc-list-item__ripple"></span>';
			initialCardList += '        <span class="mdc-list-item__text mdc-list-item__start">' + value['name'] + '</span>';
			initialCardList += '        <span class="mdc-layout-grid--align-right mdc-list-item__end material-icons destination_disclosure_icon">arrow_right</span>';
			initialCardList += '      </li>';

            var items = value['items'];

            for (var i = 0; i < items.length; i++) {
                var item = items[i];

				initialCardList += '      <li class="mdc-list-item mdc-list-item--with-one-line builder-destination-item builder-activity-setting-initial-card-list-sequence-' + value['id'] + '-item" role="menuitem" id="builder-activity-setting-initial-card-list-sequence-' + value['id'] + '" id="builder-activity-setting-initial-card-list-destination-item-' + item['id'] + '" data-node-id="' + value['id'] + '#' + item['id'] + '" data-value="' + value['id'] + '#' + item['id'] + '">';
				initialCardList += '        <span class="mdc-list-item__ripple"></span>';
				initialCardList += '        <span class="mdc-list-item__text mdc-list-item__start">' + item["name"] + '</span>';
				initialCardList += '      </li>';
            }

        });

        initialCardList += '    </ul>';

        $("#builder-activity-setting-initial-card-list").html(initialCardList);

        $(".builder-destination-item").hide();

        const options = document.querySelectorAll('.initial_dialog_card_selection_menu .mdc-list-item');

        for (let option of options) {
            option.addEventListener('click', (event) => {
                let prevent = event.currentTarget.classList.contains('prevent-menu-close');

                if (prevent) {
                    event.stopPropagation();

                    var id = event.currentTarget.id;

                    id = id.replace('builder-activity-setting-initial-card-list-sequence-', '')

                    $(".builder-destination-item").hide();

                    var icon = "#builder-activity-setting-initial-card-list-sequence-" + id + " .destination_disclosure_icon";

                    var isVisible = $(icon).html() == "arrow_drop_down";

                    $(".destination_disclosure_icon").text("arrow_right");

                    if (isVisible) {
                        $(icon).text("arrow_right");

                        $(".builder-activity-setting-initial-card-list-sequence-" + id + "-item").hide();
                    } else {
                        $("#builder-activity-setting-initial-card-list-sequence-" + id + " .destination_disclosure_icon").text("arrow_drop_down");

                        $(".builder-activity-setting-initial-card-list-sequence-" + id + "-item").show();
                    }
                }
            });
        }

        window.setTimeout(function() {
            if (initialCardSelect == null) {
                initialCardSelect = mdc.select.MDCSelect.attachTo(document.getElementById('builder-activity-setting-initial-card'));

                initialCardSelect.listen('MDCSelect:change', () => {
                    window.dialogBuilder.initialCard = initialCardSelect.value;

                    window.dialogBuilder.definition["initial-card"] = initialCardSelect.value

                    $("#action_save").show();
                });
            }

            initialCardSelect.value = window.dialogBuilder.definition["initial-card"];
            activityName.value = window.dialogBuilder.definition["name"];

            $("#builder-activity-setting-activity-name").on("change keyup paste", function() {
                window.dialogBuilder.definition["name"] = activityName.value;

                $("#action_save").show();
            });
        }, 50);

        $("#builder-activity-setting-add-keyword").click(function(eventObj) {
            eventObj.preventDefault();

            window.dialogBuilder.definition.interrupts.push({
                "pattern": "",
                "action": ""
            });

            refreshSettingsInterrupts();
        });
        
        console.log("SHOW ACTIVITY SETTINGS");
        
        $("#editor-view").hide();
        $("#settings-view").show();
    });

    var csrftoken = Cookies.get('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    var viewportHeight = $(window).height();

    var sourceTop = $("#builder_source_nodes").offset().top;

    var sourceHeight = $("#builder_source_nodes").height();

    var columnHeight = viewportHeight - sourceTop - sourceHeight - 24;

    $("#builder_source_nodes").height(columnHeight);
    $("#builder_current_node").height(columnHeight);
    $("#builder_next_nodes").height(columnHeight);
});