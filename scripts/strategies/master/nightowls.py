
import logging
import threading
import random
import time
import math
from time import sleep
from strategies.base import StrategyThread

class NightOwls(StrategyThread):
    body_parts = ['eye_left', 'eye_right', 'body']
    all_owls = ['KEVIN', 'MAJA', 'LISA', 'MARTHA', 'KLAUS']

    def __init__(self, main_thread):
        """
        :param main_thread: SnowlyServer
        :return:
        """
        StrategyThread.__init__(self, main_thread, 'NightOwls')

    def startup(self):
        # fade down all owls to night mode
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

    def light_up(self):
        lo_state = 0.2
        self.main_thread.send_command(self.main_thread.get_client_ids(), {
            'command': 'dim',
            'id': 'body',
            'start_val': 0.0,
            'end_val': lo_state,
            'duration': 10.0,
            'step': 1,
            'clear': True
        })
        self.wait(random.uniform(3.0,5.0))
        for i in range(0,4):
            self.main_thread.send_command(self.main_thread.get_client_ids(), {
                'command': 'dim',
                'id': 'body',
                'start_val': lo_state,
                'end_val': 1.0,
                'duration': 2.0
            })
            self.main_thread.send_command(self.main_thread.get_client_ids(), {
                'command': 'dim',
                'id': 'body',
                'start_val': 1.0,
                'end_val': lo_state,
                'duration': 2.0
            })
            self.wait(2.0)

        self.wait(5)

    def light_down(self):
        lo_state = 0.0
        self.main_thread.send_command(self.main_thread.get_client_ids(), {
            'command': 'dim',
            'id': 'body',
            'start_val': float('nan'),
            'end_val': lo_state,
            'duration': 10.0,
            'step': 1,
            'clear': True
        })
        self.wait(random.uniform(3.0,5.0))
        for i in range(0,4):
            self.main_thread.send_command(self.main_thread.get_client_ids(), {
                'command': 'dim',
                'id': 'body',
                'start_val': float('nan'),
                'end_val': 1.0,
                'duration': 2.0
            })
            self.main_thread.send_command(self.main_thread.get_client_ids(), {
                'command': 'dim',
                'id': 'body',
                'start_val': float('nan'),
                'end_val': lo_state,
                'duration': 2.0
            })
            self.wait(2.0)

        self.wait(5)

    def wave(self):
        PI = 3.1415926535
        total_owls = len(self.main_thread.get_client_ids())

        start_time = time.time()
        while not self.__signalExit__ and time.time()-start_time < 30.0:
            t = 0
            while (not self.__signalExit__ and t < 2*PI):
                owl_count = 0
                for owl in self.main_thread.get_client_ids():
                    val = 0.5 + 0.5*math.sin(t - owl_count*2*PI/total_owls)
                    for part in self.body_parts:
                        self.main_thread.send_command([owl], {
                            'command': 'dim',
                            'id': part,
                            'end_val': val,
                            'duration': 0.1,
                            'step': 1,
                            'clear': True
                        })
                    owl_count += 1
                t += 0.1
                self.wait(0.1)

        self.wait(5)


    def run(self):
        logging.debug('NightOwls.run')

        self.wait(5)

        start_time = time.time()
        duration_phase_blinking = random.uniform(30.0, 60.0)
        while not self.__signalExit__:
            self.startup()

            # make sure all owls are ready
            self.wait(5)

            # PHASE 1: Night Blinking
            while not self.__signalExit__ and time.time() - start_time < duration_phase_blinking:
                self.main_thread.send_command(self.main_thread.get_client_ids(), {
                    'command': 'switch_strategy',
                    'strategy': 'NightBlinking'
                })
                self.wait(2.0)

            # PHASE 2: Synchronized lighting up
            self.main_thread.send_command(self.main_thread.get_client_ids(), {
                'command': 'switch_strategy',
                'strategy': None
            })

            self.light_up()
            self.light_down()

            self.wait(5)

            #self.wave()
            self.light_down()

            # self.main_thread.send_command(self.main_thread.get_client_ids(), {
            #     'command': 'switch_strategy',
            #     'strategy': None
            # })
            #self.wait(60.0)

            # terminate
            self.signal_exit()

        logging.debug('NightOwls finished')
