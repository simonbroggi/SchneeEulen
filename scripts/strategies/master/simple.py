
import logging
import threading
import time
import random
from time import sleep
from strategies.base import StrategyThread

class SimpleMasterStrategy(StrategyThread):
    all_owls = ['KEVIN', 'MAJA', 'LISA', 'MARTHA', 'KLAUS']
    body_parts = ['eye_left', 'eye_right', 'body']

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

        for owl in owls:
            for part in self.body_parts:
                self.main_thread.send_command([owl], {
                    'command': 'dim',
                    'id': part,
                    'end_val': 0.0,
                    'duration': 4.0,
                    'step': 2,
                    'clear': True
                })
        self.wait(5)

    def stripes(self, owls):
        start_time = time.time()
        duration = random.uniform(30.0, 70.0)
        wait_time = random.uniform(1.0,5.0)
        while not self.__signalExit__ and time.time()-start_time < duration:
            for owl in owls:
                logging.debug("owl %s" % owl)
                logging.debug("clientsbyid %s" % self.main_thread.clientsById)

                for part in self.body_parts:
                    self.main_thread.send_command([owl], {
                        'command': 'dim',
                        'id': part,
                        'end_val': 1.0,
                        'duration': 0.5,
                        'step': 4,
                        'clear': True
                    })
                    self.main_thread.send_command([owl], {
                        'command': 'dim',
                        'id': part,
                        'end_val': 0.0,
                        'duration': 0.5,
                        'step': 4
                    })

                self.wait(0.33)
            self.wait(wait_time)

    def dimAllTo(self, val_body, val_eyes, duration):
        owls = self.main_thread.get_client_ids()
        logging.debug('got owls %s' % owls)
        if self.__signalExit__:
            return

        self.main_thread.send_command(owls, {
            'command': 'dim',
            'id': 'body',
            'end_val': val_body,
            'duration': duration,
            'step': 1,
            'clear': False
        })
        eyes = ['eye_left', 'eye_right']
        for part in eyes:
            self.main_thread.send_command(owls, {
                'command': 'dim',
                'id': part,
                'end_val': val_eyes,
                'duration': duration,
                'step': 1,
                'clear': False
            })

    def head_shake(self, owls):
        start_time = time.time()
        duration = random.uniform(20.0, 60.0)
        wait_time = random.uniform(1.0,5.0)

        while not self.__signalExit__ and time.time()-start_time < duration:
            common_head_angle = random.uniform(0.0, 180.0)
            for owl in owls:
                self.main_thread.send_command([owl], {
                    'command': 'move',
                    'id': 'head',
                    'end_angle': common_head_angle,
                    'duration': 4.0,
                    'clear': False
                })

            self.wait(wait_time)

    def run(self):
        logging.debug('- using SimpleMasterStrategy.run adv')

        self.main_thread.send_command(self.main_thread.get_client_ids(), {
            'command': 'switch_strategy',
            'strategy': 'NightBlinking'
        })

        self.wait(10.0)

        logging.debug('- switch to direct control ---------------------->')
        run_startup = True
        duration = 30.0
        start_time = time.time()
        while not self.__signalExit__ and time.time() - start_time < duration:
            logging.debug('- waiting for clients to sync')
            self.main_thread.send_command(self.main_thread.get_client_ids(), {
                'command': 'switch_strategy',
                'strategy': None
            })

            common_head_angle = random.uniform(0.0, 180.0)

            # self.main_thread.send_command({
            #     'command': 'sync'
            # })
            # self.wait(2.0)

            #owls = self.main_thread.get_client_ids()
            owls = self.all_owls
            owls = ['KLAUS', 'LISA', 'MAJA', 'KEVIN', 'MARTHA']

            if run_startup and len(owls) > 0:
                self.startup()
                run_startup = False

            if not run_startup:
                logging.debug('- got owls %s' % owls)

                self.stripes(owls)
                self.dimAllTo(0.33, 0.03, 1.0)
                self.wait(2.0)

                self.head_shake(owls)

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
            self.wait(random.uniform(2.0, 12.0))

        logging.debug('SimpleMasterStrategy finished')
