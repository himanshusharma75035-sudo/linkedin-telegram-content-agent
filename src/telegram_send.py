import argparse
import json
import os
import sys
import urllib.parse
import urllib.request

from common import ROOT_DIR, load_env_file


ENV_FILE = ROOT_DIR / "telegram.env"


def telegram_request(method: str, values: dict | None = None) -> dict:
    load_env_file(ENV_FILE)
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("telegram.env must define TELEGRAM_BOT_TOKEN.")

    url = f"https://api.telegram.org/bot{token}/{method}"
    data = urllib.parse.urlencode(values).encode("utf-8") if values else None
    request = urllib.request.Request(url, data=data, method="POST" if data else "GET")
    with urllib.request.urlopen(request, timeout=30) as response:
        body = json.loads(response.read().decode("utf-8"))
    if not body.get("ok"):
        raise RuntimeError(f"Telegram API error: {body}")
    return body


def send_message(text: str) -> dict:
    load_env_file(ENV_FILE)
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not chat_id or chat_id.startswith("replace_"):
        raise RuntimeError("telegram.env must define TELEGRAM_CHAT_ID.")
    return telegram_request(
        "sendMessage",
        {
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": "true",
        },
    )


def print_updates() -> None:
    body = telegram_request("getUpdates")
    found = set()
    for update in body.get("result", []):
        message = update.get("message") or update.get("channel_post") or {}
        chat = message.get("chat") or {}
        chat_id = chat.get("id")
        if chat_id is None or chat_id in found:
            continue
        found.add(chat_id)
        label = chat.get("title") or chat.get("username") or chat.get("first_name") or ""
        print(f"chat_id={chat_id} type={chat.get('type', '')} name={label}")
    if not found:
        print("No chats found. Send /start to the bot, then run this command again.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Send a Telegram bot message.")
    parser.add_argument("message", nargs="*", help="Message text; reads stdin if omitted.")
    parser.add_argument("--get-updates", action="store_true", help="List recent chat IDs.")
    args = parser.parse_args()

    if args.get_updates:
        print_updates()
        return 0

    text = " ".join(args.message).strip() or sys.stdin.read().strip()
    if not text:
        print("Message is empty.", file=sys.stderr)
        return 2
    send_message(text)
    print("Sent Telegram message.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
