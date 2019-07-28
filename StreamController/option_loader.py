import atexit
import pathlib2
import os
import shelve

path = pathlib2.Path(os.path.join(os.path.abspath(__file__)))
path = path.parents[0]
path = path/"options"/"data"

class ShelveHandeler:
    def __init__(self):
        self.shelf = shelve.open(str(path))
        atexit.register(close)

    def close(self):
        self.shelf.close()

    def assign(self, key, value):
        self.shelf[key] = value        