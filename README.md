# VolleyScore

A lightweight, web-based scoreboard overlay designed for Volleyball broadcasts using OBS Studio. VolleyScore features a control panel for updating scores, sets, and service indicators in real-time, powered by a local Python Flask server.

## Features

- **Web-Based Control Panel**: Control the score from the host computer or any device on the same local network (e.g., a tablet or phone).
- **Real-Time Overlay**: Instant updates to the OBS Browser Source.
- **Automatic Game Logic**:
  - Automatically increments the Set count when a team reaches 25 points.
  - Resets points automatically after a set win.
- **Service Indicator**: Visual indicator for which team has possession/service.
- **Customizable Away Logo**: Upload a custom logo for the Away team directly from the control panel.
- **Persistent State**: Scores are saved locally in the browser, so you don't lose progress if you accidentally refresh the control panel.
- **Single File Executable**: Can be compiled into a single `.exe` file for easy distribution.

## Quick Start (Using the EXE)

This project is set up with GitHub Actions to automatically build a Windows executable.

1. Go to the **Actions** tab in this repository.
2. Click on the latest successful **Build EXE** workflow run.
3. Scroll down to the **Artifacts** section and download **VolleyScore-Scorebug**.
4. Extract the zip file and run `server.exe`.
5. Allow the application through the firewall if prompted (needed to serve the web pages).

## Running from Source

If you prefer to run the Python code directly:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/VolleyScore.git
   cd VolleyScore
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Server**:
   ```bash
   python scorebug/server.py
   ```

## Usage

Once the server is running (you should see `Running on http://0.0.0.0:8000` in the console):

### 1. Open the Control Panel
Open your web browser and navigate to:

You can access the control panel from the computer running the server, or from any other device (like a phone or tablet) on the same network.

**On the host computer:**
Open your web browser and navigate to:
`http://localhost:8000/control_panel`

**On another device (e.g., a tablet):**
1.  Find the local IP address of the computer running the server. On Windows, you can do this by opening Command Prompt (`cmd`) and typing `ipconfig`. Look for the "IPv4 Address" (e.g., `192.168.1.15`).
2.  On your other device, open a web browser and navigate to `http://<YOUR_IP_ADDRESS>:8000/control_panel`, replacing `<YOUR_IP_ADDRESS>` with the address you found.

> **Note:** When you first run the server, Windows Firewall might ask for permission. You must **allow access** for other devices on your network to be able to connect.

Use this interface to change team names, update scores, manage sets, and upload logos.

### 2. Add to OBS Studio
1. Open OBS Studio.
2. Under **Sources**, click the `+` icon and select **Browser**.
3. Name it "Volleyball Scoreboard".
4. Configure the settings:
   - **URL**: `http://localhost:8000`
   - **Width**: `1050` (The board is 1000px wide, extra space prevents scrollbars)
   - **Height**: `400`
   - **Custom CSS**: (Leave empty)
5. Click **OK**.

### 3. Uploading Logos
In the Control Panel, you can upload a PNG or JPG file for the Away team. The Home team logo is currently set statically in the CSS (defaulting to `scalia.jpg`), but can be modified in `scorebug/static/scorebug.html` or replaced in the static folder.

## Project Structure

```
.
├── .github/workflows/build.yml   # GitHub Actions workflow for building the EXE
├── scorebug/
│   ├── static/
│   │   ├── scorebug.html         # The OBS overlay
│   │   └── control_panel.html    # The control panel
│   └── server.py                 # The Flask server
├── .gitignore
├── README.md
└── requirements.txt
```

## Development

- **Backend**: Python (Flask)
- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **Build Tool**: PyInstaller

## Contributing

Contributions are welcome! Please feel free to submit a pull request. See [CONTRIBUTING.md](CONTRIBUTING.md) for more information.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
