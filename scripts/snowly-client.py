#!/usr/bin/python
from PodSixNet.Connection import connection, ConnectionListener
import time, os, sys, select, threading, socket
import logging
import pigpio
import consts
from time import sleep

__exitSignal__ = False

# generic network listener, used for reconnecting
class SnowlyClient(ConnectionListener):
    host = ''
    port = 0
    state = consts.STATE_DISCONNECTED
    isConnecting = 0
    count = 0

    global __exitSignal__

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.connect()

    def Network(self, data):
        log.debug('received network data: %s' % data)
        pass

    def Network_connected(self, data):
        log.debug("connected to the server")
        self.state = consts.STATE_CONNECTED
        self.isConnecting = 0
        self.send_config()

    def Network_disconnected(self, data):
        log.debug("disconnected from the server")
        self.state = consts.STATE_DISCONNECTED
        self.isConnecting = 0

    def Network_error(self, data):
        log.debug("error: %s" % data['error'][1])
        self.state = consts.STATE_DISCONNECTED
        self.isConnecting = 0

    def Network_setoutput(self, data):
        # set rpi output as the white master wishes
        index = data['index']
        val = data['val']
        #print time.time(), "set output ", index, ' to ', val
        if 0 <= index < len(conf.clientOutputMappings):
            io.output(conf.clientOutputMappings[index], val)

    def connect(self):
        log.debug("Connecting to "+''.join((self.host, ':'+str(self.port))))      
        self.isConnecting = 1
        self.Connect((self.host, self.port))
        
    def reconnect(self):
        # if we get disconnected, only try once per second to re-connect
        log.debug("no connection or connection lost - trying reconnection in %ds..." % conf.NETWORK_CONNECT_RETRY_DELAY)
        sleep(conf.NETWORK_CONNECT_RETRY_DELAY)
        self.connect()

    def send_config(self):
        self.Send({
            'action': 'config',
            'id': conf.CLIENT_ID,
            'inputs': len(conf.clientInputMappings),
            'outputs': len(conf.clientOutputMappings), 
            'inputWeight': conf.CLIENT_WEIGHT_INPUTS,
            'outputWeight': conf.CLIENT_WEIGHT_OUTPUTS
        })

    def event_input(self, channel, val):
        print "input event on channel ", channel, " val=", val, " delegating to master "
        self.Send({
            'action': 'input',
            'channel': channel,
            'val': val
        })

    def check_keyboard_commands(self):
        r, w, x = select.select([sys.stdin], [], [], 0.0001)
        for s in r:
            if s == sys.stdin:
                input = sys.stdin.readline()
                if input.lower().startswith('i'):
                    try:
                        # simulate input (format: "i2.1" => set input 2 to 1
                        channel = input[1:input.index('.')]
                        val = int(input[input.index('.')+1:])
                        print "simulate input value: channel=", channel, " val=", val
                        self.event_input(channel, val)
                    except:
                        print 'Unknown command'

                return True
        return False

    def Loop(self):
        self.Pump()
        connection.Pump()

        # test notify master of carrot found
        if self.count == 1000:
            #self.Send({"action": "carrot", "size": "large"})
            self.count = 0
        self.count += + 1

        if self.state == consts.STATE_DISCONNECTED and not self.isConnecting:
            self.reconnect()

# logging configuration
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] (%(threadName)-10s) %(message)s')

# read configuration
config_file = 'conf'
if len(sys.argv) == 2:
    config_file = os.path.basename(sys.argv[1])
    if config_file[-3:] == ".py":
        config_file = config_file[:-3]

log.debug("Reading configuration from file %s.py" % config_file)
conf = __import__(config_file, globals(), locals(), [])

# update log configuration
log.setLevel(conf.LOG_LEVEL)
##logging.basicConfig(level=conf.LOG_LEVEL, format='[%(levelname)s] (%(threadName)-10s) %(message)s')

log.debug("Creating client %s" % conf.CLIENT_ID)
client = SnowlyClient(conf.MASTER_IP, conf.MASTER_PORT)

# main thread
try:
    while not __exitSignal__:
        log.debug("- main loop step %s" % time.time())
        client.check_keyboard_commands()
        client.Loop()
        sleep(1)
        
except KeyboardInterrupt:
    log.debug("Keyboard interrupt")
    __exitSignal__ = True

log.debug("Exit client %s" % conf.CLIENT_ID)

