# AW-StreamDeck — Manual Activity Watcher for ActivityWatch

Full documentation of the setup, changes made, architecture, and Stream Deck wiring.

---

## Table of Contents

1. [What This Does](#what-this-does)
2. [Architecture](#architecture)
3. [Files Changed / Created](#files-changed--created)
4. [ActivityWatch Integration Changes](#activitywatch-integration-changes)
5. [Activity Taxonomy](#activity-taxonomy)
6. [Stream Deck Setup Guide](#stream-deck-setup-guide)
7. [How It Works](#how-it-works)
8. [Rebuilding the EXE](#rebuilding-the-exe)
9. [Troubleshooting](#troubleshooting)

---

## What This Does

This system lets you press a button on your Elgato Stream Deck to log what you're working on to ActivityWatch. Each button press writes your current activity (e.g. "Pipeline Development", "Email Triage") to a state file. A background watcher (`aw-streamdeck.exe`) polls that file every 20 seconds and sends heartbeats to ActivityWatch's API. The result shows up in the ActivityWatch timeline under the `aw-manual-streamdeck_UFCW-PC005` bucket.

The watcher is auto-started by ActivityWatch (aw-qt) alongside the built-in watchers. It logs to `%LOCALAPPDATA%\activitywatch\activitywatch\Logs\aw-streamdeck\aw-streamdeck.log`.

---

## Architecture

```
Stream Deck Button
       |
       v
[PythonScriptDeck Plugin]  -->  runs  activities\<category>\<script>.py
       |                              |
       |                              v
       |                        writes to ~/.aw_state.json
       |                              |
       v                              v
  (no CMD flash)              aw-streamdeck.exe reads state
  via pythonw.exe + venv              |
                                      v
                              POST heartbeat to
                              http://localhost:5600/api/0
                              bucket: aw-manual-streamdeck_UFCW-PC005
                                      |
                                      v
                              ActivityWatch Timeline
```

### Data Flow

1. You press a Stream Deck button
2. PythonScriptDeck runs the corresponding `.py` script via the venv's `pythonw.exe`
3. The script writes `{"label": "Pipeline Development"}` to `~/.aw_state.json`
4. `aw-streamdeck.exe` (running in background, auto-started by aw-qt) polls the state file every 20 seconds
5. When the label changes, the watcher sends a heartbeat to ActivityWatch
6. ActivityWatch stores the event and displays it in the Timeline

---

## Files Changed / Created

### Core Watcher Files

| File | Purpose |
|------|---------|
| `aw_watcher.py` | Main watcher logic (polls state file, sends heartbeats). Logs to file instead of console. |
| `config.py` | Configuration (AW API URL, bucket ID, hostname, intervals) |
| `aw-streamdeck.exe` | PyInstaller-built standalone executable. Auto-discovered and started by aw-qt. |
| `set_activity.py` | CLI tool to set activity from terminal |
| `set-activity.bat` | Batch wrapper for `set_activity.py` (terminal use) |

### ActivityWatch Integration

| File | Purpose |
|------|---------|
| `aw-qt.toml` | Auto-start config (at `%LOCALAPPDATA%\activitywatch\activitywatch\aw-qt\aw-qt.toml`) |
| `aw-streamdeck.toml` | Watcher-specific config |

### Stream Deck Activity Scripts

29 scripts in `activities/<category>/<name>.py`, each writing a label to the state file.

---

## ActivityWatch Integration Changes

### How Auto-Start Works

aw-qt discovers modules by scanning the ActivityWatch install directory for `aw-*.exe` files and recursing into `aw-*` directories. It found `aw-streamdeck.exe` inside `aw-streamdeck/` and registered it as a bundled module.

**Key detail**: aw-qt only recognizes `.exe` files on Windows (not `.py`, `.bat`, or `.cmd`). This is why the watcher was compiled into a standalone executable using PyInstaller.

### aw-qt.toml

**Location:** `%LOCALAPPDATA%\activitywatch\activitywatch\aw-qt\aw-qt.toml`

```toml
[aw-qt]
autostart_modules = ["aw-server", "aw-watcher-afk", "aw-watcher-window", "aw-streamdeck"]

[aw-qt-testing]
#autostart_modules = ["aw-server", "aw-watcher-afk", "aw-watcher-window"]
```

### Bucket Name

Bucket ID is `aw-manual-streamdeck_UFCW-PC005` (uses dynamic hostname via `socket.gethostname()`).

---

## Activity Taxonomy

29 activities across 7 categories. Each maps to a Stream Deck button.

### Development (5)
| Script | Label |
|--------|-------|
| `pipeline_development.py` | Pipeline Development |
| `api_integration.py` | API Integration |
| `ml_data_quality_systems.py` | ML / Data Quality Systems |
| `html_document_templates.py` | HTML / Document Templates |
| `tool_utility_development.py` | Tool / Utility Development |

### Data Engineering (5)
| Script | Label |
|--------|-------|
| `etl_planning_design_architecture.py` | ETL Planning, Design & Architecture |
| `unit_configuration.py` | Unit Configuration |
| `data_validation_cleaning.py` | Data Validation & Cleaning |
| `data_migration_remediation.py` | Data Migration & Remediation |
| `pipeline_monitoring_testing.py` | Pipeline Monitoring & Testing |

### CRM Admin (5)
| Script | Label |
|--------|-------|
| `layout_configuration.py` | Layout Configuration |
| `entity_configuration.py` | Entity Configurtaion (Editing / Creating) |
| `data_integrity_monitoring.py` | Data Integrity Monitoring |
| `user_support_troubleshooting.py` | User Support & Troubleshooting |
| `creating_reports.py` | Creating Reports |

### Administration (5)
| Script | Label |
|--------|-------|
| `dues_processing.py` | Dues Processing |
| `international_reporting.py` | International Reporting |
| `seniority_list_management.py` | Seniority List Management |
| `email_triage.py` | Email Triage |
| `email_follow_up.py` | Email Follow-up |

### Systems Infrastructure (3)
| Script | Label |
|--------|-------|
| `documentation_systems_writing.py` | Documentation / Sytems Writing |
| `environment_management.py` | Environment Management |
| `running_a_crm_backup.py` | Running a CRM Backup |

### Analysis & Reporting (3)
| Script | Label |
|--------|-------|
| `leadership_reporting.py` | Leadership Reporting |
| `data_analysis.py` | Data Analysis |
| `research.py` | Research |

### Training & Support (3)
| Script | Label |
|--------|-------|
| `staff_training.py` | Staff Training |
| `documentation_for_non_technical_users.py` | Documentation for Non-Technical Users |
| `stakeholder_education.py` | Stakeholder Education |

---

## Stream Deck Setup Guide

### Prerequisites

- Elgato Stream Deck software installed
- [PythonScriptDeck](https://marketplace.elgato.com/product/pythonscriptdeck-4cbe9ebb-8a48-427d-b1fa-f5f21b6a68d2) plugin installed from the Elgato Marketplace

### Per-Button Configuration

For each Stream Deck button:

1. Drag **Python Script Deck** action onto the button
2. Configure:

| Field | Value |
|-------|-------|
| **Path to Script** | Full path to the `.py` file (see table below) |
| **Use virtual Environment?** | Yes |
| **Path to Virtual Environment** | `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\.venv` |
| **Python interpreter (optional)** | Leave blank (venv handles it) |

### Example: "Email Triage" Button

- **Path to Script:** `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\activities\administration\email_triage.py`
- **Use virtual Environment?** Yes
- **Path to Virtual Environment:** `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\.venv`

### Stream Deck Profile Layout Suggestion

With 29 buttons + a "Next Page" button, use **4 pages** on a 6-button Stream Deck, or **2 pages** on a 15-button Stream Deck. Organize by category.

---

## How It Works

### The Watcher (`aw-streamdeck.exe`)

- Auto-started by aw-qt alongside the built-in watchers (aw-server, aw-watcher-afk, aw-watcher-window)
- Logs to `%LOCALAPPDATA%\activitywatch\activitywatch\Logs\aw-streamdeck\aw-streamdeck.log`
- Polls `~/.aw_state.json` every 20 seconds (`INTERVAL = 20`)
- When the label changes, sends a heartbeat to ActivityWatch API
- Creates the bucket `aw-manual-streamdeck_UFCW-PC005` on first run
- On startup, resets state to `"unknown"`
- Pulse time is 35 seconds — if no heartbeat received in 35s, AW closes the event
- Built with PyInstaller (`--onefile --windowed`) so no console window appears

### The Activity Scripts (`activities/<category>/<name>.py`)

Each script is minimal — just writes the label to the state file:

```python
import json
from pathlib import Path

STATE_FILE = Path.home() / ".aw_state.json"
STATE_FILE.write_text(json.dumps({"label": "Pipeline Development"}), encoding="utf-8")
print("Pipeline Development")
```

- `print()` output is used by PythonScriptDeck for the "return value" feature
- No CMD flash — runs via `pythonw.exe` in the venv
- No network calls — the watcher handles all API communication

### The State File (`~/.aw_state.json`)

Simple JSON file with a single `label` key:

```json
{"label": "Pipeline Development"}
```

The watcher reads this file, not the scripts directly. This means:
- Multiple scripts can write to it (only the last one wins)
- The watcher is decoupled from the Stream Deck
- You can also set activity from the terminal: `python set_activity.py "Email Triage"`

### The Config (`config.py`)

```python
import socket
from pathlib import Path

STATE_FILE = Path.home() / ".aw_state.json"
AW_BASE    = "http://localhost:5600/api/0"
HOSTNAME   = socket.gethostname()            # UFCW-PC005
BUCKET_ID  = f"aw-manual-streamdeck_{HOSTNAME}"  # aw-manual-streamdeck_UFCW-PC005
PULSE_TIME = 35
INTERVAL   = 20
```

---

## Rebuilding the EXE

If you modify `aw_watcher.py` or `config.py`, you must rebuild the executable for aw-qt to pick up the changes:

```powershell
cd "C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck"

# Activate the venv
.venv\Scripts\Activate.ps1

# Build the exe (must have pyinstaller installed in venv)
pyinstaller --onefile --windowed --name aw-streamdeck aw_watcher.py

# Move the exe from dist/ to the aw-streamdeck directory
Copy-Item dist\aw-streamdeck.exe .\aw-streamdeck.exe -Force

# Clean up build artifacts
Remove-Item dist, build -Recurse -Force
Remove-Item aw-streamdeck.spec -Force

# Restart ActivityWatch to pick up the new exe
Stop-Process -Name aw-qt -Force
Stop-Process -Name aw-streamdeck -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Start-Process "C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-qt.exe"
```

**Important**: The exe is a PyInstaller `--onefile` bundle. It bundles `aw_watcher.py`, `config.py`, and all dependencies (including `requests`). The `--windowed` flag prevents any console window from appearing.

---

## Troubleshooting

### Watcher not auto-starting

1. Check aw-qt logs at `%LOCALAPPDATA%\activitywatch\activitywatch\Logs\aw-qt\` — look for `Starting module aw-streamdeck`
2. If you see `Module aw-streamdeck not found`, verify `aw-streamdeck.exe` exists in `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\`
3. If the exe is missing, rebuild it (see [Rebuilding the EXE](#rebuilding-the-exe))

### Watcher running but not logging

Check `%LOCALAPPDATA%\activitywatch\activitywatch\Logs\aw-streamdeck\aw-streamdeck.log` for errors.

### Button press but no data in ActivityWatch

1. Is the watcher running? Check Task Manager for `aw-streamdeck.exe`
2. Check the state file: `type %USERPROFILE%\.aw_state.json`
3. If state file shows your label but AW doesn't update, wait 20 seconds (polling interval)
4. Check the watcher log for errors
5. Restart ActivityWatch if needed

### CMD window flashes when pressing a button

Make sure the venv is configured in PythonScriptDeck:
- **Use virtual Environment?** → Yes
- **Path to Virtual Environment** → `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\.venv`

The venv includes `pythonw.exe` which runs without a console window. Note: the *watcher* exe uses `--windowed` so it never shows a console. The CMD flash issue is only about the *button scripts*.

### Bucket not showing in Timeline

In ActivityWatch at `http://localhost:5600`:
- Go to **Timeline** view
- Look for the **Activity** filter dropdown at the top
- You should see `aw-manual-streamdeck_UFCW-PC005` listed
- If not, hard-refresh the page (Ctrl+F5)

### Adding a new activity

1. Add the label string to the `Activity` enum in `aw_watcher.py`
2. Add the same string to `VALID_ACTIVITIES` in `set_activity.py`
3. Create a new script in `activities/<category>/<name>.py` following the same pattern
4. **Rebuild the exe** (see [Rebuilding the EXE](#rebuilding-the-exe)) — the watcher must be recompiled for enum changes to take effect
5. Restart ActivityWatch to start the new exe

### Key file locations

| Item | Path |
|------|------|
| Watcher exe | `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\aw-streamdeck.exe` |
| Watcher source | `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\aw_watcher.py` |
| Config | `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\config.py` |
| Watcher log | `%LOCALAPPDATA%\activitywatch\activitywatch\Logs\aw-streamdeck\aw-streamdeck.log` |
| CLI setter | `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\set_activity.py` |
| Activity scripts | `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\activities\<category>\<name>.py` |
| Virtual environment | `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\.venv\` |
| State file | `%USERPROFILE%\.aw_state.json` |
| AW-qt config | `%LOCALAPPDATA%\activitywatch\activitywatch\aw-qt\aw-qt.toml` |
| AW-qt logs | `%LOCALAPPDATA%\activitywatch\activitywatch\Logs\aw-qt\` |
| AW-streamdeck config | `%LOCALAPPDATA%\activitywatch\activitywatch\aw-streamdeck\aw-streamdeck.toml` |
| ActivityWatch data | `%LOCALAPPDATA%\activitywatch\activitywatch\` |