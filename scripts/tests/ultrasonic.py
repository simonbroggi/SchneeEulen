#!/usr/bin/env python

import time, sys, random, math
import threading
import pigpio


class UltrasonicDistance(threading.Thread):
    def __init__(self, gpio_trigger, gpio_echo, update_interval = 0.5):
        threading.Thread.__init__(self)
        self.signal = True
          
        self.gpio_trigger = gpio_trigger
        self.gpio_echo = gpio_echo
        self.update_interval = update_interval
            
        time.sleep(0.5)

        self.pulselen = 0
        self.pulsestart = 0

        self.val = -1
        self.pi = pigpio.pi()
        self.pi.set_mode(self.gpio_echo, pigpio.INPUT)
        self.pi.set_mode(self.gpio_trigger, pigpio.OUTPUT)
        self.pi.write(self.gpio_trigger, 0)
        self.cb = self.pi.callback(self.gpio_echo, pigpio.EITHER_EDGE, self.edge_cb)
        
    def run(self):
        while self.signal:
            self.measure()
            print self.val
            time.sleep(self.update_interval)
        print "Terminated"
        
    def edge_cb(self, gpio, level, tick):
       if level == 0:
           self.pulselen = tick - self.pulsestart
           self.val = 0.5*(self.pulselen*34000)*1E-06
       else:
           self.pulsestart = tick
       
    def measure(self):
        self.pi.gpio_trigger(self.gpio_trigger, 10, 1)

    def destroy(self):
        self.cb.cancel()
        self.pi.stop()

t = UltrasonicDistance(23, 22, 0.25)
t.daemon = True
t.start()

try: 
    time.sleep(1000)
except KeyboardInterrupt:
    print "-interrupt-"
    t.signal = False
    time.sleep(1)
    t.destroy()
    





