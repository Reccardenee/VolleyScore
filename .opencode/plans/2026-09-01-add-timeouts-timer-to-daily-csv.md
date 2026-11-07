# Daily CSV: add timeouts/timer (all but theme) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Daily `match_report_YYYY-MM-DD.csv` (`scorebug/server.py:36-39`) records timeouts + timer state (all match fields except theme) on every point, timeout and timer event, appending in chronological order even after PC shutoff/reboot; old headers ignored.

**Architecture:** Extend `log_score_event` (`scorebug/server.py:193-232`) fieldset (all `DEFAULT_SCORE` scalars except `theme*` + `keyboardShortcuts`/`overlayVisibility`), widen `/update` trigger beyond `homeScore/awayScore/homeSets/awaySets` (`559-563`) to also fire on `homeTimeouts/awayTimeouts/currentSet/timer*`, and add explicit logging in `POST /timer_control` (`609-655`) and `POST /timeout_control` (`657-680`). Keep daily-file `get_daily_log_file` + `'a'` append `225`; new header only if file missing `224-231`; don't-care old data means no migration — new columns appear after first new event.

**Tech Stack:** Python (Flask, gevent), csv `DictWriter`, pytest `VOLLEYSCORE_LOG_DIR` isolation (`scorebug/tests/conftest.py:54`), manual smoke on `dist/server.exe` `VOLLEYSCORE_PORT=8233`.

---

## File Structure

**Files modified:**
- `scorebug/server.py:193-232` — `log_score_event` fieldset + header logic
- `scorebug/server.py:559-563` — `if` guard in `POST /update` that decides when to log
- `scorebug/server.py:609-655` — `POST /timer_control` add old snapshot + log
- `scorebug/server.py:657-680` — `POST /timeout_control` add old snapshot + log
- `scorebug/tests/test_server.py:562-567` — extended CSV tests (append, header, timer/timeout logging)
- `README.md:210-230` — daily log docs

**No new files.**

---

### Task 1: Expand daily CSV fieldset (all but theme)

**Files:**
- Modify: `scorebug/server.py:193-232`

- [ ] **Step 1: Write failing test `test_daily_csv_has_timeout_timer_fields`**

Add to `scorebug/tests/test_server.py` (after `test_qrcode_image`):

```python
def test_daily_csv_has_timeout_timer_fields(clean_state):
    post_update({"homeScore": 1})
    s = get_state()
    assert s["homeScore"] == 1
    # helper get_daily_rows reads VOLLEYSCORE_LOG_DIR/match_report_*.csv
    rows = get_daily_rows()
    header = list(rows[0].keys()) if rows else []
    assert "homeTimeouts" in header
    assert "timerElapsed" in header
    assert "currentSet" in header
    assert "timerStarted" in header
```

- [ ] **Step 2: Run test to verify it fails**

Run: `& .venv\Scripts\python.exe -m pytest scorebug/tests/test_server.py::test_daily_csv_has_timeout_timer_fields -v`
Expected: `FAILED` (header missing timer/timeout cols)

- [ ] **Step 3: Expand `log_score_event`**

In `scorebug/server.py:193-232` replace `log_entry = { ... }` with (all but theme):

```python
def log_score_event(old_score_state, new_score_state):
    timestamp = datetime.now().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "homeName": new_score_state["homeName"],
        "awayName": new_score_state["awayName"],
        "matchTitle": new_score_state.get("matchTitle", ""),
        "currentSet": new_score_state.get("currentSet", 1),
        "oldHomeScore": old_score_state["homeScore"],
        "newHomeScore": new_score_state["homeScore"],
        "oldAwayScore": old_score_state["awayScore"],
        "newAwayScore": new_score_state["awayScore"],
        "oldHomeSets": old_score_state["homeSets"],
        "newHomeSets": new_score_state["homeSets"],
        "oldAwaySets": old_score_state["awaySets"],
        "newAwaySets": new_score_state["awaySets"],
        "homeTimeouts": new_score_state.get("homeTimeouts", 2),
        "awayTimeouts": new_score_state.get("awayTimeouts", 2),
        "homeTimeoutsUsed": 2 - new_score_state.get("homeTimeouts", 2),
        "awayTimeoutsUsed": 2 - new_score_state.get("awayTimeouts", 2),
        "timerStarted": new_score_state.get("timerStarted", False),
        "timerPaused": new_score_state.get("timerPaused", False),
        "timerElapsed": round(compute_timer_elapsed(new_score_state), 1),
        "accumulatedTime": new_score_state.get("accumulatedTime", 0),
        "possession": new_score_state["possession"],
        "event": "score_update",
    }
    if new_score_state["homeScore"] > old_score_state["homeScore"]:
        log_entry["scoredTeam"] = new_score_state["homeName"]
    elif new_score_state["awayScore"] > old_score_state["awayScore"]:
        log_entry["scoredTeam"] = new_score_state["awayName"]
    else:
        log_entry["scoredTeam"] = "None"
    current_log_file = get_daily_log_file()
    file_exists = os.path.exists(current_log_file)
    with open(current_log_file, 'a', newline='') as csvfile:
        fieldnames = list(log_entry.keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(log_entry)
    print(f"Logged score event: {log_entry}")
```

Excludes `themeBgPrimary/Secondary`, `themeAccent`, `themeAccentSecondary`, `themeBorder`, `keyboardShortcuts`, `overlayVisibility`, `homePlayers/awayPlayers`, `previousSetScores`, `scoreHistory`, `homeLogo/awayLogo`, `pin`.

- [ ] **Step 4: Run test to verify it passes**

Run: `& .venv\Scripts\python.exe -m pytest scorebug/tests/test_server.py::test_daily_csv_has_timeout_timer_fields -v`
Expected: `PASSED`

- [ ] **Step 5: Commit**

```bash
git add scorebug/server.py scorebug/tests/test_server.py
git commit -m "feat(csv): daily log includes timeouts/timer (all but theme)"
```

---

### Task 2: Widen `/update` logging trigger + keep daily append

**Files:**
- Modify: `scorebug/server.py:558-564`

- [ ] **Step 1: Write failing test `test_daily_log_on_timeout_change`**

```python
def test_daily_log_on_timeout_change(clean_state):
    r = post_update({"homeSets": 1})
    assert r.status_code == 200
    rows = get_daily_rows()
    assert any(row.get("currentSet") == "2" for row in rows)
```

- [ ] **Step 2: Run to fail**

Run: `& .venv\Scripts\python.exe -m pytest scorebug/tests/test_server.py::test_daily_log_on_timeout_change -v`
Expected: `FAILED` (no row for pure set change)

- [ ] **Step 3: Widen guard**

Replace `scorebug/server.py:558-563`:

```python
    if (current_score["homeScore"] != old_current_score["homeScore"] or
        current_score["awayScore"] != old_current_score["awayScore"] or
        current_score["homeSets"] != old_current_score["homeSets"] or
        current_score["awaySets"] != old_current_score["awaySets"] or
        current_score.get("currentSet", 1) != old_current_score.get("currentSet", 1) or
        current_score.get("homeTimeouts", 2) != old_current_score.get("homeTimeouts", 2) or
        current_score.get("awayTimeouts", 2) != old_current_score.get("awayTimeouts", 2) or
        current_score.get("timerStarted", False) != old_current_score.get("timerStarted", False) or
        current_score.get("timerPaused", False) != old_current_score.get("timerPaused", False) or
        current_score.get("possession", "none") != old_current_score.get("possession", "none") or
        current_score.get("matchTitle", "") != old_current_score.get("matchTitle", "")):
        log_score_event(old_current_score, current_score)
```

- [ ] **Step 4: Run to pass**

Run: `& .venv\Scripts\python.exe -m pytest scorebug/tests -q`
Expected: `all passed`

- [ ] **Step 5: Verify append after reboot**

Manual: `POST /update {"homeScore":1}` → `scorebug/logs/match_report_YYYY-MM-DD.csv` tail has row. Kill `dist/server.exe`, restart same `VOLLEYSCORE_CONFIG`/`LOG_FOLDER`, `POST /update {"homeScore":2}` → tail shows appended row, header not duplicated.

- [ ] **Step 6: Commit**

```bash
git add scorebug/server.py scorebug/tests/test_server.py
git commit -m "feat(csv): log on timeout/timer/set/possession changes, keep daily append"
```

---

### Task 3: Log `POST /timer_control` and `POST /timeout_control`

**Files:**
- Modify: `scorebug/server.py:609-655` and `657-680`

- [ ] **Step 1: Write failing tests**

```python
def test_daily_log_on_timer_pause(clean_state):
    post("/timer_control", {"action": "start"})
    post("/timer_control", {"action": "pause"})
    rows = get_daily_rows()
    assert any(r["timerPaused"] == "True" for r in rows)

def test_daily_log_on_timeout_use(clean_state):
    post("/timeout_control", {"team": "home", "change": -1})
    rows = get_daily_rows()
    assert any(r["homeTimeouts"] == "1" for r in rows)
```

- [ ] **Step 2: Run to fail**

Run: `& .venv\Scripts\python.exe -m pytest scorebug/tests/test_server.py -k "daily_log_on_timer or daily_log_on_timeout" -v`
Expected: `FAILED`

- [ ] **Step 3: Add old snapshot + log**

`scorebug/server.py:609` top of `timer_control`:

```python
def timer_control():
    global current_score
    old_current_score = current_score.copy()
    action = request.form.get("action", "")
    ...
    if old_current_score != current_score:
        log_score_event(old_current_score, current_score)
    save_config(current_score)
    socketio.emit('score_update', current_score)
    return jsonify({"status": "ok"})
```

`scorebug/server.py:657` top of `timeout_control`:

```python
def timeout_control():
    global current_score
    old_current_score = current_score.copy()
    team = request.form.get("team", "")
    change = int(request.form.get("change", 0))
    ...
    if old_current_score != current_score:
        log_score_event(old_current_score, current_score)
    save_config(current_score)
    socketio.emit('score_update', current_score)
    return jsonify({"status": "ok"})
```

- [ ] **Step 4: Run to pass**

Run: `& .venv\Scripts\python.exe -m pytest scorebug/tests -q`
Expected: `all passed`

- [ ] **Step 5: Commit**

```bash
git add scorebug/server.py scorebug/tests/test_server.py
git commit -m "feat(csv): log timer_control and timeout_control events daily"
```

---

### Task 4: Isolate VOLLEYSCORE_LOG_DIR in tests + docs

**Files:**
- Modify: `scorebug/tests/conftest.py:20-60`, `README.md:210-230`

- [ ] **Step 1: Add helper `get_daily_rows()` and isolate log dir**

In `scorebug/tests/conftest.py` after `baseline_config()` add:

```python
def get_daily_rows():
    import os, csv, glob
    log_dir = os.environ.get("VOLLEYSCORE_LOG_DIR", str(LOG_DIR))
    files = sorted(glob.glob(os.path.join(log_dir, "match_report_*.csv")))
    if not files:
        return []
    with open(files[-1], newline='') as f:
        return list(csv.DictReader(f))
```

Modify `server_process` env to `{"VOLLEYSCORE_PORT": str(PORT), "VOLLEYSCORE_LOG_DIR": log_tmp}` where `log_tmp = tempfile.mkdtemp(prefix="volleyscore_logs_")` and cleanup `shutil.rmtree(log_tmp)` after yield.

- [ ] **Step 2: Run pytest**

Run: `& .venv\Scripts\python.exe -m pytest scorebug/tests -q`
Expected: `all passed`, `scorebug/logs/` untouched

- [ ] **Step 3: Update README daily log section**

Add `## Match Logs` describing daily file, append after shutoff, columns (excluding theme), one match per day.

- [ ] **Step 4: Commit**

```bash
git add scorebug/tests/conftest.py scorebug/tests/test_server.py README.md
git commit -m "test(csv): isolate VOLLEYSCORE_LOG_DIR and document daily append"
```

---

### Task 5: Final verification

- [ ] **Step 1: Python tests**

Run: `& .venv\Scripts\python.exe -m pytest scorebug/tests -q`

- [ ] **Step 2: E2E**

Run: `cmd /c "cd e2e && npx playwright test --workers=1"`

- [ ] **Step 3: Local exe smoke (append + timer/timeout):**

```bash
.venv\Scripts\pyinstaller.exe --clean scorebug/server.spec
$env:VOLLEYSCORE_PORT="8233"; $env:VOLLEYSCORE_CONFIG="C:\Temp\vs_csv\config.json"; $env:VOLLEYSCORE_LOG_DIR="C:\Temp\vs_csv\logs"; dist\server.exe
curl http://127.0.0.1:8233/update -F homeScore=1
curl http://127.0.0.1:8233/timeout_control -F team=home -F change=-1
curl http://127.0.0.1:8233/timer_control -F action=pause
cat C:\Temp\vs_csv\logs\match_report_*.csv  # 3 rows, header once
# kill exe, restart same env, curl homeScore=2 → 4th row appended
```

---

## Verification (end)

1. `pytest scorebug/tests -q` — new daily_csv tests pass
2. `npx playwright test --workers=1` — 21 passed
3. Manual exe kill/restart append check

## Self-Review

All but theme: timeouts+timer+currentSet+possession+matchTitle ✓, daily append ✓, shutoff append ✓, old data ignored ✓, theme excluded ✓.
