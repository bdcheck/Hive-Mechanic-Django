/* global requirejs, $ */

requirejs.config({
  shim: {
    jquery: {
      exports: '$'
    },
    cookie: {
      exports: 'Cookies',
      deps: ['jquery']
    },
    klayjs: {
      exports: '$klay'
    },
    dagre: {
      exports: 'dagre'
    },
    'cytoscape-klay': {
      deps: ['klayjs']
    },
    'cytoscape-dagre': {
      deps: ['dagre']
    }
  },
  baseUrl: '/static/builder-js/js/app',
  paths: {
    app: '/static/builder-js/js/app',
    material: '/static/builder-js/vendor/material-components-web.min',
    jquery: '/static/builder-js/vendor/jquery-3.4.0.min',
    cookie: '/static/builder-js/vendor/js.cookie',
    cytoscape: '/static/builder-js/vendor/cytoscape-3.19.1.min',
    'cytoscape-klay': '/static/builder-js/vendor/cytoscape-klay',
    'cytoscape-dagre': '/static/builder-js/vendor/cytoscape-dagre',
    klayjs: '/static/builder-js/vendor/klay',
    dagre: '/static/builder-js/vendor/dagre.min'
  }
})

requirejs(['material', 'cookie', 'cytoscape', 'cytoscape-dagre'], function (mdc, Cookies, cytoscape, cytoscapeDagre) {
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

  const baseDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('base-dialog'))

  mdc.ripple.MDCRipple.attachTo(document.getElementById('action_add_game'))

  const addDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('dialog_add_game'))

  const viewStructureDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('preview-dialog'))

  $('#action_add_game').click(function (eventObj) {
    eventObj.preventDefault()
    addDialog.open()
  })

  const nameField = mdc.textField.MDCTextField.attachTo(document.getElementById('textfield_add_game'))

  $('input[type=radio][name=activity-template]').change(function (eventObj) { // eslint-disable-line @typescript-eslint/no-unused-vars
    const selected = $('input[type=radio][name=activity-template]:checked')

    const name = selected.attr('data-name')

    const existingName = $('#field_add_game').val()

    if (existingName === '' || (existingName.startsWith('New ') && existingName.endsWith(' Activity'))) {
      if (name !== undefined) {
        nameField.value = 'New ' + name + ' Activity'
      } else {
        nameField.value = 'New Blank Activity'
      }
    }
  })

  addDialog.listen('MDCDialog:closed', function (action) {
    if (action.detail.action === 'add') {
      const name = nameField.value

      const selected = $('input[type=radio][name=activity-template]:checked').val()

      const payload = {
        name,
        template: selected
      }

      $.post('/builder/add-game.json', payload, function (response) {
        if (response.success) {
          $('#dialog-title').html('Success')
        } else {
          $('#dialog-title').html('Failure')
        }

        $('#dialog-content').html(response.message)

        baseDialog.listen('MDCDialog:closed', function () {
          if (response.success) {
            if (response.redirect !== undefined) {
              window.location.href = response.redirect
            }
          }
        })

        baseDialog.open()
      })
    }
  })

  const cloneDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('dialog_clone_game'))
  const cloneNameField = mdc.textField.MDCTextField.attachTo(document.getElementById('textfield_clone_game'))

  cloneDialog.listen('MDCDialog:closed', function (action) {
    if (action.detail.action === 'add') {
      const name = cloneNameField.value

      const payload = {
        name,
        template: $('#original_clone_id').val()
      }

      $.post('/builder/add-game.json', payload, function (response) {
        if (response.success) {
          $('#dialog-title').html('Success')
        } else {
          $('#dialog-title').html('Failure')
        }

        $('#dialog-content').html(response.message)

        baseDialog.listen('MDCDialog:closed', function () {
          if (response.success) {
            if (response.redirect !== undefined) {
              window.location.href = response.redirect
            }
          }
        })

        baseDialog.open()
      })
    }
  })

  const archiveDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('dialog_archive_game'))

  archiveDialog.listen('MDCDialog:closed', function (action) {
    if (action.detail.action === 'archive') {
      window.location.href = '/builder/activity/' + $('#game_archive_id').val() + '/archive'
    }
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

  $('.activity_menu_open').click(function (eventObj) {
    eventObj.preventDefault()

    const menu = mdc.menu.MDCMenu.attachTo($(this).parent().find('.mdc-menu')[0])
    menu.setFixedPosition(true)

    menu.listen('MDCMenu:selected', function (event) {
      const data = $(event.detail.item).data()

      if (data.action === 'archive') {
        $('#archive_game_name').html(data.name)
        $('#game_archive_id').val(data.id)

        archiveDialog.open()
      } else if (data.action === 'clone') {
        cloneNameField.value = 'Clone of ' + data.name
        $('#original_clone_id').val(data.id)

        cloneDialog.open()
      } else {
        alert('ACTION: ' + data.action + '(' + data.id + ')')
      }
    })

    menu.open = (menu.open === false)
  })

  $('.toggle_integration_content').hide()

  $('.toggle_integration').click(function (eventObj) { // eslint-disable-line @typescript-eslint/no-unused-vars
    const visible = $('.toggle_integration_content:visible')

    $('.toggle_integration_content').hide()
    $('.toggle_integration span.material-icons').text('add_circle')

    if (visible.length === 0) {
      $(this).parent().find('.toggle_integration_content').show()
      $(this).parent().find('.toggle_integration span.material-icons').text('cancel')
    }
  })

  $('.builder_game_preview').each(function () {
    $(this).height($(this).parent().parent().height())
  })

  cytoscapeDagre(cytoscape) // register extension

  $('.builder_game_preview').each(function (index) { // eslint-disable-line @typescript-eslint/no-unused-vars
    const definition = $(this).data('definition')

    const cy = cytoscape({
      container: $(this),
      elements: definition,
      userZoomingEnabled: false,
      userPanningEnabled: false,
      boxSelectionEnabled: false,
      layout: {
        name: 'dagre'
      }
    })

    cy.ready(function (event) { // eslint-disable-line @typescript-eslint/no-unused-vars
      cy.center()
      cy.autolock(true)
    })
  })

  $('.preview_icon_button').click(function (eventObj) {
    eventObj.preventDefault()

    $('#preview-dialog-canvas').height(parseInt($(window).height() * 0.9))
    $('#preview-dialog-canvas').width(parseInt($(window).width() * 0.9))

    $('#preview-dialog-content').height($('#preview-dialog-canvas').height())
    $('#preview-dialog-content').css('overflow', 'hidden')

    viewStructureDialog.open()

    $('#preview-dialog-canvas').attr('src', $(this).attr('data-preview-url'))
  })

  window.setTimeout(function () {
    $('.preview_icon_button').show()
  }, 500)
})
