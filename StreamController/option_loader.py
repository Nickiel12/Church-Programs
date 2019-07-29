import atexit
import pathlib2
import json
import os

class OptHandle:
    def __init__(self):
        path = pathlib2.Path(os.path.abspath(__file__)).parents[1]/"options.json"
        with open(str(path)) as file:
            self.dict = json.loads(file.read())
        atexit.register(self.dump_and_close)

    def dump_and_close(self):
        json.dumps(self.dict)

class JSD:
	" JSON decoder contains simple constants for easily readable json options decoding"
	# Window Classifiers
	WINDOW_PROPRESENTER = "propresenter_window_title"

	# OBS Hotkeys
	OBS_START_STREAM = "obs_start_stream"
	OBS_STOP_STREAM = "obs_stop_stream"

	# Live center screen
	CENTER_SCREEN_HOTKEY = "center_screen_hotkey"
	CENTER_SCREEN_OBS = "center_screen_obs_key"

	# Live from camera scene hotkeys
	CAMERA_SCENE_HOTKEY = "camera_scene_hotkey"
	CAMERA_SCENE_OBS = "camera_scene_obs_key"

	# Clicker Keys
	CLICKER_NEXT = "clicker_forward"
	CLICKER_PREV = "clicker_backward"

	# Mouse Screen Positions
	TRAY_OBS_POS = "obs_tray_position"
	FACEBOOK_LIVE_BUTTON = "facebook_live_button"
	FACEBOOK_CONNECT_BUTTON = "facebook_connect_button"
	FACEBOOK_STREAM_LABEL = "facebook_stream_label"
	FACEBOOK_GOLIVE_BUTTON = "facebook_golive_button"
