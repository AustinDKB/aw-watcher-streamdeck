import json
from pathlib import Path

STATE_FILE = Path.home() / ".aw_state.json"
STATE_FILE.write_text(json.dumps({"label": "User Support & Troubleshooting"}), encoding="utf-8")
print("User Support & Troubleshooting")