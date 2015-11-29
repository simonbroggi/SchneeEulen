#!/usr/bin/python

# coding=utf-8
import time, sys, random, math
import threading
import pigpio
import logging


class Dimmer(threading.Thread):
    def __init__(self, gpio_led, steps=1000, freq=100):
        logging.debug('Initializing dimmer gpio=%s steps=%s freq=%s' % (gpio_led, steps, freq))
        threading.Thread.__init__(self)
        self.signal = True

        self.pi = pigpio.pi()
        self.steps = 1000
        self.freq = freq
        self.gpio = gpio_led
        self.pwm_init()
        self.queue = []
        self.current_val = 0.0
        self.stop_op = False

    def pwm_init(self):
        self.pi.set_PWM_range(self.gpio, self.steps)
        self.pi.set_PWM_frequency(self.gpio, self.freq)

    def dutycycle(self, val):
        # val = max(min(val, steps), 0)
        # return steps*(1.0 - math.log(steps-val, steps))
        return val

    def stop(self):
        logging.debug('Stopping op')
        self.stop_op = True

    def clear(self):
        logging.debug('Clear queue')
        del self.queue[:]

    def add(self, start_val, end_val, duration, step_size=1, clear=False):
        logging.debug('Add op start_val=%.2f end_val=%.2f duration=%.2f step_size=%s' % (start_val, end_val, duration, step_size))

        if clear:
            self.clear()

        self.queue.append({'start_val': start_val,
                           'end_val': end_val,
                           'duration': duration,
                           'step_size': step_size})

    def destroy(self):
        self.pi.set_PWM_dutycycle(self.gpio, 0)
        self.pi.stop()

    def run_op(self, op):
        logging.debug('run op=%s' % op)

        step_size = op['step_size']
        if op['start_val'] > op['end_val']:
            step_size = -abs(op['step_size'])

        start_step = int(round(op['start_val'] * (self.steps - 1.0)))
        end_step = int(round(op['end_val'] * (self.steps - 1.0)))
        step_count = (abs(end_step - start_step) + 1) / abs(step_size)

        step_delay = op['duration'] / step_count
        logging.debug('start=%f end_step=%f step_delay=%f step_count=%f' % (start_step, end_step, step_delay, step_count))

        t = start_step
        while self.signal and not self.stop_op and step_count > 0:
            logging.debug('- set dutycycle for t=%f => %f' % (t, self.dutycycle(t)))
            self.pi.set_PWM_dutycycle(self.gpio, self.dutycycle(t))
            time.sleep(step_delay)
            t += step_size
            step_count -= 1

        # case when step_size does not fit end
        self.pi.set_PWM_dutycycle(self.gpio, self.dutycycle(end_step))

    def run(self):
        logging.debug('Enter dimmer loop')
        while self.signal:
            while self.signal and len(self.queue) > 0 and not self.stop_op:
                logging.debug('Fetch op from queue')
                op = self.queue.pop()
                logging.debug('- op=%s' % op)
                self.run_op(op)

            while self.stop_op and self.signal:
                time.sleep(0.01)


if __name__ == "__main__":
    log = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] (%(threadName)-10s) %(message)s')

    logging.debug('dimmer test (start)')
    dimmer = Dimmer(27)
    dimmer.daemon = True
    dimmer.start()

    dimmer.add(1.0, 0.0, 1.0, -1)
    dimmer.add(0.0, 1.0, 1.0, 1)
    dimmer.add(0.0, 1.0, 5.0, 4)

    try:
        time.sleep(1000)
    except KeyboardInterrupt:
        print '- interrupt -'
        dimmer.signal = False
        time.sleep(1)
        dimmer.destroy()


    logging.debug('dimmer test (end)')
