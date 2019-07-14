from ahk import AHK
from ahk.window import Window

import logging
from logging import debug
if __name__=="__main__":
	logging.basicConfig(level=logging.DEBUG,
		format= '%(asctime)s - %(levelname)s - %(message)s')

import pathlib2
import subprocess
from threading import Thread
import time
import webbrowser

class AHKHandeler():

    def __init__(self, stream_name, obs_start_hotkey="^+J", obs_stop_hotkey="^!J"):
        self.ahk = AHK()
        self.get_OBS()
        self.get_ProPresenter()
        self.obs_start_stream_hotkey = obs_start_hotkey
        self.obs_stop_stream_hotkey = obs_stop_hotkey
        debug(self.obs_start_stream_hotkey)

        time.sleep(1)

        self.stream_title = stream_name

    def get_ProPresenter(self):
        self.ProPresenter = self.ahk.win_get("ProPresenter - Registered To: VALLEY CHRISTAIN CENTER")
        return self.ProPresenter

    def propresenter_send(self, key, window=None):
        old_window = self.ahk.active_window
        if self.ahk.active_window == self.get_ProPresenter():
            self.ahk.send(key)
        if window == None:
            window = self.get_ProPresenter()
            logging.warning(f"sending {key} to ProPresenter")
            window.activate()
            time.sleep(2)
            self.ahk.send(key)
            time.sleep(.5)
            old_window.activate()

    def get_OBS(self):
        self.OBS = self.ahk.win_get("OBS")
        if self.OBS.id == "":
            self.open_OBS()
            self.OBS = self.ahk.win_get("OBS")
        return self.OBS

    def open_OBS(self):
       self.ahk.run_script("CoordMode, Mouse, Screen\n"+
       "MouseMove, 516, 998 \n Click")
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
        old_window.activate()

    def chrome_facebook_live_start(self):
        webbrowser.open("https://www.facebook.com/CenterEvents1/")

        # Upstairs deployment settings
        thread = Thread(target = self.start_stream, args=(8000, (430, 593),
        (719, 152), self.stream_title, (1018, 518), (1174, 922)))

        # Nick's Laptop
        # thread = Thread(target=self.start_stream_facebook, args=(8000, (711, 741), 
        # (1084, 190), "A really cool title", (1577, 649), (1804, 960)))
        thread.start()

    def start_stream_facebook(
        self,
        # Facebook related
        wait_time:int, live_position:tuple, connect_position:tuple, stream_title:str,
        stream_label_position:tuple, stream_go_live_position:tuple,
        obs_window = None
        ):

        if obs_window == None:
            obs_window = self.get_OBS()
        if stream_title == None:
            raise ValueError("No stream title was given")

        self.ahk.run_script(f"#NoEnv \n Sleep {wait_time} \n "+
            # Click Live
            f"MouseMove, {live_position[0]}, {live_position[1]} \n"+
            "Sleep 250 \n Click \n Sleep 5000 \n"+
            # Click connect
            f"MouseMove, {connect_position[0]}, {connect_position[1]} \n Sleep 250 \n"+
            "Click \n Sleep 1500 \n"
                )

        self.chrome_window = self.ahk.active_window
        self.end_stream_position = stream_go_live_position

        # Start the OBS stream
        self.OBS_send(self.obs_start_stream_hotkey)
        time.sleep(2)

        # Click go live button on facebook
        self.ahk.run_script(f"#NoEnv \n"+
            # Click Title label
            f"MouseMove, {stream_label_position[0]}, {stream_label_position[1]},"+
            f"\n Sleep 250 \n Click \n Send {stream_title} \n"+
            f"MouseMove, {stream_go_live_position[0]}, {stream_go_live_position[1]}\n"#+
            "Sleep 250 \n Click"
            )

        return

    def stop_facebook_stream(self, end_stream_position:tuple):

        #self.OBS_send(self.obs_stop_stream_hotkey)
        if self.chrome_window != None:
            self.chrome_window.activate()
            self.ahk.run_script(f"MouseMove, {self.end_stream_position[0]},"+
                f" {self.end_stream_position[1]}"+
                "\n Sleep 250 \n Click")
            self.OBS_send("^!j")

        raise ReferenceError

if __name__ == "__main__":
    ahker = AHKHandeler()
    ahker.chrome_facebook_live_start()
    time.sleep(30)
    ahker.stop_facebook_stream((1804, 960))