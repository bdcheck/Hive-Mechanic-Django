# Incoming globals: definition, response, last_transition, previous_state

# Definition Example
#      {
#        "message": "Are you ready to proceed? (Respond Y to continue.)",
#        "next": "process-consent",
#        "type": "send-message",
#        "id": "request-consent-2",
#        "name": "Request Consent"
#      },
#
# Must populate:
#   result = {
#       'details': {},
#       'actions': [],
#       'next_id': None
#   }

result['details'] = {
    'message': definition['message']
}

result['actions'] = []

result['next_id'] = definition['next']

if ('#' in result['next_id']) is False:
    result['next_id'] = definition['sequence_id'] + '#' + result['next_id']
