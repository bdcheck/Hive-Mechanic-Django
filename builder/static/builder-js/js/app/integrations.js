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
    drawer.open = true
    const editDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('dialog_edit_integration'));

    //Button click to open integration dialog using
    $(".edit_integration").click(function(eventObj) {
        eventObj.preventDefault();
        let tg = $(eventObj.target);
        let tx_in = $("#integration_name");
        let tx_id = $('#integration_id')
		let int_id = tg.attr('data-id');
        let int_name = tg.attr('data-name');
        let game_name = tg.attr('data-game');
        let radios = $('input[name=game_id]');

        let radio = radios.filter(function() {
            return $(this).val() === game_name
        })

        radio.prop("checked", true)
        tx_in.val(int_name)
        tx_id.val(int_id)
        editDialog.open()
    });
    editDialog.listen('MDCDialog:closed', function() {
        let radios = $('input[name=game_id]');
        let tx_in = $("#integration_name");
        let tx_id = $('#integration_id')
        radios.prop("checked", false)
        tx_in.val("")
        tx_id.val("")
    });


});