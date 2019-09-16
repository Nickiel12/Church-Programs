import atexit
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
        print(f"thread with target \"{func}\" has been started")
        return thread
    return wrapper


def make_functions(setup_inst):
    output = []
    platform_settings = setup_inst.platform_settings
    for i in platform_settings:
        if i[:3] == "url":
            output.append([partial(setup_inst.open_url,
                          platform_settings[i], .2), .2])
        elif i[:4] == "wait":
            output.append([partial(setup_inst.sleep, 
                           platform_settings[i]), platform_settings[i]])
        elif i[:3] == "mos":
            output.append([partial(setup_inst.mouse_click,
                           platform_settings[i], .5), .5])
        elif i == "title":
            output.append([partial(setup_inst.write,
                           setup_inst.stream_title, 1), 1])
    return output


def Settings():
    path = pathlib2.Path(os.path.abspath(__file__)
                         ).parent/"extras"/"options.json"
    with open(path) as file:
        json_file = json.load(file)
    return DotDict(json_file)


class DotDict(dict):
    """dot.notation access to dictionary attributes"""
    def __init__(self, iterable):
        super().__init__()
        if isinstance(iterable, dict):
            for k, v in iterable.items():
                self[k] = v

    def __getattr__(*args):
        val = dict.get(*args)
        return DotDict(val) if type(val) is dict else val
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
