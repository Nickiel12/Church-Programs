import wx
if __name__ != "__main__":
    import StreamController.Gui as Gui
else:
    import Gui

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

controllerGui = Gui.ChurchGui()
