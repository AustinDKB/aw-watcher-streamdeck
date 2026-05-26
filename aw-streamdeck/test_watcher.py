"""
Test suite for aw-streamdeck watcher.
Run: python test_watcher.py
"""
import json
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

# ── paths ────────────────────────────────────────────────────────────────────
HERE    = Path(__file__).parent
WATCHER = HERE / "aw_watcher.py"
SET_ACT = HERE / "set_activity.py"
PYTHON  = sys.executable

# ── config ────────────────────────────────────────────────────────────────────
AW_BASE    = "http://localhost:5600/api/0"
HOSTNAME   = socket.gethostname()
BUCKET_ID  = f"aw-manual-streamdeck_{HOSTNAME}"
STATE_FILE = Path.home() / ".aw_state.json"

# Import activity labels from the single source of truth
sys.path.insert(0, str(HERE))
from aw_watcher import Activity

VALID_ACTIVITIES = [a.value for a in Activity]

# ── helpers ───────────────────────────────────────────────────────────────────
PASS = "\033[32mPASS\033[0m"
FAIL = "\033[31mFAIL\033[0m"
results: list[tuple[str, bool, str]] = []


def check(name: str, condition: bool, detail: str = ""):
    status = PASS if condition else FAIL
    print(f"  [{status}] {name}" + (f" - {detail}" if detail else ""))
    results.append((name, condition, detail))


def run_set_activity(label: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [PYTHON, str(SET_ACT), label],
        capture_output=True, text=True,
    )


# ── unit tests ────────────────────────────────────────────────────────────────
def test_aw_reachable():
    print("\n[Unit] AW server reachable")
    r = requests.get(f"{AW_BASE}/info", timeout=5)
    check("GET /api/0/info returns 200", r.status_code == 200, f"status={r.status_code}")


def test_bucket_creation():
    print("\n[Unit] Bucket creation")
    payload = {"client": BUCKET_ID, "type": "app.label", "hostname": HOSTNAME}
    r = requests.post(f"{AW_BASE}/buckets/{BUCKET_ID}", json=payload, timeout=5)
    check("POST bucket returns 200, 304, or 409", r.status_code in (200, 304, 409), f"status={r.status_code}")


def test_bucket_exists():
    print("\n[Unit] Bucket exists after creation")
    r = requests.get(f"{AW_BASE}/buckets/{BUCKET_ID}", timeout=5)
    check("GET bucket returns 200", r.status_code == 200, f"status={r.status_code}")


def test_heartbeat():
    print("\n[Unit] Heartbeat sends successfully")
    now = datetime.now(timezone.utc).isoformat()
    payload = {"timestamp": now, "duration": 0, "data": {"label": "unknown"}}
    r = requests.post(
        f"{AW_BASE}/buckets/{BUCKET_ID}/heartbeat?pulsetime=35",
        json=payload, timeout=5,
    )
    check("POST heartbeat returns 200", r.status_code == 200, f"status={r.status_code}")


def test_state_file_write():
    print("\n[Unit] State file write")
    result = run_set_activity("Feature Dev")
    exists = STATE_FILE.exists()
    if exists:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        correct = data.get("label") == "Feature Dev"
    else:
        correct = False
    check("State file exists after set_activity.py call", exists)
    check("State file contains correct label", correct, f"got={data if exists else 'N/A'}")


def test_state_file_read():
    print("\n[Unit] State file read")
    STATE_FILE.write_text(json.dumps({"label": "Code Review"}), encoding="utf-8")
    data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    check("State file reads correct label", data.get("label") == "Code Review", f"got={data}")


def test_invalid_label_rejected():
    print("\n[Unit] Invalid label rejected")
    result = run_set_activity("not-a-real-activity")
    check(
        "set_activity.py exits with code 1 for invalid label",
        result.returncode == 1,
        f"returncode={result.returncode}",
    )


def test_valid_labels():
    print("\n[Unit] All valid labels accepted")
    for label in VALID_ACTIVITIES:
        result = run_set_activity(label)
        ok = result.returncode == 0
        if ok:
            data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            ok = data.get("label") == label
        check(f"  label '{label}'", ok)


# ── integration test ───────────────────────────────────────────────────────────
def test_integration():
    print("\n[Integration] Full watcher sequence (~3 min)")

    proc = subprocess.Popen(
        [PYTHON, "-u", str(WATCHER)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, cwd=str(HERE),
    )
    print(f"  Watcher started (pid={proc.pid})")

    try:
        time.sleep(5)
        check("Watcher process running after 5s", proc.poll() is None)

        # Feature Dev for 65s -> 3 heartbeats at t=20,40,60 -> duration ~40s
        run_set_activity("Feature Dev")
        print("  Set Feature Dev")
        time.sleep(65)

        # Bug Fix for 65s -> 3 heartbeats -> duration ~40s
        run_set_activity("Bug Fix")
        print("  Set Bug Fix")
        time.sleep(65)

        # Research for 25s -> at least 1 heartbeat
        run_set_activity("Research")
        print("  Set Research")
        time.sleep(25)

    finally:
        proc.terminate()
        try:
            stdout, stderr = proc.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()

    print("\n  --- Watcher stdout ---")
    for line in (stdout or "").splitlines():
        print(f"  {line}")
    if stderr:
        print("  --- Watcher stderr ---")
        for line in stderr.splitlines():
            print(f"  {line}")
    print("  --- End watcher output ---\n")

    r = requests.get(
        f"{AW_BASE}/buckets/{BUCKET_ID}/events",
        params={"limit": 100},
        timeout=5,
    )
    check("AW events query returns 200", r.status_code == 200, f"status={r.status_code}")

    if r.status_code != 200:
        return

    events = r.json()
    print(f"\n  Full event log from AW ({len(events)} events):")
    for ev in events:
        dur   = ev.get("duration", 0)
        label = ev.get("data", {}).get("label", "?")
        ts    = ev.get("timestamp", "?")
        print(f"    {ts}  {label:<40} duration={dur:.1f}s")

    def max_duration(label: str) -> float:
        return max(
            (ev.get("duration", 0) for ev in events if ev.get("data", {}).get("label") == label),
            default=0.0,
        )

    feature_dur  = max_duration("Feature Dev")
    bugfix_dur   = max_duration("Bug Fix")
    research_exists = any(ev.get("data", {}).get("label") == "Research" for ev in events)

    check(
        "Feature Dev event exists with duration >= 40s",
        feature_dur >= 40,
        f"max_duration={feature_dur:.1f}s",
    )
    check(
        "Bug Fix event exists with duration >= 40s",
        bugfix_dur >= 40,
        f"max_duration={bugfix_dur:.1f}s",
    )
    check("At least one Research event exists", research_exists)


# ── main ───────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("ActivityWatch manual watcher — test suite")
    print(f"Bucket: {BUCKET_ID}")
    print("=" * 60)

    test_aw_reachable()
    test_bucket_creation()
    test_bucket_exists()
    test_heartbeat()
    test_state_file_write()
    test_state_file_read()
    test_invalid_label_rejected()
    test_valid_labels()
    test_integration()

    print("\n" + "=" * 60)
    passed = sum(1 for _, ok, _ in results if ok)
    failed = sum(1 for _, ok, _ in results if not ok)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
