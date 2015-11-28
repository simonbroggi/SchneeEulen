#!/usr/bin/env python

import time, sys, random, math
import threading
import pigpio

pi = pigpio.pi() # connect to local Pi

steps = 1000
pi.set_PWM_range(27, steps)
pi.set_PWM_frequency(27, 100)

def dutycycle(val):
   ## val = max(min(val, steps), 0)
   ## return steps*(1.0 - math.log(steps-val, steps))
   return val 


def dimmer(pin, start_val, end_val, duration, step_size = 1):
   pi = pigpio.pi()
   
   print "dimmer worker on pin %s start=%s end=%s, duration=%s" % (pin, start_val, end_val, duration)
   start_time = time.time()

   if start_val > end_val and step_size > 0:
      step_size = - step_size

   start_step = int(round(start_val*(steps - 1.0)))
   end_step = int(round(end_val*(steps - 1.0)))
   step_count = abs(end_step - start_step + 1)

   step_delay = duration / step_count
   print "start=",start_step,"end=",end_step,"delay=",step_delay
   
   for t in range(start_step, end_step, step_size):
      ## print t, dutycycle(t)
      pi.set_PWM_dutycycle(pin, dutycycle(t))
      time.sleep(step_delay)

   print time.time() - start_time
   pi.stop()
   return


t = threading.Thread(target=dimmer, args=(27, 0.0, 1.0, 0.5, 1))
t.start()
t.join()
t = threading.Thread(target=dimmer, args=(27, 1.0, 0.0, 0.5, -1))
t.start()
t.join()

pi.set_PWM_dutycycle(27, 0)
pi.stop()
