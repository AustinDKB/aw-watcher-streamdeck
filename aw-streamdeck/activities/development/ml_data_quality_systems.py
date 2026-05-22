import json
from pathlib import Path

STATE_FILE = Path.home() / ".aw_state.json"
STATE_FILE.write_text(json.dumps({"label": "ML / Data Quality Systems"}), encoding="utf-8")
print("ML / Data Quality Systems")