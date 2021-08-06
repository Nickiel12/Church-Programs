from Classes.StreamEvents import StreamEvents as SE
from Classes.SubScenes import SubScenes as SS

import logging

logger = logging.getLogger(__name__)


# the biggest issue with this function is the fact that all socket messages, are strings
# so all of these have to be strings
def handle_message(socket_json: dict, message_handler=None):
    if message_handler is None:
        return
    logger.info("handling a message")

    try:
        message_type = socket_json["type"]

        if message_type == "Timer_Length":
            message_handler(SE.TIMER_CHANGE_LENGTH, socket_json["data"])

        if message_type == "button":
            button = socket_json["button"]

            if button == "Scene_Camera":
                message_handler(SE.CAMERA_SCENE)
            elif button == "Scene_Screen":
                message_handler(SE.SCREEN_SCENE)
            elif button == "Prev_Slide":
                message_handler(SE.PREV_SLIDE)
            elif button == "Next_Slide":
                message_handler(SE.NEXT_SLIDE)

            elif button == "Auto_Change_To_Camera":
                message_handler(SE.AUTO_CHANGE_TO_CAMERA, event_data=socket_json["data"])
            elif button == "Timer_Pause":
                message_handler(SE.TIMER_RUNNING, event_data=socket_json["data"])
            elif button == "Augmented":
                if socket_json["data"]:
                    message_handler(SE.AUGMENTED_ON)
                else:
                    message_handler(SE.AUGMENTED_OFF)
            elif button == "Change_With_Clicker":
                if socket_json["data"]:
                    message_handler(SE.CHANGE_WITH_CLICKER_ON)
                else:
                    message_handler(SE.CHANGE_WITH_CLICKER_OFF)

            elif button == "Toggle_Computer_Volume":
                message_handler(SE.TOGGLE_COMPUTER_VOLUME, event_data=socket_json["data"])
            elif button == "Toggle_Stream_Volume":
                message_handler(SE.TOGGLE_STREAM_VOLUME, event_data=socket_json["data"])

            elif button == "Media_Pause_Play":
                message_handler(SE.MEDIA_PAUSE_PLAY)

            elif button == "Camera_None":
                message_handler(SS.Camera.CAMERA_NONE)
            elif button == "Camera_Top_Right":
                message_handler(SS.Camera.CAMERA_TOP_RIGHT)
            elif button == "Camera_Bottom_Right":
                message_handler(SS.Camera.CAMERA_BOTTOM_RIGHT)
            elif button == "Camera_Bottom_Left":
                message_handler(SS.Camera.CAMERA_BOTTOM_LEFT)
            elif button == "Screen_None":
                message_handler(SS.Screen.SCREEN_NONE)
            elif button == "Screen_Top_Right":
                message_handler(SS.Screen.SCREEN_TOP_RIGHT)
            elif button == "Screen_Bottom_Right":
                message_handler(SS.Screen.SCREEN_BOTTOM_RIGHT)

            # sitting here, doing nothing, neglected
            elif button == "ExtraBottomRightMid":
                pass

        elif message_type == "update":
            specifier = socket_json["specifier"]
            if specifier == "all":
                message_handler(SE.UPDATE_REQUEST, specifier)
    except Exception as e:
        logger.critical(f"Message not handled :`(  {socket_json}")
        raise e
