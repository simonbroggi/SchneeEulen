#!/usr/bin/env python
import time, sys, random, math
import threading
import pigpio 
import time

pi = pigpio.pi() 
 
servos = 4 #GPIO number


#pulsewidth can only set between 500-2500
freq=50
pi.set_PWM_frequency(servos, freq)
print("Set PWM frequency to {}".format(freq, 1000))

MIN_ANGLE=0
MIN_PULSEWIDTH=500
MAX_ANGLE=180
MAX_PULSEWIDTH=2500

def servodrive(pin, start_angle, end_angle, duration, step_size = 1):
    pi = pigpio.pi()

    pulse_range = MAX_PULSEWIDTH - MIN_PULSEWIDTH
    angle_range = MAX_ANGLE - MIN_ANGLE

    start_pw = MIN_PULSEWIDTH + int(round(((start_angle - MIN_ANGLE)/angle_range) * pulse_range))
    end_pw = MIN_PULSEWIDTH + int(round(((end_angle - MIN_ANGLE)/angle_range) * pulse_range))
    
    step_count = abs((end_pw - start_pw + 1)/step_size)
    
    step_delay = duration / step_count
    
    if start_pw > end_pw:
        step_size = - abs(step_size)

    print "servo worker on pin %s start_pw=%s end_pw=%s step_size=%s duration=%s" % (pin, start_pw, end_pw, step_size, duration)
    
    for pw in range(start_pw, end_pw, step_size):
        pi.set_servo_pulsewidth(servos, pw)
        time.sleep(step_delay)

    pi.stop()



pi.set_servo_pulsewidth(servos, 0)

t = threading.Thread(target=servodrive, args=(servos, 0.0, MAX_ANGLE, 4.0, 2))
t.start()
t.join()
t = threading.Thread(target=servodrive, args=(servos, MAX_ANGLE, 0.0, 4.0, -2))
t.start()
t.join()

pi.set_servo_pulsewidth(servos, 0); 
pi.stop()


