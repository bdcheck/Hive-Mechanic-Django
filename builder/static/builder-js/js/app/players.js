/* global requirejs, alert */

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

  const itemsList = mdc.list.MDCList.attachTo(document.getElementById('sequences_list'))

  itemsList.listen('MDCList:action', function (e) {
    const path = $(itemsList.listElements[e.detail.index]).attr('data-href')

    window.location = path
  })

  const topAppBar = mdc.topAppBar.MDCTopAppBar.attachTo(document.getElementById('app-bar'))

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

  mdc.dataTable.MDCDataTable.attachTo(document.getElementById('table_players'))

  $('.action_delete_player').click(function (eventObj) {
    eventObj.preventDefault()

    alert('TODO: Remove player #' + $(eventObj.target).attr('data-id'))
  })

  const baseDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('base-dialog'))

  let selectedClearId = -1

  const clearVariablesDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('dialog_clear_variables'))

  clearVariablesDialog.listen('MDCDialog:closed', function (action) {
    if (action.detail.action === 'clear_variables') {
      const which = $('input[type=radio][name=clear-variables]:checked').val()

      const payload = {
        id: selectedClearId,
        clear: which
      }

      $.post('/builder/clear-variables.json', payload, function (response) {
        if (response.success) {
          $('#dialog-title').html('Success')
        } else {
          $('#dialog-title').html('Failure')
        }

        $('#dialog-content').html(response.message)

        baseDialog.listen('MDCDialog:closed', function () {

        })

        baseDialog.open()
      })
    }
  })

  $('.action_clear_variables').click(function (eventObj) {
    eventObj.preventDefault()

    selectedClearId = parseInt($(eventObj.target).attr('data-id'))

    clearVariablesDialog.open()
  })
})
