
import logging

from Classes.MasterController import MasterController

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s][%(levelname)s] %(message)s', datefmt='%H:%M:%S')
#datefmt='%m/%d/%Y %H:%M:%S'
logger = logging.getLogger("Main")


#Go here for intermediate processing (get event from socket, 
# send it here, then send to automationcontroller for dispatch)
# ./Classes/MasterController.py
MasterApp = MasterController()

if __name__ == "__main__":
    MasterApp.start()
    try:
        input()
    except KeyboardInterrupt:
        pass
    MasterApp.stop()
