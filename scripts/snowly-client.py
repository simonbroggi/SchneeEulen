#!/usr/bin/python
import logging
import os
import select
import sys
import time
from time import sleep

import consts
from PodSixNet.Connection import connection, ConnectionListener
from actors import led
from actors import servo
from strategies.base import StrategyThread
from strategies.client.simple import SimpleRandomizedStrategy

__exitSignal__ = False

# logging configuration
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] (%(threadName)-10s) %(message)s')


# generic network listener, used for reconnecting
class SnowlyClient(ConnectionListener):
    host = ''
    port = 0
    state = consts.STATE_DISCONNECTED
    is_connecting = 0
    count = 0
    strategies = {}
    active_strategy = None
    connect_retry_time = 0

    # actors
    dimmers = {}
    servos = {}

    # sensors
    distance_sensors = {}

    slave_mode = False
    slave_keepalive = 0

    global __exitSignal__

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.connect()

        self.initSensors()
        self.initActors()

    def initSensors(self):
        None

    def initActors(self):
        self.initDimmers()
        self.initServos()

    """ Initialize independent dimmer threads """
    def initDimmers(self):
        logging.debug("initializing dimmers: %s", conf.LIGHT_DIMMERS)
        for key in conf.LIGHT_DIMMERS.keys():
            dimmer_conf = conf.LIGHT_DIMMERS[key]
            logging.debug("- dimmer %s gpio=%s steps=%s freq=%s" % (key,dimmer_conf['gpio'],dimmer_conf['steps'],dimmer_conf['freq']))
            self.dimmers[key] = led.Dimmer(dimmer_conf['gpio'], dimmer_conf['steps'], dimmer_conf['freq'])
            self.dimmers[key].start()

            #for j in range(0,1):
            #    dim.add(0.0, 1.0, 4.0, 1)
            #    dim.add(1.0, 0.0, 4.0, -1)

    """ Initialize independent servo threads """
    def initServos(self):
        logging.debug("initializing servos: %s", conf.SERVO_CONTROL)
        for key in conf.SERVO_CONTROL.keys():
            servo_conf = conf.SERVO_CONTROL[key]
            self.servos[key] = servo.Servo(servo_conf['gpio'], 0.0, 180.0)
            self.servos[key].start()

    def shutdownDimmers(self):
        logging.debug("shutting down dimmer threads")
        for dimmer in self.dimmers.items():
            dimmer[1].signal_exit()
            while dimmer[1].is_alive():
                sleep(0.05)

        logging.debug("all dimmers shutdown gracefully")

    def shutdownServos(self):
        logging.debug("shutting down all servo threads")
        for servo in self.servos.items():
            servo[1].signal_exit()
            while servo[1].is_alive():
                sleep(0.05)

        logging.debug("all servos shutdown gracefully")

    def get_dimmer(self, key):
        #logging.debug(self.dimmers)
        return self.dimmers[key]

    def get_servo(self, key):
        return self.servos[key]

    def Network(self, data):
        log.debug('received network data: %s' % data)
        pass

    def Network_connected(self, data):
        log.debug("connected to the server")
        self.state = consts.STATE_CONNECTED
        self.is_connecting = 0
        self.send_config()

    def Network_disconnected(self, data):
        log.debug("disconnected from the server")
        self.state = consts.STATE_DISCONNECTED
        self.is_connecting = 0

    def Network_error(self, data):
        log.debug("error: %s" % data['error'][1])
        self.state = consts.STATE_DISCONNECTED
        self.is_connecting = 0

    def Network_setoutput(self, data):
        None

    def connect(self):
        log.debug("Connecting to "+''.join((self.host, ':'+str(self.port))))      
        self.is_connecting = 1
        self.Connect((self.host, self.port))
        
    def reconnect(self):
        # if we get disconnected, only try once per second to re-connect
        log.debug("no connection or connection lost - trying reconnection in %ds..." % conf.NETWORK_CONNECT_RETRY_DELAY)
        self.connect_retry_time = conf.NETWORK_CONNECT_RETRY_DELAY + time.time()
        self.connect()

    def send_config(self):
        self.Send({
            'action': 'config',
            'id': conf.CLIENT_ID
        })

    def event_input(self, channel, val):
        log.debug("input event on channel=%s val=%s delegating to master ", (channel, val))
        self.Send({
            'action': 'input',
            'channel': channel,
            'val': val
        })

    def Network_sync(self, data):
        logging.debug('master command: sync %s' % data)
        if self.active_strategy is not None:
            self.switch_strategy(None)

        self.slave_mode = True
        self.slave_keepalive = time.time()

    def Network_command(self, data):
        logging.debug('master command: command %s' % data)
        if self.active_strategy is not None:
            self.switch_strategy(None)

        self.slave_mode = True
        self.slave_keepalive = time.time()

        self.process_command(data)

    def process_command(self, data):
        logging.debug('processing command %s' % data['command'])
        if data['command'] == 'dim':
            try:
                dimmer = self.dimmers[data['id']]
                dimmer.add(data['start_val'], data['end_val'], data['duration'], data['step'], data['clear'])
            except Exception as e:
                logging.error("error with dim command: %s" % e)

        elif data['command'] == 'move':
            try:
                servo = self.servos[data['id']]
                servo.add(data['start_angle'], data['end_angle'], data['duration'], data['step'], data['clear'])
            except Exception as e:
                logging.error("error with dim command: %s" % e)


    def check_keyboard_commands(self):
        r, w, x = select.select([sys.stdin], [], [], 0.0001)
        for s in r:
            if s == sys.stdin:
                input = sys.stdin.readline()
                if input.lower().startswith('i'):
                    try:
                        # led dimming command
                        channel = input[1:input.index('.')]
                        val = int(input[input.index('.')+1:])
                        print "simulate input value: channel=", channel, " val=", val
                        self.event_input(channel, val)
                    except:
                        print 'Unknown command'

                return True
        return False


    # def run_actions(self):
    #     ordered_actions = sorted(self.strategies.items(), key=lambda x: x[1]['weight'])
    #
    #     for action in ordered_actions:
    #         action[0].update(self.current_time, self.delta_time)

    def register_strategy(self, strategy, weight):
        if not issubclass(strategy, StrategyThread):
            raise BaseException("Strategy does not have base type StrategyThread", strategy)

        self.strategies[strategy] = {
            'weight': weight
        }

        #strategy.registered({'owner': self })
        logging.debug("registered strategy %s" % strategy)

    def remove_strategy(self, strategy):
        del self.strategies[strategy]

    def switch_strategy(self, new_strategy):
        logging.debug("switching strategy to %s" % new_strategy)
        if self.active_strategy:
            logging.debug('signalling exit to strategy %s' % self.active_strategy)
            self.active_strategy.signal_exit()

        if new_strategy is not None:
            self.active_strategy = new_strategy(self)
            self.active_strategy.start()
            logging.debug('active strategy is now %s' % self.active_strategy)
        else:
            logging.debug('None strategy selected')
            self.active_strategy = None

    def Loop(self):
        self.Pump()
        connection.Pump()

        # master keep alive
        if self.count == 100:
            self.Send({"action": "mouse", "size": "large"})
            self.count = 0
        self.count += + 1

        if self.state == consts.STATE_DISCONNECTED and not self.is_connecting:
            #logging.debug('%s' % (self.connect_retry_time - time.time()))
            if self.connect_retry_time - time.time() <= 0:
                self.reconnect()

        if self.slave_mode and (time.time() - self.slave_keepalive > consts.SLAVE_TIMEOUT):
            logging.debug('---> no command from master within %s seconds' % consts.SLAVE_TIMEOUT)
            logging.debug('terminating slave mode...')
            self.slave_mode = False

        if not self.slave_mode and self.active_strategy is None:
            strategies = sorted(self.strategies.items(), key=lambda x: x[1]['weight'])
            if len(strategies) > 0:
                logging.debug("no strategy set, choosing strategy according to weight: %s" % strategies[0][0])
                self.switch_strategy(strategies[0][0])

    def shutdown(self):
        logging.debug('terminate snowly client')
        if self.active_strategy:
            self.active_strategy.signal_exit()
            sleep(2.0)

        self.shutdownDimmers()
        self.shutdownServos()

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
client = SnowlyClient(conf.CLIENT_MASTER_IP, conf.CLIENT_MASTER_PORT)

# register client strategies (stoppable threads)
client.register_strategy(StrategyThread, 999)
client.register_strategy(SimpleRandomizedStrategy, 0)


# main thread
try:
    while not __exitSignal__:
        # log.debug("- main loop step %s" % time.time())
        client.check_keyboard_commands()
        client.Loop()
        sleep(0.01)
        
except KeyboardInterrupt:
    log.debug("Keyboard interrupt")
    __exitSignal__ = True
    client.shutdown()

log.debug("Exit client %s" % conf.CLIENT_ID)

