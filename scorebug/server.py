import os
import sys
import uuid
import json
from flask import Flask, request, send_from_directory, jsonify
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename

# Determine base directory for PyInstaller compatibility
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
    EXE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    EXE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=os.path.join(BASE_DIR, "static"))
socketio = SocketIO(app, cors_allowed_origins="*")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
UPLOAD_FOLDER = os.path.join(EXE_DIR, 'uploads')
CONFIG_FILE = os.path.join(EXE_DIR, 'config.json')

# Ensure upload directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Global state to store the current score
DEFAULT_SCORE = {
    "awayName": "Away",
    "homeName": "Home",
    "awayScore": 0,
    "homeScore": 0,
    "awaySets": 0,
    "homeSets": 0,
    "possession": "none",
    "awayLogo": "/static/away_logo.jpg",
    "homeLogo": "/static/home_logo_placeholder.jpg",
    "homePlayers": ["", "", "", "", "", ""],
    "awayPlayers": ["", "", "", "", "", ""]
}

def load_config():
    """Load configuration from file or return default."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
    return DEFAULT_SCORE.copy()

def save_config(config):
    """Save configuration to file."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}")

current_score = load_config()

def allowed_file(filename):
    """
    Check if the file has an allowed extension.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    """
    Route for scorebug overlay (used in OBS).
    """
    return send_from_directory("static", "scorebug.html")

@app.route("/control_panel")
def control_panel():
    """
    Route for control panel.
    """
    return app.send_static_file("control_panel.html")

@app.route("/dual_formation")
def dual_formation():
    """
    Route for side-by-side team formations.
    """
    return send_from_directory("static", "dual_formation.html")

@app.route("/update", methods=["POST"])
def update():
    """
    Endpoint to update score from control panel.
    """
    global current_score
    form_data = request.form

    new_logo_url = form_data.get("awayLogo", current_score["awayLogo"])
    new_home_logo_url = form_data.get("homeLogo", current_score["homeLogo"])

    if 'awayLogoFile' in request.files:
        file = request.files['awayLogoFile']
        if file and file.filename and allowed_file(file.filename):
            extension = os.path.splitext(file.filename)[1]
            filename = secure_filename(f"away_logo_{uuid.uuid4().hex}{extension}")
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                file.save(save_path)
                new_logo_url = f"/uploads/{filename}"
            except Exception as e:
                print(f"Error saving file: {e}")

    if 'homeLogoFile' in request.files:
        file = request.files['homeLogoFile']
        if file and file.filename and allowed_file(file.filename):
            extension = os.path.splitext(file.filename)[1]
            filename = secure_filename(f"home_logo_{uuid.uuid4().hex}{extension}")
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                file.save(save_path)
                new_home_logo_url = f"/uploads/{filename}"
            except Exception as e:
                print(f"Error saving file: {e}")

    home_players = [form_data.get(f"homeP{i}", "") for i in range(1, 7)]
    away_players = [form_data.get(f"awayP{i}", "") for i in range(1, 7)]

    current_score.update({
        "awayName": form_data.get("awayName", current_score["awayName"]),
        "homeName": form_data.get("homeName", current_score["homeName"]),
        "awayScore": int(form_data.get("awayScore", current_score["awayScore"])),
        "homeScore": int(form_data.get("homeScore", current_score["homeScore"])),
        "awaySets": int(form_data.get("awaySets", current_score["awaySets"])),
        "homeSets": int(form_data.get("homeSets", current_score["homeSets"])),
        "possession": form_data.get("possession", current_score["possession"]),
        "awayLogo": new_logo_url,
        "homeLogo": new_home_logo_url,
        "homePlayers": home_players,
        "awayPlayers": away_players,
    })

    save_config(current_score)
    
    # Emit update to all connected clients
    socketio.emit('score_update', current_score)

    return jsonify({"status": "ok", "newLogoUrl": new_logo_url, "newHomeLogoUrl": new_home_logo_url})

@app.route("/current")
def current():
    """
    Endpoint to provide current score to overlay (fallback/initial load).
    """
    return jsonify(current_score)

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    """
    Serve uploaded files from the UPLOAD_FOLDER.
    """
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@socketio.on('connect')
def handle_connect():
    """Send current state to client upon connection."""
    emit('score_update', current_score)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8000, allow_unsafe_werkzeug=True)