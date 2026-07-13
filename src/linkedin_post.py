import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

from common import ROOT_DIR, load_env_file, read_json


ENV_FILE = ROOT_DIR / "linkedin.env"
TOKEN_FILE = ROOT_DIR / "linkedin_token.json"
POSTS_URL = "https://api.linkedin.com/rest/posts"
DEFAULT_LINKEDIN_VERSION = "202604"
DEFAULT_ORGANIZATION_ID = "109667739"


def linkedin_version() -> str:
    load_env_file(ENV_FILE)
    return os.environ.get("LINKEDIN_API_VERSION", DEFAULT_LINKEDIN_VERSION).strip()


def linkedin_author_urn(token: dict) -> str:
    load_env_file(ENV_FILE)
    author_urn = os.environ.get("LINKEDIN_AUTHOR_URN", "").strip()
    if author_urn:
        return author_urn

    organization_id = os.environ.get("LINKEDIN_ORGANIZATION_ID", DEFAULT_ORGANIZATION_ID).strip()
    if organization_id:
        return f"urn:li:organization:{organization_id}"

    return token["person_urn"]


def linkedin_post_url(post_id: str) -> str:
    if not post_id:
        return ""
    return f"https://www.linkedin.com/feed/update/{post_id}/"


def publish_text_post(text: str) -> str:
    if not TOKEN_FILE.exists():
        raise FileNotFoundError("Missing linkedin_token.json. Run linkedin_oauth.py first.")

    token = read_json(TOKEN_FILE)
    if token.get("expires_at", 0) <= int(time.time()):
        raise RuntimeError("LinkedIn token expired. Run linkedin_oauth.py again.")

    body = json.dumps(
        {
            "author": linkedin_author_urn(token),
            "commentary": text,
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": [],
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        POSTS_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {token['access_token']}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
            "LinkedIn-Version": linkedin_version(),
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.headers.get("x-restli-id", "")
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"LinkedIn API returned HTTP {exc.code}: {details}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish a LinkedIn text post.")
    parser.add_argument("message", nargs="*", help="Post text; reads stdin if omitted.")
    args = parser.parse_args()

    text = " ".join(args.message).strip() or sys.stdin.read().strip()
    if not text:
        print("Post is empty.", file=sys.stderr)
        return 2
    if len(text) > 3000:
        print("Post exceeds 3,000 characters.", file=sys.stderr)
        return 2
    print(f"Published LinkedIn post: {publish_text_post(text) or 'created'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
