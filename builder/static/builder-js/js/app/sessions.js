/* global requirejs, confirm */

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

  drawer.open = true

  mdc.dataTable.MDCDataTable.attachTo(document.getElementById('table_sessions'))

  $('.session-action').click(function (event) {
    event.preventDefault()

    const sessionId = $(this).attr('data-session-id')
    const action = $(this).attr('data-action')

    const data = {
      action: action,
      session: sessionId
    }

    if (action === 'delete') {
      if (confirm('Are you sure you wish to remove this session?')) {
        $.post('/builder/session/actions', data, function (data) {
          if (data.success) {
            window.location.reload()
          }
        })
      }
    } else if (action === 'cancel') {
      if (confirm('Are you sure you wish to cancel this session?')) {
        $.post('/builder/session/actions', data, function (data) {
          if (data.success) {
            window.location.reload()
          }
        })
      }
    } else {
      $.post('/builder/session/actions', data, function (data) {
        if (data.success) {
          window.location.reload()
        }
      })
    }
  })
})
