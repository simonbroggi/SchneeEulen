
import logging
import threading
import time
import random
from time import sleep
from strategies.base import StrategyThread

class Dancer(StrategyThread):
    body_parts = ['eye_left', 'eye_right', 'body']

    def __init__(self, main_thread):
        """
        :param main_thread: SnowlyServer
        :return:
        """
        StrategyThread.__init__(self, main_thread, 'Dancer')

    def lightup(self):
        # fade down all leds
        owls = self.main_thread.get_client_ids()
        logging.debug('got owls %s' % owls)
        body_parts = ['eye_left', 'eye_right', 'body']
        for part in body_parts:
            self.main_thread.send_command(owls, {
                'command': 'dim',
                'id': part,
                'end_val': 0.0,
                'duration': 2.0,
                'step': 1,
                'clear': True
            })
        for part in body_parts:
            self.main_thread.send_command(owls, {
                'command': 'dim',
                'id': part,
                'start_val': 0.0,
                'end_val': 1.0,
                'duration': 4.0,
                'step': 1,
                'clear': False
            })

        self.wait(7.0)

    def run(self):
        logging.debug('- using Dancer.run')
        self.main_thread.send_command(self.main_thread.get_client_ids(), {
            'command': 'switch_strategy',
            'strategy': None
        })
        self.wait(5.0)

        logging.debug('- switch to direct control ---------------------->')
        run_startup = True
        duration = 180.0

        start_time = time.time()
        while not self.__signalExit__ and time.time() - start_time < duration:
            logging.debug('- waiting for clients to sync')
            self.main_thread.send_command(self.main_thread.get_client_ids(), {
                'command': 'switch_strategy',
                'strategy': None
            })

            self.lightup()
            common_head_angle = 0

            # self.main_thread.send_command({
            #     'command': 'sync'
            # })
            # self.wait(2.0)

            owls = self.main_thread.get_client_ids()
            for owl in owls:
                    self.main_thread.send_command([owl], {
                        'command': 'move',
                        'id': 'head',
                        'end_angle': common_head_angle,
                        'duration': 2.5,
                        'clear': False
                    })

            self.wait(1)

        logging.debug('Lightup finished')
