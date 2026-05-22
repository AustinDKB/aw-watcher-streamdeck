# aw-streamdeck — ActivityWatch Manual Activity Watcher

Logs what you're working on to ActivityWatch via Stream Deck buttons + background watcher.

---

## Fresh PC Setup (~5 min)

**Prerequisites:** Python 3.12, ActivityWatch, Stream Deck software + PythonScriptDeck plugin installed.

### 1 — Clone / copy repo
```
C:\Users\<YOU>\stream-deck-watcher\aw-streamdeck\
```

### 2 — Edit USER CONFIG in `generate_profile.py`
```python
INSTALL_DIR  = r"C:\Users\<YOU>\stream-deck-watcher\aw-streamdeck"
VENV_EXE     = r"C:\Users\<YOU>\AppData\Local\Programs\Python\Python312\pythonw.exe"
```
Leave `SCRIPTS_DIR`, `PROFILE_NAME`, and everything else as-is.

### 3 — Build the watcher exe
```powershell
$dest = "$env:LOCALAPPDATA\Programs\ActivityWatch\aw-streamdeck"
mkdir $dest
copy aw_watcher.py $dest
copy config.py $dest
cd $dest
python -m venv .venv
.venv\Scripts\pip install aw-client pyinstaller
.venv\Scripts\pyinstaller --onefile --windowed --name aw-streamdeck aw_watcher.py
copy dist\aw-streamdeck.exe .\aw-streamdeck.exe
```

### 4 — Enable aw-qt autostart
Edit `%LOCALAPPDATA%\activitywatch\activitywatch\aw-qt\aw-qt.toml`:
```toml
[aw-qt]
autostart_modules = ["aw-server", "aw-watcher-afk", "aw-watcher-window", "aw-streamdeck"]
```

### 5 — Generate Stream Deck profile
```powershell
cd C:\Users\<YOU>\stream-deck-watcher\aw-streamdeck
python generate_profile.py
```
Restart Stream Deck → select **AW Activities** profile.

### 6 — Restart ActivityWatch
Close and reopen ActivityWatch (aw-qt). `aw-streamdeck.exe` starts automatically.

### Verify it works
```powershell
# Should show "Watcher started" with today's date:
Get-Content "$env:LOCALAPPDATA\activitywatch\activitywatch\Logs\aw-streamdeck\aw-streamdeck.log" -Tail 5
# Press a Stream Deck button, then check state file updated:
Get-Content "$env:USERPROFILE\.aw_state.json"
```

---

## How it works

- **Stream Deck button press** → runs `activities/<category>/<name>.py` → writes `~/.aw_state.json`
- **aw-streamdeck.exe** (background) → polls state file every 20s → heartbeats to ActivityWatch
- **ActivityWatch** → stores events in bucket `aw-manual-streamdeck_<hostname>`

---

## Valid activities (29)

- **Development:** Pipeline Development, API Integration, ML / Data Quality Systems, HTML / Document Templates, Tool / Utility Development
- **Data Engineering:** ETL Planning Design & Architecture, Unit Configuration, Data Validation & Cleaning, Data Migration & Remediation, Pipeline Monitoring & Testing
- **CRM Admin:** Layout Configuration, Entity Configuration (Editing / Creating), Data Integrity Monitoring, User Support & Troubleshooting, Creating Reports
- **Administration:** Dues Processing, International Reporting, Seniority List Management, Email Triage, Email Follow-up
- **Systems Infrastructure:** Documentation / Systems Writing, Environment Management, Running a CRM Backup
- **Analysis & Reporting:** Leadership Reporting, Data Analysis, Research
- **Training & Support:** Staff Training, Documentation for Non-Technical Users, Stakeholder Education

---

## Add a new activity

1. Add to `Activity` enum in `aw_watcher.py`
2. Add same string to `VALID_ACTIVITIES` in `set_activity.py`
3. Create `activities/<category>/<name>.py` (see any existing script for template)
4. Add to `CATEGORIES` or `TOP_6` in `generate_profile.py`
5. Rebuild exe (repeat Step 3 above) + regenerate profile (Step 5)
