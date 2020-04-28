from dataclasses import dataclass

from Classes.Watch_Classes import WatchBool, WatchNumber, WatchStr

@dataclass
class States:

    stream_running: WatchBool
    stream_setup: WatchBool

    stream_title: WatchStr