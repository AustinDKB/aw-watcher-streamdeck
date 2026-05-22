import json
from pathlib import Path

STATE_FILE = Path.home() / ".aw_state.json"
STATE_FILE.write_text(json.dumps({"label": "Layout Configuration"}), encoding="utf-8")
print("Layout Configuration")