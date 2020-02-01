# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

# from django.db import models

def process_incoming(integration, payload):
    issues = []
    
    print('PAYLOAD: ' + str(payload))

    if 'actions' in payload:
        actions = json.loads(payload['actions'])
        
        for action in actions:
            issue = execute_action(integration, action)
            
            if issue is not None:
                issues.append(issue)
    else: 
        issues.append('No "actions" element found in HTTP payload.')
        
    return issues

def execute_action(integration, action):
    action_type = action['action']
    
    if action_type == 'check_server':
        return None 
        
    return 'No action found for "' + action_type + '".'
