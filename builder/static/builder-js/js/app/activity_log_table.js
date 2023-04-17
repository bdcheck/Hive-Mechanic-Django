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

  const startDate = mdc.textField.MDCTextField.attachTo(document.getElementById('start_date'))
  const endDate = mdc.textField.MDCTextField.attachTo(document.getElementById('end_date'))

  $('#filter_date_button').click(function (eventObj) {
    console.log('START:')
    console.log(startDate.value)

    console.log('END:')
    console.log(endDate.value)

    if (startDate.value !== '' && endDate.value !== '' && endDate.value < startDate.value) {
      const endValue = endDate.value

      endDate.value = startDate.value
      startDate.value = endValue
    }

    const currentUrl = new URL(window.location)

    currentUrl.searchParams.set('start', startDate.value)
    currentUrl.searchParams.set('end', endDate.value)

    window.location = currentUrl.href
  })

  mdc.textField.MDCTextField.attachTo(document.getElementById('search_field'))
  // const clearSearch = mdc.textField.MDCTextFieldIcon(document.getElementById('search_field_clear'));

  $('#search_field input').keyup(function (eventObj) {
    if (eventObj.originalEvent.keyCode === 13) {
      eventObj.preventDefault()

      const query = $('#search_field input').val()

      const currentUrl = new URL(window.location)

      currentUrl.searchParams.set('q', query)

      window.location = currentUrl.href
    }
  })

  $('#search_field_clear').click(function (eventObj) {
    const currentUrl = new URL(window.location)

    currentUrl.searchParams.set('q', '')

    window.location = currentUrl.href
  })

  $('#sort_source').click(function (eventObj) {
    const currentUrl = new URL(window.location)

    if (currentUrl.searchParams.get('sort', '') === 'source') {
      currentUrl.searchParams.set('sort', '-source')
    } else {
      currentUrl.searchParams.set('sort', 'source')
    }

    window.location = currentUrl.href
  })

  $('#sort_player').click(function (eventObj) {
    const currentUrl = new URL(window.location)

    if (currentUrl.searchParams.get('sort', '') === 'player') {
      currentUrl.searchParams.set('sort', '-player')
    } else {
      currentUrl.searchParams.set('sort', 'player')
    }

    window.location = currentUrl.href
  })

  $('#sort_message').click(function (eventObj) {
    const currentUrl = new URL(window.location)

    if (currentUrl.searchParams.get('sort', '') === 'message') {
      currentUrl.searchParams.set('sort', '-message')
    } else {
      currentUrl.searchParams.set('sort', 'message')
    }

    window.location = currentUrl.href
  })

  $('#sort_logged').click(function (eventObj) {
    const currentUrl = new URL(window.location)

    if (currentUrl.searchParams.get('sort', '') === 'logged') {
      currentUrl.searchParams.set('sort', '-logged')
    } else {
      currentUrl.searchParams.set('sort', 'logged')
    }

    window.location = currentUrl.href
  })
})
