window.dialogBuilder.definition = {{ definition|safe }};

var nodes = [];
var edges = [];

for (var i = 0; i < window.dialogBuilder.definition.sequences.length; i++) {
    let sequenceDef = window.dialogBuilder.definition.sequences[i];
    
    var gameSequence = sequence.loadSequence(sequenceDef);
    
    for (var j = 0; j < sequenceDef.items.length; j++) {
        let itemDef = sequenceDef.items[j];
        
        let cardNode = Node.createCard(itemDef, gameSequence);
        
        var nodeId = cardNode.id;
        
        if (nodeId.indexOf('#') == -1) {
            nodeId = sequenceDef['id'] + "#" + nodeId
        }
        
        nodes.push({
            'id': nodeId,
            'name': cardNode.cardName()
        });
        
        var destNodes = cardNode.destinationNodes(gameSequence);
        
        for (var k = 0; k < destNodes.length; k++) {
            let destNode = destNodes[k];
            
            var destId = destNode.id;
            
            if (destId.indexOf('#') == -1) {
                destId = destNode.sequence.identifier() + "#" + destId
            }
            
            edges.push({
                'id': nodeId + '__' + destId,
                'source': nodeId,
                'target': destId
            });
        }
    }
}

var cyto = [];

for (var i = 0; i < nodes.length; i++) {
	let node = nodes[i];
	
	cyto.push({
		'data': node,
		'group': 'nodes'
	});
}

for (var i = 0; i < edges.length; i++) {
	let edge = edges[i];
	
	cyto.push({
		'data': edge,
		'group': 'edges'
	});
}

JSON.stringify(cyto, null, 2);
