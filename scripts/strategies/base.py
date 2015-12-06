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
        minSleepTime = min(0.01, seconds)
        while seconds > 0.0 and not self.__signalExit__:
            time.sleep(minSleepTime)
            seconds -= minSleepTime # might be improved with accurate measurement using time.time()

    def run(self):
        logging.debug('- BaseStrategy.run __signalExit__=%s' % self.__signalExit__)
        while not self.__signalExit__:
            logging.debug("-- BaseStrategy.run step")
            self.wait(1.0)
            pass

    def signal_exit(self):
        logging.debug('Thread exit signalled - terminating gracefully')
        self.__signalExit__ = True
