
import flask
from flask_mobility import Mobility
from flask_socketio import SocketIO

from Classes.Forms import SetupStreamForm, GoLiveForm
from Classes.MasterController import MasterController

def route(app:flask.Flask, socketio:SocketIO, MasterApp:MasterController):
    
    @app.route("/")
    def send_to_index():
        if MasterApp.States.stream_is_setup or MasterApp.States.stream_running:
            return flask.redirect(flask.url_for("index"))
        else:
            return flask.redirect(flask.url_for('setup_stream'))


    @app.route("/index", methods=["GET", "POST"])
    def index():
        return flask.render_template("index.html", state=MasterApp.States.stream_running)


    @app.route("/setup_stream", methods=['GET', 'POST'])
    def setup_stream():
        form = SetupStreamForm()
        if form.validate_on_submit():
            MasterApp.States.stream_title = form.stream_title.data
            MasterApp.setup_stream()
            return flask.redirect(flask.url_for('index'))
        return flask.render_template("setup_stream.html", form=form)


    @app.route("/go_live", methods=["GET", "POST"])
    def go_live():
        form = GoLiveForm()
        if form.validate_on_submit():
            answer = form.are_you_sure.data
            if answer == "yes":
                MasterApp.go_live()
            return flask.redirect(flask.url_for('index'))
        else:
            state = MasterApp.States.stream_running
            return flask.render_template("go_live.html", form=form, state=state)


    @socketio.on("scene_camera")
    def on_scene_camera(event=None):
        MasterApp.handle_state_change("camera")

    @socketio.on("message")
    def on_socket_message(event=None):
        print("Ring Ring! You have a message:\n")
        print(event)


    @socketio.on("scene_screen")
    def on_scene_screen(event=None):
        MasterApp.handle_state_change("screen")


    @socketio.on("automatic_change")
    def on_auto_change(event=None):
        MasterApp.handle_state_change("auto_lock")


    @socketio.on("auto_change_to_camera")
    def auto_change_to_camera(event=None):
        MasterApp.handle_state_change("auto_change_to_camera")

    @socketio.on("slide_next")
    def on_slide_next(event=None):
        MasterApp.handle_state_change("clicker_next")


    @socketio.on("slide_prev")
    def on_slide_prev(event=None):
        MasterApp.handle_state_change("clicker_prev")


    @socketio.on("volume")
    def toggle_volume(event=None):
        MasterApp.auto_contro.toggle_sound()

    @socketio.on("muted")
    def toggle_muted(event=None):
        MasterApp.handle_state_change("muted")

    @socketio.on("camera_augmented_toggle")
    def on_toggle_screen(event=None):
        MasterApp.handle_state_change("toggle_camera_scene_augmented")

    @socketio.on("special_scene")
    def on_special_scene(event):
        MasterApp.handle_state_change("scene_event", event["data"])

    @socketio.on("change_timer_event")
    def on_change_timer_event(event):
        MasterApp.handle_state_change("timer_event", event["data"])

    @socketio.on("timer_length")
    def on_change_timer_length(event):
        MasterApp.handle_state_change("timer_length", event["data"])

    @socketio.on("new_connection")
    def refresh_new_page(event=None):
        MasterApp.update_page()
