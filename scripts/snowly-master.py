#!/usr/bin/python
from weakref import WeakKeyDictionary

import time, os, sys, select, threading, socket
import logging
import consts
from time import sleep

from PodSixNet.Channel import Channel
from PodSixNet.Server import Server

# logging configuration
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] (%(threadName)-10s) %(message)s')


"""
LENZERHEIDE ZAUBERWALD 2015 * SCHNEE-EULEN * Snowy owls (master)
"""
class SnowlyChannel(Channel):
    """
    Networking channel for one connected client pi.
    """
    def __init__(self, *args, **kwargs):
        Channel.__init__(self, *args, **kwargs)

    def Network_input(self, data):
        log.debug("snowl client: input changed: %s", data)

    def Network_config(self, data):
        log.debug("received client config: %s", data)
        # insert and map client inputs/outputs
        self._server.update_clients(self, data)

    def Close(self):
        self._server.remove_client(self)


class SnowlyServer(Server):
    channelClass = SnowlyChannel
    exitSignal = False

    framerate = 20
    last_time = 0
    current_time = 0
    delta_time = 0

    def __init__(self, *args, **kwargs):
        self.id = conf.CLIENT_ID
        self.conf = kwargs['conf']
        del kwargs['conf']
        log.debug('using master.conf from %s', self.conf)

        Server.__init__(self, *args, **kwargs)
        self.clients = WeakKeyDictionary()
        log.debug('Server launched')

    def Connected(self, channel, addr):
        log.debug('new channel: %s', channel)

    def update_clients(self, channel, data):
        log.debug('updating client information on server: channel=%s data=%s' % (channel, data))

        # store client data
        self.clients[channel] = {
            'id': data['id'],
        }

    def remove_client(self, channel):
        print 'removing client', channel
        del self.clients[channel]


    """
    Main loop
    """
    def launch(self, stdscr=None, *args, **kwds):
        print "Snowly Server ready"
        while not self.exitSignal:
            self.current_time = time.time()
            self.delta_time = self.current_time - self.last_time
            if self.delta_time >= (1.0/self.framerate):
                #self.run_actions()
                self.last_time = self.current_time

            try:
                self.Pump()
            except Exception as e:
                # catch and log any exceptions that come up to this point
                log.error(e)

            # sleep smallest interval possible on system (~1-10ms)
            time.sleep(0.0001)




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

log.debug("Snowly Server initializing at %s:%s" % (conf.MASTER_IP, conf.MASTER_PORT))
server = SnowlyServer(localaddr=(conf.MASTER_IP, conf.MASTER_PORT), conf=conf)

# add strategies
#server.register_action(PrintStateAction(), 999)
#server.register_action(SingleSnowHare(), 0)
#server.register_action(MultipathBase(config='multipath-left.csv', use_inputs=[0]), 0)
#server.register_action(MultipathBase(config='multipath-right.csv', use_inputs=[1]), 1)
#server.register_action(IdleAnimation('multipath-idle.csv', use_inputs=[0,1]), 2)

server.launch()

