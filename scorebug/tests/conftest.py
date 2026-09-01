import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pytest
import requests

BASE_DIR = Path(__file__).resolve().parent.parent
SERVER_SCRIPT = BASE_DIR / "server.py"
PORT = 8123
URL = f"http://127.0.0.1:{PORT}"

CONFIG_FILE = BASE_DIR / "config.json"
LOG_DIR = BASE_DIR / "logs"


def baseline_config():
    return {
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
        "previousSetScores": [None, None, None, None, None],
        "awayColorPrimary": "#FF0000",
        "awayColorSecondary": "#FFAAAA",
        "homeColorPrimary": "#0000FF",
        "homeColorSecondary": "#AAAAFF",
        "themeBgPrimary": "#142850",
        "themeBgSecondary": "#0a1f3c",
        "themeAccent": "#F0A500",
        "themeAccentSecondary": "#B87B00",
        "themeBorder": "#2a406b",
        "overlayVisibility": {"scorebug_sets": False, "timer": False, "timeouts": False, "score_history": False},
        "keyboardShortcuts": {"home_point_plus": "1","home_point_minus": "shift+1","away_point_plus": "2","away_point_minus": "shift+2","home_set_plus": "3","home_set_minus": "shift+3","away_set_plus": "4","away_set_minus": "shift+4","possession_cycle": "space","timer_toggle": "t","timer_reset": "shift+t","home_timeout_plus": "u","home_timeout_minus": "shift+u","away_timeout_plus": "i","away_timeout_minus": "shift+i","overlay_sets": "ctrl+1","overlay_timer": "ctrl+2","overlay_timeouts": "ctrl+3","overlay_history": "ctrl+4","tab_match": "alt+1","tab_teams": "alt+2","tab_settings": "alt+3"},
        "matchTitle": "Test Match",
        "pin": "",
        "timerStarted": False,
        "timerPaused": False,
        "timerStartTimestamp": None,
        "timerPausedTimestamp": None,
        "accumulatedTime": 0,
        "homeTimeouts": 2,
        "awayTimeouts": 2,
        "scoreHistory": [],
    }


def get_daily_rows(port=PORT, log_dir=None):
    """Read the last daily CSV for the test server's VOLLEYSCORE_LOG_DIR."""
    import glob, csv
    if log_dir is None:
        log_dir = os.environ.get("VOLLEYSCORE_LOG_DIR", str(LOG_DIR))
    files = sorted(glob.glob(os.path.join(log_dir, "match_report_*.csv")))
    if not files:
        return []
    with open(files[-1], newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


@pytest.fixture(scope="session")
def server_process():
    backup = Path(tempfile.mkdtemp(prefix="volleyscore_backup_"))
    if CONFIG_FILE.exists():
        shutil.copy2(CONFIG_FILE, backup / "config.json")
    if LOG_DIR.exists():
        shutil.copytree(LOG_DIR, backup / "logs", dirs_exist_ok=True)

    log_path = Path(tempfile.mkdtemp(prefix="volleyscore_srv_")) / "server.log"
    isolated_log_dir = Path(tempfile.mkdtemp(prefix="volleyscore_logs_"))
    # expose for helpers
    os.environ["VOLLEYSCORE_LOG_DIR"] = str(isolated_log_dir)
    env = {**os.environ, "VOLLEYSCORE_PORT": str(PORT), "VOLLEYSCORE_LOG_DIR": str(isolated_log_dir)}
    proc = subprocess.Popen(
        [sys.executable, str(SERVER_SCRIPT)],
        cwd=str(BASE_DIR),
        stdout=log_path.open("w"),
        stderr=subprocess.STDOUT,
        env=env,
    )

    deadline = time.time() + 30
    while time.time() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f"Server exited early. Log:\n{log_path.read_text()}")
        try:
            r = requests.get(f"{URL}/current", timeout=1)
            if r.status_code == 200:
                break
        except requests.RequestException:
            time.sleep(0.2)
    else:
        proc.terminate()
        raise RuntimeError(f"Server did not start. Log:\n{log_path.read_text()}")

    yield proc

    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()

    shutil.rmtree(isolated_log_dir, ignore_errors=True)
    os.environ.pop("VOLLEYSCORE_LOG_DIR", None)
    if (backup / "config.json").exists():
        shutil.copy2(backup / "config.json", CONFIG_FILE)
    else:
        CONFIG_FILE.unlink(missing_ok=True)
    if (backup / "logs").exists():
        shutil.rmtree(LOG_DIR, ignore_errors=True)
        shutil.copytree(backup / "logs", LOG_DIR)


@pytest.fixture()
def clean_state(server_process):
    payload = json.dumps(baseline_config())
    r = requests.post(
        f"{URL}/import_config",
        files={"configFile": ("baseline.json", payload.encode(), "application/json")},
    )
    assert r.status_code == 200, r.text
    return server_process
