
import logging
import threading
import pigpio
from time import sleep
from base import BaseStrategy

class Breathing(BaseStrategy):
    def __init__(self, main_thread):
        BaseStrategy.__init__(self, main_thread)

    def run(self):
        while not self.__signalExit__:
            body_dimmer = self.main_thread.get_dimmer('eye_left')
            #logging.debug('**breath start**')
            body_dimmer.add(0.0, 1.0, 1.0, 2)
            body_dimmer.add(1.0, 0.0, 1.0, 2)
            self.wait(3)

        logging.debug('breathing finished')


class SimpleRandomizedStrategy(BaseStrategy):
    """
    Let's a single snow hare run step-by-step linearly through all boxes.
    """
    def __init__(self, main_thread):
        BaseStrategy.__init__(self, main_thread)

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

        while not self.__signalExit__:
            servo = self.main_thread.get_servo('head')
            servo.add(0, 180.0, 1.0, 4.0)
            #servo.add(180.0, 0, 3.0, 4.0)
            #logging.debug("body_dimmer start")
            #body_dimmer = self.main_thread.get_dimmer('eye_left')
            #body_dimmer.add(0.0, 1.0, 1.0, 1, False)
            #body_dimmer.add(1.0, 0.0, 1.0, -1)

            logging.debug("randomized self.wait(5)")
            self.wait(4.0)

        # wait for subthread to finish
        breathing.signal_exit()
        while breathing.is_alive():
            logging.debug('...waiting for breathing to finish gracefully...')
            sleep(0.01)

        logging.debug('SimpleRandomizedStrategy finished')
