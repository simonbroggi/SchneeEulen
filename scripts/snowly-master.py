#!/usr/bin/python
from weakref import WeakKeyDictionary

import time, os, sys, select, threading, socket
import logging
import consts
from time import sleep
import datetime
import subprocess
import cherrypy

from PodSixNet.Channel import Channel
from PodSixNet.Server import Server

from strategies.base import StrategyThread
from strategies.master.nightowls import NightOwls
from strategies.master.simple import SimpleMasterStrategy
from strategies.master.lightup import LightUp
from strategies.master.dancer import Dancer
from strategies.master.breathing import Breathing
from strategies.master.headshake import Headshake
from strategies.master.sleep import Sleep
from strategies.master.autoclient import AutoClient

# logging configuration
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] (%(threadName)-10s) %(message)s')

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
    playlist = []

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
            if id in self.clientsById:
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

        self.playlist = self.conf.MASTER_PLAYLIST
        self.playlist_desc = self.conf.MASTER_PLAYLIST_DESC

        if self.playlist is None:
            self.playlist = []

        playlist_index = 0
        while not self.exitSignal:
            try:
                self.Pump()
            except Exception as e:
                # catch and log any exceptions that come up to this point
                log.error(e)

            if (self.active_strategy is not None) and (not self.active_strategy.is_alive()):
                logging.debug('strategy terminated - set active_strategy to None')
                self.active_strategy = None

            if self.active_strategy is None:
                if playlist_index < len(self.playlist):
                    #logging.debug('playlist')
                    active_item = self.playlist[playlist_index]
                    playlist_index = (playlist_index + 1) % len(self.playlist)
                    if active_item not in ['Sleep']:
                        strategy_class = globals()[active_item]
                        self.switch_strategy(strategy_class)
                else:
                    # no playlist
                    strategies = sorted(self.strategies.items(), key=lambda x: x[1]['weight'])
                    if len(strategies) > 0:
                        logging.debug("no strategy set, choosing strategy according to weight: %s" % strategies[0][0])
                        self.switch_strategy(strategies[0][0])

            # sleep some time
            time.sleep(0.01)

        self.shutdown()

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
        conf = __import__('conf.' + config_file, globals(), locals(), [config_file])

        # update log configuration
        log.setLevel(conf.LOG_LEVEL)

        log.debug("Snowly Server initializing at %s:%s" % (conf.MASTER_IP, conf.MASTER_PORT))
        server = SnowlyServer(localaddr=(conf.MASTER_IP, conf.MASTER_PORT), conf=conf)

        # register master strategies (stoppable threads)
        server.register_strategy(AutoClient, 0)
        server.register_strategy(NightOwls, 1)
        server.register_strategy(LightUp, 2)
        server.register_strategy(Dancer, 3)
        server.register_strategy(Breathing, 4)
        server.register_strategy(Headshake, 5)
        server.register_strategy(Sleep, 6)
        server.register_strategy(SimpleMasterStrategy, 7)

        self.server = server

    def run(self):
        self.server.launch()

    def signal_exit(self):
        self.server.exitSignal = True

class SnowlyWeb:
    @cherrypy.expose
    def index(self):
        return open('static/index.html')

class SnowlyWebService:
    exposed = True

    def __init__(self, net_server):
        self.net_server = net_server
        self.server = self.net_server.server

    def set_datetime(self, datestring):
        try:
            #dt = dateutil.parser.parse(datestring)
            dt = datetime.now()
            logging.debug('set system datetime to string %s (datetime %s)' % (datestring, dt))
            subprocess.call("sudo date -s '{:}'".format(dt.strftime('%Y/%m/%d %H:%M:%S')), shell=True)
        except:
            logging.debug('error setting datetime')
            
    # def _cp_dispatch(self, vpath):
    #     logging.debug('cp_dispatch:%s' % vpath)
    #     if len(vpath) == 1:
    #         cherrypy.request.params['name'] = vpath.pop()
    #         return self
    #     #
    #     # if len(vpath) == 3:
    #     #     cherrypy.request.params['artist'] = vpath.pop(0)  # /band name/
    #     #     vpath.pop(0) # /albums/
    #     #     cherrypy.request.params['title'] = vpath.pop(0) # /album title/
    #     #     return self.albums
    #
    #     return self

    @cherrypy.tools.json_out()
    @cherrypy.tools.accept(media='application/json')
    def GET(self, *vpath):
        try:
            cmd = vpath[0]
            if cmd == 'clients':
                return self.server.clientsById.keys()
            elif cmd == 'info':
                return {
                    'clients': self.server.clientsById.keys(),
                    'active_strategy': str(self.server.active_strategy.__class__.__name__),
                    #'master_strategies': self.server.strategies.keys()
                    'playlist': self.server.playlist,
                    'playlist_desc': self.server.playlist_desc
                }
            else:
                return {'available_commands': {
                    'clients': 'list of connected clients',
                    'info': 'information about strategies'
                }}
        except Exception as e:
            logging.error(e)

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def PUT(self, *vpath):
        cmd = vpath[0]
        if cmd == '':
            clientId = vpath[1]
        else:
            return {'result': 'not implemented'}

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def POST(self, *vpath):
        try:
            cmd = vpath[0]
            if cmd == 'play':
                logging.info('switching master strategy to %s' % vpath[1])
                strategy_class = globals()[vpath[1]]
                self.server.switch_strategy(strategy_class)
                return {'result': 'ok'}
        except Exception as e:
            logging.error(e)

    #def POST(self):
    #
    #    return

    # @cherrypy.expose
    # #@cherrypy.tools.json_in()
    # @cherrypy.tools.json_out()
    # def index(self):
    #     logging.debug('snowlywebservice json')
    #     data = cherrypy.request.json
    #     return '{"ok":"%s" % self.net_server }'

#    index._cp_config = {
#        'cherrypy.tools.json_in.on': True
#    }

if __name__ == '__main__':
    # owl communication network
    logging.debug('=== initializing owl communication network')
    snowlynet = SnowlyNet(False)
    snowlynet.start()
    # try:
    #     while True and snowlynet.is_alive():
    #         sleep(1)
    # except KeyboardInterrupt:
    #     logging.debug('interrupted - signalling exit')
    #     snowlynet.signal_exit()

    # owl control web interface
    logging.debug('=== initializing owl web control interface')

    api_conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'application/json')],
        }
    }
    web_conf = {
        '/': {
             'tools.sessions.on': True,
             'tools.staticdir.root': os.path.abspath(os.getcwd())
         },
         '/static': {
             'tools.staticdir.on': True,
             'tools.staticdir.dir': './static'
         }
    }

    # disable logging
    cherrypy.config.update({'log.screen': False,
                       'log.access_file': '',
                       'log.error_file': ''})
    cherrypy.log.access_file = None

    #webapp = SnowlyWeb()
    #webapp.snowlcontrol = SnowlyWebService(snowlynet)

    cherrypy.server.socket_port = 8081
    cherrypy.server.socket_host = '0.0.0.0'

    if hasattr(cherrypy.engine, 'signal_handler'):
        cherrypy.engine.signal_handler.subscribe()

    cherrypy.tree.mount(SnowlyWeb(), '', web_conf)
    cherrypy.tree.mount(SnowlyWebService(snowlynet), '/api', api_conf)

    cherrypy.engine.start()
    #cherrypy.engine.block()

    try:
        while True and snowlynet.is_alive():
            sleep(1)
    except KeyboardInterrupt:
        logging.debug('interrupted - signalling exit')
        snowlynet.signal_exit()
        cherrypy.engine.exit()

"""
sudo iptables -I INPUT 1 -i eth0 -p tcp --dport 8080 -j ACCEPT
sudo iptables -I INPUT 1 -i wlan0 -p tcp --dport 8080 -j ACCEPT
"""