/* global requirejs, $ */

requirejs.config({
  shim: {
    jquery: {
      exports: '$'
    },
    cookie: {
      exports: 'Cookies'
    },
    bootstrap: {
      deps: ['jquery']
    }
  },
  baseUrl: '/static/builder-js/js/app',
  paths: {
    app: '/static/builder-js/js/app',
    material: '/static/builder-js/vendor/material-components-web.min',
    jquery: '/static/builder-js/vendor/jquery-3.4.0.min',
    cookie: '/static/builder-js/vendor/js.cookie'
  }
})

requirejs(['material', 'cookie', 'jquery'], function (mdc, Cookies) {
  const drawer = mdc.drawer.MDCDrawer.attachTo(document.querySelector('.mdc-drawer'))

  const topAppBar = mdc.topAppBar.MDCTopAppBar.attachTo(document.getElementById('app-bar'))

  topAppBar.setScrollTarget(document.getElementById('main-content'))

  topAppBar.listen('MDCTopAppBar:nav', () => {
    drawer.open = !drawer.open
  })

  const itemsList = mdc.list.MDCList.attachTo(document.getElementById('sequences_list'))

  itemsList.listen('MDCList:action', function (e) {
    const path = $(itemsList.listElements[e.detail.index]).attr('data-href')

    window.location = path
  })

  const csrftoken = Cookies.get('csrftoken')

  function csrfSafeMethod (method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method))
  }

  $.ajaxSetup({
    beforeSend: function (xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader('X-CSRFToken', csrftoken)
      }
    }
  })

  $('#banner_image').click(function (event) {
    event.preventDefault()

    $('#banner_file').click()
  })

  const uploadDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('dialog_upload_file'))
  const uploadDescriptionField = mdc.textField.MDCTextField.attachTo(document.getElementById('file_description'))

  uploadDialog.listen('MDCDialog:closed', function (action) {
    if (action.detail.action === 'upload') {
      $('#upload_file_description').val(uploadDescriptionField.value)

      $('#upload_file_form').submit()
    }
  })

   
  $('#upload_button').click(function (eventObj) { // eslint-disable-line @typescript-eslint/no-unused-vars
    $('#upload_field').off('change')

    $('#upload_field').on('change', function (event) {
      const filename = event.target.files[0].name

      uploadDescriptionField.value = filename

      uploadDialog.open()
    })

    $('#upload_field').click()
  })

  // const fileFilterField = mdc.textField.MDCTextField.attachTo(document.getElementById('file_filter'))
  // mdc.textField.MDCTextField.attachTo(document.getElementById('file_filter'))

  // $('#image-filter').on('keyup', function () {
  //  const val = $(this).val().toLowerCase()
  //  console.log(val)
  //  $('.image-grid').filter(function () {
  //    $(this).toggle($(this).data('name').toLowerCase().indexOf(val) > -1)
  //  })
  // })

  $('.clipboard-copy').click(function () { // catch the form's submit event
    const copyText = $(this).attr('data-url')

    navigator.clipboard.writeText(copyText).then(function () {
      alert('URL copied to clipboard.')
    }).catch(function () {
      alert('Error copying URL to clipboard.')
    })
  })

  drawer.open = true
})
