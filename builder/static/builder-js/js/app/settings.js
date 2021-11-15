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

    const topAppBar = mdc.topAppBar.MDCTopAppBar.attachTo(document.getElementById('app-bar'));
    
    var selectedSequence = null;

    topAppBar.setScrollTarget(document.getElementById('main-content'));

    topAppBar.listen('MDCTopAppBar:nav', () => {
        drawer.open = !drawer.open;
    });

    const itemsList = mdc.list.MDCList.attachTo(document.getElementById('sequences_list'));

    itemsList.listen('MDCList:action', function(e) {
    	const path = $(itemsList.listElements[e['detail']['index']]).attr("data-href");

    	window.location = path;
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

    $("#banner_image").click(function(event) {
        event.preventDefault();

        $("#banner_file").click();
    });
    
    const nameField = mdc.textField.MDCTextField.attachTo(document.querySelector('.mdc-text-field'));

    $('#update_button').click(function() { // catch the form's submit event
    	console.log("CLICK");
    	
        var fileData = new FormData();
        fileData.append('site_name', $('#site_name').val());
        fileData.append('site_banner', $('#banner_file').get(0).files[0]);

        $.ajax({
            url: '/builder/settings',
            type: 'POST',
            data: fileData,
            async: true,
            cache: false,
            processData: false,
            contentType: false,
            enctype: 'multipart/form-data',
            success: function(response){
                $("#banner_image").attr("src", response["url"]);
                alert('Settings updated.');
            }
        });

        return false;
    });
    
    drawer.open = true;
});