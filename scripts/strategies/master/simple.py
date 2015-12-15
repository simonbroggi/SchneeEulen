
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

    def startup(self):
        # fade down all leds
        owls = self.main_thread.get_client_ids()
        logging.debug('got owls %s' % owls)
        body_parts = ['eye_left', 'eye_right', 'body']
        for owl in owls:
            for part in body_parts:
                self.main_thread.send_command([owl], {
                    'command': 'dim',
                    'id': part,
                    'end_val': 0.0,
                    'duration': 4.0,
                    'step': 2,
                    'clear': True
                })
        self.wait(5)

    def run(self):
        logging.debug('- using SimpleMasterStrategy.run adv')
        body_parts = ['eye_left', 'eye_right', 'body']

        run_startup = True
        while not self.__signalExit__:
            logging.debug('- waiting for clients to sync')
            common_head_angle = random.uniform(0.0, 180.0)

            # self.main_thread.send_command({
            #     'command': 'sync'
            # })
            # self.wait(2.0)

            owls = self.main_thread.get_client_ids()
            if run_startup and len(owls) > 0:
                self.startup()
                run_startup = False

            if not run_startup:
                logging.debug('- got owls %s' % owls)
                for owl in owls:
                    logging.debug("owl %s" % owl)
                    logging.debug("clientsbyid %s" % self.main_thread.clientsById)

                    for part in body_parts:
                        self.main_thread.send_command([owl], {
                            'command': 'dim',
                            'id': part,
                            'end_val': 1.0,
                            'duration': 0.1,
                            'step': 4,
                            'clear': True
                        })
                        self.main_thread.send_command([owl], {
                            'command': 'dim',
                            'id': part,
                            'end_val': 0.0,
                            'duration': 0.1,
                            'step': 4
                        })

                    self.wait(0.25)

                for owl in owls:
                    self.main_thread.send_command([owl], {
                        'command': 'move',
                        'id': 'head',
                        'end_angle': common_head_angle,
                        'duration': 4.0,
                        'clear': False
                    })
            # self.main_thread.send_command(self.main_thread.get_client_ids(), {
            #     'command': 'dim',
            #     'id': 'eye_left',
            #     'start_val': 0.0,
            #     'end_val': 1.0,
            #     'duration': 1.0,
            #     'step': 1,
            #     'clear': False
            # })
            #
            # #servo.add(data['start_angle'], data['end_angle'], data['duration'], data['step'], data['clear'])
            # self.main_thread.send_command(self.main_thread.get_client_ids(), {
            #     'command': 'move',
            #     'id': 'head',
            #     "start_angle": float('nan'),
            #     "end_angle": random.uniform(0.0, 180.0),
            #     'duration': 4.0,
            #     'step': 1,
            #     'clear': False
            # })
            self.wait(10.0)

        logging.debug('SimpleMasterStrategy finished')
