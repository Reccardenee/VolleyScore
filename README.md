# VolleyScore

A lightweight, web-based scoreboard overlay designed for Volleyball broadcasts using OBS Studio. VolleyScore features a control panel for updating scores, sets, and service indicators in real-time, powered by a Flask-SocketIO server.

## Motivation
This tool was built for a local volleyball team to use during OBS-based livestreams, and as a way for me to learn and practice Flask, WebSockets (Socket.IO), simple frontend state management, and packaging with PyInstaller. It focuses on working, easy-to-use functionality rather than being a perfectly optimized or generalized solution.

## Features

- **Web-Based Control Panel**: Control the score from the host computer or any device on the same local network (e.g., a tablet or phone). Organized into Match, Teams, Match Stats and Settings tabs.
- **Instant Updates via WebSockets**: Real-time updates to the OBS Browser Source using Flask-SocketIO, providing low latency.
- **Multiple Overlay Views**:
  - **Main Scorebug** (`/` or `scorebug.html`): The primary scoreboard overlay showing current score and sets won.
  - **Sets Scorebug** (`scorebug_sets.html`): Displays all 5 sets with alternating orange/blue themes. Shows the live score in the current set column and completed set scores in their respective columns (including the completed 5th set, which stays visible after the match ends).
  - **Home Formation** (`home_formation.html`): Home team starting lineup view.
  - **Away Formation** (`away_formation.html`): Away team starting lineup view.
  - **Dual Formation** (`dual_formation.html`): Side-by-side view of both team starting lineups.
  - **Match Timer** (`match_timer.html`): Elapsed match time overlay with start/pause/resume/reset controls.
  - **Timeouts** (`timeouts.html`): Timeout indicator overlay (2 per team per set).
  - **Score History** (`score_history.html`): Last 5 points overlay.
- **Match Timer**: Manual start/pause/resume/reset via the Match Stats tab. Auto-starts when the first point is scored. Elapsed time is tracked by the server and the display ticks from a server-reported baseline, so pausing freezes the clock exactly (no jumps from clock skew).
- **Timeouts**: Track the 2 timeouts per team per set. Counts reset automatically when a new set starts.
- **Score History**: Every point is recorded server-side; the overlays show the last 5. Full point-by-point history is available in the CSV match export.
- **Match Export**: Export the full match (teams, sets, score history, timeouts, duration) as JSON or a point-by-point CSV.
- **Config Backup**: Export/import the full configuration (`config.json`) for backup or moving between machines.
- **PIN Protection**: Optionally protect the control panel with a 4-digit PIN (set/changed in the Settings tab). The PIN gates score updates as well as the timer and timeout controls.
- **Automatic Game Logic**:
  - Automatically increments the Set count when a team reaches 25 points (or 15 in the 5th set) with at least a 2-point difference.
  - Tracks which set is currently being played (`currentSet`).
  - Records completed set scores to `previousSetScores` for display in the sets scorebug.
  - Resets points automatically after a set win.
- **Custom Team Colors**: Configure primary and secondary colors for each team. These colors are used for the vertical bars next to team logos and in the formation header gradients.
- **Overlay Theme**: Change the shared color palette (background gradient, accent, border) of the main scorebug, sets, timer, timeouts and score history overlays from the Settings tab. The team formations keep their team colors.
- **Overlay Display**: Show or hide the sets, timer, timeouts and score history overlays from the Settings tab — they fade in/out with a subtle rise. The standard scorebug is always visible. Overlay state persists across restarts.
- **Service Indicator**: Visual indicator for which team has possession/service.
- **Customizable Logos**: Upload custom logos for both Home and Away teams directly from the control panel.
- **Persistent State**: Scores are saved to a local `config.json` file on the server and synced across all connected clients.
- **Single File Executable**: Can be compiled into a single `.exe` file for easy distribution.

## Quick Start (Using the EXE)

This project is set up with GitHub Actions to automatically build a Windows executable.

1. Go to the **Actions** tab in this repository.
2. Click on the latest successful **Build & Test** workflow run.
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

Once the server is running (you should see something like `(XXXX) wsgi starting up on http://0.0.0.0:8000` in the console):

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

Use this interface to change team names, update scores, manage sets, upload logos, and configure team colors.

The control panel also includes **live overlay previews** (in the Match, Teams and Match Stats tabs): scaled-down, real-time copies of the scoreboard, sets, formation, timer, timeouts and score history overlays. They update instantly via the same WebSocket used by OBS, so you can track changes as you adjust the score. Previews are scaled to fit the panel width; previews on hidden tabs render automatically when you switch to their tab.

### 2. Add to OBS Studio
1. Open OBS Studio.
2. Under **Sources**, click the `+` icon and select **Browser**.
3. Name it "Volleyball Scoreboard".
4. Configure the settings:
   - **URL**: `http://localhost:8000/`
   - **Width**: `1050` (The board is 1000px wide, extra space prevents scrollbars)
   - **Height**: `300`
   - **Custom CSS**: (Leave empty)
5. Click **OK**.

#### Additional Overlay Views

**Sets Scorebug** (shows all sets):
- **URL**: `http://localhost:8000/scorebug_sets`
- **Width**: `1050`
- **Height**: `350`

**Home Formation**:
- **URL**: `http://localhost:8000/home_formation`
- **Width**: `960`
- **Height**: `1080`

**Away Formation**:
- **URL**: `http://localhost:8000/away_formation`
- **Width**: `960`
- **Height**: `1080`

**Dual Formation** (both teams side by side):
- **URL**: `http://localhost:8000/dual_formation`
- **Width**: `1920`
- **Height**: `1080`

**Match Timer**:
- **URL**: `http://localhost:8000/match_timer`
- **Width**: `400`
- **Height**: `200`

**Timeouts**:
- **URL**: `http://localhost:8000/timeouts`
- **Width**: `550`
- **Height**: `200`

**Score History** (last 5 points):
- **URL**: `http://localhost:8000/score_history`
- **Width**: `450`
- **Height**: `350`

**Match Export** (downloads JSON/CSV, not an overlay):
- **URL**: `http://localhost:8000/export_match`

#### Recommended OBS layout: one scene

Because the timer, timeouts, score history and sets overlays render fully transparent when hidden, you don't need separate scenes per overlay. Add all overlay browser sources to a single scene, stack them at the same position and size, then use the **Overlay Display** toggles in the control panel to fade the one you need in and out. The main scorebug (URL `http://localhost:8000/`) is always visible.

### 3. Uploading Logos, Colors and Players
In the Control Panel, you can:
- Upload PNG or JPG files for both teams. These logos are saved on the server in an `uploads` folder and will persist across restarts.
- Configure primary and secondary colors for each team using color pickers. These colors will appear in the formation headers and logo bars.
- Enter the 6 starting players per team (positions 1-6). These names are shown in the formation overlays.
- Configure the shared **overlay theme** (background, accent and border colors for scorebug, sets, timer, timeouts and history) and toggle which overlays are **displayed** in the Settings tab.

### 4. Manual Set Adjustment
The control panel allows manual set adjustment. You can increment/decrement sets manually using the +/- buttons next to the sets input fields. This is useful if you need to correct the set count due to an error or special situation.

The server will also automatically increment sets when a team reaches 25 points (or 15 in the 5th set) with at least a 2-point lead.

## Project Structure

```
.
├── .github/workflows/build.yml   # GitHub Actions: test job + EXE build job
├── scorebug/
│   ├── static/
│   │   ├── scorebug.html         # Main scoreboard overlay
│   │   ├── scorebug_sets.html    # All sets scoreboard overlay
│   │   ├── control_panel.html    # The control panel
│   │   ├── home_formation.html   # Home team lineup view
│   │   ├── away_formation.html   # Away team lineup view
│   │   ├── dual_formation.html   # Both teams lineup view
│   │   ├── match_timer.html      # Match timer overlay
│   │   ├── timeouts.html         # Timeouts overlay
│   │   ├── score_history.html    # Last 5 points overlay
│   │   ├── export_match.html     # Match export page
│   │   └── volley-ui.js          # Shared frontend utilities
│   ├── server.py                 # The Flask-SocketIO server
│   ├── server.spec               # PyInstaller build spec
│   └── tests/                    # Automated integration tests (pytest)
├── e2e/                          # Playwright end-to-end tests (Node)
│   ├── playwright.config.js      # Launches an isolated server on port 8130
│   └── tests/                    # Full-match, set 5, timer, PIN, previews, theme, visibility...
├── .gitignore
├── README.md
└── requirements.txt
```

## How Set Auto-Completion Works

When a set is won:
1. A team reaches 25 points (or 15 in the 5th set)
2. The winning team has at least a 2-point lead
3. The server automatically:
   - Records the set score to `previousSetScores`
   - Increments the winning team's set count
   - Updates `currentSet` to the next set number (max 5)
   - Resets the score to 0-0 for the new set
   - Emits the updated state to all connected clients

The Sets Scorebug (`scorebug_sets.html`) uses this information to display:
- The current set's live score in the active set column
- Completed set scores in their respective columns
- 0-0 for sets not yet played
- Alternating orange (sets 1,3,5) and blue (sets 2,4) color themes

## Development

- **Backend**: Python (Flask, Flask-SocketIO, Gevent)
- **Frontend**: HTML, CSS, JavaScript (Vanilla), Socket.IO Client
- **Build Tool**: PyInstaller

### Running Tests

The integration tests start a real server instance on an isolated port and verify the API end-to-end:

```bash
pip install pytest requests
python -m pytest scorebug/tests -v
```

Your `config.json` and `logs/` are automatically backed up and restored around the test run.

### Running Playwright E2E Tests

End-to-end tests simulate a real user driving the control panel in a headless Chromium browser and verify the overlays react in real time (full matches, the 5th-set tie-break, timer pause/resume, PIN protection, overlay previews, theme colors, overlay show/hide, exports and more). They run against an isolated server on port 8130 with its own `config.json` and logs.

```bash
cd e2e
npm install
npx playwright install chromium
npx playwright test
```

> **Windows PowerShell note:** if `npm`/`npx` are blocked by the execution policy, prefix the command with `cmd /c`, e.g. `cmd /c "npx playwright test"`.

### Test Isolation

The server honors three environment variables so tests never touch your real data:

- `VOLLEYSCORE_PORT` - the HTTP port to listen on
- `VOLLEYSCORE_CONFIG` - path to a `config.json` other than the default
- `VOLLEYSCORE_LOG_DIR` - directory for the match report logs

Both test suites (pytest and Playwright) run automatically on every push via the `test` job in `.github/workflows/build.yml`.

## Contributing

Contributions are welcome! Please feel free to submit a pull request. See [CONTRIBUTING.md](CONTRIBUTING.md) for more information.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.