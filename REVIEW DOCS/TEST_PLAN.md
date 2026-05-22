# AW-StreamDeck — Full Test Plan

Complete checklist to verify every button, script, and integration works before your next work day.

---

## Pre-Test Checklist

Before testing buttons, confirm the infrastructure is running.

### 1. ActivityWatch is running

- [ ] Open `http://localhost:5600` in your browser — it should load the AW dashboard
- [ ] In Task Manager, confirm `aw-qt.exe` is running

If AW is not running:
```
Start-Process "C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-qt.exe"
```

### 2. Watcher is running

- [ ] Open Task Manager → confirm `aw-streamdeck.exe` is running
- [ ] Check the watcher log for recent entries:

```powershell
Get-Content "$env:LOCALAPPDATA\activitywatch\activitywatch\Logs\aw-streamdeck\aw-streamdeck.log" -Tail 5
```

You should see `Watcher started` and at least one heartbeat transition line like:
```
2026-05-20 11:02:32,195 [INFO]: unknown -> Email Triage  (20s)
```

If the watcher is not running, restart ActivityWatch:
```powershell
Stop-Process -Name "aw-qt" -Force -ErrorAction SilentlyContinue
Stop-Process -Name "aw-streamdeck" -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Start-Process "C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-qt.exe"
Start-Sleep -Seconds 10
Get-Process -Name "aw-streamdeck" -ErrorAction SilentlyContinue | Format-Table Name,Id
```

### 3. Watcher does NOT reset state on startup

- [ ] Check current state file:
```powershell
Get-Content (Join-Path $env:USERPROFILE ".aw_state.json")
```

- [ ] If it says `{"label": "unknown"}` and you set an activity before restarting, that's the old bug. The fix should preserve state. Verify by:

1. Set an activity from the command line:
```powershell
& "C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\.venv\Scripts\pythonw.exe" "C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\activities\development\pipeline_development.py"
```

2. Confirm state file shows `"Pipeline Development"`

3. Restart the watcher (restart AW as shown above)

4. Check state file again — it should STILL show `"Pipeline Development"`, NOT `"unknown"`

---

## Phase 1: Script Test (Command Line)

Test every script manually from PowerShell. Each script should print the label name and update the state file. Run each command and verify the output.

```powershell
$venvPython = "C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\.venv\Scripts\pythonw.exe"
$base = "C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\activities"
$stateFile = Join-Path $env:USERPROFILE ".aw_state.json"
```

| # | Category | Script | Expected Output | Expected State | PASS? |
|---|----------|--------|----------------|---------------|-------|
| 1 | Development | `pipeline_development.py` | Pipeline Development | Pipeline Development | [ ] |
| 2 | Development | `api_integration.py` | API Integration | API Integration | [ ] |
| 3 | Development | `ml_data_quality_systems.py` | ML / Data Quality Systems | ML / Data Quality Systems | [ ] |
| 4 | Development | `html_document_templates.py` | HTML / Document Templates | HTML / Document Templates | [ ] |
| 5 | Development | `tool_utility_development.py` | Tool / Utility Development | Tool / Utility Development | [ ] |
| 6 | Data Engineering | `etl_planning_design_architecture.py` | ETL Planning, Design & Architecture | ETL Planning, Design & Architecture | [ ] |
| 7 | Data Engineering | `unit_configuration.py` | Unit Configuration | Unit Configuration | [ ] |
| 8 | Data Engineering | `data_validation_cleaning.py` | Data Validation & Cleaning | Data Validation & Cleaning | [ ] |
| 9 | Data Engineering | `data_migration_remediation.py` | Data Migration & Remediation | Data Migration & Remediation | [ ] |
| 10 | Data Engineering | `pipeline_monitoring_testing.py` | Pipeline Monitoring & Testing | Pipeline Monitoring & Testing | [ ] |
| 11 | CRM Admin | `layout_configuration.py` | Layout Configuration | Layout Configuration | [ ] |
| 12 | CRM Admin | `entity_configuration.py` | Entity Configurtaion (Editing / Creating) | Entity Configurtaion (Editing / Creating) | [ ] |
| 13 | CRM Admin | `data_integrity_monitoring.py` | Data Integrity Monitoring | Data Integrity Monitoring | [ ] |
| 14 | CRM Admin | `user_support_troubleshooting.py` | User Support & Troubleshooting | User Support & Troubleshooting | [ ] |
| 15 | CRM Admin | `creating_reports.py` | Creating Reports | Creating Reports | [ ] |
| 16 | Administration | `dues_processing.py` | Dues Processing | Dues Processing | [ ] |
| 17 | Administration | `international_reporting.py` | International Reporting | International Reporting | [ ] |
| 18 | Administration | `seniority_list_management.py` | Seniority List Management | Seniority List Management | [ ] |
| 19 | Administration | `email_triage.py` | Email Triage | Email Triage | [ ] |
| 20 | Administration | `email_follow_up.py` | Email Follow-up | Email Follow-up | [ ] |
| 21 | Systems Infra | `documentation_systems_writing.py` | Documentation / Sytems Writing | Documentation / Sytems Writing | [ ] |
| 22 | Systems Infra | `environment_management.py` | Environment Management | Environment Management | [ ] |
| 23 | Systems Infra | `running_a_crm_backup.py` | Running a CRM Backup | Running a CRM Backup | [ ] |
| 24 | Analysis | `leadership_reporting.py` | Leadership Reporting | Leadership Reporting | [ ] |
| 25 | Analysis | `data_analysis.py` | Data Analysis | Data Analysis | [ ] |
| 26 | Analysis | `research.py` | Research | Research | [ ] |
| 27 | Training | `staff_training.py` | Staff Training | Staff Training | [ ] |
| 28 | Training | `documentation_for_non_technical_users.py` | Documentation for Non-Technical Users | Documentation for Non-Technical Users | [ ] |
| 29 | Training | `stakeholder_education.py` | Stakeholder Education | Stakeholder Education | [ ] |

### Quick-test command for each script:

```powershell
# Example — repeat for each row
& $venvPython "$base\development\pipeline_development.py"
Get-Content $stateFile
```

If any script fails or prints nothing, check:
- File path is correct (spaces, typos)
- The `.py` file exists
- The venv python path is correct

---

## Phase 2: Watcher Pickup Test

After running a script, the watcher should detect the state change within **20 seconds** (one poll cycle).

For each test:

1. Set the activity via command line (or StreamDeck button)
2. Wait 25 seconds
3. Check the watcher log:

```powershell
Get-Content "$env:LOCALAPPDATA\activitywatch\activitywatch\Logs\aw-streamdeck\aw-streamdeck.log" -Tail 3
```

You should see a transition line like:
```
2026-05-20 11:15:02,241 [INFO]: Pipeline Development -> API Integration  (45s)
```

If you see **no new log line after 25 seconds**, the watcher may be stuck. Restart ActivityWatch.

---

## Phase 3: StreamDeck Button Configuration

For each button on the StreamDeck, verify the configuration in the Elgato Stream Deck software (PythonScriptDeck plugin):

### Per-Button Settings

| Field | Value |
|-------|-------|
| **Action** | Python Script Deck |
| **Path to Script** | Full path to the `.py` file (see table below) |
| **Use virtual Environment?** | Yes |
| **Path to Virtual Environment** | `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\.venv\Scripts\pythonw.exe` |

> **IMPORTANT**: If the plugin asks for the virtual environment path as a **folder**, use `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\.venv`. If it asks for a **python interpreter path**, use the full `pythonw.exe` path above. Try the folder first — that's the standard venv format. If buttons don't fire, switch to the `pythonw.exe` path.

> **Why `pythonw.exe`?** Using `python.exe` will flash a CMD window on every button press. `pythonw.exe` runs silently.

### Full Script Paths for Each Button

#### Development (5 buttons)

| Button | Script Path |
|--------|-----------|
| Pipeline Development | `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\activities\development\pipeline_development.py` |
| API Integration | `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\activities\development\api_integration.py` |
| ML / Data Quality Systems | `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\activities\development\ml_data_quality_systems.py` |
| HTML / Document Templates | `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\activities\development\html_document_templates.py` |
| Tool / Utility Development | `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\activities\development\tool_utility_development.py` |

#### Data Engineering (5 buttons)

| Button | Script Path |
|--------|-----------|
| ETL Planning, Design & Architecture | `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\activities\data_engineering\etl_planning_design_architecture.py` |
| Unit Configuration | `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\activities\data_engineering\unit_configuration.py` |
| Data Validation & Cleaning | `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\activities\data_engineering\data_validation_cleaning.py` |
| Data Migration & Remediation | `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\activities\data_engineering\data_migration_remediation.py` |
| Pipeline Monitoring & Testing | `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\activities\data_engineering\pipeline_monitoring_testing.py` |

#### CRM Admin (5 buttons)

| Button | Script Path |
|--------|-----------|
| Layout Configuration | `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\activities\crm_admin\layout_configuration.py` |
| Entity Configuration | `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\activities\crm_admin\entity_configuration.py` |
| Data Integrity Monitoring | `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\activities\crm_admin\data_integrity_monitoring.py` |
| User Support & Troubleshooting | `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\activities\crm_admin\user_support_troubleshooting.py` |
| Creating Reports | `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\activities\crm_admin\creating_reports.py` |

#### Administration (5 buttons)

| Button | Script Path |
|--------|-----------|
| Dues Processing | `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\activities\administration\dues_processing.py` |
| International Reporting | `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\activities\administration\international_reporting.py` |
| Seniority List Management | `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\activities\administration\seniority_list_management.py` |
| Email Triage | `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\activities\administration\email_triage.py` |
| Email Follow-up | `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\activities\administration\email_follow_up.py` |

#### Systems Infrastructure (3 buttons)

| Button | Script Path |
|--------|-----------|
| Documentation / Systems Writing | `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\activities\systems_infrastructure\documentation_systems_writing.py` |
| Environment Management | `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\activities\systems_infrastructure\environment_management.py` |
| Running a CRM Backup | `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\activities\systems_infrastructure\running_a_crm_backup.py` |

#### Analysis & Reporting (3 buttons)

| Button | Script Path |
|--------|-----------|
| Leadership Reporting | `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\activities\analysis_reporting\leadership_reporting.py` |
| Data Analysis | `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\activities\analysis_reporting\data_analysis.py` |
| Research | `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\activities\analysis_reporting\research.py` |

#### Training & Support (3 buttons)

| Button | Script Path |
|--------|-----------|
| Staff Training | `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\activities\training_support\staff_training.py` |
| Documentation for Non-Technical Users | `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\activities\training_support\documentation_for_non_technical_users.py` |
| Stakeholder Education | `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\activities\training_support\stakeholder_education.py` |

---

## Phase 4: StreamDeck Button Test

Press each button on the Stream Deck. After each press, wait 5 seconds and verify the state file changed.

```powershell
# Quick check — run after each button press
Get-Content (Join-Path $env:USERPROFILE ".aw_state.json")
```

| # | Button Label | State file shows | PASS? |
|---|-------------|-----------------|-------|
| 1 | Pipeline Development | | [ ] |
| 2 | API Integration | | [ ] |
| 3 | ML / Data Quality Systems | | [ ] |
| 4 | HTML / Document Templates | | [ ] |
| 5 | Tool / Utility Development | | [ ] |
| 6 | ETL Planning, Design & Architecture | | [ ] |
| 7 | Unit Configuration | | [ ] |
| 8 | Data Validation & Cleaning | | [ ] |
| 9 | Data Migration & Remediation | | [ ] |
| 10 | Pipeline Monitoring & Testing | | [ ] |
| 11 | Layout Configuration | | [ ] |
| 12 | Entity Configuration | | [ ] |
| 13 | Data Integrity Monitoring | | [ ] |
| 14 | User Support & Troubleshooting | | [ ] |
| 15 | Creating Reports | | [ ] |
| 16 | Dues Processing | | [ ] |
| 17 | International Reporting | | [ ] |
| 18 | Seniority List Management | | [ ] |
| 19 | Email Triage | | [ ] |
| 20 | Email Follow-up | | [ ] |
| 21 | Documentation / Systems Writing | | [ ] |
| 22 | Environment Management | | [ ] |
| 23 | Running a CRM Backup | | [ ] |
| 24 | Leadership Reporting | | [ ] |
| 25 | Data Analysis | | [ ] |
| 26 | Research | | [ ] |
| 27 | Staff Training | | [ ] |
| 28 | Documentation for Non-Technical Users | | [ ] |
| 29 | Stakeholder Education | | [ ] |

**If a button doesn't work:**
1. Check the PythonScriptDeck configuration for that button (path to script, venv path)
2. Try running the script manually from PowerShell to confirm the script itself works
3. Check if PythonScriptDeck has any error output — look in the Stream Deck app for error indicators

---

## Phase 5: ActivityWatch Timeline Verification

After pressing a few buttons and waiting 60+ seconds, verify events appear in the ActivityWatch timeline.

1. Open `http://localhost:5600` in your browser
2. Go to the **Timeline** view
3. Look for `aw-manual-streamdeck_UFCW-PC005` in the Activity filter
4. You should see colored blocks matching the activities you've been testing

### Verify via API:

```powershell
$r = Invoke-WebRequest -Uri "http://localhost:5600/api/0/buckets/aw-manual-streamdeck_UFCW-PC005/events?limit=10" -UseBasicParsing
$r.Content | ConvertFrom-Json | ForEach-Object { "$($_.data.label) — $([Math]::Round($_.duration,1))s" }
```

You should see activity labels with durations growing over time.

---

## Phase 6: End-to-End Quick Test

The fastest way to confirm everything works:

```powershell
# 1. Set activity to "Email Triage"
& "C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\.venv\Scripts\pythonw.exe" "C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\activities\administration\email_triage.py"

# 2. Verify state file
Get-Content (Join-Path $env:USERProfile ".aw_state.json")
# Expected: {"label": "Email Triage"}

# 3. Wait 25 seconds, then check watcher log
Start-Sleep -Seconds 25
Get-Content "$env:LOCALAPPDATA\activitywatch\activitywatch\Logs\aw-streamdeck\aw-streamdeck.log" -Tail 3
# Expected: a line showing "-> Email Triage"

# 4. Verify ActivityWatch received it
$r = Invoke-WebRequest -Uri "http://localhost:5600/api/0/buckets/aw-manual-streamdeck_UFCW-PC005/events?limit=3" -UseBasicParsing
($r.Content | ConvertFrom-Json)[0].data.label
# Expected: Email Triage
```

If all three checks pass, the full pipeline works:
**StreamDeck button → script → state file → watcher → ActivityWatch**

---

## Troubleshooting Reference

| Symptom | Check | Fix |
|---------|-------|-----|
| CMD window flashes on button press | PythonScriptDeck venv config | Make sure venv is configured and using `pythonw.exe` |
| Button press but no change in state file | Run script manually from PowerShell | If manual works, the PythonScriptDeck config is wrong |
| State file updates but AW doesn't change | Wait 20 seconds (polling interval) | If still nothing after 25s, check watcher log for errors |
| Watcher not running | Task Manager → `aw-streamdeck.exe` | Restart ActivityWatch (`aw-qt.exe`) |
| Watcher resets to "unknown" on restart | Check this is the fixed version | The `aw_watcher.py` should have `if not STATE_FILE.exists():` guard — if missing, rebuild the exe |
| Activity not showing in AW Timeline | Hard-refresh browser (Ctrl+F5) | AW web UI caches; the data is usually there |
| Need to rebuild exe after code changes | Run rebuild commands | See "Rebuild the EXE" section below |

### Key file locations

| Item | Path |
|------|------|
| State file | `%USERPROFILE%\.aw_state.json` |
| Watcher log | `%LOCALAPPDATA%\activitywatch\activitywatch\Logs\aw-streamdeck\aw-streamdeck.log` |
| Activity scripts | `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\activities\<category>\<name>.py` |
| Virtual environment | `C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck\.venv\` |

### Rebuild the EXE

Only needed if you change `aw_watcher.py` or `config.py`:

```powershell
cd "C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-streamdeck"
.venv\Scripts\Activate.ps1
pyinstaller --onefile --windowed --name aw-streamdeck aw_watcher.py
Stop-Process -Name "aw-streamdeck" -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Copy-Item dist\aw-streamdeck.exe .\aw-streamdeck.exe -Force
Remove-Item dist, build -Recurse -Force
Remove-Item aw-streamdeck.spec -Force
Stop-Process -Name "aw-qt" -Force
Start-Sleep -Seconds 2
Start-Process "C:\Users\abakanec\AppData\Local\Programs\ActivityWatch\aw-qt.exe"
```

---

## Known Issues

### Typo: "Entity Configurtaion"

The label `Entity Configurtaion (Editing / Creating)` has a known typo — "Configurtaion" instead of "Configuration". This is consistent across `set_activity.py`, `aw_watcher.py`, and `entity_configuration.py`. It works correctly as-is, but if you want to fix it, you must update **all three** files and rebuild the exe:

1. `set_activity.py` line 17: `VALID_ACTIVITIES` set
2. `aw_watcher.py` line 39: `Activity` enum value
3. `activities/crm_admin/entity_configuration.py` line 5: the label string

### Typo: "Documentation / Sytems Writing"

Same issue — "Sytems" instead of "Systems". Present in:

1. `set_activity.py` line 26
2. `aw_watcher.py` line 47
3. `activities/systems_infrastructure/documentation_systems_writing.py` line 4

### Typo in test_watcher.py

`test_watcher.py` still uses the old 5-activity list (`admin-email`, `meetings`, `deep-work`, etc.) and old `BUCKET_ID` format. It needs updating to match the current 29-activity taxonomy and `aw-manual-streamdeck_{hostname}` bucket format.