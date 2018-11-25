#
# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import boto3
import time
import logging
import json
import pprint
import os
import bibot_config as bibot
import bibot_userexits as userexits

#
# See additional configuration parameters at bottom 
#

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)



def get_slot_values(slot_values, intent_request):
    if slot_values is None:
        slot_values = {key: None for key in bibot.SLOT_CONFIG}
    
    slots = intent_request['currentIntent']['slots']

    for key,config in bibot.SLOT_CONFIG.items():
        slot_values[key] = slots.get(key)
        logger.debug('<<BIBot>> retrieving slot value for %s = %s', key, slot_values[key])
        if slot_values[key]:
            if config.get('type', bibot.ORIGINAL_VALUE) == bibot.TOP_RESOLUTION:
                # get the resolved slot name of what the user said/typed
                if len(intent_request['currentIntent']['slotDetails'][key]['resolutions']) > 0:
                    slot_values[key] = intent_request['currentIntent']['slotDetails'][key]['resolutions'][0]['value']
                else:
                    errorMsg = bibot.SLOT_CONFIG[key].get('error', 'Sorry, I don\'t understand "{}".')
                    raise bibot.SlotError(errorMsg.format(slots.get(key)))
                
            slot_values[key] = userexits.post_process_slot_value(key, slot_values[key])
    
    return slot_values


def get_remembered_slot_values(slot_values, session_attributes):
    logger.debug('<<BIBot>> get_remembered_slot_values() - session_attributes: %s', session_attributes)

    str = session_attributes.get('rememberedSlots')
    remembered_slot_values = json.loads(str) if str is not None else {key: None for key in bibot.SLOT_CONFIG}
    
    if slot_values is None:
        slot_values = {key: None for key in bibot.SLOT_CONFIG}
    
    logger.debug('<<BIBot>> get_remembered_slot_values() - slot_values: %s', slot_values)
    logger.debug('<<BIBot>> get_remembered_slot_values() - remembered_slot_values: %s', remembered_slot_values)
    for key,config in bibot.SLOT_CONFIG.items():
        if config.get('remember', False):
            logger.debug('<<BIBot>> get_remembered_slot_values() - slot_values[%s] = %s', key, slot_values.get(key))
            logger.debug('<<BIBot>> get_remembered_slot_values() - remembered_slot_values[%s] = %s', key, remembered_slot_values.get(key))
            if slot_values.get(key) is None:
                slot_values[key] = remembered_slot_values.get(key)
                
    return slot_values


def remember_slot_values(slot_values, session_attributes):
    if slot_values is None:
        slot_values = {key: None for key,config in bibot.SLOT_CONFIG.items() if config['remember']}
    session_attributes['rememberedSlots'] = json.dumps(slot_values)
    logger.debug('<<BIBot>> Storing updated slot values: %s', slot_values)           
    return slot_values


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }
    
    logger.debug('<<BIBot>> "Lambda fulfillment function response = \n' + pprint.pformat(response, indent=4)) 

    return response


def increment_counter(session_attributes, counter):
    counter_value = session_attributes.get(counter, '0')

    if counter_value: count = int(counter_value) + 1
    else: count = 1
    
    session_attributes[counter] = count

    return count


