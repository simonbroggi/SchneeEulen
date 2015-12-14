
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
            breathTime = 8.0 * (1.0-self.agitation)
            inhaleTime = breathTime * 0.4
            exhaleTime = breathTime - inhaleTime
            self.body_dimmer.add(0.2, 1.0, inhaleTime, 2)
            self.body_dimmer.add(1.0, 0.2, exhaleTime, 2)
            self.wait(breathTime)
        logging.debug('breathing finished')

class BlinkingAgitation(StrategyThread):
    """Blinks (with both eyes) more frequent when agitation is higher.
    agitation: float between 0 and 1
    """
    def __init__(self, main_thread, agitation = 0.5):
        StrategyThread.__init__(self, main_thread, 'BlinkingAgitation')
        self.agitation = agitation
        self.eye_left = self.main_thread.get_dimmer('eye_left')
        self.eye_right = self.main_thread.get_dimmer('eye_right')

    def run(self):
        while not self.__signalExit__:
            self.eye_left.add(0.3, 0.05, 0.1, 6)
            self.eye_left.add(0.05, 0.3, 0.1, 6)
            self.eye_right.add(0.3, 0.05, 0.1, 6)
            self.eye_right.add(0.05, 0.3, 0.1, 6)
            waitTime = random.uniform(5.0, 20.0)
            waitTime = waitTime * (1.0-self.agitation)
            waitTime += 0.3 # add minimum wait time
            self.wait(waitTime)
        logging.debug('blinking finished')

class LookingAgitation(StrategyThread):
    """Looks to different spots faster and more frequently if more agitated.
    agitation: float between 0 and 1
    """
    def __init__(self, main_thread, agitation=0.5):
        StrategyThread.__init__(self, main_thread, 'LookingAgitation')
        self.agitation = agitation
        self.servo = self.main_thread.get_servo('head')

    def run(self):
        while not self.__signalExit__:
            waitTime = random.uniform(20.0, 30.0) * (1.0-self.agitation)
            logging.debug('wait %f' % waitTime)
            self.wait(waitTime)
            head_angle = random.uniform(0.0, 180.0)
            turnTime = random.uniform(4.0, 20.0) * (1.0-self.agitation)
            #logging.debug('%f %f %f' % (last_angle, head_angle, turnTime))
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
        breathing.start()

        blinking = BlinkingAgitation(self.main_thread)
        blinking.start()

        looking = LookingAgitation(self.main_thread)
        looking.start()

        while not self.__signalExit__:
            self.wait(10)

            agitation = random.uniform(0.0, 1.0)
            logging.debug("setting agitation to %f"%agitation)

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
