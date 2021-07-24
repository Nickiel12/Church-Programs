import enum
from enum import auto


class SubScenes(enum.IntEnum):
    CAMERA_NONE = auto()
    CAMERA_TOP_RIGHT = auto()
    CAMERA_BOTTOM_RIGHT = auto()
    CAMERA_BOTTOM_LEFT = auto()
    SCREEN_NONE = auto()
    SCREEN_TOP_RIGHT = auto()
    SCREEN_BOTTOM_RIGHT = auto()