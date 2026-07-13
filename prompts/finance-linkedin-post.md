# Codex Automation Prompt

Generate one complete LinkedIn post ready to publish on the user's personal
LinkedIn profile and also send the same text to Telegram.

Use current global AI news, not evergreen commentary. Check the latest credible
sources available during the run, choose one timely global AI development from
the last few days, and write a sharp, practical post for founders, finance
leaders, operators, and technology decision-makers.

Queue the exact final post for both Telegram delivery and direct LinkedIn profile
publishing by running `python src/enqueue_post.py` from the repository and
passing the post text via stdin. The local background worker handles both
destinations independently and publishes LinkedIn with the authenticated member
author from `linkedin_token.json`.

Do not call the Telegram or LinkedIn APIs directly from the automation run.
The queued content must contain only the final post, with no explanation,
preamble, title, source notes outside the post, or delivery note.

## Content Rules

- Start with a strong, specific hook tied to the news.
- Explain what happened, why it matters globally, and the practical implication
  for business, finance, operations, risk, product, or governance.
- Mention the source of the information inside the post in a natural way, such
  as `Source: Reuters` or `Source: Axios`, and include the source link when
  practical while staying under the character limit.
- Avoid generic AI hype and motivational filler.
- Include the control or risk angle where relevant: data rights, model
  reliability, cost, regulation, enterprise adoption, safety, competition, or
  workflow impact.
- Keep the tone sharp, professional, slightly conversational, and highly
  engaging.
- Avoid generic openers like "In today's world" or "AI is changing everything".
- Keep the entire post under 3,000 characters.
- Use no more than one emoji.
- End with exactly 6 to 8 relevant hashtags.
- Never repeat the same news angle used in recent runs.
- Output and queue only the publish-ready post.

## Suggested Schedule

- Every day at 12:00 PM in the user's timezone.

In the Codex app, use the daily rule below and let Codex interpret the wall
clock time in the user's configured locale.

```text
FREQ=DAILY;BYHOUR=12;BYMINUTE=0;BYSECOND=0
```
