import time
from functools import partial

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s][%(levelname)s] %(message)s', datefmt='%H:%M:%S')
#datefmt='%m/%d/%Y %H:%M:%S'
logger = logging.getLogger("EventHandeler")

class EventHandeler:

    def __init__(self, MasterApp):
        self.MasterApp = MasterApp

    def handle_state_change(self, event_name, event_data=""):
        logger.debug(f"event_name {event_name} caught")
        {
            "camera"       : self.MasterApp.set_scene_camera,
            "screen"       : self.MasterApp.set_scene_screen,
            "auto_lock"    : self.toggle_automatic,
            "clicker_next" : partial(self.clicker, "next"),
            "clicker_prev" : partial(self.clicker, "prev"),
            "toggle_camera_scene_augmented" : self.toggle_augmented,
            "auto_change_to_camera" : self.toggle_auto_back,
            "muted"        : self.toggle_muted,
            "scene_event"  : partial(self.scene_event, event_data),
            "timer_length" : partial(self.timer_length, event_data),
        }.get(event_name)()


    def toggle_automatic(self):
        self.MasterApp.States.automatic_enabled = not self.MasterApp.States.automatic_enabled
    
    def clicker(self, direction):
        self.MasterApp.auto_contro.propre_send(direction)
        time.sleep(.2)
        if self.MasterApp.States.automatic_enabled:
            self.MasterApp.set_scene_screen()

    def toggle_augmented(self):
        if not (self.MasterApp.States.current_scene == "augmented"):
            self.MasterApp.set_scene_augmented()
        else:
            self.MasterApp.States.automatic_enabled = True
            self.MasterApp.set_scene_camera()

    def toggle_auto_back(self):
        self.MasterApp.States.auto_change_to_camera = not self.MasterApp.States.auto_change_to_camera
        self.MasterApp.check_auto()

    def toggle_muted(self):
        if self.MasterApp.States.stream_is_muted:
            self.MasterApp.auto_contro.obs_send("unmute")
            self.MasterApp.States.stream_is_muted = False
        else:
            self.MasterApp.auto_contro.obs_send("mute")
            self.MasterApp.States.stream_is_muted = True

    def scene_event(self, event_data):
        if event_data.startswith("Camera"):
            self.MasterApp.States.current_camera_sub_scene = event_data
            if self.MasterApp.States.current_scene == "camera":
                self.MasterApp.set_scene_camera(change_sub_scene = True)
        elif event_data.startswith("Screen"):
            self.MasterApp.States.current_screen_sub_scene = event_data
            if self.MasterApp.States.current_scene == "screen":
                self.MasterApp.set_scene_screen(change_sub_scene = True)


    timer_values = {
        "5"   : 5,
        "7.5" : 7.5,
        "15"  : 15,
        "30"  : 30,
    }

    def timer_length(self, event_data):
        if not (event_data in self.timer_values):
            try:
                event_data = int(event_data)
            except ValueError:
                assert False == True, "Invalid timer event data provided"
            
        self.MasterApp.Timer.timer_length = self.timer_values[event_data]
        logger.debug(f"Changed timer length to {event_data}")
        