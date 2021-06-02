import enum
from enum import auto


class StreamEvents(enum.Flag):
    CAMERA_SCENE = auto()
    SCREEN_SCENE = auto()
    SPECIAL_SCENE = auto()
    AUGMENTED_ON = auto()
    AUGMENTED_OFF = auto()
    AUTO_CHANGE_TO_CAMERA = auto()

    TIMER_RUNNING = auto()
    TIMER_CHANGE_LENGTH = auto()
    AUTO_CHANGE_SCENE_ON = auto()
    AUTO_CHANGE_SCENE_OFF = auto()

    PREV_SLIDE = auto()
    NEXT_SLIDE = auto()
    TOGGLE_COMPUTER_VOLUME = auto()
    TOGGLE_STREAM_VOLUME = auto()
