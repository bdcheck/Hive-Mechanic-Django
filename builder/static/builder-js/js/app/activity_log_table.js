/* global requirejs */

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

  const itemsList = mdc.list.MDCList.attachTo(document.getElementById('sequences_list'))

  itemsList.listen('MDCList:action', function (e) {
    const path = $(itemsList.listElements[e.detail.index]).attr('data-href')

    window.location = path
  })

  topAppBar.setScrollTarget(document.getElementById('main-content'))

  topAppBar.listen('MDCTopAppBar:nav', () => {
    drawer.open = !drawer.open
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

  drawer.open = true

  const itemsPerPage = mdc.select.MDCSelect.attachTo(document.getElementById('items_per_page'))

  const currentUrl = new URL(window.location)

  let pageSize = currentUrl.searchParams.get('size')

  if (pageSize === undefined || pageSize === null) {
    pageSize = '25'
  }

  itemsPerPage.value = pageSize

  itemsPerPage.listen('MDCSelect:change', function () {
    const currentUrl = new URL(window.location)

    currentUrl.searchParams.set('size', itemsPerPage.value)

    window.location = currentUrl.href
  })

  mdc.dataTable.MDCDataTable.attachTo(document.getElementById('events_table'))

  $('.mdc-data-table__row').click(function (event) {
    let target = $(event.target)

    while (target.get(0).nodeName.toLowerCase() !== 'tr') {
      target = target.parent()
    }

    $('#event_name').html(target.data('name'))
    $('#event_summary').html(target.data('message'))
    $('#event_date').html(target.data('date'))

    console.log('PARSE: ')
    console.log(target.data('details'))

    const details = target.data('details')

    let detailsHtml = ''

    for (let key of Object.keys(details)) {
      let value = details[key]

      if (detailsHtml !== '') {
        detailsHtml += '<br />'
      }

      if (key === 'hive_player') {
        key = 'Player'

        value = 'twilio_player:XXXXXX' + value.slice(-4)
      } else if (key === 'hive_session') {
        key = 'Session'
      } else if (key === 'game_version') {
        key = 'Game'
      }

      detailsHtml += '<strong>' + key + ':</strong> ' + value
    }

    $('#event_details').html(detailsHtml)
    $('#event_preview').hide()

    const dialogPreview = mdc.dialog.MDCDialog.attachTo(document.getElementById('dialog_preview'))
    console.log('dialogPreview')
    console.log(dialogPreview)

    const preview = target.data('attachment')

    console.log('PREVIEW: ')
    console.log(preview)

    if (preview) {
      $('#event_preview').attr('src', preview)
      $('#event_preview').show()

      $('#dialog_preview_image').attr('src', preview)
    } else {
      $('#event_preview').hide()
    }

    $('#event_preview').click(function () {
      console.log('CLICK PREVIEW')
      dialogPreview.open()
    })

    const currentBackground = target.css('background-color')

    $('.mdc-data-table__row').css('background-color', '')

    if (currentBackground === 'rgb(224, 224, 224)') { // Deselect
      $('#event_details_view').hide()
      $('#empty_details').show()
    } else { // Select
      $('#event_details_view').show()
      $('#empty_details').hide()

      target.css('background-color', 'rgb(224, 224, 224)')
    }
  })

  $('#event_details_view').hide()

  mdc.textField.MDCTextField.attachTo(document.getElementById('start_date'))
  mdc.textField.MDCTextField.attachTo(document.getElementById('end_date'))
  mdc.textField.MDCTextField.attachTo(document.getElementById('search_field'))
})
