import time, sys, random, math
import threading
import logging


class BaseStrategy(threading.Thread):
    subthreads = []
    main_thread = None

    """
    Base class to execute strategies (similar to Unity's GameObject)
    """
    def __init__(self, main_thread):
        threading.Thread.__init__(self)
        self.daemon = True
        self.__signalExit__ = False
        self.main_thread = main_thread
        #""":type : SnowlyClient"""

    def wait(self, seconds):
        logging.debug("wait %s" % seconds)
        startTime = time.time()
        minSleepTime = min(0.001, seconds)
        while time.time() - startTime < seconds and not self.__signalExit__:
            time.sleep(minSleepTime)

    def run(self):
        logging.debug('- BaseStrategy.run __signalExit__=%s' % self.__signalExit__)
        while not self.__signalExit__:
            logging.debug("-- BaseStrategy.run step")
            self.wait(1.0)

    def signal_exit(self):
        logging.debug('Thread exit signalled - terminating gracefully')
        self.__signalExit__ = True
