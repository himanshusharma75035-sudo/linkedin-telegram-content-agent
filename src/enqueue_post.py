import argparse
import sys
import uuid
from datetime import datetime, timezone

from common import ROOT_DIR, atomic_write_json


OUTBOX_DIR = ROOT_DIR / "outbox"


def enqueue(text: str, targets: list[str]) -> str:
    message_id = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"
    path = OUTBOX_DIR / f"{message_id}.json"
    atomic_write_json(
        path,
        {
            "id": message_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "text": text,
            "targets": {
                target: {
                    "delivered": False,
                    "delivered_at": None,
                    "reference": None,
                    "attempts": 0,
                    "last_error": None,
                }
                for target in targets
            },
        },
    )
    return message_id


def main() -> int:
    parser = argparse.ArgumentParser(description="Queue one post for delivery.")
    parser.add_argument("message", nargs="*", help="Post text; reads stdin if omitted.")
    parser.add_argument(
        "--targets",
        nargs="+",
        choices=["telegram", "linkedin"],
        default=["telegram", "linkedin"],
    )
    args = parser.parse_args()

    text = " ".join(args.message).strip() or sys.stdin.read().strip()
    if not text:
        print("Post is empty.", file=sys.stderr)
        return 2
    if len(text) > 3000:
        print("Post exceeds 3,000 characters.", file=sys.stderr)
        return 2

    message_id = enqueue(text, list(dict.fromkeys(args.targets)))
    print(f"Queued post: {message_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
