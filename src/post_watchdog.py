import json
import re
from datetime import datetime, timezone
from pathlib import Path

from common import ROOT_DIR, atomic_write_json, read_json
from telegram_send import send_message


SENT_DIR = ROOT_DIR / "sent"
OUTBOX_DIR = ROOT_DIR / "outbox"
STATE_FILE = ROOT_DIR / "watchdog_state.json"
TOKEN_FILE = ROOT_DIR / "linkedin_token.json"
WATCHDOG_SLOTS = [
    {
        "key": "ai_news",
        "label": "Tuesday/Thursday AI-news LinkedIn post",
        "weekdays": {1, 3},
        "check_after": (12, 35),
        "start": (12, 0),
        "end": (14, 59, 59),
    },
    {
        "key": "finance_mw",
        "label": "Monday/Wednesday finance LinkedIn post",
        "weekdays": {0, 2},
        "check_after": (15, 35),
        "start": (15, 0),
        "end": None,
    },
]


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {"alerted": {}, "confirmed": {}, "token_alerts": {}}
    try:
        state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        state.setdefault("token_alerts", {})
        return state
    except json.JSONDecodeError:
        return {"alerted": {}, "confirmed": {}, "token_alerts": {}}


def check_token_expiry(now: datetime | None = None) -> str:
    if not TOKEN_FILE.exists():
        return "missing_token"

    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    token = read_json(TOKEN_FILE)
    expires_at = int(token.get("expires_at", 0))
    if not expires_at:
        return "unknown_expiry"

    expiry = datetime.fromtimestamp(expires_at, tz=timezone.utc)
    days_left = (expiry - now.astimezone(timezone.utc)).total_seconds() / 86400
    if days_left > 7:
        return "valid"

    level = "expired" if days_left <= 0 else "seven_day_warning"
    state = load_state()
    alert_key = f"{expires_at}:{level}"
    if alert_key in state["token_alerts"]:
        return "already_alerted"

    if level == "expired":
        message = (
            "LinkedIn automation alert: the access token expired. "
            "Run `python src/linkedin_oauth.py` before the next scheduled post."
        )
    else:
        message = (
            f"LinkedIn automation warning: the access token expires on "
            f"{expiry.astimezone().strftime('%d %b %Y, %I:%M %p')}. "
            "Run `python src/linkedin_oauth.py` this week."
        )
    send_message(message)
    state["token_alerts"][alert_key] = now.isoformat()
    atomic_write_json(STATE_FILE, state)
    return level


def artifact_in_slot(path: Path, date_key: str, slot: dict) -> bool:
    match = re.search(rf"{date_key}-(\d{{6}})", path.name)
    if not match:
        return False
    timestamp = int(match.group(1))
    start_hour, start_minute = slot["start"]
    start = start_hour * 10000 + start_minute * 100
    if timestamp < start:
        return False
    if slot["end"]:
        end_hour, end_minute, end_second = slot["end"]
        end = end_hour * 10000 + end_minute * 100 + end_second
        if timestamp > end:
            return False
    return True


def slot_due(slot: dict, now: datetime) -> bool:
    weekdays = slot["weekdays"]
    if weekdays is not None and now.weekday() not in weekdays:
        return False
    return (now.hour, now.minute) >= slot["check_after"]


def check_slot(slot: dict, now: datetime, state: dict) -> str:
    date_key = now.strftime("%Y%m%d")
    state_key = f"{slot['key']}:{date_key}"
    sent_files = [
        path
        for path in SENT_DIR.glob(f"{date_key}-*.json")
        if artifact_in_slot(path, date_key, slot)
    ]
    if sent_files:
        if state_key not in state["confirmed"]:
            state["confirmed"][state_key] = now.isoformat()
            if state_key in state["alerted"]:
                send_message(
                    f"LinkedIn automation recovery confirmed: {slot['label']} is now published."
                )
            atomic_write_json(STATE_FILE, state)
        return "confirmed"

    if state_key in state["alerted"]:
        return "already_alerted"

    pending_files = [
        path
        for path in OUTBOX_DIR.glob(f"{date_key}-*.json")
        if artifact_in_slot(path, date_key, slot)
    ]
    check_hour, check_minute = slot["check_after"]
    check_time = f"{check_hour:02d}:{check_minute:02d}"
    if pending_files:
        message = (
            f"LinkedIn automation alert: {slot['label']} is queued but not "
            f"confirmed as published by {check_time}. The worker will keep retrying."
        )
        result = "pending"
    else:
        message = (
            f"LinkedIn automation alert: no {slot['label']} artifact was found by "
            f"{check_time} after the primary and recovery schedules."
        )
        result = "missing"

    send_message(message)
    state["alerted"][state_key] = now.isoformat()
    atomic_write_json(STATE_FILE, state)
    return result


def check(now: datetime | None = None) -> str:
    now = now or datetime.now().astimezone()
    state = load_state()
    results = [
        check_slot(slot, now, state)
        for slot in WATCHDOG_SLOTS
        if slot_due(slot, now)
    ]
    if not results:
        return "not_due"
    if any(result in {"missing", "pending"} for result in results):
        return "alerted"
    if any(result == "confirmed" for result in results):
        return "confirmed"
    return results[-1]
