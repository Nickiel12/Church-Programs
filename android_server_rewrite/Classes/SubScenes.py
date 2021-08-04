import enum
from enum import auto


class SubScenes:

    class Camera(enum.IntEnum):
        CAMERA_NONE = auto()
        CAMERA_TOP_RIGHT = auto()
        CAMERA_BOTTOM_RIGHT = auto()
        CAMERA_BOTTOM_LEFT = auto()

    class Screen(enum.IntEnum):
        SCREEN_NONE = auto()
        SCREEN_TOP_RIGHT = auto()
        SCREEN_BOTTOM_RIGHT = auto()

    AUGMENTED = auto()
