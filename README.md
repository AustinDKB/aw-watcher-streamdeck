# aw-watcher-streamdeck

Track what you're working on by pressing a button on your Elgato Stream Deck. Each button press logs your current activity to [ActivityWatch](https://activitywatch.net/), giving you an automatic timeline of your day without lifting a finger.

---

## How it works

```
Stream Deck button press
        |
        v
[PythonScriptDeck plugin]
        |
        v
activities/<category>/<name>.py  →  writes label to ~/.aw_state.json
                                              |
                                              v  (polls every 20s)
                                       aw-streamdeck.exe
                                              |
                                              v
                                    POST heartbeat to ActivityWatch
                                    localhost:5600/api/0
                                    bucket: aw-manual-streamdeck_<hostname>
                                              |
                                              v
                                    ActivityWatch Timeline
```

The state machine is a single JSON file (`~/.aw_state.json`). No database, no queue, no IPC — just a file write and a poll loop.

---

## Repository structure

```
stream-deck-watcher/
└── aw-streamdeck/
    ├── aw_watcher.py        # Background daemon — polls state file, sends heartbeats
    ├── config.py            # Constants (bucket ID, intervals, file paths)
    ├── set_activity.py      # CLI tool: python set_activity.py "Feature Dev"
    ├── test_watcher.py      # Unit + integration tests
    ├── requirements.txt     # pip deps (aw-client)
    ├── activities/          # One .py file per activity, organized by category
    │   ├── coding/
    │   ├── devops/
    │   ├── planning/
    │   ├── communication/
    │   ├── learning/
    │   ├── admin/
    │   └── afk.py
    └── generator/           # Stream Deck profile builder (run once to set up buttons)
        └── generate_profile.py
```

---

## Quick start

```powershell
# 1. Clone
git clone https://github.com/<YOU>/stream-deck-watcher C:\Users\<YOU>\stream-deck-watcher

# 2. Install watcher deps
cd aw-streamdeck
python -m venv .venv
.venv\Scripts\activate
pip install aw-client

# 3. Run the watcher (keep this process running)
python aw_watcher.py

# 4. Set an activity from terminal to test
python set_activity.py "Feature Dev"
```

For full setup (Stream Deck profile generation, exe build, aw-qt integration) see the detailed guide below.

---

## Documentation

| Doc | Description |
|-----|-------------|
| [aw-streamdeck/SETUP_GUIDE.md](aw-streamdeck/SETUP_GUIDE.md) | Full 9-step setup: prerequisites → Stream Deck profile → verification |
| [aw-streamdeck/README.md](aw-streamdeck/README.md) | Activity categories, customization guide, project structure |
| [AGENT.md](AGENT.md) | Architecture reference for AI-assisted development |

---

## Run tests

```powershell
cd aw-streamdeck
python test_watcher.py   # requires ActivityWatch running at localhost:5600
```

---

## Customize for your workflow

The default activities are a generic developer template. Fork this repo and edit three files to make it yours:

1. **`activities/<category>/<name>.py`** — one file per activity (6 lines each)
2. **`aw_watcher.py`** — add entries to the `Activity` enum
3. **`set_activity.py`** — add strings to `VALID_ACTIVITIES`

Then regenerate the Stream Deck profile:

```powershell
pip install pillow
python generator/generate_profile.py
```

See [SETUP_GUIDE.md § Step 3](aw-streamdeck/SETUP_GUIDE.md) for the full customization walkthrough.
