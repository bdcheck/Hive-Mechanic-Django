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

  mdc.dataTable.MDCDataTable.attachTo(document.getElementById('table_players'))

  $('.action_approve_user').click(function (eventObj) {
    eventObj.preventDefault()

    const data = {
      action: 'activate_user',
      email: $(eventObj.target).attr('data-id')
    }

    if (confirm('Are you sure you wish to activate this author?')) {
      $.post('/builder/authors', data, function (data) {
        if (data.message) {
          alert(data.message)
        }

        window.location.reload()
      })
    }
  })

  $('.action_delete_user').click(function (eventObj) {
    eventObj.preventDefault()

    const data = {
      action: 'delete_user',
      email: $(eventObj.target).attr('data-id')
    }

    if (confirm('Are you sure you wish to delete this author?')) {
      $.post('/builder/authors', data, function (data) {
        if (data.message) {
          alert(data.message)
        }

        window.location.reload()
      })
    }
  })

  $('.action_deactivate_user').click(function (eventObj) {
    eventObj.preventDefault()

    const data = {
      action: 'deactivate_user',
      email: $(eventObj.target).attr('data-id')
    }

    if (confirm('Are you sure you wish to deactivate this author?')) {
      $.post('/builder/authors', data, function (data) {
        if (data.message) {
          alert(data.message)
        }

        window.location.reload()
      })
    }
  })

  $('.action_decrease_access').click(function (eventObj) {
    eventObj.preventDefault()

    const data = {
      action: 'demote_user',
      email: $(eventObj.target).attr('data-id')
    }

    if (confirm('Are you sure you wish to demote this author?')) {
      $.post('/builder/authors', data, function (data) {
        if (data.message) {
          alert(data.message)
        }

        window.location.reload()
      })
    }
  })

  $('.action_increase_access').click(function (eventObj) {
    eventObj.preventDefault()

    const data = {
      action: 'promote_user',
      email: $(eventObj.target).attr('data-id')
    }

    if (confirm('Are you sure you wish to promote this author?')) {
      $.post('/builder/authors', data, function (data) {
        if (data.message) {
          alert(data.message)
        }

        window.location.reload()
      })
    }
  })
})
