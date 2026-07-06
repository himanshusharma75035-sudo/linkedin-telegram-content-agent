import json
from datetime import datetime

from common import ROOT_DIR, atomic_write_json
from telegram_send import send_message


SENT_DIR = ROOT_DIR / "sent"
OUTBOX_DIR = ROOT_DIR / "outbox"
STATE_FILE = ROOT_DIR / "watchdog_state.json"
POST_WEEKDAYS = {0, 2}
CHECK_AFTER = (12, 35)


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {"alerted": {}, "confirmed": {}}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"alerted": {}, "confirmed": {}}


def check(now: datetime | None = None) -> str:
    now = now or datetime.now().astimezone()
    if now.weekday() not in POST_WEEKDAYS or (now.hour, now.minute) < CHECK_AFTER:
        return "not_due"

    date_key = now.strftime("%Y%m%d")
    state = load_state()
    sent_files = list(SENT_DIR.glob(f"{date_key}-*.json"))
    if sent_files:
        if date_key not in state["confirmed"]:
            state["confirmed"][date_key] = now.isoformat()
            if date_key in state["alerted"]:
                send_message(
                    "LinkedIn automation recovery confirmed: today's post is now published."
                )
            atomic_write_json(STATE_FILE, state)
        return "confirmed"

    if date_key in state["alerted"]:
        return "already_alerted"

    pending_files = list(OUTBOX_DIR.glob(f"{date_key}-*.json"))
    if pending_files:
        message = (
            "LinkedIn automation alert: today's post is queued but not confirmed "
            "as published by 12:35 PM. The worker will keep retrying."
        )
        result = "pending"
    else:
        message = (
            "LinkedIn automation alert: no post artifact was found by 12:35 PM "
            "after the primary and recovery schedules."
        )
        result = "missing"

    send_message(message)
    state["alerted"][date_key] = now.isoformat()
    atomic_write_json(STATE_FILE, state)
    return result
