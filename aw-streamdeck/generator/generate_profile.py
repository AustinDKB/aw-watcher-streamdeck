#!/usr/bin/env python3
"""
generate_profile.py — Builds a Stream Deck ProfilesV3 profile for AW activities.

Edit USER CONFIG below, then run from the aw-streamdeck directory:
    python generator/generate_profile.py

Restart Stream Deck software after running. Switch to "AW Activities" in the profiles list.
Requires: Python 3.8+, Pillow (pip install pillow)
"""

import json
import os
import sys
import uuid
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Pillow required: pip install pillow")

# ─── USER CONFIG ──────────────────────────────────────────────────────────────
# Set INSTALL_DIR to the aw-streamdeck folder (parent of generator/)
INSTALL_DIR  = r"C:\Users\<YOU>\stream-deck-watcher\aw-streamdeck"
VENV_EXE     = r"C:\Users\<YOU>\AppData\Local\Programs\Python\Python312\pythonw.exe"
SCRIPTS_DIR  = rf"{INSTALL_DIR}\activities"
PROFILE_NAME = "AW Activities"

# Top 6 buttons on the main page (quick-access shortcuts)
TOP_6 = [
    ("Feature\nDev",     "coding/feature_dev.py",          "\U0001f4bb"),  # 0,0
    ("Bug\nFix",         "coding/bug_fix.py",              "\U0001f41b"),  # 1,0
    ("Code\nReview",     "coding/code_review.py",          "\U0001f50d"),  # 0,1
    ("Sprint\nPlan",     "planning/sprint_planning.py",    "\U0001f4cb"),  # 1,1
    ("Team\nMeeting",    "communication/team_meeting.py",  "\U0001f465"),  # 0,2
    ("Research",         "planning/research.py",           "\U0001f52c"),  # 1,2
]

# Each category: (short_name, full_name, folder_name, [(button_label, script_file), ...])
# short_name is used as the style key for icon colors — keep unique.
CATEGORIES = [
    ("Coding",  "Coding",        "coding", [
        ("Feature\nDev",    "feature_dev.py"),
        ("Bug\nFix",        "bug_fix.py"),
        ("Code\nReview",    "code_review.py"),
        ("Refactor",        "refactoring.py"),
        ("Write\nTests",    "writing_tests.py"),
    ]),
    ("DevOps",  "DevOps",        "devops", [
        ("CI/CD\nPipeline", "ci_cd_pipeline.py"),
        ("Deploy",          "deployment.py"),
        ("Monitor",         "monitoring.py"),
        ("Infra",           "infrastructure.py"),
    ]),
    ("Plan",    "Planning",      "planning", [
        ("Sprint\nPlan",    "sprint_planning.py"),
        ("Arch\nDesign",    "architecture_design.py"),
        ("Research",        "research.py"),
        ("Tasks",           "task_management.py"),
    ]),
    ("Comms",   "Communication", "communication", [
        ("Team\nMeeting",   "team_meeting.py"),
        ("1:1",             "one_on_one.py"),
        ("Client\nMtg",     "client_meeting.py"),
        ("Async\nComms",    "async_comms.py"),
    ]),
    ("Learn",   "Learning",      "learning", [
        ("Read\nDocs",      "reading_docs.py"),
        ("Tutorial",        "tutorial_course.py"),
        ("Experiment",      "experimenting.py"),
    ]),
    ("Admin",   "Admin",         "admin", [
        ("Reports",         "reports_metrics.py"),
        ("Time\nTrack",     "time_tracking.py"),
        ("Admin\nEmail",    "admin_email.py"),
    ]),
]
# ──────────────────────────────────────────────────────────────────────────────

PROFILES_DIR = Path(os.environ["APPDATA"]) / "Elgato" / "StreamDeck" / "ProfilesV3"

PLUGIN_UUID = "com.nicoohagedorn.pythonscriptdeck.script"
FOLDER_UUID = "com.elgato.streamdeck.profile.openchild"
BACK_UUID   = "com.elgato.streamdeck.profile.backtoparent"
AFK_SCRIPT  = Path(SCRIPTS_DIR) / "afk.py"

FOLDER_POSITIONS = [(2,0),(3,0),(4,0),(2,1),(3,1),(4,1)]
AFK_POSITION     = (2, 2)

CATEGORY_STYLE = {
    "Coding":  ("#1A2E50", "#6A9BD4", "\U0001f4bb"),   # navy / steel blue
    "DevOps":  ("#1A3020", "#6ABD8A", "\u2699"),        # dark green / mint
    "Plan":    ("#2E2010", "#D4A06A", "\U0001f4cb"),    # dark amber / tan
    "Comms":   ("#2E1A40", "#B06AD4", "\U0001f4ac"),    # dark violet / lavender
    "Learn":   ("#301A10", "#D47A6A", "\U0001f4d6"),    # dark rust / salmon
    "Admin":   ("#1A1A2E", "#6A6ABD", "\U0001f4c4"),    # dark indigo / periwinkle
    "Top6":    ("#3D1866", "#E8B72C", "\u2605"),        # deep purple / gold
    "AFK":     ("#1A1A1A", "#4A4A4A", "\U0001f4a4"),    # near black / gray
}


def _id() -> str:
    return str(uuid.uuid4())


def _fwd(p) -> str:
    return str(p).replace("\\", "/")


def _make_icon(emoji: str, bg: str) -> Image.Image:
    img  = Image.new("RGB", (288, 288), bg)
    draw = ImageDraw.Draw(img)

    try:
        em_font = ImageFont.truetype("seguiemj.ttf", 96)
    except OSError:
        try:
            em_font = ImageFont.truetype("seguisym.ttf", 96)
        except OSError:
            em_font = ImageFont.load_default()

    draw.text((144, 120), emoji, font=em_font, anchor="mm", embedded_color=True)
    return img


def _save_icon(action: dict, page_dir: Path, slot: str,
               _label: str, style_key: str, emoji_override: str | None = None) -> None:
    bg, _accent, emoji = CATEGORY_STYLE.get(style_key, ("#1a1a2e", "#ffffff", "\u25b6"))
    if emoji_override:
        emoji = emoji_override
    img = _make_icon(emoji, bg)
    images_dir = page_dir / "Images"
    images_dir.mkdir(parents=True, exist_ok=True)
    fname = f"{slot.replace(',', '_')}.png"
    img.save(images_dir / fname)
    action["States"][0]["Image"] = f"Images/{fname}"
    action["States"][0]["TitleColor"] = "#ffffff"


def _script_action(title: str, script_path) -> dict:
    return {
        "ActionID": _id(),
        "LinkedTitle": True,
        "Name": "Run Script",
        "Plugin": {
            "Name": "PythonScriptDeck",
            "UUID": "com.nicoohagedorn.pythonscriptdeck",
            "Version": "0.5.0.2",
        },
        "Resources": None,
        "Settings": {
            "path": _fwd(script_path),
            "useVenv": False,
            "venvPath": "",
        },
        "State": 0,
        "States": [{
            "FontFamily": "",
            "FontSize": 12,
            "FontStyle": "Normal",
            "FontUnderline": False,
            "OutlineThickness": 0,
            "ShowTitle": True,
            "Title": title,
            "TitleAlignment": "bottom",
            "TitleColor": "#ffffff",
        }],
        "UUID": PLUGIN_UUID,
    }


def _folder_action(title: str, child_guid: str) -> dict:
    return {
        "ActionID": _id(),
        "LinkedTitle": True,
        "Name": "Create Folder",
        "Plugin": {
            "Name": "Create Folder",
            "UUID": FOLDER_UUID,
            "Version": "1.0",
        },
        "Resources": None,
        "Settings": {"ProfileUUID": child_guid.lower()},
        "State": 0,
        "States": [{
            "FontFamily": "",
            "FontSize": 12,
            "FontStyle": "Normal",
            "FontUnderline": False,
            "ShowTitle": True,
            "Title": title,
            "TitleAlignment": "bottom",
            "TitleColor": "#ffffff",
        }],
        "UUID": FOLDER_UUID,
    }


def _back_action() -> dict:
    return {
        "ActionID": _id(),
        "LinkedTitle": True,
        "Name": "Parent Folder",
        "Plugin": {
            "Name": "Open Parent Folder",
            "UUID": BACK_UUID,
            "Version": "1.0",
        },
        "Resources": None,
        "Settings": {},
        "State": 0,
        "States": [{}],
        "UUID": BACK_UUID,
    }


def _page_manifest(actions: dict) -> dict:
    return {
        "Controllers": [{"Actions": actions if actions else None, "Type": "Keypad"}],
        "Icon": "",
        "Name": "",
    }


def _write_page(profile_dir: Path, page_guid: str, actions: dict) -> None:
    page_dir = profile_dir / "Profiles" / page_guid.upper()
    page_dir.mkdir(parents=True, exist_ok=True)
    (page_dir / "manifest.json").write_text(
        json.dumps(_page_manifest(actions), separators=(",", ":")),
        encoding="utf-8",
    )


def _detect_device() -> dict:
    if not PROFILES_DIR.exists():
        return {}
    for p in PROFILES_DIR.iterdir():
        m = p / "manifest.json"
        if m.exists():
            try:
                return json.loads(m.read_text(encoding="utf-8")).get("Device", {})
            except Exception:
                pass
    return {}


def build_profile() -> Path:
    profile_guid   = str(uuid.uuid4()).upper()
    main_page_guid = str(uuid.uuid4())
    profile_dir    = PROFILES_DIR / f"{profile_guid}.sdProfile"
    profile_dir.mkdir(parents=True, exist_ok=True)
    (profile_dir / "Profiles").mkdir(exist_ok=True)

    # ── Sub-pages ─────────────────────────────────────────────────────────────
    cat_guids: dict[str, str] = {}

    for short_name, full_name, cat_dir, activities in CATEGORIES:
        cat_guid = str(uuid.uuid4())
        cat_guids[short_name] = cat_guid

        actions: dict = {"4,2": _back_action()}
        all_slots = [
            f"{c},{r}" for r in range(3) for c in range(5) if (c, r) != (4, 2)
        ]
        page_dir = profile_dir / "Profiles" / cat_guid.upper()

        for slot, (act_title, act_file) in zip(all_slots, activities):
            script = Path(SCRIPTS_DIR) / cat_dir / act_file
            act = _script_action(act_title, script)
            _save_icon(act, page_dir, slot, act_title, short_name)
            actions[slot] = act

        _write_page(profile_dir, cat_guid, actions)
        print(f"  [{short_name}] -> {cat_guid}")

    # ── Main page ──────────────────────────────────────────────────────────────
    main_actions: dict = {}
    top6_slots    = ["0,0", "1,0", "0,1", "1,1", "0,2", "1,2"]
    main_page_dir = profile_dir / "Profiles" / main_page_guid.upper()

    for slot, (title, script_rel, emoji) in zip(top6_slots, TOP_6):
        script = Path(SCRIPTS_DIR) / script_rel
        act = _script_action(title, script)
        _save_icon(act, main_page_dir, slot, title, "Top6", emoji)
        main_actions[slot] = act

    for (col, row), (short_name, *_) in zip(FOLDER_POSITIONS, CATEGORIES):
        slot = f"{col},{row}"
        fold = _folder_action(short_name, cat_guids[short_name])
        _save_icon(fold, main_page_dir, slot, short_name, short_name)
        main_actions[slot] = fold

    afk_slot = f"{AFK_POSITION[0]},{AFK_POSITION[1]}"
    afk = _script_action("AFK", AFK_SCRIPT)
    _save_icon(afk, main_page_dir, afk_slot, "AFK", "AFK")
    main_actions[afk_slot] = afk

    _write_page(profile_dir, main_page_guid, main_actions)

    # ── Default page (empty — SD requires Default != Current) ─────────────────
    default_page_guid = str(uuid.uuid4())
    _write_page(profile_dir, default_page_guid, {})

    # ── Top-level manifest ────────────────────────────────────────────────────
    top = {
        "Device": _detect_device(),
        "Name": PROFILE_NAME,
        "Pages": {
            "Current": main_page_guid.lower(),
            "Default": default_page_guid.lower(),
            "Pages": [main_page_guid.lower()],
        },
        "Version": "3.0",
    }
    (profile_dir / "manifest.json").write_text(
        json.dumps(top, separators=(",", ":")), encoding="utf-8"
    )

    print(f"\nProfile written: {profile_dir}")
    print("-> Restart Stream Deck, then select 'AW Activities' in Profiles.")
    return profile_dir


if __name__ == "__main__":
    build_profile()
