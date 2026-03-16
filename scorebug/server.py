import os
import sys
import uuid
from flask import Flask, request, send_from_directory, jsonify
from werkzeug.utils import secure_filename

# Determine base directory for PyInstaller compatibility
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=os.path.join(BASE_DIR, "static"))

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')

# Ensure upload directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Global state to store the current score
current_score = {
    "awayName": "AWAY",
    "homeName": "HOME",
    "awayScore": 0,
    "homeScore": 0,
    "awaySets": 0,
    "homeSets": 0,
    "possession": "none",
    "awayLogo": "/static/away_logo.jpg"
}

def allowed_file(filename):
    """
    Check if the file has an allowed extension.
    
    Args:
        filename (str): The name of the file to check.
        
    Returns:
        bool: True if the file has an allowed extension, False otherwise.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    """
    Route for scorebug overlay (used in OBS).
    Serves the main scoreboard HTML file.
    """
    return send_from_directory("static", "scorebug.html")

@app.route("/control_panel")
def control_panel():
    """
    Route for control panel.
    Serves the control panel HTML file.
    """
    return app.send_static_file("control_panel.html")

@app.route("/update", methods=["POST"])
def update():
    """
    Endpoint to update score from control panel.
    Handles form data submission and file uploads for logos.
    """
    global current_score
    form_data = request.form

    # Default to the existing logo or the one provided in the hidden text field
    new_logo_url = form_data.get("awayLogo", current_score["awayLogo"])

    # Handle File Upload if present
    if 'awayLogoFile' in request.files:
        file = request.files['awayLogoFile']
        if file and file.filename and allowed_file(file.filename):
            # Generate a unique secure filename
            extension = os.path.splitext(file.filename)[1]
            filename = secure_filename(f"away_logo_{uuid.uuid4().hex}{extension}")

            # Save the file
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                file.save(save_path)
                # Update the URL to point to the new file
                new_logo_url = f"/uploads/{filename}"
            except Exception as e:
                print(f"Error saving file: {e}")

    # Update global score data (use current values as fallbacks)
    current_score.update({
        "awayName": form_data.get("awayName", current_score["awayName"]),
        "homeName": form_data.get("homeName", current_score["homeName"]),
        "awayScore": int(form_data.get("awayScore", current_score["awayScore"])),
        "homeScore": int(form_data.get("homeScore", current_score["homeScore"])),
        "awaySets": int(form_data.get("awaySets", current_score["awaySets"])),
        "homeSets": int(form_data.get("homeSets", current_score["homeSets"])),
        "possession": form_data.get("possession", current_score["possession"]),
        "awayLogo": new_logo_url,
    })

    # Return status and new logo URL
    return jsonify({"status": "ok", "newLogoUrl": new_logo_url})

@app.route("/current")
def current():
    """
    Endpoint to provide current score to overlay.
    Returns the current score as JSON.
    """
    return jsonify(current_score)

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    """
    Serve uploaded files from the UPLOAD_FOLDER.
    """
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)