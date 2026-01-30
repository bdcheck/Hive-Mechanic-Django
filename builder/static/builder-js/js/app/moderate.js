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

  mdc.dataTable.MDCDataTable.attachTo(document.getElementById('moderation_table'))

   
  $('.mdc-data-table__row').click(function (event) { // eslint-disable-line @typescript-eslint/no-unused-vars

  })

  mdc.textField.MDCTextField.attachTo(document.getElementById('search_field'))
  // const clearSearch = mdc.textField.MDCTextFieldIcon(document.getElementById('search_field_clear'));

  const statusSelect = mdc.select.MDCSelect.attachTo(document.getElementById('status_select'))

  statusSelect.listen('MDCSelect:change', () => {
    const url = new URL(window.location.href)

    url.searchParams.set('status', statusSelect.value)

    window.location = url
  })

  $('#search_field input').keyup(function (eventObj) {
    if (eventObj.originalEvent.keyCode === 13) {
      eventObj.preventDefault()

      const query = $('#search_field input').val()

      const currentUrl = new URL(window.location)

      currentUrl.searchParams.set('q', query)

      window.location = currentUrl.href
    }
  })

   
  $('#search_field_clear').click(function (eventObj) { // eslint-disable-line @typescript-eslint/no-unused-vars
    const currentUrl = new URL(window.location)

    currentUrl.searchParams.set('q', '')

    window.location = currentUrl.href
  })

   
  $('#sort_player').click(function (eventObj) { // eslint-disable-line @typescript-eslint/no-unused-vars
    const currentUrl = new URL(window.location)

    if (currentUrl.searchParams.get('sort', '') === 'player') {
      currentUrl.searchParams.set('sort', '-player')
    } else {
      currentUrl.searchParams.set('sort', 'player')
    }

    window.location = currentUrl.href
  })

   
  $('#sort_content').click(function (eventObj) { // eslint-disable-line @typescript-eslint/no-unused-vars
    const currentUrl = new URL(window.location)

    if (currentUrl.searchParams.get('sort', '') === 'content') {
      currentUrl.searchParams.set('sort', '-content')
    } else {
      currentUrl.searchParams.set('sort', 'content')
    }

    window.location = currentUrl.href
  })

   
  $('#sort_submitted').click(function (eventObj) { // eslint-disable-line @typescript-eslint/no-unused-vars
    const currentUrl = new URL(window.location)

    if (currentUrl.searchParams.get('sort', '') === 'submitted') {
      currentUrl.searchParams.set('sort', '-added')
    } else {
      currentUrl.searchParams.set('sort', 'added')
    }

    window.location = currentUrl.href
  })

  const fetchSelected = function () {
    const selectedIds = []

    $('.moderate-item:checked').each(function (index, element) {
      const selectedId = $(element).attr('data-value')

      if (selectedId !== undefined) {
        selectedIds.push(selectedId)
      }
    })

    return selectedIds
  }

  $('.moderate-item:checked').prop('checked', false)

  $('#button_approve').prop('disabled', true)
  $('#button_reject').prop('disabled', true)
  $('#button_reset').prop('disabled', true)

  $('input[type="checkbox"]').change(function () {
    window.setTimeout(function () {
      const selected = fetchSelected()

      if (selected.length === 0) {
        $('#selection_label').text('Please select items to moderate.')

        $('#button_approve').prop('disabled', true)
        $('#button_reject').prop('disabled', true)
        $('#button_reset').prop('disabled', true)
      } else if (selected.length === 1) {
        $('#selection_label').text('1 item selected.')

        $('#button_approve').prop('disabled', false)
        $('#button_reject').prop('disabled', false)
        $('#button_reset').prop('disabled', false)
      } else {
        $('#selection_label').text(`${selected.length} items selected.`)

        $('#button_approve').prop('disabled', false)
        $('#button_reject').prop('disabled', false)
        $('#button_reset').prop('disabled', false)
      }
    }, 250)
  })

   
  $('#button_approve').click(function (eventObj) { // eslint-disable-line @typescript-eslint/no-unused-vars
    const selected = fetchSelected()

    const payload = {
      action: 'approve',
      selected_ids: JSON.stringify(selected)
    }

    $.post('/builder/moderate', payload, function (data) {
      alert(data.message)

      window.location.reload()
    })
  })

   
  $('#button_reject').click(function (eventObj) { // eslint-disable-line @typescript-eslint/no-unused-vars
    const selected = fetchSelected()

    const payload = {
      action: 'reject',
      selected_ids: JSON.stringify(selected)
    }

    $.post('/builder/moderate', payload, function (data) {
      alert(data.message)

      window.location.reload()
    })
  })

   
  $('#button_reset').click(function (eventObj) { // eslint-disable-line @typescript-eslint/no-unused-vars
    const selected = fetchSelected()

    const payload = {
      action: 'reset',
      selected_ids: JSON.stringify(selected)
    }

    $.post('/builder/moderate', payload, function (data) {
      alert(data.message)

      window.location.reload()
    })
  })

  $('#right_bar').css('max-width', $('#right_bar').width() + 'px')
})
