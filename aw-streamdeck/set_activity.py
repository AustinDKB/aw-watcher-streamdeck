import json
import sys
from pathlib import Path

VALID_ACTIVITIES = {
    "Pipeline Development",
    "API Integration",
    "ML / Data Quality Systems",
    "HTML / Document Templates",
    "Tool / Utility Development",
    "ETL Planning, Design & Architecture",
    "Unit Configuration",
    "Data Validation & Cleaning",
    "Data Migration & Remediation",
    "Pipeline Monitoring & Testing",
    "Layout Configuration",
    "Entity Configuration (Editing / Creating)",
    "Data Integrity Monitoring",
    "User Support & Troubleshooting",
    "Creating Reports",
    "Dues Processing",
    "International Reporting",
    "Seniority List Management",
    "Email Triage",
    "Email Follow-up",
    "Documentation / Systems Writing",
    "Environment Management",
    "Running a CRM Backup",
    "Leadership Reporting",
    "Data Analysis",
    "Research",
    "Staff Training",
    "Documentation for Non-Technical Users",
    "Stakeholder Education",
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
