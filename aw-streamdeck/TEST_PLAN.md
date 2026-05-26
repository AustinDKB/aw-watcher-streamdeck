# AW-StreamDeck — Test Plan

Complete checklist to verify every activity script, button, and integration works.

---

## Pre-Test Checklist

Before running any tests, confirm infrastructure is running.

### 1. ActivityWatch is running

- [ ] Open `http://localhost:5600` in your browser — AW dashboard loads
- [ ] Confirm `aw-qt.exe` is running in Task Manager

```powershell
Start-Process "$env:LOCALAPPDATA\Programs\ActivityWatch\aw-qt.exe"
```

### 2. Watcher is running

- [ ] Confirm `aw-streamdeck.exe` in Task Manager
- [ ] Check watcher log:

```powershell
Get-Content "$env:LOCALAPPDATA\activitywatch\activitywatch\Logs\aw-streamdeck\aw-streamdeck.log" -Tail 5
```

Expected: `Watcher started` and at least one heartbeat line like:
```
2026-05-25 09:00:00,000 [INFO]: unknown -> Feature Dev  (20s)
```

If watcher not running:
```powershell
Stop-Process -Name "aw-qt","aw-streamdeck" -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Start-Process "$env:LOCALAPPDATA\Programs\ActivityWatch\aw-qt.exe"
Start-Sleep -Seconds 10
Get-Process -Name "aw-streamdeck" -ErrorAction SilentlyContinue
```

### 3. State is preserved across restarts

- [ ] Set an activity: `python set_activity.py "Feature Dev"`
- [ ] Restart ActivityWatch (commands above)
- [ ] Check state file — should still show `"Feature Dev"`, NOT `"unknown"`

```powershell
Get-Content "$env:USERPROFILE\.aw_state.json"
```

---

## Phase 1: Script Test (Command Line)

Test every activity script from PowerShell. Each should print the label and update the state file.

```powershell
$venvPy = "$env:LOCALAPPDATA\Programs\ActivityWatch\aw-streamdeck\.venv\Scripts\pythonw.exe"
$base   = "$env:LOCALAPPDATA\Programs\ActivityWatch\aw-streamdeck\activities"
$state  = "$env:USERPROFILE\.aw_state.json"
```

| # | Category | Script | Expected Output | PASS? |
|---|----------|--------|----------------|-------|
| 1 | Coding | `coding\feature_dev.py` | Feature Dev | [ ] |
| 2 | Coding | `coding\bug_fix.py` | Bug Fix | [ ] |
| 3 | Coding | `coding\code_review.py` | Code Review | [ ] |
| 4 | Coding | `coding\refactoring.py` | Refactoring | [ ] |
| 5 | Coding | `coding\writing_tests.py` | Writing Tests | [ ] |
| 6 | DevOps | `devops\ci_cd_pipeline.py` | CI/CD Pipeline | [ ] |
| 7 | DevOps | `devops\deployment.py` | Deployment | [ ] |
| 8 | DevOps | `devops\monitoring.py` | Monitoring | [ ] |
| 9 | DevOps | `devops\infrastructure.py` | Infrastructure | [ ] |
| 10 | Planning | `planning\sprint_planning.py` | Sprint Planning | [ ] |
| 11 | Planning | `planning\architecture_design.py` | Architecture Design | [ ] |
| 12 | Planning | `planning\research.py` | Research | [ ] |
| 13 | Planning | `planning\task_management.py` | Task Management | [ ] |
| 14 | Communication | `communication\team_meeting.py` | Team Meeting | [ ] |
| 15 | Communication | `communication\one_on_one.py` | One-on-One | [ ] |
| 16 | Communication | `communication\client_meeting.py` | Client Meeting | [ ] |
| 17 | Communication | `communication\async_comms.py` | Async Comms | [ ] |
| 18 | Learning | `learning\reading_docs.py` | Reading Docs | [ ] |
| 19 | Learning | `learning\tutorial_course.py` | Tutorial / Course | [ ] |
| 20 | Learning | `learning\experimenting.py` | Experimenting | [ ] |
| 21 | Admin | `admin\reports_metrics.py` | Reports & Metrics | [ ] |
| 22 | Admin | `admin\time_tracking.py` | Time Tracking | [ ] |
| 23 | Admin | `admin\admin_email.py` | Admin Email | [ ] |
| 24 | — | `afk.py` | AFK | [ ] |

### Quick-test command for each script:

```powershell
& $venvPy "$base\coding\feature_dev.py"
Get-Content $state
# Expected: {"label": "Feature Dev"}
```

---

## Phase 2: Watcher Pickup Test

After running a script, the watcher detects the change within **20 seconds** (one poll cycle).

1. Set an activity
2. Wait 25 seconds
3. Check watcher log:

```powershell
Get-Content "$env:LOCALAPPDATA\activitywatch\activitywatch\Logs\aw-streamdeck\aw-streamdeck.log" -Tail 3
```

Expected:
```
2026-05-25 09:05:00,000 [INFO]: Feature Dev -> Bug Fix  (45s)
```

If no new log line after 25 seconds, restart ActivityWatch.

---

## Phase 3: Stream Deck Button Configuration

For each button, verify PythonScriptDeck settings in the Elgato Stream Deck app:

| Field | Value |
|-------|-------|
| Action | Python Script Deck |
| Path to Script | Full path to the `.py` file |
| Use virtual Environment? | Yes |
| Path to Virtual Environment | `%LOCALAPPDATA%\Programs\ActivityWatch\aw-streamdeck\.venv` |

> Use `pythonw.exe` (not `python.exe`) to suppress the CMD window flash.

### Script paths by category

**Coding (5 buttons)**

| Button | Script |
|--------|--------|
| Feature Dev | `...\activities\coding\feature_dev.py` |
| Bug Fix | `...\activities\coding\bug_fix.py` |
| Code Review | `...\activities\coding\code_review.py` |
| Refactoring | `...\activities\coding\refactoring.py` |
| Writing Tests | `...\activities\coding\writing_tests.py` |

**DevOps (4 buttons)**

| Button | Script |
|--------|--------|
| CI/CD Pipeline | `...\activities\devops\ci_cd_pipeline.py` |
| Deployment | `...\activities\devops\deployment.py` |
| Monitoring | `...\activities\devops\monitoring.py` |
| Infrastructure | `...\activities\devops\infrastructure.py` |

**Planning (4 buttons)**

| Button | Script |
|--------|--------|
| Sprint Planning | `...\activities\planning\sprint_planning.py` |
| Architecture Design | `...\activities\planning\architecture_design.py` |
| Research | `...\activities\planning\research.py` |
| Task Management | `...\activities\planning\task_management.py` |

**Communication (4 buttons)**

| Button | Script |
|--------|--------|
| Team Meeting | `...\activities\communication\team_meeting.py` |
| One-on-One | `...\activities\communication\one_on_one.py` |
| Client Meeting | `...\activities\communication\client_meeting.py` |
| Async Comms | `...\activities\communication\async_comms.py` |

**Learning (3 buttons)**

| Button | Script |
|--------|--------|
| Reading Docs | `...\activities\learning\reading_docs.py` |
| Tutorial / Course | `...\activities\learning\tutorial_course.py` |
| Experimenting | `...\activities\learning\experimenting.py` |

**Admin (3 buttons)**

| Button | Script |
|--------|--------|
| Reports & Metrics | `...\activities\admin\reports_metrics.py` |
| Time Tracking | `...\activities\admin\time_tracking.py` |
| Admin Email | `...\activities\admin\admin_email.py` |

> `...` = `%LOCALAPPDATA%\Programs\ActivityWatch\aw-streamdeck`

---

## Phase 4: Stream Deck Button Test

Press each button. Wait 5 seconds, then verify the state file.

```powershell
Get-Content "$env:USERPROFILE\.aw_state.json"
```

| # | Button Label | State file shows | PASS? |
|---|-------------|-----------------|-------|
| 1 | Feature Dev | `{"label": "Feature Dev"}` | [ ] |
| 2 | Bug Fix | `{"label": "Bug Fix"}` | [ ] |
| 3 | Code Review | `{"label": "Code Review"}` | [ ] |
| 4 | Refactoring | `{"label": "Refactoring"}` | [ ] |
| 5 | Writing Tests | `{"label": "Writing Tests"}` | [ ] |
| 6 | CI/CD Pipeline | `{"label": "CI/CD Pipeline"}` | [ ] |
| 7 | Deployment | `{"label": "Deployment"}` | [ ] |
| 8 | Monitoring | `{"label": "Monitoring"}` | [ ] |
| 9 | Infrastructure | `{"label": "Infrastructure"}` | [ ] |
| 10 | Sprint Planning | `{"label": "Sprint Planning"}` | [ ] |
| 11 | Architecture Design | `{"label": "Architecture Design"}` | [ ] |
| 12 | Research | `{"label": "Research"}` | [ ] |
| 13 | Task Management | `{"label": "Task Management"}` | [ ] |
| 14 | Team Meeting | `{"label": "Team Meeting"}` | [ ] |
| 15 | One-on-One | `{"label": "One-on-One"}` | [ ] |
| 16 | Client Meeting | `{"label": "Client Meeting"}` | [ ] |
| 17 | Async Comms | `{"label": "Async Comms"}` | [ ] |
| 18 | Reading Docs | `{"label": "Reading Docs"}` | [ ] |
| 19 | Tutorial / Course | `{"label": "Tutorial / Course"}` | [ ] |
| 20 | Experimenting | `{"label": "Experimenting"}` | [ ] |
| 21 | Reports & Metrics | `{"label": "Reports & Metrics"}` | [ ] |
| 22 | Time Tracking | `{"label": "Time Tracking"}` | [ ] |
| 23 | Admin Email | `{"label": "Admin Email"}` | [ ] |
| 24 | AFK | `{"label": "AFK"}` | [ ] |

---

## Phase 5: ActivityWatch Timeline Verification

After pressing buttons and waiting 60+ seconds, verify events appear in AW.

1. Open `http://localhost:5600`
2. Go to **Timeline**
3. Find `aw-manual-streamdeck_<your-hostname>` in the Activity filter
4. Colored blocks should match the activities you pressed

### Verify via API:

```powershell
$hostname = $env:COMPUTERNAME
$url = "http://localhost:5600/api/0/buckets/aw-manual-streamdeck_$hostname/events?limit=10"
(Invoke-WebRequest -Uri $url -UseBasicParsing).Content | ConvertFrom-Json |
    ForEach-Object { "$($_.data.label) — $([Math]::Round($_.duration, 1))s" }
```

---

## Phase 6: End-to-End Quick Test

Full pipeline check in ~30 seconds:

```powershell
$aw = "$env:LOCALAPPDATA\Programs\ActivityWatch\aw-streamdeck"
$hostname = $env:COMPUTERNAME

# 1. Set an activity
& "$aw\.venv\Scripts\pythonw.exe" "$aw\activities\coding\feature_dev.py"

# 2. Verify state file
Get-Content "$env:USERPROFILE\.aw_state.json"
# Expected: {"label": "Feature Dev"}

# 3. Wait one poll cycle, check log
Start-Sleep -Seconds 25
Get-Content "$env:LOCALAPPDATA\activitywatch\activitywatch\Logs\aw-streamdeck\aw-streamdeck.log" -Tail 3
# Expected: line containing "-> Feature Dev"

# 4. Verify AW received it
$url = "http://localhost:5600/api/0/buckets/aw-manual-streamdeck_$hostname/events?limit=3"
((Invoke-WebRequest -Uri $url -UseBasicParsing).Content | ConvertFrom-Json)[0].data.label
# Expected: Feature Dev
```

All four checks passing = full pipeline working.

---

## Troubleshooting

| Symptom | Check | Fix |
|---------|-------|-----|
| CMD flash on button press | PythonScriptDeck venv config | Use `pythonw.exe` not `python.exe` |
| Button press, state file unchanged | Run script manually | If manual works, PythonScriptDeck path is wrong |
| State file correct, AW not updating | Wait 20s (poll interval) | If still nothing, check watcher log |
| Watcher not running | Task Manager | Restart aw-qt |
| "unknown label" in watcher log | Enum/set out of sync | Ensure `Activity` enum, `VALID_ACTIVITIES`, and script `label` string are identical |
| Bucket missing from AW Timeline | Hard-refresh browser | Ctrl+F5; data is there, cache is stale |

### Rebuild the EXE

Only needed when `aw_watcher.py` or `config.py` changes:

```powershell
$aw = "$env:LOCALAPPDATA\Programs\ActivityWatch\aw-streamdeck"
Set-Location $aw
.venv\Scripts\pyinstaller --onefile --windowed --name aw-streamdeck aw_watcher.py
Copy-Item dist\aw-streamdeck.exe .\aw-streamdeck.exe -Force
Remove-Item dist, build, aw-streamdeck.spec -Recurse -Force
Stop-Process -Name "aw-qt","aw-streamdeck" -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Start-Process "$env:LOCALAPPDATA\Programs\ActivityWatch\aw-qt.exe"
```
