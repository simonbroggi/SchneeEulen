#!/usr/bin/env python

import time
import pigpio

servos = 4 # broadcom GPIO number
pi = pigpio.pi()

pi.set_servo_pulsewidth(servos, 500)

#pulsewidth can only set between 500-2500
delay=8
freq=50

#pi.set_PWM_frequency(4, freq)
print("Set PWM frequency to {}".format(freq, 1000))

def slow_movement():
    for pw in range(800,1500,1):
        pi.set_servo_pulsewidth(servos, pw)
        time.sleep(0.1)

try:
    while True:

##      pi.set_servo_pulsewidth(servos, 800)
##      time.sleep(2)
##      pi.set_servo_pulsewidth(servos, 2100)
##      time.sleep(2)

        slow_movement()
        #pi.set_PWM_dutycycle(4, 255)
        #time.sleep(2)

#        pi.set_servo_pulsewidth(servos, 500) #0 degree
#        print("Servo {} {} micro pulses".format(servos, 1000))
#        time.sleep(delay)
#        pi.set_servo_pulsewidth(servos, 625) #90 degree
#        print("Servo {} {} micro pulses".format(servos, 1500))
#        time.sleep(delay)

#        pi.set_servo_pulsewidth(servos, 2500) #180 degree
#        print("Servo {} {} micro pulses".format(servos, 2000))
#        time.sleep(delay)
#        pi.set_servo_pulsewidth(servos, 1500)
#        print("Servo {} {} micro pulses".format(servos, 1500))
#        time.sleep(delay)

   # switch all servos off
except KeyboardInterrupt:
    pigpio.set_servo_pulsewidth(servos, 0);

pi.stop()
