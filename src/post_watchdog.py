import json
from datetime import datetime, timezone

from common import ROOT_DIR, atomic_write_json, read_json
from telegram_send import send_message


SENT_DIR = ROOT_DIR / "sent"
OUTBOX_DIR = ROOT_DIR / "outbox"
STATE_FILE = ROOT_DIR / "watchdog_state.json"
TOKEN_FILE = ROOT_DIR / "linkedin_token.json"
POST_WEEKDAYS = {0, 2}
CHECK_AFTER = (12, 35)


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
