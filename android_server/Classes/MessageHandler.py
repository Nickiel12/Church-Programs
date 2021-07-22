
from Classes.StreamEvents import StreamEvents as SE

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s][%(levelname)s] %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger("MessageHandler")

def handle_message(socket_json:dict, masterApp):
    logger.info("handling a message")

    try:    
        type = socket_json["type"]

        if type == "timer":
            masterApp.event_handler.handle_state_change(SE.TIMER_CHANGE_LENGTH, socket_json["data"])

        if type == "button":
            button = socket_json["button"]

            if button == "Scene_Camera":
                masterApp.event_handler.handle_state_change(SE.CAMERA_SCENE)
            elif button == "Scene_Screen":
                masterApp.event_handler.handle_state_change(SE.SCREEN_SCENE)
            elif button == "Prev_Slide":
                masterApp.event_handler.handle_state_change(SE.PREV_SLIDE)
            elif button == "Next_Slide":
                masterApp.event_handler.handle_state_change(SE.NEXT_SLIDE)

            elif button == "Auto_Change_To_Camera":
                masterApp.event_handler.handle_state_change(SE.AUTO_CHANGE_TO_CAMERA, event_data=socket_json["data"])
            elif button == "Timer_Pause":
                masterApp.event_handler.handle_state_change(SE.TIMER_RUNNING, event_data=socket_json["data"])
            elif button == "Augmented":
                if (socket_json["data"] == True):
                    masterApp.event_handler.handle_state_change(SE.AUGMENTED_ON)
                else:
                    masterApp.event_handler.handle_state_change(SE.AUGMENTED_OFF)
            elif button == "ChangeWithClicker":
                if socket_json["data"] == True:
                    masterApp.event_handler.handle_state_change(SE.CHANGE_WITH_CLICKER_ON)
                else:
                    masterApp.event_handler.handle_state_change(SE.CHANGE_WITH_CLICKER_OFF)
            
            elif button == "Computer_Sound":
                masterApp.event_handler.handle_state_change(SE.TOGGLE_COMPUTER_VOLUME, event_data=socket_json["data"])
            elif button == "Stream_Sound":
                masterApp.event_handler.handle_state_change(SE.TOGGLE_STREAM_VOLUME, event_data=socket_json["data"])

            elif button == "MediaPausePlay":
                masterApp.event_handler.handle_state_change(SE.MEDIA_PAUSE_PLAY)

            elif button == "ExtraTopLeft":
                masterApp.event_handler.handle_state_change(SE.SPECIAL_SCENE, "Camera_None")
            elif button == "ExtraTopLeftMid":
                masterApp.event_handler.handle_state_change(SE.SPECIAL_SCENE, "Camera_Top_Right")
            elif button == "ExtraTopRightMid":
                masterApp.event_handler.handle_state_change(SE.SPECIAL_SCENE, "Screen_None")
            elif button == "ExtraTopRight":
                masterApp.event_handler.handle_state_change(SE.SPECIAL_SCENE, "Screen_Top_Right")
            elif button == "ExtraBottomLeft":
                masterApp.event_handler.handle_state_change(SE.SPECIAL_SCENE, "Camera_Bottom_Left")
            elif button == "ExtraBottomLeftMid":
                masterApp.event_handler.handle_state_change(SE.SPECIAL_SCENE, "Camera_Bottom_Right")
            elif button == "ExtraBottomRightMid":
                pass
            elif button == "ExtraBottomRight":
                masterApp.event_handler.handle_state_change(SE.SPECIAL_SCENE, "Screen_Bottom_Right")
                
        elif type == "update":
            specifier = socket_json["specifier"]
            if specifier == "all":
                masterApp.update_all()
    except Exception as e:
        logger.critical(f"Message not handled :`(  {socket_json}")
        raise e
            
                