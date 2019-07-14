var modules = ["material", 'cards/node', 'jquery'];

if (window.dialogBuilder.cards != undefined) {
    var cards = window.dialogBuilder.cards;
    
    for (var i = 0; i < cards.length; i++) {
        modules.push(cards[i]);
    }
}

define(modules, function (mdc, Node) {
    class Sequence {
        constructor(definition) {
            this.definition = definition;
            this.changeListeners = [];
            
            console.log(definition);
        }
        
        allActions() {
            var actions = [];
            
            for (var i = 0; i < this.definition["items"].length; i++) {
                var item = this.definition["items"][i];
                
                var action = {"id": item["id"]};
                
                if (item["name"] != undefined) {
                    action["name"] = item["name"];
                } else {
                    action["name"] = item["id"];
                }
                
                actions.push(action);
            }
            
            return actions;
        }
        
        name() {
            return this.definition['name'];
        }

        selectInitialNode() {
            $("#sequence_breadcrumbs").html(this.name());
            
            this.loadNode(this.definition.items[0]);
        }
        
        loadNode(definition) {
            var me = this;
            
            var node = Node.createCard(definition, this);
            
            var current = $("#builder_current_node");
            
            var html = node.editHtml();
            
            current.html(html);
            node.initialize();
            
            if ($("#sequence_breadcrumbs").children("#breadcrumb-" + node.id).length > 0) {
                var match = $("#sequence_breadcrumbs").children("#breadcrumb-" + node.id);
                var last = $("#sequence_breadcrumbs").children().last();
                
                while (match.attr("id") != last.attr("id")) {

                    last.remove();

                    last = $("#sequence_breadcrumbs").children().last();
                }
            } else {
                var chevron = '<i class="material-icons" style="font-size: 0.75rem;">chevron_right</i>';
                var breadcrumb = '<a id="breadcrumb-' + node.id + '" href="#">' + node.cardName() + '</a>';

                $("#sequence_breadcrumbs").append(chevron + breadcrumb);

                $("#breadcrumb-" + node.id).click(function(eventObj) {
                    eventObj.preventDefault();
                
                    me.loadNode(definition);
            
                    return false;
                })
            }
            
            var destinations = $("#builder_next_nodes");
            
            var destinationNodes = node.destinationNodes(this);
            
            var destinationHtml = '';

            for (var i = 0; i < destinationNodes.length; i++) {
                destinationHtml += destinationNodes[i].viewHtml();
            }

            destinations.html(destinationHtml);
            
            for (var i = 0; i < destinationNodes.length; i++) {
                const destinationNode = destinationNodes[i];
                
            	console.log(destinationNode);
                
                $("#" + destinationNode["cardId"]).css("background-color", "#E0E0E0");
            
                destinationNode.onClick(function() {
                    me.loadNode(destinationNode.definition);    
                });
            }

            var sources = $("#builder_source_nodes");
            
            var sourceNodes = node.sourceNodes(this);
            
            var sourceHtml = '';

            for (var i = 0; i < sourceNodes.length; i++) {
                sourceHtml += sourceNodes[i].viewHtml();
            }

            sources.html(sourceHtml);

            for (var i = 0; i < sourceNodes.length; i++) {
                const sourceNode = sourceNodes[i];
                
                sourceNode.onClick(function() {
                    me.loadNode(sourceNode.definition);    
                });
            }
        }
        
        checkCorrectness() {
            console.log("Checking correctness...");
            var items = this.definition.items;
            
            for (var i = 0; i < items.length; i++) {
                var item = items[i];
                
                if (Node.canCreateCard(item, this) == false) {
                    console.log("Cannot create node for item:");
                    console.log(item);
                }
            }
            
            console.log("Check complete.");
        }
        
        addChangeListener(changeFunction) {
            this.changeListeners.push(changeFunction);
        }
        
        removeChangeListener(changeFunction) {
            var index = this.changeListeners.indexOf(changeFunction);
            
            if (index >= 0) {
                this.changeListeners.splice(index, 1);
            }
        }
        
        markChanged(changedId) {
            for (var i = 0; i < this.changeListeners.length; i++) {
                this.changeListeners[i](changedId);
            }
        }

        chooseDestinationSelect(cardId) {
            var body = '';
            body += '<div class="mdc-select mdc-select--outlined" id="' + cardId + '_destination" style="width: 100%; margin-top: 8px;">';
            body += '  <i class="mdc-select__dropdown-icon"></i>';
            body += '    <select class="mdc-select__native-control" id="">';
            body += '      <option value="" disabled selected></option>';
            
            var actions = this.allActions();
            
            for (var i = 0; i < actions.length; i++) {
                var action = actions[i];

                body += '      <option value="' + action['id'] + '">' + action['name'] + '</option>';
            }

            body += '      <option value="add_card">Add&#8230;</option>';
            body += '    </select>';
            body += '  <div class="mdc-notched-outline">';
            body += '    <div class="mdc-notched-outline__leading"></div>';
            body += '    <div class="mdc-notched-outline__notch">';
            body += '      <label class="mdc-floating-label">Destination</label>';
            body += '    </div>';
            body += '    <div class="mdc-notched-outline__trailing"></div>';
            body += '  </div>';
            body += '</div>';
            
            return body;
        }

        refreshDestinationSelect(cardId) {
            var selectId = '#' + cardId + '_destination select';
            
            $(selectId).empty();
            
            $(selectId).append('<option value="" disabled selected></option>');

            var actions = this.allActions();

            for (var i = 0; i < actions.length; i++) {
                var action = actions[i];

                $(selectId).append('<option value="' + action['id'] + '">' + action['name'] + '</option>');
            }
            
            $(selectId).append('<option value="add_card">Add&#8230;</option>');
        }

        addCard(cardId, callback) {
        	$("#add-card-name-value").val("");
            $("#add-card-select-widget").val("");
            
            var me = this;
            
            var listener = {
				handleEvent: function (event) {
					if (event.detail.action == "add_card") {
						var cardName = $("#add-card-name-value").val();
						var cardType = $("#add-card-select-widget").val();

						console.log('CARD TYPE');
						console.log(cardType);
					
						var cardClass = window.dialogBuilder.cardMapping[cardType];
					
						var cardDef = cardClass.createCard(cardName);
					
						if (me.definition["items"].includes(cardDef) == false) {
							me.definition["items"].push(cardDef);
						}   

						me.refreshDestinationSelect(cardId);

						$('#' + cardId + '_destination select').val(cardDef["id"]);

						callback(cardDef["id"]);
					
						window.dialogBuilder.addCardDialog.unlisten('MDCDialog:closed', this);
				   }
				}
			};
            
            window.dialogBuilder.addCardDialog.listen('MDCDialog:closed', listener);

            window.dialogBuilder.addCardDialog.open();
        }
        
/*        updateId(oldId, newId) {
        	for (var i = 0; i < this.definition["items"].length; i++) {
        		var item = this.definition["items"][i];
        		
        		if (item["id"] == oldId) {
        			item["id"] = newId;
        			
        			break;
        		}
        		
        		for (allActions)
        		            var node = Node.createCard(definition, this);

        		// item.updateDestination(oldId, newId);
        	}
        }
*/
    }

    var sequence = {}
    
    sequence.loadSequence = function(definition) {
        var sequence = new Sequence(definition);
        
        sequence.checkCorrectness();
        
        return sequence;
    }
    
    return sequence;
});
