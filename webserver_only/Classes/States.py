from dataclasses import dataclass


@dataclass
class States:

    stream_running: bool
    stream_setup: bool

    stream_title: str

    def set_callback(self, callback):
        self.callback = callback

    def __setattr__(self, name, value):
        self.callback(name)
        return super().__setattr__(name, value)