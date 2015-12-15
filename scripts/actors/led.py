#!/usr/bin/python

# coding=utf-8
import time, sys, math
import threading
import pigpio
import logging
import Queue

class Dimmer(threading.Thread):
    MAX_QUEUE_SIZE = 50

    def __init__(self, gpio_led, steps=1000, freq=100, body_part='Dimmer-%s'):
        logging.debug('Initializing dimmer gpio=%s steps=%s freq=%s' % (gpio_led, steps, freq))
        threading.Thread.__init__(self, name=body_part % gpio_led)
        self.signal = True

        self.pi = pigpio.pi()
        self.steps = steps
        self.freq = freq
        self.gpio = gpio_led
        self.queue = Queue.Queue(self.MAX_QUEUE_SIZE)
        self.current_val = 0.0
        self.stop_op = False
        self.daemon = True

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
        with self.queue.mutex:
            self.queue.queue.clear()

    def add(self, start_val, end_val, duration, step_size=1, clear=False):
        logging.debug('Add op start_val=%.2f end_val=%.2f duration=%.2f step_size=%s' % (start_val, end_val, duration, step_size))

        if clear:
            self.clear()

        self.queue.put({'start_val': start_val,
                           'end_val': end_val,
                           'duration': duration,
                           'step_size': step_size})
        logging.debug('queue=%s' % self.queue)

    def destroy(self):
        self.pi.set_PWM_dutycycle(self.gpio, 0)
        self.pi.stop()

    def run_op(self, op):
        logging.debug('run op=%s' % op)

        if math.isnan(op['start_val']):
            start_step = self.current_val
            logging.debug('start_val is_nan, using %f' % start_step)
        else:
            start_step = int(round(op['start_val'] * (self.steps - 1.0)))

        if math.isnan(op['end_val']):
            end_step = self.current_val
            logging.debug('start_val is_nan, using %f' % end_step)
        else:
            end_step = int(round(op['end_val'] * (self.steps - 1.0)))

        step_size = op['step_size']
        if start_step > end_step:
            step_size = -abs(op['step_size'])

        if step_size == 0:
            logging.debug('warning: no dim steps needed')
            return

        step_count = (abs(end_step - start_step) + 1) / abs(step_size)
        if step_count == 0:
            logging.debug('warning: no dim steps needed')
            return

        step_delay = op['duration'] / step_count
        logging.debug('self=%s start=%f end_step=%f step_delay=%f step_count=%f' % (self, start_step, end_step, step_delay, step_count))

        t = start_step
        while self.signal and not self.stop_op and step_count > 0:
            #logging.debug('- set dutycycle for t=%f => %f, current_val=%f' % (t, self.dutycycle(t), self.current_val))
            self.current_val = t
            self.pi.set_PWM_dutycycle(self.gpio, self.dutycycle(self.current_val))
            time.sleep(step_delay)
            t += step_size
            step_count -= 1

        # case when step_size does not fit end
        self.current_val = self.dutycycle(end_step)
        self.pi.set_PWM_dutycycle(self.gpio, self.dutycycle(end_step))

    def run(self):
        logging.debug('Enter dimmer loop')
        self.pwm_init()

        while self.signal:
            while self.signal and self.queue.qsize() > 0 and not self.stop_op:
                logging.debug('Fetch op from queue=%s' % self.queue)
                op = self.queue.get()
                logging.debug('- op=%s' % op)
                self.run_op(op)

            #while self.stop_op and self.signal:
            #    time.sleep(0.001)

        logging.debug("terminating led dimmer on gpio=%s gracefully" % self.gpio)
        self.destroy()

    def signal_exit(self):
        self.signal = False

if __name__ == "__main__":
    log = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] (%(threadName)-10s) %(message)s')

    logging.debug('dimmer test (start)')
    dimmer = Dimmer(27, 500, 500)
    dimmer.start()
    dimmer.add(float('nan'), 1.0, 0.0, 1)
    dimmer.add(1.0, 0.0, 0.0, -1)

    time.sleep(2)
    #dimmer.add(0.0, 1.0, 0.0, 1)
    dimmer.add(float('nan'), 0.0, 0.0, -1)
    dimmer.add(float('nan'), 0.0, 1.0, 1)
    try:
        time.sleep(1000)
    except KeyboardInterrupt:
        print '- interrupt -'
        dimmer.signal_exit()
        time.sleep(1)
        dimmer.destroy()

    logging.debug('dimmer test (end)')
