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
    └── requirements.txt    # Single dep: requests
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
deep-work | meetings | admin-email | file-management | afk | unknown
```

`set_activity.py` validates against this set and exits 1 on bad label.
`unknown` is the reset state written on watcher startup.

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
In Stream Deck software, set button action to Open/Run with command:
```
python C:\path\to\aw-streamdeck\set_activity.py "deep-work"
```
No code changes needed.

## Running

```bash
# Setup (one-time)
cd aw-streamdeck
python -m venv .venv
.venv\Scripts\activate
pip install requests

# Start watcher daemon (keep running)
python aw_watcher.py

# Switch activity (from any terminal)
python set_activity.py "deep-work"
python set_activity.py "afk"

# Run tests (ActivityWatch must be running)
python test_watcher.py
```

## Testing

`test_watcher.py` has two layers:

**Unit tests** — run fast, test: AW connectivity, bucket creation, heartbeat POST, state file read/write, label validation.

**Integration test** — ~3 minutes. Spawns the actual watcher subprocess, cycles through activities (65s deep-work → 65s admin-email → 25s afk), then queries AW API to verify events landed with correct durations.

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
