import copy
import pathlib
import json
import logging

from utils import DotDict

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s][%(levelname)s] %(message)s', datefmt='%H:%M:%S')
#datefmt='%m/%d/%Y %H:%M:%S'
logger = logging.getLogger("Main")


class MasterState:

    OPTIONS_FILE_PATH = pathlib.Path(".").parent/"extras"/"options.json"
    settings = None

    def __init__(self):
        self.update_settings()

    def update_settings(self):
        if self.settings != None:
            tmp_settings = copy.deepcopy(self.settings)
        try:
            with open(self.OPTIONS_FILE_PATH) as file:
                json_file = json.load(file)
            dot_dict = DotDict(json_file)
            path = self.OPTIONS_FILE_PATH.parent / "options" / \
                str(dot_dict.streaming_service + ".json")
            with open(path) as file:
                json_file_2 = json.load(file)
            dot_dict["setup_" +
                     dot_dict.streaming_service] = DotDict(json_file_2)
            self.settings = dot_dict
            logger.info("Successfully updated settings from file")
        except (json.JSONDecodeError) as e:
            logger.warning("Loading settings from file failed")
            logger.error(e)
            self.settings = tmp_settings


if __name__ == "__main__":
    MasterState()
