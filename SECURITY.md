# Security Policy

## Secrets

Never commit any of the following:

- `telegram.env`
- `linkedin.env`
- `linkedin_token.json`
- Telegram bot tokens
- LinkedIn Client Secrets
- LinkedIn access tokens

The repository `.gitignore` excludes the expected local files, but always
review `git status` before committing.

If a secret is exposed:

1. Revoke or rotate it at the provider immediately.
2. Remove it from local files and shell history where practical.
3. Do not rely on deleting a GitHub commit; assume a pushed secret was copied.

## Local token storage

This reference implementation stores tokens as local plaintext files. Use
Windows ACLs, an encrypted disk, and a dedicated user account where possible.
For multi-user or hosted deployments, replace file storage with a secrets
manager.

## Reporting a vulnerability

Please open a GitHub issue without including credentials, tokens, private post
content, or personal data. For sensitive reports, contact the repository owner
through the private contact method listed on their GitHub profile.
