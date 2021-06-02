
from Classes.StreamEvents import StreamEvents as SE

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s][%(levelname)s] %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger("MessageHandler")

def handle_message(socket_json:dict, masterApp):
    logger.info("handling a message")

    try:    
        type = socket_json["type"]

        if type == "button":
            button = socket_json["button"]

            if button == "Scene_Camera":
                masterApp.event_handeler.handle_state_change(SE.CAMERA_SCENE)
            elif button == "Scene_Screen":
                masterApp.event_handeler.handle_state_change(SE.SCREEN_SCENE)
            elif button == "Prev_Slide":
                masterApp.event_handeler.handle_state_change(SE.PREV_SLIDE)
            elif button == "Next_Slide":
                masterApp.event_handeler.handle_state_change(SE.NEXT_SLIDE)

            elif button == "Timer_Pause":
                masterApp.event_handeler.handle_state_change(SE.TIMER_PAUSE, event_data=socket_json["data"])
            elif button == "Augmented":
                if (socket_json["data"] == "true"):
                    masterApp.event_handeler.handle_state_change(SE.AUGMENTED_ON)
                else:
                    masterApp.event_handeler.handle_state_change(SE.AUGMENTED_OFF)
            elif button == "ChangeWithClicker":
                pass
            
            elif button == "ExtraTopLeft":
                pass
            elif button == "ExtraTopLeftMid":
                pass
            elif button == "ExtraTopRightMid":
                pass
            elif button == "ExtraTopRight":
                pass
            elif button == "ExtraBottomLeft":
                pass
            elif button == "ExtraBottomLeftMid":
                pass
            elif button == "ExtraBottomRightMid":
                pass
            elif button == "ExtraBottomRight":
                pass
    except Exception as e:
        logger.critical(f"Message not handled :`(  {socket_json}")
        raise e
            
                