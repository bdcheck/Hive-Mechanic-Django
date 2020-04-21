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
        material: "/static/builder-js/vendor/material-components-web.min",
        jquery: "/static/builder-js/vendor/jquery-3.4.0.min",
        cookie: "/static/builder-js/vendor/js.cookie"
    }
});

requirejs(["material", "app/sequence", "cookie", "cards/node", "jquery"], function(mdc, sequence, Cookies, Node) {
    const drawer = mdc.drawer.MDCDrawer.attachTo(document.querySelector('.mdc-drawer'));

    const topAppBar = mdc.topAppBar.MDCTopAppBar.attachTo(document.getElementById('app-bar'));
    
    const warningDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('builder-outstanding-issues-dialog'));

    // console.log('MDC');
    // console.log(mdc);
    
    var selectedSequence = null;

    topAppBar.setScrollTarget(document.getElementById('main-content'));

    topAppBar.listen('MDCTopAppBar:nav', () => {
        drawer.open = !drawer.open;
    });
    
    function onSequenceChanged(changedId) {
        $("#action_save").text("save");
        
        if (window.dialogBuilder.sequences != undefined) {
            var issues = [];

			$(".outstanding-issue-item").remove();
            
            for (var i = 0; i < window.dialogBuilder.sequences.length; i++) {
                var loadedSequence = sequence.loadSequence(window.dialogBuilder.sequences[i]);
                
                issues = issues.concat(loadedSequence.issues());
            }
            
            console.log("ISSUES: " + JSON.stringify(issues, null, 2));
            
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

						for (var i = 0; i < window.dialogBuilder.sequences.length; i++) {
							var sequence = window.dialogBuilder.sequences[i];
				
							for (var j = 0; j < sequence["items"].length; j++) {
								var item = sequence["items"][j];

								if (item["id"] == id) {
									console.log(sequence);
	
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
        window.dialogBuilder.sequences = window.dialogBuilder.sequences.filter(function(value) {
            return value != sequenceDefinition;
        });
        
        window.dialogBuilder.reloadSequences();
        
        window.dialogBuilder.loadSequence(window.dialogBuilder.sequences[0], null);

        $("#action_save").show();
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
        
        $.each(window.dialogBuilder.sequences, function(index, value) {
            items.push('<a class="mdc-list-item select_sequence" href="#" data-index="' + index +'">');
            items.push('<i class="material-icons mdc-list-item__graphic" aria-hidden="true">view_module</i>');
            items.push('<span class="mdc-list-item__text">' + value['name'] + '</span>');
            items.push('</a>');
        });

        items.push('<a class="mdc-list-item add_sequence" href="#" style="margin-top: 2em;">');
        items.push('<i class="material-icons mdc-list-item__graphic" aria-hidden="true">add_box</i>');
        items.push('<span class="mdc-list-item__text">Add Sequence</span>');
        items.push('</a>');

        items.push('<div role="separator" class="mdc-list-divider"></div>');

        items.push('<a class="mdc-list-item go_home" href="#" style="margin-top: 2em;">');
        items.push('<i class="material-icons mdc-list-item__graphic" aria-hidden="true">home</i>');
        items.push('<span class="mdc-list-item__text">Return to Home</span>');
        items.push('</a>');
        
        $("#sequences_list").html(items.join(""));
        
        $(".select_sequence").off("click");
        $(".select_sequence").click(function(eventObj) {
            window.dialogBuilder.loadSequence(window.dialogBuilder.sequences[$(eventObj.target).data("index")], null);
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
                        
                        window.dialogBuilder.sequences.push(sequence);
                        
                        window.dialogBuilder.reloadSequences();
                        
                        var last = window.dialogBuilder.sequences.length - 1;
                        
                        window.dialogBuilder.loadSequence(window.dialogBuilder.sequences[last], null);
                    
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

		var allCardSelectContent =  '<li class="mdc-list-item mdc-list-item--selected">';
		allCardSelectContent +=     '  <span class="mdc-list-item__text">Please Select a Card&#8230;</span>';
		allCardSelectContent +=     '</li>';

		$.each(window.dialogBuilder.sequences, function(index, value) {
			allCardSelectContent += '<li class="mdc-list-divider" role="separator"></li>';
			allCardSelectContent += '<li class="mdc-list-item prevent-menu-close" role="menuitem" id="all_cards_destination_sequence_' + value['id'] + '">';
			allCardSelectContent += '  <span class="mdc-list-item__text">' + value['name'] + '</span>';
			allCardSelectContent += '  <span class="mdc-list-item__meta material-icons destination_disclosure_icon">arrow_right</span>';
			allCardSelectContent += '</li>';

			var items = value['items'];

			for (var i = 0; i < items.length; i++) {
				var item = items[i];

				allCardSelectContent += '<li class="mdc-list-item all-cards-select-item all_cards_destination_sequence_' + value['id'] + '_item" role="menuitem" id="all_cards_destination_item_' + item['id'] + '" data-node-id="' + value['id'] + '#' + item['id'] + '">';
				allCardSelectContent += '  <span class="mdc-list-item__text">' + item["name"] + '</span>';
				allCardSelectContent += '</li>';
			}
		});

		$("#select-all-cards-items").html(allCardSelectContent);

		$(".all-cards-select-item").hide();

		$("#select-all-cards .mdc-list-item").off("click");

		const options = document.querySelectorAll('#select-all-cards .mdc-list-item');

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
					var nodeId = $(event.currentTarget).attr("data-node-id");

					var id = event.currentTarget.id;

					id = id.replace("all_cards_destination_item_", '');

					window.dialogBuilder.loadNodeById(id);
				}
			});
		}

		window.setTimeout(function() {
			window.dialogBuilder.allCardsSelect.selectedIndex = 0;
		}, 500);
	}

	window.dialogBuilder.loadNodeById = function(cardId) {
		var me = this;

		for (var i = 0; i < window.dialogBuilder.sequences.length; i++) {
			var sequence = window.dialogBuilder.sequences[i];

			if (sequence["id"] != cardId) {
				for (var j = 0; j < sequence["items"].length; j++) {
					var item = sequence["items"][j];

					if (item["id"] == cardId) {
						console.log(sequence);

						window.dialogBuilder.loadSequence(sequence, item['id']);

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
        window.dialogBuilder.sequences = data;
        
        $("#action_save").off("click");

        $("#action_save").click(function(eventObj) {
            eventObj.preventDefault();

            if (window.dialogBuilder.update != undefined) {
            	if ($("#action_save").text() == "warning") {
					warningDialog.open();
            	} else {
					window.dialogBuilder.update(data, function() {
						$("#action_save").hide();
					}, function(error) {
						console.log(error);
					});
				}
            }
        });
        
        var keys = Object.keys(window.dialogBuilder.cardMapping);
        
        for (var i = 0; i < keys.length; i++) {
            var key = keys[i];
            
            var nodeClass = window.dialogBuilder.cardMapping[key];
            
            var name = nodeClass.cardName();
            
            if (name == Node.cardName()) {
                name = key;
            }

            $("#add-card-select-widget").append('<li class="mdc-list-item" data-value="' + key + '">' + name + '</li>');
        }
        
        window.dialogBuilder.reloadSequences();

        window.dialogBuilder.allCardsSelect = mdc.select.MDCSelect.attachTo(document.getElementById('select-all-cards'));
        
        window.dialogBuilder.addCardDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('add-card-dialog'));
        mdc.textField.MDCTextField.attachTo(document.getElementById('add-card-name'));
        
        window.dialogBuilder.newCardSelect = mdc.select.MDCSelect.attachTo(document.getElementById('add-card-type'));

        window.dialogBuilder.addSequenceDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('add-sequence-dialog'));
        mdc.textField.MDCTextField.attachTo(document.getElementById('add-sequence-name'));

        window.dialogBuilder.editSequenceDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('edit-sequence-dialog'));
        mdc.textField.MDCTextField.attachTo(document.getElementById('edit-sequence-name'));

        window.dialogBuilder.removeSequenceDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('remove-sequence-dialog'));

        window.dialogBuilder.loadSequence(window.dialogBuilder.sequences[0], null);

		const warning = document.getElementById('builder-outstanding-issues-dialog-save');
		
		warning.addEventListener('click', (event) => {
			window.dialogBuilder.update(data, function() {
				$("#action_save").hide();

				console.log("SAVE WITH WARNINGS");

				warningDialog.close();

				console.log("CLOSE");
			}, function(error) {
				console.log(error);
			});
			
			return;
		});
        
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
});