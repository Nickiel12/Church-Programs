import atexit
from kivy.app import App
import json
import math
import pathlib2
import threading
from functools import partial, wraps
import os
import logging
from logging import debug

from exceptions import PopupNotExist

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s')


def threaded(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        if debug == None:
            print(f"thread with target \"{func}\" has been started")
        return thread
    return wrapper


@threaded
def open_program(program, program_path=None):
    """opens the program argument, if present, program_path is opened instead

    Arguments:
        program {str} -- either "obs", or "propresenter"

    Keyword Arguments:
        program_path {str or pathlib2 path object} -- a path to a file to open (default: {None})
    """

    # TODO add propresenter path
    obs_path = pathlib2.Path(
                            "C:\\ProgramData\\Microsoft\\Windows\\Start Menu" +
                            "\\Programs\\OBS Studio\\OBS Studio (64bit).lnk")
    pro_path = pathlib2.Path("C:\\Program Files (x86)\\Renewed Vision\\+" +
                             "ProPresenter 6\\ProPresenter.exe")

    if not program_path:
        if program.lower() == "obs":
            os.startfile(str(obs_path))
        elif program.lower() == "propresenter":
            os.startfile(str(pro_path))


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
            print(setup_inst.auto_contro.settings)
    output.append([partial(setup_inst.auto_contro.obs_send,
        "start"), 1])
    return output


def Settings():
    path = pathlib2.Path(os.path.abspath(__file__)
                         ).parent/"extras"/"options.json"
    with open(path) as file:
        json_file = json.load(file)
    dot_dict = DotDict(json_file)
    path = path.parent / "options" / str(dot_dict.streaming_service + ".json")
    with open(path) as file:
        json_file_2 = json.load(file)
    dot_dict["setup_" + dot_dict.streaming_service] = DotDict(json_file_2)
    return dot_dict


class DotDict(dict):
    """dot.notation access to dictionary attributes"""
    def __init__(self, iterable):
        super().__init__()
        if isinstance(iterable, dict):
            for k, v in iterable.items():
                self[k] = v

    def __getattr__(self, *args):
        val = dict.get(*args)
        return DotDict(val) if type(val) is dict else val
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
