import time

import logging

logger = logging.getLogger(__name__)


class Timer:

    def __init__(self, MasterApp):
        self.MasterApp = MasterApp
        imer_start_time = time.time()
        timer_length = MasterApp.settings.kivy.scene_timer_time

    def _kill_timer(self, *args):
        print("timer stopped")
        self.MasterApp.States.timer_run.set()

    def zero_timer(self, *args):
        self.pause_timer()
        self.MasterApp.States.timer_time = 0.0

    def pause_timer(self, *args):
        self.MasterApp.States.timer_paused = True

    def start_timer(self, *args):
        self.MasterApp.States.timer_paused = False

    def reset_timer(self):
        self.timer_start_time = time.time()
        self.start_timer()

    def timer_unavailable(self):
        self.MasterApp.States.timer_text = "Unvailable"

    def timer_available(self):
        self.MasterApp.States.timer_text = None
        self.zero_timer()

    @threaded
    def _timer(self):
        while not self.MasterApp.States.timer_run.is_set():
            if self.MasterApp.States.timer_text is None:
                try:
                    if self.MasterApp.States.timer_paused is False:
                        end_time = self.timer_start_time + self.timer_length
                        self.timer_left = round(end_time - time.time(), 1)
                        if not (self.timer_left >= 0):
                            self.timer_run_out()
                    else:
                        time.sleep(.3)
                except KeyboardInterrupt:
                    return
            else:
                time.sleep(.3)
            time.sleep(.1)

    def timer_run_out(self):
        self.MasterApp.States.timer_paused = True
        self.MasterApp.on_hotkey("camera")