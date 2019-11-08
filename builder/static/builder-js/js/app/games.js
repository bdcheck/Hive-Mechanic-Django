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

requirejs(["material", "cookie", "jquery"], function(mdc, Cookies) {
	console.log(mdc);
	
    const drawer = mdc.drawer.MDCDrawer.attachTo(document.querySelector('.mdc-drawer'));

    const topAppBar = mdc.topAppBar.MDCTopAppBar.attachTo(document.getElementById('app-bar'));
    
    var selectedSequence = null;

    topAppBar.setScrollTarget(document.getElementById('main-content'));

    topAppBar.listen('MDCTopAppBar:nav', () => {
        drawer.open = !drawer.open;
    });

	const baseDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('base-dialog'));

	const fabRipple = mdc.ripple.MDCRipple.attachTo(document.getElementById('action_add_game'));

	const addDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('dialog_add_game'));

	$("#action_add_game").click(function(eventObj) {
		$("#field_add_game").val("");
		addDialog.open();
	});

	addDialog.listen('MDCDialog:closed', function() {
		console.log("NEW GAME: " + $("#field_add_game").val());
		
		var name = $("#field_add_game").val();
		
		$.post('/builder/add-game.json', { 'name': name}, function(response) {
			console.log("RESPONSE");
			
			if (response['success']) {
				$("#dialog-title").html("Success");
			} else {
				$("#dialog-title").html("Failure");
			}
			
			$("#dialog-content").html(response['message']);

			console.log(response);

			baseDialog.listen('MDCDialog:closed', function() {
				if (response['success']) {
					if (response['redirect'] != undefined) {
						location.href = response['redirect'];
					}
				}
			});
			
			baseDialog.open();
		});
	});

	const gameName = mdc.textField.MDCTextField.attachTo(document.getElementById('textfield_add_game'));
    
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
    
    drawer.open = true;

	const dataTable = mdc.dataTable.MDCDataTable.attachTo(document.getElementById('table_games'));
});