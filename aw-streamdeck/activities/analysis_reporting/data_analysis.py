import json
from pathlib import Path

STATE_FILE = Path.home() / ".aw_state.json"
STATE_FILE.write_text(json.dumps({"label": "Data Analysis"}), encoding="utf-8")
print("Data Analysis")