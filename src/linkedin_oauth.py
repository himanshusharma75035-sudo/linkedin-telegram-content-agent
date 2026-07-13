import json
import os
import secrets
import time
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

from common import ROOT_DIR, atomic_write_json, load_env_file


ENV_FILE = ROOT_DIR / "linkedin.env"
TOKEN_FILE = ROOT_DIR / "linkedin_token.json"
AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
USERINFO_URL = "https://api.linkedin.com/v2/userinfo"
SCOPES = "openid profile email w_member_social w_organization_social"


def post_form(url: str, values: dict) -> dict:
    payload = urllib.parse.urlencode(values).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def get_json(url: str, access_token: str) -> dict:
    request = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {access_token}"},
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


class CallbackHandler(BaseHTTPRequestHandler):
    result = {}

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        CallbackHandler.result = {key: values[0] for key, values in params.items()}
        body = (
            "<html><body><h2>LinkedIn authorization received.</h2>"
            "<p>You can close this tab and return to the terminal.</p></body></html>"
        ).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        return


def main() -> int:
    load_env_file(ENV_FILE)
    client_id = os.environ.get("LINKEDIN_CLIENT_ID", "").strip()
    client_secret = os.environ.get("LINKEDIN_CLIENT_SECRET", "").strip()
    redirect_uri = os.environ.get(
        "LINKEDIN_REDIRECT_URI",
        "http://localhost:8080/linkedin/callback",
    ).strip()

    if not client_id or not client_secret:
        raise RuntimeError("linkedin.env must define the Client ID and Client Secret.")

    parsed_redirect = urllib.parse.urlparse(redirect_uri)
    if parsed_redirect.hostname not in {"localhost", "127.0.0.1"}:
        raise RuntimeError("This helper requires a localhost redirect URI.")

    state = secrets.token_urlsafe(32)
    query = urllib.parse.urlencode(
        {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "state": state,
            "scope": SCOPES,
        }
    )

    server = HTTPServer((parsed_redirect.hostname, parsed_redirect.port or 8080), CallbackHandler)
    print("Opening LinkedIn authorization in your browser...")
    webbrowser.open(f"{AUTH_URL}?{query}")
    server.handle_request()
    server.server_close()

    result = CallbackHandler.result
    if result.get("error"):
        raise RuntimeError(
            f"LinkedIn authorization failed: {result.get('error_description', result['error'])}"
        )
    if result.get("state") != state:
        raise RuntimeError("LinkedIn OAuth state mismatch.")
    if not result.get("code"):
        raise RuntimeError("LinkedIn did not return an authorization code.")

    token = post_form(
        TOKEN_URL,
        {
            "grant_type": "authorization_code",
            "code": result["code"],
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
        },
    )
    profile = get_json(USERINFO_URL, token["access_token"])
    person_id = profile.get("sub")
    if not person_id:
        raise RuntimeError("LinkedIn userinfo did not return a member identifier.")

    atomic_write_json(
        TOKEN_FILE,
        {
            "access_token": token["access_token"],
            "expires_in": token.get("expires_in"),
            "expires_at": int(time.time()) + int(token.get("expires_in", 0)),
            "scope": token.get("scope", SCOPES),
            "person_id": person_id,
            "person_urn": f"urn:li:person:{person_id}",
            "name": profile.get("name"),
            "email": profile.get("email"),
        },
    )
    print(f"LinkedIn authorized for: {profile.get('name') or person_id}")
    print(f"Saved local token: {TOKEN_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
