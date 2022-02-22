/* global requirejs */

requirejs.config({
  shim: {
    jquery: {
      exports: '$'
    },
    cookie: {
      exports: 'Cookies'
    },
    dagre: {
      exports: 'dagre'
    },
    bootstrap: {
      deps: ['jquery']
    }
  },
  baseUrl: '/static/builder-js/js/app',
  paths: {
    app: '/static/builder-js/js/app',
    material: '/static/builder-js/vendor/material-components-web-11.0.0',
    jquery: '/static/builder-js/vendor/jquery-3.4.0.min',
    cookie: '/static/builder-js/vendor/js.cookie',
    cytoscape: '/static/builder-js/vendor/cytoscape-3.19.1.min',
    'cytoscape-dagre': '/static/builder-js/vendor/cytoscape-dagre',
    dagre: '/static/builder-js/vendor/dagre.min'
  }
})

requirejs(['material', 'cookie', 'jquery', 'cytoscape', 'cytoscape-dagre'], function (mdc, Cookies, Node, cytoscape, cytoscapeDagre) {
  const csrftoken = $('[name=csrfmiddlewaretoken]').val()

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

  $('#cytoscape_canvas').height($(window).height())

  cytoscapeDagre(cytoscape) // register extension

  const cy = cytoscape({
    container: $(window.visualizationOptions.container),
    elements: window.visualizationOptions.source,
    layout: {
      name: 'dagre'
    },
    style: [{
      selector: 'node',
      style: {
        label: 'data(name)',
        'label-type': 'data(hive_node_type)',
        'font-size': '10pt',
        'text-halign': 'center',
        'text-valign': 'center',
        'compound-sizing-wrt-labels': 'include'
      }
    }, {
      selector: 'edge',
      style: {
        'curve-style': 'bezier',
        'control-point-distance': 64,
        'target-arrow-shape': 'triangle',
        label: 'data(hive_edge_description)',
        'font-size': '8pt',
        'text-rotation': 'autorotate',
        color: '#fff',
        'text-background-color': '#000',
        'text-background-opacity': 1,
        'text-background-shape': 'round-rectangle',
        'text-background-padding': '1px'
      }
    }]
  })

  cy.center()
})
