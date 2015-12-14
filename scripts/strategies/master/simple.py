
import logging
import threading
import pigpio
import random
from time import sleep
from strategies.base import StrategyThread

class SimpleMasterStrategy(StrategyThread):
    """
    Let's a single snow hare run step-by-step linearly through all boxes.
    """
    def __init__(self, main_thread):
        """
        :param main_thread: SnowlyServer
        :return:
        """
        StrategyThread.__init__(self, main_thread)

    def run(self):
        logging.debug('- using RandomStrategy.run')

        while not self.__signalExit__:
            logging.debug('- waiting for clients to sync')
            # self.main_thread.send_command({
            #     'command': 'sync'
            # })
            # self.wait(2.0)

            self.main_thread.send_command(self.main_thread.get_client_ids(), {
                'command': 'dim',
                'id': 'eye_left',
                'start_val': 0.0,
                'end_val': 1.0,
                'duration': 1.0,
                'step': 1,
                'clear': False
            })

            #servo.add(data['start_angle'], data['end_angle'], data['duration'], data['step'], data['clear'])
            self.main_thread.send_command(self.main_thread.get_client_ids(), {
                'command': 'move',
                'id': 'head',
                "start_angle": float('nan'),
                "end_angle": random.uniform(0.0, 180.0),
                'duration': 4.0,
                'step': 1,
                'clear': False
            })

            self.wait(5.0)

        logging.debug('SimpleRandomizedStrategy finished')
