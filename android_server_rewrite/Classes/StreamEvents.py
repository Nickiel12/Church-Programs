from enum import auto


class StreamEvents:

    CAMERA_SCENE = "Scene_Camera"
    SCREEN_SCENE = "Scene_Screen"
    AUGMENTED_SCENE = "Augmented"
    AUGMENTED_ON = "Augmented_On"
    AUGMENTED_OFF = "Augmented_Off"
    AUTO_CHANGE_TO_CAMERA = "Auto_Change_To_Camera"

    TIMER_RUNNING = "Timer_Pause"
    TIMER_CHANGE_LENGTH = "Timer_Length"
    CHANGE_WITH_CLICKER_ON = "Change_With_Clicker_On"
    CHANGE_WITH_CLICKER_OFF = "Change_With_Clicker_Off"

    PREV_SLIDE = "Prev_Slide"
    NEXT_SLIDE = "Next_Slide"
    TOGGLE_COMPUTER_VOLUME = "Toggle_Computer_Volume"
    TOGGLE_STREAM_VOLUME = "Toggle_Stream_Volume"

    # Media buttons
    MEDIA_PAUSE_PLAY = "Media_Pause_Play"
    MEDIA_VOLUME_DOWN = "Media_Volume_Down"
    MEDIA_VOLUME_UP = "Media_Volume_Up"

    OBS_MUTE = "OBS_Mute"
    OBS_UNMUTE = "OBS_Unmute"
    START_STREAM = "Start_Stream"
    STOP_STREAM = "Stop_Stream"

    UPDATE_REQUEST = "Update_Request"
