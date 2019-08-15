import pyautogui
import time
import threading
import webbrowser
from utils import Settings
from dialogs import WarningPopup
if True == False:
    from kivy_based.utils import Settings
    from kivy_based.dialogs import WarningPopup

import logging
from logging import debug
if __name__=="__main__":
    logging.basicConfig(level=logging.DEBUG,
        format= '%(asctime)s - %(levelname)s - %(message)s')

def setup_facebook(stream_title, is_dev=False):
    thread = threading.Thread(target = threaded_setup_facebook)
    debug("starting")
    thread.start()    

def threaded_setup_facebook():
    popup = WarningPopup()
    popup.open()
    debug("popup opened")
    settings = Settings()
    debug("loaded settings")
    sfb = settings.setup_facebook
    webbrowser.open(sfb.url)
    debug(f"opened browser with url: {sfb.url}")
    time.sleep(sfb.wait_0)
    pyautogui.click(sfb.one[0], sfb.one[1])
    time.sleep(sfb.wait_1)
    pyautogui.click(sfb.two[0], sfb.two[1])
    time.sleep(sfb.wait_2)
    pyautogui.click(sfb.three[0], sfb.three[1])

    popup.close()
    return True

if __name__ == "__main__":
    setup_facebook("it'sa supera coolera")