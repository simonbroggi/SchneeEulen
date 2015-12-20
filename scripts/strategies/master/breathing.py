
import logging
import threading
import random
import time
import math
from time import sleep
from strategies.base import StrategyThread

class Breathing(StrategyThread):
    body_parts = ['eye_left', 'eye_right', 'body']
    all_owls = ['KEVIN', 'MAJA', 'LISA', 'MARTHA', 'KLAUS']

    def __init__(self, main_thread):
        """
        :param main_thread: SnowlyServer
        :return:
        """
        StrategyThread.__init__(self, main_thread, 'Breathing')

    def startup(self):
        # fade down all owls
        self.main_thread.send_command(self.main_thread.get_client_ids(), {
                'command': 'switch_strategy',
                'strategy': None
            })

        for part in self.body_parts:
            self.main_thread.send_command(self.main_thread.get_client_ids(), {
                'command': 'dim',
                'id': part,
                'end_val': 0.0,
                'duration': 2.0,
                'step': 1,
                'clear': True
            })
        self.wait(3.0)

    def run(self):
        logging.debug('Breathing.run')
        self.wait(5)

        start_time = time.time()
        duration = random.uniform(60.0, 120.0)

        while not self.__signalExit__:
            active_strategy = 'BreathAndLook'
            self.startup()

            while not self.__signalExit__ and time.time() - start_time < duration:
                self.main_thread.send_command(self.main_thread.get_client_ids(), {
                    'command': 'switch_strategy',
                    'strategy': active_strategy
                })
                self.wait(2.0)

            # terminate
            self.signal_exit()

        logging.debug('Breathing finished')
