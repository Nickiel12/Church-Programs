import atexit
import json
import math
import pathlib2
from functools import partial
import os

import logging
from logging import debug
if __name__=="__main__":
    logging.basicConfig(level=logging.DEBUG,
        format= '%(asctime)s - %(levelname)s - %(message)s')

from exceptions import PopupNotExist
if True == False:
    from kivy_based.exceptions import PopupNotExist
    from kivy_based.automation_controller import Setup

def make_functions(setup_inst):
    output = []
    platform_settings = setup_inst.platform_settings
    for i in platform_settings:
        if i[:3] == "url": output.append([partial(setup_inst.open_url, 
            platform_settings[i], 2), .2])
        elif i[:4] == "wait": output.append([partial(setup_inst.sleep, 
            platform_settings[i]), platform_settings[i]])
        elif i[:3] == "mos": output.append([partial(setup_inst.mouse_click,
            platform_settings[i], .5), .5])
        elif i == "title": output.append([partial(setup_inst.input_text,
            setup_inst.stream_title, 1), 1])

def Settings():
    path = pathlib2.Path(os.path.abspath(__file__)).parent/"options.json"
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

if __name__ == "__main__":
    pass