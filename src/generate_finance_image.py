import argparse
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

from common import ROOT_DIR, load_env_file


IMAGE_DIR = ROOT_DIR / "generated_images"
OPENAI_IMAGE_URL = "https://api.openai.com/v1/images/generations"
DEFAULT_IMAGE_MODEL = "gpt-image-1-mini"


def image_prompt(post_text: str) -> str:
    compact = re.sub(r"\s+", " ", post_text).strip()
    return (
        "Create a clean, professional LinkedIn image for an Indian fintech "
        "finance leadership post. Visual style: realistic modern finance "
        "workspace, subtle AI-assisted FP&A/dashboard elements, audit trail, "
        "cash-flow or reconciliation indicators, polished corporate lighting, "
        "no logos, no readable text, no screenshots, no people facing camera. "
        "The image should support this post topic: "
        f"{compact[:900]}"
    )


def generate_finance_image(post_text: str, image_id: str | None = None) -> Path | None:
    load_env_file(ROOT_DIR / "openai.env")
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None

    IMAGE_DIR.mkdir(exist_ok=True)
    image_id = image_id or datetime.now().strftime("%Y%m%d-%H%M%S")
    output_path = IMAGE_DIR / f"finance-{image_id}.png"
    body = json.dumps(
        {
            "model": os.environ.get("OPENAI_IMAGE_MODEL", DEFAULT_IMAGE_MODEL),
            "prompt": image_prompt(post_text),
            "size": os.environ.get("OPENAI_IMAGE_SIZE", "1536x1024"),
            "n": 1,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        OPENAI_IMAGE_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI image API returned HTTP {exc.code}: {detail}") from exc

    b64_data = (result.get("data") or [{}])[0].get("b64_json")
    if not b64_data:
        raise RuntimeError("OpenAI image API response did not include b64_json image data.")
    output_path.write_bytes(base64.b64decode(b64_data))
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate an AI image for a finance LinkedIn post.")
    parser.add_argument("--id", help="Stable image id used in the output filename.")
    parser.add_argument("post_text", nargs="*", help="Post text; reads stdin if omitted.")
    args = parser.parse_args()

    post_text = " ".join(args.post_text).strip() or sys.stdin.read().strip()
    if not post_text:
        print("Post text is empty.", file=sys.stderr)
        return 2
    path = generate_finance_image(post_text, args.id)
    if path is None:
        print("OPENAI_API_KEY is not configured; image generation skipped.")
        return 0
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
