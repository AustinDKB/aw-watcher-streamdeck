# Changelog

## 2026-05-20 — Fix: Watcher resetting activity to `unknown` on restart

### Problem

When ActivityWatch or the `aw-streamdeck` watcher restarted (e.g. system reboot, AW update), the watcher called `reset_state()` unconditionally in `aw_watcher.py:105`, overwriting `~/.aw_state.json` with `{"label": "unknown"}`. This meant any activity set via StreamDeck button was lost on every restart, and all logged time would flip back to `unknown`.

Evidence: the AW event log and watcher log showed only `unknown` labels after the 10:38 AM restart, despite a "Pipeline Development" event from earlier.

### Additional finding

The StreamDeck → script → state file path works correctly when the PythonScriptDeck plugin is properly configured. Manual test confirmed `pythonw.exe email_triage.py` writes to `~/.aw_state.json` and the watcher picks up the change within one poll cycle (~20s). If StreamDeck buttons appear not to work, the issue is in the PythonScriptDeck per-button configuration, not in the watcher.

### Fix

Changed `aw_watcher.py` `main()`:

```python
# Before (reset every startup):
ensure_bucket()
reset_state()
logger.info("Watcher started")

# After (only reset if no state file exists):
ensure_bucket()
if not STATE_FILE.exists():
    reset_state()
logger.info("Watcher started")
```

Also improved `read_state()` error handling — now logs specific warnings for file-not-found vs. parse errors vs. unknown labels, instead of silently falling back.

Also added `logger.debug("heartbeat sent: %s", label)` to `send_heartbeat()` for future debugging.

### Verification

- Rebuilt `aw-streamdeck.exe` with PyInstaller (`--onefile --windowed`)
- Restarted ActivityWatch — watcher preserved "Email Triage" state instead of resetting to `unknown`
- Log confirmed: `unknown -> Email Triage (20s)` showing the existing state was read correctly

### Files changed

| File | Change |
|------|--------|
| `aw_watcher.py` | Don't reset state file on startup if it already exists; improved error logging in `read_state()`; debug log in `send_heartbeat()` |
| `aw-streamdeck.exe` | Rebuilt from updated `aw_watcher.py` |

### Rebuild instructions

After any change to `aw_watcher.py` or `config.py`:

```powershell
cd "C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck"
.venv\Scripts\Activate.ps1
pyinstaller --onefile --windowed --name aw-streamdeck aw_watcher.py
Copy-Item dist\aw-streamdeck.exe .\aw-streamdeck.exe -Force
Remove-Item dist, build -Recurse -Force
Remove-Item aw-streamdeck.spec -Force
# Restart ActivityWatch
Stop-Process -Name aw-qt -Force
Stop-Process -Name aw-streamdeck -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Start-Process "C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-qt.exe"
```

### Key paths

| Item | Path |
|------|------|
| Watcher source | `aw_watcher.py` |
| Config | `config.py` |
| Watcher exe | `aw-streamdeck.exe` |
| State file | `%USERPROFILE%\.aw_state.json` |
| Watcher log | `%LOCALAPPDATA%\activitywatch\activitywatch\Logs\aw-streamdeck\aw-streamdeck.log` |
| Activity scripts | `activities\<category>\<name>.py` |
| Virtual environment | `.venv\` |

### StreamDeck button troubleshooting

If pressing a StreamDeck button doesn't change the activity:

1. Check PythonScriptDeck per-button config:
   - **Path to Script:** full absolute path to the `.py` file
   - **Use virtual Environment?** → **Yes**
   - **Path to Virtual Environment:** `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\.venv`
2. Manually test: `"C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\.venv\Scripts\pythonw.exe" "<path_to_script>.py"` then check `~/.aw_state.json`
3. Check watcher log for activity transitions (appears within ~20s)