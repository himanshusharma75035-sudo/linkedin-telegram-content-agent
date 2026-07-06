# Maintenance contract

The live Codex automation and this repository must remain synchronized.

Whenever the LinkedIn content automation changes, update and commit the
corresponding repository files in the same work session.

Changes that require a repository commit include:

- schedule or timezone changes
- content prompt or topic-policy changes
- Telegram or LinkedIn delivery behavior
- queue schema and retry behavior
- OAuth scopes, endpoints, or token handling
- LinkedIn API version headers
- startup and background-worker behavior
- setup instructions or environment variables

## Source mapping

| Live component | Repository mirror |
| --- | --- |
| Codex automation prompt | `prompts/finance-linkedin-post.md` |
| Post enqueue behavior | `src/enqueue_post.py` |
| Telegram delivery | `src/telegram_send.py` |
| LinkedIn delivery | `src/linkedin_post.py` |
| Background retries | `src/delivery_worker.py` |
| Delivery watchdog | `src/post_watchdog.py` |
| LinkedIn authorization | `src/linkedin_oauth.py` |
| Windows startup | `scripts/` |
| User setup | `README.md` |

## Change checklist

1. Update the live automation or local worker.
2. Apply the equivalent repository change.
3. Run unit tests and syntax checks.
4. Scan staged files for credentials and tokens.
5. Commit and push to `main`.
6. Confirm GitHub Actions passes.
7. Confirm the 12:20 recovery automation remains duplicate-safe.
8. Confirm the 12:35 watchdog recognizes a sent artifact without alerting.
9. Confirm token-expiry warnings are sent once per warning level.
