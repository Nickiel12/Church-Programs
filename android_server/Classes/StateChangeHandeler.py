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
            SE.CHANGE_WITH_CLICKER_ON   : self.change_with_clicker_on,
            SE.CHANGE_WITH_CLICKER_OFF  : self.change_with_clicker_off,
            SE.AUTO_CHANGE_TO_CAMERA  : partial(self.auto_change_to_camera, event_data),
            SE.TOGGLE_COMPUTER_VOLUME : partial(self.toggle_muted, event_data),
            SE.TOGGLE_STREAM_VOLUME   : partial(self.toggle_stream_is_muted, event_data),
            SE.TIMER_RUNNING         : partial(self.set_timer_stopped, event_data),
            SE.TIMER_CHANGE_LENGTH : partial(self.timer_length, event_data),
        }.get(event_name)()


    def change_with_clicker_on(self):
        self.MasterApp.States.change_with_clicker = True
    def change_with_clicker_off(self):
        self.MasterApp.States.change_with_clicker = False
    
    def augmented_on(self):
        self.MasterApp.States.augmented = True
        if not (self.MasterApp.States.current_scene == "augmented"):
            self.MasterApp.set_scene_augmented()
    def augmented_off(self):
        self.MasterApp.States.augmented = False
        self.MasterApp.States.change_with_clicker = True
        self.MasterApp.set_scene_camera()

    def auto_change_to_camera(self, data):
        self.MasterApp.States.auto_change_to_camera = data
        self.MasterApp.check_auto()

    def clicker(self, direction):
        self.MasterApp.auto_contro.propre_send(direction)
        time.sleep(.2)
        if self.MasterApp.States.change_with_clicker:
            self.MasterApp.set_scene_screen()

    def toggle_muted(self, turn_volume_down):
        if not turn_volume_down:
            # turn the volume UP!
            if (not self.MasterApp.in_debug_mode):
                self.MasterApp.auto_contro.toggle_sound(True)
            else:
                logger.debug("Pretend I am turning up the computer volume!")
        else:
            if (not self.MasterApp.in_debug_mode):
                self.MasterApp.auto_contro.toggle_sound(False)
            else:
                logger.debug("Pretend I am turn the computer volume down!")
        self.MasterApp.States.sound_on = not turn_volume_down

    def toggle_stream_is_muted(self, mute_stream):
        if not mute_stream:
            if (not self.MasterApp.in_debug_mode):
                self.MasterApp.auto_contro.obs_send("unmute")
            else:
                logger.debug("Pretend I am turning the stream sound on!")
            self.MasterApp.States.stream_is_muted = False
        else:
            if (not self.MasterApp.in_debug_mode):
                self.MasterApp.auto_contro.obs_send("mute")
            else:
                logger.debug("Pretend I am muting the stream sound")
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
        self.MasterApp.States.timer_not_running = value


    def timer_length(self, event_data):
        try:
            assert event_data > 1
                
            self.MasterApp.Timer.timer_length = event_data
            self.MasterApp.States.timer_length = event_data
            logger.debug(f"Changed timer length to {event_data}")
        except AssertionError:
            logger.debug(f"Unable to understand!")