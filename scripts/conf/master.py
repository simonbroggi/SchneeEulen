#!/usr/bin/python
# -*- coding: utf-8 -*-

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
CLIENT_ID = 'KEVIN'

# dimmer configuration per client (should be 3 per owl-client, max 9 per raspberry)
LIGHT_DIMMERS = {
    'eye_left': {
        'gpio': 13,
        'steps': 500,
        'freq': 200,
    },
     'body': {
        'gpio': 19,
        'steps': 500,
        'freq': 500
    },
    'eye_right': {
        'gpio': 26,
        'steps': 500,
        'freq': 200
    }
}

# servo configuration per client (should be 1 per owl)
SERVO_CONTROL = {
    'head': {
        'gpio': 6
    }
}


#
# networking
#
NETWORK_CONNECT_RETRY_DELAY = 1

# information about where to send data
CLIENT_MASTER_IP = '10.0.0.1'
CLIENT_MASTER_PORT = 12345

#
# master configuration
#
MASTER_IP = '0.0.0.0'
MASTER_PORT = 12345

MASTER_PLAYLIST = [
    'Breathing',
    'SimpleMasterStrategy',
    'AutoClient',
    'NightOwls',
    'LightUp',
    'Dancer',
    'Headshake',
    'Sleep',
    'Idle'
]

MASTER_SKIP_LIST = [
  'Idle'
]

MASTER_PLAYLIST_DESC = [
    'Einfaches Atmen und leichte Kopfbewegungen',
    'Lichtstreifen von Eule zu Eule',
    'Herzschlag, Nervosität usw. - das volle Programm',
    'Nachteulen - nur die Augen leuchten im Dunkeln auf',
    'Foto-Modus: alle dezent hell für 30sec',
    'Tanz-Choreographie - siehe Lenzerheide Zauberwald',
    'Alle drehen gemeinsam den Kopf hin und her',
    'Dunkles Schlafen... für 30s',
    'Dolce far niente - für manuelle Steuerung'
]

#
# test mode (for websockets)
#
TEST_MODE = False
TEST_CLIENTS = ['KLAUS', 'MARTHA']
