# aw-streamdeck — ActivityWatch Manual Activity Watcher

Logs what you're working on to ActivityWatch via Stream Deck buttons + a background watcher daemon.

---

## How it works

- **Stream Deck button press** → runs `activities/<category>/<name>.py` → writes label to `~/.aw_state.json`
- **aw-streamdeck.exe** (background, auto-started by aw-qt) → polls state file every 20s → sends heartbeats to ActivityWatch
- **ActivityWatch** → stores events in bucket `aw-manual-streamdeck_<hostname>` → shows in Timeline

The CLI tool (`set_activity.py`) can also set the activity from any terminal without needing the Stream Deck.

---

## Project structure

```
aw-streamdeck/
├── aw_watcher.py        # Background daemon
├── config.py            # Constants (STATE_FILE, BUCKET_ID, INTERVAL=20, PULSE_TIME=35)
├── set_activity.py      # CLI: python set_activity.py "Feature Dev"
├── test_watcher.py      # Unit + integration tests
├── requirements.txt     # aw-client
├── activities/          # Activity scripts (one .py per activity)
│   ├── coding/          # Feature Dev, Bug Fix, Code Review, Refactoring, Writing Tests
│   ├── devops/          # CI/CD Pipeline, Deployment, Monitoring, Infrastructure
│   ├── planning/        # Sprint Planning, Architecture Design, Research, Task Management
│   ├── communication/   # Team Meeting, One-on-One, Client Meeting, Async Comms
│   ├── learning/        # Reading Docs, Tutorial / Course, Experimenting
│   ├── admin/           # Reports & Metrics, Time Tracking, Admin Email
│   └── afk.py           # Away From Keyboard
└── generator/           # Stream Deck profile builder
    └── generate_profile.py
```

---

## Fresh PC Setup (~10 min)

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for the full 9-step walkthrough.

Short version:

1. Clone repo to `C:\Users\<YOU>\stream-deck-watcher\`
2. Edit `INSTALL_DIR` and `VENV_EXE` in `generator/generate_profile.py`
3. Build `aw-streamdeck.exe` with PyInstaller (see SETUP_GUIDE § Step 4)
4. Add `"aw-streamdeck"` to `autostart_modules` in `aw-qt.toml`
5. Run `python generator/generate_profile.py` — restart Stream Deck — select **AW Activities**
6. Restart ActivityWatch (aw-qt) — exe auto-starts

---

## Valid activities (23 across 6 categories)

| Category | Activities |
|----------|-----------|
| **Coding** | Feature Dev, Bug Fix, Code Review, Refactoring, Writing Tests |
| **DevOps** | CI/CD Pipeline, Deployment, Monitoring, Infrastructure |
| **Planning** | Sprint Planning, Architecture Design, Research, Task Management |
| **Communication** | Team Meeting, One-on-One, Client Meeting, Async Comms |
| **Learning** | Reading Docs, Tutorial / Course, Experimenting |
| **Admin** | Reports & Metrics, Time Tracking, Admin Email |

Plus **AFK** (Away From Keyboard).

---

## Customizing activities

To add, remove, or rename activities you need to update three files in sync:

### 1. Create the activity script

```python
# activities/<category>/<name>.py
import json
from pathlib import Path

STATE_FILE = Path.home() / ".aw_state.json"
STATE_FILE.write_text(json.dumps({"label": "My Activity"}), encoding="utf-8")
print("My Activity")
```

### 2. Add to the `Activity` enum (`aw_watcher.py`)

```python
MY_ACTIVITY = "My Activity"
```

### 3. Add to `VALID_ACTIVITIES` (`set_activity.py`)

```python
"My Activity",
```

### 4. Add to `CATEGORIES` or `TOP_6` in `generator/generate_profile.py`

```python
("My\nActivity", "my_activity.py"),
```

### 5. Regenerate the Stream Deck profile

```powershell
pip install pillow   # only needed once
python generator/generate_profile.py
```

Restart Stream Deck software, then select **AW Activities** again.

### 6. Rebuild the watcher exe

Because `aw_watcher.py` changed, rebuild the exe (see [SETUP_GUIDE.md § Step 4](SETUP_GUIDE.md)):

```powershell
cd "$env:LOCALAPPDATA\Programs\ActivityWatch\aw-streamdeck"
.venv\Scripts\pyinstaller --onefile --windowed --name aw-streamdeck aw_watcher.py
Copy-Item dist\aw-streamdeck.exe .\aw-streamdeck.exe -Force
```

Then restart ActivityWatch.

---

## CLI usage

```powershell
# Set activity from terminal (bypasses Stream Deck entirely)
python set_activity.py "Feature Dev"
python set_activity.py "AFK"

# Check current activity
Get-Content "$env:USERPROFILE\.aw_state.json"
```

---

## Run tests

```powershell
python test_watcher.py   # requires ActivityWatch running at localhost:5600
```

Tests cover all 23 activities + AFK + end-to-end integration (set label → wait → verify AW event).
