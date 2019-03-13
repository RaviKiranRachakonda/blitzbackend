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

# Gremlin imports.
from __future__ import print_function  # Python 2/3 compatibility
from project-dir.gremlin_python import statics
from project-dir.gremlin_python.structure.graph import Graph
from project-dir.gremlin_python.process.graph_traversal import __
from project-dir.gremlin_python.process.strategies import *
from project-dir.gremlin_python.driver.driver_remote_connection import DriverRemoteConnection


import logging
import json
import bibot_helpers as helpers

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


# TODO:  Make this URL configurable.
graphConnection = DriverRemoteConnection('ws://neptunedbcluster-cxu2i0c92g94.cluster-cryiyy1ygf5o.us-east-1.neptune.amazonaws.com:8182/gremlin','g')

def get_slots(intent_request):
    return intent_request['currentIntent']['slots']



def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


def category(intent_request):

    categoryName = get_slots(intent_request)["CategorySlot"]
    source = intent_request['invocationSource']
    product_name = 'Cisco NCS 4201'
    graph = Graph()
    
    g = graph.traversal().withRemote(graphConnection)

    print(g.V().limit(2).toList())

    output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    output_session_attributes['Product'] = product_name
    output_session_attributes['Category'] = categoryName
    output_session_attributes['Type'] = 'SYSTEM_SPEC'

    if source == 'DialogCodeHook':
      return delegate(output_session_attributes, get_slots(intent_request))


    # Selected Category, Return a dummy Cisco Product.
    # This will need to hook up with Neptune.
    return close(output_session_attributes,
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': 'Proceeding with category = {}, product = {}'.format(categoryName, product_name)
                 })



def lambda_handler(event, context):
    logger.debug('<<BIBot>> Lex event info = ' + json.dumps(event))

    session_attributes = event['sessionAttributes']
    logger.debug('<<BIBot>> lambda_handler: session_attributes = ' + json.dumps(session_attributes))

    return hello_intent_handler(event, session_attributes)


def hello_intent_handler(intent_request, session_attributes):
    session_attributes['resetCount'] = '0'
    session_attributes['finishedCount'] = '0'
    # don't alter session_attributes['lastIntent'], let BIBot remember the last used intent

    askCount = helpers.increment_counter(session_attributes, 'greetingCount')
    
    # build response string
    if askCount == 1: response_string = "Hello! How can I help?"
    elif askCount == 2: response_string = "I'm here"
    elif askCount == 3: response_string = "I'm listening"
    elif askCount == 4: response_string = "Yes?"
    elif askCount == 5: response_string = "Really?"
    else: response_string = 'Ok'

    return category(intent_request)

    #return helpers.close(session_attributes, 'Fulfilled', {'contentType': 'PlainText','content': response_string})   

