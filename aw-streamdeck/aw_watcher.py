"""AW-StreamDeck manual activity watcher for ActivityWatch."""

import logging
import os
import time
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
import json

from aw_client import ActivityWatchClient
from aw_core.models import Event

from config import BUCKET_ID, HOSTNAME, INTERVAL, PULSE_TIME, STATE_FILE

LOG_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "activitywatch" / "activitywatch" / "Logs" / "aw-streamdeck"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "aw-streamdeck.log"

logger = logging.getLogger("aw-streamdeck")
logger.setLevel(logging.INFO)
_file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
_file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s"))
logger.addHandler(_file_handler)


class Activity(str, Enum):
    PIPELINE_DEVELOPMENT               = "Pipeline Development"
    API_INTEGRATION                    = "API Integration"
    ML_DATA_QUALITY_SYSTEMS            = "ML / Data Quality Systems"
    HTML_DOCUMENT_TEMPLATES            = "HTML / Document Templates"
    TOOL_UTILITY_DEVELOPMENT           = "Tool / Utility Development"
    ETL_PLANNING_DESIGN_ARCHITECTURE   = "ETL Planning, Design & Architecture"
    UNIT_CONFIGURATION                 = "Unit Configuration"
    DATA_VALIDATION_CLEANING           = "Data Validation & Cleaning"
    DATA_MIGRATION_REMEDIATION         = "Data Migration & Remediation"
    PIPELINE_MONITORING_TESTING        = "Pipeline Monitoring & Testing"
    LAYOUT_CONFIGURATION               = "Layout Configuration"
    ENTITY_CONFIGURATION               = "Entity Configuration (Editing / Creating)"
    DATA_INTEGRITY_MONITORING          = "Data Integrity Monitoring"
    USER_SUPPORT_TROUBLESHOOTING       = "User Support & Troubleshooting"
    CREATING_REPORTS                   = "Creating Reports"
    DUES_PROCESSING                    = "Dues Processing"
    INTERNATIONAL_REPORTING            = "International Reporting"
    SENIORITY_LIST_MANAGEMENT          = "Seniority List Management"
    EMAIL_TRIAGE                       = "Email Triage"
    EMAIL_FOLLOW_UP                    = "Email Follow-up"
    DOCUMENTATION_SYSTEMS_WRITING      = "Documentation / Systems Writing"
    ENVIRONMENT_MANAGEMENT             = "Environment Management"
    RUNNING_A_CRM_BACKUP               = "Running a CRM Backup"
    LEADERSHIP_REPORTING               = "Leadership Reporting"
    DATA_ANALYSIS                      = "Data Analysis"
    RESEARCH                           = "Research"
    STAFF_TRAINING                     = "Staff Training"
    DOCUMENTATION_NON_TECHNICAL        = "Documentation for Non-Technical Users"
    STAKEHOLDER_EDUCATION              = "Stakeholder Education"
    UNKNOWN                            = "unknown"


def reset_state():
    STATE_FILE.write_text(json.dumps({"label": Activity.UNKNOWN.value}), encoding="utf-8")


def read_state() -> str:
    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        label = data.get("label", Activity.UNKNOWN.value)
        if label not in [a.value for a in Activity]:
            logger.warning("unknown label in state file: %s", label)
            return Activity.UNKNOWN.value
        return label
    except FileNotFoundError:
        logger.warning("state file not found, resetting to unknown")
        return Activity.UNKNOWN.value
    except Exception as e:
        logger.warning("failed to read state file: %s", e)
        return Activity.UNKNOWN.value


def main():
    client = ActivityWatchClient("aw-streamdeck", host="localhost", port=5600)
    client.create_bucket(BUCKET_ID, event_type="app.label")

    if not STATE_FILE.exists():
        reset_state()
    logger.info("Watcher started")

    current_label = read_state()
    label_since   = time.monotonic()

    while True:
        try:
            time.sleep(INTERVAL)
            new_label = read_state()

            if new_label != current_label:
                elapsed       = int(time.monotonic() - label_since)
                prev_label    = current_label
                current_label = new_label
                label_since   = time.monotonic()
                logger.info("%s -> %s  (%ds)", prev_label, current_label, elapsed)

            event = Event(
                timestamp=datetime.now(timezone.utc),
                duration=timedelta(0),
                data={"label": current_label},
            )
            client.heartbeat(BUCKET_ID, event, pulsetime=PULSE_TIME)
            logger.debug("heartbeat sent: %s", current_label)

        except KeyboardInterrupt:
            logger.info("Watcher stopped")
            break
        except Exception as e:
            logger.error("unexpected: %s", e)


if __name__ == "__main__":
    main()
