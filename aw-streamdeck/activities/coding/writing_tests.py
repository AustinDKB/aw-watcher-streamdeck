import json
from pathlib import Path

STATE_FILE = Path.home() / ".aw_state.json"
STATE_FILE.write_text(json.dumps({"label": "Writing Tests"}), encoding="utf-8")
print("Writing Tests")
