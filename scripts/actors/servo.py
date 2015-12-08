#!/usr/bin/python

# coding=utf-8
import time, sys, math
import threading
import pigpio
import logging
import Queue

class Servo(threading.Thread):
    signal = True
    stop_op = False
    min_angle = 0
    max_angle = 180
    pw_min = 800
    pw_max = 1500
    freq = 50
    gpio = None

    def __init__(self, gpio, min_angle=0.0, max_angle=180.0, pw_min=800, pw_max=2500, freq=50):
        logging.debug('Initializing pwm servo controller gpio=%s min_angle=%s max_angle=%s limit_min=%s limit_max=%s' % (gpio, min_angle, max_angle, pw_min, pw_max))
        threading.Thread.__init__(self)
        self.daemon = True

        # socket connection to pigpiod
        self.pi = pigpio.pi()
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.pw_min = pw_min
        self.pw_max = pw_max
        self.freq = freq
        self.gpio = gpio
        self.queue = Queue.Queue()
        self.current_val = 0.0

    def pwm_init(self):
        logging.debug("- gpio=%s set pwm freq=%s" % (self.gpio, self.freq))
        self.pi.set_PWM_frequency(self.gpio, self.freq)

    def stop(self):
        logging.debug('Stopping op')
        self.stop_op = True

    def clear(self):
        logging.debug('Clear queue')
        del self.queue[:]

    """ Adds a movement to the current queue. If clear flag is set will empty the queue beforehand. """
    def add(self, start_angle, end_angle, duration, step_size=1, clear=False):
        logging.debug('Servo add op start_val=%.2f end_val=%.2f duration=%.2f step_size=%s' % (start_angle, end_angle, duration, step_size))

        if clear:
            self.clear()

        self.queue.put({'start_angle': start_angle,
                           'end_angle': end_angle,
                           'duration': duration,
                           'step_size': step_size})
        logging.debug('queue=%s' % self.queue)

    def destroy(self):
        self.pi.set_PWM_dutycycle(self.gpio, 0)
        self.pi.stop()

    def run_op(self, op):
        logging.debug('servo run op=%s' % op)

        pulse_range = self.pw_max - self.pw_min
        angle_range = self.max_angle - self.min_angle

        start_pw = self.pw_min + int(round(((op['start_angle'] - self.min_angle)/angle_range) * pulse_range))
        end_pw = self.pw_min + int(round(((op['end_angle'] - self.min_angle)/angle_range) * pulse_range))

        step_count = abs((end_pw - start_pw + 1)/op['step_size'])

        step_delay = op['duration'] / step_count

        step_size = op['step_size']
        if start_pw > end_pw:
            step_size = - abs(op['step_size'])

        logging.debug("servo worker on gpio=%s start_pw=%s end_pw=%s step_size=%s duration=%s" % (self.gpio, start_pw, end_pw, step_size, op['duration']))

        pw = start_pw
        while self.signal and not self.stop_op and step_count > 0:
            self.pi.set_servo_pulsewidth(self.gpio, pw)
            pw += step_size
            time.sleep(step_delay)
            step_count -= 1

        self.pi.set_servo_pulsewidth(self.gpio, end_pw)

    def run(self):
        self.pwm_init()
        logging.debug('Servo loop gpio=%s' % self.gpio)
        while self.signal:
            while self.signal and self.queue.qsize() > 0 and not self.stop_op:
                logging.debug('Fetch op from queue=%s' % self.queue)
                op = self.queue.get()
                logging.debug('- op=%s' % op)
                self.run_op(op)

            while self.stop_op and self.signal:
                time.sleep(0.01)

        logging.debug('Servo on gpio=%s graceful shutdown' % self.gpio)
        self.pi.set_servo_pulsewidth(self.gpio, 0)

    """ Signal shutdown wish """
    def signal_exit(self):
        self.signal = False

if __name__ == "__main__":
    log = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] (%(threadName)-10s) %(message)s')

    logging.debug('servo test (start)')
    servo = Servo(4)
    servo.start()
    servo.add(0.0, 180.0, 1.0, 2)
    servo.add(180.0, 0.0, 1.0, -2)
    servo.add(0.0, 180.0, 2.0, 1)
    servo.add(180.0, 0.0, 2.0, -1)
    servo.add(0.0, 180.0, 4.0, 1)
    servo.add(180.0, 0.0, 4.0, -1)
    servo.add(0.0, 180.0, 8.0, 1)
    servo.add(180.0, 0.0, 8.0, -1)

    try:
        time.sleep(1000)
    except KeyboardInterrupt:
        print '- interrupt -'
        servo.signal_exit()
        time.sleep(1)
        servo.destroy()

    logging.debug('servo test (end)')


