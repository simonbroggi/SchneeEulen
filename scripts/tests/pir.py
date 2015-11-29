#!/usr/bin/env python

import time, sys, random, math
import threading
import pigpio


class PIR:
    def __init__(self, gpio_trigger):
        self.gpio_trigger = gpio_trigger
        self.val = 0
        self.pi = pigpio.pi()
        self.pi.set_mode(self.gpio_trigger, pigpio.INPUT)
        self.cb = self.pi.callback(self.gpio_trigger, pigpio.EITHER_EDGE, self.edge_cb)
        
    def edge_cb(self, gpio, level, tick):
        print("edge_cb level=%s" % level)
        self.val = level

    def destroy(self):
        self.cb.cancel()
        self.pi.stop()

pir = PIR(24)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print "-interrupt-"
    pir.destroy()
    





