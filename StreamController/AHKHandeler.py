from ahk import AHK, Bindable_Hotkey
from ahk.window import Window
import atexit
from enum import Enum
import pathlib2
import subprocess
from threading import Thread
import time
import webbrowser

from option_loader import JSD

import logging
from logging import debug

class WindowClassEnum(Enum):
    CHROME = 1    

class AHKHandeler:

    WINDOW_CLASSES = WindowClassEnum

    def __init__(self, stream_name:str, json_dict):
        """
            Stream name
        """
        self.decoder = json_dict
        self.stream_title = stream_name
        
        self.ahk = AHK()
        self.get_OBS()
        self.get_ProPresenter()
        #self.start_hotkeys()
        atexit.register(self.stop_hotkeys)
         
    def start_hotkeys(self):
        self.camera_scene_hotkey = Bindable_Hotkey(self.ahk, self.decoder[
            JSD.CAMERA_SCENE_HOTKEY])
        self.camera_scene_hotkey.bind(lambda:self.OBS_send(self.decoder[
            JSD.CAMERA_SCENE_OBS]))
        self.screen_scene_hotkey = Bindable_Hotkey(self.ahk, self.decoder[
            JSD.CENTER_SCREEN_HOTKEY])
        self.screen_scene_hotkey.bind(lambda:self.OBS_send(self.decoder[
            JSD.CENTER_SCREEN_OBS]))

        self.camera_scene_hotkey.start()
        self.screen_scene_hotkey.start()
        return

    def stop_hotkeys(self):
        self.camera_scene_hotkey.stop()
        self.screen_scene_hotkey.stop()

    def get_ProPresenter(self):
        self.ProPresenter = self.ahk.win_get(self.decoder[JSD.WINDOW_PROPRESENTER])
        return self.ProPresenter

    def propresenter_send(self, key, window=None):
        old_window = self.ahk.active_window
        if self.ahk.active_window == self.get_ProPresenter():
            self.ahk.send(key)
        if window == None:
            window = self.get_ProPresenter()
            window.activate()
            time.sleep(2)
            self.ahk.send(key)
            time.sleep(.5)
            old_window.activate()

    def bring_to_front(self, preset_classes, window_class=None):
        if window_class == None:
            if preset_classes == self.WINDOW_CLASSES.CHROME:
                window_class = "Chrome_WidgetWin_1"
        self.ahk.run_script(f"WinActivate, ahk_class {window_class} \n WinMaximize")
        return

    def get_OBS(self):
        self.OBS = self.ahk.win_get("OBS")
        if self.OBS.id == "":
            self.open_OBS()
            self.OBS = self.ahk.win_get("OBS")
        return self.OBS

    def open_OBS(self):
        self.ahk.run_script("CoordMode, Mouse, Screen\n"+
            f"MouseMove, {self.decoder[JSD.TRAY_OBS_POS][0]}, "+
            f"{self.decoder[JSD.TRAY_OBS_POS][1]} \n Click\n"+
            "Sleep 500 \n MouseMove, 500, 500")
        time.sleep(1)
        return
 
    def OBS_send(self, key, window=None):
        old_window = self.ahk.active_window
        if window == None:
            window = self.get_OBS()
        logging.warning(f"sending {key} to obs")
        window.activate()
        time.sleep(.5)
        self.ahk.send(key)
        time.sleep(.5)
        window.to_bottom()
        old_window.activate()
        return

    def chrome_facebook_live_start(self):
        webbrowser.open("https://www.facebook.com/CenterEvents1/")

        # Upstairs deployment settings
        thread = Thread(target = self.setup_stream_facebook, args=(8000, (430, 593),
        (719, 152), self.stream_title, (1018, 518)))

        # Nick's Laptop
        # thread = Thread(target=self.setup_stream_facebook, args=(8000, (711, 741), 
        # (1084, 190), "A really cool title", (1577, 649)))
        thread.start()

    def setup_stream_facebook(
        self,
        # Facebook related
        wait_time:int, live_position:tuple, connect_position:tuple, stream_title:str,
        stream_label_position:tuple,
        obs_window = None
        ):

        if obs_window == None:
            obs_window = self.get_OBS()
        if self.stream_title == None:
            raise ValueError("No stream title was given")

        self.bring_to_front(self.WINDOW_CLASSES.CHROME)
        self.ahk.run_script(f"#NoEnv \n CoordMode, Mouse, Screen"+
            " \n Sleep {wait_time} \n "+
            # Click Live
            f"MouseMove, 500, 500 \n Sleep 500 \n"+
            f"MouseMove, {live_position[0]}, {live_position[1]} \n"+
            "Sleep 250 \n Click \n Sleep 5000 \n"+
            # Click connect
            f"MouseMove, {connect_position[0]}, {connect_position[1]} \n Sleep 250 \n"+
            "Click \n Sleep 1500 \n"
                )

        # Start the OBS stream
        self.OBS_send(self.decoder[JSD.OBS_START_STREAM])
        time.sleep(2)

        # Click go live button on facebook
        self.ahk.run_script(f"#NoEnv \n"+
            # Click Title label
            f"MouseMove, {stream_label_position[0]}, {stream_label_position[1]},"+
            f"\n Sleep 250 \n Click \n Send {stream_title} \n"
            )

        return

    def start_facebook_stream(self, stream_go_live_position=(1018, 518)):
        original_window = self.ahk.active_window
        self.bring_to_front(self.WINDOW_CLASSES.CHROME)
        time.sleep(1)
        self.ahk.run_script(f"MouseMove, {stream_go_live_position[0]},"+
        f" {stream_go_live_position[1]}\n"+
            "Sleep 250 \n Click", blocking = False)
        original_window.activate()

    def stop_facebook_stream(self):

        self.OBS_send(self.decoder[JSD.OBS_STOP_STREAM])
        self.bring_to_front(self.WINDOW_CLASSES.CHROME)
        
        self.OBS_send("^!j")

        raise ReferenceError

if __name__ == "__main__":
    ahker = AHKHandeler()
    ahker.chrome_facebook_live_start()
    time.sleep(30)
    ahker.stop_facebook_stream((1804, 960))