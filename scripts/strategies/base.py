#!/usr/bin/python

import time, sys, random, math
import threading
import logging


class StrategyThread(threading.Thread):
    subthreads = []
    last_update = -1
    main_thread = None
    """:type : SnowlyClient"""

    """
    Base class to execute strategies
    """
    def __init__(self, main_thread, threadName=None):
        threading.Thread.__init__(self, name=threadName)
        self.daemon = True
        self.__signalExit__ = False
        self.main_thread = main_thread

    def wait(self, seconds):
        #logging.debug("wait %s" % seconds)
        startTime = time.time()
        minSleepTime = min(0.001, seconds)
        while time.time() - startTime < seconds and not self.__signalExit__:
            time.sleep(minSleepTime)

    def run(self):
        self.last_update = time.time()
        while not self.__signalExit__:
            #logging.debug("-- BaseStrategy.run step")
            self.wait(1.0)

    def keep_alive(self):
        t = time.time()
        logging.debug('%s got keepalive at %s' % (self.getName(), t))
        self.last_update = t

    def signal_exit(self):
        logging.debug('Thread exit signalled - terminating gracefully')
        self.__signalExit__ = True


