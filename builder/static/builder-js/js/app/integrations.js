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
  drawer.open = true
  const editDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('dialog_edit_integration'))

  // Button click to open integration dialog using
  $('.edit_integration').click(function (eventObj) {
    eventObj.preventDefault()
    const target = $(eventObj.target)
    const integrationName = $('#integration_name')
    const integrationId = $('#integration_id')
    const dataId = target.attr('data-id')
    const dataName = target.attr('data-name')
    const gameName = target.attr('data-game')
    const radios = $('input[name=game_id]')

    const radio = radios.filter(function () {
      return $(this).val() === gameName
    })

    radio.prop('checked', true)
    integrationName.val(dataName)
    integrationId.val(dataId)
    editDialog.open()
  })
  editDialog.listen('MDCDialog:closed', function () {
    const radios = $('input[name=game_id]')
    const integrationName = $('#integration_name')
    const integrationId = $('#integration_id')
    radios.prop('checked', false)
    integrationName.val('')
    integrationId.val('')
  })
  $('#builder_integration_form').on('submit', function () {
    const integrationName = $('#integration_name')

    if (integrationName.val() === '') {
      alert('Name Required')
      return false
    }
  })
})
