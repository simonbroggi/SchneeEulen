# configuration template for snow owls
# copy to conf.py locally and adjust

#
# global configuration
#


#
# client configuration
#

# networking
NETWORK_CONNECT_RETRY_DELAY = 3

# information about where to send data
NETWORK_MASTER = '10.0.0.1'
NETWORK_MASTER_PORT = 12345


# id for this specific client - must be unique in the network
CLIENT_ID = 'OWL'


# default map for available outputs (with virtual numbering 0..numOutputs)
# to Raspberry Pi B+ board mapping (BCM)
#
# http://pi4j.com/images/j8header.png seems to be wrong for B+
# see http://raspberrypi.stackexchange.com/questions/12966/what-is-the-difference-between-board-and-bcm-for-gpio-pin-numbering
#
DIMMER_PIN_MAPPING = [
    7, 15, 16, 0, 1, 2, 3, 4, 5, 12, 13, 6, 14,
    10, 11, 21, 22, 26, 24, 27, 25, 28, 29
]

#
# master configuration
#
MASTER_IP = '10.0.0.1'
MASTER_PORT = 12345
