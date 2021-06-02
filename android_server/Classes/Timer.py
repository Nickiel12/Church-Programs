import time
import logging

from Classes.StreamEvents import StreamEvents
from utils import threaded

logger = logging.getLogger(__name__)


class Timer:

    def __init__(self, MasterApp):
        self.MasterApp = MasterApp
        self.timer_length = MasterApp.settings.general.default_timer_length
        self.timer_start_time = time.time() - self.timer_length
        self.started_once = False
        self._timer()

    def _kill_timer(self, *args):
        self.MasterApp.States.timer_kill.set()

    def pause_timer(self, *args):
        self.MasterApp.States.timer_not_running = True
        self.MasterApp.States.timer_text = "0.0"

    def start_timer(self, *args):
        self.started_once = True
        self.MasterApp.States.timer_not_running = False

    def reset_timer(self):
        self.timer_start_time = time.time()
        self.start_timer()

    def timer_unavailable(self):
        self.MasterApp.States.timer_text = "Unvailable"

    def timer_available(self):
        self.MasterApp.States.timer_text = "0.0"
        self.pause_timer()

    @threaded
    def _timer(self):
        while not self.MasterApp.States.timer_kill.is_set():
            if self.started_once == True:
                try:
                    if self.MasterApp.States.timer_not_running == False:
                        end_time = self.timer_start_time + self.timer_length
                        self.timer_left = round(end_time - time.time(), 1)
                        self.MasterApp.States.timer_text = self.timer_left
                        if not (self.timer_left >= 0):
                            self.timer_run_out()
                    else:
                        time.sleep(.3)
                except KeyboardInterrupt:
                    return
            time.sleep(.1)
        logger.info("timer killed")

    def timer_run_out(self):
        self.MasterApp.States.timer_not_running = True
        self.MasterApp.handle_state_change(StreamEvents.CAMERA_SCENE)