import time
from functools import partial
from Classes.StreamEvents import StreamEvents as SE


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
            SE.CAMERA_SCENE  : self.MasterApp.set_scene_camera,
            SE.SCREEN_SCENE  : self.MasterApp.set_scene_screen,
            SE.SPECIAL_SCENE : partial(self.scene_event, event_data),
            SE.AUGMENTED_ON  : self.augmented_on,
            SE.AUGMENTED_OFF : self.augmented_off,
            SE.PREV_SLIDE    : partial(self.clicker, "prev"),
            SE.NEXT_SLIDE    : partial(self.clicker, "next"),
            SE.AUTO_CHANGE_SCENE_ON   : self.automatic_on,
            SE.AUTO_CHANGE_SCENE_OFF  : self.automatic_off,
            SE.TOGGLE_COMPUTER_VOLUME : self.toggle_muted,
            SE.TIMER_PAUSE         : partial(self.set_timer_stopped, event_data),
            SE.TIMER_CHANGE_LENGTH : partial(self.timer_length, event_data),
            #SE.TOGGLE_STREAM_VOLUME   : ,
        }.get(event_name)()


    def automatic_off(self):
        self.MasterApp.States.automatic_enabled = False
    def automatic_on(self):
        self.MasterApp.States.automatic_enabled = True
    
    def augmented_on(self):
        self.MasterApp.States.augmented = True
        if not (self.MasterApp.States.current_scene == "augmented"):
            self.MasterApp.set_scene_augmented()
    def augmented_off(self):
        self.MasterApp.States.augmented = False
        self.MasterApp.States.automatic_enabled = True
        self.MasterApp.set_scene_camera()

    def clicker(self, direction):
        self.MasterApp.auto_contro.propre_send(direction)
        time.sleep(.2)
        if self.MasterApp.States.automatic_enabled:
            self.MasterApp.set_scene_screen()

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

    def set_timer_stopped(self, value):
        self.MasterApp.States.timer_paused = value

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
        