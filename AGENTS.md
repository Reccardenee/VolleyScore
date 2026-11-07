<!-- bmad:context -->
<!-- Verified 2026-11-07 against a4cc37a. Managed by bmad-project-context; edits inside this block are replaced on refresh. Keep anything you want preserved outside the markers. -->

## VolleyScore

Lightweight volleyball scoreboard overlay for OBS Studio and live broadcasts with real-time web control panel. Built with Python 3, Flask, Flask-SocketIO, gevent, vanilla JS / WebSockets, and packaged as a standalone Windows executable via PyInstaller.

## Where things are

- Server backend: `scorebug/server.py`
- Frontend templates and assets: `scorebug/static/`
- PyInstaller executable spec: `scorebug/server.spec`
- Unit tests: `scorebug/tests/` (78 tests via `pytest`)
- End-to-end browser tests: `e2e/tests/` (27 tests via Playwright)
- Built executable output: `scorebug/dist/server.exe`

## Running and verifying

- Virtual environment: Use `uv` or `.venv/Scripts/python.exe`.
- Run unit tests: `.\.venv\Scripts\python.exe -m pytest scorebug/tests -q`
- Run Playwright E2E tests: `cd e2e; npx.cmd playwright test --workers=1`
- Run E2E tests against built executable: `$env:E2E_SERVER_CMD = (Resolve-Path "scorebug/dist/server.exe").Path; cd e2e; npx.cmd playwright test --workers=1`
- Build Windows standalone executable: `cd scorebug; ..\.venv\Scripts\pyinstaller.exe --clean server.spec`

## Conventions that differ from defaults

- Overlay routes omit `.html` extensions (e.g. `/scorebug_sets`, `/match_timer`, `/timeouts`, `/dual_formation`).
- Overlays avoid external CDNs for offline operation during gym live broadcasts; JS dependencies (`socket.io.min.js`, `lucide.min.js`, `volley-ui.js`) are bundled locally under `static/`.
- Paths in `server.py` resolve relative to `sys._MEIPASS` when frozen, and relative to `sys.executable` for writable data (`config.json`, `uploads/`, `logs/`).

## Known pitfalls

- On Windows PowerShell, `npm` and `npx` script policies require invoking `npm.cmd` and `npx.cmd`.
- PyInstaller requires gevent hidden imports explicitly defined in `scorebug/server.spec` (`engineio.async_drivers.gevent`, `geventwebsocket`, `gevent.monkey`, etc.).
- When testing the frozen exe, stdout must be reconfigured to UTF-8 (`errors="replace"`) to prevent UnicodeEncodeError crashes on non-ASCII team or player names.

<!-- /bmad:context -->
