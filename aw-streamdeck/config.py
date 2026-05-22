import socket
from pathlib import Path

STATE_FILE = Path.home() / ".aw_state.json"
AW_BASE    = "http://localhost:5600/api/0"
HOSTNAME   = socket.gethostname()
BUCKET_ID  = f"aw-manual-streamdeck_{HOSTNAME}"
PULSE_TIME = 35
INTERVAL   = 20
