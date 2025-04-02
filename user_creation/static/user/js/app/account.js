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

	drawer.open = true;

	const emailField = mdc.textField.MDCTextField.attachTo(document.getElementById('email-field'));
	const currentPasswordField = mdc.textField.MDCTextField.attachTo(document.getElementById('current-password-field'));
	const newPasswordField = mdc.textField.MDCTextField.attachTo(document.getElementById('new-password-field'));
	const confirmPasswordField = mdc.textField.MDCTextField.attachTo(document.getElementById('confirm-password-field'));

	$("#update-form").submit(function(event) {
		let email = emailField.value;
		let currentPassword = currentPasswordField.value;
		let newPassword = newPasswordField.value;
		let confirmPassword = confirmPasswordField.value;

		if (newPassword != "") {
			if (currentPassword == "") {
				alert("Enter current password to continue.")

				event.preventDefault();
			} else if (newPassword != confirmPassword) {
				alert("Password confirmation does not match new password provided.")

				event.preventDefault();
			}
		}

		if (email == "") {
			alert("Please enter a valid e-mail address.")

			event.preventDefault();
		}
	});
});