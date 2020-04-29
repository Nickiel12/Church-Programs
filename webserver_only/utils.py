import atexit
import json
import math
import pathlib
import threading
import keyboard
import mouse
from functools import partial, wraps
import os
import time
import webbrowser
import logging

logger = logging.getLogger(__name__)

from exceptions import PopupNotExist
from dialogs import WarningPopup, Question

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s')


def threaded(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"starting thread with target {func}")
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper


def with_popup(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.popup is False:
            raise PopupNotExist
        func(self, *args, **kwargs)
    return wrapper


@threaded
def open_program(program, program_path=None):
    """opens the program argument, if present, program_path is opened instead

    Arguments:
        program {str} -- either "obs", or "propresenter"

    Keyword Arguments:
        program_path {str or pathlib path object} -- a path to a file to open (default: {None})
    """

    # TODO add propresenter path
    obs_path = pathlib.Path("C:\\ProgramData\\Microsoft\\Windows\\Start Menu" +
                            "\\Programs\\OBS Studio\\OBS Studio (64bit).lnk")
    pro_path = pathlib.Path("C:\\Program Files (x86)\\Renewed Vision\\+" +
                             "ProPresenter 6\\ProPresenter.exe")

    if not program_path:
        if program.lower() == "obs":
            os.startfile(str(obs_path))
        elif program.lower() == "propresenter":
            os.startfile(str(pro_path))

class Setup:
    def __init__(self, popup: WarningPopup, stream_title: str, 
                 auto_contro
                 #: AutomationController,
                 ,settings, *args, **kwargs):
        self.auto_contro = auto_contro
        self.popup = popup
        self.stream_title = stream_title
        self.settings = settings
        self.platform_settings = self.settings[f"setup_" +
                                    f"{self.settings.streaming_service}"]

    def del_popup(self):
        self.popup = False

    def set_popup(self, popup):
        self.popup = popup

    def open_url(self, url, timer_time):
        logger.info(f"Opening {url}")
        self.popup.set_task("Opening Browser", timer_time)
        webbrowser.open(url)

    @with_popup
    @threaded
    def sleep(self, time_to_sleep):
        logger.info(f"setup is sleeping for {time_to_sleep}")
        self.popup.set_task("Waiting", time_to_sleep)
        time.sleep(time_to_sleep)

    @with_popup
    @threaded
    def mouse_click(self, mouse_pos: tuple, timer_time):
        self.popup.set_task("Moving & Clicking Mouse", timer_time)
        mouse.move(mouse_pos[0], mouse_pos[1])
        mouse.click()

    @with_popup
    @threaded
    def write(self, text: str, timer_time):
        self.popup.set_task("Entering Text", timer_time)
        keyboard.write(text)

def make_functions(setup_inst):
    output = []
    platform_settings = setup_inst.platform_settings
    length = len(platform_settings)
    for i in range(1, length):
        current_type = platform_settings[str(i)]["type"]
        if current_type == "Open URL":
            output.append([partial(setup_inst.open_url,
                          platform_settings[str(i)]["value"], .2), .2])
        elif current_type == "Wait":
            output.append([partial(setup_inst.sleep, 
                           platform_settings[str(i)]["value"]), platform_settings[str(i)]["value"]])
        elif current_type == "Mouse Movement":
            output.append([partial(setup_inst.mouse_click,
                           platform_settings[str(i)]["value"], .5), .5])
        elif current_type == "Text Field":
            output.append([partial(setup_inst.write,
                           setup_inst.stream_title, 1), 1])
        elif current_type == "Go Live":
            setup_inst.auto_contro.settings["go_live"]= platform_settings[str(i)]["value"]
    output.append([partial(setup_inst.auto_contro.obs_send,
        "start"), 1])
    return output


class DotDict(dict):
    """dot.notation access to dictionary attributes"""
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, iterable):
        super().__init__()
        if isinstance(iterable, dict):
            for k, v in iterable.items():
                self[k] = v

    def __getattr__(*args):
        val = dict.get(*args)
        return DotDict(val) if type(val) is dict else val
