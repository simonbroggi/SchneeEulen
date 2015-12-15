
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
    def __init__(self, main_thread, agitation=0.5):
        StrategyThread.__init__(self, main_thread, 'BreathingAgitation')
        self.agitation = agitation
        self.body_dimmer = self.main_thread.get_dimmer('body')
        self.dark = 0.15
        self.light = 0.6

    def run(self):
        while not self.__signalExit__:
            breathTime = 3.5 * (1.5-self.agitation)
            inhaleTime = breathTime * 0.42
            exhaleTime = breathTime - inhaleTime
            self.body_dimmer.add(float('nan'), self.light, inhaleTime, 1)
            self.body_dimmer.add(float('nan'), self.dark, exhaleTime, 1)
            self.wait(breathTime)
        logging.debug('breathing finished')

class HeartbeatAgitation(StrategyThread):
    """All lights pulsate like a heartbeat.
    Faster heartbeat when agitation is higher.
    """
    def __init__(self, main_thread, agitation=0.5):
        StrategyThread.__init__(self, main_thread, 'HeartbeatAgitation')
        self.agitation = agitation
        self.body_dimmer = self.main_thread.get_dimmer('body')
        self.eye_left = self.main_thread.get_dimmer('eye_left')
        self.eye_right = self.main_thread.get_dimmer('eye_right')
        self.low = 0.35
        self.mid = 0.65
        self.midLow = 0.45
        self.high = 1.0
        self.eye_delta = - 0.3

    def add(self, start_val, end_val, duration, step_size=2, clear=False):
        self.body_dimmer.add(start_val, end_val, duration, step_size, clear)
        eye_start = start_val + self.eye_delta
        if eye_start <= 0.0:
            eye_start = 0.0
        if eye_start >= 1.0:
            eye_start = 1.0
        eye_end = end_val + self.eye_delta
        if eye_end <= 0.0:
            eye_end = 0.0
        if eye_end >= 1.0:
            eye_end = 1.0
        self.eye_left.add(start_val + self.eye_delta, end_val + self.eye_delta, duration, step_size, clear)
        self.eye_right.add(start_val + self.eye_delta, end_val + self.eye_delta, duration, step_size, clear)

    def run(self):
        while not self.__signalExit__:
            beatTime = 1.0 * (1.5-self.agitation)
            first = beatTime * 0.2
            second = beatTime * 0.1
            third = beatTime * 0.22
            recover = beatTime - first - second - third
            self.add(float('nan'), self.mid, first, 2, True)
            self.add(float('nan'), self.midLow, second)
            self.add(float('nan'), self.high, third)
            self.add(float('nan'), self.low, recover)
            self.wait(beatTime + 0.3)
        logging.debug('heartbeat finished')

class BlinkingAgitation(StrategyThread):
    """Blinks (with both eyes) more frequent when agitation is higher.

    agitation: float between 0 and 1
    """
    def __init__(self, main_thread, agitation=0.5):
        StrategyThread.__init__(self, main_thread, 'BlinkingAgitation')
        self.agitation = agitation
        self.open = 0.10  # 0.3
        self.closed = 0.005  # 0.05
        self.eye_left = self.main_thread.get_dimmer('eye_left')
        self.eye_right = self.main_thread.get_dimmer('eye_right')

    def add(self, start_val, end_val, duration, step_size=2, clear=False):
        self.eye_left.add(start_val, end_val, duration, step_size, clear)
        self.eye_right.add(start_val, end_val, duration, step_size, clear)

    def run(self):
        doubleBlink = False
        while not self.__signalExit__:
            closeT = 0.18
            openT = 0.32
            self.add(float('nan'), self.closed, closeT)
            self.add(float('nan'), self.open, openT)
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

    def turnNow(self):
        # turn
        currentAngle = self.servo.pwm_to_angle(self.servo.current_val)
        newAngle = random.uniform(120.0, 180.0)
        if currentAngle > 120:
            newAngle = random.uniform(0.0, 60.0)
        elif currentAngle > 60:
            if random.uniform(0.0, 1.0) > 0.5:
                newAngle = 0
            else:
                newAngle = 180

        deltaAngle = newAngle - currentAngle
        if deltaAngle < 0:
            deltaAngle *= -1
        turnTime = deltaAngle / self.velocity
        self.servo.add(float('nan'), newAngle, turnTime, 1.0, True)

    def run(self):
        while not self.__signalExit__:
            # turn
            newAngle = random.uniform(0.0, 180.0)
            currentAngle = self.servo.pwm_to_angle(self.servo.current_val)
            deltaAngle = newAngle - currentAngle
            if deltaAngle < 0:
                deltaAngle *= -1
            turnTime = deltaAngle / self.velocity
            self.servo.add(float('nan'), newAngle, turnTime, 1.0, True)
            self.wait(turnTime)
            # wait
            waitTime = random.uniform(2.0, 10.0) * (1.5-self.agitation) * (1.5-self.agitation)
            self.wait(waitTime)

class CleaningStrategy(StrategyThread):
    """
    owl cleans itselve
    """
    def __init__(self, main_thread):
        StrategyThread.__init__(self, main_thread, 'CleaningStrategy')
        self.servo = self.main_thread.get_servo('head')
        self.body = self.main_thread.get_dimmer('body')
        self.eye_left = self.main_thread.get_dimmer('eye_left')
        self.eye_right = self.main_thread.get_dimmer('eye_right')
        self.rest_angle = 70
        self.delta_angle = 70
        self.t = 0.004

    def run(self):
        while not self.__signalExit__:

            self.body.add(float('nan'), 0.01, 2, 1, True)
            self.servo.add(float('nan'), self.rest_angle, 2, 1, True)
            self.wait(2)

            self.body.add(float('nan'), 1, self.t * 8.5)
            step = 10
            self.servo.add(float('nan'), self.rest_angle + self.delta_angle, self.t, step)
            self.servo.add(float('nan'), self.rest_angle - self.delta_angle, self.t, step)
            self.servo.add(float('nan'), self.rest_angle + self.delta_angle, self.t, step)
            self.servo.add(float('nan'), self.rest_angle - self.delta_angle, self.t, step)
            self.servo.add(float('nan'), self.rest_angle + self.delta_angle, self.t, step)
            self.servo.add(float('nan'), self.rest_angle - self.delta_angle, self.t, step)
            self.servo.add(float('nan'), self.rest_angle + self.delta_angle, self.t, step)
            self.servo.add(float('nan'), self.rest_angle - self.delta_angle, self.t, step)
            self.servo.add(float('nan'), self.rest_angle, self.t*0.5)
            self.wait(6)


class AutoStrategy(StrategyThread):
    """
    Let's a single owl be more or less agitated
    """
    def __init__(self, main_thread):
        StrategyThread.__init__(self, main_thread, 'AutoStrategy')

    def run(self):
        logging.debug('- using AutoStrategy.run CLEAN!!!')
        cleaning = CleaningStrategy(self.main_thread)
        cleaning.start()

        self.wait(200)
        cleaning.signal_exit()

        looking = HeadTurnAngularVelocity(self.main_thread)
        looking.start()

        while not self.__signalExit__:
            breathing = BreathingAgitation(self.main_thread)
            breathing.start()
            blinking = BlinkingAgitation(self.main_thread)
            blinking.start()
            looking.velocity = 60
            looking.agitation = 0.0
            self.wait(30)
            breathing.signal_exit()
            blinking.signal_exit()
            looking.velocity = 120
            looking.agitation = 0.9
            looking.turnNow()
            self.wait(2)
            heartbeat = HeartbeatAgitation(self.main_thread, 0.75)
            heartbeat.eye_delta = -0.1
            heartbeat.start()
            while not self.__signalExit__ and heartbeat.agitation > 0.2:
                self.wait(1)
                heartbeat.eye_delta -= 0.00005
                heartbeat.agitation -= 0.05
            heartbeat.signal_exit()

        # wait for subthread to finish
        breathing.signal_exit()
        blinking.signal_exit()
        looking.signal_exit()
        heartbeat.signal_exit()
        while breathing.is_alive() or blinking.is_alive() or looking.is_alive() or heartbeat.is_alive():
            logging.debug('...waiting for breathing, blinking and looking to finish gracefully...')
            sleep(0.01)

        logging.debug('SimpleRandomizedStrategy finished')
