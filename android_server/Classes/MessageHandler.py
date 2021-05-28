
from Classes.MasterController import MasterController
import json
from Classes.StreamEvents import StreamEvents as SE

def handle_message(socket_json:dict, masterApp:MasterController):
    type = socket_json["type"]
    if type == "button":
        button = socket_json["button"]

        if button == "Scene_Camera":
            masterApp.handle_state_change(SE.CAMERA_SCENE)
        elif button == "Scene_Screen":
            masterApp.handle_state_change(SE.SCREEN_SCENE)
        elif button == "Timer_Pause":
            masterApp.handle_state_change(SE.TIMER_PAUSE, socket_json["data"])
        elif button == "Prev_Slide":
            masterApp.handle_state_change(SE.PREV_SLIDE)
        elif button == "Next_Slide":
            masterApp.handle_state_change(SE.NEXT_SLIDE)
        
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

        
            