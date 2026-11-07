# Overlay Theme + Visibility Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a configurable 5-color theme shared by all overlays (except formations) and per-overlay show/hide control with a fade+rise animation, driven from the control panel.

**Architecture:** Extend the existing single-state design — new keys in `current_score` flow automatically to `/current` and the `score_update` socket broadcast (server.py:510-528). Overlays map those keys to CSS variables; the panel drives both via the existing `/update` POST. No new routes, no plugins needed in OBS.

**Tech Stack:** Flask + Socket.IO (Python), vanilla JS/CSS overlays, pytest, Playwright.

---

### Task 1: Server — add theme + overlay keys to defaults

**Files:**
- Modify: `scorebug/server.py:54-86` (DEFAULT_SCORE)

- [ ] **Step 1: Write the failing test**

Add to `scorebug/tests/test_server.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `& .venv\Scripts\python.exe -m pytest scorebug\tests\test_server.py::test_theme_colors_defaults_in_current -q`
Expected: 500 error / KeyError.. Actually `/current` returns full state; missing key just won't be present → assertion fails.

- [ ] **Step 3: Add the keys to `DEFAULT_SCORE`**

In `server.py` after the `homeColorSecondary` line (line ~72):

```python
    "homeColorPrimary": "#0000FF",
    "homeColorSecondary": "#AAAAFF",
    # Overlay theme: shared palette for scorebug/sets/timer/timeouts/history (not formations)
    "themeBgPrimary": "#142850",
    "themeBgSecondary": "#0a1f3c",
    "themeAccent": "#F0A500",
    "themeAccentSecondary": "#B87B00",
    "themeBorder": "#2a406b",
    # Per-overlay show/hide; the standard scorebug is always visible
    "overlayVisibility": {
        "scorebug_sets": False,
        "timer": False,
        "timeouts": False,
        "score_history": False,
    },
```

- [ ] **Step 4: Run tests, expect pass**

`& .venv\Scripts\python.exe -m pytest scorebug\tests\test_server.py -q`
Expected: all pass (existing 50 + new tests).

- [ ] **Step 5: Commit**

---

### Task 2: Server — accept theme colors and overlay toggles in `/update`

**File:**
- Modify: `scorebug/server.py:396-415` (the `current_score.update({...})` block) and right after it

- [ ] **Step 1: Add tests**

```python
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


def test_overlay_toggle_fields_absent_keeps_existing(clean_state):
    # An update carrying no overlay_* fields must not clobber existing flags
    post_update({"overlay_timer": "true"})
    r = post_update({"homeScore": 2})
    assert r.status_code == 200
    assert get_state()["overlayVisibility"]["timer"] is True
```

- [ ] **Step 2: Run tests to verify they fail** (values stay defaults / timer stays false)

Run: `& .venv\Scripts\python.exe -m pytest scorebug\tests\test_server.py -q -k "theme_colors or overlay_toggle"`

- [ ] **Step 3: Implement in the `/update` handler**

In the `current_score.update({ ... })` dict (after `"homeColorSecondary": ...` line ~413):

```python
        "themeBgPrimary": get_val("themeBgPrimary", current_score["themeBgPrimary"]),
        "themeBgSecondary": get_val("themeBgSecondary", current_score["themeBgSecondary"]),
        "themeAccent": get_val("themeAccent", current_score["themeAccent"]),
        "themeAccentSecondary": get_val("themeAccentSecondary", current_score["themeAccentSecondary"]),
        "themeBorder": get_val("themeBorder", current_score["themeBorder"]),
```

After the dict closes (after line 415):

```python
    # Overlay visibility: full-replacement semantics. Toggled flags always
    # arrive together from the panel; fields omitted are left untouched.
    if any(k in form_data for k in ("overlay_timer", "overlay_timeouts",
                                    "overlay_history", "overlay_sets")):
        vis = dict(current_score.get("overlayVisibility", {
            "scorebug_sets": False, "timer": False, "timeouts": False, "score_history": False,
        }))
        vis["timer"] = form_data.get("overlay_timer") == "true"
        vis["timeouts"] = form_data.get("overlay_timeouts") == "true"
        vis["score_history"] = form_data.get("overlay_history") == "true"
        vis["scorebug_sets"] = form_data.get("overlay_sets") == "true"
        current_score["overlayVisibility"] = vis
```

- [ ] **Step 4: Run tests to verify pass**

Run: `& .venv\Scripts\python.exe -m pytest scorebug\tests\test_server.py -q`
Expected: all tests pass.

- [ ] **Step 5: Commit**

---

### Task 3: scorebug + scorebug_sets — apply theme (and visibility for sets)

**Files:**
- Modify: `scorebug/static/scorebug.html` (updateUI at ~440)
- Modify: `scorebug/static/scorebug_sets.html` (updateUI at ~473, body at ~265)

- [ ] **Step 1: Edit `scorebug.html`**

In `updateUI`, right after the existing team-color block (lines 440-444):

```js
    // Overlay theme (shared non-team palette)
    root.style.setProperty('--primary-blue', data.themeBgPrimary || '#142850');
    root.style.setProperty('--secondary-blue', data.themeBgSecondary || '#0a1f3c');
    root.style.setProperty('--accent-gold', data.themeAccent || '#F0A500');
    root.style.setProperty('--secondary-gold', data.themeAccentSecondary || '#B87B00');
    root.style.setProperty('--subtle-border-color', data.themeBorder || '#2a406b');
```

(scorebug is never hidden — no visibility code.)

- [ ] **Step 2: Edit `scorebug_sets.html`** — same theme block right after lines 475-478, and add visibility + fade CSS:

In `updateUI` after the color block:

```js
    const sb = document.getElementById('scoreboard');
    const vis = data.overlayVisibility || {};
    if (sb) sb.classList.toggle('hidden', !vis.scorebug_sets);
```

Add to `<style>`:

```css
#scoreboard {
  transition: opacity 0.4s ease, transform 0.4s ease;
}
#scoreboard.hidden {
  opacity: 0;
  transform: translateY(10px);
  pointer-events: none;
}
```

- [ ] **Step 3: Commit**

---

### Task 4: timer, timeouts, score_history — theme + visibility + fade

**Files:**
- Modify: `scorebug/static/match_timer.html`
- Modify: `scorebug/static/timeouts.html`
- Modify: `scorebug/static/score_history.html`

All three follow the same pattern. For each:

- [ ] **Step 1 — CSS (all three):** fade classes for the container:

```css
.timer-container {
  transition: opacity 0.4s ease, transform 0.4s ease;
}
.timer-container.hidden {
  opacity: 0;
  transform: translateY(10px);
  pointer-events: none;
}
```

(repeat with `.timeout-container` / `.history-container`)

- [ ] **Step 2 — timer (match_timer.html):** Call a shared function after `syncTimerState` in both `score_update` handler and the `connect` fetch callback:

```js
    function applyTheme(data) {
      const root = document.documentElement;
      root.style.setProperty('--primary-blue', data.themeBgPrimary || '#142850');
      root.style.setProperty('--secondary-blue', data.themeBgSecondary || '#0a1f3c');
      root.style.setProperty('--accent-gold', data.themeAccent || '#F0A500');
      root.style.setProperty('--secondary-gold', data.themeAccentSecondary || '#B87B00');
    }

    function applyVisibility(data) {
      const vis = data.overlayVisibility || {};
      const el = document.querySelector('.timer-container');
      if (el) el.classList.toggle('hidden', !vis.timer);
    }
```

Call both in the `score_update` handler (`oldState` line ~120) and in the connect fetch (`~172`).

- [ ] **Step 3 — timeouts + score_history:** same two functions; swap `--subtle-border-color` var mapping too, selectors `.timeout-container` / `.history-container`, flags `vis.timeouts` / `vis.score_history`. Replace literal `color: #f0a500;` → `color: var(--accent-gold);` in `timeouts.html:45` and `score_history.html:42`.

- [ ] **Step 4: Commit**

---

### Task 5: Control panel — theme pickers and overlay display toggles

**File:**
- Modify: `scorebug/static/control_panel.html`

- [ ] **Step 1: Add "Overlay Theme" card** under the Settings tab (after the PIN card, ~line 1169):

```html
<div class="card">
  <div class="card-title">Overlay Theme</div>
  <div class="form-group">
    <label class="form-label">Background (top)</label>
    <input type="color" class="color-input" id="themeBgPrimary" value="#142850">
  </div>
  <div class="form-group">
    <label class="form-label">Background (bottom)</label>
    <input type="color" class="color-input" id="themeBgSecondary" value="#0a1f3c">
  </div>
  <div class="form-group">
    <label class="form-label">Accent</label>
    <input type="color" class="color-input" id="themeAccent" value="#F0A500">
  </div>
  <div class="form-group">
    <label class="form-label">Accent (secondary)</label>
    <input type="color" class="color-input" id="themeAccentSecondary" value="#B87B00">
  </div>
  <div class="form-group">
    <label class="form-label">Border</label>
    <input type="color" class="color-input" id="themeBorder" value="#2a406b">
  </div>
  <button class="btn btn-primary" onclick="saveTheme()">Apply Theme</button>
</div>
```

- [ ] **Step 2: Add "Overlay Display" card** (after the theme card):

```html
<div class="card">
  <div class="card-title">Overlay Display</div>
  <p class="form-label">The standard scorebug is always visible. Toggle the rest — they fade in/out on the overlays.</p>
  <div class="grid-2">
    <button class="btn btn-secondary" id="overlayToggleSets" onclick="toggleOverlay('sets')">All Sets</button>
    <button class="btn btn-secondary" id="overlayToggleTimer" onclick="toggleOverlay('timer')">Match Timer</button>
    <button class="btn btn-secondary" id="overlayToggleTimeouts" onclick="toggleOverlay('timeouts')">Timeouts</button>
    <button class="btn btn-secondary" id="overlayToggleHistory" onclick="toggleOverlay('history')">Score History</button>
  </div>
</div>
```

- [ ] **Step 3: loadState additions** (control_panel.html:1379-1383 region, after team colors):

```js
      // Theme colors
      setIfExists('themeBgPrimary', state.themeBgPrimary, '#142850');
      setIfExists('themeBgSecondary', state.themeBgSecondary, '#0a1f3c');
      setIfExists('themeAccent', state.themeAccent, '#F0A500');
      setIfExists('themeAccentSecondary', state.themeAccentSecondary, '#B87B00');
      setIfExists('themeBorder', state.themeBorder, '#2a406b');
```

Add helper:

```js
    function setIfExists(id, value, fallback) {
      const el = document.getElementById(id);
      if (el) el.value = value || fallback;
    }
```

- [ ] **Step 4: Add JS functions** (near `sendTeamSettings`):

```js
    function saveTheme() {
      if (!isAuthenticated) { showToast('Enter PIN first', 'warning'); return; }
      const formData = new FormData();
      formData.append('themeBgPrimary', document.getElementById('themeBgPrimary').value);
      formData.append('themeBgSecondary', document.getElementById('themeBgSecondary').value);
      formData.append('themeAccent', document.getElementById('themeAccent').value);
      formData.append('themeAccentSecondary', document.getElementById('themeAccentSecondary').value);
      formData.append('themeBorder', document.getElementById('themeBorder').value);
      appendPin(formData);
      postUpdate(formData);
    }

    let overlayFlags = { sets: false, timer: false, timeouts: false, history: false };

    function updateOverlayButtons(vis) {
      overlayFlags = {
        sets: !!(vis && vis.scorebug_sets),
        timer: !!(vis && vis.timer),
        timeouts: !!(vis && vis.timeouts),
        history: !!(vis && vis.score_history),
      };
      const setBtn = (id, on) => {
        const el = document.getElementById(id);
        if (el) {
          el.classList.toggle('btn-primary', on);
          el.classList.toggle('btn-secondary', !on);
        }
      };
      setBtn('overlayToggleSets', overlayFlags.sets);
      setBtn('overlayToggleTimer', overlayFlags.timer);
      setBtn('overlayToggleTimeouts', overlayFlags.timeouts);
      setBtn('overlayToggleHistory', overlayFlags.history);
    }

    function toggleOverlay(name) {
      if (!isAuthenticated) { showToast('Enter PIN first', 'warning'); return; }
      overlayFlags[name] = !overlayFlags[name];
      updateOverlayButtons({
        scorebug_sets: overlayFlags.sets,
        timer: overlayFlags.timer,
        timeouts: overlayFlags.timeouts,
        score_history: overlayFlags.history,
      });
      const formData = new FormData();
      formData.append('overlay_sets', overlayFlags.sets ? 'true' : 'false');
      formData.append('overlay_timer', overlayFlags.timer ? 'true' : 'false');
      formData.append('overlay_timeouts', overlayFlags.timeouts ? 'true' : 'false');
      formData.append('overlay_history', overlayFlags.history ? 'true' : 'false');
      appendPin(formData);
      postUpdate(formData);
    }
```

- [ ] **Step 5:** call `updateOverlayButtons(state.overlayVisibility)` inside the `socket.on('score_update')` handler and in `loadState`. Commit.

---

### Task 6: E2E tests for theme + visibility

**File:**
- Create: `e2e/tests/theme.spec.js`

- [ ] **Step 1: Write tests**

```js
const { test, expect } = require('@playwright/test');

async function resetOverlays(request) {
  await request.post('/update', { form: {
    overlay_sets: 'false', overlay_timer: 'false', overlay_timeouts: 'false', overlay_history: 'false',
  }});
}

test('theme color change reaches the match timer overlay', async ({ page, request }) => {
  await request.post('/update', { form: { themeBgPrimary: '#112233' } });
  await page.goto('/match_timer');
  await page.waitForTimeout(500);
  const primary = await page.evaluate(() =>
    getComputedStyle(document.documentElement).getPropertyValue('--primary-color').trim());
  expect(primary).toBe('#112233');
});

test('hiding the timer fades the overlay out', async ({ page, request }) => {
  await resetOverlays(request);
  await request.post('/update', { form: { overlay_timer: 'true' } });
  await page.goto('/match_timer');
  await page.waitForTimeout(400);
  await expect(page.locator('.timer-container')).not.toHaveClass(/hidden/);
  await request.post('/update', { form: { overlay_timer: 'false' } });
  await page.waitForTimeout(500);
  await expect(page.locator('.timer-container')).toHaveClass(/hidden/);
});
```

Note about the CSS var name: match_timer.html currently uses `--primary-blue`. Plan (Task 4) keeps that name. Use the same name in the assertion. Check the theme block actually applied.

- [ ] **Step 2: Run** — from `e2e/`: `cmd /c "npx playwright test --workers=1"`
- [ ] **Step 3: Commit**

---

### Task 7: Docs — README

**File:**
- Modify: `README.md`

Add under existing settings sections:
- **Overlay Theme**: 5 shared colors applied to scorebug, sets, timer, timeouts, history. Formations keep team colors.
- **Overlay Display**: control panel toggles for sets/timer/timeouts/history with fade+rise animation; the standard scorebug stays always on.
- **OBS setup** note: single scene, stack all browser sources at the same position/size; no scene switching required — drive visibility from the panel.

- [ ] **Step 1: Edit README**
- [ ] **Step 2: Commit**

---

## Verification (end)

1. `& .venv\Scripts\python.exe -m pytest scorebug\tests -q`
2. `cd e2e; cmd /c "npx playwright test --workers=1"`