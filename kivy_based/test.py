import flask
import flask_socketio
import keyboard

app = flask.Flask(__name__)
socket = flask_socketio.SocketIO(app)

@app.route("/")
def index():
    return flask.render_template("index.html")

keyboard.add_hotkey("a", lambda: print("hello"))

if __name__ == "__main__":
    socket.run(app, host="0.0.0.0")