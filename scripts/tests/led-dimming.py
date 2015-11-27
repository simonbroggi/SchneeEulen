#!/usr/bin/env python

import time, sys, random, math
import pigpio

pi = pigpio.pi() # connect to local Pi

start_time = time.time()

##while (time.time()-start_time) < 20:
##   R = random.randrange(0, 255, 1)
##   pi.set_PWM_dutycycle(27, R)
##   time.sleep(0.02)

steps = 40000
pi.set_PWM_range(27, steps)
print pi.get_PWM_range(27)
pi.set_PWM_frequency(27, 10000000)

def dutycycle(val):
   return (1.0 - math.log(steps-val) / math.log(steps))

def godown():
   for t in range(steps-1, 1, -1):
      #print dutycycle(t)*steps
      pi.set_PWM_dutycycle(27,dutycycle(t)*steps)
      #time.sleep(0.0001)

def goup():
   for t in range(1, steps-1, 1):
      pi.set_PWM_dutycycle(27,dutycycle(t)*steps)
      time.sleep(0.0001)

godown()
goup()

pi.set_PWM_dutycycle(27, 255)
time.sleep(5)
pi.set_PWM_dutycycle(27, 0)
pi.stop()
