import time
import States

if __name__ == "__main__":
    import Classes.States

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s][%(levelname)s] %(message)s', datefmt='%H:%M:%S')
#datefmt='%m/%d/%Y %H:%M:%S'
logger = logging.getLogger("EventHandeler")

class EventHandeler:

    def __init__(self, MasterApp):
        self.MasterApp = MasterApp

    def handle_state_change(self, event_name, event_type=""):
        sett = self.MasterApp.settings
        logger.debug(f"event_name {event_name} caught")
        if event_name == "camera":
            self.MasterApp.set_scene_camera()
        elif event_name == "screen":
            self.MasterApp.set_scene_screen()
        elif event_name == "auto_lock":
            state = self.MasterApp.States.automatic_enabled
            self.MasterApp.States.automatic_enabled = not state
        elif event_name == "clicker_next":
            self.MasterApp.auto_contro.propre_send("next")
            time.sleep(.2)
            if self.MasterApp.States.automatic_enabled:
                self.MasterApp.set_scene_screen()
        elif event_name == "clicker_prev":
            self.MasterApp.auto_contro.propre_send("prev")
            time.sleep(.2)
            if self.MasterApp.States.automatic_enabled:
                self.MasterApp.set_scene_screen()
        elif event_name == "toggle_camera_scene_augmented":
            if not (self.MasterApp.States.current_scene == "augmented"):
                self.MasterApp.set_scene_augmented()
            else:
                self.MasterApp.States.automatic_enabled = True
                self.MasterApp.set_scene_camera()
        elif event_name == "muted":
            if self.MasterApp.States.stream_is_muted:
                self.MasterApp.auto_contro.obs_send("unmute")
                self.MasterApp.States.stream_is_muted = False
            else:
                self.MasterApp.auto_contro.obs_send("mute")
                self.MasterApp.States.stream_is_muted = True
        elif event_type == "scene_event":
            if event_name.startswith("Camera"):
                self.MasterApp.States.current_camera_sub_scene = event_name
                if self.MasterApp.States.current_scene == "camera":
                    self.MasterApp.set_scene_camera(change_sub_scene = True)
            elif event_name.startswith("Screen"):
                self.MasterApp.States.current_screen_sub_scene = event_name
                if self.MasterApp.States.current_scene == "screen":
                    self.MasterApp.set_scene_screen(change_sub_scene = True)
        elif event_type == "timer_event":
            acceptable_values = {
                "5" : 5,
                "7.5" : 7.5,
                "15" : 15,
                "30" : 30,
            }

