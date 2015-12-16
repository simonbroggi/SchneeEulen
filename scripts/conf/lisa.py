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
CLIENT_ID = 'LISA'

# dimmer configuration per client (should be 3 per owl-client, max 9 per raspberry)
LIGHT_DIMMERS = {
    'eye_left': {
        'gpio': 17,
        'steps': 500,
        'freq': 300
    },
     'body': {
        'gpio': 27,
        'steps': 500,
        'freq': 500
    },
    'eye_right': {
        'gpio': 22,
        'steps': 500,
        'freq': 400
    }
}

# servo configuration per client (should be 1 per owl)
SERVO_CONTROL = {
    'head': {
        'gpio': 4
    }
}


#
# networking
#
NETWORK_CONNECT_RETRY_DELAY = 3

# information about where to send data
CLIENT_MASTER_IP = '10.0.0.1'
CLIENT_MASTER_PORT = 12345

#
# master configuration
#
MASTER_IP = '0.0.0.0'
MASTER_PORT = 12345
