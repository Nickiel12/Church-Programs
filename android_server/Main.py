
import engineio.async_drivers.gevent
import logging
from gevent import monkey
import flask
from flask_mobility import Mobility
from flask_socketio import SocketIO

from Classes.MasterController import MasterController
from Classes.Flask_Router import route

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s][%(levelname)s] %(message)s', datefmt='%H:%M:%S')
#datefmt='%m/%d/%Y %H:%M:%S'
logger = logging.getLogger("Main")
web_logger = logging.getLogger("Main.webserver")


app = flask.Flask(__name__)
app.config['SECRET_KEY'] = '$hor!K#y'
socketio = SocketIO(app, async_mode='gevent')
monkey.patch_socket()
Mobility(app)

#Go here for intermediate processing (get event from socket, 
# send it here, then send to automationcontroller for dispatch)
# ./Classes/MasterController.py
MasterApp = MasterController(socketio=socketio)

#Go here for routing and socket event handling ./Classes/Flask_Router.py
route(app, socketio, MasterApp)

if __name__ == "__main__":
    MasterApp.start(app)
