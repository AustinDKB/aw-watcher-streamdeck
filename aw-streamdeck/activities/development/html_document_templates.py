import json
from pathlib import Path

STATE_FILE = Path.home() / ".aw_state.json"
STATE_FILE.write_text(json.dumps({"label": "HTML / Document Templates"}), encoding="utf-8")
print("HTML / Document Templates")