from dataclasses import dataclass

from Classes.Watch_Classes import WatchBool, WatchNumber, WatchStr

@dataclass
class States:

    stream_running: bool
    stream_setup: bool

    stream_title: str