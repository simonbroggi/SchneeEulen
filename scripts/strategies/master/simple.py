
import logging
import threading
import pigpio
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
            logging.debug("randomized self.wait(n)")

            self.main_thread.send_command(self.main_thread.get_client_ids(), {
                "action": "dimmer",
                "dimmer_id": "left_eye",
                "start_val": 0.0,
                "end_val": 1.0,
                "duration": 1.0,
                "step": 1
            })
            self.wait(5.0)

        logging.debug('SimpleRandomizedStrategy finished')
