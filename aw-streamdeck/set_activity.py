import json
import sys
from pathlib import Path

VALID_ACTIVITIES = {
    # Coding
    "Feature Dev",
    "Bug Fix",
    "Code Review",
    "Refactoring",
    "Writing Tests",
    # DevOps
    "CI/CD Pipeline",
    "Deployment",
    "Monitoring",
    "Infrastructure",
    # Planning
    "Sprint Planning",
    "Architecture Design",
    "Research",
    "Task Management",
    # Communication
    "Team Meeting",
    "One-on-One",
    "Client Meeting",
    "Async Comms",
    # Learning
    "Reading Docs",
    "Tutorial / Course",
    "Experimenting",
    # Admin
    "Reports & Metrics",
    "Time Tracking",
    "Admin Email",
    "unknown",
}

STATE_FILE = Path.home() / ".aw_state.json"


def main():
    if len(sys.argv) < 2:
        print("Usage: python set_activity.py <activity>", file=sys.stderr)
        print(f"Valid activities: {', '.join(sorted(VALID_ACTIVITIES))}", file=sys.stderr)
        sys.exit(1)

    label = sys.argv[1].strip()

    if label not in VALID_ACTIVITIES:
        print(f"Error: '{label}' is not a valid activity.", file=sys.stderr)
        print(f"Valid activities: {', '.join(sorted(VALID_ACTIVITIES))}", file=sys.stderr)
        sys.exit(1)

    STATE_FILE.write_text(json.dumps({"label": label}), encoding="utf-8")
    print(f"Activity set to: {label}")


if __name__ == "__main__":
    main()
