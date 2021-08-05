import time
from functools import partial
from Classes.StreamEvents import StreamEvents as SE
from Classes.SubScenes import SubScenes as SS

import logging

logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s][%(levelname)s] %(message)s', datefmt='%H:%M:%S')
# datefmt='%m/%d/%Y %H:%M:%S'
logger = logging.getLogger("EventHandler")


class EventHandler:

    def __init__(self, MasterApp):
        self.MasterApp = MasterApp
        self.states = MasterApp.States

    def handle_state_change(self, event_name, event_data=""):
        logger.debug(f"event_name {event_name} caught")

        # if event is part of SubScenes enum
        if SS.is_member(event_name):
            self.scene_event(event_name)
        else:
            {
                SE.CAMERA_SCENE: self.MasterApp.set_scene_camera,
                SE.SCREEN_SCENE: self.MasterApp.set_scene_screen,
                SE.AUGMENTED_ON: partial(self.augmented, True),
                SE.AUGMENTED_OFF: partial(self.augmented, False),
                SE.CHANGE_WITH_CLICKER_ON: partial(self.change_with_clicker, True),
                SE.CHANGE_WITH_CLICKER_OFF: partial(self.change_with_clicker, False),
                SE.PREV_SLIDE: partial(self.clicker, SE.PREV_SLIDE),
                SE.NEXT_SLIDE: partial(self.clicker, SE.NEXT_SLIDE),
                SE.AUTO_CHANGE_TO_CAMERA: partial(self.auto_change_to_camera, event_data),
                SE.TIMER_RUNNING: partial(self.set_timer_stopped, event_data),
                SE.TIMER_CHANGE_LENGTH: partial(self.timer_length, event_data),
                SE.TOGGLE_STREAM_VOLUME: partial(self.toggle_stream_is_muted, event_data),
                SE.TOGGLE_COMPUTER_VOLUME: partial(self.toggle_muted, event_data),
                SE.MEDIA_PAUSE_PLAY: self.media_pause_play,
                SE.UPDATE_REQUEST: partial(self.update, event_data)
            }.get(event_name)()

    def change_with_clicker(self, value: bool):
        self.states.change_with_clicker = value

    def augmented(self, yes):
        if yes:
            if not (self.states.current_scene == SE.AUGMENTED_SCENE):
                self.MasterApp.set_scene_augmented()
                self.states.augmented = True
        else:
            self.states.change_with_clicker = True
            self.MasterApp.set_scene_camera()
            self.states.augmented = False
        self.MasterApp.check_auto()

    def auto_change_to_camera(self, data):
        self.states.auto_change_to_camera = data
        self.MasterApp.check_auto()

    def clicker(self, direction):
        if not self.MasterApp.in_debug_mode:
            self.MasterApp.auto_contro.propre_send(direction)

        # TODO Check if this can be optimized because this is part of the clicker lag
        if not self.states.current_scene == SE.SCREEN_SCENE:
            if self.states.change_with_clicker:
                # TODO find tune this timing, might get away with no sleep time
                time.sleep(.2)
                self.MasterApp.set_scene_screen()
        else:
            self.MasterApp.check_auto()

    def toggle_muted(self, turn_volume_down):
        if not turn_volume_down:
            # turn the volume UP!
            if not self.MasterApp.in_debug_mode:
                self.MasterApp.auto_contro.toggle_sound(SE.MEDIA_VOLUME_UP)
            else:
                logger.debug("Pretend I am turning up the computer volume!")
        else:
            if not self.MasterApp.in_debug_mode:
                self.MasterApp.auto_contro.toggle_sound(SE.MEDIA_VOLUME_DOWN)
            else:
                logger.debug("Pretend I am turn the computer volume down!")
        # set like this because turn_volume_down is the opposite of sound on
        self.states.sound_on = not turn_volume_down

    def toggle_stream_is_muted(self, mute_stream):
        if not mute_stream:
            if not self.MasterApp.in_debug_mode:
                self.MasterApp.auto_contro.obs_send(SE.OBS_UNMUTE)
            else:
                logger.debug("Pretend I am turning the stream sound on!")
            self.states.stream_is_muted = False
        else:
            if not self.MasterApp.in_debug_mode:
                self.MasterApp.auto_contro.obs_send(SE.OBS_MUTE)
            else:
                logger.debug("Pretend I am muting the stream sound")
            self.states.stream_is_muted = True

    def media_pause_play(self):
        if not self.MasterApp.in_debug_mode:
            self.MasterApp.auto_contro.toggle_media_pause_play_global()

    def scene_event(self, event_data):
        if SS.Camera.is_member(event_data):
            self.states.current_camera_sub_scene = event_data
            if self.states.current_scene == SE.CAMERA_SCENE:
                self.MasterApp.set_scene_camera(change_sub_scene=True)

        elif SS.Screen.is_member(event_data):
            self.states.current_screen_sub_scene = event_data
            if self.states.current_scene == SE.SCREEN_SCENE:
                self.MasterApp.set_scene_screen(change_sub_scene=True)

    def update(self, specifier):
        if specifier == "all":
            self.MasterApp.update_all()

    def set_timer_stopped(self, value: bool):
        self.states.timer_not_running = value

    def timer_length(self, event_data):
        try:
            assert event_data > 1

            # TODO address this
            self.MasterApp.Timer._timer_length = event_data
            self.states.timer_length = event_data
            logger.debug(f"Changed timer length to {event_data}")
        except AssertionError:
            logger.debug(f"Unable to understand new timer length")
