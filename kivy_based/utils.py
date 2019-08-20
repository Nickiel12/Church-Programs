import atexit
import json
import math
import pathlib2
import threading
from functools import partial, wraps
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

def threaded(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        print(f"thread with target \"{func}\" has been started")
        return thread
    return wrapper

@threaded
def open_program(program, program_path = None):
    """opens the program argument, if present, program_path is opened instead
    
    Arguments:
        program {str} -- either "obs", or "propresenter"
    
    Keyword Arguments:
        program_path {str or pathlib2 path object} -- a path to a file to open (default: {None})
    """

#TODO add propresenter path
    obs_path = pathlib2.Path(
    "C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs"+
    "\\OBS Studio\\OBS Studio (64bit).lnk")

    if not program_path:
        if program.lower() == "obs":
            os.startfile(str(obs_path))
        elif program.lower() == "propresenter":
            raise NotImplementedError("propresenter, open path not implemented")
            #os.startfile(str(pro_path))
def make_functions(setup_inst):
    output = []
    platform_settings = setup_inst.platform_settings
    for i in platform_settings:
        if i[:3] == "url": output.append([partial(setup_inst.open_url, 
            platform_settings[i], .2), .2])
        elif i[:4] == "wait": output.append([partial(setup_inst.sleep, 
            platform_settings[i]), platform_settings[i]])
        elif i[:3] == "mos": output.append([partial(setup_inst.mouse_click,
            platform_settings[i], .5), .5])
        elif i == "title": output.append([partial(setup_inst.write,
            setup_inst.stream_title, 1), 1])
    return output

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