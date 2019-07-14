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
    
    function loadSequence(definition) {
        if (selectedSequence != null) {
            selectedSequence.removeChangeListener(onSequenceChanged);
        }

        selectedSequence = sequence.loadSequence(definition);
        
        $(".mdc-top-app-bar__title").html(selectedSequence.name());
        
        selectedSequence.addChangeListener(onSequenceChanged);
        
        selectedSequence.selectInitialNode();
    };
    
    $("#action_save").hide();
    
    $.getJSON(window.dialogBuilder.source, function(data) {
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

        var items = [];
        
        $.each(data, function(index, value) {
            items.push('<a class="mdc-list-item select_sequence" href="#" data-index="' + index +'">');
            items.push('<i class="material-icons mdc-list-item__graphic" aria-hidden="true">view_module</i>');
            items.push('<span class="mdc-list-item__text">' + value['name'] + '</span>');
            items.push('</a>');
        });
        
        $("#sequences_list").html(items.join(""));
        
        $(".select_sequence").off("click");
        $(".select_sequence").click(function(eventObj) {
            loadSequence(data[$(eventObj.target).data("index")]);
        });
        
        console.log('CARDS');
        console.log(window.dialogBuilder.cardMapping);
        
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
                
        window.dialogBuilder.addCardDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('add-card-dialog'));
        mdc.textField.MDCTextField.attachTo(document.getElementById('add-card-name'));
        mdc.select.MDCSelect.attachTo(document.getElementById('add-card-type'));

        loadSequence(data[0]);
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