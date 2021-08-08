import logging
import pathlib

from Classes.MasterController import MasterController

import logging

# logging.basicConfig(level=logging.INFO,
#                    format='{%(name)s}[%(asctime)s][%(levelname)s] %(message)s', datefmt='%H:%M:%S',
#                    filename="log.txt")
# datefmt='%m/%d/%Y %H:%M:%S'


logger = logging.getLogger("Main")
logger.setLevel(logging.DEBUG)
# This sets the minimum level it will process, even when we later add handlers
# it will discard below this level first

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s', datefmt='%H:%M:%S')
stream_handler.setFormatter(formatter)

logFilePath = pathlib.Path(".").parent / "log.txt"
file_handler = logging.FileHandler(logFilePath)
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('{%(name)s}[%(asctime)s][%(levelname)s] - {%(funcName)s} - %(message)s',
                              datefmt='%H:%M:%S')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)


# Go here for intermediate processing (get event from socket,
# send it here, then send to automation controller for dispatch)
# ./Classes/MasterController.py
MasterApp = MasterController()

if __name__ == "__main__":
    try:
        input()
    except KeyboardInterrupt:
        pass
    MasterApp.stop()
