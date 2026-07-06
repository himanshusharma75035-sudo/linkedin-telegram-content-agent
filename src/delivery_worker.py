import argparse
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path

from common import ROOT_DIR, atomic_write_json, read_json
from linkedin_post import publish_text_post
from post_watchdog import check as check_post_watchdog
from telegram_send import send_message


OUTBOX_DIR = ROOT_DIR / "outbox"
SENT_DIR = ROOT_DIR / "sent"
FAILED_DIR = ROOT_DIR / "failed"
POLL_SECONDS = 60


def mark_success(message: dict, target: str, reference: str | None) -> None:
    status = message["targets"][target]
    status["delivered"] = True
    status["delivered_at"] = datetime.now(timezone.utc).isoformat()
    status["reference"] = reference
    status["last_error"] = None


def mark_failure(message: dict, target: str, error: Exception) -> None:
    status = message["targets"][target]
    status["attempts"] += 1
    status["last_error"] = str(error)


def process_message(path: Path) -> bool:
    message = read_json(path)
    text = message["text"]

    telegram = message["targets"].get("telegram")
    if telegram and not telegram["delivered"]:
        try:
            result = send_message(text)
            reference = str((result.get("result") or {}).get("message_id", ""))
            mark_success(message, "telegram", reference)
        except Exception as exc:
            mark_failure(message, "telegram", exc)
        atomic_write_json(path, message)

    linkedin = message["targets"].get("linkedin")
    if linkedin and not linkedin["delivered"]:
        try:
            mark_success(message, "linkedin", publish_text_post(text))
        except Exception as exc:
            mark_failure(message, "linkedin", exc)
        atomic_write_json(path, message)

    complete = all(target["delivered"] for target in message["targets"].values())
    if complete:
        SENT_DIR.mkdir(parents=True, exist_ok=True)
        shutil.move(str(path), SENT_DIR / path.name)
        (FAILED_DIR / path.name).unlink(missing_ok=True)
        return True

    FAILED_DIR.mkdir(parents=True, exist_ok=True)
    atomic_write_json(FAILED_DIR / path.name, message)
    return False


def process_once() -> tuple[int, int]:
    OUTBOX_DIR.mkdir(parents=True, exist_ok=True)
    sent = 0
    pending = 0
    for path in sorted(OUTBOX_DIR.glob("*.json")):
        if process_message(path):
            sent += 1
        else:
            pending += 1
    check_post_watchdog()
    return sent, pending


def main() -> int:
    parser = argparse.ArgumentParser(description="Deliver queued posts.")
    parser.add_argument("--once", action="store_true", help="Process the queue once and exit.")
    parser.add_argument("--poll-seconds", type=int, default=POLL_SECONDS)
    args = parser.parse_args()

    if args.once:
        sent, pending = process_once()
        print(f"Completed: {sent}; pending retry: {pending}")
        return 0

    print("Delivery worker is running. Press Ctrl+C to stop.")
    while True:
        try:
            sent, pending = process_once()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] Completed: {sent}; pending retry: {pending}", flush=True)
        except Exception as exc:
            print(f"Worker error: {exc}", flush=True)
        time.sleep(max(args.poll_seconds, 15))


if __name__ == "__main__":
    raise SystemExit(main())
