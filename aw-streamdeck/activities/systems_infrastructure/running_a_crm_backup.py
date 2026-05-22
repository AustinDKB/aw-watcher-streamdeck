import json
from pathlib import Path

STATE_FILE = Path.home() / ".aw_state.json"
STATE_FILE.write_text(json.dumps({"label": "Running a CRM Backup"}), encoding="utf-8")
print("Running a CRM Backup")