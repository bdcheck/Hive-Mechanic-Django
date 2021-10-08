requirejs.config({
    shim: {
        jquery: {
            exports: "$"
        },
        cookie: {
            exports: "Cookies",
            deps: ["jquery"]
        },
        klayjs: {
            exports: "$klay"
        },
        dagre: {
            exports: "dagre"
        },
        "cytoscape-klay": {
            deps: ["klayjs"]
        },
        "cytoscape-dagre": {
            deps: ["dagre"]
        },
    },
    baseUrl: "/static/builder-js/js/app",
    paths: {
        app: '/static/builder-js/js/app',
        material: "/static/builder-js/vendor/material-components-web.min",
        jquery: "/static/builder-js/vendor/jquery-3.4.0.min",
        cookie: "/static/builder-js/vendor/js.cookie",
        cytoscape: "/static/builder-js/vendor/cytoscape-3.19.1.min",
        "cytoscape-klay": "/static/builder-js/vendor/cytoscape-klay",
        "cytoscape-dagre": "/static/builder-js/vendor/cytoscape-dagre",
        klayjs: '/static/builder-js/vendor/klay',
        dagre: '/static/builder-js/vendor/dagre.min'
    }
});

requirejs(["material", "cookie", "cytoscape", "cytoscape-dagre"], function(mdc, Cookies, cytoscape, cytoscape_dagre) {
    const drawer = mdc.drawer.MDCDrawer.attachTo(document.querySelector('.mdc-drawer'));

    const itemsList = mdc.list.MDCList.attachTo(document.getElementById('sequences_list'));

    itemsList.listen('MDCList:action', function(e) {
        const path = $(itemsList.listElements[e['detail']['index']]).attr("data-href");

        window.location = path;
    });

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
        eventObj.preventDefault();

        $("#field_add_game").val("");
        addDialog.open();
    });

    addDialog.listen('MDCDialog:closed', function() {
        var name = $("#field_add_game").val();
        
        $.post('/builder/add-game.json', { 'name': name}, function(response) {
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

	$(".activity_menu_open").click(function(eventObj) {
		eventObj.preventDefault();

		const menu = mdc.menu.MDCMenu.attachTo($(this).parent().find('.mdc-menu')[0]);
        menu.setFixedPosition(true);

        menu.listen("MDCMenu:selected", function (event) {
        	var data = $(event.detail.item).data();
        	
        	console.log('ACTION: ' + data['action'] + '(' + data['id'] + ')');
        });

		menu.open = (menu.open == false);
	});
	
	$(".toggle_integration_content").hide();
	
	$(".toggle_integration").click(function(eventObj) {
		var visible = $(".toggle_integration_content:visible");
		
		$(".toggle_integration_content").hide();
		$(".toggle_integration span.material-icons").text("add_circle");
		
		if (visible.length == 0) {
			$(this).parent().find(".toggle_integration_content").show();
			$(this).parent().find(".toggle_integration span.material-icons").text("cancel");
		}
	});
	
    $(".builder_game_preview").each(function() {
		$(this).height($(this).parent().height());
	});

    cytoscape_dagre(cytoscape); // register extension
    
    $(".builder_game_preview" ).each(function(index) {
		var definition = $(this).data("definition");

		var cy = cytoscape({
			'container': $(this),
			'elements': definition,

			'layout': {
				name: 'dagre'
			}
		});

		cy.ready(function(event){
			cy.center();
		});
    });
});