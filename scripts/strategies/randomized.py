
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
            body_dimmer.add(0.1, 1.0, 1.0, 2.0, True)
            body_dimmer.add(1.0, 0.1, 1.0, 2.0)
            self.wait(5)

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
            # logging.debug('*twinkle*')
            # self.twinkle(0)
            # logging.debug('*wait 10s*')
            # self.wait(10.0)
            servo = self.main_thread.get_servo('head')
            servo.add(0, 180.0, 4.0, 2.0)
            self.wait(10)

        # wait for subthread to finish
        breathing.signal_exit()
        while breathing.is_alive():
            logging.debug('waiting for breathing to finish gracefully')
            sleep(0.01)

        logging.debug('SimpleRandomizedStrategy finished')
