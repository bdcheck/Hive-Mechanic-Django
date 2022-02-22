// Derived from https://github.com/sheppard/python-requirejs

const context = this

window = {
  dialogBuilder: {}
}

const console = {
  history: [],
  log: function () {
    console.history.push([].map.call(arguments, function (cell) {
      return '' + cell
    }).join(' '))
  },
  get: function (key) {
    return console[key]
  }
}

const define = function (modules, callback) {
  const newModules = []

  for (var i = 0; i < modules.length; i++) {
    if (modules[i] === 'cards/node') {
      modules[i] = 'Node'
    } else if (modules[i] === 'slugify') {
      modules[i] = 'slugifyExt'
    }

    if (context[modules[i]] !== undefined) {
      newModules.push(context[modules[i]])
    } else {
      newModules.push('?')
    }
  }

  const module = callback.apply(null, newModules)

  if (module !== undefined) {
    if (module.name !== undefined) {
      context[module.name] = module
    } else if (module.loadSequence !== undefined) {
      context.sequence = module
    }
  }
}
