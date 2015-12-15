
import logging
import threading
import pigpio
import random
from time import sleep
from strategies.base import StrategyThread

class BreathingAgitation(StrategyThread):
    """Breaths faster when agitation is higher.

    agitation: float between 0 and 1
    """
    def __init__(self, main_thread, agitation = 0.5):
        StrategyThread.__init__(self, main_thread, 'BreathingAgitation')
        self.agitation = agitation
        self.body_dimmer = self.main_thread.get_dimmer('body')

    def run(self):
        while not self.__signalExit__:
            breathTime = 3.0 * (1.5-self.agitation)
            inhaleTime = breathTime * 0.4
            exhaleTime = breathTime - inhaleTime
            self.body_dimmer.add(0.2, 1.0, inhaleTime, 2)
            self.body_dimmer.add(1.0, 0.2, exhaleTime, 2)
            self.wait(breathTime)
        logging.debug('breathing finished')

class HeartbeatAgitation(StrategyThread):
    """All lights pulsate like a heartbeat.
    Faster heartbeat when agitation is higher.
    """
    def __init__(self, main_thread, agitation = 0.5):
        StrategyThread.__init__(self, main_thread, 'HeartbeatAgitation')
        self.agitation = agitation
        self.body_dimmer = self.main_thread.get_dimmer('body')
        self.eye_left = self.main_thread.get_dimmer('eye_left')
        self.eye_right = self.main_thread.get_dimmer('eye_right')
        self.low = 0.35
        self.mid = 0.5
        self.midLow = 0.45
        self.high = 1.0

    def add(self, start_val, end_val, duration, step_size=40, clear=False):
        self.body_dimmer.add(start_val, end_val, duration, step_size, clear)
        self.eye_left.add(start_val, end_val, duration, step_size, clear)
        self.eye_right.add(start_val, end_val, duration, step_size, clear)


    def run(self):
        while not self.__signalExit__:
            beatTime = 1.0 * (1.5-self.agitation)
            first = beatTime * 0.2
            second = beatTime * 0.07
            third = beatTime * 0.22
            recover = beatTime - first - second - third
            self.add(self.low, self.mid, first)
            self.add(self.mid, self.midLow, second)
            self.add(self.midLow, self.high, third)
            self.add(self.high, self.low, recover)
            self.wait(beatTime)
        logging.debug('heartbeat finished')

class BlinkingAgitation(StrategyThread):
    """Blinks (with both eyes) more frequent when agitation is higher.

    agitation: float between 0 and 1
    """
    def __init__(self, main_thread, agitation = 0.5):
        StrategyThread.__init__(self, main_thread, 'BlinkingAgitation')
        self.agitation = agitation
        self.open = 0.7  # 0.3
        self.closed = 0.05  # 0.05
        self.eye_left = self.main_thread.get_dimmer('eye_left')
        self.eye_right = self.main_thread.get_dimmer('eye_right')

    def add(self, start_val, end_val, duration, step_size=10, clear=False):
        self.eye_left.add(start_val, end_val, duration, step_size, clear)
        self.eye_right.add(start_val, end_val, duration, step_size, clear)

    def run(self):
        doubleBlink = False
        while not self.__signalExit__:
            closeT = 0.1
            openT = 0.15
            self.add(self.open, self.closed, closeT)
            self.add(self.closed, self.open, openT)
            self.wait(closeT + openT)
            if doubleBlink:
                doubleBlink = False
            else:
                waitTime = random.uniform(0.0, 10.0)
                waitTime = waitTime * (1.0-self.agitation)
                waitTime += 4  # add minimum wait time
                self.wait(waitTime)
                if random.uniform(0.0, 1.0) > 0.8:
                    doubleBlink = True
        logging.debug('blinking finished')

class HeadTurnAngularVelocity(StrategyThread):
    def __init__(self, main_thread, agitation=0.5):
        StrategyThread.__init__(self, main_thread, 'HeadTurnAngularVelocity')
        self.agitation = agitation
        self.servo = self.main_thread.get_servo('head')
        self.velocity = 80  # turn speed in degrees per second

    def run(self):
        while not self.__signalExit__:
            # turn
            newAngle = random.uniform(0.0, 180.0)
            currentAngle = self.servo.pwm_to_angle(self.servo.current_val)
            deltaAngle = newAngle - currentAngle
            if deltaAngle < 0:
                deltaAngle *= -1
            turnTime = deltaAngle / self.velocity
            self.servo.add(currentAngle, newAngle, turnTime, 1.0, True)
            self.wait(turnTime)
            # wait
            waitTime = random.uniform(3.0, 30.0) * (1.5-self.agitation)
            self.wait(waitTime)


class HeadTurnAgitation(StrategyThread):
    """Looks to different spots faster and more frequently if more agitated.
    agitation: float between 0 and 1
    """
    def __init__(self, main_thread, agitation=0.5):
        StrategyThread.__init__(self, main_thread, 'HeadTurnAgitation')
        self.agitation = agitation
        self.servo = self.main_thread.get_servo('head')
        self.maxAngleVelocity = 30  # degrees per second

    def run(self):
        last_angle = 90.0  # assuming a default
        while not self.__signalExit__:
            waitTime = random.uniform(20.0, 30.0) * (1.0-self.agitation)
            logging.debug('wait %f' % waitTime)
            self.wait(waitTime)
            head_angle = random.uniform(0.0, 180.0)
            turnTime = random.uniform(4.0, 20.0) * (1.0-self.agitation)
            deltaAngle = head_angle - last_angle
            if deltaAngle < 0:
                deltaAngle *= -1
            angleVelocity = deltaAngle / turnTime
            if angleVelocity > self.maxAngleVelocity:
                turnTime = deltaAngle / self.maxAngleVelocity
            # logging.debug('%f %f %f' % (last_angle, head_angle, turnTime))
            self.servo.add(float('nan'), head_angle, turnTime, 1.0, True)
            self.wait(turnTime)
            last_angle = head_angle
        logging.debug('looking finished')

class AutoStrategy(StrategyThread):
    """
    Let's a single owl be more or less agitated
    """
    def __init__(self, main_thread):
        StrategyThread.__init__(self, main_thread, 'AutoStrategy')

    def run(self):
        logging.debug('- using AutoStrategy.run')

        # background breathing
        breathing = BreathingAgitation(self.main_thread)
        # breathing = HeartbeatAgitation(self.main_thread)
        breathing.start()

        blinking = BlinkingAgitation(self.main_thread)
        blinking.start()

        # looking = HeadTurnAgitation(self.main_thread)
        looking = HeadTurnAngularVelocity(self.main_thread)
        looking.start()

        while not self.__signalExit__:
            self.wait(15)

            agitation = random.uniform(0.0, 1.0)
            agitation = 0.5
            logging.debug("setting agitation to %f" % agitation)

            breathing.agitation = agitation
            blinking.agitation = agitation
            looking.agitation = agitation

        # wait for subthread to finish
        breathing.signal_exit()
        blinking.signal_exit()
        looking.signal_exit()
        while breathing.is_alive() or blinking.is_alive() or looking.is_alive():
            logging.debug('...waiting for breathing, blinking and looking to finish gracefully...')
            sleep(0.01)

        logging.debug('SimpleRandomizedStrategy finished')
