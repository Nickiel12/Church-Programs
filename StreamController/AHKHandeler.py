from ahk import AHK
from ahk.window import Window

import logging
from logging import debug
if __name__=="__main__":
	logging.basicConfig(level=logging.DEBUG,
		format= '%(asctime)s - %(levelname)s - %(message)s')

from threading import Thread
import time
import webbrowser

class AHKHandeler():

    def __init__(self, obs_start_hotkey="^+J", obs_stop_hotkey="^!J"):
        self.ahk = AHK()
        self.get_OBS()
        self.get_ProPresenter()
        self.obs_start_stream_hotkey = obs_start_hotkey
        debug(self.obs_start_stream_hotkey)

    def get_OBS(self):
        self.OBS = self.ahk.win_get("OBS")
        return self.OBS

    def get_ProPresenter(self):
        self.ProPresenter = self.ahk.win_get("ProPresenter")
        return self.ProPresenter

    def propresenter_send(self, key, window=None):
        if window == None:
            window = self.get_ProPresenter()
        window.send(key)

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
        thread = Thread(target=self.start_stream_facebook, args=(8000, (711, 741), 
        (1084, 190), "A really cool title", (1577, 649), (1804, 960)))
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
            "Click \n Sleep 5000 \n"+
            # Click connect
            f"MouseMove, {connect_position[0]}, {connect_position[1]} \n"+
            "Click \n Sleep 1500 \n"+
            # Click Title label
            f"MouseMove, {stream_label_position[0]}, {stream_label_position[1]},"
            f"\n Click \n Send {stream_title} \n"
                )

        # Start the OBS stream
        self.OBS_send(self.obs_start_stream_hotkey)
        time.sleep(2)

        # Click go live button on facebook
        self.ahk.run_script(f"#NoEnv \n"+
            f"MouseMove, {stream_go_live_position[0]}, {stream_go_live_position[1]}\n"+
            "Click")

        return

if __name__ == "__main__":
    ahker = AHKHandeler()
    ahker.chrome_facebook_live_start()