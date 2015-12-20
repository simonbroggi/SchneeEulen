
import logging
import threading
import time
import random
from time import sleep
from strategies.base import StrategyThread

class Sleep(StrategyThread):
    body_parts = ['eye_left', 'eye_right', 'body']

    def __init__(self, main_thread):
        """
        :param main_thread: SnowlyServer
        :return:
        """
        StrategyThread.__init__(self, main_thread, 'Sleep')

    def fadedown(self):
        # fade down all leds
        owls = self.main_thread.get_client_ids()
        for part in self.body_parts:
            self.main_thread.send_command(owls, {
                'command': 'dim',
                'id': part,
                'end_val': 0,
                'duration': 1.0,
                'step': 1,
                'clear': True
            })
        self.wait(5)

    def run(self):
        logging.debug('- using Sleep.run')
        self.main_thread.send_command(self.main_thread.get_client_ids(), {
            'command': 'switch_strategy',
            'strategy': None
        })
        self.wait(5.0)

        logging.debug('- switch to direct control ---------------------->')
        self.fadedown()
        run_startup = True
        duration = 30.0

        start_time = time.time()
        while not self.__signalExit__ and time.time() - start_time < duration:
            self.main_thread.send_command(self.main_thread.get_client_ids(), {
                'command': 'switch_strategy',
                'strategy': None
            })

            self.wait(2.0)

        logging.debug('Sleep finished')
