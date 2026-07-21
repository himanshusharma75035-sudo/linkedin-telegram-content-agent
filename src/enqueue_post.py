import argparse
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from common import ROOT_DIR, atomic_write_json


OUTBOX_DIR = ROOT_DIR / "outbox"
DEFAULT_IMAGE_ALT_TEXT = "AI-generated finance workflow visual for this LinkedIn post."


def maybe_generate_finance_image(text: str, message_id: str) -> str | None:
    try:
        from generate_finance_image import generate_finance_image

        path = generate_finance_image(text, message_id)
        return str(path.resolve()) if path else None
    except Exception as exc:
        print(f"Finance image generation skipped: {exc}", file=sys.stderr)
        return None


def build_message_id() -> str:
    return f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"


def enqueue(
    text: str,
    targets: list[str],
    image_path: str | None = None,
    image_alt_text: str | None = None,
    message_id: str | None = None,
) -> str:
    message_id = message_id or build_message_id()
    path = OUTBOX_DIR / f"{message_id}.json"
    atomic_write_json(
        path,
        {
            "id": message_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "text": text,
            "image_path": image_path,
            "image_alt_text": image_alt_text,
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
    parser.add_argument("--image", help="Attach an existing image path to the LinkedIn post.")
    parser.add_argument(
        "--finance-image",
        action="store_true",
        help="Generate and attach an AI image for finance-track LinkedIn posts.",
    )
    args = parser.parse_args()

    text = " ".join(args.message).strip() or sys.stdin.read().strip()
    if not text:
        print("Post is empty.", file=sys.stderr)
        return 2
    if len(text) > 3000:
        print("Post exceeds 3,000 characters.", file=sys.stderr)
        return 2

    image_path = args.image
    message_id = build_message_id()
    if args.finance_image:
        image_path = maybe_generate_finance_image(text, message_id) or image_path
    if image_path:
        image_path = str(Path(os.path.expandvars(image_path)).expanduser().resolve())

    message_id = enqueue(
        text,
        list(dict.fromkeys(args.targets)),
        image_path=image_path,
        image_alt_text=DEFAULT_IMAGE_ALT_TEXT if image_path else None,
        message_id=message_id,
    )
    print(f"Queued post: {message_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
