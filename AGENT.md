# AGENT.md — aw-watcher-streamdeck

## What This Is

Python activity tracker bridging manual input → ActivityWatch (localhost:5600).
Three modes of input: CLI command, Stream Deck button press, or direct state file write.
Background daemon polls state file every 20s and sends heartbeats to ActivityWatch API.

## Repo Layout

```
stream-deck-watcher/
└── aw-streamdeck/          # All application code lives here
    ├── aw_watcher.py       # Background daemon (entry: python aw_watcher.py)
    ├── set_activity.py     # CLI switcher (entry: python set_activity.py <label>)
    ├── config.py           # All constants — edit here to change behavior
    ├── test_watcher.py     # Integration + unit tests
    ├── requirements.txt    # Single dep: aw-client
    ├── activities/         # One .py per activity, organized by category
    │   ├── coding/         # feature_dev, bug_fix, code_review, refactoring, writing_tests
    │   ├── devops/         # ci_cd_pipeline, deployment, monitoring, infrastructure
    │   ├── planning/       # sprint_planning, architecture_design, research, task_management
    │   ├── communication/  # team_meeting, one_on_one, client_meeting, async_comms
    │   ├── learning/       # reading_docs, tutorial_course, experimenting
    │   ├── admin/          # reports_metrics, time_tracking, admin_email
    │   └── afk.py
    └── generator/          # Stream Deck profile builder
        └── generate_profile.py
```

## Architecture

```
Stream Deck button / CLI
        ↓
set_activity.py  →  writes label  →  ~/.aw_state.json
                                            ↓  (poll every 20s)
                                      aw_watcher.py
                                            ↓
                               POST heartbeat → ActivityWatch API
                                    localhost:5600/api/0
                                    bucket: aw-manual-streamdeck
```

State machine is a single JSON file. No database, no queue, no IPC.

## Key Constants (config.py)

| Constant    | Value                      | Meaning                              |
|-------------|----------------------------|--------------------------------------|
| `STATE_FILE`  | `~/.aw_state.json`       | Persists current label across runs   |
| `AW_BASE`     | `http://localhost:5600/api/0` | ActivityWatch REST endpoint       |
| `BUCKET_ID`   | `aw-manual-streamdeck`   | Bucket name visible in AW UI         |
| `PULSE_TIME`  | `35`                     | Events within 35s gap merge into one |
| `INTERVAL`    | `20`                     | Seconds between state file polls     |

## Valid Activity Labels (Activity enum in aw_watcher.py)

```
Coding:        Feature Dev | Bug Fix | Code Review | Refactoring | Writing Tests
DevOps:        CI/CD Pipeline | Deployment | Monitoring | Infrastructure
Planning:      Sprint Planning | Architecture Design | Research | Task Management
Communication: Team Meeting | One-on-One | Client Meeting | Async Comms
Learning:      Reading Docs | Tutorial / Course | Experimenting
Admin:         Reports & Metrics | Time Tracking | Admin Email
Special:       unknown
```

`set_activity.py` validates against this set and exits 1 on bad label.
`unknown` is the fallback when the state file is missing or contains an unrecognized label.

## Common Tasks

### Add a new activity type
1. Add value to `Activity` enum in `aw_watcher.py`
2. Add same string to `VALID_ACTIVITIES` set in `set_activity.py`
3. Done — no other changes needed

### Change polling rate
Edit `INTERVAL` and/or `PULSE_TIME` in `config.py`.
Keep `PULSE_TIME > INTERVAL` so heartbeats don't create gaps.

### Change ActivityWatch endpoint
Edit `AW_BASE` in `config.py`.

### Wire a Stream Deck button
Use `generator/generate_profile.py` to auto-generate the full Stream Deck profile (recommended).

For manual wiring, use PythonScriptDeck plugin pointing at the script directly:
```
activities\coding\feature_dev.py
```
No code changes needed for manual wiring.

## Running

```bash
# Setup (one-time)
cd aw-streamdeck
python -m venv .venv
.venv\Scripts\activate
pip install aw-client

# Start watcher daemon (keep running)
python aw_watcher.py

# Switch activity (from any terminal)
python set_activity.py "Feature Dev"
python set_activity.py "AFK"

# Run tests (ActivityWatch must be running)
python test_watcher.py
```

## Testing

`test_watcher.py` has two layers:

**Unit tests** — run fast, test: AW connectivity, bucket creation, heartbeat POST, state file read/write, label validation.

**Integration test** — ~3 minutes. Spawns the actual watcher subprocess, cycles through activities (e.g. 65s Feature Dev → 65s Code Review → 25s AFK), then queries AW API to verify events landed with correct durations.

Tests require ActivityWatch running at localhost:5600. Tests create/use the real `aw-manual-streamdeck` bucket.

## Error Handling Conventions

- Watcher catches all exceptions in the poll loop, logs them, continues running — never crashes on transient AW unavailability.
- `set_activity.py` exits 1 with a message on bad label or file write failure.
- State file missing → treated as "unknown" by watcher (safe default).

## Platform Notes

- State file path uses `pathlib.Path.home()` — works Windows and Linux.
- Tested on Windows with Python 3.12.
- ActivityWatch must be installed separately (not included here).
- Stream Deck software is Elgato's proprietary app — this repo has no dependency on it.

## What Not to Do

- Don't add a database or message queue — the state file pattern is intentional and simple.
- Don't make `aw_watcher.py` accept arguments — `config.py` is the single config surface.
- Don't add activities without updating both `Activity` enum and `VALID_ACTIVITIES` set — they must stay in sync.
- Don't change `PULSE_TIME` below `INTERVAL` — causes gaps in the AW timeline.
