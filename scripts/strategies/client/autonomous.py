
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

class HeartbeatBody(StrategyThread):
    """body light pulsate like a heartbeat.
    Faster heartbeat when agitation is higher.
    """
    def __init__(self, main_thread, agitation=0.5):
        StrategyThread.__init__(self, main_thread, 'HeartbeatBody')
        self.agitation = agitation
        self.body_dimmer = self.main_thread.get_dimmer('body')
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
        logging.debug('heartbeat body finished')

class BreathAndLook(StrategyThread):
    def __init__(self, main_thread, agitation=0.5):
        StrategyThread.__init__(self, main_thread, 'BreathAndLook')

    def run(self):
        breath = BreathingAgitation(self.main_thread, random.uniform(0.1, 0.9))
        breath.start()
        looking = HeadTurnAngularVelocity(self.main_thread, random.uniform(0.1, 0.9))
        looking.start()
        blinking = BlinkingAgitation(self.main_thread)
        blinking.start()
        while not self.__signalExit__:
            self.wait(0.3)
        breath.signal_exit()
        looking.signal_exit()
        blinking.signal_exit()

class HeartbeatAndLook(StrategyThread):
    def __init__(self, main_thread, agitation=0.5):
        StrategyThread.__init__(self, main_thread, 'HeartbeatAndLook')

    def run(self):
        heartbeat = HeartbeatBody(self.main_thread)
        heartbeat.start()
        looking = HeadTurnAngularVelocity(self.main_thread)
        looking.start()
        blinking = BlinkingAgitation(self.main_thread)
        blinking.start()
        while not self.__signalExit__:
            self.wait(0.3)
        heartbeat.signal_exit()
        looking.signal_exit()
        blinking.signal_exit()

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
        self.delta_angle = 35
        self.t = 0.055  # 0.004 # 0.53 for a No
        self.bright = 0.07
        self.dark = 0.02

    def run(self):
        self.body.add(float('nan'), self.dark, 1, 1, True)
        self.servo.add(float('nan'), self.rest_angle, 1, 1, True)
        self.eye_left.add(float('nan'), 0.02, 1)
        self.eye_right.add(float('nan'), 0.02, 1)
        self.wait(3)

        step = 30
        lightStep = 3
        posAngle = self.rest_angle + self.delta_angle + 10
        negAngle = self.rest_angle - self.delta_angle
        self.servo.add(float('nan'), posAngle, self.t, step)
        self.body.add(float('nan'), self.bright, self.t, lightStep)
        self.servo.add(float('nan'), negAngle, self.t, step)
        self.body.add(float('nan'), self.dark, self.t, lightStep)
        self.servo.add(float('nan'), posAngle, self.t, step)
        self.body.add(float('nan'), self.bright, self.t, lightStep)
        self.servo.add(float('nan'), negAngle, self.t, step)
        self.body.add(float('nan'), self.dark, self.t, lightStep)
        self.servo.add(float('nan'), posAngle, self.t, step)
        self.body.add(float('nan'), self.bright, self.t, lightStep)
        self.servo.add(float('nan'), negAngle, self.t, step)
        self.body.add(float('nan'), self.dark, self.t, lightStep)
        self.servo.add(float('nan'), posAngle, self.t, step)
        self.body.add(float('nan'), self.bright, self.t, lightStep)
        self.servo.add(float('nan'), negAngle, self.t, step)
        self.body.add(float('nan'), self.dark, self.t, lightStep)
        self.servo.add(float('nan'), self.rest_angle, self.t*0.5)
        self.wait(self.t * 8.5)

class SimpleAuto(StrategyThread):

    def __init__(self, main_thread):
        StrategyThread.__init__(self, main_thread, 'SimpleAuto')
        self.servo = self.main_thread.get_servo('head')
        self.body = self.main_thread.get_dimmer('body')
        self.eye_left = self.main_thread.get_dimmer('eye_left')
        self.eye_right = self.main_thread.get_dimmer('eye_right')

    def lookAroundAndBreath(self, t=20, agitation=0.5):
        looking = HeadTurnAngularVelocity(self.main_thread)
        breathing = BreathingAgitation(self.main_thread, agitation)
        blinking = BlinkingAgitation(self.main_thread, agitation)
        blinking.start()
        breathing.start()
        self.wait(0.7)
        looking.start()
        self.wait(t - 0.7)
        looking.signal_exit()
        breathing.signal_exit()
        blinking.signal_exit()
        while looking.is_alive() or breathing.is_alive() or blinking.is_alive():
            self.wait(0.05)

    def heartbeatBody(self, beat_start=0.2, beat_end=0.75, t=16):
        beat_delta = beat_start-beat_end
        if beat_delta < 0:
            beat_delta *= -1
        a_step = beat_delta / t
        heartbeat = HeartbeatBody(self.main_thread, beat_start)
        heartbeat.eye_delta = -0.1
        heartbeat.start()
        if beat_end < beat_start:
            while heartbeat.agitation > beat_end and not self.__signalExit__:
                self.wait(1)
                heartbeat.agitation -= a_step
        else:
            while heartbeat.agitation < beat_end and not self.__signalExit__:
                self.wait(1)
                heartbeat.agitation += a_step
        heartbeat.signal_exit()

    def heartbeat(self, beat_start=0.2, beat_end=0.75, t=16):
        beat_delta = beat_start-beat_end
        if beat_delta < 0:
            beat_delta *= -1
        a_step = beat_delta / t
        heartbeat = HeartbeatAgitation(self.main_thread, beat_start)
        heartbeat.eye_delta = -0.1
        heartbeat.start()
        if beat_end < beat_start:
            while heartbeat.agitation > beat_end and not self.__signalExit__:
                self.wait(1)
                heartbeat.agitation -= a_step
        else:
            while heartbeat.agitation < beat_end and not self.__signalExit__:
                self.wait(1)
                heartbeat.agitation += a_step
        heartbeat.signal_exit()

    def lookAndHeartbeat(self):
        self.turnFar()
        heartbeat = HeartbeatAgitation(self.main_thread, 0.75)
        heartbeat.eye_delta = -0.1
        heartbeat.start()
        while not self.__signalExit__ and heartbeat.agitation > 0.2:
            self.wait(1)
            heartbeat.eye_delta -= 0.00005
            heartbeat.agitation -= 0.03
        heartbeat.signal_exit()

    def turnFar(self, velocity=100):
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
        turnTime = deltaAngle / velocity
        self.servo.add(float('nan'), newAngle, turnTime, 1.0, True)
        self.wait(turnTime)

    def fadeOut(self, t=1.5):
        self.body.add(float('nan'), 0.0, t, 1, True)
        self.eye_left.add(float('nan'), 0.00, t, 1, True)
        self.eye_right.add(float('nan'), 0.00, t, 1, True)
        self.wait(t)

    def lookyEyes(self, n=3):
        self.fadeOut(5)
        self.servo.add(float('nan'), 70, 2, 1, True)
        brightEyes = 0.25
        darkEyes = 0.01
        dimDownTime = 6
        velocity = 15
        i = 0
        while i < n:
            i += 1
            currentAngle = self.servo.pwm_to_angle(self.servo.current_val)
            newAngle = random.uniform(0.0, 180.0)
            deltaAngle = newAngle - currentAngle
            if deltaAngle < 0:
                deltaAngle *= -1
            turnTime = deltaAngle / velocity
            self.servo.add(float('nan'), newAngle, turnTime, 1, False)
            self.eye_left.add(float('nan'), brightEyes, turnTime, 1, False)
            self.eye_right.add(float('nan'), brightEyes, turnTime, 1, False)
            self.wait(turnTime)

            self.eye_left.add(float('nan'), darkEyes, dimDownTime, 1, False)
            self.eye_right.add(float('nan'), darkEyes, dimDownTime, 1, False)
            self.wait(dimDownTime)

    def cleanUntilDone(self):
        self.cleaning()
        while random.uniform(0.0, 1.0) > 0.6:
            if random.uniform(0.0, 1.0) > 0.7:
                self.turnFar()
                self.wait(1.3)
                self.cleaning()
            else:
                self.wait(0.3)
                self.cleaning()

    def sayNo(self):
        rest_angle = 70
        delta_angle = 35
        t = 0.53

        self.servo.add(float('nan'), rest_angle, 1, 1, True)
        self.wait(1.1)

        step = 30
        posAngle = rest_angle + delta_angle
        negAngle = rest_angle - delta_angle
        self.servo.add(float('nan'), negAngle, t, step)
        self.servo.add(float('nan'), posAngle, t, step)
        self.servo.add(float('nan'), negAngle, t, step)
        self.servo.add(float('nan'), posAngle, t, step)
        self.servo.add(float('nan'), negAngle, t, step)
        self.servo.add(float('nan'), posAngle, t, step)
        self.servo.add(float('nan'), negAngle, t, step)
        self.servo.add(float('nan'), posAngle, t, step)
        self.servo.add(float('nan'), rest_angle, t*0.5)
        self.wait(t * 8.5)

    def cleaning(self):
        rest_angle = 70
        delta_angle = 35
        t = 0.055  # 0.004 # 0.53 for a No
        bright = 0.07
        dark = 0.02

        self.body.add(float('nan'), bright, 1, 1, True)
        self.servo.add(float('nan'), rest_angle, 1, 1, True)
        self.eye_left.add(float('nan'), 0.02, 1, 1, True)
        self.eye_right.add(float('nan'), 0.02, 1, 1, True)
        self.wait(1.1)

        step = 30
        lightStep = 3
        posAngle = rest_angle + delta_angle
        negAngle = rest_angle - delta_angle
        self.servo.add(float('nan'), negAngle, t, step)
        self.body.add(float('nan'), dark, t, lightStep)
        self.servo.add(float('nan'), posAngle, t, step)
        self.body.add(float('nan'), bright, t, lightStep)
        self.servo.add(float('nan'), negAngle, t, step)
        self.body.add(float('nan'), dark, t, lightStep)
        self.servo.add(float('nan'), posAngle, t, step)
        self.body.add(float('nan'), bright, t, lightStep)
        self.servo.add(float('nan'), negAngle, t, step)
        self.body.add(float('nan'), dark, t, lightStep)
        self.servo.add(float('nan'), posAngle, t, step)
        self.body.add(float('nan'), bright, t, lightStep)
        self.servo.add(float('nan'), negAngle, t, step)
        self.body.add(float('nan'), dark, t, lightStep)
        self.servo.add(float('nan'), posAngle, t, step)
        self.body.add(float('nan'), bright, t, lightStep)
        self.servo.add(float('nan'), rest_angle, t*0.5)
        self.wait(t * 8.5)

    def newR(self, lastR, n):
        r = random.randint(0, n)
        while r == lastR:
            r = random.randint(0, n)
        return r

    def run(self):
        while not self.__signalExit__:
            self.lookyEyes(random.randint(2, 5))
            self.wait(3)

        while not self.__signalExit__:
            self.heartbeatBody(0.2, 0.75, 20)
            self.sayNo()
            self.wait(1)
            self.heartbeatBody(0.75, 0.2, 20)
            self.sayNo()
            self.wait(1)

        while not self.__signalExit__:
            self.lookAroundAndBreath(25, 1)
            self.sayNo()
            self.wait(1)
            self.lookAroundAndBreath(25, 0)
            self.sayNo()
            self.wait(1)

        self.heartbeat(0.3, 1, 20)

        self.lookyEyes(random.randint(2, 5))
        self.lookAndHeartbeat()
        self.lookAroundAndBreath(15, 0.5)
        self.cleanUntilDone()
        self.lookAroundAndBreath(15, 0)
        self.sayNo()
        self.lookAroundAndBreath(15, 1)

        r = -1
        while not self.__signalExit__:
            r = self.newR(r, 5)
            logging.debug("******** SimpleAuto doing %i" % r)
            if r == 0:
                self.lookyEyes(random.randint(2, 5))
            elif r == 1:
                self.lookAndHeartbeat()
            elif r == 2:
                self.lookAroundAndBreath(random.uniform(20, 50), random.uniform(0.2, 0.8))
            elif r == 3:
                self.cleanUntilDone()
            elif r == 4:
                self.lookAroundAndBreath(random.uniform(10, 30), random.uniform(0, 1))
            elif r == 5:
                self.sayNo()

class AutoStrategy(StrategyThread):
    """
    Let's a single owl be more or less agitated
    """
    def __init__(self, main_thread):
        StrategyThread.__init__(self, main_thread, 'AutoStrategy')

    def run(self):
        logging.debug('- using AutoStrategy.run')
        cleaning = CleaningStrategy(self.main_thread)
        cleaning.start()
        self.wait(0.3)
        while cleaning.is_alive():
            self.wait(0.1)
        self.wait(0.2)

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
                heartbeat.agitation -= 0.03
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
