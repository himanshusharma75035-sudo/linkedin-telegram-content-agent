import argparse
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from common import ROOT_DIR, load_env_file, read_json


ENV_FILE = ROOT_DIR / "linkedin.env"
TOKEN_FILE = ROOT_DIR / "linkedin_token.json"
POSTS_URL = "https://api.linkedin.com/rest/posts"
IMAGES_URL = "https://api.linkedin.com/rest/images?action=initializeUpload"
DEFAULT_LINKEDIN_VERSION = "202604"


def linkedin_version() -> str:
    load_env_file(ENV_FILE)
    return os.environ.get("LINKEDIN_API_VERSION", DEFAULT_LINKEDIN_VERSION).strip()


def linkedin_author_urn(token: dict) -> str:
    load_env_file(ENV_FILE)
    author_urn = os.environ.get("LINKEDIN_AUTHOR_URN", "").strip()
    if author_urn:
        return author_urn

    organization_id = os.environ.get("LINKEDIN_ORGANIZATION_ID", "").strip()
    if organization_id:
        return f"urn:li:organization:{organization_id}"

    return token["person_urn"]


def linkedin_post_url(post_id: str) -> str:
    if not post_id:
        return ""
    return f"https://www.linkedin.com/feed/update/{post_id}/"


def load_token() -> dict:
    if not TOKEN_FILE.exists():
        raise FileNotFoundError("Missing linkedin_token.json. Run linkedin_oauth.py first.")

    token = read_json(TOKEN_FILE)
    if token.get("expires_at", 0) <= int(time.time()):
        raise RuntimeError("LinkedIn token expired. Run linkedin_oauth.py again.")
    return token


def api_headers(token: dict, content_type: str = "application/json") -> dict:
    return {
        "Authorization": f"Bearer {token['access_token']}",
        "Content-Type": content_type,
        "X-Restli-Protocol-Version": "2.0.0",
        "LinkedIn-Version": linkedin_version(),
    }


def initialize_image_upload(token: dict, owner_urn: str) -> tuple[str, str]:
    body = json.dumps({"initializeUploadRequest": {"owner": owner_urn}}).encode("utf-8")
    request = urllib.request.Request(
        IMAGES_URL,
        data=body,
        headers=api_headers(token),
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"LinkedIn image initialization returned HTTP {exc.code}: {details}") from exc

    value = result.get("value") or {}
    image_urn = value.get("image")
    upload_url = value.get("uploadUrl")
    if not image_urn or not upload_url:
        raise RuntimeError(f"LinkedIn image initialization returned an unexpected response: {result}")
    return image_urn, upload_url


def upload_image_binary(upload_url: str, image_path: str) -> None:
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"LinkedIn image file not found: {path}")
    content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    request = urllib.request.Request(
        upload_url,
        data=path.read_bytes(),
        headers={"Content-Type": content_type},
        method="PUT",
    )
    try:
        with urllib.request.urlopen(request, timeout=120):
            return
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"LinkedIn image upload returned HTTP {exc.code}: {details}") from exc


def publish_post(text: str, image_path: str | None = None, alt_text: str | None = None) -> dict:
    token = load_token()
    author = linkedin_author_urn(token)
    image_urn = None
    payload = {
        "author": author,
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
    if image_path:
        image_urn, upload_url = initialize_image_upload(token, author)
        upload_image_binary(upload_url, image_path)
        payload["content"] = {
            "media": {
                "id": image_urn,
                "altText": alt_text or "AI-generated finance workflow visual.",
            }
        }

    request = urllib.request.Request(
        POSTS_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers=api_headers(token),
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            post_id = response.headers.get("x-restli-id", "")
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"LinkedIn API returned HTTP {exc.code}: {details}") from exc
    return {"post_id": post_id, "image_urn": image_urn}


def publish_text_post(text: str) -> str:
    return publish_post(text)["post_id"]


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
