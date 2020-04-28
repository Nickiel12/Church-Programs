import flask
from flask_socketio import SocketIO
from flask_mobility import Mobility
from flask_mobility.decorators import mobile_template
import time
import eventlet

from utils import threaded
from forms import SetupStreamForm, GoLiveForm

if __name__ != "__main__":
    from kivy.app import App

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = '$hor!K#y'
socketio = SocketIO(app)
Mobility(app)

SceneController = None
master_app = None


@threaded
def loop():
    time.sleep(3)
    try:
        if __name__ != "__main__":        
            print("starting webserver")
            global SceneController
            global master_app
            master_app = App.get_running_app()
            SceneController = master_app.root.ids.MainScreen.ids.ScenePanel
            while True:
                socketio.emit("update", {"data": "None", 
                              "states": [
                                SceneController.current_scene == "camera",
                                SceneController.current_scene == "center",
                                SceneController.ids.SCQAutomatic.ids.cb.active,
                                SceneController.ids.TimerLabel.text,
                                master_app.auto_contro.get_sound_state(),
                                SceneController.is_center_augmented
                                ]})
                time.sleep(.2)
        else:
            print("starting test webserver")
            while True:
                socketio.emit("update", {"data": "None",
                              "states": [
                                    True,
                                    False,
                                    True,
                                    "Test",
                                    True, 
                                    False
                                ]})
                time.sleep(1)
    except KeyboardInterrupt:
        return


@app.route("/")
def send_to_index():
    global SceneController
    if __name__ != "__main__":
        if master_app.stream_setup or master_app.stream_running:
            return flask.redirect(flask.url_for("index"))
        else:
            return flask.redirect(flask.url_for('setup_stream'))
    else:
        return flask.redirect(flask.url_for("index"))


@app.route("/index", methods=["GET", "POST"])
def index():
    if __name__ == "__main__":
        return flask.render_template("index.html", state=True)
    else:
        state = master_app.stream_running
        return flask.render_template("index.html", state=state)


@app.route("/setup_stream", methods=['GET', 'POST'])
def setup_stream():
    form = SetupStreamForm()
    if form.validate_on_submit():
        if __name__ != "__main__":    
            startup = master_app.root.ids.StartupScreenId.ids.StartupControl
            startup.ids.StreamTitleInput.text = form.stream_title.data
            startup.on_submit(stream_name=form.stream_title.data)
        return flask.redirect(flask.url_for('index'))
    return flask.render_template("setup_stream.html", form=form)


@app.route("/go_live", methods=["GET", "POST"])
def go_live():
    form = GoLiveForm()
    if form.validate_on_submit():
        answer = form.are_you_sure.data
        if answer == "yes":
            if __name__ != "__main__":
                master_app.root.ids.MainScreen.ids.StreamPanel.fake_press_go_live()
        return flask.redirect(flask.url_for('index'))
    if __name__ == "__main__":
        return flask.render_template("go_live.html", form=form, state=True)
    else:
        state = master_app.stream_running
        return flask.render_template("go_live.html", form=form, state=state)


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


@socketio.on("volume")
def toggle_volume(event):
    global master_app
    master_app.auto_contro.toggle_sound()


@socketio.on("center_toggle")
def on_toggle_center(event):
    SceneController.on_hotkey("toggle_center_augmented")


def start_web_server():
    loop()
    socketio.run(app, "0.0.0.0")

if __name__ == "__main__":
    loop()
    socketio.run(app, "0.0.0.0", debug=True)
