from dataclasses import dataclass
import threading
from types import FunctionType


@dataclass
class States:

    stream_running: bool
    stream_is_setup: bool
    stream_title: str
    stream_is_muted: bool

    automatic_enabled: bool
    auto_change_to_camera: bool
    current_scene: str
    current_camera_sub_scene: str
    current_screen_sub_scene: str

    timer_text: str
    timer_paused: bool
    timer_kill: threading.Event

    sound_on: bool
    timer_length: int
    
    callback: FunctionType = None

    def __setattr__(self, name, value):
        returnable = super().__setattr__(name, value)
        if self.callback:
            self.callback(name, value)
        return returnable