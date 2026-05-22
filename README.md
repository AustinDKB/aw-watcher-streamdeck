# aw-watcher-streamdeck

Manual activity tracker bridging Elgato Stream Deck → ActivityWatch.

Press a button → writes activity to `~/.aw_state.json` → background watcher polls every 20s → heartbeats sent to ActivityWatch API → timeline updated.

See [aw-streamdeck/SETUP_GUIDE.md](aw-streamdeck/SETUP_GUIDE.md) for full setup, Stream Deck wiring, and deployment instructions.
See [aw-streamdeck/TEST_PLAN.md](aw-streamdeck/TEST_PLAN.md) for the complete test checklist.

---

## Quick start

```bash
cd aw-streamdeck
python -m venv .venv
.venv\Scripts\activate
pip install aw-client
python aw_watcher.py
```

## Run tests

```bash
cd aw-streamdeck
python test_watcher.py   # requires ActivityWatch running at localhost:5600
```

Tests cover all 29 activities across 7 categories plus a full end-to-end integration test.
