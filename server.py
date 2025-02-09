from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO
from geopy.distance import geodesic
import os

app = Flask(__name__, template_folder="templates", static_folder="static")
socketio = SocketIO(app, cors_allowed_origins="*")

last_position = None
total_distance = 0
step_length = 0.78  # Average step length in meters
step_count = 0

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@socketio.on("update_position")
def handle_position(data):
    global last_position, total_distance, step_count

    lat, lon = data["latitude"], data["longitude"]
    current_position = (lat, lon)

    if last_position:
        distance = geodesic(last_position, current_position).meters
        total_distance += distance
        step_count = int(total_distance / step_length)
    
    last_position = current_position

    socketio.emit("update_stats", {"distance": round(total_distance, 2), "steps": step_count})

@socketio.on("heartbeat")
def handle_heartbeat(data):
    intensity = data["intensity"]
    speed = max(0.5, min(2, intensity / 10))
    socketio.emit("update_heartbeat", {"speed": speed})

if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)
