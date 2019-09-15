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
    
    // console.log('MDC');
    // console.log(mdc);
    
    var selectedSequence = null;

    topAppBar.setScrollTarget(document.getElementById('main-content'));

    topAppBar.listen('MDCTopAppBar:nav', () => {
        drawer.open = !drawer.open;
    });
    
    function onSequenceChanged(changedId) {
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
    
    window.dialogBuilder.loadSequence = function(definition, initialId) {
        if (selectedSequence != null) {
            selectedSequence.removeChangeListener(onSequenceChanged);
        }

        selectedSequence = sequence.loadSequence(definition);
        
        $(".mdc-top-app-bar__title").html(selectedSequence.name());
        
        selectedSequence.addChangeListener(onSequenceChanged);
        
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
    }
    
    $.getJSON(window.dialogBuilder.source, function(data) {
        window.dialogBuilder.sequences = data;
        
        $("#action_save").off("click");

        $("#action_save").click(function(eventObj) {
            eventObj.preventDefault();
            if (window.dialogBuilder.update != undefined) {
                window.dialogBuilder.update(data, function() {
                    $("#action_save").hide();
                }, function(error) {
                    console.log(error);
                });
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

            $("#add-card-select-widget").append('<option value="' + key + '">' + name + '</option>');
        }
        
        window.dialogBuilder.reloadSequences();
        
        window.dialogBuilder.addCardDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('add-card-dialog'));
        mdc.textField.MDCTextField.attachTo(document.getElementById('add-card-name'));
        mdc.select.MDCSelect.attachTo(document.getElementById('add-card-type'));

        window.dialogBuilder.addSequenceDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('add-sequence-dialog'));
        mdc.textField.MDCTextField.attachTo(document.getElementById('add-sequence-name'));

        window.dialogBuilder.loadSequence(window.dialogBuilder.sequences[0], null);
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