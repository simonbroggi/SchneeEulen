
import logging
import threading
import pigpio
import random
from time import sleep
from strategies.base import StrategyThread

class SimpleBlink(StrategyThread):
    def __init__(self, main_thread):
        StrategyThread.__init__(self, main_thread, 'SimpleBlink')

    def run(self):
        head_angle = random.uniform(0.0, 180.0)
        servo = self.main_thread.get_servo('head')

        head_speed = random.uniform(4.0, 6.0)
        servo.add(servo.current_val, head_angle, head_speed, 1.0, True)
        self.wait(head_speed - 1.0)

        while not self.__signalExit__:
            last_head_angle = head_angle
            head_angle = max(min(random.uniform(head_angle - 25.0, head_angle + 25.0), 180.0), 0.0)
            head_speed = random.uniform(2.0, 4.0)
            servo.add(last_head_angle, head_angle, head_speed, 1.0, True)

            eye_left = self.main_thread.get_dimmer('eye_left')
            eye_right = self.main_thread.get_dimmer('eye_right')

            eye_brightness = random.uniform(0.1, 0.8)
            eye_left.add(0.0, eye_brightness, 3.5, 1, True)
            eye_right.add(0.0, eye_brightness, 3.5, 1, True)

            blinking_count = random.randint(1,4)
            while not self.__signalExit__ and blinking_count > 0:
                self.wait(random.uniform(0.5,3.5))
                eye_left.add(eye_brightness, 0.0, 0.2, 6)
                eye_right.add(eye_brightness, 0.0, 0.2, 6)
                eye_left.add(0.0, eye_brightness, 0.4, 6)
                eye_right.add(0.0, eye_brightness, 0.4, 6)

                self.wait(random.uniform(2.0,5.0))
                blinking_count -= 1

            eye_left.add(eye_brightness, 0.0, 1.5, 1)
            eye_right.add(eye_brightness, 0.0, 1.5, 1)

            self.wait(random.uniform(8.0, 25.0))

        logging.debug('simpleblink finished')


class NightBlinking(StrategyThread):
    def __init__(self, main_thread):
        StrategyThread.__init__(self, main_thread, 'NightBlinking')

    def run(self):
        logging.debug('- using NightBlinking.run')

        # background blinking
        blinking = SimpleBlink(self.main_thread)
        blinking.start()

        # head_angle = 0.0
        # last_angle = 0.0
        #
        # while not self.__signalExit__:
        #     # servo = self.main_thread.get_servo('head')
        #     #
        #     # head_angle = random.uniform(0.0, 180.0)
        #     # servo.add(last_angle, head_angle, random.uniform(2.0, 10.0), 1.0, True)
        #     # last_angle = head_angle
        #     #
        #     # eye_left = self.main_thread.get_dimmer('eye_left')
        #     # eye_left.add(0.0, 1.0, 2.0, 2, True)
        #     # eye_left.add(1.0, 0.0, 2.0, 2)
        #     #
        #     # eye_right = self.main_thread.get_dimmer('eye_right')
        #     # eye_right.add(0.0, 1.0, 2.0, 2, True)
        #     # eye_right.add(1.0, 0.0, 2.0, 2)
        #     #
        #     # #servo.add(180.0, 0, 3.0, 4.0)
        #     # #logging.debug("body_dimmer start")
        #     # #body_dimmer = self.main_thread.get_dimmer('eye_left')
        #     # #body_dimmer.add(0.0, 1.0, 1.0, 1, False)
        #     # #body_dimmer.add(1.0, 0.0, 1.0, -1)
        #     #
        #     # logging.debug("randomized self.wait(5)")
        #     self.wait(25)

        while not self.__signalExit__:
            body_dimmer = self.main_thread.get_dimmer('body')
            body_dimmer.add(float('nan'), 0.0, 2.0, True)

            self.wait(20)

        # wait for subthread to finish
        blinking.signal_exit()
        while blinking.is_alive():
            logging.debug('...waiting for simple blinking to finish gracefully...')
            sleep(0.01)

        logging.debug('NightBlinking finished')
