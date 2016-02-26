
import logging
import threading
import time
import random
import consts
from time import sleep
from strategies.base import StrategyThread

class Idle(StrategyThread):
    body_parts = ['eye_left', 'eye_right', 'body']

    def __init__(self, main_thread):
        """
        :param main_thread: SnowlyServer
        :return:
        """
        StrategyThread.__init__(self, main_thread, 'Idle')

    def run(self):
        logging.debug('- using Idle.run')
        self.last_update = time.time()

        self.main_thread.send_command(self.main_thread.get_client_ids(), {
            'command': 'switch_strategy',
            'strategy': None
        })

        logging.debug('- switch to direct control ---------------------->')

        start_time = time.time()
        timeout = consts.IDLE_TIMEOUT
        while not self.__signalExit__ and time.time() - self.last_update < timeout:
            # keep clients idle
            self.main_thread.send_command(self.main_thread.get_client_ids(), {
                'command': 'switch_strategy',
                'strategy': None
            })
            #logging.info('-idle keepalive = %s' % self.last_update)
            self.wait(2.0)

        logging.debug('Idle finished')
