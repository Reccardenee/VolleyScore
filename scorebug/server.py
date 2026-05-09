import gevent.monkey
gevent.monkey.patch_all()

import os
import sys
import signal
import uuid
import json
import csv
from datetime import datetime
from flask import Flask, request, send_from_directory, jsonify, Response
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename
import qrcode
import socket
from io import BytesIO

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
LOG_FOLDER = os.path.join(EXE_DIR, 'logs')
LOG_FILE = os.path.join(LOG_FOLDER, 'match_report.csv')

# Ensure upload and log directories exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Global state to store the current score
DEFAULT_SCORE = {
    "awayName": "Away",
    "homeName": "Home",
    "awayScore": 0,
    "homeScore": 0,
    "awaySets": 0,
    "homeSets": 0,
    "currentSet": 1,  # Track which set is currently being played
    "possession": "none",
    "awayLogo": "/static/away_logo.jpg",
    "homeLogo": "/static/home_logo_placeholder.jpg",
    "homePlayers": ["", "", "", "", "", ""],
    "awayPlayers": ["", "", "", "", "", ""],
    "previousSetScores": [], # Store previous set scores
    "awayColorPrimary": "#FF0000",
    "awayColorSecondary": "#FFAAAA",
    "homeColorPrimary": "#0000FF",
    "homeColorSecondary": "#AAAAFF",
}

def load_config():
    """Load configuration from file or return default."""
    config = DEFAULT_SCORE.copy()
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                loaded_config = json.load(f)
                config.update(loaded_config) # Merge loaded config with defaults
        except Exception as e:
            print(f"Error loading config: {e}")
    return config

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

def log_score_event(old_score_state, new_score_state):
    """
    Logs score changes to a CSV file.
    """
    timestamp = datetime.now().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "homeName": new_score_state["homeName"],
        "awayName": new_score_state["awayName"],
        "oldHomeScore": old_score_state["homeScore"],
        "newHomeScore": new_score_state["homeScore"],
        "oldAwayScore": old_score_state["awayScore"],
        "newAwayScore": new_score_state["awayScore"],
        "oldHomeSets": old_score_state["homeSets"],
        "newHomeSets": new_score_state["homeSets"],
        "oldAwaySets": old_score_state["awaySets"],
        "newAwaySets": new_score_state["awaySets"],
        "possession": new_score_state["possession"],
        "event": "score_update" # Can be expanded for other events
    }

    # Determine which team scored, if any
    if new_score_state["homeScore"] > old_score_state["homeScore"]:
        log_entry["scoredTeam"] = new_score_state["homeName"]
    elif new_score_state["awayScore"] > old_score_state["awayScore"]:
        log_entry["scoredTeam"] = new_score_state["awayName"]
    else:
        log_entry["scoredTeam"] = "None"

    file_exists = os.path.exists(LOG_FILE)
    with open(LOG_FILE, 'a', newline='') as csvfile:
        fieldnames = log_entry.keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader() # Write header only if file is new
        writer.writerow(log_entry)
    print(f"Logged score event: {log_entry}")

def get_local_ip():
    """
    Get the local IP address of the machine.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80)) # Connect to a public DNS server
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except Exception:
        return "127.0.0.1" # Fallback to localhost


@app.route("/")
def index():
    """
    Route for scorebug overlay (used in OBS).
    """
    return app.send_static_file("scorebug.html")

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
    return app.send_static_file("dual_formation.html")

@app.route("/home_formation")
def home_formation():
    """
    Route for home team formation only.
    """
    return app.send_static_file("home_formation.html")

@app.route("/away_formation")
def away_formation():
    """
    Route for away team formation only.
    """
    return app.send_static_file("away_formation.html")

@app.route("/scorebug_sets")
def scorebug_sets():
    """
    Route for scorebug with all sets always visible.
    """
    return app.send_static_file("scorebug_sets.html")

@app.route("/formations_control")
def formations_control():
    """
    Route for formations control panel.
    """
    return app.send_static_file("formations_control.html")

@app.route("/team_settings_control")
def team_settings_control():
    """
    Route for team settings control panel.
    """
    return app.send_static_file("team_settings_control.html")

@app.route("/qrcode_image")
def qrcode_image():
    """
    Generates and serves a QR code for the control panel URL.
    """
    local_ip = get_local_ip()
    control_panel_url = f"http://{local_ip}:8000/control_panel"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(control_panel_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    
    return Response(buffer.getvalue(), mimetype="image/png")


@app.route("/update", methods=["POST"])
def update():
    """
    Endpoint to update score from control panel.
    """
    global current_score
    form_data = request.form

    old_current_score = current_score.copy()

    def get_val(key, current_val):
        val = form_data.get(key)
        # For colors, ensure a default if empty string is passed
        if key.endswith("ColorPrimary") or key.endswith("ColorSecondary"):
            return val if val and val.strip() != "" else current_val
        return val if val and val.strip() != "" else current_val

    new_logo_url = get_val("awayLogo", current_score["awayLogo"])
    new_home_logo_url = get_val("homeLogo", current_score["homeLogo"])

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

    home_players = [get_val(f"homeP{i}", current_score["homePlayers"][i-1]) for i in range(1, 7)]
    away_players = [get_val(f"awayP{i}", current_score["awayPlayers"][i-1]) for i in range(1, 7)]

    # Handle previous set scores (expecting a JSON string from the frontend)
    previous_set_scores_str = form_data.get("previousSetScores")
    if previous_set_scores_str:
        try:
            previous_set_scores = json.loads(previous_set_scores_str)
        except json.JSONDecodeError:
            previous_set_scores = current_score["previousSetScores"] # Fallback to current if invalid
    else:
        previous_set_scores = current_score["previousSetScores"]

    current_score.update({
        "awayName": get_val("awayName", current_score["awayName"]),
        "homeName": get_val("homeName", current_score["homeName"]),
        "awayScore": int(get_val("awayScore", current_score["awayScore"])),
        "homeScore": int(get_val("homeScore", current_score["homeScore"])),
        "awaySets": int(get_val("awaySets", current_score["awaySets"])),
        "homeSets": int(get_val("homeSets", current_score["homeSets"])),
        "possession": get_val("possession", current_score["possession"]),
        "awayLogo": new_logo_url,
        "homeLogo": new_home_logo_url,
        "homePlayers": home_players,
        "awayPlayers": away_players,
        "previousSetScores": previous_set_scores,
        "awayColorPrimary": get_val("awayColorPrimary", current_score["awayColorPrimary"]),
        "awayColorSecondary": get_val("awayColorSecondary", current_score["awayColorSecondary"]),
        "homeColorPrimary": get_val("homeColorPrimary", current_score["homeColorPrimary"]),
        "homeColorSecondary": get_val("homeColorSecondary", current_score["homeColorSecondary"]),
    })

    # Check if set is complete (25 points, or 15 for tie-break set 5)
    set_complete = False
    winning_score = 15 if current_score["currentSet"] == 5 else 25
    
    if current_score["homeScore"] >= winning_score or current_score["awayScore"] >= winning_score:
        # Check for minimum 2 point difference
        if abs(current_score["homeScore"] - current_score["awayScore"]) >= 2:
            set_complete = True
    
    if set_complete:
        # Record the completed set score
        current_score["previousSetScores"].append({
            "home": current_score["homeScore"],
            "away": current_score["awayScore"]
        })
        
        # Increment sets won
        if current_score["homeScore"] > current_score["awayScore"]:
            current_score["homeSets"] += 1
        else:
            current_score["awaySets"] += 1
        
        # Move to next set (max 5 sets)
        if current_score["currentSet"] < 5:
            current_score["currentSet"] += 1
        
        # Reset scores for new set
        current_score["homeScore"] = 0
        current_score["awayScore"] = 0

    # Log score change only if score actually changed
    if (current_score["homeScore"] != old_current_score["homeScore"] or
        current_score["awayScore"] != old_current_score["awayScore"] or
        current_score["homeSets"] != old_current_score["homeSets"] or
        current_score["awaySets"] != old_current_score["awaySets"]):
        log_score_event(old_current_score, current_score)
    
    save_config(current_score)
    socketio.emit('score_update', current_score)

    return jsonify({"status": "ok", "newLogoUrl": new_logo_url, "newHomeLogoUrl": new_home_logo_url})

@app.route("/current")
def current():
    """
    Endpoint to provide current score to overlay (fallback/initial load).
    Returns the live score.
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
    def handle_exit(sig, frame):
        print("\nShutting down VolleyScore Server...")
        os._exit(0)

    signal.signal(signal.SIGINT, handle_exit)

    print("VolleyScore Server starting...")
    print("-" * 40)
    print(f"Control Panel: http://{get_local_ip()}:8000/control_panel")
    print("-" * 40)

    socketio.run(app, host="0.0.0.0", port=8000, log_output=False)