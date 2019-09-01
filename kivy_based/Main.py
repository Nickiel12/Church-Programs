import flask
from flask_socketio import SocketIO
from flask_mobility import Mobility
from flask_mobility.decorators import mobile_template
from kivy.app import App
import os
import time
import pathlib2
import eventlet
eventlet.monkey_patch()

from Gui import GuiApp 
from utils import threaded

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
Mobility(app)

path = pathlib2.Path(
"C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs"+
"\\OBS Studio\\OBS Studio (64bit).lnk")
os.startfile(str(path))
gui_app = GuiApp()

SceneController = None

@threaded
def loop():
    time.sleep(3)
    print("starting webserver")
    start_web_server()
    global SceneController
    SceneController = App.get_running_app().root.ids.MainScreen.ids.ScenePanel
    while True:
        socketio.emit("update", {"data":"None", 
            "states":[
                SceneController.current_scene=="camera",
                SceneController.current_scene=="center",
                SceneController.ids.SCQAutomatic.ids.cb.active,
                SceneController.timer_left
            ]})
        time.sleep(.2)

@app.route("/")
@mobile_template("{mobile_}index.html")
def index(template):
    return flask.render_template(template)

@socketio.on("event")
def my_event(data):
    print(f"Recieved data: {data}")

@socketio.on("scene_camera")
def on_scene_camera(event):
    SceneController.on_hotkey("camera")

@socketio.on("scene_center")
def on_scene_center(event):
    SceneController.on_hotkey("center")

@socketio.on("automatic_change")
def on_auto_change(event):
    SceneController.on_hotkey("scene_lock")

@socketio.on("slide_next")
def on_slide_next(event):
    SceneController.on_hotkey("clicker_next")

@socketio.on("slide_prev")
def on_slide_prev(event):
    SceneController.on_hotkey("clicker_prev")

@threaded
def start_web_server():
    socketio.run(app, host="0.0.0.0")
    
if __name__ == '__main__':
    print("starting")
    #loop()
    gui_app.run()
