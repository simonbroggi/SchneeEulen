# configuration template to be used in git
# copy to conf.py locally and adjust
import logging

#
# global configuration
#

# available log levels: NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = logging.DEBUG


#
# client configuration
#

# id for this specific client - must be unique in the network
CLIENT_ID = 'SNOWCHILD'

# networking
NETWORK_CONNECT_RETRY_DELAY = 3

# information about where to send data
CLIENT_MASTER_IP = '10.0.0.1'
CLIENT_MASTER_PORT = 12345

#
# master configuration
#
MASTER_IP = '10.0.0.1'
MASTER_PORT = 12345
