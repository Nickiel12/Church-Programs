import flask
from flask_socketio import SocketIO
from flask_mobility import Mobility
from flask_mobility.decorators import mobile_template
import time
from engineio.async_drivers import gevent

from utils import threaded
from forms import GoLiveForm

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = '$hor!K#y'
socketio = SocketIO(app)
Mobility(app)

SceneController = None

@threaded
def loop():
    time.sleep(3)
    try:
        if __name__ != "__main__":        
            print("starting webserver")
            global SceneController
            SceneController = App.get_running_app().root.ids.MainScreen.ids.ScenePanel
            while True:
                socketio.emit("update", {"data":"None", 
                    "states":[
                        SceneController.current_scene=="camera",
                        SceneController.current_scene=="center",
                        SceneController.ids.SCQAutomatic.ids.cb.active,
                        SceneController.ids.TimerLabel.text
                    ]})
                time.sleep(.2)
        else:
            print("starting test webserver")
            while True:
                socketio.emit("update", {"data":"None",
                    "states":[
                        True,
                        False,
                        True,
                        "Test"
                    ]})
    except KeyboardInterrupt:
        return

@app.route("/")
@app.route("/index")
@mobile_template("{mobile_}index.html")
def index(template):
    return flask.render_template(template)

@app.route("/go_live", methods=['GET', 'POST'])
def go_live(*args):
    print(args)
    form = GoLiveForm()
    if form.validate_on_submit():
        print("data submitted")
        print(form.stream_title.data)
        return flask.redirect(flask.url_for('index'))
    return flask.render_template("go_live.html", form=form)

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

if __name__ == "__main__":
    loop()
    socketio.run(app, "0.0.0.0", debug=True)