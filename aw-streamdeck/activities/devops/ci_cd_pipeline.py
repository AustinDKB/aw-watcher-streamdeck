import json
from pathlib import Path

STATE_FILE = Path.home() / ".aw_state.json"
STATE_FILE.write_text(json.dumps({"label": "CI/CD Pipeline"}), encoding="utf-8")
print("CI/CD Pipeline")
