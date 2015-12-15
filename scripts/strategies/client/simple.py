
import logging
import threading
import pigpio
import random
from time import sleep
from strategies.base import StrategyThread

class Breathing(StrategyThread):
    def __init__(self, main_thread):
        StrategyThread.__init__(self, main_thread)

    def run(self):
        while not self.__signalExit__:
            body_dimmer = self.main_thread.get_dimmer('body')
            #logging.debug('**breath start**')
            body_dimmer.add(0.2, 1.0, 2.0, 2, True)
            body_dimmer.add(1.0, 0.2, 2.0, 2)
            self.wait(4.1)

        logging.debug('breathing finished')


class SimpleRandomizedStrategy(StrategyThread):
    """
    Let's a single snow hare run step-by-step linearly through all boxes.
    """
    def __init__(self, main_thread):
        StrategyThread.__init__(self, main_thread)

    def twinkle(self, eye=0):
        return

    def breathe(self):
        while not self.__signalExit__:
            logging.debug("-- breathing: live from subthread")
            sleep(3.0)

    def run(self):
        logging.debug('- using RandomStrategy.run')

        # background breathing
        breathing = Breathing(self.main_thread)
        breathing.start()

        head_angle = 0.0
        last_angle = 0.0

        while not self.__signalExit__:
            # servo = self.main_thread.get_servo('head')
            #
            # head_angle = random.uniform(0.0, 180.0)
            # servo.add(last_angle, head_angle, random.uniform(2.0, 10.0), 1.0, True)
            # last_angle = head_angle
            #
            # eye_left = self.main_thread.get_dimmer('eye_left')
            # eye_left.add(0.0, 1.0, 2.0, 2, True)
            # eye_left.add(1.0, 0.0, 2.0, 2)
            #
            # eye_right = self.main_thread.get_dimmer('eye_right')
            # eye_right.add(0.0, 1.0, 2.0, 2, True)
            # eye_right.add(1.0, 0.0, 2.0, 2)
            #
            # #servo.add(180.0, 0, 3.0, 4.0)
            # #logging.debug("body_dimmer start")
            # #body_dimmer = self.main_thread.get_dimmer('eye_left')
            # #body_dimmer.add(0.0, 1.0, 1.0, 1, False)
            # #body_dimmer.add(1.0, 0.0, 1.0, -1)
            #
            # logging.debug("randomized self.wait(5)")
            self.wait(25)

        # wait for subthread to finish
        breathing.signal_exit()
        while breathing.is_alive():
            logging.debug('...waiting for breathing to finish gracefully...')
            sleep(0.01)

        logging.debug('SimpleRandomizedStrategy finished')
