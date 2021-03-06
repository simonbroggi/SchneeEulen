#!/usr/bin/python
import logging
import os
import select
import sys
import time
import signal
from time import sleep

import consts
from PodSixNet.Connection import connection, ConnectionListener
from actors import led
from actors import servo
from strategies.base import StrategyThread
from strategies.client.simple import SimpleRandomizedStrategy
from strategies.client.nightblinking import NightBlinking
from strategies.client.autonomous import AutoStrategy
from strategies.client.autonomous import SimpleAuto
from strategies.client.autonomous import BreathAndLook
from strategies.client.autonomous import HeartbeatAndLook



__exitSignal__ = False

# logging configuration
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] (%(threadName)-10s) %(message)s')

SERVO_DEFAULT_MIN_PW = 500
SERVO_DEFAULT_MAX_PW = 2500

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
        logger.debug("initializing dimmers: %s", conf.LIGHT_DIMMERS)
        for key in conf.LIGHT_DIMMERS.keys():
            dimmer_conf = conf.LIGHT_DIMMERS[key]
            logger.debug("- dimmer %s gpio=%s steps=%s freq=%s" % (key,dimmer_conf['gpio'],dimmer_conf['steps'],dimmer_conf['freq']))
            self.dimmers[key] = led.Dimmer(dimmer_conf['gpio'], dimmer_conf['steps'], dimmer_conf['freq'], 'Dimmer-' + key + '-%s')
            self.dimmers[key].start()

            #for j in range(0,1):
            #    dim.add(0.0, 1.0, 4.0, 1)
            #    dim.add(1.0, 0.0, 4.0, -1)

    """ Initialize independent servo threads """
    def initServos(self):
        logger.debug("initializing servos: %s", conf.SERVO_CONTROL)
        for key in conf.SERVO_CONTROL.keys():
            servo_conf = conf.SERVO_CONTROL[key]
            if not 'direction' in servo_conf:
                servo_conf['direction'] = 'normal'
            if not 'min_pw' in servo_conf:
                servo_conf['min_pw'] = SERVO_DEFAULT_MIN_PW
            if not 'max_pw' in servo_conf:
                servo_conf['max_pw'] = SERVO_DEFAULT_MAX_PW
            if not 'freq' in servo_conf:
                servo_conf['freq'] = 50
            self.servos[key] = servo.Servo(servo_conf['gpio'], 0.0, 180.0, int(servo_conf['min_pw']), int(servo_conf['max_pw']), int(servo_conf['freq']), servo_conf['direction'])
            self.servos[key].start()

    def shutdownDimmers(self):
        logger.debug("shutting down dimmer threads")
        for dimmer in self.dimmers.items():
            dimmer[1].signal_exit()
            while dimmer[1].is_alive():
                sleep(0.05)

        logger.debug("all dimmers shutdown gracefully")

    def shutdownServos(self):
        logger.debug("shutting down all servo threads")
        for servo in self.servos.items():
            servo[1].signal_exit()
            while servo[1].is_alive():
                sleep(0.05)

        logger.debug("all servos shutdown gracefully")

    def get_dimmer(self, key):
        #logger.debug(self.dimmers)
        return self.dimmers[key]

    def get_servo(self, key):
        return self.servos[key]

    def Network(self, data):
        logger.debug('received network data: %s' % data)
        pass

    def Network_connected(self, data):
        logger.debug("connected to the server")
        self.state = consts.STATE_CONNECTED
        self.is_connecting = 0
        self.send_config()

    def Network_disconnected(self, data):
        logger.debug("disconnected from the server")
        self.state = consts.STATE_DISCONNECTED
        self.is_connecting = 0

    def Network_error(self, data):
        logger.debug("error: %s", data)
        self.state = consts.STATE_DISCONNECTED
        self.is_connecting = 0

    def Network_setoutput(self, data):
        None

    def connect(self):
        logger.debug("Connecting to "+''.join((self.host, ':'+str(self.port))))
        self.is_connecting = 1
        self.Connect((self.host, self.port))

    def reconnect(self):
        # if we get disconnected, only try once per second to re-connect
        logger.debug("no connection or connection lost - trying reconnection in %ds..." % conf.NETWORK_CONNECT_RETRY_DELAY)
        self.connect_retry_time = conf.NETWORK_CONNECT_RETRY_DELAY + time.time()
        self.connect()

    def send_config(self):
        self.Send({
            'action': 'config',
            'id': conf.CLIENT_ID
        })

    def event_input(self, channel, val):
        logger.debug("input event on channel=%s val=%s delegating to master ", (channel, val))
        self.Send({
            'action': 'input',
            'channel': channel,
            'val': val
        })

    def Network_sync(self, data):
        logger.debug('master command: sync %s' % data)
        if self.active_strategy is not None:
            self.switch_strategy(None)

        self.slave_mode = True
        self.slave_keepalive = time.time()

    def Network_command(self, data):
        logger.debug('master command: command %s' % data)
        #if self.active_strategy is not None:
        #    self.switch_strategy(None)

        self.slave_mode = True
        self.slave_keepalive = time.time()

        self.process_command(data)

    def process_command(self, data):
        logger.debug('processing command %s' % data['command'])
        if data['command'] == 'dim':
            if not 'start_val' in data:
                data['start_val'] = float('nan')
            if not 'end_val' in data:
                data['end_val'] = float('nan')
            if not 'duration' in data:
                data['duration'] = 4.0
            if not 'step' in data:
                data['step'] = 1
            if not 'clear' in data:
                data['clear'] = False

            try:
                dimmer = self.dimmers[data['id']]
                dimmer.add(data['start_val'], data['end_val'], data['duration'], data['step'], data['clear'])
            except Exception as e:
                logger.error(e)
                logger.error("error with dim command: %s" % e)

        elif data['command'] == 'move':
            # fill in defaults
            if not 'start_angle' in data:
                data['start_angle'] = float('nan')
            if not 'end_angle' in data:
                data['end_angle'] = float('nan')
            if not 'duration' in data:
                data['duration'] = 4.0
            if not 'step' in data:
                data['step'] = 1
            if not 'clear' in data:
                data['clear'] = False

            try:
                servo = self.servos[data['id']]
                servo.add(data['start_angle'], data['end_angle'], data['duration'], data['step'], data['clear'])
            except Exception as e:
                logger.error("error with move command: %s" % e)

        elif data['command'] == 'switch_strategy':
            try:
                strategy = data['strategy']
                logger.debug('----> command switch_strategy strategy=%s active_strategy=%s' % (strategy, self.active_strategy))

                if strategy is not None:
                    logger.debug('calling switch_strategy with %s' % globals()[strategy])
                    self.switch_strategy(globals()[strategy])
                else:
                    logger.debug('calling switch strategy with None')
                    self.switch_strategy(None)

            except Exception as e:
                logger.error("error when switching strategy: %s" % e)

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
                        print("simulate input value: channel=", channel, " val=", val)
                        self.event_input(channel, val)
                    except:
                        print('Unknown command')

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
            'id': strategy.__name__,
            'weight': weight
        }

        #strategy.registered({'owner': self })
        logger.debug("registered strategy %s with id %s" % (strategy, strategy.__name__))

    def remove_strategy(self, strategy):
        del self.strategies[strategy]

    def switch_strategy(self, new_strategy):
        logger.debug("==============> switch strategy: active=%s new=%s" % (self.active_strategy, new_strategy))
        if type(self.active_strategy) is new_strategy:
            logger.debug('strategy %s already active' % new_strategy)
            return

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
        try:
            self.Pump()
            connection.Pump()
        except Exception as e:
            #logging.error(e)	
            sleep(5)
            pass

        # master keep alive
        if self.count == 100:
            self.Send({"action": "mouse", "size": "large"})
            self.count = 0
        self.count += + 1

        if self.state == consts.STATE_DISCONNECTED and not self.is_connecting:
            #logging.debug('%s' % (self.connect_retry_time - time.time()))
            if self.connect_retry_time - time.time() <= 0:
                self.reconnect()

        if (self.active_strategy is not None) and (not self.active_strategy.is_alive()):
            self.active_strategy = None

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
            sleep(1.0)

        self.shutdownDimmers()
        self.shutdownServos()

# read configuration
config_file = 'conf'
if len(sys.argv) == 2:
    config_file = os.path.basename(sys.argv[1])
    if config_file[-3:] == ".py":
        config_file = config_file[:-3]

logging.debug("Reading configuration from file %s.py" % config_file)
conf = __import__('conf.' + config_file, globals(), locals(), [config_file])
#logging.debug(_conf)
#conf = _conf[config_file]

# update log configuration
logging.basicConfig(level=conf.LOG_LEVEL, format='[%(levelname)s] (%(threadName)-10s) %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(conf.LOG_LEVEL)

logger.debug("Creating client %s" % conf.CLIENT_ID)
client = SnowlyClient(conf.CLIENT_MASTER_IP, conf.CLIENT_MASTER_PORT)

# register client strategies (stoppable threads)
client.register_strategy(SimpleAuto, 0)
#client.register_strategy(BreathAndLook, 1)
#client.register_strategy(HeartbeatAndLook, 2)
#client.register_strategy(NightBlinking, 999)

#client.register_strategy(SimpleRandomizedStrategy, 1)
#client.register_strategy(StrategyThread, 999)
#client.register_strategy(AutoStrategy, 0)
#client.register_strategy(SimpleRandomizedStrategy, 1)

#client.register_strategy(NightBlinking, 999)

def clean_terminate(signal, frame):
    __exitSignal__ = True
    client.shutdown()
    exit(0)

signal.signal(signal.SIGTERM, clean_terminate)

# main thread
try:
    while not __exitSignal__:
        # logger.debug("- main loop step %s" % time.time())
        client.check_keyboard_commands()
        client.Loop()
        sleep(0.01)

except KeyboardInterrupt:
    logger.debug("Keyboard interrupt")
    __exitSignal__ = True
    client.shutdown()

logger.debug("Exit client %s" % conf.CLIENT_ID)
