define(['material', 'slugify', 'marked', 'purify', 'jquery'], function (mdc, slugifyExt, marked, purify) {
  class Node {
    constructor (definition, sequence) {
      this.definition = definition
      this.sequence = sequence
      this.id = definition.id
      this.cardId = Node.uuidv4()
    }

    cardName () {
      if (this.definition.name !== undefined) {
        return this.definition.name
      }

      return this.definition.type
    }

    cardType () {
      return this.definition.type
    }

    cardCategory () {
      return 'Uncategorized'
    }

    cardTypeSlug () {
      return Node.slugify(this.definition.type)
    }

    cardIcon () {
      return '<i class="fas fa-question" style="margin-right: 16px; font-size: 20px; "></i>'
    }

    visualizationStyle () {
      return {
        shape: 'round-rectangle',
        'background-color': '#eeeeee'
      }
    }

    destinationDescription (nodeId) {
      return 'Go to...'
    }

    editHtml () {
      let htmlString = '<div class="mdc-card" id="' + this.cardId + '" style="' + this.style() + '" data-node-id="' + this.id + '">'
      htmlString += '  <div class="mdc-layout-grid" style="margin: 0; padding-left: 16px; padding-right: 16px; padding-bottom: 16px;">'
      htmlString += '    <div class="mdc-layout-grid__inner" style="row-gap: 8px;">'
      htmlString += '      <div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12">'
      htmlString += '        <div class="mdc-typography--headline6" style="margin-bottom: 16px;">'
      htmlString += '          <span>' + this.cardIcon() + '</span>'
      htmlString += '          <span style="vertical-align: top;">' + this.cardType() + '</span>'
      htmlString += '          <div class="mdc-menu-surface--anchor" style="float: right;">'
      htmlString += '            <i class="material-icons mdc-icon-button__icon" aria-hidden="true" id="' + this.cardId + '_menu_open">more_vert</i>'
      htmlString += '            <div class="mdc-menu mdc-menu-surface" id="' + this.cardId + '_menu">'
      htmlString += '              <ul class="mdc-list" role="menu" aria-hidden="true" aria-orientation="vertical" tabindex="-1">'
      htmlString += '                <li class="mdc-list-item mdc-list-item mdc-list-item--with-one-line" role="menuitem" data-action="insert_before">'
      htmlString += '                  <span class="mdc-list-item__ripple"></span>'
      htmlString += '                  <span class="mdc-list-item__text mdc-list-item__start">Insert Card Before&#8230;</span>'
      htmlString += '                </li>'
      htmlString += '                <li class="mdc-list-item mdc-list-item mdc-list-item--with-one-line" role="menuitem" data-action="advanced">'
      htmlString += '                  <span class="mdc-list-item__ripple"></span>'
      htmlString += '                  <span class="mdc-list-item__text mdc-list-item__start">Advanced Settings&#8230;</span>'
      htmlString += '                </li>'
      htmlString += '              </ul>'
      htmlString += '            </div>'
      htmlString += '          </div>'
      htmlString += '        </div>'
      htmlString += '      </div>'
      htmlString += '      <div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12">'
      htmlString += '        <div class="mdc-text-field mdc-text-field--outlined" id="' + this.cardId + '_name" style="width: 100%; background-color: #ffffff;">'
      htmlString += '          <input class="mdc-text-field__input" type="text" id="' + this.cardId + '_name_value">'
      htmlString += '          <div class="mdc-notched-outline">'
      htmlString += '            <div class="mdc-notched-outline__leading"></div>'
      htmlString += '            <div class="mdc-notched-outline__notch">'
      htmlString += '              <label for="' + this.cardId + '_name_value" class="mdc-floating-label">Card Name</label>'
      htmlString += '            </div>'
      htmlString += '            <div class="mdc-notched-outline__trailing"></div>'
      htmlString += '          </div>'
      htmlString += '        </div>'
      htmlString += '      </div>'

      if (this.showComment()) {
        htmlString += '      <div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12 mdc-typography--caption" id="' + this.cardId + '_comment" style="background-color: #FDFEDE; padding: 4px;"></div>'
      }

      htmlString += this.editBody()

      htmlString += '    </div>'
      htmlString += '  </div>'
      htmlString += '</div>'
      htmlString += '<div class="mdc-dialog" id="' + this.cardId + '-advanced-dialog">'
      htmlString += '  <div class="mdc-dialog__container">'
      htmlString += '    <div class="mdc-dialog__surface">'
      htmlString += '      <h2 class="mdc-dialog__title" id="' + this.cardId + '-advanced-dialog-title">' + this.cardName() + '</h2>'
      htmlString += '      <div class="mdc-dialog__content" id="' + this.cardId + '-advanced-dialog-content" style="padding-top: 8px;">'
      htmlString += this.advancedEditBody()
      htmlString += '      </div>'
      htmlString += '      <footer class="mdc-dialog__actions">'
      htmlString += '        <button type="button" class="mdc-button mdc-dialog__button" data-mdc-dialog-action="delete" style="margin-right: auto;">'
      htmlString += '          <span class="mdc-button__label">Remove Card</span>'
      htmlString += '        </button>'
      htmlString += '        <button type="button" class="mdc-button mdc-dialog__button" data-mdc-dialog-action="close">'
      htmlString += '          <span class="mdc-button__label">Close</span>'
      htmlString += '        </button>'
      htmlString += '      </footer>'
      htmlString += '    </div>'
      htmlString += '  </div>'
      htmlString += '  <div class="mdc-dialog__scrim"></div>'
      htmlString += '</div>'

      return htmlString
    }

    /* Error / validity checking */
    issues (sequence) {
      const issues = []

      if (this.definition.name === undefined || this.definition.name.trim().length === 0) {
        issues.push(['Please provide a node name.', 'node', this.definition.id, this.cardName()])
      }

      if (this.definition.id === undefined || this.definition.id.trim().length === 0) {
        issues.push(['Please provide a node ID.', 'node', this.definition.id], this.cardName())
      }

      const destinations = this.destinationNodes(sequence)

      for (let i = 0; i < destinations.length; i++) {
        const destination = destinations[i]

        if (destination === null || destination === undefined) {
          issues.push(['Empty destination node.', 'node', this.definition.id, this.cardName()])
        } else if (this.sequence.definition.id === destination.sequence.definition.id && this.id === destination.id) {
          issues.push(['Node references self in destination.', 'node', this.definition.id, this.cardName()])
        }
      }

      return issues
    }

    initialize () {
      const me = this

      mdc.menuSurface.MDCMenuSurface.attachTo(document.getElementById(this.cardId + '_menu'))

      const nameField = mdc.textField.MDCTextField.attachTo(document.getElementById(this.cardId + '_name'))
      nameField.value = this.cardName()

      $('#' + this.cardId + '_name_value').on('change keyup paste', function () {
        const value = $('#' + me.cardId + '_name_value').val()

        me.definition.name = value

        me.sequence.markChanged(me.id)
      })

      const idField = mdc.textField.MDCTextField.attachTo(document.getElementById(this.cardId + '_advanced_identifier'))
      idField.value = this.id

      $('#' + this.cardId + '_advanced_identifier_value').on('change keyup paste', function () {
        const value = $('#' + me.cardId + '_advanced_identifier_value').val()

        const slugged = slugifyExt(value, {
          remove: /[*+~.()'"!:@]/g,
          trim: false
        })

        let oldId = me.definition.id

        if (slugged !== value) {
          $('#' + me.cardId + '_activity-identifier-warning').show()
        } else {
          $('#' + me.cardId + '_activity-identifier-warning').hide()

          const newId = slugged
          const newFullId = me.sequence.definition.id + '#' + newId

          const sources = me.sourceNodes(me.sequence)

          for (let i = 0; i < sources.length; i++) {
            sources[i].updateReferences(oldId, newFullId)
          }

          oldId = me.sequence.definition.id + '#' + oldId

          for (let i = 0; i < sources.length; i++) {
            sources[i].updateReferences(oldId, newFullId)
          }

          me.definition.id = newId
          me.id = newId

          me.sequence.markChanged(me.id)
        }
      })

      $('#' + this.cardId + '_activity-identifier-warning').hide()

      const commentField = mdc.textField.MDCTextField.attachTo(document.getElementById(this.cardId + '_advanced_comment_field'))

      if (this.definition.comment !== undefined) {
        commentField.value = this.definition.comment

        this.updateCommentDisplay(this.definition.comment)
      } else {
        this.updateCommentDisplay('')
      }

      $('#' + this.cardId + '_advanced_comment_value').on('change keyup paste', function () {
        const value = $('#' + me.cardId + '_advanced_comment_value').val()

        me.definition.comment = value

        me.updateCommentDisplay(me.definition.comment)

        me.sequence.markChanged(me.id)
      })

      const element = $('#' + this.cardId + '-advanced-dialog').detach()
      $('body').append(element)

      const advancedDialog = mdc.dialog.MDCDialog.attachTo(document.getElementById(this.cardId + '-advanced-dialog'))

      advancedDialog.listen('MDCDialog:closed', function (event) {
        if (event.detail.action === 'delete') {
          me.sequence.removeCard(me.id)
        }
      })

      mdc.dialog.MDCDialog.attachTo(document.getElementById('card-insert-before'))

      const menu = mdc.menu.MDCMenu.attachTo(document.getElementById(this.cardId + '_menu'))
      menu.setFixedPosition(true)

      menu.listen('MDCMenu:selected', function (event) {
        if (event.detail.index === 0) { // Insert Before
          $('.add_card_context').hide()
          $('#add_card_context_before').show()

          me.sequence.addCard(function (newCardId) {
            const connectExisting = mdc.checkbox.MDCCheckbox.attachTo(document.getElementById('add_card_context_connect_existing'))

            me.sequence.insertBefore(me.id, newCardId, connectExisting.checked)

            //              insertBeforeDialog.listen('MDCDialog:closed', function (event) {
            //                if (event.detail.action === 'transfer') {
            //                } else { // Keep
            //                  me.sequence.insertBefore(me.id, newCardId, false)
            //                }
            //
            //                insertBeforeDialog.unlisten('MDCDialog:closed', this)
            //              })
            //
            //              insertBeforeDialog.open()
          })
        } else {
          advancedDialog.open()
        }
      })

      $('#' + this.cardId + '_menu_open').click(function (eventObj) {
        eventObj.preventDefault()

        menu.open = (menu.open === false)
      })
    }

    updateCommentDisplay (comment) {
      if (comment === null || comment === '') {
        $('#' + this.cardId + '_comment').hide()
      } else {
        $('#' + this.cardId + '_comment').show()
        $('#' + this.cardId + '_comment').html(purify.sanitize(marked.parse(comment)))
      }
    }

    updateReferences (oldId, newId) {
      console.log('TODO: Implement "updateReferences" in ' + this.cardName())
    }

    fetchLocalizedValue (bundle) {
      const keys = Object.keys(bundle)

      keys.sort(function (one, two) {
        const diff = two.length - one.length

        if (diff !== 0) {
          return diff
        }

        if (one < two) {
          return -1
        } else if (one > two) {
          return 1
        }

        return 0
      })

      for (let i = 0; i < navigator.language.lengths; i++) {
        const language = navigator.languages[i].toLowerCase()

        for (let j = 0; j < keys.length; j++) {
          const key = keys[j].toLowerCase()

          if (language.startsWith(key)) {
            return bundle[key]
          }
        }
      }

      return bundle[keys[0]]
    }

    fetchLocalizedConstant (term) {
      const constants = {
        begins_with: {
          en: 'Begins with...'
        },
        ends_with: {
          en: 'Ends with...'
        },
        equals: {
          en: 'Equals/is...'
        },
        not_equals: {
          en: 'Does not equal / is not...'
        },
        contains: {
          en: 'Contains...'
        },
        not_contains: {
          en: 'Does not contain...'
        },
        no_action_defined: {
          en: 'No action defined...'
        }
      }

      this.addTerms(constants)

      const keys = Object.keys(constants[term])

      for (let i = 0; i < navigator.languages.length; i++) {
        const language = navigator.languages[i].toLowerCase()

        for (let j = 0; j < keys.length; j++) {
          const key = keys[j].toLowerCase()

          if (language.startsWith(key)) {
            return constants[term][key]
          }
        }
      }

      return term
    }

    addTerms (terms) {
      // Override in subclasses...
    }

    createImageUrlField (field) {
      const me = this

      const fieldLines = []

      fieldLines.push('<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-' + field.width + '">')
      fieldLines.push('  <div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12">')
      fieldLines.push('    <img src="https://via.placeholder.com/150" id="' + me.cardId + '_' + field.field + '_preview" style="max-width: 100%; margin-bottom: 8px;">')
      fieldLines.push('  </div>')
      fieldLines.push('  <div class="mdc-text-field mdc-text-field--outlined" id="' + me.cardId + '_' + field.field + '_field" style="width: 100%; margin-top: 4px;">')
      fieldLines.push('    <input class="mdc-text-field__input"style="width: 100%" id="' + me.cardId + '_' + field.field + '_value" />')
      fieldLines.push('    <div class="mdc-notched-outline">')
      fieldLines.push('      <div class="mdc-notched-outline__leading"></div>')
      fieldLines.push('      <div class="mdc-notched-outline__notch">')
      fieldLines.push('        <label for="' + me.cardId + '_' + field.field + '_value" class="mdc-floating-label">' + me.fetchLocalizedValue(field.label) + '</label>')
      fieldLines.push('      </div>')
      fieldLines.push('      <div class="mdc-notched-outline__trailing"></div>')
      fieldLines.push('    </div>')
      fieldLines.push('  </div>')
      fieldLines.push('</div>')

      return fieldLines.join('\n')
    }

    createSoundUrlField (field) {
      const me = this

      const fieldLines = []

      fieldLines.push('<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-' + field.width + '">')
      fieldLines.push('  <div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12">')
      fieldLines.push('    <audio controls src="" id="' + me.cardId + '_' + field.field + '_preview" style="max-width: 100%; margin-bottom: 8px;"> </audio>')
      fieldLines.push('  </div>')
      fieldLines.push('  <div class="mdc-text-field mdc-text-field--outlined" id="' + me.cardId + '_' + field.field + '_field" style="width: 100%; margin-top: 4px;">')
      fieldLines.push('    <input class="mdc-text-field__input"style="width: 100%" id="' + me.cardId + '_' + field.field + '_value" />')
      fieldLines.push('    <div class="mdc-notched-outline">')
      fieldLines.push('      <div class="mdc-notched-outline__leading"></div>')
      fieldLines.push('      <div class="mdc-notched-outline__notch">')
      fieldLines.push('        <label for="' + me.cardId + '_' + field.field + '_value" class="mdc-floating-label">' + me.fetchLocalizedValue(field.label) + '</label>')
      fieldLines.push('      </div>')
      fieldLines.push('      <div class="mdc-notched-outline__trailing"></div>')
      fieldLines.push('    </div>')
      fieldLines.push('  </div>')
      fieldLines.push('</div>')

      return fieldLines.join('\n')
    }

    createTextField (field) {
      const me = this

      const fieldLines = []

      fieldLines.push('<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-' + field.width + '">')
      fieldLines.push('  <div class="mdc-text-field mdc-text-field--outlined" id="' + me.cardId + '_' + field.field + '_field" style="width: 100%; margin-top: 4px;">')
      fieldLines.push('    <input class="mdc-text-field__input"style="width: 100%" id="' + me.cardId + '_' + field.field + '_value" />')
      fieldLines.push('    <div class="mdc-notched-outline">')
      fieldLines.push('      <div class="mdc-notched-outline__leading"></div>')
      fieldLines.push('      <div class="mdc-notched-outline__notch">')
      fieldLines.push('        <label for="' + me.cardId + '_' + field.field + '_value" class="mdc-floating-label">' + me.fetchLocalizedValue(field.label) + '</label>')
      fieldLines.push('      </div>')
      fieldLines.push('      <div class="mdc-notched-outline__trailing"></div>')
      fieldLines.push('    </div>')
      fieldLines.push('  </div>')
      fieldLines.push('</div>')

      return fieldLines.join('\n')
    }

    createTextArea (field) {
      const me = this

      const fieldLines = []

      fieldLines.push('<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-' + field.width + '">')
      fieldLines.push('  <label class="mdc-text-field mdc-text-field--textarea mdc-text-field--outlined" id="' + me.cardId + '_' + field.field + '_field" style="width: 100%; margin-top: 4px;">')
      fieldLines.push('    <span class="mdc-notched-outline">')
      fieldLines.push('      <span class="mdc-notched-outline__leading"></span>')
      fieldLines.push('      <span class="mdc-notched-outline__notch">')
      fieldLines.push('        <span class="mdc-floating-label" for="' + me.cardId + '_' + field.field + '_value">' + me.fetchLocalizedValue(field.label) + '</span>')
      fieldLines.push('      </span>')
      fieldLines.push('      <span class="mdc-notched-outline__trailing"></span>')
      fieldLines.push('    </span>')
      fieldLines.push('    <span class="mdc-text-field__resizer">')
      fieldLines.push('      <textarea class="mdc-text-field__input" rows="4" style="width: 100%" id="' + me.cardId + '_' + field.field + '_value"></textarea>')
      fieldLines.push('    </span>')
      fieldLines.push('  </label>')
      fieldLines.push('</div>')

      return fieldLines.join('\n')
    }

    createReadOnly (field) {
      const me = this

      const fieldLines = []

      let style = 'caption'

      if (field.style !== undefined) {
        style = field.style
      }

      let helpClass = ''

      if (field.is_help) {
        helpClass = 'hive_mechanic_help'
      }

      let addClasses = ''

      if (field.add_class !== undefined) {
        addClasses = field.add_class
      }

      if (field.value === '----') {
        fieldLines.push('<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-' + field.width + ' mdc-typography--' + style + ' ' + helpClass + '">')
        fieldLines.push('  <hr style="height: 1px; border: none; color: #9D9E9D; background-color: #9D9E9D;" />')
        fieldLines.push('</div>')
      } else {
        fieldLines.push('<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-' + field.width + ' mdc-typography--' + style + ' ' + helpClass + ' ' + addClasses + '" style="display: flex; align-items: center;">')
        fieldLines.push('  <div>' + me.fetchLocalizedValue(field.value) + '</div>')
        fieldLines.push('</div>')
      }

      if (field.width !== 12 && helpClass !== '') {
        fieldLines.push('<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-' + field.width + ' mdc-typography--' + style + ' hive_mechanic_help_filler">&nbsp;&nbsp;</div>')
      }

      return fieldLines.join('\n')
    }

    createSelect (field) {
      const me = this

      const fieldLines = []

      fieldLines.push('<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-' + field.width + ' mdc-typography--caption">')

      fieldLines.push('  <div class="mdc-select mdc-select--outlined" id="' + me.cardId + '_' + field.field + '" style="width: 100%; margin-top: 4px;">')
      fieldLines.push('    <div class="mdc-select__anchor">')
      fieldLines.push('      <span class="mdc-notched-outline">')
      fieldLines.push('        <span class="mdc-notched-outline__leading"></span>')
      fieldLines.push('        <span class="mdc-notched-outline__notch">')
      fieldLines.push('          <span class="mdc-floating-label">' + me.fetchLocalizedValue(field.label) + '</span>')
      fieldLines.push('        </span>')
      fieldLines.push('        <span class="mdc-notched-outline__trailing"></span>')
      fieldLines.push('      </span>')
      fieldLines.push('      <span class="mdc-select__selected-text-container">')
      fieldLines.push('        <span class="mdc-select__selected-text"></span>')
      fieldLines.push('      </span>')
      fieldLines.push('      <span class="mdc-select__dropdown-icon">')
      fieldLines.push('        <svg class="mdc-select__dropdown-icon-graphic" viewBox="7 10 10 5" focusable="false">')
      fieldLines.push('          <polygon class="mdc-select__dropdown-icon-inactive" stroke="none" fill-rule="evenodd" points="7 10 12 15 17 10"></polygon>')
      fieldLines.push('          <polygon class="mdc-select__dropdown-icon-active" stroke="none" fill-rule="evenodd" points="7 15 12 10 17 15"></polygon>')
      fieldLines.push('        </svg>')
      fieldLines.push('      </span>')
      fieldLines.push('    </div>')

      fieldLines.push('    <div class="mdc-select__menu mdc-menu mdc-menu-surface" role="listbox">')
      fieldLines.push('      <ul class="mdc-list" role="listbox">')

      if (Array.isArray(field.options)) {
        $.each(field.options, function (index, option) {
          fieldLines.push('          <li class="mdc-list-item" data-value="' + option.value + '" role="option">')
          fieldLines.push('            <span class="mdc-list-item__ripple"></span>                ')
          fieldLines.push('            <span class="mdc-list-item__text">' + me.fetchLocalizedValue(option.label) + '<span>')
          fieldLines.push('          </li>')
        })
      }

      fieldLines.push('      </ul>')
      fieldLines.push('    </div>')
      fieldLines.push('  </div>')
      fieldLines.push('</div>')

      return fieldLines.join('\n')
    }

    createCardReference (field) {
      const me = this

      const fieldLines = []

      fieldLines.push('<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-' + field.width + '" style="text-align: right; display: flex; align-items: center; justify-content: right;">')
      fieldLines.push('  <button class="mdc-icon-button" id="' + me.cardId + '_' + field.field + '_edit">')
      fieldLines.push('    <i class="material-icons mdc-icon-button__icon" aria-hidden="true">link</i>')
      fieldLines.push('  </button>')
      fieldLines.push('  <button class="mdc-icon-button" id="' + me.cardId + '_' + field.field + '_goto">')
      fieldLines.push('    <i class="material-icons mdc-icon-button__icon" aria-hidden="true">keyboard_arrow_right</i>')
      fieldLines.push('  </button>')
      fieldLines.push('</div>')

      return fieldLines.join('\n')
    }

    createList (field) {
      const me = this

      const fieldLines = []

      const fieldName = field.field

      fieldLines.push('<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12">')
      fieldLines.push('  <div class="mdc-typography--subtitle2">' + me.fetchLocalizedValue(field.label) + '</div>')
      fieldLines.push('</div>')

      fieldLines.push('<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12">')
      fieldLines.push('  <div id="' + me.cardId + '__' + fieldName + '__items"></div>')
      fieldLines.push('</div>')

      if (field.add_item_text !== undefined) {
        fieldLines.push('<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-6 ">')
        fieldLines.push('  <span class="mdc-typography--caption">' + me.fetchLocalizedValue(field.add_item_text) + '</span>')
        fieldLines.push('</div>')
      } else {
        fieldLines.push('<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-6"></div>')
      }

      if (field.add_item_label !== undefined) {
        fieldLines.push('<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-6" style="text-align: right;">')
        fieldLines.push('  <button class="mdc-button mdc-button--raised" id="' + me.cardId + '__' + fieldName + '__add_item">')
        fieldLines.push('    <span class="mdc-button__label">' + me.fetchLocalizedValue(field.add_item_label) + '</span>')
        fieldLines.push('  </button>')
        fieldLines.push('</div>')
      }

      return fieldLines.join('\n')
    }

    createStructure (field) {
      const me = this

      const fieldLines = []

      const fieldName = field.field

      fieldLines.push('<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12">')
      fieldLines.push('  <div class="mdc-typography--subtitle2">' + me.fetchLocalizedValue(field.label) + '</div>')
      fieldLines.push('</div>')

      fieldLines.push('<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12">')
      fieldLines.push('  <div id="' + me.cardId + '__' + fieldName + '" class="mdc-layout-grid__inner"></div>')
      fieldLines.push('</div>')

      return fieldLines.join('\n')
    }

    createPattern (field) {
      const me = this

      const fieldLines = []

      const fieldName = field.field

      let operations = [
        'begins_with',
        'ends_with',
        'equals',
        'not_equals',
        'contains',
        'not_contains'
      ]

      if (field.operations !== undefined) {
        operations = field.operations
      }

      fieldLines.push('<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-' + field.operation_width + ' mdc-typography--caption" style="margin-bottom: 8px;">')
      fieldLines.push('  <div class="mdc-select mdc-select--outlined" id="' + me.cardId + '_' + fieldName + '__operation" style="width: 100%;">')
      fieldLines.push('    <div class="mdc-select__anchor">')
      fieldLines.push('      <span class="mdc-notched-outline">')
      fieldLines.push('        <span class="mdc-notched-outline__leading"></span>')
      fieldLines.push('        <span class="mdc-notched-outline__notch">')
      fieldLines.push('          <span class="mdc-floating-label">' + me.fetchLocalizedValue(field.operation_label) + '</span>')
      fieldLines.push('        </span>')
      fieldLines.push('        <span class="mdc-notched-outline__trailing"></span>')
      fieldLines.push('      </span>')
      fieldLines.push('      <span class="mdc-select__selected-text-container">')
      fieldLines.push('        <span class="mdc-select__selected-text"></span>')
      fieldLines.push('      </span>')
      fieldLines.push('      <span class="mdc-select__dropdown-icon">')
      fieldLines.push('        <svg class="mdc-select__dropdown-icon-graphic" viewBox="7 10 10 5" focusable="false">')
      fieldLines.push('          <polygon class="mdc-select__dropdown-icon-inactive" stroke="none" fill-rule="evenodd" points="7 10 12 15 17 10"></polygon>')
      fieldLines.push('          <polygon class="mdc-select__dropdown-icon-active" stroke="none" fill-rule="evenodd" points="7 15 12 10 17 15"></polygon>')
      fieldLines.push('        </svg>')
      fieldLines.push('      </span>')
      fieldLines.push('    </div>')

      fieldLines.push('    <div class="mdc-select__menu mdc-menu mdc-menu-surface" role="listbox">')
      fieldLines.push('      <ul class="mdc-list" role="listbox">')

      $.each(operations, function (index, operation) {
        fieldLines.push('          <li class="mdc-list-item" data-value="' + operation + '" role="option">')
        fieldLines.push('            <span class="mdc-list-item__ripple"></span>                ')
        fieldLines.push('            <span class="mdc-list-item__text">' + me.fetchLocalizedConstant(operation) + '<span>')
        fieldLines.push('          </li>')
      })

      fieldLines.push('      </ul>')
      fieldLines.push('    </div>')
      fieldLines.push('  </div>')
      fieldLines.push('</div>')

      fieldLines.push('<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-' + field.content_width + '">')
      fieldLines.push('  <div class="mdc-text-field mdc-text-field--outlined" id="' + me.cardId + '_' + fieldName + '__content_field" style="width: 100%">')
      fieldLines.push('    <input class="mdc-text-field__input"style="width: 100%" id="' + me.cardId + '_' + fieldName + '__content_value" />')
      fieldLines.push('    <div class="mdc-notched-outline">')
      fieldLines.push('      <div class="mdc-notched-outline__leading"></div>')
      fieldLines.push('      <div class="mdc-notched-outline__notch">')
      fieldLines.push('        <label for="' + me.cardId + '_' + field.field + '__content_value" class="mdc-floating-label">' + me.fetchLocalizedValue(field.content_label) + '</label>')
      fieldLines.push('      </div>')
      fieldLines.push('      <div class="mdc-notched-outline__trailing"></div>')
      fieldLines.push('    </div>')
      fieldLines.push('  </div>')
      fieldLines.push('</div>')

      return fieldLines.join('\n')
    }

    addListFieldItem (index, field, itemDefinition, onDelete) {
      const me = this

      const fieldName = field.field

      const listContainerId = me.cardId + '__' + fieldName + '__items'

      const itemIndex = $('#' + listContainerId + ' .' + me.cardId + '__' + fieldName + '__item').length

      const templateLines = []

      templateLines.push('<div class="' + me.cardId + '__' + fieldName + '__item mdc-layout-grid__inner" style="row-gap: 8px; margin-top: 8px;">')

      $.each(field.template, function (index, template) {
        const templateField = jQuery.extend(true, {}, template)

        templateField.original_field = templateField.field

        templateField.field = fieldName + '__' + templateField.field + '__' + itemIndex

        templateLines.push(me.createField(templateField))
      })

      templateLines.push('</div>')

      $('#' + listContainerId).append(templateLines.join('\n'))

      $.each(field.template, function (index, template) {
        const templateField = jQuery.extend(true, {}, template)

        templateField.original_field = templateField.field

        templateField.field = fieldName + '__' + templateField.field + '__' + itemIndex

        itemDefinition[templateField.field] = itemDefinition[templateField.original_field]

        me.initializeField(templateField, itemDefinition, function (newValue) {
          itemDefinition[templateField.original_field] = newValue

          me.sequence.markChanged(me.id)
        }, onDelete)
      })
    }

    addStructureFieldItem (field, itemDefinition) {
      const me = this

      const fieldName = field.field

      const listContainerId = me.cardId + '__' + field.parent_field

      const fieldHtml = me.createField(field)

      $('#' + listContainerId).append(fieldHtml)

      me.initializeField(field, itemDefinition, function (newValue) {
        itemDefinition[fieldName] = newValue

        me.sequence.markChanged(me.id)
      }, null)
    }

    createField (field) {
      const fieldLines = []

      if (field.width === undefined) {
        field.width = 12
      }

      if (field.parent_field !== undefined) {
        field = jQuery.extend(true, {}, field)

        field.original_field = field.field
        field.field = field.parent_field + '__' + field.field
      }

      if (field.type === 'integer') {
        if (field.input === 'text') {
          fieldLines.push(this.createTextField(field))
        }
      } else if (field.type === 'text') {
        if (field.multiline) {
          fieldLines.push(this.createTextArea(field))
        } else {
          fieldLines.push(this.createTextField(field))
        }
      } else if (field.type === 'choice') {
        fieldLines.push(this.createSelect(field))
      } else if (field.type === 'readonly') {
        fieldLines.push(this.createReadOnly(field))
      } else if (field.type === 'card') {
        fieldLines.push(this.createCardReference(field))
      } else if (field.type === 'list') {
        fieldLines.push(this.createList(field))
      } else if (field.type === 'structure') {
        fieldLines.push(this.createStructure(field))
      } else if (field.type === 'pattern') {
        fieldLines.push(this.createPattern(field))
      } else if (field.type === 'image-url') {
        fieldLines.push(this.createImageUrlField(field))
      } else if (field.type === 'sound-url') {
        fieldLines.push(this.createSoundUrlField(field))
      } else {
        // TODO: Unknown Card Type
      }

      return fieldLines.join('\n')
    }

    initializeField (field, definition, onUpdate, onDelete) {
      const me = this

      let fieldName = field.field

      if (field.parent_field !== undefined) {
        fieldName = field.parent_field + '__' + fieldName
      }

      if (field.type === 'integer') {
        const fieldWidget = mdc.textField.MDCTextField.attachTo(document.getElementById(me.cardId + '_' + fieldName + '_field'))

        if (definition[field.field] === undefined && definition[field.default] !== undefined) {
          definition[field.field] = field.default
        }

        if (definition[field.field] !== undefined) {
          fieldWidget.value = definition[field.field]
        }

        $('#' + me.cardId + '_' + fieldName + '_value').on('change keyup paste', function () {
          const value = $('#' + me.cardId + '_' + fieldName + '_value').val()

          me.sequence.markChanged(me.id)

          onUpdate(parseInt(value))
        })
      } else if (field.type === 'image-url') {
        const fieldWidget = mdc.textField.MDCTextField.attachTo(document.getElementById(me.cardId + '_' + fieldName + '_field'))

        if (definition[field.field] === undefined && definition[field.default] !== undefined) {
          definition[field.field] = field.default
        }

        if (definition[field.field] !== undefined) {
          fieldWidget.value = definition[field.field]

          $('#' + me.cardId + '_' + field.field + '_preview').attr('src', fieldWidget.value)
        }

        $('#' + me.cardId + '_' + fieldName + '_value').on('change keyup paste', function () {
          const value = $('#' + me.cardId + '_' + fieldName + '_value').val()

          $('#' + me.cardId + '_' + field.field + '_preview').attr('src', value)

          me.sequence.markChanged(me.id)

          onUpdate(value)
        })
      } else if (field.type === 'sound-url') {
        const fieldWidget = mdc.textField.MDCTextField.attachTo(document.getElementById(me.cardId + '_' + fieldName + '_field'))

        if (definition[field.field] === undefined && definition[field.default] !== undefined) {
          definition[field.field] = field.default
        }

        if (definition[field.field] !== undefined) {
          fieldWidget.value = definition[field.field]

          $('#' + me.cardId + '_' + field.field + '_preview').attr('src', fieldWidget.value)
        }

        $('#' + me.cardId + '_' + fieldName + '_value').on('change keyup paste', function () {
          const value = $('#' + me.cardId + '_' + fieldName + '_value').val()

          $('#' + me.cardId + '_' + field.field + '_preview').attr('src', value)

          me.sequence.markChanged(me.id)

          onUpdate(value)
        })
      } else if (field.type === 'choice') {
        if (Array.isArray(field.options)) {
          const choiceField = mdc.select.MDCSelect.attachTo(document.getElementById(me.cardId + '_' + fieldName))

          if (definition[field.field] !== undefined) {
            choiceField.value = definition[field.field]
          }

          choiceField.listen('MDCSelect:change', function () {
            onUpdate(choiceField.value)
          })

          me.sequence.markChanged(me.id)
        } else {
          // Fetch values and update structure and re-render
          $.get(field.options, function (data) {
            field.options = data

            const optionLines = []

            $.each(data, function (index, option) {
              optionLines.push('          <li class="mdc-list-item" data-value="' + option.value + '" role="option">')
              optionLines.push('            <span class="mdc-list-item__ripple"></span>                ')
              optionLines.push('            <span class="mdc-list-item__text">' + me.fetchLocalizedValue(option.label) + '<span>')
              optionLines.push('          </li>')
            })

            $('#' + me.cardId + '_' + fieldName + ' ul.mdc-list').html(optionLines.join(''))

            me.initializeField(field, definition, onUpdate, null)
          })
        }
      } else if (field.type === 'text') {
        const fieldWidget = mdc.textField.MDCTextField.attachTo(document.getElementById(me.cardId + '_' + fieldName + '_field'))

        if (definition[field.field] !== undefined) {
          fieldWidget.value = definition[field.field]
        }

        $('#' + me.cardId + '_' + fieldName + '_value').on('change keyup paste', function () {
          const value = fieldWidget.value

          me.sequence.markChanged(me.id)

          onUpdate(value)
        })
      } else if (field.type === 'readonly') {
        // Do nothing...
      } else if (field.type === 'card') {
        $('#' + me.cardId + '_' + fieldName + '_edit').on('click', function () {
          me.sequence.refreshDestinationMenu(function (destination) {
            window.dialogBuilder.chooseDestinationDialog.close()

            onUpdate(destination)

            me.sequence.markChanged(me.id)
            me.sequence.loadNode(me.definition)
          })

          window.dialogBuilder.chooseDestinationDialog.open()
        })

        $('#' + me.cardId + '_' + fieldName + '_goto').on('click', function () {
          const destinationNodes = me.destinationNodes(me.sequence)

          for (let i = 0; i < destinationNodes.length; i++) {
            const destinationNode = destinationNodes[i]

            if (definition[field.field] !== undefined && definition[field.field].endsWith(destinationNode.id)) {
              $("[data-node-id='" + destinationNode.id + "']").css('background-color', '#ffffff')
            } else {
              $("[data-node-id='" + destinationNode.id + "']").css('background-color', '#e0e0e0')
            }
          }
        })

        if (definition[field.field] === null || definition[field.field] === undefined || definition[field.field] === '') {
          $('#' + me.cardId + '_' + fieldName + '_goto').hide()
        } else {
          $('#' + me.cardId + '_' + fieldName + '_goto').show()
        }
      } else if (field.type === 'list') {
        $('#' + me.cardId + '__' + fieldName + '__add_item').on('click', function () {
          definition[field.field].push({})

          me.sequence.loadNode(me.definition)
          me.sequence.markChanged(me.id)
        })

        const fieldSequence = definition[field.field]

        $.each(definition[field.field], function (index, item) {
          me.addListFieldItem(index, field, item, function () {
            fieldSequence.splice(index, 1)

            me.sequence.loadNode(me.definition)
            me.sequence.markChanged(me.id)
          })
        })
      } else if (field.type === 'structure') {
        $.each(field.fields, function (index, itemField) {
          itemField.parent_field = field.field

          me.addStructureFieldItem(itemField, definition[field.field])
        })
      } else if (field.type === 'pattern') {
        const operationField = mdc.select.MDCSelect.attachTo(document.getElementById(me.cardId + '_' + fieldName + '__operation'))
        const contentField = mdc.textField.MDCTextField.attachTo(document.getElementById(me.cardId + '_' + fieldName + '__content_field'))

        let actualFieldName = field.field

        if (field.original_field !== undefined) {
          actualFieldName = field.original_field
        }

        if (definition[actualFieldName] !== undefined) {
          contentField.value = definition[actualFieldName]
          me.updatePatternView(contentField.value, operationField, contentField)
        }

        let lastValue = 'delete-me'

        operationField.listen('MDCSelect:change', function () {
          me.updatePatternValue(operationField.value, contentField.value, onUpdate)

          me.updatePatternView(definition[actualFieldName], operationField, contentField)
        })

        $('#' + me.cardId + '_' + fieldName + '__content_value').on('change keyup paste', function (event) {
          if (event.keyCode === 46 || event.keyCode === 8) {
            if (lastValue === '') {
              lastValue = null
            } else if (lastValue === null) {
              if (onDelete !== null) {
                onDelete()
              }
            } else {
              lastValue = $('#' + me.cardId + '_' + fieldName + '__content_value').val()
            }
          } else {
            lastValue = $('#' + me.cardId + '_' + fieldName + '__content_value').val()

            me.updatePatternValue(operationField.value, lastValue, onUpdate)

            me.updatePatternView(definition[actualFieldName], operationField, contentField)
          }
        })
      } else {
        // TODO: Unknown Card Type
      }
    }

    updatePatternView (pattern, operationField, patternField) {
      const oldOperationValue = operationField.value
      let newOperationValue = oldOperationValue

      const oldPatternValue = patternField.value
      let newPatternValue = oldPatternValue

      if (pattern === '') {
        newOperationValue = 'contains'
        newPatternValue = ''
      } else if (pattern.startsWith('^(?!') && pattern.endsWith(')$')) {
        newOperationValue = 'not_equals'
        newPatternValue = pattern.replace('^(?!', '').replace(')$', '')
      } else if (pattern.startsWith('(?!') && pattern.endsWith(')')) {
        newOperationValue = 'not_contains'
        newPatternValue = pattern.replace('(?!', '').replace(')', '')
      } else if (pattern.startsWith('(?!') && pattern.endsWith(')')) {
        newOperationValue = 'not_contains'
        newPatternValue = pattern.replace('(?!', '').replace(')', '')
      } else if (pattern.startsWith('^') && pattern.endsWith('$')) {
        newOperationValue = 'equals'
        newPatternValue = pattern.replace('^', '').replace('$', '')
      } else if (pattern.startsWith('^')) {
        newOperationValue = 'begins_with'
        newPatternValue = pattern.replace('^', '')
      } else if (pattern.endsWith('$')) {
        newOperationValue = 'ends_with'
        newPatternValue = pattern.replace('$', '')
      } else {
        newOperationValue = 'contains'
        newPatternValue = pattern
      }

      if (newOperationValue !== oldOperationValue) {
        operationField.value = newOperationValue
      }

      if (newPatternValue !== oldPatternValue) {
        patternField.value = newPatternValue
      }
    };

    updatePatternValue (operation, pattern, onUpdated) {
      let patternValue = ''

      if (pattern === '') {
        patternValue = ''
      } else if (operation === 'begins_with') {
        patternValue = '^' + pattern
      } else if (operation === 'ends_with') {
        patternValue = pattern + '$'
      } else if (operation === 'equals') {
        patternValue = '^' + pattern + '$'
      } else if (operation === 'not_contains') {
        patternValue = '(?!' + pattern + ')'
      } else if (operation === 'not_equals') {
        patternValue = '^(?!' + pattern + ')$'
      } else {
        patternValue = pattern
      }

      onUpdated(patternValue)
    };

    humanizePattern (pattern, action) {
      if (action === undefined || action === '?' || action === null || action === '') {
        action = '?'
      }

      action = this.lookupCardName(action)

      if (pattern.startsWith('^[') && pattern.endsWith(']')) {
        const matches = []

        for (let i = 2; i < pattern.length - 1; i++) {
          matches.push('' + pattern[i])
        }

        let humanized = ''

        for (let i = 0; i < matches.length; i++) {
          if (humanized.length > 0) {
            if (i < matches.length - 1) {
              humanized += ', '
            } else if (matches.length > 2) {
              humanized += ', or '
            } else {
              humanized += ' or '
            }
          }

          humanized += '"' + matches[i] + '"'
        }

        return '[TRANSLATE] If response starts with ' + humanized + ', go to <em>' + action + '</em>.'
      } else if (pattern === '.*') {
        return '[TRANSLATE] If response is anything, go to <em>' + action + '</em>.'
      } else if (pattern.startsWith('^') && pattern.endsWith('$')) {
        return '[TRANSLATE] If response is "' + pattern + '", go to <em>' + action + '</em>.'
      }

      return '[TRANSLATE] If responses matches "' + pattern + '", go to <em>' + action + '</em>.'
    }

    editFields () {
      const me = this

      const fields = this.cardFields()

      const fieldLines = []

      $.each(fields, function (index, field) {
        fieldLines.push(me.createField(field))
      })

      return fieldLines.join('\n')
    }

    initializeFields () {
      const fields = this.cardFields()

      const me = this

      $.each(fields, function (index, field) {
        const onUpdate = function (newValue) {
          me.definition[field.field] = newValue

          me.sequence.markChanged(me.id)
        }

        if (field.type === 'integer') {
          me.initializeField(field, me.definition, onUpdate, null)
        } else if (field.type === 'image-url') {
          me.initializeField(field, me.definition, onUpdate, null)
        } else if (field.type === 'sound-url') {
          me.initializeField(field, me.definition, onUpdate, null)
        } else if (field.type === 'choice') {
          me.initializeField(field, me.definition, onUpdate, null)
        } else if (field.type === 'text') {
          me.initializeField(field, me.definition, onUpdate, null)
        } else if (field.type === 'readonly') {
          // Do nothing...
        } else if (field.type === 'card') {
          me.initializeField(field, me.definition, onUpdate, null)
        } else if (field.type === 'list') {
          me.initializeField(field, me.definition, function () {}, null)
        } else if (field.type === 'structure') {
          me.initializeField(field, me.definition, function () {}, null)
        } else if (field.type === 'pattern') {
          me.initializeField(field, me.definition, onUpdate, null)
        } else {
          // TODO: Unknown Card Type
        }
      })

      window.setTimeout(me.sequence.initializeDestinationMenu, 250)

      if (window.dialogBuilder.helpToggle.selected) {
        $('.hive_mechanic_help').hide()
        $('.hive_mechanic_help_filler').show()
      } else {
        $('.hive_mechanic_help').show()
        $('.hive_mechanic_help_filler').hide()
      }
    }

    editBody () {
      return this.editFields()

      // var htmlString  = '<div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12">';
      //     htmlString += this.viewBody();
      //     htmlString += '</div>';
      //
      // return htmlString
    }

    advancedEditBody () {
      let htmlString = '<div class="mdc-layout-grid" style="margin: 0; padding: 0;">'
      htmlString += '  <div class="mdc-layout-grid__inner" style="row-gap: 16px;">'
      htmlString += '    <div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12">'
      htmlString += '      <div class="mdc-text-field mdc-text-field--outlined" id="' + this.cardId + '_advanced_identifier" style="width: 100%">'
      htmlString += '        <input class="mdc-text-field__input" type="text" id="' + this.cardId + '_advanced_identifier_value">'
      htmlString += '        <div class="mdc-notched-outline">'
      htmlString += '          <div class="mdc-notched-outline__leading"></div>'
      htmlString += '          <div class="mdc-notched-outline__notch">'
      htmlString += '            <label for="' + this.cardId + '_advanced_identifier_value" class="mdc-floating-label">Card Identifier</label>'
      htmlString += '          </div>'
      htmlString += '          <div class="mdc-notched-outline__trailing"></div>'
      htmlString += '        </div>'
      htmlString += '      </div>'
      htmlString += '      <div class="mdc-typography--caption" id="' + this.cardId + '_activity-identifier-warning" style="color: #B71C1C;">Invalid characters or format detected. Please use only alphanumeric characters and dashes.</div>'
      htmlString += '    </div>'

      htmlString += '    <div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12">'
      htmlString += '      <div class="mdc-text-field mdc-text-field--textarea mdc-text-field--outlined" id="' + this.cardId + '_advanced_comment_field" style="width: 100%">'
      htmlString += '        <div class="mdc-notched-outline">'
      htmlString += '          <div class="mdc-notched-outline__leading"></div>'
      htmlString += '          <div class="mdc-notched-outline__notch">'
      htmlString += '            <label for="' + this.cardId + '_advanced_comment_value" class="mdc-floating-label">Comment</label>'
      htmlString += '          </div>'
      htmlString += '          <div class="mdc-notched-outline__trailing"></div>'
      htmlString += '        </div>'
      htmlString += '        <textarea class="mdc-text-field__input" rows="4" style="width: 100%" id="' + this.cardId + '_advanced_comment_value"></textarea>'
      htmlString += '      </div>'
      htmlString += '    </div>'
      htmlString += '    <div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-12 mdc-typography--caption">'
      htmlString += '      (<a href="https://www.markdownguide.org/cheat-sheet/" target="_blank">Markdown Cheat Sheet</a>)'
      htmlString += '    </div>'

      htmlString += '  </div>'
      htmlString += '</div>'

      return htmlString
    }

    showComment () {
      return true
    }

    viewHtml () {
      let htmlString = '<div class="mdc-card" id="' + this.cardId + '" style="' + this.style() + '"  data-node-id="' + this.id + '">'
      htmlString += '  <h6 class="mdc-typography--headline6" style="margin: 16px; margin-bottom: 0;"><span style="float: right">' + this.cardIcon() + '</span>' + this.cardName() + '</h6>'
      htmlString += this.viewBody()
      htmlString += '</div>'

      return htmlString
    }

    viewBody () {
      return '<div class="mdc-typography--body1" style="margin: 16px;"><pre>' + JSON.stringify(this.definition, null, 2) + '</pre></div>'
    }

    style () {
      return 'background-color: #ffffff; margin-bottom: 10px;'
    }

    readOnlyStyle () {
      return ''
    }

    destinationNodes (sequence) {
      return []
    }

    setDefaultDestination (originalId) {
      // replace nodes in def.
    }

    sourceNodes (sequence) {
      const sources = []
      const includedIds = []

      for (let i = 0; i < window.dialogBuilder.definition.sequences.length; i++) {
        const sequenceDef = window.dialogBuilder.definition.sequences[i]

        for (let j = 0; j < sequenceDef.items.length; j++) {
          const item = sequenceDef.items[j]

          const node = this.sequence.resolveNode(sequenceDef.id + '#' + item.id)

          if (node !== null) {
            const destinations = node.destinationNodes(sequence)

            let isSource = false

            for (let k = 0; k < destinations.length && isSource === false; k++) {
              const destination = destinations[k]

              if (this.sequence.definition.id === destination.sequence.definition.id && this.id === destination.id) {
                isSource = true
              }
            }

            if (isSource && includedIds.indexOf(node.id) === -1) {
              sources.push(node)
              includedIds.push(node.id)
            }
          }
        }
      }

      return sources
    }

    onClick (callback) {
      $('#' + this.cardId).click(function (eventObj) {
        callback()
      })
    }

    lookupCardName (cardId) {
      if (cardId !== '') {
        const node = this.sequence.resolveNode(cardId)

        if (node !== null) {
          cardId = node.cardName()
        }
      }

      return cardId
    }

    static cardIdExists (cardId, sequence) {
      if (cardId !== '') {
        const node = sequence.resolveNode(cardId)

        if (node !== null) {
          return true
        }
      }

      return false
    }

    static createCard (definition, sequence) {
      if (window.dialogBuilder.cardMapping !== undefined) {
        const classObj = window.dialogBuilder.cardMapping[definition.type]

        if (classObj !== undefined) {
          return new classObj(definition, sequence) // eslint-disable-line new-cap
        }
      }

      return new Node(definition, sequence)
    }

    static canCreateCard (definition, sequence) {
      if (window.dialogBuilder.cardMapping !== undefined) {
        const classObj = window.dialogBuilder.cardMapping[definition.type]

        return (classObj !== undefined)
      }

      return false
    }

    static registerCard (name, classObj) {
      if (window.dialogBuilder.cardMapping === undefined) {
        window.dialogBuilder.cardMapping = {}
      }

      window.dialogBuilder.cardMapping[name] = classObj
    }

    static uuidv4 () {
      return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        const r = Math.random() * 16 | 0; const v = c === 'x' ? r : (r & 0x3 | 0x8)
        return v.toString(16)
      })
    }

    static newNodeId (cardName, sequence) {
      const newIdBase = Node.slugify(cardName)

      if (Node.cardIdExists(newIdBase, sequence) === false) {
        return newIdBase
      }

      let index = 1

      let newId = newIdBase + '-' + index

      while (Node.cardIdExists(newId, sequence)) {
        index += 1

        newId = newIdBase + '-' + index
      }

      return newId
    }

    static slugify (text) {
      let cleaned = text.split('').map(function (character) {
        if (/^[a-z0-9]+$/i.test(character)) {
          return character
        } else {
          return '-'
        }
      }).join('')

      while (cleaned.includes('--')) {
        cleaned = cleaned.replace('--', '-')
      }

      return slugifyExt(cleaned, {
        remove: /[*+~.()'"!?:@]/g,
        trim: true
      })
    }

    static cardName () {
      return 'Node'
    }
  }

  return Node
})
