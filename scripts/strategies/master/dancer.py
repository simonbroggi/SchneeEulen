
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

    def lightup(self):
        # fade down everything
        logging.debug('fade down everything')
        owls = self.main_thread.get_client_ids()
        for part in self.body_parts:
            self.main_thread.send_command(owls, {
                'command': 'dim',
                'id': part,
                'end_val': 0.0,
                'duration': 2.0,
                'step': 1,
                'clear': True
            })
        self.wait(4.0)

        if self.__signalExit__:
            return

        # fade down to middle
        logging.debug('fade down to middle')
        self.dimAllTo(0.33, 0.05, 2.0)
        self.wait(5.0)

        if self.__signalExit__:
            return

        # fade up middle
        logging.debug('fade vibration (30s)')
        start_time = time.time()
        duration = 180
        while not self.__signalExit__ and (time.time() - start_time < duration):
            self.wait(2)
            self.dimAllTo(1.0, 1.0, 0.3)
            self.dimAllTo(0.33, 0.05, 0.3)

        if self.__signalExit__:
            return

    def turn_all_heads_to(self, head_angle, duration):
        owls = self.main_thread.get_client_ids()
        for owl in owls:
            self.main_thread.send_command([owl], {
                'command': 'move',
                'id': 'head',
                'end_angle': head_angle,
                'duration': duration,
                'clear': False
            })

    def twinkle(self):
        owl = ['KLAUS']
        logging.debug('KLAUS: turn head to dancer')
        self.main_thread.send_command(owl, {
                'command': 'move',
                'id': 'head',
                'end_angle': 0.0,
                'duration': 0.25,
                'clear': True
            })
        self.wait(5.0)
        if self.__signalExit__:
            return

        start_time = time.time()
        duration = 10
        while not self.__signalExit__ and (time.time() - start_time < duration):
            self.main_thread.send_command(owl, {
                'command': 'dim',
                'id': 'eye_right',
                'end_val': 0.0,
                'duration': 0.5,
                'step': 2,
                'clear': True
            })
            self.wait(1.0)
            self.main_thread.send_command(owl, {
                'command': 'dim',
                'id': 'eye_right',
                'end_val': 1.0,
                'duration': 0.5,
                'step': 2,
                'clear': False
            })
            self.wait(1.0)


    def run(self):
        logging.debug('- using Dancer.run')

        self.wait(5.0)
        self.main_thread.send_command(self.main_thread.get_client_ids(), {
            'command': 'switch_strategy',
            'strategy': None
        })
        self.wait(10.0)

        self.turn_all_heads_to(30.0, 0.5)
        self.lightup()
        self.turn_all_heads_to(30.0, 0.5)
        if self.__signalExit__:
            return

        logging.debug('------dancer wait------')
        self.wait(10.0)

        logging.debug('================> send dancers twinkle')
        self.twinkle()
        if self.__signalExit__:
            return

        self.turn_all_heads_to(0, 0.5)
        self.wait(10.0)
        logging.debug('KLAUS: turn head to dancer')
        self.main_thread.send_command(['KLAUS'], {
                'command': 'move',
                'id': 'head',
                'end_angle': 90.0,
                'duration': 0.05,
                'clear': True
            })

        logging.debug('set autostrategy for all owls')

        self.wait(20.0)
        start_time = time.time()
        duration = 240.0
        while not self.__signalExit__ and time.time() - start_time < duration:

            self.main_thread.send_command(self.main_thread.get_client_ids(), {
                'command': 'switch_strategy',
                'strategy': 'SimpleAuto'
            })

            self.wait(2.0)

            # self.main_thread.send_command({
            #     'command': 'sync'
            # })
            # self.wait(2.0)

        logging.debug('Dancer finished')
