import atexit
import json
import pathlib2
import os

class Settings:
    
    def __init__(self):
        path = pathlib2.Path(os.path.abspath(__file__)).parent/options.json
        with open(path) as file:
            self.json_file = json.loads(file.read())
        self.setup_facebook = self.json_file.setup_facebook