#!/usr/bin/python
from weakref import WeakKeyDictionary

import time, os, sys, select, threading, socket
import logging
import consts
from time import sleep
import cherrypy

from PodSixNet.Channel import Channel
from PodSixNet.Server import Server

from strategies.base import StrategyThread
from strategies.master.simple import SimpleMasterStrategy

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
    strategies = {}

    active_strategy = None

    clientsById = {}
    clientsByChannel = {}

    def __init__(self, *args, **kwargs):
        self.conf = kwargs['conf']
        self.id = self.conf.CLIENT_ID
        del kwargs['conf']
        logging.debug('using master.conf from %s', self.conf)

        Server.__init__(self, *args, **kwargs)
        self.clients = WeakKeyDictionary()
        logging.debug('Server launched')

    def Connected(self, channel, addr):
        logging.debug('new channel: %s', channel)

    def update_clients(self, channel, data):
        logging.debug('updating client information on server: channel=%s data=%s' % (channel, data))

        # store client data
        self.clientsByChannel[channel] = {
            'id': data['id'],
        }
        self.clientsById[data['id']] = channel

    def remove_client(self, channel):
        logging.debug('removing client %s' % channel)
        client = self.clientsByChannel[channel]
        del self.clientsById[client['id']]
        del self.clientsByChannel[channel]

    def send_command(self, clients, params):
        """
        :param clients: [str]
        :param params: {}
        :return:
        """
        logging.debug('send_command clients=%s params=%s' % (clients, params))
        params['action'] = 'command'
        for id in clients:
            self.clientsById[id].Send(params)

    def register_strategy(self, strategy, weight):
        if not issubclass(strategy, StrategyThread):
            raise BaseException("Strategy does not have base type BaseStrategy", strategy)

        self.strategies[strategy] = {
            'weight': weight
        }

        #strategy.registered({'owner': self })
        logging.debug("registered strategy %s" % strategy)

    def get_client_ids(self):
        return self.clientsById.keys()

    def remove_strategy(self, strategy):
        del self.strategies[strategy]

    def switch_strategy(self, new_strategy):
        logging.debug("switching strategy to %s" % new_strategy)
        if self.active_strategy:
            logging.debug('signalling exit to strategy %s' % self.active_strategy)
            self.active_strategy.signal_exit()

        self.active_strategy = new_strategy(self)
        self.active_strategy.start()
        logging.debug('active strategy is now %s' % self.active_strategy)

    """
    Main loop
    """
    def launch(self, stdscr=None, *args, **kwds):
        logging.debug("Snowly Server ready %s" % time.time())

        while not self.exitSignal:
            #logging.debug(self.get_client_ids())
            try:
                self.Pump()
            except Exception as e:
                # catch and log any exceptions that come up to this point
                log.error(e)

            if self.active_strategy is None:
                strategies = sorted(self.strategies.items(), key=lambda x: x[1]['weight'])
                if len(strategies) > 0:
                    logging.debug("no strategy set, choosing strategy according to weight: %s" % strategies[0][0])
                    self.switch_strategy(strategies[0][0])

            # sleep some time
            time.sleep(0.01)

    def shutdown(self):
        logging.debug('terminate snowly server master')
        if self.active_strategy:
            self.active_strategy.signal_exit()
            sleep(2.0)

        #self.shutdownDimmers()
        #self.shutdownServos()


class SnowlyNet(threading.Thread):
    server = None

    def __init__(self, daemon=True):
        threading.Thread.__init__(self)
        self.daemon = daemon

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

        # register client strategies (stoppable threads)
        server.register_strategy(SimpleMasterStrategy, 999)
        self.server = server

    def run(self):
        self.server.launch()

    def signal_exit(self):
        self.server.exitSignal = True

class SnowlyWeb:
    @cherrypy.expose
    def index(self):
        return open('index.html')

class SnowlyWebService:
    def __init__(self, net_server):
        self.net_server = net_server

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def index(self):
        data = cherrypy.request.json

if __name__ == '__main__':
    # owl communication network
    logging.debug('=== initializing owl communication network')
    snowlynet = SnowlyNet(False)
    snowlynet.start()
    try:
        snowlynet.join()
    except KeyboardInterrupt:
        logging.debug('interrupted - signalling exit')
        snowlynet.signal_exit()

    # owl control web interface
    logging.debug('=== initializing owl web control interface')
    web_conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'text/plain')],
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './static'
        }
    }

    webapp = SnowlyWeb()
    webapp.snowlcontrol = SnowlyWebService(snowlynet)

    cherrypy.server.socket_port = 8080
    cherrypy.server.socket_host = '0.0.0.0'
    #cherrypy.quickstart(webapp, '/', web_conf)


"""
sudo iptables -I INPUT 1 -i eth0 -p tcp --dport 8080 -j ACCEPT
sudo iptables -I INPUT 1 -i wlan0 -p tcp --dport 8080 -j ACCEPT
"""