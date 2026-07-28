# Codex Automation Prompt

Generate one complete LinkedIn post ready to publish on the user's personal
LinkedIn profile and also send the same text to Telegram.

This is the AI-news track and runs only on Tuesday and Thursday at 12:00 PM.

Use current global AI news, not evergreen commentary. On Tuesday, include
Monday's news window as eligible coverage. On Thursday, include Wednesday's news
window as eligible coverage. Choose one timely global AI development from the
current day or previous day that is credible, practical, and likely to matter to
founders, finance leaders, operators, and technology decision-makers.

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
- Keep it shorter and punchier than earlier long posts: target 900 to 1,400
  characters including hashtags, and never exceed 1,800 characters unless the
  story genuinely needs it.
- Explain what happened, why it matters, and one practical implication
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
- Use no more than one emoji.
- Use ASCII punctuation only: straight apostrophes, straight double quotes,
  and hyphens. Do not use curly quotes, em dashes, en dashes, or smart
  punctuation.
- End with exactly 6 to 8 relevant hashtags, formatted vertically with each
  hashtag on its own separate line.
- Never repeat the same news angle used in recent runs.
- Output and queue only the publish-ready post.

## Suggested Schedule

- Tuesday and Thursday at 12:00 PM in the user's timezone.

In the Codex app, use the weekly rule below and let Codex interpret the wall
clock time in the user's configured locale.

```text
FREQ=WEEKLY;BYDAY=TU,TH;BYHOUR=12;BYMINUTE=0;BYSECOND=0
```
