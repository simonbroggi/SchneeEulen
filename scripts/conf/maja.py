# configuration template to be used in git
# copy to conf.py locally and adjust
import logging

#
# global configuration
#

# available log levels: NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = logging.INFO


#
# client configuration
#

# id for this specific client - must be unique in the network
CLIENT_ID = 'MAJA'

# dimmer configuration per client (should be 3 per owl-client, max 9 per raspberry)
LIGHT_DIMMERS = {
    'eye_left': {
        'gpio': 16,
        'steps': 500,
        'freq': 200
    },
     'body': {
        'gpio': 20,
        'steps': 500,
        'freq': 500
    },
    'eye_right': {
        'gpio': 21,
        'steps': 500,
        'freq': 200
    }
}

# servo configuration per client (should be 1 per owl)
SERVO_CONTROL = {
    'head': {
        'gpio': 12,
        'direction': 'inverse'
    }
}


#
# networking
#
NETWORK_CONNECT_RETRY_DELAY = 3

# information about where to send data
CLIENT_MASTER_IP = '10.0.0.76'
CLIENT_MASTER_PORT = 12345

#
# master configuration
#
MASTER_IP = '0.0.0.0'
MASTER_PORT = 12345
