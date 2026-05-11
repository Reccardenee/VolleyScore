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

def get_daily_log_file():
    """Returns the log file path for the current day."""
    today = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(LOG_FOLDER, f'match_report_{today}.csv')

LOG_FILE = get_daily_log_file()

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
    "currentSet": 1,
    "possession": "none",
    "awayLogo": "/static/away_logo.jpg",
    "homeLogo": "/static/home_logo_placeholder.jpg",
    "homePlayers": ["", "", "", "", "", ""],
    "awayPlayers": ["", "", "", "", "", ""],
    "previousSetScores": [],
    "awayColorPrimary": "#FF0000",
    "awayColorSecondary": "#FFAAAA",
    "homeColorPrimary": "#0000FF",
    "homeColorSecondary": "#AAAAFF",
    "matchTitle": "Volleyball Match",
    "pin": "",
    # Match Timer
    "timerStarted": False,
    "timerPaused": False,
    "timerStartTimestamp": None,
    "timerPausedTimestamp": None,
    "accumulatedTime": 0,
    # Timeouts (resets to 2 each new set)
    "homeTimeouts": 2,
    "awayTimeouts": 2,
    # Score History (last 5 points)
    "scoreHistory": [],
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

    # Get the daily log file path (in case day changed while server was running)
    current_log_file = get_daily_log_file()
    file_exists = os.path.exists(current_log_file)
    with open(current_log_file, 'a', newline='') as csvfile:
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
    Route for control panel (unified).
    """
    return app.send_static_file("control_panel_unified.html")

@app.route("/control_panel_unified")
def control_panel_unified():
    """
    Route for unified control panel.
    """
    return app.send_static_file("control_panel_unified.html")

@app.route("/match_timer")
def match_timer():
    """
    Route for match timer overlay.
    """
    return app.send_static_file("match_timer.html")

@app.route("/timeouts")
def timeouts_overlay():
    """
    Route for timeouts overlay.
    """
    return app.send_static_file("timeouts.html")

@app.route("/score_history")
def score_history():
    """
    Route for score history overlay.
    """
    return app.send_static_file("score_history.html")

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

    # PIN verification - reject updates if PIN doesn't match (unless setting/changing PIN)
    submitted_pin = form_data.get("pin", "")
    is_setting_pin = form_data.get("isSettingPin", "false") == "true"
    current_pin = current_score.get("pin", "")

    # Allow if: no PIN set, PIN matches, or setting/changing PIN with correct current PIN
    if current_pin and submitted_pin != current_pin and not is_setting_pin:
        return jsonify({"status": "error", "message": "Invalid PIN"}), 403

    # If setting/changing PIN, validate current PIN first
    if is_setting_pin:
        new_pin = form_data.get("newPin", "")
        confirm_pin = form_data.get("confirmPin", "")

        if current_pin and submitted_pin != current_pin:
            return jsonify({"status": "error", "message": "Current PIN is incorrect"}), 403

        if new_pin != confirm_pin:
            return jsonify({"status": "error", "message": "New PINs do not match"}), 403

        if len(new_pin) != 4 or not new_pin.isdigit():
            return jsonify({"status": "error", "message": "PIN must be exactly 4 digits"}), 403

        current_score["pin"] = new_pin

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
        "matchTitle": get_val("matchTitle", current_score["matchTitle"]),
    })

    # Check if set is complete (25 points, or 15 for tie-break set 5)
    set_complete = False
    winning_score = 15 if current_score["currentSet"] == 5 else 25
    
    # Only check for set completion if scores are > 0 (prevents double-processing after reset)
    if current_score["homeScore"] > 0 and current_score["awayScore"] > 0:
        if current_score["homeScore"] >= winning_score or current_score["awayScore"] >= winning_score:
            # Check for minimum 2 point difference
            if abs(current_score["homeScore"] - current_score["awayScore"]) >= 2:
                set_complete = True
    
    if set_complete:
        # Store the old sets values BEFORE resetting (to detect if client already counted this set)
        old_home_sets = old_current_score.get("homeSets", 0)
        old_away_sets = old_current_score.get("awaySets", 0)
        
        # Record the completed set score
        current_score["previousSetScores"].append({
            "home": current_score["homeScore"],
            "away": current_score["awayScore"]
        })
        
        # Only increment sets if client hasn't already done it
        # (compare with old sets, not current, because current might have client's manual value)
        if current_score["homeScore"] > current_score["awayScore"]:
            if current_score["homeSets"] == old_home_sets:
                current_score["homeSets"] += 1
        else:
            if current_score["awaySets"] == old_away_sets:
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

        # Start timer on first point scored (with 60 second grace period)
        if not current_score["timerStarted"]:
            if current_score["homeScore"] > 0 or current_score["awayScore"] > 0:
                current_score["timerStarted"] = True
                current_score["timerStartTimestamp"] = datetime.now().timestamp()
                current_score["accumulatedTime"] = 60  # 60 second grace period

        # Add to score history
        if current_score["homeScore"] > 0 or current_score["awayScore"] > 0:
            current_score["scoreHistory"].append({
                "homeScore": current_score["homeScore"],
                "awayScore": current_score["awayScore"]
            })
            # Keep only last 5
            if len(current_score["scoreHistory"]) > 5:
                current_score["scoreHistory"] = current_score["scoreHistory"][-5:]

    # Reset timeouts when currentSet changes
    if current_score["currentSet"] != old_current_score.get("currentSet", 1):
        current_score["homeTimeouts"] = 2
        current_score["awayTimeouts"] = 2
    
    save_config(current_score)
    socketio.emit('score_update', current_score)

    return jsonify({
        "status": "ok",
        "newLogoUrl": new_logo_url,
        "newHomeLogoUrl": new_home_logo_url,
        "pinSet": bool(current_score.get("pin")),
        "isSettingPin": form_data.get("isSettingPin", "false") == "true"
    })

@app.route("/current")
def current():
    """
    Endpoint to provide current score to overlay (fallback/initial load).
    Returns the live score.
    """
    return jsonify(current_score)

@app.route("/timer_control", methods=["POST"])
def timer_control():
    """
    Endpoint to control the match timer (pause, resume, reset).
    """
    global current_score
    action = request.form.get("action", "")

    if action == "pause":
        current_score["timerPaused"] = True
        current_score["timerPausedTimestamp"] = datetime.now().timestamp()
    elif action == "resume":
        if current_score["timerPaused"] and current_score["timerPausedTimestamp"]:
            # Add elapsed time before pause to accumulated
            current_score["accumulatedTime"] += (datetime.now().timestamp() - current_score["timerPausedTimestamp"])
        current_score["timerPaused"] = False
        current_score["timerPausedTimestamp"] = None
    elif action == "reset":
        current_score["timerStarted"] = False
        current_score["timerPaused"] = False
        current_score["timerStartTimestamp"] = None
        current_score["timerPausedTimestamp"] = None
        current_score["accumulatedTime"] = 0
        current_score["scoreHistory"] = []

    save_config(current_score)
    socketio.emit('score_update', current_score)

    return jsonify({"status": "ok"})

@app.route("/timeout_control", methods=["POST"])
def timeout_control():
    """
    Endpoint to update timeout counts.
    """
    global current_score
    team = request.form.get("team", "")
    change = int(request.form.get("change", 0))

    if team == "home":
        current_score["homeTimeouts"] = max(0, min(2, current_score["homeTimeouts"] + change))
    elif team == "away":
        current_score["awayTimeouts"] = max(0, min(2, current_score["awayTimeouts"] + change))

    save_config(current_score)
    socketio.emit('score_update', current_score)

    return jsonify({"status": "ok"})

@app.route("/export_config")
def export_config():
    """
    Export current configuration as JSON file download.
    """
    response = Response(
        json.dumps(current_score, indent=4),
        mimetype='application/json',
        headers={'Content-Disposition': 'attachment;filename=config.json'}
    )
    return response

@app.route("/import_config", methods=["POST"])
def import_config():
    """
    Import configuration from JSON file upload.
    """
    global current_score

    if 'configFile' not in request.files:
        return jsonify({"status": "error", "message": "No file uploaded"}), 400

    file = request.files['configFile']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No file selected"}), 400

    try:
        config_data = json.load(file)

        # Validate required fields exist
        required_fields = ['homeName', 'awayName']
        for field in required_fields:
            if field not in config_data:
                return jsonify({"status": "error", "message": f"Invalid config file: missing {field}"}), 400

        # Update current score with imported config
        current_score = config_data
        save_config(current_score)
        socketio.emit('score_update', current_score)

        return jsonify({"status": "ok", "message": "Config imported successfully"})
    except json.JSONDecodeError:
        return jsonify({"status": "error", "message": "Invalid JSON file"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/reset_config", methods=["POST"])
def reset_config():
    """
    Reset configuration to defaults.
    """
    global current_score

    current_score = DEFAULT_SCORE.copy()
    save_config(current_score)
    socketio.emit('score_update', current_score)

    return jsonify({"status": "ok", "message": "Config reset to defaults"})

@app.route("/export_match_json")
def export_match_json():
    """
    Export match data as JSON file.
    """
    # Calculate match duration
    match_duration = ""
    if current_score.get("timerStarted"):
        if current_score.get("timerPaused") and current_score.get("timerPausedTimestamp"):
            total_seconds = current_score.get("accumulatedTime", 0) + \
                (current_score["timerPausedTimestamp"] - current_score.get("timerStartTimestamp", 0))
        elif current_score.get("timerStartTimestamp"):
            total_seconds = current_score.get("accumulatedTime", 0) + \
                (datetime.now().timestamp() - current_score.get("timerStartTimestamp", 0))
        else:
            total_seconds = current_score.get("accumulatedTime", 0)

        mins = int(total_seconds // 60)
        secs = int(total_seconds % 60)
        match_duration = f"{mins:02d}:{secs:02d}"

    export_data = {
        "matchTitle": current_score.get("matchTitle", "Volleyball Match"),
        "homeTeam": current_score.get("homeName", "Home"),
        "awayTeam": current_score.get("awayName", "Away"),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "homeColorPrimary": current_score.get("homeColorPrimary", "#0000FF"),
        "awayColorPrimary": current_score.get("awayColorPrimary", "#FF0000"),
        "previousSetScores": current_score.get("previousSetScores", []),
        "scoreHistory": current_score.get("scoreHistory", []),
        "finalScore": {
            "homeSets": current_score.get("homeSets", 0),
            "awaySets": current_score.get("awaySets", 0),
            "homePoints": current_score.get("homeScore", 0),
            "awayPoints": current_score.get("awayScore", 0)
        },
        "homeTimeoutsUsed": 2 - current_score.get("homeTimeouts", 2),
        "awayTimeoutsUsed": 2 - current_score.get("awayTimeouts", 2),
        "matchDuration": match_duration
    }

    response = Response(
        json.dumps(export_data, indent=4),
        mimetype='application/json',
        headers={'Content-Disposition': 'attachment;filename=match_export.json'}
    )
    return response

@app.route("/export_match_csv")
def export_match_csv():
    """
    Export match data as CSV file.
    """
    history = current_score.get("scoreHistory", [])

    csv_lines = ["Point,Home Score,Away Score,Scoring Team"]

    last_home = 0
    last_away = 0
    point_num = 1

    for entry in history:
        home_scored = entry.get("homeScore", 0) > last_home
        scoring_team = current_score.get("homeName", "Home") if home_scored else current_score.get("awayName", "Away")

        csv_lines.append(f"{point_num},{entry.get('homeScore', 0)},{entry.get('awayScore', 0)},{scoring_team}")

        last_home = entry.get("homeScore", 0)
        last_away = entry.get("awayScore", 0)
        point_num += 1

    csv_content = "\n".join(csv_lines)

    response = Response(
        csv_content,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=match_export.csv'}
    )
    return response

@app.route("/export_match")
def export_match():
    """
    Route for match export page.
    """
    return app.send_static_file("export_match.html")

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