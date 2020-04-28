from dataclasses import dataclass, field
import threading
from types import FunctionType


@dataclass
class States:

    stream_running: bool
    stream_setup: bool
    stream_title: str

    automatic_enabled: bool
    current_scene: str

    timer_text: str
    timer_paused: bool
    timer_kill: threading.Event
    
    callback: FunctionType = None

    def __setattr__(self, name, value):
        if self.callback:
            self.callback(name)
        return super().__setattr__(name, value)