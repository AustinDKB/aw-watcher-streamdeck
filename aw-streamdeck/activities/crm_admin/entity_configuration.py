import json
from pathlib import Path

STATE_FILE = Path.home() / ".aw_state.json"
STATE_FILE.write_text(json.dumps({"label": "Entity Configuration (Editing / Creating)"}), encoding="utf-8")
print("Entity Configuration (Editing / Creating)")