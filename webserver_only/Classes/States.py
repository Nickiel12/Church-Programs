from dataclasses import dataclass, field
from types import FunctionType


@dataclass
class States:

    stream_running: bool
    stream_setup: bool

    stream_title: str
    callback: FunctionType = None

    def __setattr__(self, name, value):
        if self.callback:
            self.callback(name)
        return super().__setattr__(name, value)