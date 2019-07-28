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

op = OptHandle()
print(op.dict)