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

  const baseDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('base-dialog'))

  const editDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById('dialog_edit_integration'))

  const integrationName = mdc.textField.MDCTextField.attachTo(document.getElementById('textfield_integration_name'))

  $('.edit_integration').click(function (eventObj) {
    eventObj.preventDefault()

    const target = $(eventObj.target)

    const integrationId = target.attr('data-id')

    integrationName.value = target.attr('data-name')

    $('#integration_id').val(integrationId)

    $('[name="activity_name"]').removeAttr('checked')

    const game = target.attr('data-game')

    const integrationType = target.attr('data-type')

    $('.activity_name').css({
      'text-decoration-line': ''
    })

    $('.mdc-radio input').removeAttr('disabled')
    $('[name="activity_name"]').removeAttr('checked')

    $('.integration_linked_warning').hide()

    $('.includes_' + integrationType + ' .activity_name').css({
      'text-decoration-line': 'line-through'
    })

    $('.includes_' + integrationType + ' .integration_linked_warning').show()

    $('.includes_' + integrationType + ' input').attr('disabled', true)

    if (game !== '') {
      $('[name="activity_name"][value="' + game + '"]').attr('checked', true)
      $('[name="activity_name"][value="' + game + '"]').removeAttr('disabled')

      $('#activity_name_' + game + '_label .activity_name').css({
        'text-decoration-line': ''
      })

      $('#activity_name_' + game + '_label .integration_linked_warning').hide()
    } else {
      $('[name="activity_name"][value="-1"]').attr('checked', true)
    }

    editDialog.open()
  })

  editDialog.listen('MDCDialog:closed', function (action) {
    if (action.detail.action === 'update_integration') {
      const name = integrationName.value

      if (name === undefined || name.trim() === '') {
        $('#dialog-title').html('Integration name required')
        $('#dialog-content').html('Please provide a name for the integration.')

        baseDialog.listen('MDCDialog:closed', function () {})

        baseDialog.open()

        return
      }

      const payload = {
        id: $('#integration_id').val(),
        name: name.trim(),
        activity: $('[name="activity_name"]:checked').val()
      }

      $.post('/builder/update-integration.json', payload, function (response) {
        if (response.result === 'success') {
          $('#dialog-title').html('Success')
        } else {
          $('#dialog-title').html('Failure')
        }

        $('#dialog-content').html(response.message)

        baseDialog.listen('MDCDialog:closed', function () {
          if (response.result === 'success') {
            if (response.redirect !== undefined) {
              window.location.href = response.redirect
            }
          }
        })

        baseDialog.open()
      })
    }
  })

  $('#builder_integration_form').on('submit', function () {
    const integrationName = $('#integration_name')

    if (integrationName.val() === '') {
      alert('Name Required')
      return false
    }
  })
})
