var modules = ["material", 'cards/node', 'cards/send_message', 'jquery', ];

define(modules, function (mdc, Node, SendMessageNode) {
    class SendPremadeWelcomeMessageNode extends SendMessageNode {
        constructor(definition, sequence) {
            super(definition, sequence);

            this.messageId = Node.uuidv4();
            
            this.definition['message'] = "Welcome to the game: " + this.definition['message'];
        }

		cardType() {
			return 'Send Premade Welcome Message';
		}

		static cardName() {
			return 'Send Premade Welcome Message';
		}
    }

    Node.registerCard('send-premade-welcome-message', SendPremadeWelcomeMessageNode);
});