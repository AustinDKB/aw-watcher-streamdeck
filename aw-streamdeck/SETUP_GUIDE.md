# AW-StreamDeck — Setup Guide

Complete setup from a fresh Windows PC to a fully working Stream Deck activity tracker.

---

## Prerequisites

Install these before starting. All are free.

| Software | Version | Where to get it |
|----------|---------|-----------------|
| Python | 3.12 (64-bit) | [python.org/downloads](https://www.python.org/downloads/) |
| ActivityWatch | latest | [activitywatch.net](https://activitywatch.net/) |
| Elgato Stream Deck software | latest | [elgato.com/downloads](https://www.elgato.com/downloads) |
| PythonScriptDeck plugin | latest | Elgato Marketplace (search inside Stream Deck software) |
| PyInstaller | (installed via pip below) | — |

> **Python install note:** During install, check **"Add Python to PATH"** and **"Install for all users"**. Use the default install location.

> **PythonScriptDeck:** Open the Stream Deck app → click the "More actions..." icon (puzzle piece) → search "PythonScriptDeck" → Install.

---

## Step 1 — Clone the repository

```powershell
git clone https://github.com/<YOUR-USERNAME>/stream-deck-watcher.git C:\Users\<YOU>\stream-deck-watcher
```

Or download the ZIP and extract to the same path. After this step you should have:

```
C:\Users\<YOU>\stream-deck-watcher\
└── aw-streamdeck\
    ├── aw_watcher.py
    ├── config.py
    ├── set_activity.py
    ├── activities\
    └── generator\
        └── generate_profile.py
```

---

## Step 2 — Edit USER CONFIG in the generator

Open `aw-streamdeck\generator\generate_profile.py` in a text editor and update the two lines at the top of the USER CONFIG section:

```python
# ─── USER CONFIG ──────────────────────────────────────────────────────────────
INSTALL_DIR  = r"C:\Users\<YOU>\stream-deck-watcher\aw-streamdeck"   # <-- your path
VENV_EXE     = r"C:\Users\<YOU>\AppData\Local\Programs\Python\Python312\pythonw.exe"  # <-- your Python
```

- `INSTALL_DIR` → the full path to the `aw-streamdeck` folder (not the repo root).
- `VENV_EXE` → path to `pythonw.exe` inside your Python install. On most systems this is exactly as shown above — just replace `<YOU>` with your Windows username.

Leave `SCRIPTS_DIR`, `PROFILE_NAME`, `TOP_6`, and `CATEGORIES` as-is for now.

**To find your Python path:**
```powershell
where pythonw
# Example output: C:\Users\austi\AppData\Local\Programs\Python\Python312\pythonw.exe
```

---

## Step 3 — Customize your categories (optional)

The default categories are a generic developer template (Coding, DevOps, Planning, etc.). To adapt them to your own workflow:

### 3a — Edit the activity labels in the generator

In `generator/generate_profile.py`, edit the `CATEGORIES` list and `TOP_6` list to match your activities. Each entry follows this pattern:

```python
CATEGORIES = [
    ("ShortName", "Full Category Name", "folder_name", [
        ("Button\nLabel",  "script_filename.py"),
        # add more...
    ]),
    # add more categories...
]
```

- `ShortName` — appears on the folder button on the main Stream Deck page (keep short, ≤8 chars)
- `Full Category Name` — used in documentation only
- `folder_name` — must match the subfolder name inside `activities/`
- `Button\nLabel` — text shown on the Stream Deck button (`\n` = line break)
- `script_filename.py` — must match the Python script file you create in Step 3b

### 3b — Add corresponding activity scripts

For each new activity, create a Python file in `activities/<folder_name>/`:

```python
# activities/coding/my_new_activity.py
import json
from pathlib import Path

STATE_FILE = Path.home() / ".aw_state.json"
STATE_FILE.write_text(json.dumps({"label": "My New Activity"}), encoding="utf-8")
print("My New Activity")
```

The `label` value is what gets logged to ActivityWatch — make it human-readable.

### 3c — Keep the enum and valid set in sync

Every label you add must also appear in two other places:

1. `aw_watcher.py` — add to the `Activity` enum:
   ```python
   MY_NEW_ACTIVITY = "My New Activity"
   ```

2. `set_activity.py` — add to `VALID_ACTIVITIES`:
   ```python
   "My New Activity",
   ```

If these three are out of sync, the watcher will log a warning and fall back to "unknown" for any unrecognized label.

---

## Step 4 — Build the watcher executable

The watcher must be compiled to a `.exe` so ActivityWatch (aw-qt) can auto-start it.

Open PowerShell and run:

```powershell
# Create the deployment directory
$dest = "$env:LOCALAPPDATA\Programs\ActivityWatch\aw-streamdeck"
New-Item -ItemType Directory -Force -Path $dest

# Copy source files
Copy-Item C:\Users\<YOU>\stream-deck-watcher\aw-streamdeck\aw_watcher.py $dest
Copy-Item C:\Users\<YOU>\stream-deck-watcher\aw-streamdeck\config.py $dest

# Set up a venv and install dependencies
Set-Location $dest
python -m venv .venv
.venv\Scripts\pip install aw-client pyinstaller

# Build the exe
.venv\Scripts\pyinstaller --onefile --windowed --name aw-streamdeck aw_watcher.py

# Move exe to deployment root
Copy-Item dist\aw-streamdeck.exe .\aw-streamdeck.exe -Force

# Clean up build artifacts
Remove-Item dist, build -Recurse -Force
Remove-Item aw-streamdeck.spec -Force
```

After this you should have `aw-streamdeck.exe` at:
```
%LOCALAPPDATA%\Programs\ActivityWatch\aw-streamdeck\aw-streamdeck.exe
```

> **Rebuilding:** Any time you change `aw_watcher.py` or `config.py`, repeat this step and restart ActivityWatch.

---

## Step 5 — Enable aw-qt autostart

ActivityWatch's launcher (aw-qt) needs to know to start your watcher alongside the built-in ones.

Open this file in a text editor:
```
%LOCALAPPDATA%\activitywatch\activitywatch\aw-qt\aw-qt.toml
```

Change the `autostart_modules` line to include `aw-streamdeck`:

**Before:**
```toml
[aw-qt]
autostart_modules = ["aw-server", "aw-watcher-afk", "aw-watcher-window"]
```

**After:**
```toml
[aw-qt]
autostart_modules = ["aw-server", "aw-watcher-afk", "aw-watcher-window", "aw-streamdeck"]
```

> **How it works:** aw-qt scans `%LOCALAPPDATA%\Programs\ActivityWatch\` for `aw-*.exe` files and directories. It finds `aw-streamdeck.exe` inside `aw-streamdeck\` and registers it as a module.

---

## Step 6 — Generate the Stream Deck profile

Install Pillow first (needed for icon generation):

```powershell
pip install pillow
```

Then generate the profile from the `aw-streamdeck` folder:

```powershell
Set-Location C:\Users\<YOU>\stream-deck-watcher\aw-streamdeck
python generator/generate_profile.py
```

Expected output:
```
  [Coding] -> <guid>
  [DevOps] -> <guid>
  [Plan] -> <guid>
  [Comms] -> <guid>
  [Learn] -> <guid>
  [Admin] -> <guid>

Profile written: C:\Users\...\Elgato\StreamDeck\ProfilesV3\<GUID>.sdProfile
-> Restart Stream Deck, then select 'AW Activities' in Profiles.
```

The generator writes directly to `%APPDATA%\Elgato\StreamDeck\ProfilesV3\`. No manual file copying needed.

---

## Step 7 — Restart ActivityWatch

Close and reopen ActivityWatch (aw-qt). The `aw-streamdeck.exe` will start automatically.

```powershell
# If ActivityWatch is already running:
Stop-Process -Name aw-qt -Force
Start-Sleep -Seconds 2
Start-Process "$env:LOCALAPPDATA\ActivityWatch\aw-qt.exe"
```

---

## Step 8 — Restart Stream Deck software and select the profile

1. Close and reopen the Elgato Stream Deck application.
2. Click the profile name at the top of the Stream Deck window.
3. Select **"AW Activities"** from the list.

You should see the main page with your top-6 quick-access buttons on the left and category folder buttons on the right.

---

## Step 9 — Verify everything works

Run each check in order:

**Check 1 — Watcher is running**
```powershell
Get-Process aw-streamdeck -ErrorAction SilentlyContinue
# Should show a process entry. If blank, the exe didn't start — check aw-qt logs.
```

**Check 2 — Watcher log shows "started"**
```powershell
Get-Content "$env:LOCALAPPDATA\activitywatch\activitywatch\Logs\aw-streamdeck\aw-streamdeck.log" -Tail 5
# Should show: <timestamp> [INFO]: Watcher started
```

**Check 3 — Press a Stream Deck button**

Press any button (e.g. "Feature Dev"). Then check the state file:
```powershell
Get-Content "$env:USERPROFILE\.aw_state.json"
# Should show: {"label": "Feature Dev"}
```

**Check 4 — ActivityWatch receives the data**

Wait ~25 seconds (one poll cycle), then open `http://localhost:5600` in a browser.
Go to **Timeline** → look for bucket `aw-manual-streamdeck_<your-hostname>` in the filter dropdown.
You should see a bar for the activity you pressed.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `aw-streamdeck.exe` doesn't start | Not in aw-qt.toml, or exe path wrong | Verify `aw-qt.toml` has `"aw-streamdeck"` in `autostart_modules`; verify exe exists at `%LOCALAPPDATA%\Programs\ActivityWatch\aw-streamdeck\aw-streamdeck.exe` |
| Pressing a button does nothing | PythonScriptDeck not configured | In Stream Deck app, check each button → the script path and venv path must be set |
| CMD window flashes on button press | Using `python.exe` instead of `pythonw.exe` | Set `VENV_EXE` to `pythonw.exe` (not `python.exe`) in generator; regenerate profile |
| State file not updating | Script path wrong in button config | Re-run `python generator/generate_profile.py` after setting correct `INSTALL_DIR`; re-import profile |
| Watcher log shows "unknown label" | Label in script doesn't match enum | Ensure `Activity` enum, `VALID_ACTIVITIES`, and the script's `label` string are identical |
| No bucket in AW Timeline | Watcher not sending heartbeats | Check watcher log for errors; verify ActivityWatch is running at localhost:5600 |
| Profile not appearing in Stream Deck | Generator didn't run, or SD not restarted | Re-run generator; fully restart Stream Deck software (not just profile switch) |

**aw-qt logs** (shows whether aw-streamdeck was discovered and started):
```
%LOCALAPPDATA%\activitywatch\activitywatch\Logs\aw-qt\
```

**Watcher logs** (shows heartbeats, label transitions, errors):
```
%LOCALAPPDATA%\activitywatch\activitywatch\Logs\aw-streamdeck\aw-streamdeck.log
```

---

## Key file locations

| Item | Path |
|------|------|
| Repo source | `C:\Users\<YOU>\stream-deck-watcher\aw-streamdeck\` |
| Watcher exe | `%LOCALAPPDATA%\Programs\ActivityWatch\aw-streamdeck\aw-streamdeck.exe` |
| Watcher log | `%LOCALAPPDATA%\activitywatch\activitywatch\Logs\aw-streamdeck\aw-streamdeck.log` |
| State file | `%USERPROFILE%\.aw_state.json` |
| aw-qt config | `%LOCALAPPDATA%\activitywatch\activitywatch\aw-qt\aw-qt.toml` |
| aw-qt logs | `%LOCALAPPDATA%\activitywatch\activitywatch\Logs\aw-qt\` |
| Stream Deck profiles | `%APPDATA%\Elgato\StreamDeck\ProfilesV3\` |
