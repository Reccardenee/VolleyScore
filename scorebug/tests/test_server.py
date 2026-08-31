import json
import time

import pytest
import requests

from conftest import URL


def get_state():
    r = requests.get(f"{URL}/current")
    r.raise_for_status()
    return r.json()


def post_update(data):
    return requests.post(f"{URL}/update", data=data)


def post(route, data=None):
    return requests.post(f"{URL}/{route}", data=data or {})


# ============================================
# TIMER
# ============================================

def test_first_point_auto_start_has_zero_accumulated(clean_state):
    r = post_update({"homeScore": 1, "awayScore": 0})
    assert r.status_code == 200
    s = get_state()
    assert s["timerStarted"] is True
    assert s["timerStartTimestamp"] is not None
    assert s["accumulatedTime"] == 0


def test_timer_resume_shifts_start_and_accumulates(clean_state):
    post("/timer_control", {"action": "start"})
    s = get_state()
    start0 = s["timerStartTimestamp"]
    time.sleep(0.6)
    post("/timer_control", {"action": "pause"})
    s = get_state()
    paused_at = s["timerPausedTimestamp"]
    time.sleep(0.3)
    post("/timer_control", {"action": "resume"})
    s = get_state()
    assert s["timerPaused"] is False
    assert abs(s["accumulatedTime"] - (paused_at - start0)) < 0.3
    assert s["timerStartTimestamp"] >= paused_at


def test_elapsed_time_after_pause_resume(clean_state):
    post("/timer_control", {"action": "start"})
    time.sleep(1.0)
    post("/timer_control", {"action": "pause"})
    time.sleep(0.5)
    post("/timer_control", {"action": "resume"})
    time.sleep(1.0)
    s = get_state()
    displayed = s["accumulatedTime"] + (time.time() - s["timerStartTimestamp"])
    assert 1.6 <= displayed <= 2.3


def test_timer_elapsed_frozen_while_paused(clean_state):
    post("/timer_control", {"action": "start"})
    time.sleep(1.0)
    post("/timer_control", {"action": "pause"})
    paused_first = get_state()["timerElapsed"]
    time.sleep(0.7)
    s = get_state()
    # While paused, the authoritative elapsed value must stay frozen
    assert abs(s["timerElapsed"] - paused_first) < 0.3


def test_timer_elapsed_advances_while_running(clean_state):
    post("/timer_control", {"action": "start"})
    s0 = get_state()
    time.sleep(1.1)
    s1 = get_state()
    assert s1["timerElapsed"] - s0["timerElapsed"] >= 0.9
    assert s1["timerElapsed"] > 0


# ============================================
# SCORE HISTORY
# ============================================

def test_set_completion_records_winning_point_and_resets(clean_state):
    r = post_update({"homeScore": 25, "awayScore": 20})
    assert r.status_code == 200
    s = get_state()
    assert s["homeSets"] == 1
    assert s["awaySets"] == 0
    assert s["currentSet"] == 2
    assert s["homeScore"] == 0
    assert s["awayScore"] == 0
    assert s["previousSetScores"] == [{"home": 25, "away": 20}, None, None, None, None]
    assert {"homeScore": 25, "awayScore": 20} in s["scoreHistory"]


def test_score_history_keeps_more_than_five_points(clean_state):
    for i in range(1, 8):
        r = post_update({"homeScore": i, "awayScore": 0})
        assert r.status_code == 200
    s = get_state()
    assert len(s["scoreHistory"]) == 7


def test_csv_export_includes_completed_set_point(clean_state):
    post_update({"homeScore": 25, "awayScore": 20})
    r = requests.get(f"{URL}/export_match_csv")
    assert r.status_code == 200
    assert "25,20" in r.text
    assert len(r.text.strip().splitlines()) >= 2


def test_game_reset_clears_score_history(clean_state):
    post_update({"homeScore": 25, "awayScore": 20})
    assert get_state()["currentSet"] == 2
    r = post_update({"homeScore": 0, "awayScore": 0, "homeSets": 0, "awaySets": 0,
                     "currentSet": 1})
    assert r.status_code == 200
    s = get_state()
    assert s["currentSet"] == 1
    assert s["scoreHistory"] == []


# ============================================
# SET COMPLETION
# ============================================

def test_fifth_set_ends_at_15(clean_state):
    post_update({"currentSet": 5})
    r = post_update({"homeScore": 15, "awayScore": 13})
    assert r.status_code == 200
    s = get_state()
    assert s["homeSets"] == 1
    assert s["currentSet"] == 5
    assert s["homeScore"] == 0


def test_set_completes_at_25_0(clean_state):
    r = post_update({"homeScore": 25, "awayScore": 0})
    assert r.status_code == 200
    s = get_state()
    assert s["homeSets"] == 1
    assert s["currentSet"] == 2
    assert s["previousSetScores"][0] == {"home": 25, "away": 0}
    assert s["homeScore"] == 0


def test_set_completes_at_0_25(clean_state):
    r = post_update({"homeScore": 0, "awayScore": 25})
    assert r.status_code == 200
    s = get_state()
    assert s["awaySets"] == 1
    assert s["currentSet"] == 2
    assert s["previousSetScores"][0] == {"home": 0, "away": 25}


def test_score_only_update_keeps_sets_and_current_set(clean_state):
    post_update({"homeScore": 25, "awayScore": 20})
    assert get_state()["currentSet"] == 2
    r = post_update({"homeScore": 3, "awayScore": 1})
    assert r.status_code == 200
    s = get_state()
    assert s["homeSets"] == 1
    assert s["currentSet"] == 2


def test_manual_set_change_recomputes_current_set(clean_state):
    r = post_update({"homeSets": 2})
    assert r.status_code == 200
    s = get_state()
    assert s["homeSets"] == 2
    assert s["currentSet"] == 3


def test_previous_sets_update_preserves_scores_and_sets(clean_state):
    post_update({"homeScore": 5, "awayScore": 3, "homeSets": 1})
    r = post_update({
        "previousSetScores": json.dumps([{"home": 25, "away": 20}, None, None, None, None]),
    })
    assert r.status_code == 200
    s = get_state()
    assert s["homeScore"] == 5
    assert s["awayScore"] == 3
    assert s["homeSets"] == 1
    assert s["currentSet"] == 2
    assert s["previousSetScores"][0] == {"home": 25, "away": 20}


def test_history_not_wiped_by_normal_updates(clean_state):
    post_update({"homeScore": 1, "awayScore": 0})
    post_update({"homeScore": 2, "awayScore": 0})
    post_update({"homeScore": 0, "awayScore": 0})
    s = get_state()
    assert len(s["scoreHistory"]) == 2


def test_explicit_reset_flag_clears_history(clean_state):
    post_update({"homeScore": 25, "awayScore": 20})
    assert get_state()["currentSet"] == 2
    r = post_update({
        "homeScore": 0, "awayScore": 0, "homeSets": 0, "awaySets": 0,
        "currentSet": 1, "resetGame": "true",
    })
    assert r.status_code == 200
    s = get_state()
    assert s["currentSet"] == 1
    assert s["scoreHistory"] == []
    assert s["previousSetScores"] == [None, None, None, None, None]


def test_set_completion_no_duplicate_when_client_recorded_set(clean_state):
    r = post_update({
        "homeScore": 25, "awayScore": 20, "homeSets": 1,
        "previousSetScores": json.dumps([{"home": 25, "away": 20}, None, None, None, None]),
    })
    assert r.status_code == 200
    s = get_state()
    assert s["previousSetScores"] == [{"home": 25, "away": 20}, None, None, None, None]
    assert s["homeSets"] == 1


def test_previous_set_slots_fill_in_order(clean_state):
    post_update({"homeScore": 25, "awayScore": 20})
    assert get_state()["currentSet"] == 2
    post_update({"homeScore": 18, "awayScore": 25})
    s = get_state()
    assert s["currentSet"] == 3
    assert s["previousSetScores"][0] == {"home": 25, "away": 20}
    assert s["previousSetScores"][1] == {"home": 18, "away": 25}
    assert s["previousSetScores"][2] is None


def test_delete_one_set_keeps_others(clean_state):
    post_update({"homeScore": 25, "awayScore": 20})
    post_update({"homeScore": 18, "awayScore": 25})
    # Delete set 1 only (slot 0 -> None); set 2 must stay
    r = post_update({
        "previousSetScores": json.dumps([None, {"home": 18, "away": 25}, None, None, None]),
    })
    assert r.status_code == 200
    s = get_state()
    assert s["previousSetScores"][0] is None
    assert s["previousSetScores"][1] == {"home": 18, "away": 25}


def test_legacy_compressed_previous_sets_normalized(clean_state):
    r = post_update({
        "homeScore": 1, "awayScore": 0,
        "previousSetScores": json.dumps([{"home": 25, "away": 20}]),
    })
    assert r.status_code == 200
    s = get_state()
    assert len(s["previousSetScores"]) == 5
    assert s["previousSetScores"][0] == {"home": 25, "away": 20}
    assert s["previousSetScores"][1] is None


def test_reset_game_clears_previous_set_slots(clean_state):
    post_update({"homeScore": 25, "awayScore": 20})
    r = post_update({
        "homeScore": 0, "awayScore": 0, "homeSets": 0, "awaySets": 0,
        "currentSet": 1,
        "previousSetScores": json.dumps([None, None, None, None, None]),
    })
    assert r.status_code == 200
    s = get_state()
    assert s["currentSet"] == 1
    assert s["previousSetScores"] == [None, None, None, None, None]


# ============================================
# RESET CONFIG
# ============================================

def test_reset_config_clears_score_history(clean_state):
    post_update({"homeScore": 1, "awayScore": 0})
    r = post("/reset_config")
    assert r.status_code == 200
    assert get_state()["scoreHistory"] == []
    post_update({"homeScore": 1, "awayScore": 0})
    r = post("/reset_config")
    assert r.status_code == 200
    assert get_state()["scoreHistory"] == []


# ============================================
# IMPORT CONFIG
# ============================================

def test_import_minimal_config_merges_with_defaults(clean_state):
    minimal = json.dumps({"homeName": "X", "awayName": "Y"})
    r = requests.post(
        f"{URL}/import_config",
        files={"configFile": ("c.json", minimal.encode(), "application/json")},
    )
    assert r.status_code == 200
    s = get_state()
    assert s["homeName"] == "X"
    assert s["homeTimeouts"] == 2
    r = post_update({"homeScore": 1, "awayScore": 0})
    assert r.status_code == 200
    r = post("/timeout_control", {"team": "home", "change": -1})
    assert r.status_code == 200
    assert get_state()["homeTimeouts"] == 1


# ============================================
# PLAYERS
# ============================================

def test_update_sets_player_names(clean_state):
    r = post_update({"homeP1": "Alice", "homeP2": "Bob", "awayP1": "Zed"})
    assert r.status_code == 200
    s = get_state()
    assert s["homePlayers"][0] == "Alice"
    assert s["homePlayers"][1] == "Bob"
    assert s["awayPlayers"][0] == "Zed"


def test_update_clears_player_name_when_sent_empty(clean_state):
    post_update({"homeP1": "Alice"})
    r = post_update({"homeP1": ""})
    assert r.status_code == 200
    assert get_state()["homePlayers"][0] == ""


def test_update_preserves_players_when_fields_not_sent(clean_state):
    post_update({"homeP1": "Alice"})
    r = post_update({"homeScore": 2})
    assert r.status_code == 200
    s = get_state()
    assert s["homePlayers"][0] == "Alice"


# ============================================
# OVERLAY ROUTES
# ============================================

def test_clean_overlay_routes(clean_state):
    for route in ["/", "/control_panel", "/scorebug_sets", "/match_timer", "/timeouts",
                  "/score_history", "/export_match", "/home_formation", "/away_formation",
                  "/dual_formation"]:
        r = requests.get(f"{URL}{route}")
        assert r.status_code == 200, f"{route} returned {r.status_code}"


def test_static_overlay_files_still_served(clean_state):
    for path in ["/static/scorebug.html", "/static/home_formation.html",
                 "/static/away_formation.html", "/static/dual_formation.html"]:
        r = requests.get(f"{URL}{path}")
        assert r.status_code == 200, f"{path} returned {r.status_code}"


# ============================================
# REGRESSION GUARDS
# ============================================

def test_update_score_and_possession(clean_state):
    r = post_update({"homeScore": 12, "awayScore": 9, "possession": "home"})
    assert r.status_code == 200
    s = get_state()
    assert s["homeScore"] == 12
    assert s["awayScore"] == 9
    assert s["possession"] == "home"


def test_pin_gate_rejects_wrong_pin(clean_state):
    post_update({"pin": "1234", "isSettingPin": "true", "newPin": "1234",
                 "confirmPin": "1234"})
    r = post_update({"homeScore": 5, "pin": "0000"})
    assert r.status_code == 403
    assert get_state()["homeScore"] == 0


def test_timeout_control_bounds(clean_state):
    post("/timeout_control", {"team": "home", "change": -5})
    assert get_state()["homeTimeouts"] == 0
    post("/timeout_control", {"team": "away", "change": 5})
    assert get_state()["awayTimeouts"] == 2


# ============================================
# TIMER EDGE CASES
# ============================================

def test_timer_start_while_running_keeps_timestamp(clean_state):
    post("/timer_control", {"action": "start"})
    s = get_state()
    ts1 = s["timerStartTimestamp"]
    time.sleep(0.4)
    post("/timer_control", {"action": "start"})
    s = get_state()
    assert s["timerStarted"] is True
    assert s["timerStartTimestamp"] == ts1
    assert s["timerPaused"] is False


def test_timer_reset_clears_all_timer_state(clean_state):
    post("/timer_control", {"action": "start"})
    time.sleep(0.5)
    post("/timer_control", {"action": "pause"})
    post_update({"homeScore": 1, "awayScore": 0})
    assert len(get_state()["scoreHistory"]) == 1
    r = post("/timer_control", {"action": "reset"})
    assert r.status_code == 200
    s = get_state()
    assert s["timerStarted"] is False
    assert s["timerPaused"] is False
    assert s["timerStartTimestamp"] is None
    assert s["timerPausedTimestamp"] is None
    assert s["accumulatedTime"] == 0
    assert s["timerElapsed"] == 0
    assert s["scoreHistory"] == []
    assert s["currentSet"] == 1


def test_export_match_json_duration_formats(clean_state):
    post("/timer_control", {"action": "start"})
    time.sleep(1.1)
    r = requests.get(f"{URL}/export_match_json")
    assert r.status_code == 200
    data = r.json()
    assert data["matchDuration"] == "00:01"
    assert data["homeTeam"] == "Home"
    assert data["awayTeam"] == "Away"
    assert data["finalScore"] == {"homeSets": 0, "awaySets": 0, "homePoints": 0, "awayPoints": 0}
    post("/timer_control", {"action": "pause"})
    r = requests.get(f"{URL}/export_match_json")
    data = r.json()
    assert data["matchDuration"] == "00:01"


# ============================================
# TIMEOUT RESETS
# ============================================

def test_timeouts_reset_on_set_completion(clean_state):
    post("/timeout_control", {"team": "home", "change": -1})
    assert get_state()["homeTimeouts"] == 1
    post_update({"homeScore": 25, "awayScore": 20})
    s = get_state()
    assert s["currentSet"] == 2
    assert s["homeTimeouts"] == 2
    assert s["awayTimeouts"] == 2


def test_timeouts_reset_on_manual_set_change(clean_state):
    post("/timeout_control", {"team": "away", "change": -1})
    assert get_state()["awayTimeouts"] == 1
    r = post_update({"homeSets": 2})
    assert r.status_code == 200
    s = get_state()
    assert s["currentSet"] == 3
    assert s["homeTimeouts"] == 2
    assert s["awayTimeouts"] == 2


# ============================================
# PIN LIFECYCLE
# ============================================

def set_pin(pin="1234"):
    return post_update({"pin": "", "isSettingPin": "true", "newPin": pin, "confirmPin": pin})


def test_pin_set_for_first_time(clean_state):
    r = set_pin()
    assert r.status_code == 200
    assert get_state()["pin"] == "1234"


def test_pin_change_with_correct_current_pin(clean_state):
    set_pin("1234")
    r = post_update({"pin": "1234", "isSettingPin": "true", "newPin": "5678", "confirmPin": "5678"})
    assert r.status_code == 200
    assert get_state()["pin"] == "5678"


def test_pin_change_rejects_wrong_current_pin(clean_state):
    set_pin("1234")
    r = post_update({"pin": "0000", "isSettingPin": "true", "newPin": "5678", "confirmPin": "5678"})
    assert r.status_code == 403
    assert get_state()["pin"] == "1234"


def test_pin_rejects_invalid_format(clean_state):
    r = post_update({"pin": "", "isSettingPin": "true", "newPin": "12ab", "confirmPin": "12ab"})
    assert r.status_code == 403
    assert get_state()["pin"] == ""
    r = post_update({"pin": "", "isSettingPin": "true", "newPin": "123", "confirmPin": "123"})
    assert r.status_code == 403
    r = post_update({"pin": "", "isSettingPin": "true", "newPin": "1111", "confirmPin": "2222"})
    assert r.status_code == 403


def test_timer_control_pin_gate(clean_state):
    set_pin()
    r = post("/timer_control", {"action": "start", "pin": "0000"})
    assert r.status_code == 403
    assert get_state()["timerStarted"] is False
    r = post("/timer_control", {"action": "start", "pin": "1234"})
    assert r.status_code == 200
    assert get_state()["timerStarted"] is True


def test_timeout_control_pin_gate(clean_state):
    set_pin()
    r = post("/timeout_control", {"team": "home", "change": -1, "pin": "0000"})
    assert r.status_code == 403
    assert get_state()["homeTimeouts"] == 2
    r = post("/timeout_control", {"team": "home", "change": -1, "pin": "1234"})
    assert r.status_code == 200
    assert get_state()["homeTimeouts"] == 1


# ============================================
# EXPORTS
# ============================================

def test_export_config_roundtrip(clean_state):
    post_update({"homeName": "Ribera", "awayName": "Sciacca", "homeScore": 7, "awayScore": 5})
    r = requests.get(f"{URL}/export_config")
    assert r.status_code == 200
    data = r.json()
    assert data["homeName"] == "Ribera"
    assert data["awayName"] == "Sciacca"
    assert data["homeScore"] == 7
    assert data["awayScore"] == 5
    assert data["homeSets"] == 0
    assert len(data["previousSetScores"]) == 5


def test_export_match_json_content(clean_state):
    post_update({"homeScore": 25, "awayScore": 20})
    post_update({"homeScore": 3, "awayScore": 1})
    r = requests.get(f"{URL}/export_match_json")
    assert r.status_code == 200
    data = r.json()
    assert data["homeTeam"] == "Home"
    assert data["previousSetScores"][0] == {"home": 25, "away": 20}
    assert data["finalScore"]["homeSets"] == 1
    assert len(data["scoreHistory"]) == 2
    assert data["homeTimeoutsUsed"] == 0


def test_export_match_csv_content(clean_state):
    post_update({"homeScore": 1, "awayScore": 0})
    post_update({"homeScore": 2, "awayScore": 0})
    post_update({"homeScore": 2, "awayScore": 1})
    r = requests.get(f"{URL}/export_match_csv")
    assert r.status_code == 200
    lines = r.text.strip().split("\n")
    assert lines[0] == "Point,Home Score,Away Score,Scoring Team"
    assert len(lines) == 4
    assert lines[3].startswith("3,2,1,")


def test_qrcode_image(clean_state):
    r = requests.get(f"{URL}/qrcode_image")
    assert r.status_code == 200
    assert "image" in r.headers.get("Content-Type", "")


# ============================================
# RESET EDGE CASES
# ============================================

def test_reset_game_flag_alone_clears_history(clean_state):
    post_update({"homeScore": 25, "awayScore": 20})
    assert get_state()["currentSet"] == 2
    r = post_update({"homeScore": 0, "awayScore": 0, "resetGame": "true"})
    assert r.status_code == 200
    s = get_state()
    assert s["scoreHistory"] == []
    assert s["previousSetScores"] == [None] * 5
    # currentSet is client-owned: flag alone clears state but keeps the set
    assert s["currentSet"] == 2
    # the panel sends the full reset (currentSet 1), which does move it back
    r = post_update({"homeScore": 0, "awayScore": 0, "currentSet": "1", "homeSets": 0, "awaySets": 0, "resetGame": "true"})
    assert r.status_code == 200
    assert get_state()["currentSet"] == 1


def test_current_set_clamped_at_5(clean_state):
    r = post_update({"homeSets": 4, "awaySets": 4})
    assert r.status_code == 200
    s = get_state()
    assert s["currentSet"] == 5
    r = post_update({"homeSets": 9, "awaySets": 9})
    s = get_state()
    assert s["currentSet"] == 5


def test_score_history_kept_full(clean_state):
    for i in range(1, 9):
        post_update({"homeScore": i, "awayScore": 0})
    s = get_state()
    assert len(s["scoreHistory"]) == 8


# ============================================
# THEME COLORS & OVERLAY VISIBILITY
# ============================================

def test_theme_colors_defaults_in_current(clean_state):
    s = get_state()
    assert s["themeBgPrimary"] == "#142850"
    assert s["themeBgSecondary"] == "#0a1f3c"
    assert s["themeAccent"] == "#F0A500"
    assert s["themeAccentSecondary"] == "#B87B00"
    assert s["themeBorder"] == "#2a406b"


def test_overlay_visibility_defaults_all_hidden(clean_state):
    s = get_state()
    assert s["overlayVisibility"] == {
        "scorebug_sets": False,
        "timer": False,
        "timeouts": False,
        "score_history": False,
    }


def test_update_theme_colors_persist(clean_state):
    r = post_update({
        "themeBgPrimary": "#111111", "themeBgSecondary": "#222222",
        "themeAccent": "#00FF00", "themeAccentSecondary": "#33CC33",
        "themeBorder": "#444444",
    })
    assert r.status_code == 200
    s = get_state()
    assert s["themeBgPrimary"] == "#111111"
    assert s["themeAccent"] == "#00FF00"


def test_theme_colors_survive_later_score_update(clean_state):
    post_update({"themeAccent": "#00FF00"})
    r = post_update({"homeScore": 1, "awayScore": 0})
    assert r.status_code == 200
    assert get_state()["themeAccent"] == "#00FF00"


def test_overlay_toggle_sets_flags(clean_state):
    r = post_update({"overlay_timer": "true", "overlay_timeouts": "true",
                     "overlay_history": "false", "overlay_sets": "false"})
    assert r.status_code == 200
    s = get_state()
    assert s["overlayVisibility"]["timer"] is True
    assert s["overlayVisibility"]["timeouts"] is True
    assert s["overlayVisibility"]["score_history"] is False
    assert s["overlayVisibility"]["scorebug_sets"] is False


def test_overlay_toggle_fields_absent_keeps_existing(clean_state):
    post_update({"overlay_timer": "true"})
    r = post_update({"homeScore": 2})
    assert r.status_code == 200
    assert get_state()["overlayVisibility"]["timer"] is True


# ============================================
# KEYBOARD SHORTCUTS
# ============================================

def test_keyboard_shortcuts_defaults_in_current(clean_state):
    s = get_state()
    assert s["keyboardShortcuts"]["home_point_plus"] == "1"
    assert s["keyboardShortcuts"]["away_point_plus"] == "2"
    assert s["keyboardShortcuts"]["timer_toggle"] == "t"
    assert s["keyboardShortcuts"]["overlay_sets"] == "ctrl+1"


def test_keyboard_shortcuts_saved_and_persist(clean_state):
    new_map = {
        "timer_toggle": "q",
        "home_point_plus": "",
        "tab_settings": "ctrl+shift+9",
    }
    r = post_update({"keyboardShortcuts": json.dumps(new_map)})
    assert r.status_code == 200
    s = get_state()
    assert s["keyboardShortcuts"]["timer_toggle"] == "q"
    assert s["keyboardShortcuts"]["home_point_plus"] == ""
    assert s["keyboardShortcuts"]["tab_settings"] == "ctrl+shift+9"
    # Unchanged keys keep their previous values
    assert s["keyboardShortcuts"]["away_point_plus"] == "2"


def test_keyboard_shortcuts_survive_score_update(clean_state):
    post_update({"keyboardShortcuts": json.dumps({"timer_toggle": "q"})})
    r = post_update({"homeScore": 1, "awayScore": 0})
    assert r.status_code == 200
    s = get_state()
    assert s["keyboardShortcuts"]["timer_toggle"] == "q"


def test_keyboard_shortcuts_invalid_json_ignored(clean_state):
    post_update({"keyboardShortcuts": json.dumps({"timer_toggle": "q"})})
    r = post_update({"keyboardShortcuts": "not json{{"})
    assert r.status_code == 200
    assert get_state()["keyboardShortcuts"]["timer_toggle"] == "q"
