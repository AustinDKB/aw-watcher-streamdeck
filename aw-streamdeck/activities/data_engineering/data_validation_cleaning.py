import json
from pathlib import Path

STATE_FILE = Path.home() / ".aw_state.json"
STATE_FILE.write_text(json.dumps({"label": "Data Validation & Cleaning"}), encoding="utf-8")
print("Data Validation & Cleaning")