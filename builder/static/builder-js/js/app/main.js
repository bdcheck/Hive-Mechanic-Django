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

requirejs(["material", "app/sequence", "cookie", "cards/node", "jquery"], function (mdc, sequence, Cookies, Node) {
    let self = this;

    let dialogIsDirty = false;

    const drawer = mdc.drawer.MDCDrawer.attachTo(document.querySelector('.mdc-drawer'));

    const topAppBar = mdc.topAppBar.MDCTopAppBar.attachTo(document.getElementById('app-bar'));

    const warningDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('builder-outstanding-issues-dialog'));
    window.dialogBuilder.selectCardsDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('builder-select-card-dialog'));

    window.dialogBuilder.restartGameDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('builder-reset-game-dialog'));

    window.dialogBuilder.gameVariablesDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('builder-game-variables-dialog'));

    window.dialogBuilder.restartGameDialog.listen('MDCDialog:closed', (result) => {
        console.log("ACTION: ");
        console.log(result);
    });

    window.dialogBuilder.viewStructureDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('preview-dialog'))

    $('#action_view_structure').click(function (eventObj) {
      eventObj.preventDefault()

      $('#preview-dialog-canvas').height(parseInt($(window).height() * 0.9))
      $('#preview-dialog-canvas').width(parseInt($(window).width() * 0.9))

      $('#preview-dialog-content').height($('#preview-dialog-canvas').height())
      $('#preview-dialog-content').css('overflow', 'hidden')

      window.dialogBuilder.viewStructureDialog.open()

      window.setTimeout(function () {
        $('#preview-dialog-canvas').attr('src', window.dialogBuilder.visualization)
      }, 100)
    })

	mdc.tooltip.MDCTooltip.attachTo(document.getElementById('action_view_structure_tip'))
	mdc.tooltip.MDCTooltip.attachTo(document.getElementById('action_reset_activity_tip'))
	mdc.tooltip.MDCTooltip.attachTo(document.getElementById('action_list_variables_tip'))
	mdc.tooltip.MDCTooltip.attachTo(document.getElementById('action_select_card_tip'))
	mdc.tooltip.MDCTooltip.attachTo(document.getElementById('action_save_tip'))

	mdc.tooltip.MDCTooltip.attachTo(document.getElementById('action_toggle_mode'))
    
    const activityName = mdc.textField.MDCTextField.attachTo(document.getElementById('builder-activity-setting-activity-name'));
    const activityIdentifier = mdc.textField.MDCTextField.attachTo(document.getElementById('builder-activity-setting-activity-identifier'));

    var initialCardSelect = null;
    var voiceCardSelect = null;

    var selectedSequence = null;

    topAppBar.setScrollTarget(document.getElementById('main-content'));

    topAppBar.listen('MDCTopAppBar:nav', () => {
        drawer.open = !drawer.open;
    });

    function onSequenceChanged(changedId) {
        $("#action_save").text("save");

        if (window.dialogBuilder.definition.sequences != undefined) {
            var issues = [];

            for (var i = 0; i < window.dialogBuilder.definition.sequences.length; i++) {

                var loadedSequence = sequence.loadSequence(window.dialogBuilder.definition.sequences[i]);

                var sequenceIssues = loadedSequence.issues();

                issues = issues.concat(sequenceIssues);
            }

            $(".outstanding-issue-item").remove();
            $(".outstanding-issue-item-divider").remove();

            if (issues.length > 0) {
                for (var i = 0; i < issues.length; i++) {
                    var issue = issues[i];

                    var item = '<li role="separator" class="mdc-list-divider outstanding-issue-item-divider"></li>';
                    item += '<li class="mdc-list-item mdc-list-item--with-two-lines prevent-menu-close outstanding-issue-item" id="builder-outstanding-issues-dialog-' + issue[2] + '">';
                    item += '  <span class="mdc-list-item__ripple"></span>';
                    item += '  <span class="mdc-list-item__content">';
                    item += '    <span class="mdc-list-item__primary-text">' + issue[0] + '</span>';
                    item += '    <span class="mdc-list-item__secondary-text">' + issue[3] + '</span>';
                    item += '  </span>';
                    item += '</li>';

                    $(item).insertBefore("#builder-outstanding-issues-dialog-save-divider");
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
    }

    function slugify(text) {
        return text.toString().toLowerCase()
            .replace(/\s+/g, '-')           // Replace spaces with -
            .replace(/[^\w\-]+/g, '')       // Remove all non-word chars
            .replace(/\-\-+/g, '-')         // Replace multiple - with single -
            .replace(/^-+/, '')             // Trim - from start of text
            .replace(/-+$/, '');            // Trim - from end of text
    }

    window.dialogBuilder.removeSequence = function (sequenceDefinition) {
        window.dialogBuilder.definition.sequencesdefinition.sequences = window.dialogBuilder.definition.sequences.filter(function (value) {
            return value != sequenceDefinition;
        });

        window.dialogBuilder.reloadSequences();

        window.dialogBuilder.loadSequence(window.dialogBuilder.definition.sequences[0], null);

        dialogIsDirty = true;
    }

    function cleanDefinition(definition) {
        if (definition == null) {
            return null;
        } else if (Array.isArray(definition)) {
            var cleanArray = [];

            $.each(definition, function (index, item) {
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

    window.dialogBuilder.loadSequence = function (definition, initialId) {
        if (selectedSequence != null) {
            selectedSequence.removeChangeListener(onSequenceChanged);
        }

        selectedSequence = sequence.loadSequence(definition);

        $(".mdc-top-app-bar__title").html(selectedSequence.name());

        selectedSequence.addChangeListener(onSequenceChanged);

        $("#action_edit_sequence").off("click");

        $("#action_edit_sequence").click(function (eventObj) {
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

                        dialogIsDirty = true;

                        window.dialogBuilder.editSequenceDialog.unlisten('MDCDialog:closed', this);
                    }
                }
            };

            window.dialogBuilder.editSequenceDialog.listen('MDCDialog:closed', editListener);

            window.dialogBuilder.editSequenceDialog.open()
        });

        $("#action_remove_sequence").click(function (eventObj) {
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

        return selectedSequence;
    };

    $("#action_save").show();

    window.dialogBuilder.reloadSequences = function () {
        var items = [];

        $.each(window.dialogBuilder.definition.sequences, function (index, value) {
            items.push('<li class="mdc-list-item mdc-list-item--with-one-line select_sequence" tabindex="' + index + '" data-index="' + index + '" style="padding-right: 0; align-items: center;">');
            items.push('  <span class="mdc-list-item__start material-icons" aria-hidden="true">view_module</span>');
            items.push('  <span class="mdc-list-item__text mdc-list-item__end" style="margin-left: 16px; flex-grow: 100;">' + value["name"] + '</span>'); //  mdc-list-item__end mdc-menu-surface--anchor
            items.push('  <span class="mdc-menu-surface--anchor">');
            items.push('    <button class="sequence-menu-open mdc-icon-button material-icons" data-index="' + index + '" tabindex="-1">');
            items.push('      more_vert');
            items.push('    </button>');
            items.push('  </span>');
            items.push('</li>')
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
        items.push('<span class="mdc-list-item__text mdc-list-item__end" style="margin-left: 16px;">Return to Dashboard</span>');
        items.push('</li>');

        $("#sequences_list").html(items.join(""));

        const sequencesList = mdc.list.MDCList.attachTo(document.getElementById('sequences_list'));

        $('button.sequence-menu-open').off();

        var selectedSequenceOption = -1;

        let menuListener = function (event) {
            var data = $(event.detail.item).data();
        }

        $('button.sequence-menu-open').on('click', (event) => {
            event.preventDefault();
            event.stopPropagation()

            const menu = mdc.menu.MDCMenu.attachTo(document.getElementById('sequence_menu'));
            menu.setAnchorElement(event.currentTarget.parentElement);
            menu.setFixedPosition(true);

            let rowData = $(event.currentTarget).data();

            selectedSequenceOption = rowData['index'];

            menu.items.forEach((item) => {
                item.setAttribute("data-index",selectedSequenceOption)
            });

            menu.unlisten("MDCMenu:selected", menuListener)

            menu.listen("MDCMenu:selected", menuListener);
            menu.open = (menu.open == false);
        });

        $(".down-sequence").off('click');
        $(".down-sequence").on('click', (event) => {
            event.preventDefault();
            let target = event.currentTarget;

            let index = parseInt(target.getAttribute('data-index'));

            let seq = window.dialogBuilder.definition.sequences
            let last = seq.length - 1
            let next = index + 1
            if (index < last) {
                temp = seq[next]
                seq[next] = seq[index]
                seq[index] = temp
                window.dialogBuilder.definition.sequences = seq
                window.dialogBuilder.reloadSequences()

                dialogIsDirty = true;
            }
        });
        $(".up-sequence").off('click');
        $(".up-sequence").on('click', (event) => {
            event.preventDefault();
            let target = event.currentTarget;
            let index = parseInt(target.getAttribute('data-index'));

            seq = window.dialogBuilder.definition.sequences
            last = seq.length - 1
            prev = index - 1
            if (index > 0) {
                temp = seq[prev]
                seq[prev] = seq[index]
                seq[index] = temp
                window.dialogBuilder.definition.sequences = seq
                window.dialogBuilder.reloadSequences()

                dialogIsDirty = true;
            }
        });

        $(".rename-sequence").off('click');
        $(".rename-sequence").on('click', (event) => {
            event.preventDefault();
            let target = event.currentTarget;
            let index = parseInt(target.getAttribute('data-index'));
            let seq = window.dialogBuilder.definition.sequences;
            let menu_sequence = seq[index];
            $("#edit-sequence-name-value").val(menu_sequence.name);

            window.dialogBuilder.editSequenceDialog.unlisten('MDCDialog:closed', editListener);

            editListener = {
                handleEvent: function (event) {
                    if (event.detail.action == "update_sequence") {
                        var name = $("#edit-sequence-name-value").val();
                        seq[index].name = name
                        window.dialogBuilder.definition.sequences = seq;
                        //$(".mdc-top-app-bar__title").html(name);

                        window.dialogBuilder.reloadSequences();

                        window.dialogBuilder.editSequenceDialog.unlisten('MDCDialog:closed', this);

                        dialogIsDirty = true;
                    }
                }
            };

            window.dialogBuilder.editSequenceDialog.listen('MDCDialog:closed', editListener);

            window.dialogBuilder.editSequenceDialog.open()

        });

        $(".delete-sequence").off('click');
        $(".delete-sequence").click(function (event) {
            let target = event.currentTarget;
            let index = parseInt(target.getAttribute('data-index'));
            let seq = window.dialogBuilder.definition.sequences;
            let menu_sequence = seq[index];

            $("#remove-sequence-name-value").html(menu_sequence['name']);

            window.dialogBuilder.removeSequenceDialog.unlisten('MDCDialog:closed', removeListener);

            removeListener = {
                handleEvent: function (event) {
                    if (event.detail.action == "remove_sequence") {
                        seq.splice(index,1)
                        window.dialogBuilder.definition.sequences = seq;
                        window.dialogBuilder.reloadSequences();
                        window.dialogBuilder.loadSequence(seq[0],null)
                        window.dialogBuilder.editSequenceDialog.unlisten('MDCDialog:closed', this);
                    }
                }
            };

            window.dialogBuilder.removeSequenceDialog.listen('MDCDialog:closed', removeListener);

            window.dialogBuilder.removeSequenceDialog.open()
        });

        $(".select_sequence").off("click");
        $(".select_sequence").click(function (eventObj) {
            $("#settings-view").hide();
            $("#editor-view").show();
            let seq = window.dialogBuilder.definition.sequences;
            let target = eventObj.currentTarget;
            let index = parseInt(target.getAttribute('data-index'));
            window.dialogBuilder.loadSequence(seq[index], null);
            //window.dialogBuilder.loadSequence(window.dialogBuilder.definition.sequences[$(eventObj.target).data("index")], null);
        });

        $(".add_sequence").off("click");
        $(".add_sequence").click(function (eventObj) {
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
        $(".go_home").click(function (eventObj) {
            location.href = '/builder/';
        });

        var allCardSelectContent = '';

        $.each(window.dialogBuilder.definition.sequences, function (index, value) {
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

        $("#select-all-cards-items .mdc-list-item").off("click");

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

                window.dialogBuilder.setHelpCardStatus();
            });
        }
    }

    window.dialogBuilder.loadNodeById = function (cardId) {
        var me = this;

        for (var i = 0; i < window.dialogBuilder.definition.sequences.length; i++) {
            var sequence = window.dialogBuilder.definition.sequences[i];

            if (sequence["id"] != cardId) {
                for (var j = 0; j < sequence["items"].length; j++) {
                    var item = sequence["items"][j];

                    if (item["id"] == cardId) {
                        var loadedSequence = window.dialogBuilder.loadSequence(sequence, item['id']);

                        $('#' + item['id'] + '-advanced-dialog').remove();

                        var node = Node.createCard(item, loadedSequence);

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

    $.getJSON(window.dialogBuilder.source, function (data) {
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

        $("#action_save").click(function (eventObj) {
	        $("#action_save").text("pending");
        
            eventObj.preventDefault();

            if (window.dialogBuilder.update != undefined) {
                if ($("#action_save").text() == "warning") {
                    warningDialog.open();
                } else {
                    var clean = cleanDefinition(window.dialogBuilder.definition);

                    window.dialogBuilder.update(clean, function () {
                    	window.setTimeout(function() {
	                        $("#action_save").text('save');
	                    }, 1000);

                        dialogIsDirty = false;
                    }, function (error) {
                        console.log(error);
                    });
                }
            }
        });

        $("#action_select_card").off("click");

        $("#action_select_card").click(function (eventObj) {
            eventObj.preventDefault();

            window.dialogBuilder.selectCardsDialog.open();
        });

        $("#action_reset_activity").off("click");

        $("#action_reset_activity").click(function (eventObj) {
            eventObj.preventDefault();

            window.dialogBuilder.restartGameDialog.open();
        });

        var keys = Object.keys(window.dialogBuilder.cardMapping);

        keys.sort(function (one, two) {
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

		$.each(window.dialogBuilder.categories, function(index, category) {
			if (category.cards.length > 0) {
				let cardItem = '';
			
				let groupSpan = 12
				let itemSpan = 3
			
				if (category.cards.length <= 2) {
					groupSpan = 6
					itemSpan = 6
				}

				cardItem += '    <div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-' + groupSpan + '">'
				cardItem += '      <strong>' + category.name + '</strong>'
				cardItem += '      <div class="mdc-layout-grid__inner" style="grid-gap: 0px;">'

				$.each(category.cards, function(card_index, card_identifier) {
					var nodeClass = window.dialogBuilder.cardMapping[card_identifier];

					var name = nodeClass.cardName();

					if (name == Node.cardName()) {
						name = key;
					}

					cardItem += '  <div class="mdc-form-field mdc-layout-grid__cell mdc-layout-grid__cell--span-' + itemSpan + '">'
					cardItem += '    <div class="mdc-radio">';
					cardItem += '      <input class="mdc-radio__native-control" type="radio" id="add-card-option-' + index + '-' + card_index + '" name="add-card-options" value="' + card_identifier + '">';
					cardItem += '      <div class="mdc-radio__background">';
					cardItem += '        <div class="mdc-radio__outer-circle"></div>';
					cardItem += '        <div class="mdc-radio__inner-circle"></div>';
					cardItem += '      </div>';
					cardItem += '    </div>';
					cardItem += '    <label for="add-card-option-' + index + '-' + card_index + '">' + name + '</label>';
					cardItem += '  </div>';
				});


				cardItem += '      </div>'
				cardItem += '    </div>'

				$("#add-card-select-widget").append(cardItem);

			}
		});        

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

        window.dialogBuilder.setHelpCardStatus = function() {
             if (!window.dialogBuilder.helpToggle.checked) {
                $('#hive-help-switch-label').text("Basic: ")
                $(".hive_mechanic_help_filler").hide()
                $(".hive_mechanic_help").show()
            } else {
                $('#hive-help-switch-label').text("Advanced: ")
                $(".hive_mechanic_help").hide()
                $(".hive_mechanic_help_filler").show()
            }
        }
        //advanced mode on turns off help
        $('#hive-help-switch-toggle').change(function () {
            window.dialogBuilder.setHelpCardStatus()
        });
        $('.hive_mechanic_help_filler').hide();


        $(".hive_mechanic_help").show();
        //load help after start
        $(document).ready(function () {
            $('.hive_mechanic_help_filler').hide();
            $(".hive_mechanic_help").show();
        });

// CK ^^^ Why document.ready?

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

            window.dialogBuilder.update(clean, function () {
                warningDialog.close();
            }, function (error) {
                console.log(error);
            });

            return;
        });

        window.setTimeout(window.dialogBuilder.reloadSequences, 500);
    });

    $("#action_open_settings").off("click");

    var updatePattern = function (action, operation, pattern) {
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

    var updateViews = function (pattern, operationField, patternField) {
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

    var chooseDestinationMenu = function (identifier) {
        var me = this;
        var body = '';

        body += '    <ul class="mdc-list mdc-dialog__content dialog_card_selection_menu" role="menu" aria-hidden="true" aria-orientation="vertical" tabindex="-1" style="padding: 0px;">';

        $.each(window.dialogBuilder.definition.sequences, function (index, value) {
            body += '<li class="mdc-list-divider" role="separator"></li>';
            body += '<li class="mdc-list-item mdc-list-item--with-one-line prevent-menu-close" role="menuitem" id="' + identifier + '_destination_sequence_' + value['id'] + '">';
            body += '  <span class="mdc-list-item__ripple"></span>';
            body += '  <span class="mdc-list-item__text mdc-list-item__start">' + value['name'] + '</span>';
            body += '  <span class="mdc-list-item__end mdc-layout-grid--align-right material-icons destination_disclosure_icon">arrow_right</span>';
            body += '</li>';

            var items = value['items'];

            for (var i = 0; i < items.length; i++) {
                var item = items[i];

                body += '<li class="mdc-list-item mdc-list-item--with-one-line ' + identifier + '_destination_sequence_' + value['id'] + '_item builder-destination-item" role="menuitem" id="' + identifier + '_destination_sequence_' + item['id'] + '" data-node-id="' + value['id'] + '#' + item['id'] + '">';
                body += '  <span class="mdc-list-item__ripple"></span>';
                body += '  <span class="mdc-list-item__text mdc-list-item__start">' + item["name"] + '</span>';
                body += '</li>';
            }
        });

        body += '    </ul>';

        return body;
    };

    var initializeDestinationMenu = function (identifier, onSelect) {
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
            interruptBody += '          <span id="outlined-select-label" class="mdc-floating-label">Incoming Response&#8230;</span>';
            interruptBody += '        </span>';
            interruptBody += '        <span class="mdc-notched-outline__trailing"></span>';
            interruptBody += '      </span>';
            interruptBody += '      <span class="mdc-select__selected-text-container">';
            interruptBody += '        <span class="mdc-select__selected-text"></span>';
            interruptBody += '      </span>';
            interruptBody += '      <span class="mdc-select__dropdown-icon">';
            interruptBody += '        <svg';
            interruptBody += '            class="mdc-select__dropdown-icon-graphic"';
            interruptBody += '            viewBox="7 10 10 5" focusable="false">';
            interruptBody += '          <polygon';
            interruptBody += '              class="mdc-select__dropdown-icon-inactive"';
            interruptBody += '              stroke="none"';
            interruptBody += '              fill-rule="evenodd"';
            interruptBody += '              points="7 10 12 15 17 10">';
            interruptBody += '          </polygon>';
            interruptBody += '          <polygon';
            interruptBody += '              class="mdc-select__dropdown-icon-active"';
            interruptBody += '              stroke="none"';
            interruptBody += '              fill-rule="evenodd"';
            interruptBody += '              points="7 15 12 10 17 15">';
            interruptBody += '          </polygon>';
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

            interruptBody += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-3 mdc-layout-grid__cell--align-middle">';
            interruptBody += '  <button class="mdc-icon-button" id="activity_interrupt_pattern_' + i + '_response_choose">';
            interruptBody += '    <i class="material-icons mdc-icon-button__icon" aria-hidden="true">link</i>';
            interruptBody += '  </button>';

            if (interrupt["action"] != undefined && interrupt["action"] != "") {
                interruptBody += '  <button class="mdc-icon-button" id="activity_interrupt_pattern_' + i + '_response_click">';
                interruptBody += '    <i class="material-icons mdc-icon-button__icon" aria-hidden="true">keyboard_arrow_right</i>';
                interruptBody += '  </button>';
            }

            interruptBody += '</div>';

            $("#activity_settings_interrupts").append(interruptBody);

            const patternField = mdc.textField.MDCTextField.attachTo(document.getElementById('activity_interrupt_pattern_' + i + '_response'));
            const operationSelect = mdc.select.MDCSelect.attachTo(document.getElementById('activity_interrupt_pattern_' + i));

            updateViews(interrupt["pattern"], operationSelect, patternField);

            operationSelect.listen('MDCSelect:change', () => {
                updatePattern(interrupt, operationSelect.value, patternField.value);

                dialogIsDirty = true;
            });

            $("#" + identifier).on("change keyup paste", function() {
                updatePattern(interrupt, operationSelect.value, patternField.value);

                dialogIsDirty = true;
            });

            $('#activity_interrupt_pattern_' + i + '_response_choose').on("click", function() {
                const chooseDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('select-interrupt-dialog'));

                $("#select-interrupt-dialog-content").html(chooseDestinationMenu("select-interrupt"));

                initializeDestinationMenu("select-interrupt", function(nodeId) {
                    interrupt["action"] = nodeId;

                    chooseDialog.close();

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

    var refreshSettingsVariables = function() {
        $("#activity_variables").empty();

        if (window.dialogBuilder.definition['variables'] == undefined) {
            window.dialogBuilder.definition['variables'] = [];
        }

        for (var i = 0; i < window.dialogBuilder.definition['variables'].length; i++) {
            const variable = window.dialogBuilder.definition['variables'][i];
            const identifier = 'activity_variable_' + i + '_response_value';

            var itemHtml = '';

            itemHtml += '<div class="mdc-select mdc-select--outlined mdc-layout-grid__cell mdc-layout-grid__cell--span-4" id="activity_variable_' + i + '_scope" style="width: 100%" class="mdc-layout-grid__cell">';
            itemHtml += '   <div class="mdc-select__anchor" style="width: 100%;">';
            itemHtml += '       <span class="mdc-notched-outline">';
            itemHtml += '           <span class="mdc-notched-outline__leading"></span>';
            itemHtml += '           <span class="mdc-notched-outline__notch">';
            itemHtml += '               <span id="outlined-select-label" class="mdc-floating-label">Scope</span>';
            itemHtml += '           </span>';
            itemHtml += '           <span class="mdc-notched-outline__trailing"></span>';
            itemHtml += '       </span>';
            itemHtml += '       <span class="mdc-select__selected-text-container">';
            itemHtml += '           <span id="demo-selected-text" class="mdc-select__selected-text"></span>';
            itemHtml += '       </span>';
            itemHtml += '       <span class="mdc-select__dropdown-icon">';
            itemHtml += '           <svg class="mdc-select__dropdown-icon-graphic" viewBox="7 10 10 5" focusable="false">';
            itemHtml += '               <polygon class="mdc-select__dropdown-icon-inactive" stroke="none" fill-rule="evenodd" points="7 10 12 15 17 10"></polygon>';
            itemHtml += '               <polygon class="mdc-select__dropdown-icon-active" stroke="none" fill-rule="evenodd" points="7 15 12 10 17 15"></polygon>';
            itemHtml += '           </svg>';
            itemHtml += '       </span>';
            itemHtml += '   </div>';
            itemHtml += '   <div class="mdc-select__menu mdc-menu mdc-menu-surface" role="listbox">';
            itemHtml += '     <ul class="mdc-list mdc-dialog__content" role="menu" aria-hidden="true" aria-orientation="vertical" tabindex="-1">';
            itemHtml += '      <li class="mdc-list-item mdc-list-item--with-one-line prevent-menu-close" role="menuitem" data-value="session">';
            itemHtml += '        <span class="mdc-list-item__ripple"></span>';
            itemHtml += '        <span class="mdc-list-item__text mdc-list-item__start">Session</span>';
            itemHtml += '      </li>';
            itemHtml += '      <li class="mdc-list-item mdc-list-item--with-one-line prevent-menu-close" role="menuitem" data-value="game">';
            itemHtml += '        <span class="mdc-list-item__ripple"></span>';
            itemHtml += '        <span class="mdc-list-item__text mdc-list-item__start">Game</span>';
            itemHtml += '      </li>';
            itemHtml += '     </ul>';
            itemHtml += '  </div>';
            itemHtml += '</div>';

            itemHtml += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-4 mdc-layout-grid__cell--align-top">';
            itemHtml += '  <div class="mdc-text-field mdc-text-field--outlined" id="activity_variable_' + i + '_name">';
            itemHtml += '    <input type="text" class="mdc-text-field__input" id="activity_variable_' + i + '_name_value" value="' + variable['name'] + '">';
            itemHtml += '    <div class="mdc-notched-outline">';
            itemHtml += '      <div class="mdc-notched-outline__leading"></div>';
            itemHtml += '      <div class="mdc-notched-outline__notch">';
            itemHtml += '        <label for="activity_variable_' + i + '_name_value" class="mdc-floating-label">Name</label>';
            itemHtml += '      </div>';
            itemHtml += '      <div class="mdc-notched-outline__trailing"></div>';
            itemHtml += '    </div>';
            itemHtml += '  </div>';
            itemHtml += '</div>';

            itemHtml += '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-4 mdc-layout-grid__cell--align-top">';
            itemHtml += '  <div class="mdc-text-field mdc-text-field--outlined" id="activity_variable_' + i + '_value">';
            itemHtml += '    <input type="text" class="mdc-text-field__input" id="activity_variable_' + i + '_value_value" value="' + variable['value'] + '">';
            itemHtml += '    <div class="mdc-notched-outline">';
            itemHtml += '      <div class="mdc-notched-outline__leading"></div>';
            itemHtml += '      <div class="mdc-notched-outline__notch">';
            itemHtml += '        <label for="activity_variable_' + i + '_value_value" class="mdc-floating-label">Value</label>';
            itemHtml += '      </div>';
            itemHtml += '      <div class="mdc-notched-outline__trailing"></div>';
            itemHtml += '    </div>';
            itemHtml += '  </div>';
            itemHtml += '</div>';

            $("#activity_variables").append(itemHtml);

            let itemIndex = i;

            const nameField = mdc.textField.MDCTextField.attachTo(document.getElementById('activity_variable_' + i + '_name'));
            const nameFieldIdentifier = 'activity_variable_' + i + '_name_value'

            $("#" + nameFieldIdentifier).on("change keyup paste", function() {
                if (variable['name'] == "" && nameField.value == "") {
                    window.dialogBuilder.definition['session-variables'].splice(itemIndex, 1);
                    refreshSettingsSessionVariables();
                } else {
                    variable['name'] = nameField.value;
                }

                dialogIsDirty = true;
            });

            const valueField = mdc.textField.MDCTextField.attachTo(document.getElementById('activity_variable_' + i + '_value'));
            const valueFieldIdentifier = 'activity_variable_' + i + '_value_value'

            $("#" + valueFieldIdentifier).on("change keyup paste", function() {
                variable['value'] = valueField.value;

                dialogIsDirty = true;
            });

            const valueScope = mdc.select.MDCSelect.attachTo(document.getElementById('activity_variable_' + i + '_scope'));

            valueScope.value = variable['scope'];

            valueScope.listen('MDCSelect:change', () => {
                variable['scope'] = valueScope.value;

                dialogIsDirty = true;
            });
        }
    };

    $("#action_open_settings").click(function(eventObj) {
        eventObj.preventDefault();

        refreshSettingsInterrupts();
        refreshSettingsVariables();

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

        $("#builder-activity-setting-voice-card-list").html(initialCardList);

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

        window.setTimeout(function () {
            if (initialCardSelect == null) {
                initialCardSelect = mdc.select.MDCSelect.attachTo(document.getElementById('builder-activity-setting-initial-card'));

                initialCardSelect.listen('MDCSelect:change', () => {
                    window.dialogBuilder.initialCard = initialCardSelect.value;

                    window.dialogBuilder.definition["initial-card"] = initialCardSelect.value

                    dialogIsDirty = true;
                });
            }

            if (voiceCardSelect == null) {
                voiceCardSelect = mdc.select.MDCSelect.attachTo(document.getElementById('builder-activity-setting-voice-card'));

                voiceCardSelect.listen('MDCSelect:change', () => {
                    window.dialogBuilder.voiceCard = voiceCardSelect.value;

                    window.dialogBuilder.definition["incoming_call_interrupt"] = voiceCardSelect.value

                    dialogIsDirty = true;
                });
            }

            initialCardSelect.value = window.dialogBuilder.definition["initial-card"];
            voiceCardSelect.value = window.dialogBuilder.definition["incoming_call_interrupt"];

            activityName.value = window.dialogBuilder.definition["name"];

            $("#builder-activity-setting-activity-name").on("change keyup paste", function () {
                window.dialogBuilder.definition["name"] = activityName.value;

                dialogIsDirty = true;
            });

            if (window.dialogBuilder.definition["identifier"] != undefined) {
                activityIdentifier.value =window.dialogBuilder.definition["identifier"];
            }

            $("#builder-activity-setting-activity-identifier").on("change keyup paste", function() {
                window.dialogBuilder.definition["identifier"] = activityIdentifier.value;

                dialogIsDirty = true;
            });
        }, 100);

        $("#builder-activity-setting-add-keyword").click(function (eventObj) {
            eventObj.preventDefault();

            window.dialogBuilder.definition.interrupts.push({
                "pattern": "",
                "action": ""
            });

            refreshSettingsInterrupts();
        });

        $("#builder-activity-setting-add-variable").click(function(eventObj) {
            eventObj.preventDefault();

            if (window.dialogBuilder.definition['variables'] == undefined) {
                window.dialogBuilder.definition['variables'] = [];
            }

            window.dialogBuilder.definition['variables'].push({
                "name": "new-variable",
                "value": "new-value",
                "scope": "session",
            });

            dialogIsDirty = true;

            refreshSettingsVariables();
        });

        $("#editor-view").hide();
        $("#settings-view").show();
    });

    $('#activity_interrupt_pattern_voice_call_click').on("click", function() {
        window.dialogBuilder.loadNodeById(window.dialogBuilder.definition['incoming_call_interrupt'].split("#")[1]);

        $("#settings-view").hide();
        $("#editor-view").show();
    });

    $('#activity_interrupt_pattern_voice_call_choose').on("click", function() {
        const chooseDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('select-interrupt-dialog'));

        $("#select-interrupt-dialog-content").html(chooseDestinationMenu("select-interrupt"));

        initializeDestinationMenu("select-interrupt", function(nodeId) {
            window.dialogBuilder.definition['incoming_call_interrupt'] = nodeId;

            chooseDialog.close();

            refreshSettingsInterrupts();
        });

        chooseDialog.open();
    });

    var csrftoken = Cookies.get('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $("#icon_activity_click").click(function(event) {
        event.preventDefault();

        $("#icon_activity_file").click();
    });

    $("#icon_activity_file").change(function() {
        $("#icon_activity_form").submit();
    });

    $('#icon_activity_form').submit(function() { // catch the form's submit event
        var fileData = new FormData();
        fileData.append('activity_pk', $('input[name="activity_pk"]').val());

        fileData.append('icon_file', $('#icon_activity_file').get(0).files[0]);

        $.ajax({
            url: $(this).attr('action'),
            type: $(this).attr('method'),
            data: fileData,
            async: true,
            cache: false,
            processData: false,
            contentType: false,
            enctype: 'multipart/form-data',
            success: function(response){
                $("#icon_activity").attr("src", response["url"]);
            }
        });

        return false;
    });

    var viewportHeight = $(window).height();

    var sourceTop = $("#builder_source_nodes").offset().top;

    var sourceHeight = $("#builder_source_nodes").height();

    var columnHeight = viewportHeight - sourceTop - sourceHeight - 24;

    $("#builder_source_nodes").height(columnHeight);
    $("#builder_current_node").height(columnHeight);
    $("#builder_next_nodes").height(columnHeight);

    window.addEventListener('beforeunload', function(e) {
        e = e || window.event;

        e.preventDefault();

        if (dialogIsDirty) {
            e.preventDefault();

            if (e) {
                e.returnValue = 'You have unsaved changes. Are you sure you want to exit now?';
            }

            return e.returnValue;
        }

        delete e['returnValue'];
    });
    
	$("#action_list_variables").off("click");

	$("#action_list_variables").click(function (eventObj) {
		eventObj.preventDefault();
		
		$("#builder-game-variables-dialog-content").html('<div class="mdc-typography--body1 mdc-layout-grid__cell mdc-layout-grid__cell--span-12 mdc-layout-grid__cell--align-top"><em>Fetching variables&#8230;</em></div>');

		window.dialogBuilder.gameVariablesDialog.open();
		
		window.dialogBuilder.fetchVariables(function(variables) {
			$("#builder-game-variables-dialog-content").html('');

            $.each(variables, function (index, item) {
				$("#builder-game-variables-dialog-content").append('<div class="mdc-typography--body1 mdc-layout-grid__cell mdc-layout-grid__cell--span-6 mdc-layout-grid__cell--align-top">' + item['name'] + '</div>');
				$("#builder-game-variables-dialog-content").append('<div class="mdc-typography--body1 mdc-layout-grid__cell mdc-layout-grid__cell--span-6 mdc-layout-grid__cell--align-top">= <strong>' + item['value'] + '</strong></div>');
            });
		
		
		});
	});
});