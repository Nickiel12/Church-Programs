import enum
import atexit
import time
import logging
from threading import Event

from utils import threaded

logger = logging.getLogger("Main." + __name__)


class Timer:

    class TimerEvents(enum.Flag):
        TIMER_START = enum.auto()
        TIMER_PAUSED = enum.auto()
        TIMER_RUN_OUT = enum.auto()
        TIMER_KILLED = enum.auto()
        TIMER_TEXT_UPDATE = enum.auto()

    _timer_left = 0.0
    _timer_running = False
    _timer_start_time = None
    _timer_length = 0
    _timer_interval = 0.1

    def __init__(self, default_length=15.0):
        self._timer_length = default_length

        self._timer_kill = Event()
        atexit.register(self.kill_timer)

        self.timer_callbacks = {
            self.TimerEvents.TIMER_START: [],
            self.TimerEvents.TIMER_PAUSED: [],
            self.TimerEvents.TIMER_RUN_OUT: [],
            self.TimerEvents.TIMER_KILLED: [],
            self.TimerEvents.TIMER_TEXT_UPDATE: [],
        }
        self._timer()
        logger.info("Timer Initialized")

    def _event(self, timer_event: TimerEvents):
        if timer_event is self.TimerEvents.TIMER_TEXT_UPDATE:
            for callback in self.timer_callbacks[timer_event]:
                callback(str(self._timer_left))
        else:
            for callback in self.timer_callbacks[timer_event]:
                callback()

    def kill_timer(self):
        self._timer_kill.set()

    def remove_timer_callback(self, callback, timer_event: TimerEvents):
        self.timer_callbacks[timer_event].remove(callback)

    def add_timer_callback(self, timer_event: TimerEvents, callback):
        """
        Adds a callback to be called when TimerEvents event occurs
        """
        self.timer_callbacks[timer_event].append(callback)

    def reset_timer(self):
        self._timer_start_time = time.time()
        self.start_timer()

    def start_timer(self, *args):
        self._timer_running = True
        self._timer_start_time = time.time()
        self._event(self.TimerEvents.TIMER_START)
        logger.info("Timer starting")

    def stop_timer(self, *args):
        self._timer_running = False
        self._timer_left = 0.0
        self._event(self.TimerEvents.TIMER_PAUSED)
        self._event(self.TimerEvents.TIMER_TEXT_UPDATE)
        logger.info("Timer stopped")

    @threaded
    def _timer(self):
        time_left = None
        while not self._timer_kill.is_set():
            try:
                if self._timer_running:
                    end_time = self._timer_start_time + self._timer_length
                    time_left = end_time - time.time()

                    self._timer_left = round(end_time - time.time(), 1)
                    self._event(self.TimerEvents.TIMER_TEXT_UPDATE)

                    if not (time_left >= 0):
                        self._event(self.TimerEvents.TIMER_RUN_OUT)
                    time.sleep(self._timer_interval)
                else:
                    time.sleep(.3)
            except KeyboardInterrupt:
                return
        logger.info("timer killed")

