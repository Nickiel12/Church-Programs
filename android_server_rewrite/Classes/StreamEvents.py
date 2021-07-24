import enum
from enum import auto


class StreamEvents(enum.Flag):

    class SubScenes(enum.IntEnum):
        CAMERA_NONE = auto()
        CAMERA_TOP_RIGHT = auto()
        CAMERA_BOTTOM_RIGHT = auto()
        CAMERA_BOTTOM_LEFT = auto()
        SCREEN_NONE = auto()
        SCREEN_TOP_RIGHT = auto()
        SCREEN_BOTTOM_RIGHT = auto()

    CAMERA_SCENE = auto()
    SCREEN_SCENE = auto()
    SPECIAL_SCENE = auto()
    AUGMENTED_ON = auto()
    AUGMENTED_OFF = auto()
    AUTO_CHANGE_TO_CAMERA = auto()

    TIMER_RUNNING = auto()
    TIMER_CHANGE_LENGTH = auto()
    CHANGE_WITH_CLICKER_ON = auto()
    CHANGE_WITH_CLICKER_OFF = auto()

    PREV_SLIDE = auto()
    NEXT_SLIDE = auto()
    TOGGLE_COMPUTER_VOLUME = auto()
    TOGGLE_STREAM_VOLUME = auto()
    MEDIA_PAUSE_PLAY = auto()
