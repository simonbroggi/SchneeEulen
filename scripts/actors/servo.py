#!/usr/bin/python

# coding=utf-8
import time, sys, math
import threading
import logging
try:
    import pigpio
except ImportError:
    logging.info("- no pigpio lib available - fallback to dummy mode")


import Queue

class Servo(threading.Thread):
    signal = True
    stop_op = False
    min_angle = 0
    max_angle = 180
    pw_min = 500
    pw_max = 2500
    freq = 50
    direction = 'normal'
    gpio = None
    current_val = pw_min
    exitEvent = None

    def __init__(self, gpio, min_angle=0.0, max_angle=180.0, pw_min=800, pw_max=2500, freq=50, direction='normal'):
        logging.debug('Initializing pwm servo controller gpio=%s min_angle=%s max_angle=%s limit_min=%s limit_max=%s direction=%s' % (gpio, min_angle, max_angle, pw_min, pw_max, direction))
        threading.Thread.__init__(self, name="Servo-%s" % gpio)
        self.daemon = True
        self.exitEvent = threading.Event()

        # socket connection to pigpiod
        self.pi = pigpio.pi()
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.pw_min = pw_min
        self.pw_max = pw_max
        self.freq = freq
        self.gpio = gpio
        self.queue = Queue.Queue()
        self.current_val = pw_min
        self.direction = direction

    def pwm_init(self):
        logging.debug("- gpio=%s set pwm freq=%s" % (self.gpio, self.freq))
        self.pi.set_PWM_frequency(self.gpio, self.freq)

    def stop(self):
        logging.debug('Stopping op')
        self.stop_op = True

    def clear(self):
        logging.debug('Clear queue')
        with self.queue.mutex:
            self.queue.queue.clear()

    """ Adds a movement to the current queue. If clear flag is set will empty the queue beforehand. """
    def add(self, start_angle, end_angle, duration, step_size=1, clear=False):
        logging.debug('Servo add op start_angle=%.2f end_val=%.2f duration=%.2f step_size=%s' % (start_angle, end_angle, duration, step_size))

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

    def pwm_to_angle(self, pwm):
        pulse_range = self.pw_max - self.pw_min
        angle_range = self.max_angle - self.min_angle
        #logging.debug("%s %s %s %f" % (pulse_range, angle_range, self.pw_min, ((pwm - self.pw_min)/float(pulse_range))))
        return ((pwm - self.pw_min) / float(pulse_range))*angle_range + self.min_angle

    def angle_to_pwm(self, angle):
        pulse_range = self.pw_max - self.pw_min
        angle_range = self.max_angle - self.min_angle
        return self.pw_min + int(round(((angle - self.min_angle)/angle_range) * pulse_range))

    def run_op(self, op):
        try:
            #logging.debug('servo run op=%s' % op)

            start_angle = op['start_angle']
            end_angle = op['end_angle']

            if self.direction == 'inverse':
                start_angle = 180.0 - start_angle
                end_angle = 180.0 - end_angle

            start_pw = self.pw_min
            end_pw = self.pw_max
            if math.isnan(start_angle):
                start_pw = self.current_val
            else:
                start_pw = self.angle_to_pwm(start_angle)

            if math.isnan(end_angle):
                end_pw = self.current_val
            else:
                end_pw = self.angle_to_pwm(end_angle)

            start_pw = min(max(start_pw, self.pw_min), self.pw_max)
            end_pw = min(max(end_pw, self.pw_min), self.pw_max)

            step_size = op['step_size']
            if start_pw > end_pw:
                step_size = - abs(op['step_size'])

            step_count = abs((end_pw - start_pw + 1)/op['step_size'])
            if step_count == 0:
                logging.warning('warning: no servo steps needed')
                step_delay = 0
            else:
                step_delay = op['duration'] / step_count

            pw = start_pw
            while self.signal and not self.stop_op and step_count > 0:
                #logging.debug('---> set servo pulsewidth %d' % pw)
                self.pi.set_servo_pulsewidth(self.gpio, pw)
                self.current_val = pw
                pw += step_size
                if self.signal:
                    self.exitEvent.wait(step_delay)
                step_count -= 1

            self.current_val = end_pw
            self.pi.set_servo_pulsewidth(self.gpio, end_pw)
        except Exception as e:
            logging.error(e)

    def run(self):
        self.pwm_init()
        logging.debug('Servo loop gpio=%s' % self.gpio)
        while self.signal:
            while self.signal and self.queue.qsize() > 0 and not self.stop_op:
                #logging.debug('Fetch op from queue=%s' % self.queue)
                op = self.queue.get()
                #logging.debug('- op=%s' % op)
                self.run_op(op)

            while self.stop_op and self.signal:
                time.sleep(0.01)

        logging.debug('Servo on gpio=%s graceful shutdown' % self.gpio)
        self.pi.set_servo_pulsewidth(self.gpio, 0)

    """ Signal shutdown wish """
    def signal_exit(self):
        self.signal = False
        self.exitEvent.set()

if __name__ == "__main__":
    log = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] (%(threadName)-10s) %(message)s')

    logging.debug('servo test (start)')
    servo = Servo(4)
    logging.debug('pwm/angle conversion tests')
    logging.debug(servo.angle_to_pwm(90))
    logging.debug(servo.pwm_to_angle(servo.angle_to_pwm(90)))
    exit()

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


